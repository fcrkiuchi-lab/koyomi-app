"""
pytest共通設定とフィクスチャ
"""
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """pytestの設定"""
    config.addinivalue_line(
        "markers", "unit: 単体テスト"
    )
    config.addinivalue_line(
        "markers", "integration: 統合テスト"
    )
    config.addinivalue_line(
        "markers", "slow: 実行に時間がかかるテスト"
    )
    config.addinivalue_line(
        "markers", "layer1: Layer1（四柱推命）のテスト"
    )
    config.addinivalue_line(
        "markers", "layer2: Layer2（西洋占星術）のテスト"
    )
