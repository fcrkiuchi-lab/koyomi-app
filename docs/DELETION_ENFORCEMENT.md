# 削除処理の強制連結ガイド

## 🎯 目的

サブスク解約時、**必ず**データ削除が実行されることを保証する。

---

## 🔥 重要な設計思想

```
解約 = 即時削除
```

この一貫性を**構造的に担保**する。

---

## ✅ 実装パターン

### パターン1: 解約API内で強制実行（推奨）

```python
# routes/subscription.py

from src.koyomi.storage.json_store import delete_user_data
from src.koyomi.storage.subscription import cancel_subscription

@app.post("/api/subscription/cancel")
def cancel_subscription_endpoint(user_id: str):
    """サブスク解約API
    
    削除が失敗した場合、解約自体も失敗させる
    """
    try:
        # 1. データ削除（先に実行）
        deleted = delete_user_data(user_id)
        
        if not deleted:
            # データがない場合はOK（既に削除済み）
            pass
        
        # 2. サブスク状態を無効化
        cancel_subscription(user_id)
        
        return {"status": "success", "message": "Subscription cancelled"}
    
    except Exception as e:
        # 削除失敗時は解約も失敗させる
        raise HTTPException(
            status_code=500,
            detail=f"Cancellation failed: {str(e)}"
        )
```

**ポイント**:
- データ削除が失敗 → 解約も失敗
- トランザクション的な一貫性

---

### パターン2: Webhook経由（決済サービス連携）

```python
# routes/webhook.py

@app.post("/webhook/stripe")
def stripe_webhook(event: dict):
    """Stripe Webhook
    
    customer.subscription.deleted イベント
    """
    if event["type"] == "customer.subscription.deleted":
        user_id = event["data"]["object"]["metadata"]["user_id"]
        
        # データ削除（失敗時は例外）
        delete_user_data(user_id)
        
        # ログ記録
        log_deletion(user_id, event["id"])
    
    return {"status": "received"}
```

---

### パターン3: 定期ジョブ（補完）

```python
# jobs/cleanup_expired.py

def cleanup_expired_subscriptions():
    """期限切れサブスクのデータ削除
    
    Note:
        メインの削除処理ではない
        漏れた場合の補完処理
    """
    expired_users = get_expired_subscriptions()
    
    for user_id in expired_users:
        try:
            delete_user_data(user_id)
            log_deletion(user_id, reason="expired")
        except Exception as e:
            log_error(f"Failed to delete {user_id}: {e}")
            alert_admin(user_id, e)  # アラート
```

---

## 🛡️ 強制力の担保

### 1. コードレビューチェックリスト

```markdown
## 解約処理のPRチェック

- [ ] delete_user_data() が呼ばれているか
- [ ] 削除失敗時の例外処理があるか
- [ ] ログ記録があるか
- [ ] テストケースがあるか
```

---

### 2. テストコード

```python
# tests/test_subscription.py

def test_cancel_deletes_data():
    """解約時にデータが削除されること"""
    user_id = "test_user"
    
    # データ作成
    create_test_session(user_id)
    assert user_data_exists(user_id)
    
    # 解約実行
    cancel_subscription(user_id)
    
    # データが削除されていることを確認
    assert not user_data_exists(user_id)


def test_cancel_fails_if_deletion_fails():
    """削除失敗時、解約も失敗すること"""
    user_id = "test_user"
    
    # 削除失敗をモック
    with mock.patch('delete_user_data', side_effect=Exception("Disk full")):
        # 解約が失敗することを確認
        with pytest.raises(Exception):
            cancel_subscription(user_id)
```

---

### 3. 監視・アラート

```python
# monitoring/deletion_monitor.py

def monitor_deletions():
    """削除処理の監視
    
    以下をチェック:
    - 削除失敗がないか
    - 期限切れなのにデータが残っていないか
    """
    # 期限切れユーザーのデータをチェック
    expired_users = get_expired_subscriptions()
    
    for user_id in expired_users:
        if user_data_exists(user_id):
            # アラート
            alert_admin(
                f"Data remains for expired user: {user_id}",
                severity="HIGH"
            )
```

---

## 📝 実装チェックリスト

### 🟢 公開前必須

- [x] delete_user_data() 実装済み
- [x] 例外を握り潰さない設計
- [ ] 解約API に delete_user_data() 連結
- [ ] テストコード作成
- [ ] 削除ログ実装（最低限ファイル出力）

### 🟡 ローンチ直前

- [ ] 削除失敗時のアラート
- [ ] 定期ジョブ（漏れ補完）
- [ ] 監視ダッシュボード

---

## 🔥 絶対に守ること

```
解約処理 = データ削除 + サブスク無効化

この2つは**必ず同時**に実行される構造にする
```

**分離してはいけない理由**:
- 手動実行は忘れる
- 別タイミングは漏れる
- 構造的強制のみが確実

---

## 📊 現在の実装状況

| 項目 | 状態 |
|------|------|
| delete_user_data() | ✅ 実装済 |
| 例外処理 | ✅ 握り潰さない |
| サニタイズ | ✅ 全関数適用 |
| 解約API連結 | ⚠️ 未実装（要実装） |
| テストコード | ⚠️ 未実装（要実装） |
| 削除ログ | ⚠️ 未実装（要実装） |

---

**最終更新**: 2026年2月12日  
**ステータス**: 設計完了、解約API連結が必要
