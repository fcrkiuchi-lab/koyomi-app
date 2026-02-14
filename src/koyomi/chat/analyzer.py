"""
統合分析エンジン - 命式計算 + 相性分析 + アドバイス生成
"""
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.koyomi.layer1.engine import MeishikiEngine
from src.koyomi.layer1.metaphor import get_metaphor, get_gogyo_meaning
from src.koyomi.chat.hearing import ConsultationHearing, PersonProfile
from src.koyomi.chat.consultant import KoyomiConsultant


class IntegratedAnalyzer:
    """統合分析エンジン"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.meishiki_engine = MeishikiEngine()
        self.consultant = KoyomiConsultant(api_key=api_key)
        self.hearing = ConsultationHearing()
    
    def analyze_consultation(
        self,
        query: str,
        people: List[PersonProfile],
        additional_context: Optional[Dict] = None
    ) -> Dict:
        """
        相談内容を総合分析
        
        Args:
            query: 相談内容
            people: 関係者リスト
            additional_context: 追加コンテキスト
        
        Returns:
            {
                "consultation_type": str,
                "people_analysis": Dict,
                "advice": str,
                "follow_up_questions": List[str]
            }
        """
        # 1. 相談タイプ分類
        consultation_type = self.hearing.classify_consultation(query)
        
        # 2. 各人物の命式分析
        people_analysis = {}
        
        for person in people:
            analysis = self._analyze_person(person)
            people_analysis[person.name] = analysis
        
        # 3. 相性分析（2人以上の場合）
        if len(people) >= 2:
            compatibility = self._analyze_compatibility(people)
            people_analysis['compatibility'] = compatibility
        
        # 4. コンテキスト抽出
        context = self.hearing.extract_implicit_info(query)
        if additional_context:
            context['additional_context'] = additional_context
        
        # 5. アドバイス生成
        advice = self.consultant.generate_advice(
            query=query,
            consultation_type=consultation_type,
            people_analysis=people_analysis,
            context=context
        )
        
        # 6. フォローアップ質問生成
        follow_up = self.hearing.generate_follow_up_questions(query, consultation_type)
        
        return {
            "consultation_type": consultation_type,
            "people_analysis": people_analysis,
            "advice": advice,
            "follow_up_questions": follow_up,
            "context": context
        }
    
    def _analyze_person(self, person: PersonProfile) -> Dict:
        """個人の命式分析"""
        
        # 命式計算
        result = self.meishiki_engine.judge_yojin(person.birth_date)
        
        # メタファー取得
        day_kan = result["pillars"]["day"]["kan"]
        month_shi = result["pillars"]["month"]["shi"]
        metaphor = get_metaphor(day_kan, month_shi)
        gogyo_type, gogyo_meaning = get_gogyo_meaning(day_kan)
        
        return {
            "pillars": result["pillars"],
            "day_kan": day_kan,
            "season": result["season"],
            "condition": result["condition"],
            "yojin": result["yojin"],
            "metaphor": metaphor,
            "gogyo_type": gogyo_type,
            "gogyo_meaning": gogyo_meaning,
        }
    
    def _analyze_compatibility(self, people: List[PersonProfile]) -> Dict:
        """相性分析（簡易版）"""
        
        if len(people) < 2:
            return {}
        
        # 2人の場合の相性分析
        person1_result = self.meishiki_engine.judge_yojin(people[0].birth_date)
        person2_result = self.meishiki_engine.judge_yojin(people[1].birth_date)
        
        day_kan1 = person1_result["pillars"]["day"]["kan"]
        day_kan2 = person2_result["pillars"]["day"]["kan"]
        
        # 五行の相生相克を簡易判定
        score, relation = self._calculate_compatibility_score(day_kan1, day_kan2)
        
        return {
            "score": score,
            "relation": relation,
            "person1_kan": day_kan1,
            "person2_kan": day_kan2,
        }
    
    def _calculate_compatibility_score(self, kan1: str, kan2: str) -> tuple:
        """相性スコア計算（簡易版）"""
        
        # 五行マッピング
        gogyo_map = {
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火",
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水",
        }
        
        element1 = gogyo_map.get(kan1, "不明")
        element2 = gogyo_map.get(kan2, "不明")
        
        # 相生関係
        sheng = {
            "木": "火", "火": "土", "土": "金",
            "金": "水", "水": "木"
        }
        
        # 相克関係
        ke = {
            "木": "土", "土": "水", "水": "火",
            "火": "金", "金": "木"
        }
        
        score = 50  # 基準点
        relation = ""
        
        # 同じ五行
        if element1 == element2:
            score = 60
            relation = f"同じ{element1}の性質を持つ（似た者同士）"
        
        # 相生関係
        elif sheng.get(element1) == element2:
            score = 80
            relation = f"{element1}が{element2}を生み出す（相生・良好な関係）"
        
        elif sheng.get(element2) == element1:
            score = 75
            relation = f"{element2}が{element1}を生み出す（相生・サポート関係）"
        
        # 相克関係
        elif ke.get(element1) == element2:
            score = 40
            relation = f"{element1}が{element2}を抑制（相克・緊張関係）"
        
        elif ke.get(element2) == element1:
            score = 45
            relation = f"{element2}が{element1}を抑制（相克・刺激関係）"
        
        else:
            score = 55
            relation = "特に強い関係性はない（中立）"
        
        return score, relation
