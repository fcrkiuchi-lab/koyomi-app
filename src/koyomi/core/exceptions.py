"""
カスタム例外クラス
"""


class KoyomiError(Exception):
    """基底例外クラス"""
    pass


class InvalidBirthDataError(KoyomiError):
    """不正な生年月日データ"""
    pass


class CalculationError(KoyomiError):
    """計算エラー"""
    pass


class LayerNotAvailableError(KoyomiError):
    """レイヤーが利用不可（条件不足）"""
    pass


class DataNotFoundError(KoyomiError):
    """必要なデータが見つからない"""
    pass
