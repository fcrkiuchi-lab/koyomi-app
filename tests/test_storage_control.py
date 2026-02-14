"""
保存制御テスト

Zone: Tests
責務: 保存ロジックの検証（最重要）

設計思想の検証:
- 単発は保存しない
- サブスク無効なら保存しない
- サブスク有効なら保存する
"""
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import shutil

from src.koyomi.storage.subscription import (
    register_subscription,
    cancel_subscription,
    is_subscription_valid
)
from src.koyomi.storage.json_store import (
    save_session,
    delete_user_data,
    BASE_DIR
)
from src.koyomi.chat.session import ConsultationSession


# テスト用データディレクトリ
TEST_DATA_DIR = Path("data/test_users")


def setup_module():
    """テスト前のセットアップ"""
    # テスト用ディレクトリ作成
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)


def teardown_module():
    """テスト後のクリーンアップ"""
    # テストデータ削除
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)


def teardown_function():
    """各テスト後のクリーンアップ"""
    # 全テストユーザーを削除
    if BASE_DIR.exists():
        for user_dir in BASE_DIR.iterdir():
            if user_dir.is_dir() and user_dir.name.startswith("test_"):
                try:
                    shutil.rmtree(user_dir)
                except:
                    pass


# ========================================
# 最重要: 保存制御テスト
# ========================================

def test_single_session_is_not_saved():
    """【重要】単発セッションは保存されないこと
    
    設計思想: 単発は完全非保存
    """
    # 単発セッション（user_id なし）
    session = ConsultationSession.create(
        birth_data={"date": "1990-01-01"},
        pillars={"year": {"kan": "甲", "shi": "子"}},
        yojin=["木"],
        metaphor={"本質": "テスト"}
    )
    
    # 保存試行
    result = save_session(session)
    
    # Noneが返る（保存されない）
    assert result is None
    
    # データディレクトリも作られていない
    assert not BASE_DIR.exists() or len(list(BASE_DIR.iterdir())) == 0


def test_subscription_session_requires_valid_subscription():
    """【重要】サブスク無効なら保存が失敗すること
    
    設計思想: サーバー側で検証
    """
    user_id = "test_invalid_user"
    
    # サブスクセッションだがサブスク未登録
    session = ConsultationSession.create(
        birth_data={"date": "1990-01-01"},
        pillars={"year": {"kan": "甲", "shi": "子"}},
        yojin=["木"],
        metaphor={"本質": "テスト"},
        user_id=user_id,
        subscription_expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    
    # 保存がPermissionErrorで失敗すること
    with pytest.raises(PermissionError) as exc_info:
        save_session(session)
    
    # エラーメッセージ確認
    assert "Subscription inactive" in str(exc_info.value)
    
    # データが保存されていないこと
    user_dir = BASE_DIR / user_id
    assert not user_dir.exists()


def test_valid_subscription_can_save():
    """【重要】サブスク有効なら保存できること
    
    設計思想: サブスクユーザーのみ保存
    """
    user_id = "test_valid_user"
    
    # サブスク登録
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    register_subscription(user_id, expires_at)
    
    # サブスクセッション
    session = ConsultationSession.create(
        birth_data={"date": "1990-01-01"},
        pillars={"year": {"kan": "甲", "shi": "子"}},
        yojin=["木"],
        metaphor={"本質": "テスト"},
        user_id=user_id,
        subscription_expires_at=expires_at
    )
    
    # 保存成功
    saved_path = save_session(session)
    
    # パスが返る
    assert saved_path is not None
    
    # ファイルが存在する
    assert Path(saved_path).exists()
    
    # クリーンアップ
    delete_user_data(user_id)
    cancel_subscription(user_id)


def test_invalid_user_id_is_rejected():
    """【重要】不正なuser_idは拒否されること
    
    設計思想: パストラバーサル防止
    """
    # 不正なuser_id（パストラバーサル試行）
    invalid_user_ids = [
        "../../etc",
        "../passwd",
        "test/../../root",
        "test user",  # スペース
        "test@user",  # 特殊文字
        "a" * 100,  # 長すぎる
    ]
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    for invalid_id in invalid_user_ids:
        # サブスク登録を試みる（失敗するはず）
        with pytest.raises(ValueError):
            register_subscription(invalid_id, expires_at)
        
        # セッション作成
        session = ConsultationSession.create(
            birth_data={},
            pillars={},
            yojin=[],
            metaphor={},
            user_id=invalid_id,
            subscription_expires_at=expires_at
        )
        
        # 保存が失敗すること
        with pytest.raises(ValueError) as exc_info:
            save_session(session)
        
        # エラーメッセージ確認
        assert "Invalid user_id" in str(exc_info.value)


# ========================================
# 削除制御テスト
# ========================================

def test_delete_removes_all_user_data():
    """【重要】削除は全データを削除すること
    
    設計思想: 解約 = 即削除
    """
    user_id = "test_delete_user"
    
    # サブスク登録
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    register_subscription(user_id, expires_at)
    
    # 複数セッション作成
    for i in range(3):
        session = ConsultationSession.create(
            birth_data={"date": f"199{i}-01-01"},
            pillars={},
            yojin=[],
            metaphor={},
            user_id=user_id,
            subscription_expires_at=expires_at
        )
        save_session(session)
    
    # ユーザーディレクトリが存在
    user_dir = BASE_DIR / user_id
    assert user_dir.exists()
    
    # セッションが3つ存在
    sessions_dir = user_dir / "sessions"
    assert len(list(sessions_dir.glob("*.json"))) == 3
    
    # 削除実行
    result = delete_user_data(user_id)
    
    # 削除成功
    assert result is True
    
    # ユーザーディレクトリが完全に削除されている
    assert not user_dir.exists()
    
    # サブスク状態もクリア
    cancel_subscription(user_id)


def test_delete_nonexistent_user_returns_false():
    """存在しないユーザーの削除はFalseを返すこと"""
    result = delete_user_data("nonexistent_user")
    assert result is False


# ========================================
# エッジケーステスト
# ========================================

def test_expired_subscription_cannot_save():
    """期限切れサブスクでは保存できないこと"""
    user_id = "test_expired_user"
    
    # 期限切れサブスク登録
    expired_at = datetime.now(timezone.utc) - timedelta(days=1)
    register_subscription(user_id, expired_at)
    
    # セッション作成
    session = ConsultationSession.create(
        birth_data={},
        pillars={},
        yojin=[],
        metaphor={},
        user_id=user_id,
        subscription_expires_at=expired_at
    )
    
    # 保存が失敗すること
    with pytest.raises(PermissionError):
        save_session(session)
    
    # クリーンアップ
    cancel_subscription(user_id)


def test_session_without_user_id_cannot_be_subscription():
    """user_idのないセッションはサブスクにならないこと"""
    session = ConsultationSession.create(
        birth_data={},
        pillars={},
        yojin=[],
        metaphor={}
    )
    
    # サブスクではない
    assert not session.is_subscription()
    
    # 保存されない
    result = save_session(session)
    assert result is None


# ========================================
# 統合テスト
# ========================================

def test_full_lifecycle():
    """完全なライフサイクルテスト
    
    1. サブスク登録
    2. データ保存
    3. データ読み込み
    4. 解約・削除
    5. データ消失確認
    """
    user_id = "test_lifecycle_user"
    
    # 1. サブスク登録
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    register_subscription(user_id, expires_at)
    assert is_subscription_valid(user_id)
    
    # 2. データ保存
    session = ConsultationSession.create(
        birth_data={"date": "1990-01-01"},
        pillars={"year": {"kan": "甲", "shi": "子"}},
        yojin=["木"],
        metaphor={"本質": "テスト"},
        user_id=user_id,
        subscription_expires_at=expires_at
    )
    saved_path = save_session(session)
    assert saved_path is not None
    assert Path(saved_path).exists()
    
    # 3. 解約・削除
    delete_user_data(user_id)
    cancel_subscription(user_id)
    
    # 4. データ消失確認
    assert not Path(saved_path).exists()
    user_dir = BASE_DIR / user_id
    assert not user_dir.exists()
    assert not is_subscription_valid(user_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
