"""
削除ログ専用ロガー

Zone: Logic
責務: データ削除の証跡記録

設計思想:
- 削除は確実に記録
- 既存ログと競合しない
- 監査証跡として使用可能
"""
import logging
from pathlib import Path
from datetime import datetime, timezone


# ログディレクトリ
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 専用ロガー作成（既存loggerと競合しない）
deletion_logger = logging.getLogger("koyomi.deletion")
deletion_logger.setLevel(logging.INFO)

# ファイルハンドラ
log_file = LOG_DIR / "deletions.log"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# フォーマット
formatter = logging.Formatter(
    '%(asctime)s,%(levelname)s,%(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)
file_handler.setFormatter(formatter)

# ハンドラ追加（重複防止）
if not deletion_logger.handlers:
    deletion_logger.addHandler(file_handler)

# 親ロガーに伝播しない（既存logと競合防止）
deletion_logger.propagate = False


def log_deletion_start(user_id: str, reason: str = "manual"):
    """削除開始をログ記録
    
    Args:
        user_id: ユーザーID
        reason: 削除理由（manual, expired, cancellation）
    """
    deletion_logger.info(f"START,{user_id},{reason}")


def log_deletion_success(user_id: str):
    """削除成功をログ記録
    
    Args:
        user_id: ユーザーID
    """
    deletion_logger.info(f"SUCCESS,{user_id}")


def log_deletion_failure(user_id: str, error: str):
    """削除失敗をログ記録
    
    Args:
        user_id: ユーザーID
        error: エラー内容
    """
    deletion_logger.error(f"FAILURE,{user_id},{error}")


def get_deletion_log_path() -> Path:
    """削除ログファイルのパスを取得
    
    Returns:
        ログファイルパス
    """
    return log_file
