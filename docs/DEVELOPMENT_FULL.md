# 暦 KOYOMI 開発ガイド

## 🎯 このドキュメントについて

実装の詳細、アーキテクチャ設計、開発フローをまとめた技術資料です。

---

## 📐 アーキテクチャ設計

### システム構成図

```
┌─────────────────┐
│  Streamlit UI   │ ← ユーザー入力（日付・時刻）
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  meishiki.py    │ ← 四柱推命計算エンジン
│  ・干支変換     │
│  ・五行判定     │
│  ・バランス計算 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  taizan.py      │ ← 泰山流調候用神判定
│  ・120通り照合  │
│  ・用神判定     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Claude Skill    │ ← 結果解釈（オプション）
│ ・自然言語化    │
│ ・メタファー生成│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit UI   │ ← チャット形式で表示
└─────────────────┘
```

---

## 🗂️ モジュール詳細

### 1. meishiki.py（計算エンジン）

**責務**：生年月日から四柱推命の基本情報を計算

```python
from datetime import date, time
from typing import Optional

def calculate_meishiki(
    birth_date: date,
    birth_time: Optional[time] = None
) -> dict:
    """
    四柱推命計算メイン関数
    
    Args:
        birth_date: 生年月日
        birth_time: 出生時刻（Noneの場合は三柱推命）
    
    Returns:
        {
            "年柱": {"干": "庚", "支": "午"},
            "月柱": {"干": "辛", "支": "巳"},
            "日柱": {"干": "甲", "支": "寅"},
            "時柱": {"干": "丙", "支": "寅"} or None,
            "五行": {"木": 2, "火": 1, "土": 3, "金": 1, "水": 1},
            "モード": "四柱推命" or "三柱推命"
        }
    """
    # 実装
    pass

def get_stem_branch(date: date) -> dict:
    """日付から干支を取得"""
    pass

def calculate_wuxing_balance(stems: list, branches: list) -> dict:
    """五行バランスを計算"""
    pass
```

---

### 2. taizan.py（泰山流ロジック）

**責務**：調候用神の判定

```python
def get_tiaohuo_yongshen(
    day_stem: str,
    month_branch: str,
    wuxing_balance: dict
) -> dict:
    """
    調候用神を判定
    
    Args:
        day_stem: 日干（甲〜癸の10種）
        month_branch: 月支（子〜亥の12種）
        wuxing_balance: 五行バランス
    
    Returns:
        {
            "用神": "水",
            "説明": "甲木生於春月、喜水潤土",
            "理由": "春の木は水分が必要"
        }
    """
    # data/taizan.json から照合
    pass
```

**データ構造**：`data/taizan.json`

```json
{
  "甲": {
    "子月": {
      "用神": "火",
      "説明": "甲木生於冬月、寒木向陽、喜火暖局"
    },
    "丑月": {
      "用神": "火",
      "説明": "..."
    }
  }
}
```

---

### 3. metaphor.py（メタファー生成）

**責務**：五行バランスを比喩表現に変換

```python
def generate_metaphor(
    wuxing_balance: dict,
    style: str = "nature"
) -> str:
    """
    メタファー生成
    
    Args:
        wuxing_balance: {"木": 2, "火": 1, ...}
        style: "nature" | "urban" | "human"
    
    Returns:
        "あなたの命式は、豊かな大地に根を張る若木のようです..."
    """
    if style == "nature":
        return _nature_metaphor(wuxing_balance)
    elif style == "urban":
        return _urban_metaphor(wuxing_balance)
    else:
        return _human_metaphor(wuxing_balance)
```

---

## 🧪 テスト戦略

### テストピラミッド

```
        ┌──────────┐
        │  E2E (5%) │  Streamlitアプリ全体
        └──────────┘
       ┌─────────────┐
       │Integration  │  モジュール間連携
       │   (15%)     │
       └─────────────┘
    ┌──────────────────┐
    │   Unit Tests     │  個別関数
    │     (80%)        │
    └──────────────────┘
```

### ユニットテスト例

```python
# tests/test_meishiki.py
import pytest
from datetime import date
from src.meishiki import calculate_meishiki

def test_四柱推命_完全データ():
    """時刻ありの完全な四柱推命"""
    result = calculate_meishiki(
        birth_date=date(1990, 5, 15),
        birth_time=time(14, 30)
    )
    
    assert result["モード"] == "四柱推命"
    assert result["時柱"] is not None
    assert len(result["五行"]) == 5
    assert sum(result["五行"].values()) == 8  # 4柱×2

def test_三柱推命_時刻不明():
    """時刻なしの三柱推命"""
    result = calculate_meishiki(
        birth_date=date(1990, 5, 15)
    )
    
    assert result["モード"] == "三柱推命"
    assert result["時柱"] is None
    assert sum(result["五行"].values()) == 6  # 3柱×2

def test_無効な日付():
    """エラーハンドリング"""
    with pytest.raises(ValueError):
        calculate_meishiki(date(9999, 99, 99))
```

---

## 🔄 開発フロー

### 1. 機能追加の手順

```bash
# 1. ブランチ作成
git checkout -b feature/metaphor-generator

# 2. テスト作成（TDD）
vim tests/test_metaphor.py

# 3. 実装
vim src/utils/metaphor.py

# 4. テスト実行
pytest tests/test_metaphor.py -v

# 5. コミット
git add .
git commit -m "feat: メタファー生成機能追加"

# 6. プッシュ
git push origin feature/metaphor-generator
```

### 2. コード品質チェック

```bash
# フォーマット（自動修正）
black src/ tests/
isort src/ tests/

# 静的解析
flake8 src/ tests/
mypy src/

# テストカバレッジ
pytest --cov=src tests/
```

---

## 📊 データフロー詳細

### 入力 → 出力の流れ

```
1. ユーザー入力
   "1990-05-15 14:30"
   
2. パース処理（app.py）
   datetime(1990, 5, 15, 14, 30)
   
3. 四柱推命計算（meishiki.py）
   {
     "年柱": {"干": "庚", "支": "午"},
     "月柱": {"干": "辛", "支": "巳"},
     "日柱": {"干": "甲", "支": "寅"},
     "時柱": {"干": "丙", "支": "寅"},
     "五行": {"木": 2, "火": 1, "土": 3, "金": 1, "水": 1}
   }
   
4. 調候用神判定（taizan.py）
   {
     "用神": "水",
     "説明": "甲木生於春月、喜水潤土"
   }
   
5. 結果統合
   {
     "命式": {...},
     "調候用神": {...},
     "生年月日": "1990-05-15",
     "モード": "四柱推命"
   }
   
6. 解釈生成（Claude Skill / metaphor.py）
   "あなたの命式は、豊かな大地に..."
   
7. UI表示（app.py）
   st.markdown(response)
```

---

## 🎨 UI/UX 設計原則

### 1. レスポンシブデザイン

```python
# モバイル・PC両対応
st.set_page_config(layout="centered")  # 最大幅900px

# カスタムCSS
st.markdown("""
<style>
    @media (max-width: 768px) {
        /* モバイル最適化 */
        .stButton > button {
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)
```

### 2. 段階的開示

```python
# 結論を先に
st.success("あなたの命式は安定感のある性質です。")

# 詳細は折りたたみ
with st.expander("詳しく見る"):
    st.write("五行バランス: ...")
```

### 3. エラーハンドリング

```python
try:
    result = calculate_meishiki(user_input)
except ValueError as e:
    st.error(f"❌ {str(e)}")
    st.info("💡 正しい形式: 1990-05-15")
```

---

## 🔐 セキュリティ考慮事項

### 1. 入力検証

```python
def validate_date(date_str: str) -> date:
    """日付の妥当性チェック"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("日付形式が正しくありません")
    
    # 範囲チェック
    if dt < date(1900, 1, 1) or dt > date.today():
        raise ValueError("1900年〜現在の範囲で入力してください")
    
    return dt
```

### 2. 環境変数管理（API使用時）

```python
# .env（Git管理外）
ANTHROPIC_API_KEY=sk-ant-...

# app.py
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

### 3. ログ管理

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 個人情報はログに残さない
logger.info("鑑定実行")  # OK
logger.info(f"入力: {birth_date}")  # NG
```

---

## 🚀 デプロイ戦略

### Streamlit Cloud（推奨）

```bash
# 1. GitHubにプッシュ
git push origin main

# 2. Streamlit Cloudで接続
# https://share.streamlit.io/

# 3. アプリURL取得
# https://your-app.streamlit.app/
```

### ローカル実行

```bash
# 開発環境
streamlit run src/app.py

# 本番相当（キャッシュ有効）
streamlit run src/app.py --server.enableCORS=false
```

---

## 📈 パフォーマンス最適化

### 1. キャッシング

```python
@st.cache_data(ttl=3600)
def load_taizan_database():
    """起動時1回のみ読み込み"""
    with open("data/taizan.json") as f:
        return json.load(f)

@st.cache_data
def calculate_meishiki(birth_date: date):
    """同じ入力は再計算しない"""
    # 重い計算処理
    pass
```

### 2. 遅延ロード

```python
# 必要になってから読み込む
def get_metaphor():
    from utils.metaphor import generate_metaphor
    return generate_metaphor(...)
```

---

## 🐛 デバッグ Tips

### Streamlit デバッグ

```python
# セッション状態確認
st.sidebar.write(st.session_state)

# 変数の中身確認
st.json(result)

# エラートレースバック
import traceback
try:
    # 処理
except Exception as e:
    st.error(traceback.format_exc())
```

### ログ出力

```python
# 開発環境のみ
if os.getenv("ENV") == "development":
    print(f"Debug: {result}")
```

---

## 📚 参考資料

### 公式ドキュメント
- [Streamlit Docs](https://docs.streamlit.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Python datetime](https://docs.python.org/3/library/datetime.html)

### 内部ドキュメント
- [Claude Skills ガイド](CLAUDE_SKILLS.md)
- [Streamlit パターン集](STREAMLIT_PATTERNS.md)

### 泰山流四柱推命
- 泰山流調候用神理論書（書籍参照）
- `data/taizan.json`（120通りのデータ）

---

## ❓ FAQ

### Q. Claude APIは必須ですか？
A. いいえ。基本機能（計算・判定）は自前実装で動作します。API は結果の自然言語化のみオプションです。

### Q. オフライン動作しますか？
A. はい。API不使用なら完全オフライン動作します。

### Q. 商用利用できますか？
A. ライセンス次第です。MIT Licenseを想定。

### Q. 他の占術と組み合わせられますか？
A. 設計上可能です。Layer2-4（西洋占星術等）の実装を想定しています。

---

**開発を楽しみ、暦の知恵を広げよう** 🌙
