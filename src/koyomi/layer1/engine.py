"""
四柱推命計算エンジン - 泰山流調候用神
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

# 十干・十二支
JIKKAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
JUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 節入り日時データ（2020-2030年の主要な節気）
SEKKI_DATA = {
    2024: {
        "立春": datetime(2024, 2, 4, 16, 27),
        "啓蟄": datetime(2024, 3, 5, 10, 23),
        "清明": datetime(2024, 4, 4, 15, 2),
        "立夏": datetime(2024, 5, 5, 8, 10),
        "芒種": datetime(2024, 6, 5, 12, 10),
        "小暑": datetime(2024, 7, 6, 22, 20),
        "立秋": datetime(2024, 8, 7, 14, 9),
        "白露": datetime(2024, 9, 7, 11, 11),
        "寒露": datetime(2024, 10, 8, 2, 59),
        "立冬": datetime(2024, 11, 7, 6, 20),
        "大雪": datetime(2024, 12, 6, 23, 17),
        "小寒": datetime(2025, 1, 5, 10, 4),
    },
    2025: {
        "立春": datetime(2025, 2, 3, 22, 10),
        "啓蟄": datetime(2025, 3, 5, 16, 7),
        "清明": datetime(2025, 4, 4, 20, 48),
        "立夏": datetime(2025, 5, 5, 13, 56),
        "芒種": datetime(2025, 6, 5, 17, 56),
        "小暑": datetime(2025, 7, 7, 4, 5),
        "立秋": datetime(2025, 8, 7, 19, 51),
        "白露": datetime(2025, 9, 7, 16, 52),
        "寒露": datetime(2025, 10, 8, 8, 41),
        "立冬": datetime(2025, 11, 7, 12, 4),
        "大雪": datetime(2025, 12, 7, 5, 5),
        "小寒": datetime(2026, 1, 5, 15, 51),
    },
    2026: {
        "立春": datetime(2026, 2, 4, 3, 58),
        "啓蟄": datetime(2026, 3, 5, 21, 54),
        "清明": datetime(2026, 4, 5, 2, 38),
        "立夏": datetime(2026, 5, 5, 19, 45),
        "芒種": datetime(2026, 6, 5, 23, 48),
        "小暑": datetime(2026, 7, 7, 9, 59),
        "立秋": datetime(2026, 8, 8, 1, 45),
        "白露": datetime(2026, 9, 7, 22, 47),
        "寒露": datetime(2026, 10, 8, 14, 35),
        "立冬": datetime(2026, 11, 7, 17, 55),
        "大雪": datetime(2026, 12, 7, 10, 52),
        "小寒": datetime(2027, 1, 5, 21, 38),
    },
}


class MeishikiEngine:
    """四柱推命計算エンジン"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent / "taizan_db.json"
        with open(db_path, "r", encoding="utf-8") as f:
            self.taizan_db = json.load(f)

    def calc_pillars(
        self, birth_dt: datetime, has_time: bool = True
    ) -> dict:
        """四柱（年柱・月柱・日柱・時柱）を計算"""
        
        # 年柱計算（立春基準）
        year_pillar = self._calc_year_pillar(birth_dt)
        
        # 月柱計算（節入り基準）
        month_pillar = self._calc_month_pillar(birth_dt)
        
        # 日柱計算（万年暦ベース）
        day_pillar = self._calc_day_pillar(birth_dt)
        
        # 時柱計算（時刻がある場合のみ）
        hour_pillar = self._calc_hour_pillar(birth_dt) if has_time else None
        
        return {
            "year": year_pillar,
            "month": month_pillar,
            "day": day_pillar,
            "hour": hour_pillar,
            "has_time": has_time,
        }

    def _calc_year_pillar(self, dt: datetime) -> dict:
        """年柱計算（立春基準）"""
        year = dt.year
        
        # 立春前なら前年扱い
        if year in SEKKI_DATA and dt < SEKKI_DATA[year]["立春"]:
            year -= 1
        
        # 1984年(甲子)を基準に計算
        offset = (year - 1984) % 60
        kan = JIKKAN[offset % 10]
        shi = JUNISHI[offset % 12]
        
        return {"kan": kan, "shi": shi, "year": year}

    def _calc_month_pillar(self, dt: datetime) -> dict:
        """月柱計算（節入り基準）"""
        year = dt.year
        month = dt.month
        
        # 節入り判定
        if year not in SEKKI_DATA:
            # データがない場合は概算
            sekki_month = month
        else:
            sekki_dates = SEKKI_DATA[year]
            sekki_month = 1
            
            # どの節気を過ぎたか判定
            for sekki_name, sekki_dt in sorted(sekki_dates.items(), key=lambda x: x[1]):
                if dt >= sekki_dt:
                    if "立春" in sekki_name: sekki_month = 1
                    elif "啓蟄" in sekki_name: sekki_month = 2
                    elif "清明" in sekki_name: sekki_month = 3
                    elif "立夏" in sekki_name: sekki_month = 4
                    elif "芒種" in sekki_name: sekki_month = 5
                    elif "小暑" in sekki_name: sekki_month = 6
                    elif "立秋" in sekki_name: sekki_month = 7
                    elif "白露" in sekki_name: sekki_month = 8
                    elif "寒露" in sekki_name: sekki_month = 9
                    elif "立冬" in sekki_name: sekki_month = 10
                    elif "大雪" in sekki_name: sekki_month = 11
                    elif "小寒" in sekki_name: sekki_month = 12
        
        # 年干から月柱を算出
        year_kan_idx = JIKKAN.index(self._calc_year_pillar(dt)["kan"])
        month_kan_idx = (year_kan_idx * 2 + sekki_month + 1) % 10
        month_shi_idx = (sekki_month + 1) % 12
        
        return {
            "kan": JIKKAN[month_kan_idx],
            "shi": JUNISHI[month_shi_idx],
            "month": sekki_month,
        }

    def _calc_day_pillar(self, dt: datetime) -> dict:
        """日柱計算（簡易版）"""
        # 1900年1月1日(庚辰)を基準日として計算
        base_date = datetime(1900, 1, 1)
        days_diff = (dt - base_date).days
        
        # 庚辰を0として計算
        base_kan = JIKKAN.index("庚")
        base_shi = JUNISHI.index("辰")
        
        kan_idx = (base_kan + days_diff) % 10
        shi_idx = (base_shi + days_diff) % 12
        
        return {"kan": JIKKAN[kan_idx], "shi": JUNISHI[shi_idx]}

    def _calc_hour_pillar(self, dt: datetime) -> dict:
        """時柱計算"""
        hour = dt.hour
        
        # 23-1時:子、1-3時:丑... 
        shi_idx = ((hour + 1) // 2) % 12
        
        # 日干から時干を算出
        day_kan = self._calc_day_pillar(dt)["kan"]
        day_kan_idx = JIKKAN.index(day_kan)
        
        hour_kan_idx = (day_kan_idx * 2 + shi_idx) % 10
        
        return {"kan": JIKKAN[hour_kan_idx], "shi": JUNISHI[shi_idx]}

    def judge_yojin(self, birth_dt: datetime) -> dict:
        """泰山流調候用神判定"""
        pillars = self.calc_pillars(birth_dt, has_time=True)
        
        # 季節判定
        month = pillars["month"]["month"]
        if month in [1, 2, 3]:
            season = "春"
        elif month in [4, 5, 6]:
            season = "夏"
        elif month in [7, 8, 9]:
            season = "秋"
        elif month in [10, 11, 12]:
            season = "冬"
        else:
            season = "土用"
        
        # 寒暖湿燥判定（簡易版：月で判定）
        if season in ["春", "秋", "冬"]:
            condition = "寒" if month in [1, 2, 10, 11, 12] else "暖"
        else:  # 夏
            condition = "湿" if month in [5, 6] else "燥"
        
        # 日干取得
        day_kan = pillars["day"]["kan"]
        
        # 用神取得
        key = f"{season}_{day_kan}"
        yojin_data = self.taizan_db.get(key, {})
        yojin_str = yojin_data.get(condition, "")
        yojin_list = yojin_str.split("_") if yojin_str else []
        
        return {
            "pillars": pillars,
            "season": season,
            "condition": condition,
            "yojin": yojin_list,
            "day_kan": day_kan,
        }

    def analyze(self, birth_dt: datetime, has_time: bool = True) -> str:
        """鑑定結果をテキスト生成"""
        result = self.judge_yojin(birth_dt)
        pillars = result["pillars"]
        
        # 命式表示
        meishiki_text = f"""
【命式】
年柱: {pillars['year']['kan']}{pillars['year']['shi']}
月柱: {pillars['month']['kan']}{pillars['month']['shi']}
日柱: {pillars['day']['kan']}{pillars['day']['shi']}
"""
        if has_time and pillars['hour']:
            meishiki_text += f"時柱: {pillars['hour']['kan']}{pillars['hour']['shi']}\n"
        else:
            meishiki_text += "時柱: （時刻不明）\n"
        
        # 用神判定
        yojin_text = f"""
【泰山流調候用神】
季節: {result['season']}
寒暖湿燥: {result['condition']}
用神: {' > '.join(result['yojin'])}
"""
        
        return meishiki_text + yojin_text


if __name__ == "__main__":
    # テスト実行
    engine = MeishikiEngine()
    test_dt = datetime(1990, 6, 15, 10, 30)
    result = engine.analyze(test_dt)
    print(result)
