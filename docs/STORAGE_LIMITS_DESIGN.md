# セッション肥大化対策（設計）

## 背景

将来的に以下のリスクがある：
- adviceが長文化
- chat履歴の保存
- PDF大量生成
- 1ユーザーあたりの容量増大

## 対策（設計段階）

### 1. ユーザーあたりセッション数上限

```python
MAX_SESSIONS_PER_USER = 100  # 例

def save_session(session):
    sessions = list_sessions(session.user_id)
    
    if len(sessions) >= MAX_SESSIONS_PER_USER:
        # 最古のセッションを削除
        oldest = min(sessions, key=lambda s: s.created_at)
        delete_session(session.user_id, oldest.session_id)
```

### 2. ユーザーあたり容量上限

```python
MAX_STORAGE_PER_USER = 50 * 1024 * 1024  # 50MB

def get_user_storage_size(user_id):
    user_dir = BASE_DIR / user_id
    return sum(f.stat().st_size for f in user_dir.rglob('*') if f.is_file())

def save_session(session):
    if get_user_storage_size(session.user_id) > MAX_STORAGE_PER_USER:
        raise StorageLimitExceeded("Storage limit reached")
```

### 3. セッションデータの圧縮

```python
import gzip

def save_session_compressed(session):
    data = json.dumps(session.to_dict())
    compressed = gzip.compress(data.encode('utf-8'))
    
    with open(file_path, 'wb') as f:
        f.write(compressed)
```

### 4. 古いセッションの自動削除

```python
from datetime import timedelta

def cleanup_old_sessions(max_age_days=365):
    """1年以上古いセッションを削除"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    
    for user_dir in BASE_DIR.iterdir():
        for session_file in (user_dir / "sessions").glob("*.json"):
            session = load_session_from_file(session_file)
            if datetime.fromisoformat(session.created_at) < cutoff:
                session_file.unlink()
```

## 実装タイミング

- **現在**: 実装不要（MVP段階）
- **実装時期**: ユーザー数 > 100 または 容量問題が発生時
- **優先度**: 中（設計は完了、実装は後回し）

## 思想との整合性

```
✅ サブスク期間のみ保持
✅ 期限切れは自動削除
✅ 容量制限で肥大化防止
✅ 古いデータは価値が低い（削除OK）
```

→ 設計思想と矛盾しない

## 注意事項

- 容量制限は「サブスク契約の一部」として明記
- ユーザーには事前通知（利用規約）
- 削除前に警告メール（将来実装）

---

**最終更新**: 2026年2月12日  
**ステータス**: 設計完了、実装は保留
