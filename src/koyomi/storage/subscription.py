"""
サブスクリプション検証

Zone: Logic（Plan必須）
責務: サブスクリプション状態のサーバー側検証

設計思想:
- フロント側の情報は信用しない
- サーバー側で必ず検証
- 不正なアクセスは例外で弾く
"""
from datetime import datetime, timezone
from typing import Optional
import re


# TODO: 本番実装時はDBまたは署名付きトークンで検証
# 現在はMVP用のダミー実装
VALID_SUBSCRIPTIONS = {}  # {user_id: expires_at}


def _sanitize_user_id(user_id: str) -> str:
    """user_idのサニタイズ
    
    Args:
        user_id: ユーザーID
    
    Returns:
        サニタイズ済みuser_id
    
    Raises:
        ValueError: 不正なuser_id
    """
    if not user_id:
        raise ValueError("user_id is required")
    
    if not re.match(r"^[a-zA-Z0-9_-]+$", user_id):
        raise ValueError(f"Invalid user_id format: {user_id}")
    
    if len(user_id) > 64:
        raise ValueError("user_id too long")
    
    return user_id


def verify_subscription(user_id: str) -> bool:
    """サブスクリプション状態を検証
    
    Args:
        user_id: ユーザーID
    
    Returns:
        True: 有効なサブスク、False: 無効
    
    Raises:
        ValueError: 不正なuser_id
    
    Note:
        MVP段階ではダミー実装
        本番では以下のいずれかで検証:
        - データベース照会
        - 署名付きJWTトークン検証
        - 外部決済APIとの連携
    """
    # user_idサニタイズ
    safe_user_id = _sanitize_user_id(user_id)
    
    # TODO: 本番実装
    # 例: DBから取得
    # subscription = db.get_subscription(safe_user_id)
    # return subscription.is_active and subscription.expires_at > datetime.now(timezone.utc)
    
    # MVP用ダミー（常にFalseを返す = 安全側）
    return safe_user_id in VALID_SUBSCRIPTIONS and \
           VALID_SUBSCRIPTIONS[safe_user_id] > datetime.now(timezone.utc)


def is_subscription_valid(user_id: str) -> bool:
    """サブスクリプション有効性チェック（エイリアス）
    
    Args:
        user_id: ユーザーID
    
    Returns:
        True: 有効、False: 無効
    """
    return verify_subscription(user_id)


def register_subscription(user_id: str, expires_at: datetime):
    """サブスクリプション登録（開発/テスト用）
    
    Args:
        user_id: ユーザーID
        expires_at: 有効期限
    
    Raises:
        ValueError: 不正なuser_id
    
    Note:
        本番では使用しない
        開発/テスト時のみ使用
    """
    safe_user_id = _sanitize_user_id(user_id)
    VALID_SUBSCRIPTIONS[safe_user_id] = expires_at


def cancel_subscription(user_id: str):
    """サブスクリプション解約（開発/テスト用）
    
    Args:
        user_id: ユーザーID
    
    Raises:
        ValueError: 不正なuser_id
    
    Note:
        本番では使用しない
        開発/テスト時のみ使用
    """
    safe_user_id = _sanitize_user_id(user_id)
    if safe_user_id in VALID_SUBSCRIPTIONS:
        del VALID_SUBSCRIPTIONS[safe_user_id]
