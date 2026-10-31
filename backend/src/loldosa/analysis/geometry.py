"""소환사의 협곡 좌표 분류.

좌표계: 0~14870, 블루(100) 기지가 왼쪽 아래, 레드(200) 기지가 오른쪽 위.
맵은 중심 기준 점대칭이라 레드 쪽 캠프는 (MAP - x, MAP - y) 로 구한다.
캠프 좌표는 커뮤니티에 공개된 근사값이며, 분 단위 위치(타임라인 프레임)를
가장 가까운 캠프/구역으로 분류하는 데만 쓴다.
"""

from __future__ import annotations

import math

MAP = 14870

# 블루팀 정글 캠프 (근사 좌표)
BLUE_CAMPS = {
    "blue": (3800, 7900),
    "gromp": (2150, 8400),
    "wolves": (3800, 6500),
    "raptors": (6950, 5400),
    "red": (7800, 4050),
    "krugs": (8400, 2700),
}
CAMP_KO = {"blue": "블루", "gromp": "두꺼비", "wolves": "늑대", "raptors": "칼날부리", "red": "레드", "krugs": "돌거북"}


def team_camps(team_id: int) -> dict[str, tuple[int, int]]:
    if team_id == 100:
        return BLUE_CAMPS
    return {k: (MAP - x, MAP - y) for k, (x, y) in BLUE_CAMPS.items()}


def nearest_camp(team_id: int, x: float, y: float) -> str:
    return min(team_camps(team_id).items(), key=lambda kv: math.dist(kv[1], (x, y)))[0]


def region(x: float | None, y: float | None) -> str:
    """base | top | bot | mid | river | blue_jungle | red_jungle | unknown"""
    if x is None or y is None:
        return "unknown"
    if x + y < 5200 or x + y > 24500:
        return "base"
    if x < 1800 or y > 13070 or (x < 4200 and y > 10700):
        return "top"
    if y < 1800 or x > 13070 or (x > 10700 and y < 4200):
        return "bot"
    if abs(x - y) < 1300:
        return "mid"
    if abs(x + y - MAP) < 1400:
        return "river"
    return "blue_jungle" if x + y < MAP else "red_jungle"


def relative_region(team_id: int, x: float | None, y: float | None) -> str:
    """정글러 기준: own_jungle / enemy_jungle / top / mid / bot / river / base"""
    r = region(x, y)
    if r.endswith("_jungle"):
        mine = "blue_jungle" if team_id == 100 else "red_jungle"
        return "own_jungle" if r == mine else "enemy_jungle"
    return r


def map_side(x: float, y: float) -> str:
    """맵을 대각선(블루 기지→레드 기지)으로 나눠 위쪽(탑 사이드)/아래쪽(봇 사이드)."""
    return "top" if y > x else "bot"


# DuckDB 매크로 (분석 SQL 에서 같은 규칙을 쓰기 위해)
SQL_MACROS = f"""
CREATE OR REPLACE MACRO region(x, y) AS CASE
    WHEN x IS NULL OR y IS NULL THEN 'unknown'
    WHEN x + y < 5200 OR x + y > 24500 THEN 'base'
    WHEN x < 1800 OR y > 13070 OR (x < 4200 AND y > 10700) THEN 'top'
    WHEN y < 1800 OR x > 13070 OR (x > 10700 AND y < 4200) THEN 'bot'
    WHEN abs(x - y) < 1300 THEN 'mid'
    WHEN abs(x + y - {MAP}) < 1400 THEN 'river'
    WHEN x + y < {MAP} THEN 'blue_jungle'
    ELSE 'red_jungle' END;
CREATE OR REPLACE MACRO rel_region(team, x, y) AS CASE
    WHEN region(x, y) = 'blue_jungle' THEN CASE WHEN team = 100 THEN 'own_jungle' ELSE 'enemy_jungle' END
    WHEN region(x, y) = 'red_jungle' THEN CASE WHEN team = 200 THEN 'own_jungle' ELSE 'enemy_jungle' END
    ELSE region(x, y) END;
CREATE OR REPLACE MACRO map_side(x, y) AS CASE WHEN y > x THEN 'top' ELSE 'bot' END;
"""


def camps_sql_values() -> str:
    rows = []
    for team in (100, 200):
        for name, (x, y) in team_camps(team).items():
            rows.append(f"({team}, '{name}', {x}, {y})")
    return ", ".join(rows)
