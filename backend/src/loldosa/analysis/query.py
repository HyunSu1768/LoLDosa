"""stats.duckdb 조회 + 표본 보정.

원칙
- 승률은 베이지안 보정(사전확률 쪽으로 k 게임만큼 당김)한 값과 원래 값, 표본 수를 함께 돌려준다.
- 범위(scope)는 최신 패치 표본이 충분하면 최신 패치, 아니면 수집 기간 전체('ALL').
- 버킷은 apex(마스터+)를 기준 정답으로, platinum 을 비교용으로 쓴다.
"""

from __future__ import annotations

import math
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import duckdb

BUCKET_KO = {"apex": "KR 마스터+", "platinum": "KR 플래티넘", "all": "KR 마스터+·플래티넘"}


def shrink(wins: float, games: float, prior: float = 0.5, k: float = 20) -> float:
    return (wins + prior * k) / (games + k)


def logit(p: float) -> float:
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def confidence(games: int) -> str:
    return "높음" if games >= 100 else "보통" if games >= 30 else "낮음"


@dataclass(frozen=True)
class Scope:
    scope: str  # patch or ALL
    bucket: str

    @property
    def label(self) -> str:
        period = f"패치 {self.scope}" if self.scope != "ALL" else "최근 수집 기간 전체"
        return f"{BUCKET_KO.get(self.bucket, self.bucket)} 솔로랭크 · {period}"


class StatsDB:
    """짧게 열고 닫는다 (분석 빌드가 파일을 교체할 수 있도록)."""

    MIN_PATCH_GAMES = 300  # 최신 패치 경기가 이보다 적으면 전체 기간 사용

    def __init__(self, path: Path) -> None:
        self.path = path
        # 서버에서는 브리핑(작업 스레드)과 상태 조회(이벤트 루프)가 동시에 쓰므로 연결은 스레드별로 둔다
        self._local = threading.local()

    @property
    def available(self) -> bool:
        return self.path.exists()

    @property
    def _con(self) -> duckdb.DuckDBPyConnection | None:
        return getattr(self._local, "con", None)

    @contextmanager
    def session(self):
        if self._con is not None:  # 같은 스레드 안의 중첩 호출은 기존 연결 재사용
            yield self
            return
        self._local.con = duckdb.connect(str(self.path), read_only=True)
        try:
            yield self
        finally:
            self._local.con.close()
            self._local.con = None

    def rows(self, sql: str, params: list | None = None) -> list[dict]:
        assert self._con is not None, "use `with stats.session():`"
        cur = self._con.execute(sql, params or [])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def one(self, sql: str, params: list | None = None) -> dict | None:
        r = self.rows(sql, params)
        return r[0] if r else None

    # ---- meta / scope ------------------------------------------------------

    def meta(self) -> dict[str, str]:
        return {r["key"]: r["value"] for r in self.rows("SELECT * FROM meta")}

    def matches(self, scope: Scope) -> int:
        r = self.one("SELECT matches FROM match_totals WHERE scope=? AND bucket=?", [scope.scope, scope.bucket])
        return r["matches"] if r else 0

    def pick_scope(self, bucket: str = "apex") -> Scope:
        latest = self.meta().get("latest_patch", "")
        for b in (bucket, "all"):
            if latest and self.matches(Scope(latest, b)) >= self.MIN_PATCH_GAMES:
                return Scope(latest, b)
            if self.matches(Scope("ALL", b)) >= 50:
                return Scope("ALL", b)
        return Scope("ALL", "all")

    def _w(self, s: Scope) -> tuple[str, list]:
        return "scope=? AND bucket=?", [s.scope, s.bucket]

    # ---- 정글 챔피언 -----------------------------------------------------------

    def champ_baseline(self, s: Scope) -> dict:
        """정글 챔피언 평균 (판 수 가중): 상대 정글 습관이 평균과 다른지 비교할 때."""
        w, p = self._w(s)
        return self.one(f"""SELECT sum(enemy_jungle_cs * games) / sum(games) AS invade,
                                   sum(first_dragon_rate * games) / sum(games) AS fd,
                                   sum(first_grub_rate * games) / sum(games) AS fg
                            FROM champ_stats WHERE {w}""", p) or {}

    def champ(self, s: Scope, champ: int) -> dict | None:
        w, p = self._w(s)
        r = self.one(f"SELECT * FROM champ_stats WHERE {w} AND champion_id=?", p + [champ])
        if not r:
            return None
        total = self.matches(s)
        ban = self.one(f"SELECT banned FROM ban_stats WHERE {w} AND champion_id=?", p + [champ])
        r["win_rate"] = r["wins"] / r["games"]
        r["win_rate_adj"] = shrink(r["wins"], r["games"])
        r["pick_rate"] = r["games"] / total if total else 0
        r["ban_rate"] = (ban["banned"] / total) if ban and total else 0
        return r

    def jungle_pool(self, s: Scope, min_games: int = 5) -> list[dict]:
        w, p = self._w(s)
        total = self.matches(s) or 1
        rows = self.rows(f"""
            SELECT c.champion_id, c.games, c.wins, coalesce(b.banned, 0) AS banned
            FROM champ_stats c LEFT JOIN ban_stats b USING (scope, bucket, champion_id)
            WHERE c.{w.replace(' AND ', ' AND c.')} AND c.games >= ?
        """, p + [min_games])
        for r in rows:
            r["win_rate_adj"] = shrink(r["wins"], r["games"])
            r["pick_rate"] = r["games"] / total
            r["ban_rate"] = r["banned"] / total
        return rows

    def matchup(self, s: Scope, champ: int, enemy: int) -> dict | None:
        w, p = self._w(s)
        r = self.one(f"SELECT * FROM matchups WHERE {w} AND champion_id=? AND enemy_id=?", p + [champ, enemy])
        if r:
            r["win_rate"] = r["wins"] / r["games"]
        return r

    def matchup_curve(self, s: Scope, champ: int, enemy: int) -> list[dict]:
        w, p = self._w(s)
        return self.rows(f"""SELECT minute, games, gold_diff, level_diff FROM matchup_curves
                             WHERE {w} AND champion_id=? AND enemy_id=? ORDER BY minute""", p + [champ, enemy])

    def curve(self, s: Scope, champ: int) -> list[dict]:
        w, p = self._w(s)
        return self.rows(f"""SELECT minute, games, gold_diff, xp_diff, level_diff, level FROM curves
                             WHERE {w} AND champion_id=? ORDER BY minute""", p + [champ])

    def start_camps(self, s: Scope, champ: int, team_id: int | None = None) -> list[dict]:
        w, p = self._w(s)
        q = f"SELECT start_camp, team_id, games, wins FROM start_camps WHERE {w} AND champion_id=?"
        params = p + [champ]
        if team_id:
            q += " AND team_id=?"
            params.append(team_id)
        return self.rows(q + " ORDER BY games DESC", params)

    def routes(self, s: Scope, champ: int) -> list[dict]:
        w, p = self._w(s)
        return self.rows(f"""SELECT route3, sum(games) AS games, sum(wins) AS wins FROM routes
                             WHERE {w} AND champion_id=? GROUP BY route3 ORDER BY games DESC""", p + [champ])

    def clears(self, s: Scope, champ: int) -> list[dict]:
        """3:00 까지 완료한 캠프 수 기준 클리어 방식 + 그때 위치."""
        w, p = self._w(s)
        return self.rows(f"""SELECT clear3, route3, sum(games) AS games, sum(wins) AS wins
                             FROM routes WHERE {w} AND champion_id=? GROUP BY ALL""", p + [champ])

    def first_ganks(self, s: Scope, champ: int) -> list[dict]:
        w, p = self._w(s)
        return self.rows(f"""SELECT lane, games, wins, avg_s, median_s, kill_rate FROM first_ganks
                             WHERE {w} AND champion_id=? ORDER BY games DESC""", p + [champ])

    def presence(self, s: Scope, champ: int) -> dict[int, dict[str, float]]:
        w, p = self._w(s)
        out: dict[int, dict[str, float]] = {}
        for r in self.rows(f"SELECT minute, region, n FROM presence WHERE {w} AND champion_id=?", p + [champ]):
            out.setdefault(r["minute"], {})[r["region"]] = r["n"]
        for m, d in out.items():
            tot = sum(d.values())
            out[m] = {k: v / tot for k, v in d.items()}
        return out

    def duration(self, s: Scope, champ: int, table: str = "duration") -> dict[str, dict]:
        w, p = self._w(s)
        return {r["dur_bucket"]: r for r in self.rows(
            f"SELECT dur_bucket, games, wins FROM {table} WHERE {w} AND champion_id=?", p + [champ])}

    def synergy(self, s: Scope, champ: int, ally: int) -> dict | None:
        w, p = self._w(s)
        return self.one(f"""SELECT sum(games) AS games, sum(wins) AS wins FROM synergy
                            WHERE {w} AND champion_id=? AND ally_id=? HAVING sum(games) > 0""", p + [champ, ally])

    def versus(self, s: Scope, champ: int, enemy: int) -> dict | None:
        w, p = self._w(s)
        return self.one(f"""SELECT sum(games) AS games, sum(wins) AS wins FROM versus
                            WHERE {w} AND champion_id=? AND enemy_id=? HAVING sum(games) > 0""", p + [champ, enemy])

    def comp_fit(self, s: Scope, champ: int, ally_damage: str) -> dict | None:
        w, p = self._w(s)
        return self.one(f"""SELECT sum(games) AS games, sum(wins) AS wins FROM comp_fit
                            WHERE {w} AND champion_id=? AND ally_damage=? HAVING sum(games) > 0""",
                        p + [champ, ally_damage])

    def worst_matchups(self, s: Scope, champ: int, min_games: int = 3, limit: int = 5) -> list[dict]:
        w, p = self._w(s)
        rows = self.rows(f"SELECT enemy_id, games, wins, gd10 FROM matchups WHERE {w} AND champion_id=? AND games>=?",
                         p + [champ, min_games])
        for r in rows:
            r["win_rate_adj"] = shrink(r["wins"], r["games"], k=15)
        return sorted(rows, key=lambda r: r["win_rate_adj"])[:limit]

    # ---- 라인 / 갱 / 오브젝트 --------------------------------------------------

    def positions(self, s: Scope, champ: int) -> dict[str, int]:
        w, p = self._w(s)
        return {r["position"]: r["games"] for r in self.rows(
            f"SELECT position, games FROM champ_positions WHERE {w} AND champion_id=?", p + [champ])}

    def lane_matchup(self, s: Scope, position: str, champ: int, enemy: int) -> dict | None:
        w, p = self._w(s)
        return self.one(f"""SELECT games, wins, gd10 FROM lane_matchups
                            WHERE {w} AND position=? AND champion_id=? AND enemy_id=?""", p + [position, champ, enemy])

    def lane_strength(self, s: Scope, position: str, champ: int) -> dict | None:
        """그 라인에서 이 챔피언의 10분 골드 차 평균 (모든 상대 합산). 특정 맞대결은 판 수가 적어서 이걸로 라인 우세를 본다."""
        w, p = self._w(s)
        return self.one(f"""SELECT sum(games) AS games, sum(gd10 * games) / sum(games) AS gd10 FROM lane_matchups
                            WHERE {w} AND position=? AND champion_id=? AND gd10 IS NOT NULL HAVING sum(games) > 0""",
                        p + [position, champ])

    def gank_exposure(self, s: Scope, position: str, champ: int) -> dict | None:
        w, p = self._w(s)
        return self.one(f"""SELECT games, died_to_jg, kill_with_jg FROM gank_exposure
                            WHERE {w} AND position=? AND champion_id=?""", p + [position, champ])

    def gank_exposure_base(self, s: Scope) -> dict[str, dict]:
        w, p = self._w(s)
        return {r["position"]: r for r in self.rows(f"""
            SELECT position, sum(games) AS games, sum(died_to_jg * games) / sum(games) AS died_to_jg,
                   sum(kill_with_jg * games) / sum(games) AS kill_with_jg
            FROM gank_exposure WHERE {w} GROUP BY position""", p)}

    def sides(self, s: Scope, champ: int, team_id: int) -> dict[str, dict[str, int]]:
        """정글러(챔피언·진영)의 3:00 / 4:00 맵 사이드 분포."""
        w, p = self._w(s)
        out: dict[str, dict[str, int]] = {"side3": {}, "side4": {}}
        for col in out:
            for r in self.rows(f"""SELECT {col} AS side, sum(games) AS games FROM routes
                                   WHERE {w} AND champion_id=? AND team_id=? AND {col} IS NOT NULL GROUP BY 1""",
                               p + [champ, team_id]):
                out[col][r["side"]] = r["games"]
        return out

    def side_transition(self, s: Scope) -> list[dict]:
        w, p = self._w(s)
        return self.rows(f"""SELECT start_side, side3, side4, sum(games) AS games FROM side_transition
                             WHERE {w} GROUP BY ALL""", p)

    def profiles(self, champ_ids: list[int]) -> dict[int, dict]:
        if not champ_ids:
            return {}
        q = ",".join("?" * len(champ_ids))
        return {r["champion_id"]: r for r in self.rows(
            f"SELECT * FROM champ_profile WHERE champion_id IN ({q})", list(champ_ids))}

    def objectives(self, s: Scope) -> dict | None:
        w, p = self._w(s)
        return self.one(f"SELECT * FROM objectives WHERE {w}", p)

    def objective_impact(self, s: Scope) -> dict[str, dict]:
        w, p = self._w(s)
        return {r["objective"]: r for r in self.rows(f"SELECT * FROM objective_impact WHERE {w}", p)}

    # ---- 프로 대회 (Leaguepedia) ----------------------------------------------

    def _has(self, table: str) -> bool:
        return bool(self.rows("SELECT 1 FROM information_schema.tables WHERE table_name = ?", [table]))

    def pro_info(self) -> dict | None:
        return self.one("SELECT * FROM pro_info") if self._has("pro_info") else None

    def pro_champ(self, champ: int) -> dict | None:
        if not self._has("pro_champ"):
            return None
        return self.one("SELECT * FROM pro_champ WHERE champion_id=?", [champ])

    def pro_matchup(self, champ: int, enemy: int) -> dict | None:
        if not self._has("pro_matchups"):
            return None
        return self.one("SELECT * FROM pro_matchups WHERE champion_id=? AND enemy_id=?", [champ, enemy])

    # ---- 정글 교전 (레벨 구간) -------------------------------------------------

    def duels(self, s: Scope, champ: int, enemy: int | None = None) -> dict[str, dict]:
        w, p = self._w(s)
        q = f"SELECT level_band, sum(fights) AS fights, sum(won) AS won FROM jungle_duels WHERE {w} AND champion_id=?"
        params = p + [champ]
        if enemy:
            q += " AND enemy_id=?"
            params.append(enemy)
        if not self._has("jungle_duels"):
            return {}
        return {r["level_band"]: r for r in self.rows(q + " GROUP BY level_band", params)}

    def has_rows(self, table: str, s: Scope) -> bool:
        w, p = self._w(s)
        return bool(self.rows(f"SELECT 1 FROM {table} WHERE {w} LIMIT 1", p))

    # ---- 턴 (귀환·오브젝트) --------------------------------------------------

    def turn_objective(self, s: Scope, objective: str) -> dict[str, dict]:
        if not self._has("turn_objective"):
            return {}
        w, p = self._w(s)
        return {r["turn"]: r for r in self.rows(
            f"SELECT turn, games, took FROM turn_objective WHERE {w} AND objective=?", p + [objective])}

    def first_recall(self, s: Scope, champ: int) -> dict | None:
        if not self._has("first_recall"):
            return None
        w, p = self._w(s)
        return self.one(f"SELECT * FROM first_recall WHERE {w} AND champion_id=?", p + [champ])

    # ---- 판단 훈련 ------------------------------------------------------------

    def decision_pool(self, minute: int, bucket: str = "apex") -> tuple[list[dict], str]:
        """같은 시간대(±1분) 정글러 상황들. 마스터+ 표본이 적으면 전체 티어."""
        if not self._has("decision_states"):
            return [], ""
        for b, label in ((bucket, BUCKET_KO.get(bucket, bucket)), (None, "전체 수집 티어")):
            q = "SELECT * FROM decision_states WHERE minute BETWEEN ? AND ?"
            params: list = [minute - 1, minute + 1]
            if b:
                q += " AND bucket = ?"
                params.append(b)
            rows = self.rows(q, params)
            if len(rows) >= 150 or b is None:
                return rows, label
        return [], ""

    def bucket_avgs(self, bucket: str) -> dict:
        """티어 전체 정글러 평균 (챔피언 가중). '다음 티어' 비교용."""
        r = self.one("""SELECT sum(games) AS games,
                sum(jungle_cs10 * games) / sum(games) AS cs10, sum(deaths10 * games) / sum(games) AS deaths10,
                sum(vision_pm * games) / sum(games) AS vision_pm, sum(camps3 * games) / sum(games) AS camps3
            FROM champ_stats WHERE scope = 'ALL' AND bucket = ?""", [bucket])
        if not r or not r["games"]:
            return {}
        if self._has("first_recall"):
            fr = self.one("""SELECT sum(median_s * games) / sum(games) AS s FROM first_recall
                             WHERE scope = 'ALL' AND bucket = ?""", [bucket])
            if fr and fr["s"]:
                r["first_recall_s"] = fr["s"]
        return r

    def path_medoid(self, champ: int, team_id: int, style: str = "any") -> dict | None:
        if not self._has("path_medoids"):
            return None
        r = self.one("SELECT * FROM path_medoids WHERE champion_id=? AND team_id=? AND style=?", [champ, team_id, style])
        if r:
            import json as _json
            r["points"] = _json.loads(r["points"])
        return r
