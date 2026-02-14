# 📱 iPhone からのデプロイ手順

## 🎯 ゴール

iPhoneだけで暦KOYOMIを本番公開する

---

## ✅ 必要なもの

1. **GitHubアカウント**
   - https://github.com で無料作成

2. **Streamlit Cloudアカウント**
   - https://share.streamlit.io
   - GitHubアカウントでログイン（連携）

3. **iOSアプリ（どれか1つ）**
   - Working Copy（推奨・無料）
   - GitHub Mobile（公式アプリ）
   - Textastic（有料）

---

## 📋 手順

### Step 1: GitHubリポジトリ作成

#### 方法A: GitHub Mobile（公式アプリ）

1. App Storeから「GitHub」をインストール
2. ログイン
3. 右上「+」→「New repository」
4. 名前: `koyomi-app`
5. Public / Private 選択
6. Create repository

#### 方法B: Safari/Chrome

1. https://github.com/new にアクセス
2. 同様に作成

---

### Step 2: コードをアップロード

#### 方法A: Working Copy（推奨）

1. **Working Copyインストール**
   - App Store → "Working Copy"

2. **リポジトリクローン**
   - Working Copy起動
   - 右上「+」→「Clone repository」
   - GitHubアカウント連携
   - `koyomi-app` を選択

3. **ファイルをコピー**
   - iCloud Drive / Filesアプリから
   - zipを展開
   - 全ファイルをWorking Copyにコピー

4. **コミット & Push**
   - Working Copy内で変更を確認
   - "Stage All" → "Commit"
   - メッセージ: "Initial commit"
   - "Push"

#### 方法B: GitHub Mobile

1. リポジトリを開く
2. "Add file" → "Upload files"
3. Filesアプリからファイル選択
4. アップロード（制限: 100ファイル以下）

---

### Step 3: Streamlit Cloudでデプロイ

1. **Streamlit Cloudにアクセス**
   - Safari/Chrome で https://share.streamlit.io
   - "Sign in with GitHub"

2. **新しいアプリを作成**
   - "New app" をクリック
   - Repository: `YOUR_USERNAME/koyomi-app`
   - Branch: `main`
   - Main file path: `app.py`
   - Advanced settings（任意）:
     - Python version: 3.11

3. **Deploy！**
   - "Deploy" ボタンをクリック
   - 3-5分待つ（ビルド中）

4. **完成** 🎉
   - URL: `https://YOUR_APP.streamlit.app`
   - iPhoneでアクセス可能

---

## 🔧 トラブルシューティング

### エラー: "Module not found"

**原因**: requirements.txtが読み込まれていない

**解決**:
1. Streamlit Cloudのダッシュボード
2. アプリ設定
3. "Reboot app"

---

### エラー: "Build failed"

**原因**: Python バージョン不一致

**解決**:
1. `.python-version` ファイルを確認
2. 3.11 になっているか
3. なければ作成:
   ```
   python==3.11
   ```

---

### Working Copy でpushできない

**原因**: 認証エラー

**解決**:
1. Working Copy → Settings
2. "Service Integration"
3. GitHub再認証
4. Personal Access Token発行

---

## 📱 Working Copy クイックガイド

### 基本操作

1. **クローン**
   - 右上「+」→「Clone repository」

2. **ファイル編集**
   - ファイルをタップ
   - 編集モード

3. **コミット**
   - 変更を確認
   - 「Stage」→「Commit」

4. **Push**
   - 「Push」タブ
   - 「Push to origin」

### Tips

- **Swipe** でステージング
- **長押し** でファイル操作
- **External Files** で外部アプリ連携

---

## 🎯 次のステップ

### デプロイ後

1. **動作確認**
   - iPhoneでURLにアクセス
   - 生年月日入力テスト
   - 鑑定結果確認

2. **カスタムドメイン設定**（任意）
   - Streamlit Cloud設定
   - 独自ドメイン連携

3. **アクセス制限**（必要に応じて）
   - Private app設定
   - パスワード保護

---

## 💡 おすすめ設定

### Streamlit Cloud Settings

```toml
# .streamlit/config.toml に記載済み

[theme]
primaryColor = "#9370DB"  # 紫（運命カラー）
backgroundColor = "#0a0a1a"  # ダークブルー
```

### GitHub Settings

- **Branch protection**: main ブランチ保護
- **Dependabot**: 自動セキュリティアップデート
- **Actions**: 自動テスト（将来）

---

## 🚨 注意事項

### セキュリティ

- ❌ APIキーをコミットしない
- ❌ `.env` ファイルを公開しない
- ✅ `.gitignore` で除外確認

### データ

- ユーザーデータは `data/users/` に保存
- `.gitignore` で Git管理外
- Streamlit Cloud では永続化されない（要注意）

---

## 📞 サポート

### 困ったら

1. **Streamlit Community**
   - https://discuss.streamlit.io

2. **GitHub Issues**
   - リポジトリの Issues タブ

3. **Claude.ai**
   - エラーメッセージをコピペして質問

---

## ✅ チェックリスト

デプロイ前に確認:

- [ ] requirements.txt が固定バージョン
- [ ] .streamlit/config.toml 存在
- [ ] .gitignore に data/users/ 除外
- [ ] app.py が正常に動作
- [ ] taizan_db.json がコミットされている

---

**これで iPhone だけで本番デプロイ完了！** 🎉
