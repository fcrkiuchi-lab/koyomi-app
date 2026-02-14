"""
ヒアリングエンジン - 相談内容から必要な情報を収集
"""
from typing import Dict, List, Optional
from datetime import datetime
import re


class ConsultationHearing:
    """相談内容のヒアリング管理"""
    
    def __init__(self):
        self.consultation_type = None
        self.people = []
        self.context = {}
        self.questions_asked = []
    
    def classify_consultation(self, query: str) -> str:
        """相談内容を分類
        
        Returns:
            "hiring" | "team" | "timing" | "partnership" | "relationship"
        """
        keywords = {
            "hiring": ["採用", "雇う", "人材", "面接", "候補"],
            "team": ["チーム", "プロジェクト", "メンバー", "編成", "配置"],
            "timing": ["タイミング", "いつ", "時期", "決断", "判断"],
            "partnership": ["組む", "パートナー", "協力", "共同", "提携"],
            "relationship": ["相性", "関係", "付き合い", "距離", "人間関係"],
        }
        
        for consult_type, words in keywords.items():
            if any(word in query for word in words):
                self.consultation_type = consult_type
                return consult_type
        
        return "general"
    
    def get_required_people(self, consultation_type: str) -> List[str]:
        """相談タイプごとに必要な人物情報を取得
        
        Returns:
            ["あなた自身", "候補者", ...] のようなリスト
        """
        people_map = {
            "hiring": ["あなた自身", "採用候補者"],
            "team": ["あなた自身", "既存メンバー（複数可）", "新メンバー（いる場合）"],
            "timing": ["あなた自身"],
            "partnership": ["あなた自身", "相手"],
            "relationship": ["あなた自身", "相手"],
            "general": ["あなた自身", "関係者"],
        }
        
        return people_map.get(consultation_type, ["あなた自身"])
    
    def generate_follow_up_questions(self, query: str, consultation_type: str) -> List[str]:
        """追加で聞くべき質問を生成
        
        Returns:
            ["現在のチーム構成は？", ...] のようなリスト
        """
        questions_map = {
            "hiring": [
                "候補者の職務経験や強みは何ですか？",
                "現在のチーム構成を教えてください",
                "どのポジションへの採用ですか？",
            ],
            "team": [
                "新規事業の内容を教えてください",
                "現在のメンバーの役割分担は？",
                "プロジェクトの期間はどのくらいですか？",
            ],
            "timing": [
                "具体的にどのような決断ですか？",
                "いつまでに決める必要がありますか？",
                "現在の状況を教えてください",
            ],
            "partnership": [
                "相手との関係性（友人/ビジネス/初対面）は？",
                "どのような協力関係を考えていますか？",
                "過去に一緒に仕事をしたことはありますか？",
            ],
            "relationship": [
                "どのような場面での相性が気になりますか？",
                "関係の期間はどのくらいですか？",
                "具体的な懸念点はありますか？",
            ],
        }
        
        return questions_map.get(consultation_type, [])
    
    def extract_implicit_info(self, query: str) -> Dict:
        """相談内容から暗黙の情報を抽出
        
        Returns:
            {"urgency": "high", "context": "..."}
        """
        context = {}
        
        # 緊急度判定
        if any(word in query for word in ["すぐ", "急", "至急", "早く"]):
            context["urgency"] = "high"
        elif any(word in query for word in ["いずれ", "将来", "そのうち"]):
            context["urgency"] = "low"
        else:
            context["urgency"] = "medium"
        
        # 感情の状態
        if any(word in query for word in ["不安", "心配", "迷っ", "悩"]):
            context["emotion"] = "anxious"
        elif any(word in query for word in ["期待", "楽しみ", "前向き"]):
            context["emotion"] = "positive"
        else:
            context["emotion"] = "neutral"
        
        # リスク許容度
        if any(word in query for word in ["慎重", "リスク", "失敗"]):
            context["risk_tolerance"] = "low"
        else:
            context["risk_tolerance"] = "medium"
        
        return context


class PersonProfile:
    """人物プロフィール"""
    
    def __init__(self, name: str, role: str, birth_date: datetime, 
                 birth_time: Optional[datetime] = None):
        self.name = name
        self.role = role
        self.birth_date = birth_date
        self.birth_time = birth_time
        self.meishiki = None  # 後で計算
        self.characteristics = {}
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role,
            "birth_date": self.birth_date.isoformat(),
            "birth_time": self.birth_time.isoformat() if self.birth_time else None,
            "meishiki": self.meishiki,
            "characteristics": self.characteristics,
        }
