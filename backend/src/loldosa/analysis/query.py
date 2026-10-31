"""stats.duckdb 조회 + 표본 보정.

원칙
- 승률은 베이지안 보정(사전확률 쪽으로 k 게임만큼 당김)한 값과 원래 값, 표본 수를 함께 돌려준다.
- 범위(scope)는 최신 패치 표본이 충분하면 최신 패치, 아니면 수집 기간 전체('ALL').
- 버킷은 apex(마스터+)를 기준 정답으로, platinum 을 비교용으로 쓴다.
"""

from __future__ import annotations

import math
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
        self._con: duckdb.DuckDBPyConnection | None = None

    @property
    def available(self) -> bool:
        return self.path.exists()

    @contextmanager
    def session(self):
        self._con = duckdb.connect(str(self.path), read_only=True)
        try:
            yield self
        finally:
            self._con.close()
            self._con = None

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

    def gank_target(self, s: Scope, lane: str, rel: str, champ: int) -> dict | None:
        w, p = self._w(s)
        return self.one(f"""SELECT ganks, kill_rate FROM gank_targets
                            WHERE {w} AND lane=? AND rel=? AND champion_id=?""", p + [lane, rel, champ])

    def gank_lane_base(self, s: Scope) -> dict[str, dict]:
        w, p = self._w(s)
        return {r["lane"]: r for r in self.rows(f"SELECT * FROM gank_lane_base WHERE {w}", p)}

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
