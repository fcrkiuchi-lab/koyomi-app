"""
AIコンサルタント - Claude APIを使った自然言語アドバイス生成
"""
import os
from typing import Dict, List, Optional
from datetime import datetime


class KoyomiConsultant:
    """暦 KOYOMI AIコンサルタント"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API key（環境変数 ANTHROPIC_API_KEY で設定可）
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.use_api = bool(self.api_key)
        
        if self.use_api:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                print("Warning: anthropic パッケージがインストールされていません")
                print("pip install anthropic でインストールしてください")
                self.use_api = False
    
    def generate_advice(
        self,
        query: str,
        consultation_type: str,
        people_analysis: Dict,
        context: Dict
    ) -> str:
        """
        具体的なアドバイスを生成
        
        Args:
            query: ユーザーの相談内容
            consultation_type: 相談タイプ
            people_analysis: 命式分析結果
            context: 追加のコンテキスト情報
        
        Returns:
            自然言語の具体的アドバイス
        """
        if self.use_api:
            return self._generate_with_api(query, consultation_type, people_analysis, context)
        else:
            return self._generate_fallback(query, consultation_type, people_analysis, context)
    
    def _generate_with_api(
        self,
        query: str,
        consultation_type: str,
        people_analysis: Dict,
        context: Dict
    ) -> str:
        """Claude APIを使用してアドバイス生成"""
        
        # システムプロンプト構築
        system_prompt = self._build_system_prompt(consultation_type)
        
        # ユーザープロンプト構築
        user_prompt = self._build_user_prompt(query, people_analysis, context)
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            print(f"API呼び出しエラー: {e}")
            return self._generate_fallback(query, consultation_type, people_analysis, context)
    
    def _build_system_prompt(self, consultation_type: str) -> str:
        """システムプロンプト構築"""
        
        base_prompt = """あなたは四柱推命の専門家であり、経営コンサルタントです。

【あなたの役割】
- 経営者・起業家の意思決定をサポート
- 人間関係の最適化アドバイス
- 具体的で実行可能な提案

【アドバイスの条件】
1. 専門用語は最小限に（必要なら簡単に説明）
2. 具体的な行動を3つ以上示す
3. タイミングも明示（いつやるべきか）
4. リスクも正直に伝える
5. 理由を明確に説明
6. 経営者が意思決定できるレベルの情報

【出力形式】
## 総合判断
結論を1-2文で端的に

## 理由
なぜそう判断したか（命式の特徴から）

## 具体的なアドバイス
1. すぐやるべきこと
2. 中期的な対策
3. 注意すべきポイント

## タイミング
いつ実行すべきか、避けるべき時期

## リスクと対策
想定されるリスクと回避方法
"""
        
        type_specific = {
            "hiring": "\n【採用判断のポイント】\n- 既存チームとの相性\n- 役割の適性\n- 育成の方向性",
            "team": "\n【チーム編成のポイント】\n- 各メンバーの強み活用\n- 役割分担の明確化\n- コミュニケーション設計",
            "timing": "\n【タイミング判断のポイント】\n- 運気の流れ\n- 準備状況の確認\n- 外部環境の考慮",
            "partnership": "\n【パートナーシップのポイント】\n- 補完関係の有無\n- 役割分担の設計\n- リスク分散の方法",
        }
        
        return base_prompt + type_specific.get(consultation_type, "")
    
    def _build_user_prompt(
        self,
        query: str,
        people_analysis: Dict,
        context: Dict
    ) -> str:
        """ユーザープロンプト構築"""
        
        prompt = f"""【相談内容】
{query}

【命式分析結果】
"""
        
        # 各人物の分析結果を追加
        for person_name, analysis in people_analysis.items():
            prompt += f"\n■ {person_name}\n"
            prompt += f"- 日干: {analysis.get('day_kan', '不明')}\n"
            prompt += f"- 特徴: {analysis.get('metaphor', {}).get('本質', '不明')}\n"
            prompt += f"- 強み: {analysis.get('metaphor', {}).get('強み', '不明')}\n"
            prompt += f"- 課題: {analysis.get('metaphor', {}).get('課題', '不明')}\n"
            
            if 'yojin' in analysis:
                prompt += f"- 用神: {' → '.join(analysis['yojin'])}\n"
        
        # 相性情報があれば追加
        if 'compatibility' in people_analysis:
            prompt += f"\n【相性分析】\n"
            compat = people_analysis['compatibility']
            prompt += f"- 総合相性: {compat.get('score', 0)}点\n"
            prompt += f"- 関係性: {compat.get('relation', '不明')}\n"
        
        # コンテキスト情報追加
        if context:
            prompt += f"\n【状況】\n"
            if 'urgency' in context:
                urgency_map = {"high": "緊急", "medium": "通常", "low": "余裕あり"}
                prompt += f"- 緊急度: {urgency_map.get(context['urgency'], '不明')}\n"
            
            if 'additional_context' in context:
                for key, value in context['additional_context'].items():
                    prompt += f"- {key}: {value}\n"
        
        prompt += "\n上記の情報をもとに、具体的で実行可能なアドバイスをお願いします。"
        
        return prompt
    
    def _generate_fallback(
        self,
        query: str,
        consultation_type: str,
        people_analysis: Dict,
        context: Dict
    ) -> str:
        """API未使用時のフォールバック（基本的なアドバイス）"""
        
        advice = "## 総合判断\n\n"
        
        # 相性スコアベースの判断
        if 'compatibility' in people_analysis:
            score = people_analysis['compatibility'].get('score', 50)
            if score >= 70:
                advice += "✅ 推奨できます。\n\n"
            elif score >= 50:
                advice += "△ 条件付きで推奨。工夫が必要です。\n\n"
            else:
                advice += "⚠️ 慎重な判断が必要です。\n\n"
        
        advice += "## 理由\n\n"
        
        # 各人物の特徴を列挙
        for person_name, analysis in people_analysis.items():
            if person_name != 'compatibility':
                metaphor = analysis.get('metaphor', {})
                advice += f"**{person_name}**: {metaphor.get('本質', '不明')}\n"
                advice += f"- 強み: {metaphor.get('強み', '不明')}\n"
                advice += f"- 課題: {metaphor.get('課題', '不明')}\n\n"
        
        advice += "\n## 具体的なアドバイス\n\n"
        advice += "※ より詳細なアドバイスを得るには、ANTHROPIC_API_KEY環境変数を設定してください。\n\n"
        advice += "1. お互いの強みを活かす役割分担を明確にする\n"
        advice += "2. コミュニケーション方法を事前にすり合わせる\n"
        advice += "3. 定期的な振り返りの機会を設ける\n"
        
        return advice
