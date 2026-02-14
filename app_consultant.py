"""
暦 KOYOMI - 対話式人間関係コンサルタント
"""
import sys
import streamlit as st
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.koyomi.chat.interviewer import Interviewer
from src.koyomi.chat.advice import AdviceGenerator
from src.koyomi.layer1.engine import MeishikiEngine

# ページ設定
st.set_page_config(
    page_title="暦 KOYOMI - 人間関係コンサルタント",
    page_icon="🏔️",
    layout="centered",
)

# CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(160deg, #0a0a1a 0%, #0d1137 30%, #1a1040 60%, #1e0f3c 80%, #0a0a1a 100%);
}
.big-decision {
    font-size: 1.5em;
    font-weight: bold;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
}
.decision-yes {
    background-color: #1e4d2b;
    color: #90ee90;
}
.decision-caution {
    background-color: #4d3a1e;
    color: #ffd700;
}
.decision-no {
    background-color: #4d1e1e;
    color: #ffcccb;
}
</style>
""", unsafe_allow_html=True)

# エンジン初期化
@st.cache_resource
def load_engines():
    return {
        "meishiki": MeishikiEngine(),
        "interviewer": None,  # セッションごとに生成
        "advice": AdviceGenerator(use_claude_api=False)  # デフォルトはルールベース
    }

engines = load_engines()

# セッション状態初期化
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.interviewer = Interviewer()
    st.session_state.analysis_complete = False
    
    # 初回メッセージ
    welcome = """
こんにちは。暦 KOYOMI です。

**人間関係の意思決定をサポート**します。

例えば：
- 「この人を採用すべきか？」
- 「このパートナーと組んで大丈夫？」
- 「今のチームで新規事業いける？」
- 「今、決断すべきタイミングか？」

どんなご相談でしょうか？
"""
    st.session_state.messages.append({
        "role": "assistant",
        "content": welcome
    })

# タイトル
st.title("🏔️ 暦 KOYOMI")
st.caption("AI人間関係コンサルタント - 意思決定をサポート")

# サイドバー: Claude API設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    use_claude = st.checkbox(
        "Claude API を使用",
        help="より詳細なアドバイスが得られます（API Key必要）"
    )
    
    if use_claude:
        api_key = st.text_input(
            "ANTHROPIC_API_KEY",
            type="password",
            help="https://console.anthropic.com/ で取得"
        )
        if api_key:
            import os
            os.environ["ANTHROPIC_API_KEY"] = api_key
            engines["advice"] = AdviceGenerator(use_claude_api=True)
            st.success("✅ Claude API有効")
    
    st.divider()
    
    st.markdown("""
### 💡 使い方

1. 相談内容を自由に入力
2. 段階的に質問に回答
3. 的確なアドバイスを受け取る

### 📊 対応する相談

- ✅ 採用判断
- ✅ パートナー選定
- ✅ チーム編成
- ✅ タイミング判断
- ✅ 相性確認
""")

# チャット履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 分析完了後の表示
if st.session_state.analysis_complete:
    with st.chat_message("assistant"):
        st.success("✅ 分析完了")
        
        if st.button("🔄 新しい相談を始める"):
            # リセット
            st.session_state.messages = []
            st.session_state.interviewer = Interviewer()
            st.session_state.analysis_complete = False
            st.rerun()
    
    st.stop()

# ユーザー入力
if prompt := st.chat_input("ご相談内容を入力してください"):
    # ユーザーメッセージ追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # ヒアリング処理
    interviewer = st.session_state.interviewer
    response = interviewer.process_answer(prompt)
    
    # アシスタント応答
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
    
    # ヒアリング完了チェック
    if interviewer.state.is_complete():
        with st.chat_message("assistant"):
            with st.spinner("🔮 命式を分析中..."):
                # TODO: 実際の命式計算と相性分析
                # 現在はダミーデータ
                meishiki_data = {
                    "person1": {"日干": "丙", "五行": {"火": 3, "土": 2, "木": 1, "金": 1, "水": 1}},
                    "person2": {"日干": "癸", "五行": {"水": 3, "金": 2, "木": 1, "火": 1, "土": 1}}
                }
                
                compatibility_data = {
                    "score": 75,
                    "relation": "相補関係",
                    "roles": {"person1": "リーダー", "person2": "サポート"}
                }
                
                # アドバイス生成
                advice = engines["advice"].generate_advice(
                    consultation_type=interviewer.state.consultation_type,
                    meishiki_data=meishiki_data,
                    compatibility_data=compatibility_data,
                    question=prompt
                )
                
                # 結果表示
                st.markdown("---")
                st.markdown("## 🎯 分析結果")
                st.markdown(advice)
        
        # 完了フラグ
        st.session_state.analysis_complete = True
        st.rerun()
