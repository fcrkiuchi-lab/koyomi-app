"""
E2Eテスト: ユーザー入力から最終出力まで
"""
import pytest
from datetime import datetime
from src.koyomi.layer1.engine import MeishikiEngine
from src.koyomi.core.birth_data import BirthData


@pytest.fixture
def sample_birth_data():
    """テスト用サンプルデータ"""
    return [
        {
            "name": "太郎（時刻あり）",
            "datetime": datetime(1990, 6, 15, 10, 30),
            "has_time": True,
            "location": (35.6762, 139.6503),
        },
        {
            "name": "花子（時刻なし）",
            "datetime": datetime(1985, 12, 25, 12, 0),
            "has_time": False,
            "location": (35.6762, 139.6503),
        },
        {
            "name": "次郎（真冬）",
            "datetime": datetime(2000, 1, 15, 8, 0),
            "has_time": True,
            "location": (35.6762, 139.6503),
        },
    ]


class TestE2EFlow:
    """エンドツーエンドのフローテスト"""
    
    @pytest.mark.integration
    def test_full_flow_with_time(self, sample_birth_data):
        """時刻あり: 入力→計算→出力の全フローが通るか"""
        engine = MeishikiEngine()
        data = sample_birth_data[0]
        
        # 計算実行
        result = engine.analyze(data["datetime"], has_time=data["has_time"])
        
        # 結果が返される
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        
        # 必須要素が含まれる
        assert "年柱:" in result
        assert "月柱:" in result
        assert "日柱:" in result
        assert "時柱:" in result
        assert "用神:" in result
    
    @pytest.mark.integration
    def test_full_flow_without_time(self, sample_birth_data):
        """時刻なし: 三柱モードで全フローが通るか"""
        engine = MeishikiEngine()
        data = sample_birth_data[1]
        
        # 計算実行
        result = engine.analyze(data["datetime"], has_time=data["has_time"])
        
        # 結果が返される
        assert result is not None
        assert "（時刻不明）" in result
    
    @pytest.mark.integration
    def test_multiple_calculations(self, sample_birth_data):
        """複数人の鑑定が連続で実行できるか"""
        engine = MeishikiEngine()
        
        results = []
        for data in sample_birth_data:
            result = engine.analyze(data["datetime"], has_time=data["has_time"])
            results.append(result)
        
        # 全て成功
        assert len(results) == len(sample_birth_data)
        
        # 結果が異なる（同じ人がいないことを確認）
        assert len(set(results)) == len(results)
    
    @pytest.mark.integration
    def test_layer1_data_consistency(self):
        """Layer1のデータ整合性テスト"""
        engine = MeishikiEngine()
        
        # 同じ日付で複数回計算しても結果が同じか
        dt = datetime(1990, 6, 15, 10, 30)
        
        result1 = engine.judge_yojin(dt)
        result2 = engine.judge_yojin(dt)
        
        assert result1["day_kan"] == result2["day_kan"]
        assert result1["season"] == result2["season"]
        assert result1["yojin"] == result2["yojin"]


class TestBirthDataClass:
    """BirthDataクラスのテスト"""
    
    @pytest.mark.integration
    def test_birth_data_layer_availability(self):
        """can_calculate()が正しく動作するか"""
        # 時刻あり、位置あり
        data_full = BirthData(
            datetime=datetime(1990, 6, 15, 10, 30),
            has_time=True,
            location=(35.6762, 139.6503)
        )
        
        assert data_full.can_calculate("shichusuimei") is True
        assert data_full.can_calculate("astrology") is True
        assert data_full.can_calculate("ekikyo") is True
        assert data_full.can_calculate("shibi") is True
        
        # 時刻なし、位置あり
        data_no_time = BirthData(
            datetime=datetime(1990, 6, 15, 12, 0),
            has_time=False,
            location=(35.6762, 139.6503)
        )
        
        assert data_no_time.can_calculate("shichusuimei") is True
        assert data_no_time.can_calculate("astrology") is True
        assert data_no_time.can_calculate("shibi") is False  # 時刻必須
        
        # 時刻あり、位置なし
        data_no_location = BirthData(
            datetime=datetime(1990, 6, 15, 10, 30),
            has_time=True,
            location=None
        )
        
        assert data_no_location.can_calculate("shichusuimei") is True
        assert data_no_location.can_calculate("astrology") is False  # 位置必須
    
    @pytest.mark.integration
    def test_birth_data_get_mode(self):
        """get_mode()が正しく動作するか"""
        data_full = BirthData(
            datetime=datetime(1990, 6, 15, 10, 30),
            has_time=True,
            location=(35.6762, 139.6503)
        )
        
        assert data_full.get_mode("shichusuimei") == "full"
        assert data_full.get_mode("astrology") == "full"
        
        data_no_time = BirthData(
            datetime=datetime(1990, 6, 15, 12, 0),
            has_time=False,
            location=(35.6762, 139.6503)
        )
        
        assert data_no_time.get_mode("shichusuimei") == "sanchu"
        assert data_no_time.get_mode("astrology") == "no_houses"
        assert data_no_time.get_mode("shibi") == "unavailable"
