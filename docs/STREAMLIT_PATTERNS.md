# Streamlit 実装パターン集

## 🎨 暦 KOYOMI の UI パターン

---

## 1️⃣ チャットUI（基本パターン）

### 最小構成（5分で動くプロトタイプ）

```python
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="暦 KOYOMI", page_icon="🌙")

# タイトル
st.title("🌙 暦 KOYOMI")
st.caption("運命とは命の運び")

# セッション状態初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは。生年月日を教えてください。"}
    ]

# 過去の会話を表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ユーザー入力
if prompt := st.chat_input("例：1990-05-15"):
    # ユーザーメッセージ追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # アシスタント応答
    with st.chat_message("assistant"):
        with st.spinner("命式を計算中..."):
            # TODO: meishiki.calculate(prompt) を実装
            response = f"【テスト】{prompt} の鑑定結果を表示します"
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
```

---

## 2️⃣ 日付・時刻入力（柔軟対応版）

### 時刻不明でもOKなUI

```python
import streamlit as st
from datetime import date, time

st.header("📅 生年月日入力")

# 2カラムレイアウト
col1, col2 = st.columns([2, 1])

with col1:
    birth_date = st.date_input(
        "生年月日",
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        help="西暦で入力してください"
    )

with col2:
    time_unknown = st.checkbox("時刻不明", value=False)

# 時刻入力（条件付き表示）
if not time_unknown:
    birth_time = st.time_input(
        "出生時刻",
        value=time(12, 0),
        help="24時間表記で入力"
    )
    st.info("⏰ 四柱推命で鑑定します")
else:
    birth_time = None
    st.warning("⏰ 時刻不明モード：三柱推命で鑑定します")

# 鑑定ボタン
if st.button("🔮 鑑定する", type="primary"):
    with st.spinner("計算中..."):
        if birth_time:
            # 四柱推命
            result = f"四柱推命: {birth_date} {birth_time}"
        else:
            # 三柱推命
            result = f"三柱推命: {birth_date}"
        
        st.success("✅ 鑑定完了")
        st.write(result)
```

---

## 3️⃣ 結果表示（expander活用）

### 結論→詳細の階層表示

```python
import streamlit as st

# 鑑定結果（サンプル）
result = {
    "五行バランス": {"木": 2, "火": 1, "土": 3, "金": 1, "水": 1},
    "調候用神": "甲木生於春月、喜水潤土",
    "メタファー": "豊かな大地に根を張る若木"
}

# 結論（目立たせる）
st.success("### 🌸 あなたの命式")
st.markdown("""
**安定感のある性質**です。  
水の要素を補うことで、さらにバランスが整います。
""")

# 詳細（折りたたみ）
with st.expander("📊 五行バランスの詳細", expanded=False):
    cols = st.columns(5)
    elements = ["木", "火", "土", "金", "水"]
    colors = ["🟢", "🔴", "🟤", "⚪", "🔵"]
    
    for i, elem in enumerate(elements):
        with cols[i]:
            st.metric(
                label=f"{colors[i]} {elem}",
                value=result["五行バランス"][elem]
            )

with st.expander("🔍 調候用神の解説"):
    st.markdown(f"""
    **調候用神**: {result["調候用神"]}
    
    あなたは春生まれの木（甲木）です。  
    成長には水分（水）と栄養豊かな土が必要です。
    """)

with st.expander("💡 メタファー"):
    st.info(result["メタファー"])
```

---

## 4️⃣ ストリーミング表示（AI風演出）

### テキストを1文字ずつ表示

```python
import streamlit as st
import time

def stream_text(text: str, delay: float = 0.02):
    """テキストを1文字ずつ表示"""
    container = st.empty()
    displayed = ""
    
    for char in text:
        displayed += char
        container.markdown(displayed)
        time.sleep(delay)
    
    return displayed

# 使用例
with st.chat_message("assistant"):
    response = "あなたの命式は、豊かな大地に根を張る若木のようです。"
    stream_text(response)
```

### st.write_stream を使う方法（推奨）

```python
import streamlit as st
import time

def response_generator(text: str):
    """ジェネレータでストリーミング"""
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

# 使用例
with st.chat_message("assistant"):
    response = "あなたの命式は、豊かな大地に根を張る若木のようです。"
    st.write_stream(response_generator(response))
```

---

## 5️⃣ サイドバー（設定・履歴管理）

### 設定パネル + 履歴クリア

```python
import streamlit as st

# サイドバー
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 表示モード
    display_mode = st.radio(
        "表示モード",
        ["シンプル", "詳細", "専門家向け"],
        help="鑑定結果の詳しさを選択"
    )
    
    # メタファータイプ
    metaphor_type = st.selectbox(
        "メタファー種類",
        ["自然", "都市", "人間関係"],
        help="五行の比喩表現スタイル"
    )
    
    st.divider()
    
    # 履歴管理
    st.header("📜 履歴")
    
    if st.button("🗑️ 会話履歴をクリア", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # 鑑定回数表示
    if "messages" in st.session_state:
        count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.caption(f"鑑定回数: {count}回")
```

---

## 6️⃣ プログレス表示（計算中の演出）

### スピナー + プログレスバー

```python
import streamlit as st
import time

if st.button("🔮 鑑定する"):
    with st.spinner("命式を計算中..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # ステップ1
        status_text.text("📅 生年月日から干支を計算...")
        time.sleep(0.5)
        progress_bar.progress(25)
        
        # ステップ2
        status_text.text("🌳 五行バランスを分析...")
        time.sleep(0.5)
        progress_bar.progress(50)
        
        # ステップ3
        status_text.text("🔥 調候用神を判定...")
        time.sleep(0.5)
        progress_bar.progress(75)
        
        # ステップ4
        status_text.text("✨ 鑑定結果を生成...")
        time.sleep(0.5)
        progress_bar.progress(100)
        
        status_text.empty()
        progress_bar.empty()
    
    st.success("✅ 鑑定完了！")
```

---

## 7️⃣ エラーハンドリング

### ユーザーフレンドリーなエラー表示

```python
import streamlit as st
from datetime import datetime

try:
    # 日付パース
    user_input = st.text_input("生年月日（例：1990-05-15）")
    
    if user_input:
        birth_date = datetime.strptime(user_input, "%Y-%m-%d").date()
        st.success(f"✅ {birth_date} で計算します")

except ValueError:
    st.error("""
    ❌ 日付形式が正しくありません。
    
    **正しい形式**: YYYY-MM-DD  
    **例**: 1990-05-15
    """)

except Exception as e:
    st.error(f"予期しないエラーが発生しました: {e}")
    st.info("お手数ですが、もう一度お試しください。")
```

---

## 8️⃣ レスポンシブデザイン

### モバイル・PC両対応

```python
import streamlit as st

# ビューポート設定
st.set_page_config(
    page_title="暦 KOYOMI",
    page_icon="🌙",
    layout="centered",  # "wide" or "centered"
    initial_sidebar_state="collapsed"  # モバイルでサイドバー非表示
)

# カスタムCSS（モバイル最適化）
st.markdown("""
<style>
    /* モバイル対応 */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            font-size: 1.2em;
        }
        
        .stChatInput {
            font-size: 16px;  /* iOS のズーム防止 */
        }
    }
    
    /* ダークモード対応 */
    @media (prefers-color-scheme: dark) {
        .stMarkdown {
            color: #e0e0e0;
        }
    }
</style>
""", unsafe_allow_html=True)
```

---

## 9️⃣ キャッシング（パフォーマンス最適化）

### 計算結果のキャッシュ

```python
import streamlit as st
from datetime import date

@st.cache_data(ttl=3600)  # 1時間キャッシュ
def calculate_meishiki(birth_date: date, birth_time=None):
    """四柱推命計算（重い処理）"""
    # TODO: 実装
    import time
    time.sleep(2)  # 計算シミュレーション
    return {"五行": "木2, 火1, 土3, 金1, 水1"}

# 使用例
birth_date = st.date_input("生年月日")

if st.button("鑑定"):
    # 初回は計算、2回目以降はキャッシュから取得
    result = calculate_meishiki(birth_date)
    st.write(result)
```

### JSON データのキャッシュ

```python
import streamlit as st
import json

@st.cache_resource
def load_taizan_data():
    """泰山流データベース読み込み（起動時1回のみ）"""
    with open("data/taizan.json", encoding="utf-8") as f:
        return json.load(f)

# 全ページで共有
taizan_db = load_taizan_data()
```

---

## 🔟 マルチページアプリ

### ページ構成

```
koyomi-project/
├── app.py              # メインページ（鑑定）
└── pages/
    ├── 1_履歴.py       # 鑑定履歴
    ├── 2_設定.py       # 詳細設定
    └── 3_ヘルプ.py     # 使い方ガイド
```

### app.py（メインページ）

```python
import streamlit as st

st.set_page_config(
    page_title="暦 KOYOMI",
    page_icon="🌙",
    layout="centered"
)

st.title("🌙 暦 KOYOMI")

# ナビゲーション
st.sidebar.page_link("app.py", label="🔮 鑑定")
st.sidebar.page_link("pages/1_履歴.py", label="📜 履歴")
st.sidebar.page_link("pages/2_設定.py", label="⚙️ 設定")
st.sidebar.page_link("pages/3_ヘルプ.py", label="❓ ヘルプ")

# メインコンテンツ
# （チャットUIなど）
```

### pages/1_履歴.py

```python
import streamlit as st

st.title("📜 鑑定履歴")

# セッション状態から履歴取得
if "messages" in st.session_state:
    history = [m for m in st.session_state.messages if m["role"] == "user"]
    
    if history:
        for i, msg in enumerate(history, 1):
            with st.expander(f"鑑定 #{i}: {msg['content'][:20]}..."):
                st.markdown(msg['content'])
    else:
        st.info("まだ鑑定履歴がありません")
else:
    st.warning("セッションが見つかりません")
```

---

## 🎯 実践：フル実装サンプル

### 統合版（app.py）

```python
import streamlit as st
from datetime import date, time, datetime
import json

# ページ設定
st.set_page_config(
    page_title="暦 KOYOMI",
    page_icon="🌙",
    layout="centered"
)

# セッション状態初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは。生年月日を教えてください。"}
    ]

# タイトル
st.title("🌙 暦 KOYOMI")
st.caption("運命とは命の運び。足元を照らし、選択をサポートします。")

# サイドバー
with st.sidebar:
    st.header("⚙️ 設定")
    
    display_mode = st.radio(
        "表示モード",
        ["シンプル", "詳細"],
        help="鑑定結果の詳しさ"
    )
    
    st.divider()
    
    if st.button("🗑️ 履歴クリア", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "履歴をクリアしました。"}
        ]
        st.rerun()

# チャット履歴表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ユーザー入力
if prompt := st.chat_input("例：1990-05-15 または 1990-05-15 14:30"):
    # ユーザーメッセージ追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # アシスタント応答
    with st.chat_message("assistant"):
        try:
            # 日付パース
            if " " in prompt:
                # 時刻あり
                dt = datetime.strptime(prompt, "%Y-%m-%d %H:%M")
                mode = "四柱推命"
            else:
                # 時刻なし
                dt = datetime.strptime(prompt, "%Y-%m-%d")
                mode = "三柱推命"
            
            with st.spinner(f"{mode}で計算中..."):
                # TODO: meishiki.calculate(dt)
                
                response = f"""
### 🌸 {dt.strftime('%Y年%m月%d日')} 生まれの方

**{mode}モード**で鑑定しました。

**結論**: あなたの命式は安定感のある性質です。

---

（ここに詳細結果を表示）
                """
                
                if display_mode == "詳細":
                    with st.expander("📊 五行バランス"):
                        cols = st.columns(5)
                        elements = ["木", "火", "土", "金", "水"]
                        for i, elem in enumerate(elements):
                            cols[i].metric(elem, i+1)
                
                st.markdown(response)
        
        except ValueError:
            response = """
❌ 日付形式が正しくありません。

**正しい形式**:
- 日付のみ: `1990-05-15`
- 時刻含む: `1990-05-15 14:30`
            """
            st.error(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
```

---

## 📚 参考リンク

- [Streamlit 公式ドキュメント](https://docs.streamlit.io/)
- [チャットアプリ チュートリアル](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps)
- [Session State ガイド](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)

---

**Streamlit で、暦を美しく表現しよう** 🎨
