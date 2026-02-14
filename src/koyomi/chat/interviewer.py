"""
対話式ヒアリングエンジン
ユーザーの相談内容を段階的に深掘り
"""
from typing import Dict, List, Optional
from enum import Enum


class QuestionType(Enum):
    """質問タイプ"""
    CONSULTATION_TYPE = "consultation_type"  # 相談の種類
    PEOPLE = "people"  # 関係者
    SPECIFIC_QUESTION = "specific_question"  # 具体的な質問
    TIMING = "timing"  # タイミング
    CONCERNS = "concerns"  # 懸念点


class InterviewState:
    """ヒアリング状態管理"""
    
    def __init__(self):
        self.consultation_type = None  # 採用/パートナー/チーム/タイミング
        self.people = []  # 関係者リスト
        self.specific_question = None  # 具体的な質問
        self.timing_info = None  # タイミング情報
        self.concerns = []  # 懸念点
        self.current_step = 0
    
    def is_complete(self) -> bool:
        """ヒアリング完了判定"""
        return (
            self.consultation_type is not None
            and len(self.people) > 0
            and self.specific_question is not None
        )


class Interviewer:
    """対話式ヒアリングエンジン"""
    
    # 相談タイプごとのテンプレート
    CONSULTATION_TYPES = {
        "採用": {
            "keywords": ["採用", "雇う", "新メンバー", "新入社員"],
            "questions": [
                "採用を検討している方の生年月日を教えてください",
                "既存チームメンバーの生年月日も教えてください",
                "どんなポジションですか？（例: エンジニア、営業）",
                "採用について特に不安な点はありますか？"
            ]
        },
        "パートナー選定": {
            "keywords": ["パートナー", "共同創業", "提携", "協力"],
            "questions": [
                "パートナー候補の方の生年月日を教えてください",
                "あなたの生年月日を教えてください",
                "どんな役割を期待していますか？",
                "既に懸念している点はありますか？"
            ]
        },
        "チーム編成": {
            "keywords": ["チーム", "プロジェクト", "新規事業"],
            "questions": [
                "チームメンバー全員の生年月日を教えてください",
                "プロジェクトの内容を簡単に教えてください",
                "成功のカギは何だと考えていますか？"
            ]
        },
        "タイミング判断": {
            "keywords": ["タイミング", "いつ", "時期", "決断"],
            "questions": [
                "あなたの生年月日を教えてください",
                "何を決断しようとしていますか？",
                "いつまでに決める必要がありますか？"
            ]
        },
        "相性確認": {
            "keywords": ["相性", "合う", "うまくいく"],
            "questions": [
                "相手の方の生年月日を教えてください",
                "あなたの生年月日を教えてください",
                "どんな関係性ですか？（仕事/恋愛/友人）",
                "特に気になる点はありますか？"
            ]
        }
    }
    
    def __init__(self):
        self.state = InterviewState()
    
    def classify_consultation(self, initial_message: str) -> str:
        """
        初回メッセージから相談タイプを分類
        
        Args:
            initial_message: ユーザーの最初のメッセージ
        
        Returns:
            相談タイプ（採用/パートナー選定/etc）
        """
        message_lower = initial_message.lower()
        
        for consult_type, config in self.CONSULTATION_TYPES.items():
            for keyword in config["keywords"]:
                if keyword in message_lower:
                    return consult_type
        
        # デフォルト
        return "相性確認"
    
    def get_next_question(self) -> Optional[str]:
        """
        次に聞くべき質問を取得
        
        Returns:
            質問文字列、またはNone（ヒアリング完了時）
        """
        if self.state.is_complete():
            return None
        
        if self.state.consultation_type is None:
            return self._get_consultation_type_question()
        
        # 相談タイプに応じた質問
        config = self.CONSULTATION_TYPES[self.state.consultation_type]
        questions = config["questions"]
        
        if self.state.current_step < len(questions):
            question = questions[self.state.current_step]
            self.state.current_step += 1
            return question
        
        # ヒアリング完了
        self.state.specific_question = "complete"
        return None
    
    def _get_consultation_type_question(self) -> str:
        """相談タイプを聞く質問"""
        return """
どんなご相談でしょうか？以下から選んでください：

1. 採用判断（この人を採用すべきか？）
2. パートナー選定（この人と組むべきか？）
3. チーム編成（このメンバーで大丈夫か？）
4. タイミング判断（今、決断すべきか？）
5. 相性確認（この人との相性は？）

番号または内容を教えてください。
"""
    
    def process_answer(self, answer: str) -> str:
        """
        回答を処理して次の質問を返す
        
        Args:
            answer: ユーザーの回答
        
        Returns:
            次の質問、または完了メッセージ
        """
        # 相談タイプが未設定の場合
        if self.state.consultation_type is None:
            # 番号で選択された場合
            if answer.strip() in ["1", "2", "3", "4", "5"]:
                types = list(self.CONSULTATION_TYPES.keys())
                self.state.consultation_type = types[int(answer) - 1]
            else:
                # キーワードから判定
                self.state.consultation_type = self.classify_consultation(answer)
            
            next_q = self.get_next_question()
            return f"承知しました。「{self.state.consultation_type}」についてですね。\n\n{next_q}"
        
        # 生年月日の抽出（簡易版）
        if "年" in answer or "/" in answer or "-" in answer:
            # TODO: より厳密な日付パース
            pass
        
        # 次の質問取得
        next_q = self.get_next_question()
        
        if next_q is None:
            return "ありがとうございます。情報が揃いました。分析を開始します..."
        
        return next_q
    
    def get_summary(self) -> Dict:
        """
        ヒアリング内容のサマリー
        
        Returns:
            {
                "consultation_type": "採用",
                "people": [...],
                "question": "...",
                ...
            }
        """
        return {
            "consultation_type": self.state.consultation_type,
            "people": self.state.people,
            "specific_question": self.state.specific_question,
            "concerns": self.state.concerns,
        }
