#!/usr/bin/env python3
"""
保存制御ロジック検証スクリプト

pytest不要で実行可能
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import shutil

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.koyomi.storage.subscription import (
    register_subscription,
    cancel_subscription,
    is_subscription_valid
)
from src.koyomi.storage.json_store import (
    save_session,
    delete_user_data,
    BASE_DIR,
    sanitize_user_id
)
from src.koyomi.chat.session import ConsultationSession


def cleanup():
    """テストデータクリーンアップ"""
    if BASE_DIR.exists():
        for user_dir in BASE_DIR.iterdir():
            if user_dir.is_dir() and user_dir.name.startswith("test_"):
                shutil.rmtree(user_dir)


def test_sanitize():
    """サニタイズテスト"""
    print("=" * 50)
    print("TEST: user_idサニタイズ")
    print("=" * 50)
    
    # 正常系
    try:
        result = sanitize_user_id("valid_user_123")
        print(f"✅ 正常なID: {result}")
    except ValueError as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    
    # 異常系
    invalid_ids = [
        "../../etc",
        "../passwd",
        "test user",  # スペース
        "test@user",  # 特殊文字
        "a" * 100,  # 長すぎる
    ]
    
    for invalid_id in invalid_ids:
        try:
            sanitize_user_id(invalid_id)
            print(f"❌ 不正IDを受理: {invalid_id}")
            return False
        except ValueError:
            print(f"✅ 不正IDを拒否: {invalid_id}")
    
    print()
    return True


def test_single_session_not_saved():
    """単発セッションは保存されないことを確認"""
    print("=" * 50)
    print("TEST: 単発セッションは保存されない")
    print("=" * 50)
    
    # 単発セッション（user_id なし）
    session = ConsultationSession.create(
        birth_data={"date": "1990-01-01"},
        pillars={"year": {"kan": "甲", "shi": "子"}},
        yojin=["木"],
        metaphor={"本質": "テスト"}
    )
    
    # 保存試行
    result = save_session(session)
    
    if result is None:
        print("✅ 単発セッションは保存されない（None返却）")
        
        # データディレクトリも作られていない
        if not BASE_DIR.exists() or len(list(BASE_DIR.iterdir())) == 0:
            print("✅ データディレクトリも未作成")
            print()
            return True
        else:
            print("❌ データディレクトリが作成されている")
            print()
            return False
    else:
        print(f"❌ 保存された: {result}")
        print()
        return False


def test_invalid_subscription():
    """サブスク無効なら保存失敗"""
    print("=" * 50)
    print("TEST: サブスク無効なら保存失敗")
    print("=" * 50)
    
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
    try:
        save_session(session)
        print("❌ 保存が成功してしまった")
        print()
        return False
    except PermissionError as e:
        if "Subscription inactive" in str(e):
            print(f"✅ PermissionError発生: {e}")
            
            # データが保存されていないこと
            user_dir = BASE_DIR / user_id
            if not user_dir.exists():
                print("✅ データ未保存")
                print()
                return True
            else:
                print("❌ データが保存されている")
                print()
                return False
        else:
            print(f"❌ 別のエラー: {e}")
            print()
            return False


def test_valid_subscription():
    """サブスク有効なら保存できる"""
    print("=" * 50)
    print("TEST: サブスク有効なら保存可能")
    print("=" * 50)
    
    user_id = "test_valid_user"
    
    # サブスク登録
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    register_subscription(user_id, expires_at)
    print(f"✅ サブスク登録: {user_id}")
    
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
    try:
        saved_path = save_session(session)
        
        if saved_path and Path(saved_path).exists():
            print(f"✅ 保存成功: {saved_path}")
            
            # クリーンアップ
            delete_user_data(user_id)
            cancel_subscription(user_id)
            print("✅ クリーンアップ完了")
            print()
            return True
        else:
            print("❌ パスが返らない、またはファイル未作成")
            print()
            return False
    
    except Exception as e:
        print(f"❌ 保存失敗: {e}")
        cancel_subscription(user_id)
        print()
        return False


def test_delete_all_data():
    """削除は全データを削除"""
    print("=" * 50)
    print("TEST: 削除は全データを削除")
    print("=" * 50)
    
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
    
    print("✅ 3セッション作成")
    
    # ユーザーディレクトリが存在
    user_dir = BASE_DIR / user_id
    sessions_dir = user_dir / "sessions"
    session_count = len(list(sessions_dir.glob("*.json")))
    
    if session_count == 3:
        print(f"✅ セッション数確認: {session_count}")
    else:
        print(f"❌ セッション数不一致: {session_count}")
        return False
    
    # 削除実行
    result = delete_user_data(user_id)
    
    if result:
        print("✅ 削除実行成功")
        
        # ユーザーディレクトリが完全に削除されている
        if not user_dir.exists():
            print("✅ ユーザーディレクトリ完全削除")
            cancel_subscription(user_id)
            print()
            return True
        else:
            print("❌ ディレクトリが残っている")
            cancel_subscription(user_id)
            print()
            return False
    else:
        print("❌ 削除失敗")
        cancel_subscription(user_id)
        print()
        return False


def main():
    """全テスト実行"""
    print("\n🔍 暦KOYOMI - 保存制御ロジック検証\n")
    
    cleanup()
    
    results = []
    
    # テスト実行
    results.append(("サニタイズ", test_sanitize()))
    results.append(("単発非保存", test_single_session_not_saved()))
    results.append(("サブスク無効拒否", test_invalid_subscription()))
    results.append(("サブスク有効保存", test_valid_subscription()))
    results.append(("完全削除", test_delete_all_data()))
    
    # クリーンアップ
    cleanup()
    
    # 結果サマリー
    print("=" * 50)
    print("📊 テスト結果")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"合計: {len(results)} テスト")
    print(f"成功: {passed}")
    print(f"失敗: {failed}")
    print()
    
    if failed == 0:
        print("🎉 すべてのテストが成功しました！")
        return 0
    else:
        print("⚠️ 一部のテストが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
