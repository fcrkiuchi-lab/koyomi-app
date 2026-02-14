"""
JSON保存（サブスクユーザーのみ）

Zone: Logic（Plan必須）
責務: セッションデータの永続化

設計思想:
- 単発利用: 保存しない（完全非保存）
- サブスク: data/users/{user_id}/sessions/{session_id}.json
- ディレクトリの存在 = 契約中
"""
import json
import shutil
import re
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from src.koyomi.chat.session import ConsultationSession
from src.koyomi.storage.subscription import is_subscription_valid
from src.koyomi.storage.deletion_log import (
    log_deletion_start,
    log_deletion_success,
    log_deletion_failure
)


# 基本ディレクトリ（サブスクユーザーのみ）
BASE_DIR = Path("data/users")


def sanitize_user_id(user_id: str) -> str:
    """user_idのサニタイズ（パストラバーサル防止）
    
    Args:
        user_id: ユーザーID
    
    Returns:
        サニタイズ済みuser_id
    
    Raises:
        ValueError: 不正なuser_id
    
    Note:
        セキュリティ上極めて重要
        user_id = "../../etc" のような攻撃を防ぐ
    """
    if not user_id:
        raise ValueError("user_id is required")
    
    # 英数字、ハイフン、アンダースコアのみ許可
    if not re.match(r"^[a-zA-Z0-9_-]+$", user_id):
        raise ValueError(f"Invalid user_id format: {user_id}")
    
    # 長さチェック（DoS防止）
    if len(user_id) > 64:
        raise ValueError("user_id too long")
    
    return user_id


def save_session(session: ConsultationSession) -> Optional[str]:
    """セッションをJSON保存
    
    Args:
        session: 保存するセッション
    
    Returns:
        保存したファイルパス（保存した場合）
        None（単発利用で保存しない場合）
    
    Raises:
        ValueError: サブスクセッションだがuser_idがない、または不正な場合
        PermissionError: サブスク無効（重要：フロント側の情報は信用しない）
    
    Note:
        サブスク検証はサーバー側で必ず実施
        フロント側から渡された情報は信用しない
    """
    # 単発利用: 保存しない
    if not session.is_subscription():
        return None
    
    # サブスクだがuser_idがない場合はエラー
    if not session.user_id:
        raise ValueError("Subscription session requires user_id")
    
    # user_idサニタイズ（パストラバーサル防止）
    safe_user_id = sanitize_user_id(session.user_id)
    
    # 🔥 重要: サブスク状態をサーバー側で検証
    if not is_subscription_valid(safe_user_id):
        raise PermissionError(
            f"Subscription inactive for user: {safe_user_id}. "
            "Data cannot be saved."
        )
    
    # ユーザーディレクトリ作成
    user_dir = BASE_DIR / safe_user_id / "sessions"
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # ファイルパス
    file_path = user_dir / f"{session.session_id}.json"
    tmp_path = file_path.with_suffix('.json.tmp')
    
    # アトミック保存（データ破損防止）
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
    
    # 原子的に置き換え
    os.replace(tmp_path, file_path)
    
    return str(file_path)


def load_session(user_id: str, session_id: str) -> Optional[ConsultationSession]:
    """セッション読み込み
    
    Args:
        user_id: ユーザーID
        session_id: セッションID
    
    Returns:
        ConsultationSession（存在する場合）
        None（存在しない場合）
    
    Raises:
        ValueError: 不正なuser_id
    """
    safe_user_id = sanitize_user_id(user_id)
    file_path = BASE_DIR / safe_user_id / "sessions" / f"{session_id}.json"
    
    if not file_path.exists():
        return None
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return ConsultationSession(**data)


def list_sessions(user_id: str) -> list:
    """ユーザーのセッション一覧
    
    Args:
        user_id: ユーザーID
    
    Returns:
        セッションIDのリスト
    
    Raises:
        ValueError: 不正なuser_id
    """
    safe_user_id = sanitize_user_id(user_id)
    sessions_dir = BASE_DIR / safe_user_id / "sessions"
    
    if not sessions_dir.exists():
        return []
    
    return [f.stem for f in sessions_dir.glob("*.json")]


def delete_session(user_id: str, session_id: str) -> bool:
    """セッション削除
    
    Args:
        user_id: ユーザーID
        session_id: セッションID
    
    Returns:
        True: 削除成功、False: ファイルが存在しない
    
    Raises:
        ValueError: 不正なuser_id
    """
    safe_user_id = sanitize_user_id(user_id)
    file_path = BASE_DIR / safe_user_id / "sessions" / f"{session_id}.json"
    
    if not file_path.exists():
        return False
    
    file_path.unlink()
    return True


def delete_user_data(user_id: str, reason: str = "manual") -> bool:
    """ユーザーデータ完全削除（解約時）
    
    Args:
        user_id: ユーザーID
        reason: 削除理由（manual, expired, cancellation）
    
    Returns:
        True: 削除成功、False: ディレクトリが存在しない
    
    Raises:
        ValueError: 不正なuser_id
        Exception: 削除失敗（重要：例外を握り潰さない）
    
    Note:
        サブスク解約時に即時実行
        復元不可
        ユーザーディレクトリごと削除（セッション削除漏れ防止）
        
        削除の確実性が最重要
        失敗した場合は例外を握り潰さず、上位で処理
        すべての削除は監査ログに記録
    """
    safe_user_id = sanitize_user_id(user_id)
    user_dir = BASE_DIR / safe_user_id
    
    if not user_dir.exists():
        return False
    
    # 削除開始ログ
    log_deletion_start(safe_user_id, reason)
    
    try:
        # ユーザーディレクトリごと削除（安全・確実）
        shutil.rmtree(user_dir)
        
        # 削除成功ログ
        log_deletion_success(safe_user_id)
        
        return True
    
    except Exception as e:
        # 削除失敗ログ
        log_deletion_failure(safe_user_id, str(e))
        
        # 例外を握り潰さない（上位で検知）
        raise


def cleanup_expired_sessions() -> int:
    """期限切れセッション削除（手動実行スクリプト用）
    
    Returns:
        削除したセッション数
    
    Note:
        MVP段階では手動実行
        将来的にcronで自動化
    """
    deleted_count = 0
    
    if not BASE_DIR.exists():
        return 0
    
    # 全ユーザーをスキャン
    for user_dir in BASE_DIR.iterdir():
        if not user_dir.is_dir():
            continue
        
        user_id = user_dir.name
        sessions_dir = user_dir / "sessions"
        
        if not sessions_dir.exists():
            continue
        
        # 各セッションをチェック
        for session_file in sessions_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                session = ConsultationSession(**data)
                
                # 期限切れチェック
                if session.is_expired():
                    session_file.unlink()
                    deleted_count += 1
            
            except Exception as e:
                # エラーログ出力（本番では適切なロガーに）
                print(f"Error processing {session_file}: {e}")
                continue
    
    return deleted_count
