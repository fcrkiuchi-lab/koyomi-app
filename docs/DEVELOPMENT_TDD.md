# 開発ガイド - 暦 KOYOMI

## 開発フロー（TDD準拠）

### 1. 新機能追加の手順

#### Step 1: テストを先に書く（RED）
```bash
# 例: Layer2（西洋占星術）を追加する場合
vim tests/unit/test_layer2.py
```

テストコードの例：
```python
def test_calculate_sun_sign():
    """太陽星座が正しく計算されるか"""
    dt = datetime(1990, 6, 15, 10, 30)
    location = (35.6762, 139.6503)
    
    result = astrology_engine.calculate_sun_sign(dt, location)
    
    assert result == "Gemini"
```

#### Step 2: テストを実行（失敗することを確認）
```bash
make test-unit
# → FAILED (機能未実装のため)
```

#### Step 3: 最小限の実装（GREEN）
```bash
vim src/koyomi/layer2/engine.py
```

実装コードの例：
```python
def calculate_sun_sign(dt, location):
    """太陽星座を計算"""
    # 最小限の実装
    return "Gemini"  # ハードコード（仮）
```

#### Step 4: テスト再実行（成功を確認）
```bash
make test-unit
# → PASSED
```

#### Step 5: リファクタリング（REFACTOR）
```python
def calculate_sun_sign(dt, location):
    """太陽星座を計算"""
    # 実際のロジックに置き換え
    import ephem
    sun = ephem.Sun(dt)
    # ... 正しい計算ロジック
    return zodiac_sign
```

#### Step 6: テスト再実行（リファクタ後も成功を確認）
```bash
make test-unit
# → PASSED
```

---

### 2. コマンド一覧

```bash
# 環境セットアップ
make install

# テスト実行
make test              # 全テスト
make test-unit         # 単体テストのみ
make test-integration  # 統合テストのみ

# カバレッジ確認
make coverage
# → htmlcov/index.html をブラウザで開く

# コード品質
make format  # 自動フォーマット
make lint    # 品質チェック

# アプリ起動
make run
```

---

### 3. ディレクトリ構造ルール

```
src/koyomi/
├── core/              # 共通ロジック
│   ├── birth_data.py  # データクラス
│   └── exceptions.py  # 例外クラス
├── layer1/            # 四柱推命
│   ├── engine.py      # エンジン本体
│   └── taizan_db.json # データ
├── layer2/            # 西洋占星術（追加予定）
├── layer3/            # 易経（追加予定）
├── layer4/            # 紫微斗数（追加予定）
└── integration/       # 統合レイヤー（追加予定）
```

**ルール**:
- 各レイヤーは独立して動作すること
- 他レイヤーへの依存は `integration/` 経由のみ
- `core/` は全レイヤーから参照可能

---

### 4. テストコードの書き方

#### Good Example ✅
```python
@pytest.mark.unit
@pytest.mark.layer1
def test_specific_case():
    """具体的な1つの機能をテスト"""
    # Arrange（準備）
    dt = datetime(1990, 6, 15, 10, 30)
    
    # Act（実行）
    result = engine.calculate(dt)
    
    # Assert（検証）
    assert result["day"]["kan"] == "丁"
```

#### Bad Example ❌
```python
def test_everything():
    """複数の機能を1つのテストで検証"""
    # これはNG！ 失敗時にどこが問題か分からない
    result = engine.calculate(...)
    assert result["day"]["kan"] == "丁"
    assert result["month"]["shi"] == "午"
    assert result["yojin"][0] == "甲"
```

**原則**:
- 1テスト = 1機能
- テスト名は具体的に
- AAA パターン（Arrange-Act-Assert）を守る

---

### 5. コミットメッセージ規約

```
[type] 簡潔な説明

詳細な説明（任意）

type:
- feat: 新機能
- fix: バグ修正
- test: テスト追加
- refactor: リファクタリング
- docs: ドキュメント更新
```

例:
```
[feat] Layer2（西洋占星術）エンジン追加

- 太陽星座計算を実装
- アスペクト判定を実装
- テストカバレッジ 85%
```

---

### 6. トラブルシューティング

#### Q: テストが失敗する
```bash
# 詳細なエラーメッセージを表示
pytest -vv tests/unit/test_layer1.py::test_specific_case

# デバッガー起動
pytest --pdb tests/unit/test_layer1.py
```

#### Q: カバレッジが低い
```bash
# カバレッジレポートを確認
make coverage
open htmlcov/index.html

# どの行がテストされていないか確認
```

#### Q: importエラーが出る
```bash
# Pythonパスを確認
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# または conftest.py でパス追加されているか確認
```

---

### 7. 推奨開発環境

```bash
# VS Code拡張機能
- Python
- Pylance
- Python Test Explorer
- GitLens

# 設定（.vscode/settings.json）
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black"
}
```

---

### 8. PRレビューチェックリスト

- [ ] テストが全て通る（`make test`）
- [ ] カバレッジが80%以上（`make coverage`）
- [ ] コードフォーマット済み（`make format`）
- [ ] Lintエラーなし（`make lint`）
- [ ] PRD.mdと整合性がある
- [ ] コミットメッセージが規約通り
