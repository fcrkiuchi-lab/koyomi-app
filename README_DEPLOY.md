# 暦 KOYOMI 🏔️

**AI人間関係コンサルタント** - 四柱推命ベースの対話式意思決定サポートシステム

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

---

## 🎯 コンセプト

運命とは「命の運び」。  
決まっているものではなく、**自ら選択し行動するもの**。

暦KOYOMIは、あなたの意思決定を照らす灯りです。  
依存ではなく、**自立のお手伝い**。

---

## ✨ 機能

### Layer 1: 四柱推命（泰山流調候用神）
- 120通りの命式データベース
- 生年月日から自動計算
- メタファー解釈

### 対話式コンサルタント
- チャット形式で相談
- 人間関係の悩みに対応
- PDF鑑定書出力

### データ保護
- 単発利用: 完全非保存（プライバシー重視）
- サブスク: 暗号化保存
- 解約即削除（GDPR準拠）

---

## 🚀 クイックスタート

### 1. ローカル実行

```bash
# リポジトリクローン
git clone https://github.com/YOUR_USERNAME/koyomi-production-ready.git
cd koyomi-production-ready

# 依存関係インストール
pip install -r requirements.txt

# アプリ起動
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセス

---

### 2. Streamlit Cloud デプロイ（推奨）

#### 手順

1. **GitHubにpush**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Streamlit Cloudでデプロイ**
   - https://share.streamlit.io にアクセス
   - "New app" をクリック
   - リポジトリ選択: `YOUR_USERNAME/koyomi-production-ready`
   - Main file: `app.py`
   - Deploy！

3. **完成** 🎉
   - 自動で公開URL生成
   - `https://YOUR_APP.streamlit.app`

---

## 📁 プロジェクト構造

```
koyomi-production-ready/
├── app.py                      # メインアプリ
├── requirements.txt            # 依存関係（固定バージョン）
├── .streamlit/
│   └── config.toml            # Streamlit設定
├── src/koyomi/
│   ├── core/                  # コア機能
│   ├── layer1/                # 四柱推命エンジン
│   ├── chat/                  # 対話システム
│   └── storage/               # データ保存
├── tests/                     # テストコード
├── docs/                      # ドキュメント
└── taizan_db.json            # 泰山流データベース
```

---

## 🧪 テスト

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ確認
pytest tests/ --cov=src --cov-report=html

# 保存制御テスト（重要）
pytest tests/test_storage_control.py -v
```

---

## 🔒 セキュリティ

- ✅ パストラバーサル防止（user_idサニタイズ）
- ✅ サーバー側サブスク検証
- ✅ アトミック保存（データ破損防止）
- ✅ 削除監査ログ
- ✅ GDPR準拠（解約即削除）

詳細: [SECURITY_VERIFICATION_REPORT.md](SECURITY_VERIFICATION_REPORT.md)

---

## 📊 技術スタック

| カテゴリ | 技術 |
|---------|------|
| UI | Streamlit 1.40.2 |
| 言語 | Python 3.11+ |
| 計算 | 自前実装（APIコスト0円） |
| データ | JSON（MVP）→ SQLite/Supabase（Phase 2） |
| デプロイ | Streamlit Cloud |
| テスト | pytest |

---

## 🛣️ ロードマップ

### ✅ Phase 1（完了）
- [x] 四柱推命エンジン実装
- [x] セキュリティ対策
- [x] テストコード
- [x] Streamlit UI

### 🔄 Phase 2（進行中）
- [ ] Layer 2: 西洋占星術
- [ ] Layer 3: 易経
- [ ] 削除スクリプト自動化
- [ ] SQLite移行

### 📋 Phase 3（計画中）
- [ ] ユーザー認証
- [ ] サブスク決済連携
- [ ] Layer 4: 紫微斗数

---

## 📝 ライセンス

MIT License

---

## 👤 作成者

暦 KOYOMI プロジェクト

---

## 🙏 謝辞

- 泰山流調候用神の知恵
- Streamlitコミュニティ
- すべてのユーザー

---

## 📞 サポート

- 🐛 バグ報告: [Issues](https://github.com/YOUR_USERNAME/koyomi-production-ready/issues)
- 💡 機能提案: [Discussions](https://github.com/YOUR_USERNAME/koyomi-production-ready/discussions)
- 📧 お問い合わせ: your-email@example.com

---

**運命は決まっていない。命をどう運ぶか、あなたが選ぶ。**
