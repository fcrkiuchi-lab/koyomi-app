"""
鑑定セッション管理

Zone: Logic（Plan必須）
責務: セッションデータ構造の定義
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid


@dataclass
class ConsultationSession:
    """鑑定セッション
    
    Attributes:
        session_id: セッション一意ID（UUID）
        user_id: ユーザーID（サブスクのみ）
        created_at: 作成日時（ISO 8601形式）
        expires_at: 有効期限（サブスク終了日時、ISO 8601形式）
        birth_data: 生年月日情報
        pillars: 命式（四柱）
        yojin: 用神リスト
        metaphor: メタファー辞書
        query: 相談内容（任意）
        summary: 鑑定まとめ（任意）
    """
    session_id: str
    created_at: str
    
    # Core層から取得したデータ
    birth_data: Dict
    pillars: Dict
    yojin: List[str]
    metaphor: Dict
    
    # 対話情報
    query: Optional[str] = None
    summary: Optional[str] = None
    
    # サブスク情報（サブスクユーザーのみ）
    user_id: Optional[str] = None
    subscription_expires_at: Optional[str] = None  # サブスク有効期限（ISO 8601）
    
    @classmethod
    def create(
        cls,
        birth_data: Dict,
        pillars: Dict,
        yojin: List[str],
        metaphor: Dict,
        query: Optional[str] = None,
        summary: Optional[str] = None,
        user_id: Optional[str] = None,
        subscription_expires_at: Optional[datetime] = None
    ) -> "ConsultationSession":
        """セッション生成
        
        Args:
            birth_data: 生年月日情報
            pillars: 命式
            yojin: 用神
            metaphor: メタファー
            query: 相談内容（任意）
            summary: まとめ（任意）
            user_id: ユーザーID（サブスクのみ）
            subscription_expires_at: サブスク有効期限（サブスクのみ）
        
        Returns:
            ConsultationSession
        """
        return cls(
            session_id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            birth_data=birth_data,
            pillars=pillars,
            yojin=yojin,
            metaphor=metaphor,
            query=query,
            summary=summary,
            user_id=user_id,
            subscription_expires_at=subscription_expires_at.isoformat() if subscription_expires_at else None
        )
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（JSON保存用）"""
        return asdict(self)
    
    def is_expired(self) -> bool:
        """有効期限チェック
        
        Returns:
            True: 期限切れ、False: 有効
        """
        if not self.subscription_expires_at:
            return False
        
        expiry = datetime.fromisoformat(self.subscription_expires_at)
        return datetime.now(timezone.utc) > expiry
    
    def is_subscription(self) -> bool:
        """サブスクセッションかどうか
        
        Returns:
            True: サブスク、False: 単発
        """
        return self.user_id is not None
