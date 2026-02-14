#!/usr/bin/env python3
"""
期限切れセッション削除スクリプト

Zone: Logic
責務: 有効期限切れのセッションデータを削除

使用方法:
    python scripts/cleanup_expired.py

Note:
    MVP段階では手動実行
    将来的にcronで自動化（例: 毎日深夜3時）
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.koyomi.storage.json_store import cleanup_expired_sessions


def main():
    """メイン処理"""
    print("期限切れセッションの削除を開始します...")
    
    deleted_count = cleanup_expired_sessions()
    
    if deleted_count == 0:
        print("削除対象のセッションはありませんでした。")
    else:
        print(f"{deleted_count}件のセッションを削除しました。")
    
    print("完了しました。")


if __name__ == "__main__":
    main()
