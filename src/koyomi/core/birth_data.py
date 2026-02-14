"""
共通データ構造
"""
from datetime import datetime
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class BirthData:
    """生年月日データ"""
    
    datetime: datetime
    has_time: bool
    location: Optional[Tuple[float, float]] = None  # (latitude, longitude)
    
    def can_calculate(self, layer: str) -> bool:
        """指定されたレイヤーが計算可能か判定
        
        Args:
            layer: "shichusuimei" | "astrology" | "ekikyo" | "shibi"
            
        Returns:
            計算可能ならTrue
        """
        if layer == "shichusuimei":
            return True  # 常に計算可能
        elif layer == "astrology":
            return self.location is not None  # 位置情報が必要
        elif layer == "ekikyo":
            return True  # 常に計算可能
        elif layer == "shibi":
            return self.has_time  # 時刻が必須
        return False
    
    def get_mode(self, layer: str) -> str:
        """レイヤーの動作モードを取得
        
        Returns:
            "full" | "partial" | "unavailable"
        """
        if not self.can_calculate(layer):
            return "unavailable"
        
        if layer == "shichusuimei":
            return "full" if self.has_time else "sanchu"  # 三柱モード
        elif layer == "astrology":
            return "full" if self.has_time else "no_houses"
        elif layer == "shibi":
            return "full" if self.has_time else "unavailable"
        
        return "full"


@dataclass
class LayerResult:
    """各レイヤーの計算結果"""
    
    layer: str
    mode: str
    success: bool
    data: dict
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "layer": self.layer,
            "mode": self.mode,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }
