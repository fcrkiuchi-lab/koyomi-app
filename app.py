"""
暦 KOYOMI - 対話式人間関係コンサルタント
"""
import sys
import os
import streamlit as st
from datetime import datetime, time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.koyomi.chat.analyzer import IntegratedAnalyzer
from src.koyomi.chat.hearing import PersonProfile
from src.koyomi.chat.session import ConsultationSession
from src.koyomi.chat.export import export_pdf
from src.koyomi.storage.json_store import save_session

# ページ設定
st.set_page_config(
    page_title="暦 KOYOMI - AI人間関係コンサルタント",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "暦 KOYOMI - 運命とは命の運び。依存ではなく、自立のお手伝い。"
    }
)

# CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(160deg, #0a0a1a 0%, #0d1137 30%, #1a1040 60%, #1e0f3c 80%, #0a0a1a 100%);
}
.consultation-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# セッション状態初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """こんにちは。暦 KOYOMI です。

**AI人間関係コンサルタント**として、あなたの意思決定をサポートします。

以下のようなご相談に対応します：
- 採用判断（この人を雇うべきか？）
- チーム編成（このメンバーで新規事業いける？）
- タイミング（今、決断すべきか？）
- パートナーシップ（この人と組むべきか？）
- 人間関係（相性はどうか？）

**まずは、ご相談内容を自由に入力してください。**
""",
        }
    ]

if "consultation_stage" not in st.session_state:
    st.session_state.consultation_stage = "initial"

if "people" not in st.session_state:
    st.session_state.people = []

if "query" not in st.session_state:
    st.session_state.query = ""

if "current_session" not in st.session_state:
    st.session_state.current_session = None

# エンジン初期化（セッション毎）
def get_analyzer():
    """ユーザー毎のAnalyzerインスタンスを取得"""
    api_key = st.session_state.get("api_key")
    
    # API不要モード（自前計算のみ）
    if not api_key:
        return IntegratedAnalyzer(api_key=None)
    
    # APIモード（ユーザー専用）
    return IntegratedAnalyzer(api_key=api_key)

# タイトル
st.title("🏔️ 暦 KOYOMI")
st.caption("AI人間関係コンサルタント - 運命とは命の運び")

# サイドバー: API設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    api_key_input = st.text_input(
        "Anthropic API Key（任意）",
        type="password",
        help="Claude APIを使用してより詳細なアドバイスを生成します"
    )
    
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ API Key設定完了（あなた専用）")
        st.info("詳細なアドバイスが生成されます")
    else:
        st.warning("⚠️ API Key未設定")
        st.info("基本的なアドバイスのみ表示されます")
    
    st.markdown("---")
    
    # データ保存ポリシー
    st.markdown("### 📄 データ保存について")
    st.info("単発利用: データは保存されません（PDF出力のみ）")
    
    if st.button("詳細ポリシーを表示"):
        st.markdown("[データ保存ポリシー](docs/DATA_POLICY.md)")
    
    st.markdown("---")
    
    st.markdown("""
### 使い方
1. 相談内容を入力
2. 関係者の情報を入力
3. AIが分析・アドバイス
4. PDF形式でダウンロード可能

### 相談例
- 「この人を採用すべきか迷っています」
- 「新規事業のチーム編成について」
- 「パートナーと組むべきか判断したい」
""")

# メインエリア
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 相談内容")
    
    # チャット履歴表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # ユーザー入力
    if st.session_state.consultation_stage == "initial":
        if prompt := st.chat_input("相談内容を入力してください"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # メッセージ履歴制限（メモリ圧迫防止）
            if len(st.session_state.messages) > 100:
                st.session_state.messages = st.session_state.messages[-100:]
            
            st.session_state.query = prompt
            
            from src.koyomi.chat.hearing import ConsultationHearing
            hearing = ConsultationHearing()
            consultation_type = hearing.classify_consultation(prompt)
            required_people = hearing.get_required_people(consultation_type)
            
            response = f"""承知しました。

あなたの相談内容：「{prompt}」

関係者の生年月日を教えてください。
右側のフォームに入力してください。

必要な人数: {len(required_people)}人
"""
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.consultation_stage = "collecting"
            st.rerun()

with col2:
    st.header("👥 関係者情報")
    
    if st.session_state.consultation_stage in ["collecting", "analyzing"]:
        num_people = st.number_input(
            "関係者の人数",
            min_value=1,
            max_value=10,
            value=2,
            help="あなた自身を含めた人数"
        )
        
        people_data = []
        
        for i in range(num_people):
            with st.expander(f"👤 {i+1}人目", expanded=(i < 2)):
                name = st.text_input(
                    "名前・役割",
                    value=f"人物{i+1}",
                    key=f"name_{i}",
                    help="例: 私自身、候補者A、既存メンバーB"
                )
                
                col_date, col_time = st.columns([2, 1])
                
                with col_date:
                    birth_date = st.date_input(
                        "生年月日",
                        value=datetime(1990, 1, 1),
                        min_value=datetime(1900, 1, 1),
                        max_value=datetime.now(),
                        key=f"date_{i}"
                    )
                
                with col_time:
                    has_time = st.checkbox(
                        "時刻あり",
                        value=False,
                        key=f"has_time_{i}"
                    )
                
                if has_time:
                    birth_time = st.time_input(
                        "出生時刻",
                        value=time(12, 0),
                        key=f"time_{i}"
                    )
                    birth_dt = datetime.combine(birth_date, birth_time)
                else:
                    birth_dt = datetime.combine(birth_date, time(12, 0))
                
                people_data.append({
                    "name": name,
                    "birth_date": birth_dt,
                    "role": name
                })
        
        with st.expander("📝 追加情報（任意）", expanded=False):
            additional_context = st.text_area(
                "補足情報",
                placeholder="例: プロジェクト期間、業界、現在の状況など",
                height=100
            )
        
        if st.button("🔮 分析開始", type="primary", use_container_width=True):
            if st.session_state.query:
                with st.spinner("分析中..."):
                    people_profiles = [
                        PersonProfile(
                            name=p["name"],
                            role=p["role"],
                            birth_date=p["birth_date"]
                        )
                        for p in people_data
                    ]
                    
                    context_dict = {"additional_info": additional_context} if additional_context else None
                    
                    # ユーザー専用のAnalyzerを取得
                    analyzer = get_analyzer()
                    
                    result = analyzer.analyze_consultation(
                        query=st.session_state.query,
                        people=people_profiles,
                        additional_context=context_dict
                    )
                    
                    # セッション作成（単発: 保存しない）
                    # 将来的にサブスクユーザーの場合はuser_id, expires_atを設定
                    session = ConsultationSession.create(
                        birth_data={"people": [p for p in people_data]},
                        pillars=result['people_analysis'],
                        yojin=[],  # TODO: 複数人の場合の用神
                        metaphor={},  # TODO: 複数人の場合のメタファー
                        query=st.session_state.query,
                        summary=result['advice']
                    )
                    
                    st.session_state.current_session = session
                    
                    advice_message = f"""
## 📊 分析結果

{result['advice']}

---

### 💡 追加で確認したい点

{chr(10).join([f"- {q}" for q in result['follow_up_questions'][:3]])}

これらについても教えていただけると、より詳細なアドバイスが可能です。
"""
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": advice_message
                    })
                    
                    st.session_state.consultation_stage = "analyzing"
                    st.rerun()
        
        # PDF出力ボタン
        if st.session_state.current_session:
            st.markdown("---")
            st.markdown("### 📄 鑑定結果の保存")
            
            if st.button("📥 PDFダウンロード", use_container_width=True):
                with st.spinner("PDF生成中..."):
                    try:
                        pdf_path = export_pdf(st.session_state.current_session)
                        
                        with open(pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="💾 PDFを保存",
                                data=pdf_file,
                                file_name=f"koyomi_{st.session_state.current_session.session_id}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        st.success("✅ PDF生成完了！")
                        st.info("💡 単発利用のため、サーバーにはデータは保存されません")
                        
                    except Exception as e:
                        st.error(f"PDF生成エラー: {e}")
        
        if st.button("🔄 新しい相談", use_container_width=True):
            # セキュリティ: セッションデータをクリア
            st.session_state.consultation_stage = "initial"
            st.session_state.query = ""
            st.session_state.people = []
            st.session_state.current_session = None
            
            # API Keyは保持（ユーザーの利便性のため）
            # 完全クリアする場合: st.session_state.clear()
            
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": """こんにちは。暦 KOYOMI です。

**AI人間関係コンサルタント**として、あなたの意思決定をサポートします。

**まずは、ご相談内容を自由に入力してください。**
""",
                }
            ]
            st.rerun()
    
    else:
        st.info("👈 まずは相談内容を入力してください")

st.markdown("---")
st.caption("暦 KOYOMI - 依存ではなく、自立のお手伝い")
