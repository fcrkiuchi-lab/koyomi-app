#!/usr/bin/env python3
"""
テスト用解約スクリプト

⚠️ 警告: これは開発/テスト専用です
本番では使用しないでください

使用方法:
    python scripts/cancel_subscription_test.py <user_id>
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.koyomi.storage.json_store import delete_user_data
from src.koyomi.storage.subscription import cancel_subscription


def cancel_subscription_safe(user_id: str) -> bool:
    """サブスク解約（テスト用）
    
    Args:
        user_id: ユーザーID
    
    Returns:
        True: 成功、False: 失敗
    
    Note:
        本番では使用しない
        API経由での解約を実装すること
    """
    print(f"⚠️  テスト用解約処理を開始: {user_id}")
    print(f"⚠️  本番では使用しないでください")
    
    try:
        # 1. データ削除
        print(f"1. データ削除中...")
        deleted = delete_user_data(user_id, reason="test_cancellation")
        
        if deleted:
            print(f"   ✅ データ削除成功")
        else:
            print(f"   ℹ️  データなし（既に削除済み）")
        
        # 2. サブスク状態無効化
        print(f"2. サブスク状態無効化中...")
        cancel_subscription(user_id)
        print(f"   ✅ サブスク無効化成功")
        
        print(f"✅ 解約処理完了: {user_id}")
        return True
    
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法: python scripts/cancel_subscription_test.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    
    # 確認
    print(f"\n{'='*50}")
    print(f"解約対象: {user_id}")
    print(f"{'='*50}")
    
    confirm = input("実行しますか？ (yes/no): ")
    
    if confirm.lower() != "yes":
        print("キャンセルしました")
        sys.exit(0)
    
    # 実行
    success = cancel_subscription_safe(user_id)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
