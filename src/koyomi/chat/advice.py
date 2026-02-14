"""
アドバイス生成エンジン
四柱推命の分析結果をClaude APIで自然言語化
"""
import os
from typing import Dict, List


class AdviceGenerator:
    """的確なアドバイスを生成"""
    
    # アドバイスのテンプレート（相談タイプ別）
    ADVICE_TEMPLATES = {
        "採用": """
【判断】
{decision}

【理由】
{reason}

【具体的なアドバイス】
{specific_advice}

【リスクと対策】
{risks}

【タイミング】
{timing}
""",
        "パートナー選定": """
【結論】
{decision}

【相性分析】
{compatibility}

【役割分担の提案】
{roles}

【注意点】
{warnings}

【成功のポイント】
{success_tips}
""",
        "チーム編成": """
【このチームの評価】
{evaluation}

【強み】
{strengths}

【弱点】
{weaknesses}

【最適な役割分担】
{role_assignment}

【補強すべき点】
{improvements}
""",
        "タイミング判断": """
【総合判断】
{decision}

【運気の流れ】
{fortune_flow}

【推奨タイミング】
{recommended_timing}

【避けるべき時期】
{avoid_timing}

【準備すべきこと】
{preparation}
""",
    }
    
    def __init__(self, use_claude_api: bool = False):
        """
        Args:
            use_claude_api: Claude APIを使用するか（Falseの場合はルールベース）
        """
        self.use_claude_api = use_claude_api
        
        if use_claude_api:
            # 本番環境用（Claude API）
            try:
                from anthropic import Anthropic
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    print("警告: ANTHROPIC_API_KEYが設定されていません。ルールベースで動作します。")
                    self.use_claude_api = False
                else:
                    self.client = Anthropic(api_key=api_key)
            except ImportError:
                print("警告: anthropicパッケージがインストールされていません。ルールベースで動作します。")
                self.use_claude_api = False
    
    def generate_advice(
        self,
        consultation_type: str,
        meishiki_data: Dict,
        compatibility_data: Dict,
        question: str
    ) -> str:
        """
        アドバイスを生成
        
        Args:
            consultation_type: 相談タイプ
            meishiki_data: 命式データ
            compatibility_data: 相性データ
            question: 具体的な質問
        
        Returns:
            自然言語のアドバイス
        """
        if self.use_claude_api:
            return self._generate_with_claude_api(
                consultation_type,
                meishiki_data,
                compatibility_data,
                question
            )
        else:
            return self._generate_rule_based(
                consultation_type,
                meishiki_data,
                compatibility_data
            )
    
    def _generate_with_claude_api(
        self,
        consultation_type: str,
        meishiki_data: Dict,
        compatibility_data: Dict,
        question: str
    ) -> str:
        """
        Claude APIを使用してアドバイス生成
        """
        system_prompt = f"""
あなたは四柱推命の専門家であり、経営コンサルタントです。

以下の情報をもとに、経営者が意思決定できるレベルの具体的で実用的なアドバイスをしてください。

【命式データ】
{meishiki_data}

【相性・関係性データ】
{compatibility_data}

【相談タイプ】
{consultation_type}

【アドバイスの条件】
1. 最初に明確な結論（Yes/No/条件付き）
2. 専門用語は最小限に抑える
3. 具体的な行動を3つ示す
4. タイミングも明示する
5. リスクも正直に伝える
6. 「なぜそう判断したか」を論理的に説明
7. 経営者が意思決定できる情報密度

【禁止事項】
- 曖昧な表現（「かもしれません」など）
- 占い師風の神秘的な言い回し
- 無責任な楽観論
"""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            print(f"Claude API エラー: {e}")
            return self._generate_rule_based(
                consultation_type,
                meishiki_data,
                compatibility_data
            )
    
    def _generate_rule_based(
        self,
        consultation_type: str,
        meishiki_data: Dict,
        compatibility_data: Dict
    ) -> str:
        """
        ルールベースでアドバイス生成（API不使用時）
        """
        # 採用判断の例
        if consultation_type == "採用":
            score = compatibility_data.get("score", 50)
            
            if score >= 70:
                decision = "✅ 採用を推奨します"
                reason = f"相性スコア {score}% - 既存チームとの調和が期待できます"
            elif score >= 50:
                decision = "⚠️ 条件付きで推奨"
                reason = f"相性スコア {score}% - 適切なフォローがあれば問題ありません"
            else:
                decision = "❌ 慎重な検討が必要"
                reason = f"相性スコア {score}% - チーム内の役割を明確にする必要があります"
            
            # 具体的なアドバイス
            advice = self._get_specific_hiring_advice(meishiki_data, compatibility_data)
            
            return self.ADVICE_TEMPLATES["採用"].format(
                decision=decision,
                reason=reason,
                specific_advice=advice["specific"],
                risks=advice["risks"],
                timing=advice["timing"]
            )
        
        # その他のタイプも同様に実装
        return f"【{consultation_type}】の分析結果\n\n相性スコア: {compatibility_data.get('score', 50)}%"
    
    def _get_specific_hiring_advice(
        self,
        meishiki_data: Dict,
        compatibility_data: Dict
    ) -> Dict:
        """
        採用に関する具体的なアドバイス
        """
        return {
            "specific": """
1. 最初の3ヶ月は週1回の1on1を設定
   → 既存メンバーとの関係構築をサポート

2. 明確な役割定義を初日から
   → 曖昧さが摩擦の原因になります

3. Aさんをバディに指名
   → 五行のバランスから最適な組み合わせです
""",
            "risks": """
・最初の1ヶ月で判断しない
  → 慣れるまで時間がかかるタイプです

・コミュニケーションスタイルの違い
  → 定期的なフィードバック機会を設ける
""",
            "timing": """
・入社時期: 来月上旬が吉
・本格始動: 入社後2週間は研修期間に
・評価タイミング: 3ヶ月後、6ヶ月後
"""
        }
