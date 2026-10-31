"""LCU 챔피언 선택 세션(/lol-champ-select/v1/session)을 브리핑용 상태로 정규화."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Stage(str, Enum):
    PLANNING = "planning"  # 선픽 의도 표시 단계
    BANNING = "banning"
    PRE_MY_PICK = "pre_my_pick"  # 내 픽 전: 픽/밴 추천
    POST_MY_PICK = "post_my_pick"  # 내 픽 확정 후, 아직 미확정 픽 있음
    FINAL = "final"  # 10명 확정: 최종 게임 플랜


@dataclass(frozen=True)
class Slot:
    cell_id: int
    position: str  # "jungle", "top", ... (적팀은 보통 빈 문자열)
    champion_id: int  # 확정 또는 선택 중인 챔피언 (0 = 없음)
    intent_id: int  # 선픽 의도 (아군만)
    locked: bool
    spells: tuple[int, int] = (0, 0)
    team_id: int = 0  # 100 블루 / 200 레드 (LCU team 1/2)

    @property
    def shown_champion(self) -> int:
        return self.champion_id or self.intent_id


@dataclass(frozen=True)
class ChampSelectState:
    stage: Stage
    timer_phase: str
    local_cell_id: int
    allies: tuple[Slot, ...]
    enemies: tuple[Slot, ...]
    ally_bans: tuple[int, ...]
    enemy_bans: tuple[int, ...]
    in_progress_cells: tuple[int, ...] = field(default=())

    @property
    def me(self) -> Slot | None:
        return next((s for s in self.allies if s.cell_id == self.local_cell_id), None)

    @property
    def my_position(self) -> str:
        return self.me.position if self.me else ""

    @property
    def is_jungle(self) -> bool:
        return self.my_position == "jungle"

    @property
    def my_team_id(self) -> int:
        return self.me.team_id if self.me and self.me.team_id else 100

    @property
    def enemy_team_id(self) -> int:
        return 300 - self.my_team_id

    def picked_or_banned(self) -> set[int]:
        out = set(self.ally_bans) | set(self.enemy_bans)
        out |= {s.champion_id for s in self.allies + self.enemies if s.champion_id}
        return out

    @property
    def ally_jungle(self) -> Slot | None:
        return next((s for s in self.allies if s.position == "jungle"), None)

    def signature(self) -> tuple:
        """브리핑을 다시 만들어야 하는 변화만 담은 키 (타이머 변화 등은 무시)."""
        return (
            self.stage,
            tuple((s.cell_id, s.champion_id, s.locked) for s in self.allies),
            tuple((s.cell_id, s.champion_id, s.locked) for s in self.enemies),
            self.ally_bans,
            self.enemy_bans,
        )


def _flatten_actions(session: dict) -> list[dict]:
    return [a for group in session.get("actions") or [] for a in group]


def parse_session(session: dict) -> ChampSelectState:
    local = session.get("localPlayerCellId", -1)
    actions = _flatten_actions(session)
    my_team_cells = {m["cellId"] for m in session.get("myTeam") or []}

    locked_picks: dict[int, int] = {}
    in_progress: list[int] = []
    ally_bans: list[int] = []
    enemy_bans: list[int] = []
    for a in actions:
        if a.get("isInProgress"):
            in_progress.append(a["actorCellId"])
        if not a.get("completed"):
            continue
        if a.get("type") == "pick":
            locked_picks[a["actorCellId"]] = a.get("championId", 0)
        elif a.get("type") == "ban" and a.get("championId"):
            (ally_bans if a["actorCellId"] in my_team_cells else enemy_bans).append(a["championId"])

    # 일부 모드는 actions 대신 bans 필드만 채운다
    bans = session.get("bans") or {}
    ally_bans = ally_bans or [b for b in bans.get("myTeamBans", []) if b]
    enemy_bans = enemy_bans or [b for b in bans.get("theirTeamBans", []) if b]

    def slot(m: dict) -> Slot:
        cell = m["cellId"]
        return Slot(
            cell_id=cell,
            position=(m.get("assignedPosition") or "").lower(),
            champion_id=m.get("championId", 0) or locked_picks.get(cell, 0),
            intent_id=m.get("championPickIntent", 0) or 0,
            locked=cell in locked_picks,
            spells=(m.get("spell1Id", 0) or 0, m.get("spell2Id", 0) or 0),
            team_id={1: 100, 2: 200}.get(m.get("team", 0), 0),
        )

    allies = tuple(slot(m) for m in session.get("myTeam") or [])
    enemies = tuple(slot(m) for m in session.get("theirTeam") or [])
    timer_phase = (session.get("timer") or {}).get("phase", "")

    return ChampSelectState(
        stage=_stage(timer_phase, local, allies, enemies, actions),
        timer_phase=timer_phase,
        local_cell_id=local,
        allies=allies,
        enemies=enemies,
        ally_bans=tuple(ally_bans),
        enemy_bans=tuple(enemy_bans),
        in_progress_cells=tuple(in_progress),
    )


def _stage(timer_phase, local, allies, enemies, actions) -> Stage:
    if timer_phase == "PLANNING":
        return Stage.PLANNING
    slots = allies + enemies
    if timer_phase == "FINALIZATION" or (slots and all(s.locked for s in slots)):
        return Stage.FINAL
    in_progress_types = {a.get("type") for a in actions if a.get("isInProgress")}
    if "ban" in in_progress_types and not any(s.locked for s in slots):
        return Stage.BANNING
    me = next((s for s in allies if s.cell_id == local), None)
    if me and me.locked:
        return Stage.POST_MY_PICK
    return Stage.PRE_MY_PICK
