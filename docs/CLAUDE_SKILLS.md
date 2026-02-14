# Claude Skills 活用ガイド

## 📖 Skills とは？

**繰り返す作業をパッケージ化**して、Claudeが自動で実行してくれる機能。

### 特徴
- ✅ **コード不要** - Markdownで指示を書くだけ
- ✅ **自動起動** - タスクに応じて適切なスキルを選択
- ✅ **チーム共有** - GitでSkillを管理・配布可能
- ✅ **無料プランOK** - Pro/Max不要

---

## 🎯 暦 KOYOMI での活用例

### 1. 鑑定結果解釈スキル

**ファイル**: `.claude/skills/koyomi-interpretation/SKILL.md`

```markdown
---
name: koyomi-interpretation
description: 四柱推命の計算結果を、優しい日本語で解釈・説明する
---

# 四柱推命 鑑定結果解釈スキル

## 目的
meishiki.pyの出力（五行バランス、調候用神等）を受け取り、
ユーザーに分かりやすく伝える。

## 入力形式
```json
{
  "五行バランス": {"木": 2, "火": 1, "土": 3, "金": 1, "水": 1},
  "調候用神": "甲木生於春月、喜水潤土",
  "生年月日": "1990-05-15",
  "時刻": "14:30"
}
```

## 出力形式

### 1. 結論（2-3文）
- 最も重要なポイントを先に伝える
- 専門用語は使わない

例：
「あなたの命式は土のエネルギーが強く、安定感のある性質です。
水の要素を補うことで、さらにバランスが整います。」

### 2. 詳細解説（expander推奨）
- 五行それぞれの意味
- 調候用神の解説
- 実生活への応用

### 3. メタファー（選択肢）
五行をわかりやすい比喩で表現：
- 木：成長する樹木、上昇志向
- 火：情熱、華やかさ
- 土：安定、包容力
- 金：鋭さ、理論性
- 水：柔軟性、知恵

## 禁止事項
- ❌ 断定的な未来予測（「〜になります」）
- ❌ 依存を促す表現（「この日しかダメ」）
- ✅ 選択肢を示す（「〜という考え方もあります」）

## 哲学
運命とは命の運び。
「決まっていること」ではなく、「どう運ぶか」を照らす。
```

---

### 2. メタファー生成スキル

**ファイル**: `.claude/skills/koyomi-metaphor/SKILL.md`

```markdown
---
name: koyomi-metaphor
description: 五行バランスを現代的な比喩で表現
---

# メタファー生成スキル

## 入力
五行バランス（例：木2, 火1, 土3, 金1, 水1）

## 出力例

### パターンA：自然の風景
「あなたの命式は、豊かな大地（土）に根を張る若木（木）のようです。
時折、静かな小川（水）が流れ、穏やかな日差し（火）が降り注ぎます。」

### パターンB：都市の比喩
「安定した基盤（土）の上に建つビル（木）。
時に情熱（火）が灯り、冷静な判断（金）が働き、柔軟な対応（水）も可能です。」

### パターンC：人間関係
「包容力のある（土）性格で、成長意欲（木）も持ち合わせています。
情熱（火）を適度に保ち、論理性（金）と柔軟性（水）でバランスを取ります。」

## 選定基準
- ユーザーの年齢層に応じる（推測可能な場合）
- シンプルで印象に残る表現
- ポジティブな解釈を優先
```

---

## 🛠️ Skills の使い方

### A. Claudeアプリでの使用

1. **アップロード**
```
Settings → Capabilities → Skills → Upload
```

2. **有効化**
スキル一覧でトグルON

3. **自動起動**
通常の会話で自動的に適用される
```
User: "1990年5月15日生まれの鑑定結果を解釈して"
Claude: [koyomi-interpretationスキルを起動]
```

---

### B. Claude Code での使用

1. **プロジェクトルートに配置**
```bash
mkdir -p .claude/skills/koyomi-interpretation
# SKILL.mdを配置
```

2. **自動認識**
Claude Codeが自動でスキルを検出

3. **手動起動（オプション）**
```bash
/skill koyomi-interpretation
```

---

### C. API での使用

```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_KEY")

# Skillファイルを読み込み
with open(".claude/skills/koyomi-interpretation/SKILL.md") as f:
    skill_content = f.read()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": skill_content  # スキルを system prompt に注入
        }
    ],
    messages=[
        {
            "role": "user", 
            "content": "五行バランス: 木2, 火1, 土3, 金1, 水1 を解釈して"
        }
    ]
)

print(message.content)
```

---

## 📊 Skills vs 他の手法

| 手法 | 使い分け |
|------|---------|
| **Skills** | 繰り返し使う定型作業（鑑定解釈、メタファー生成） |
| **Custom Instructions** | 全体的な話し方の設定（「敬語で」「簡潔に」） |
| **Projects** | 長期的なコンテキスト保持（1つの顧客との連続セッション） |
| **通常プロンプト** | 一回限りのタスク |

---

## 🎓 スキル作成のベストプラクティス

### 1. description を明確に
```markdown
# 悪い例
description: 四柱推命のスキル

# 良い例
description: 四柱推命の計算結果（JSON形式）を受け取り、ユーザーに優しい日本語で解釈・説明する
```

### 2. 具体例を含める
```markdown
## 入力例
{"五行バランス": {...}}

## 出力例
「あなたの命式は...」
```

### 3. 禁止事項を明記
```markdown
## 禁止事項
- ❌ 断定的表現
- ✅ 選択肢を示す
```

### 4. 段階的詳細（Progressive Disclosure）
```markdown
---
name: koyomi
description: 短い説明（200字以内） ← Claude が最初に読む
---

# 詳細な指示 ← 必要に応じて読む

## サンプル ← さらに詳しく

### templates/ ← ファイル分割も可
```

---

## 🔄 スキルの更新ワークフロー

```bash
# 1. スキル編集
vim .claude/skills/koyomi-interpretation/SKILL.md

# 2. テスト（Claude Codeで）
/skill koyomi-interpretation
"テスト用の鑑定データで動作確認"

# 3. コミット
git add .claude/skills/
git commit -m "feat: 鑑定解釈スキル更新 - メタファー追加"

# 4. チーム共有
git push origin main
```

---

## 💡 実践例：フルワークフロー

### シナリオ
ユーザーが生年月日を入力 → 四柱推命計算 → Claude Skillで解釈

### Streamlit アプリ（app.py）
```python
import streamlit as st
import anthropic
import json
from meishiki import calculate

# 入力
birth_date = st.date_input("生年月日")

if st.button("鑑定"):
    # 計算
    result = calculate(birth_date)
    
    # Skillで解釈（API使用の場合）
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])
    
    with open(".claude/skills/koyomi-interpretation/SKILL.md") as f:
        skill = f.read()
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=[{"type": "text", "text": skill}],
        messages=[{
            "role": "user",
            "content": f"以下の鑑定結果を解釈してください：\n{json.dumps(result, ensure_ascii=False)}"
        }]
    )
    
    st.markdown(message.content[0].text)
```

---

## 🌟 応用アイデア

### 1. 多言語対応スキル
```markdown
---
name: koyomi-en
description: Interpret shichusuimei results in English
---
```

### 2. レポート生成スキル
```markdown
---
name: koyomi-report
description: 月次運勢レポートをPDF形式で生成
dependencies: reportlab
---
```

### 3. データ分析スキル
```markdown
---
name: koyomi-stats
description: 過去の鑑定データから統計分析
---
```

---

## 📚 参考リンク

- [Agent Skills 公式仕様](https://agentskills.io/)
- [Anthropic Skills ドキュメント](https://docs.claude.com/en/docs/claude-code/skills)
- [Skills ディレクトリ](https://claude.com/connectors)

---

**Skills で、暦の知恵を自動化しよう** ✨
