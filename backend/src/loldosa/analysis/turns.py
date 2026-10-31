"""턴(귀환·오브젝트 타이밍) 분석의 공통 규칙.

귀환 감지: 1분 간격 위치로는 귀환 대부분을 놓친다(분수대에 찍힌 프레임 약 2.5%).
대신 상점에서만 가능한 ITEM_PURCHASED 이벤트(ms 단위)를 쓴다.
- 같은 선수의 구매가 GAP_MS 이내로 이어지면 한 번의 상점 방문으로 묶는다.
- 시작 아이템 구매(START_MS 이전)는 제외한다.
- 방문 직전 DEATH_WINDOW_MS 안에 죽었으면 '데스 귀환', 아니면 '귀환'.
한계: 아무것도 사지 않은 귀환은 잡히지 않는다. 방문 시각은 '상점 도착' 시각이다(귀환 시작보다 약 8초 늦음).
"""

from __future__ import annotations

from dataclasses import dataclass

GAP_MS = 20_000
START_MS = 90_000
DEATH_WINDOW_MS = 120_000

# 오브젝트 직전 '턴' 판정 창 (오브젝트 첫 처치 시각 T 기준)
SETUP_FROM_MS = 150_000  # T-150초부터
SETUP_TO_MS = 40_000  # T-40초까지 상점에 다녀왔으면 '준비 귀환'
SYNC_MS = 30_000  # 정글과 라이너의 상점 방문이 30초 이내면 '같이 귀환'
LATE_FROM_MS = 30_000  # T-30초 이후 상점에 있었으면 '오브젝트 직전 귀환'

# 오브젝트별로 같이 귀환해야 하는 라인
OBJECTIVE_LANES = {"DRAGON": ("BOTTOM", "UTILITY", "MIDDLE"), "HORDE": ("TOP", "MIDDLE"),
                   "RIFTHERALD": ("TOP", "MIDDLE")}


@dataclass
class ShopVisit:
    participant_id: int
    ts_ms: int  # 첫 구매 시각
    death_back: bool


def shop_visits(purchases: list[tuple[int, int]], deaths: list[tuple[int, int]]) -> list[ShopVisit]:
    """purchases/deaths: (participant_id, ts_ms) 목록."""
    by_pid: dict[int, list[int]] = {}
    for pid, ts in purchases:
        if ts >= START_MS:
            by_pid.setdefault(pid, []).append(ts)
    death_by: dict[int, list[int]] = {}
    for pid, ts in deaths:
        death_by.setdefault(pid, []).append(ts)
    out = []
    for pid, times in by_pid.items():
        times.sort()
        start = prev = None
        for ts in times + [None]:
            if ts is not None and prev is not None and ts - prev <= GAP_MS:
                prev = ts
                continue
            if start is not None:
                died = any(start - DEATH_WINDOW_MS <= d < start for d in death_by.get(pid, []))
                out.append(ShopVisit(pid, start, died))
            start = prev = ts
    return sorted(out, key=lambda v: v.ts_ms)


TURN_KO = {"sync": "정글+라이너 같이 미리 귀환", "jg_only": "정글만 미리 귀환", "none": "미리 귀환 안 함",
           "late": "직전 30초 안에 정글이 상점"}
OBJ_KO = {"DRAGON": "첫 드래곤", "HORDE": "공허 유충"}


def team_turn(visits: list[ShopVisit], t_ms: int, jungler: int, lane_pids: list[int]) -> str:
    """오브젝트 첫 처치 시각 t_ms 기준 한 팀의 턴 상태 (build.py 의 SQL 과 같은 규칙)."""
    jg = [v for v in visits if v.participant_id == jungler]
    if any(t_ms - LATE_FROM_MS <= v.ts_ms <= t_ms for v in jg):
        return "late"
    setup = [v for v in jg if not v.death_back and t_ms - SETUP_FROM_MS <= v.ts_ms <= t_ms - SETUP_TO_MS]
    if not setup:
        return "none"
    lanes = [v for v in visits if v.participant_id in lane_pids and not v.death_back]
    if any(abs(l.ts_ms - j.ts_ms) <= SYNC_MS for j in setup for l in lanes):
        return "sync"
    return "jg_only"
