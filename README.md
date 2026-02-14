# 📅 暦 KOYOMI

**四柱推命ベースの多層占術統合システム（TDD準拠）**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)]()

---

## 🌟 特徴

- **完全自前計算**: API不要、コスト0円
- **時刻不明対応**: 三柱推命モードあり
- **TDD準拠**: テスト駆動開発で高品質保証
- **多層統合**: 東洋・西洋の占術を統合（予定）
- **メタファー辞書120通り**: 日干×月支の全組み合わせ完備
- **Claude Skills対応**: 鑑定解釈の自動化
- **Streamlitパターン集**: 10種類以上のUI実装例

---

## 🚀 クイックスタート

### 1. インストール

```bash
# 依存パッケージインストール
make install

# または
pip install -r requirements.txt --break-system-packages
```

### 2. テスト実行

```bash
# 全テスト実行
make test

# カバレッジ確認
make coverage
```

### 3. アプリ起動

```bash
make run

# または
streamlit run app.py
```

---

## 📂 プロジェクト構造

```
koyomi/
├── .claude/                # Claude Code設定
│   ├── CLAUDE.md           # プロジェクト概要・規約
│   └── skills/koyomi/      # 鑑定解釈スキル
│       └── SKILL.md
├── src/koyomi/             # ソースコード
│   ├── core/               # 共通ロジック
│   │   ├── birth_data.py   # データクラス
│   │   └── exceptions.py   # 例外定義
│   ├── layer1/             # 四柱推命（完成）
│   │   ├── engine.py       # 計算エンジン
│   │   ├── metaphor.py     # メタファー辞書120通り
│   │   └── taizan_db.json  # 泰山流データ
│   ├── layer2/             # 西洋占星術（予定）
│   ├── layer3/             # 易経（予定）
│   ├── layer4/             # 紫微斗数（予定）
│   └── integration/        # 統合レイヤー（予定）
├── tests/                  # テストコード
│   ├── unit/               # 単体テスト
│   └── integration/        # 統合テスト
├── docs/                   # ドキュメント
│   ├── PRD.md              # 要件定義書
│   ├── DEVELOPMENT_TDD.md  # TDD開発ガイド
│   ├── DEVELOPMENT_FULL.md # 完全開発ガイド
│   ├── CLAUDE_SKILLS.md    # Claude Skills活用法
│   └── STREAMLIT_PATTERNS.md # UI実装パターン集
├── app.py                  # Streamlit UI
├── Makefile                # 開発タスク
├── pytest.ini              # テスト設定
└── requirements.txt        # 依存パッケージ
```

---

## 🧪 テスト駆動開発（TDD）

このプロジェクトは**TDD（Test-Driven Development）**で開発されています。

### テストカバレッジ目標

- **単体テスト**: 80%以上 ✅
- **統合テスト**: 主要パス100% ⬜

### テスト実行方法

```bash
# 全テスト
make test

# 単体テストのみ
make test-unit

# 統合テストのみ
make test-integration

# カバレッジレポート生成
make coverage
# → htmlcov/index.html を開く
```

---

## 🛠 開発方針

### Red-Green-Refactor サイクル

1. **Red**: テストを先に書く（失敗する）
2. **Green**: 最小限の実装で通す
3. **Refactor**: コードを改善

詳細は [DEVELOPMENT.md](docs/DEVELOPMENT.md) を参照。

---

## 📊 実装状況

### Layer 1: 四柱推命（泰山流調候用神）✅

- [x] 年柱・月柱・日柱・時柱の計算
- [x] 用神判定（120通り）
- [x] 時刻不明対応（三柱モード）
- [x] 単体テスト（カバレッジ 80%+）
- [x] メタファー辞書120通り（日干×月支）
- [x] 五行の意味辞書
- [x] Streamlit UI統合

### Layer 2: 西洋占星術 ⬜

- [ ] 天体位置計算
- [ ] ハウス計算
- [ ] アスペクト判定
- [ ] 時刻不明対応

### Layer 3: 易経 ⬜

- [ ] 卦生成
- [ ] 解釈取得

### Layer 4: 紫微斗数 ⬜

- [ ] 命盤作成
- [ ] 主星配置

### 統合レイヤー ⬜

- [ ] 多層結果統合
- [ ] メタファー辞書
- [ ] 自然言語生成

---

## 🎯 哲学

> 運命とは命の運び。  
> 「決まっていること」ではなく、「命をどう運んでいくか」自ら選択し行動すること。

運びの足元を照らし、意思決定をサポートする。  
依存ではなく、自立のお手伝い。

---

## 📖 ドキュメント

### 基本ドキュメント
- [PRD（要件定義書）](docs/PRD.md) - プロジェクト全体の要件と設計
- [TDD開発ガイド](docs/DEVELOPMENT_TDD.md) - テスト駆動開発の手順
- [完全開発ガイド](docs/DEVELOPMENT_FULL.md) - アーキテクチャ詳細

### 活用ガイド
- [Claude Skills活用法](docs/CLAUDE_SKILLS.md) - 鑑定解釈の自動化
- [Streamlitパターン集](docs/STREAMLIT_PATTERNS.md) - UI実装10種類以上

### Claude Code設定
- [CLAUDE.md](.claude/CLAUDE.md) - プロジェクト概要と規約
- [鑑定解釈スキル](.claude/skills/koyomi/SKILL.md) - 用神解釈の自動化

---

## 🤝 コントリビューション

1. Issueを作成
2. ブランチを切る
3. **テストを先に書く**（TDD）
4. 実装してテストを通す
5. PRを作成

詳細は [DEVELOPMENT.md](docs/DEVELOPMENT.md) を参照。

---

## 📄 ライセンス

MIT License

---

## 🔗 リンク

- [PRD（要件定義書）](docs/PRD.md)
- [開発ガイド](docs/DEVELOPMENT.md)
- [テストカバレッジレポート](htmlcov/index.html)（ローカルのみ）

---

## 💡 開発コマンド

```bash
make help  # コマンド一覧表示
```

| コマンド | 説明 |
|----------|------|
| `make install` | 依存パッケージインストール |
| `make test` | 全テスト実行 |
| `make test-unit` | 単体テストのみ |
| `make test-integration` | 統合テストのみ |
| `make coverage` | カバレッジレポート生成 |
| `make format` | コードフォーマット |
| `make lint` | コード品質チェック |
| `make clean` | キャッシュ削除 |
| `make run` | Streamlit起動 |
