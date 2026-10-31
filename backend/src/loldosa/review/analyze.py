"""경기 리뷰: 내 경기 타임라인을 고티어 기준과 비교해 '어떻게 했어야 했는지'를 만든다.

원칙은 브리핑과 같다.
- 내 기록(사실)과 고티어 기준(통계)은 각각 근거(Evidence)로 남긴다.
- 피드백(lesson)은 둘을 비교한 규칙의 결과이며 어떤 근거에서 나왔는지 표시한다.
- 타임라인으로 알 수 없는 것(킬 없는 갱 시도, 와드 위치)은 말하지 않는다.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field

from ..analysis.geometry import CAMP_KO, map_side, region, relative_region, team_camps
from ..analysis.query import StatsDB
from ..briefing.engine import BAND_KO, josa, mmss, pct, signed
from ..briefing.models import EvidenceLog
from ..ddragon import ChampionIndex
from ..analysis.turns import (LATE_FROM_MS, OBJECTIVE_LANES, SETUP_FROM_MS, SETUP_TO_MS, TURN_KO, shop_visits,
                              team_turn)
from ..store.matches import MatchStore

SRC_MINE = "내 경기 기록 (Riot Match-V5 타임라인)"
REGION_KO = {"own_jungle": "우리 정글", "enemy_jungle": "상대 정글", "river": "강가", "top": "탑 라인",
             "mid": "미드 라인", "bot": "봇 라인", "base": "본진", "unknown": "알 수 없음",
             "blue_jungle": "블루 진영 정글", "red_jungle": "레드 진영 정글"}
POS_KO = {"TOP": "탑", "JUNGLE": "정글", "MIDDLE": "미드", "BOTTOM": "원딜", "UTILITY": "서폿", "": "?"}
OBJ_KO = {"DRAGON": "드래곤", "HORDE": "공허 유충", "RIFTHERALD": "전령", "BARON_NASHOR": "바론",
          "ATAKHAN": "아타칸"}
FAR = 5000  # 오브젝트에서 이 거리보다 멀면 '합류 못 함'


@dataclass
class Metric:
    label: str
    mine: str
    bench: str
    verdict: str  # good | bad | neutral
    evidence: list[str] = field(default_factory=list)
    target: str = ""  # 다음 티어 평균
    me_avg: str = ""  # 내 최근 평균


@dataclass
class Moment:
    t: float  # 초
    kind: str  # start | clear | kill | death | assist | enemy_gank | objective
    text: str
    x: float | None = None
    y: float | None = None
    good: bool | None = None
    evidence: list[str] = field(default_factory=list)


@dataclass
class Lesson:
    title: str  # 한 줄 요약
    text: str  # 무엇이 있었고 어떻게 했어야 하는지
    severity: int  # 클수록 중요
    evidence: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)  # 학습 탭 개념 id
    t: float | None = None  # 경기 시각(초) — 리플레이 이동용


@dataclass
class Review:
    match_id: str
    summary: dict
    is_jungle: bool
    scope_label: str = ""
    lessons: list[Lesson] = field(default_factory=list)
    strengths: list[Lesson] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    moments: list[Moment] = field(default_factory=list)
    paths: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    facts: dict = field(default_factory=dict)  # 개념 체크용 구조화 값
    checks: list = field(default_factory=list)  # learn.skills 의 개념 체크 결과

    def to_dict(self) -> dict:
        return asdict(self)


def _dist(a, b) -> float:
    return math.dist(a, b) if a and b and None not in a and None not in b else float("inf")


class Reviewer:
    def __init__(self, store: MatchStore, stats: StatsDB, champs: ChampionIndex) -> None:
        self.store, self.stats, self.champs = store, stats, champs

    def name(self, cid: int) -> str:
        return self.champs.name(cid)

    # ------------------------------------------------------------------ load

    def _load(self, match_id: str) -> tuple[dict, list[dict], dict, list[dict]]:
        x = self.store._x
        m = x("SELECT match_id, patch, game_start, duration_s, winner_team FROM matches WHERE match_id=?", [match_id])
        if not m:
            raise KeyError(match_id)
        match = dict(zip(["match_id", "patch", "game_start", "duration_s", "winner_team"], m[0]))
        cols = ["participant_id", "puuid", "team_id", "position", "champion_id", "win", "kills", "deaths", "assists",
                "vision_score", "control_wards", "enemy_jungle_minions"]
        parts = [dict(zip(cols, r)) for r in x(f"SELECT {', '.join(cols)} FROM participants WHERE match_id=?",
                                                 [match_id])]
        frames: dict = {}
        for pid, minute, fx, fy, level, gold, jcs, cur in x(
                "SELECT participant_id, minute, x, y, level, total_gold, jungle_cs, current_gold FROM frames WHERE match_id=?",
                [match_id]):
            frames.setdefault(pid, {})[minute] = {"x": fx, "y": fy, "level": level, "gold": gold, "jcs": jcs,
                                                  "cur": cur}
        self.purchases = [(p, t) for p, t in x(
            "SELECT participant_id, ts_ms FROM events WHERE match_id=? AND type='ITEM_PURCHASED'", [match_id])]
        ecols = ["ts_ms", "type", "participant_id", "victim_id", "assists", "team_id", "monster_type",
                 "monster_sub_type", "x", "y"]
        events = [dict(zip(ecols, r)) for r in x(
            f"SELECT {', '.join(ecols)} FROM events WHERE match_id=? AND type IN ('CHAMPION_KILL', 'ELITE_MONSTER_KILL', "
            "'BUILDING_KILL', 'TURRET_PLATE_DESTROYED') "
            "ORDER BY ts_ms", [match_id])]
        return match, parts, frames, events

    # ------------------------------------------------------------------ main

    def review(self, match_id: str, puuid: str) -> Review:
        match, parts, frames, events = self._load(match_id)
        me = next((p for p in parts if p["puuid"] == puuid), None)
        if me is None:
            raise KeyError(f"{match_id}에 내 기록이 없어요")
        by_pid = {p["participant_id"]: p for p in parts}
        enemy_jg = next((p for p in parts if p["position"] == "JUNGLE" and p["team_id"] != me["team_id"]), None)
        team_kills = sum(p["kills"] for p in parts if p["team_id"] == me["team_id"])

        summary = {
            "match_id": match_id, "date": str(match["game_start"])[:16], "patch": match["patch"],
            "duration": mmss(match["duration_s"]), "win": bool(me["win"]),
            "champion_id": me["champion_id"], "champion": self.name(me["champion_id"]),
            "key": (self.champs.get(me["champion_id"]).key if self.champs.get(me["champion_id"]) else ""),
            "position": POS_KO.get(me["position"], me["position"]),
            "kda": f"{me['kills']}/{me['deaths']}/{me['assists']}",
            "side": "블루" if me["team_id"] == 100 else "레드",
            "enemy_jungler": self.name(enemy_jg["champion_id"]) if enemy_jg else "",
            "enemy_jungler_key": (self.champs.get(enemy_jg["champion_id"]).key
                                  if enemy_jg and self.champs.get(enemy_jg["champion_id"]) else ""),
        }
        rv = Review(match_id, summary, is_jungle=me["position"] == "JUNGLE")
        self.ev = EvidenceLog()
        self.me, self.enemy_jg, self.frames, self.by_pid = me, enemy_jg, frames, by_pid

        rv.paths = {
            "me": [[m, f["x"], f["y"]] for m, f in sorted(frames.get(me["participant_id"], {}).items()) if 1 <= m <= 10],
            "enemy_jungler": ([[m, f["x"], f["y"]] for m, f in sorted(frames.get(enemy_jg["participant_id"], {}).items())
                               if 1 <= m <= 10] if enemy_jg else []),
            "team": me["team_id"],
        }
        self.visits = shop_visits(self.purchases, [(e["victim_id"], e["ts_ms"]) for e in events
                                                   if e["type"] == "CHAMPION_KILL"])
        rv.moments = self.moments(events)

        if not rv.is_jungle:
            rv.notes.append(f"이 경기는 {josa(summary['position'], '으로')} 플레이했어요. 정글 비교는 정글로 한 판에서만 보여드려요.")
        elif self.stats.available:
            with self.stats.session():
                s = self.stats.pick_scope("apex")
                rv.scope_label = s.label
                self.scope = s
                self.jungle_review(rv, events, team_kills)
        else:
            rv.notes.append("고티어 통계가 없어요. `loldosa update` 후 다시 보세요.")
        rv.evidence = self.ev.items
        rv.lessons.sort(key=lambda l: -l.severity)
        for l in rv.lessons + rv.strengths:
            l.concepts = lesson_concepts(l.title)
            m = re.match(r"(\d+):(\d{2})", l.title)
            if m:
                l.t = int(m.group(1)) * 60 + int(m.group(2))
        if rv.is_jungle:
            from ..learn.skills import evaluate
            rv.checks = evaluate(rv.facts)
        return rv

    # ------------------------------------------------------------------ helpers

    def mine(self, text: str) -> str:
        return self.ev.add(text, SRC_MINE)

    def bench(self, text: str, games: int | None) -> str:
        from ..analysis.query import confidence

        return self.ev.add(text, f"Riot Match-V5 타임라인 · {self.scope.label}", games,
                           confidence(games) if games is not None else None)

    def pos_at(self, pid: int, ts_ms: float) -> tuple[float, float] | None:
        f = self.frames.get(pid, {})
        m = int(ts_ms // 60000)
        a, b = f.get(m), f.get(m + 1)
        if a and b:  # 1분 간격 위치를 시간 비율로 보간
            r = (ts_ms - m * 60000) / 60000
            return a["x"] + (b["x"] - a["x"]) * r, a["y"] + (b["y"] - a["y"]) * r
        if a:
            return a["x"], a["y"]
        return None

    def trade(self, events: list[dict], t_ms: float, team: int, window_ms: int = 60_000) -> str | None:
        """상대가 오브젝트를 먹은 앞뒤 1분 안에 우리가 다른 곳에서 얻은 것 (맞교환). 없으면 None."""
        got = []
        for e in events:
            if abs(e["ts_ms"] - t_ms) > window_ms:
                continue
            if e["type"] == "ELITE_MONSTER_KILL" and e["team_id"] == team:
                got.append(OBJ_KO.get(e["monster_type"], e["monster_type"]))
            elif e["type"] == "BUILDING_KILL" and e["team_id"] not in (team, None):
                got.append("포탑")
        plates = sum(1 for e in events if e["type"] == "TURRET_PLATE_DESTROYED" and abs(e["ts_ms"] - t_ms) <= window_ms
                     and e["team_id"] not in (team, None))
        kills = sum(1 for e in events if e["type"] == "CHAMPION_KILL" and abs(e["ts_ms"] - t_ms) <= window_ms
                    and self.by_pid.get(e["victim_id"], {}).get("team_id") not in (team, None))
        if plates >= 2:
            got.append(f"포탑 방패 {plates}개")
        if kills >= 2:
            got.append(f"킬 {kills}개")
        return ", ".join(dict.fromkeys(got)) if got else None

    def involved(self, e: dict, pid: int) -> bool:
        return e["participant_id"] == pid or pid in (e["assists"] or [])

    def team_of(self, pid: int) -> int:
        return self.by_pid[pid]["team_id"] if pid in self.by_pid else 0

    # ------------------------------------------------------------------ moments

    def moments(self, events: list[dict]) -> list[Moment]:
        me, ejg = self.me, self.enemy_jg
        pid, team = me["participant_id"], me["team_id"]
        out: list[Moment] = []
        f1 = self.frames.get(pid, {}).get(1)
        if f1:
            camp = min(team_camps(team).items(), key=lambda kv: math.dist(kv[1], (f1["x"], f1["y"])))[0]
            out.append(Moment(60, "start", f"1:00 {CAMP_KO[camp]} 근처에서 시작 ({'탑' if map_side(f1['x'], f1['y']) == 'top' else '봇'} 사이드)",
                              f1["x"], f1["y"]))
        f3 = self.frames.get(pid, {}).get(3)
        if f3 and me["position"] == "JUNGLE":
            camps = (f3["jcs"] or 0) // 4
            out.append(Moment(180, "clear", f"3:00까지 {camps}캠프 먹음, 위치: {REGION_KO[relative_region(team, f3['x'], f3['y'])]}",
                              f3["x"], f3["y"]))
        for e in events:
            if e["ts_ms"] > 15 * 60000:
                break
            t = e["ts_ms"] / 1000
            where = REGION_KO[relative_region(team, e["x"], e["y"])]
            if e["type"] == "CHAMPION_KILL":
                victim = self.by_pid.get(e["victim_id"])
                vname = self.name(victim["champion_id"]) if victim else "?"
                if e["victim_id"] == pid:
                    killers = [self.by_pid[k] for k in [e["participant_id"], *(e["assists"] or [])] if k in self.by_pid]
                    with_jg = ejg and any(k["participant_id"] == ejg["participant_id"] for k in killers)
                    out.append(Moment(t, "death", f"{mmss(t)} {where}에서 죽음"
                                      + (f" (상대 정글 {self.name(ejg['champion_id'])} 낌)" if with_jg else ""),
                                      e["x"], e["y"], False))
                elif self.involved(e, pid):
                    out.append(Moment(t, "kill" if e["participant_id"] == pid else "assist",
                                      f"{mmss(t)} {where}에서 {vname} 처치 {'(킬)' if e['participant_id'] == pid else '(어시스트)'}",
                                      e["x"], e["y"], True))
                elif ejg and victim and victim["team_id"] == team and self.involved(e, ejg["participant_id"]):
                    p = self.pos_at(pid, e["ts_ms"])
                    d = _dist(p, (e["x"], e["y"]))
                    mine = REGION_KO[relative_region(team, *p)] if p else "?"
                    out.append(Moment(t, "enemy_gank", f"{mmss(t)} 상대 정글이 {where}에서 아군 {vname} 잡음 — 나는 {mine}"
                                      + (f" (거리 {d:,.0f})" if d != float("inf") else ""), e["x"], e["y"], False))
            elif e["type"] == "ELITE_MONSTER_KILL":
                ours = e["team_id"] == team
                obj = OBJ_KO.get(e["monster_type"], e["monster_type"])
                p = self.pos_at(pid, e["ts_ms"])
                d = _dist(p, (e["x"], e["y"]))
                out.append(Moment(t, "objective", f"{mmss(t)} {'우리' if ours else '적'} 팀 {obj} 먹음"
                                  + (f" — 나와의 거리 {d:,.0f}" if d != float("inf") else ""), e["x"], e["y"], ours))
        for v in self.visits:
            if v.ts_ms > 15 * 60000 or v.death_back:
                continue
            if v.participant_id == pid:
                out.append(Moment(v.ts_ms / 1000, "recall", f"{mmss(v.ts_ms / 1000)} 귀환(아이템 구매)"))
            elif ejg and v.participant_id == ejg["participant_id"]:
                out.append(Moment(v.ts_ms / 1000, "enemy_recall", f"{mmss(v.ts_ms / 1000)} 상대 정글 귀환(아이템 구매)"))
        return sorted(out, key=lambda m: m.t)

    # ------------------------------------------------------------------ jungle review

    def jungle_review(self, rv: Review, events: list[dict], team_kills: int) -> None:
        s, me, ejg = self.scope, self.me, self.enemy_jg
        pid, champ, team = me["participant_id"], me["champion_id"], me["team_id"]
        cname = self.name(champ)
        fr = self.frames.get(pid, {})
        c = self.stats.champ(s, champ)
        if not c or c["games"] < 10:
            rv.notes.append(f"{cname} 고티어 정글 기록이 {c['games'] if c else 0}판뿐이라 비교하기 어려워요.")
        n = c["games"] if c else 0

        def metric(label, mine_v, bench_v, verdict, mine_text, bench_text, games=None):
            e = [self.mine(mine_text)]
            if bench_text:
                e.append(self.bench(bench_text, games))
            rv.metrics.append(Metric(label, mine_v, bench_v, verdict, e))
            return e

        # 1) 3:00 클리어
        clears = self.stats.clears(s, champ)
        tot = sum(r["games"] for r in clears)
        full = sum(r["games"] for r in clears if r["clear3"] == "full_clear") / tot if tot else None
        camps3 = (fr.get(3, {}).get("jcs") or 0) // 4 if fr.get(3) else None
        rv.facts["camps3"] = camps3
        rv.facts["full_clear_rate"] = full
        early_lane = next((e for e in events if e["type"] == "CHAMPION_KILL" and e["ts_ms"] < 210000
                           and self.involved(e, pid)), None)
        if camps3 is not None:
            verdict = "good" if camps3 >= 6 else ("bad" if camps3 <= 3 and not early_lane and (full or 0) >= 0.4
                                                  else "neutral")
            ev = metric("3:00까지 먹은 캠프", f"{camps3}캠프", f"풀캠 {pct(full)}" if full is not None else "-", verdict,
                        f"3:00 정글 CS {fr[3]['jcs']} → {camps3}캠프 먹음",
                        f"{cname} 3:00까지 풀캠한 비율 {pct(full)} (n={tot})" if tot else None, tot)
            if verdict == "bad":
                rv.lessons.append(Lesson(
                    "초반 정글링이 느렸음",
                    f"3:00에 {camps3}캠프였고, 그 전에 킬관여도 없었어요. 고티어 {josa(cname)} {pct(full)}가 3분 안에 풀캠을 해요. "
                    f"첫 동선에서 캠프를 빠뜨리지 말고, 일찍 빠질 거면 확실한 갱 각이 있을 때만 빠지세요.", 2, ev))
            elif verdict == "good":
                rv.strengths.append(Lesson("3분 안에 풀캠", f"3:00까지 6캠프를 다 먹었어요.", 1, ev))

        # 2) 10분 정글 CS
        f10 = fr.get(10)
        if f10 and c and c.get("jungle_cs10"):
            mine10, avg10 = f10["jcs"] or 0, c["jungle_cs10"]
            rv.facts.update(cs10=mine10, cs10_bench=avg10)
            r = mine10 / avg10 if avg10 else 1
            verdict = "bad" if r < 0.85 else "good" if r > 1.05 else "neutral"
            ev = metric("10분 정글 CS", f"{mine10}", f"{avg10:.0f}", verdict, f"10분 정글 몬스터 CS {mine10}",
                        f"{cname} 10분 평균 정글 CS {avg10:.1f} (n={n})", n)
            if verdict == "bad":
                rv.lessons.append(Lesson("10분까지 정글 몬스터를 덜 먹었음",
                                         f"10분 정글 CS {mine10}로 고티어 평균({avg10:.0f})의 {r * 100:.0f}%예요. "
                                         f"갱·싸움 사이사이 리젠된 캠프를 놓치지 말고 챙기세요.", 1 if me["win"] else 2, ev))

        # 3) 골드 차 vs 적 정글
        if ejg:
            ef = self.frames.get(ejg["participant_id"], {})
            gd10 = (fr[10]["gold"] - ef[10]["gold"]) if fr.get(10) and ef.get(10) else None
            m = self.stats.matchup(s, champ, ejg["champion_id"])
            base, bn, label = ((m["gd10"], m["games"], f"vs {self.name(ejg['champion_id'])}")
                               if m and m["games"] >= 10 else ((c or {}).get("gd10"), n, "모든 상대"))
            if gd10 is not None and base is not None:
                diff = gd10 - base
                verdict = "bad" if diff < -400 else "good" if diff > 400 else "neutral"
                ev = metric("10분 정글 골드 차", signed(gd10), signed(base), verdict,
                            f"10분 골드 차(vs 상대 정글 {self.name(ejg['champion_id'])}) {signed(gd10)}",
                            f"{cname} {label} 10분 정글 골드 차 평균 {signed(base)} (n={bn})", bn)
                if verdict == "bad":
                    rv.lessons.append(Lesson("10분 정글 골드 차이가 컸음",
                                             f"10분에 상대 정글보다 {abs(gd10):,.0f} 골드 밀렸어요(고티어 평균 {signed(base)}). "
                                             f"아래 데스·오브젝트 장면부터 확인하세요.", 2, ev))
                elif verdict == "good":
                    rv.strengths.append(Lesson("10분 정글 골드 앞섬", f"10분에 상대 정글보다 {gd10:+,.0f} 골드 앞섰어요.", 1, ev))

        # 4) 10분 전 데스 / 킬관여
        deaths10 = [e for e in events if e["type"] == "CHAMPION_KILL" and e["ts_ms"] < 600000 and e["victim_id"] == pid]
        rv.facts["deaths10"] = len(deaths10)
        rv.facts["risky_deaths10"] = sum(1 for e in deaths10
                                         if relative_region(team, e["x"], e["y"]) in ("enemy_jungle", "river"))
        tk10 = [e for e in events if e["type"] == "CHAMPION_KILL" and e["ts_ms"] < 600000
                and e["victim_id"] != pid and self.involved(e, pid)]
        if c:
            verdict = "bad" if len(deaths10) >= c["deaths10"] + 1 else "good" if not deaths10 else "neutral"
            metric("10분 전 데스", f"{len(deaths10)}", f"{c['deaths10']:.1f}", verdict,
                   f"10분 전 데스 {len(deaths10)}회", f"{cname} 10분 전 평균 데스 {c['deaths10']:.2f} (n={n})", n)
            verdict = "good" if len(tk10) >= c["takedowns10"] + 1 else "bad" if len(tk10) + 1 <= c["takedowns10"] else "neutral"
            metric("10분 전 킬관여", f"{len(tk10)}", f"{c['takedowns10']:.1f}", verdict,
                   f"10분 전 킬·어시스트 {len(tk10)}회", f"{cname} 10분 전 평균 킬관여 {c['takedowns10']:.2f} (n={n})", n)
        for e in deaths10[:2]:
            where = relative_region(team, e["x"], e["y"])
            with_jg = ejg and self.involved(e, ejg["participant_id"])
            t = e["ts_ms"] / 1000
            text = f"{mmss(t)} {REGION_KO[where]}에서 죽었어요" + (" (상대 정글 낌)" if with_jg else "") + ". "
            ev = [self.mine(f"{mmss(t)} {REGION_KO[where]} 데스, 상대 정글 낌: {'예' if with_jg else '아니오'}")]
            if ejg and 150 <= t <= 300:
                sides = self.stats.sides(s, ejg["champion_id"], ejg["team_id"])
                col = "side3" if t < 210 else "side4"
                d = sides[col]
                tot_s = sum(d.values())
                if tot_s >= 10:
                    side_here = map_side(e["x"], e["y"])
                    share = d.get(side_here, 0) / tot_s
                    ev.append(self.bench(f"상대 {self.name(ejg['champion_id'])} {'3:00' if col == 'side3' else '4:00'} "
                                         f"{'탑' if side_here == 'top' else '봇'} 사이드 비율 {pct(share)} (n={tot_s})", tot_s))
                    if share >= 0.6:
                        text += (f"고티어 {josa(self.name(ejg['champion_id']))} 이 시간에 {pct(share)} 확률로 바로 그 사이드에 있어요. "
                                 f"이때는 반대편에서 움직이거나, 들어가기 전에 시야부터 잡았어야 해요.")
                    else:
                        text += "상대 정글 위치를 알기 어려운 때였으니 들어가기 전에 시야부터 확인했어야 해요."
            elif where in ("enemy_jungle", "river"):
                text += "상대 정글이나 강가에서 죽었다면, 들어가기 전에 미니맵으로 상대 정글과 라인에 안 보이는 적부터 확인하세요."
            else:
                text += "죽기 직전 상황을 리플레이로 확인해 보세요."
            rv.lessons.append(Lesson(f"{mmss(t)} 데스", text, 3 if t < 600 else 2, ev))

        # 5) 적 정글 갱을 막지 못한 순간 (10분 전, 아군 사망 + 적 정글 관여, 내가 멀리 있음)
        if ejg:
            for e in events:
                if e["type"] != "CHAMPION_KILL" or e["ts_ms"] >= 600000:
                    continue
                victim = self.by_pid.get(e["victim_id"])
                if not victim or victim["team_id"] != team or e["victim_id"] == pid:
                    continue
                if not self.involved(e, ejg["participant_id"]):
                    continue
                p = self.pos_at(pid, e["ts_ms"])
                lane = region(e["x"], e["y"])
                if lane not in ("top", "mid", "bot") or not p:
                    continue
                t = e["ts_ms"] / 1000
                same_side = map_side(*p) == map_side(e["x"], e["y"])
                ev = [self.mine(f"{mmss(t)} 상대 {josa(self.name(ejg['champion_id']), '이가')} {REGION_KO[lane]}에서 아군 "
                                f"{self.name(victim['champion_id'])} 킬에 낌, 그때 내 위치 "
                                f"{REGION_KO[relative_region(team, *p)]}")]
                rv.facts["enemy_ganks10"] = sum(
                    1 for x in events if x["type"] == "CHAMPION_KILL" and x["ts_ms"] < 600000
                    and self.by_pid.get(x["victim_id"], {}).get("team_id") == team and x["victim_id"] != pid
                    and self.involved(x, ejg["participant_id"]) and region(x["x"], x["y"]) in ("top", "mid", "bot"))
                rv.lessons.append(Lesson(
                    f"{mmss(t)} {REGION_KO[lane]} 갱 당함",
                    f"상대 {josa(self.name(ejg['champion_id']), '이가')} {mmss(t)}에 {REGION_KO[lane]}에서 아군 "
                    f"{josa(self.name(victim['champion_id']), '을를')} 잡았고, 그때 나는 {REGION_KO[relative_region(team, *p)]}"
                    f"({'같은' if same_side else '반대'} 사이드)에 있었어요. "
                    + ("같은 쪽에 있었으니 역갱(커버) 각이 있었어요." if same_side else
                       "반대편에 있었다면 그동안 내 쪽에서 캠프·바위게·반대쪽 갱으로 이득을 챙겼어야 해요."),
                    2, ev))
                break  # 가장 이른 한 번만

        # 6) 오브젝트
        times = self.stats.objectives(s) or {}
        lost_once: dict[str, float] = {}
        for e in events:
            if e["type"] != "ELITE_MONSTER_KILL" or e["ts_ms"] > 20 * 60000:
                continue
            ours = e["team_id"] == team
            obj = OBJ_KO.get(e["monster_type"], e["monster_type"])
            p = self.pos_at(pid, e["ts_ms"])
            d = _dist(p, (e["x"], e["y"]))
            t = e["ts_ms"] / 1000
            # 유충처럼 연달아 잡히는 오브젝트는 3분 안의 것은 한 번만 피드백
            recent = lost_once.get(e["monster_type"])
            trade = self.trade(events, e["ts_ms"], team) if not ours and d > FAR else None
            if trade:
                ev = [self.mine(f"{mmss(t)} 상대 {obj} 때 우리 팀이 얻은 것: {trade}")]
                rv.strengths.append(Lesson(f"{mmss(t)} {obj} 맞교환", f"{josa(obj, '을를')} 내준 대신 {trade} 챙겼어요.", 1, ev))
                rv.facts["traded"] = rv.facts.get("traded", 0) + 1
            elif not ours and d > FAR and (recent is None or t - recent > 180):
                lost_once[e["monster_type"]] = t
                rv.facts["far_lost"] = rv.facts.get("far_lost", 0) + 1
                med = {"DRAGON": times.get("first_dragon_median_s"), "HORDE": times.get("first_grub_median_s"),
                       "RIFTHERALD": times.get("herald_median_s")}.get(e["monster_type"])
                ev = [self.mine(f"{mmss(t)} 상대 팀 {obj} 먹음, 그때 나와의 거리 {d:,.0f}")]
                if med:
                    ev.append(self.bench(f"첫 {obj} 보통 잡는 시각(중앙값) {mmss(med)} (n={times.get('matches')})",
                                         times.get("matches")))
                rv.lessons.append(Lesson(
                    f"{mmss(t)} {obj} 합류 못 하고 내줌",
                    f"상대가 {josa(obj, '을를')} 가져갈 때 나는 {d:,.0f} 거리(맵 약 {d / 14870 * 100:.0f}%)에 있었어요. "
                    + (f"고티어 기준 첫 {josa(obj)} 보통 {mmss(med)}쯤 잡히니, 1분 전에 귀환하고 근처 라인 주도권을 잡은 뒤 자리 잡았어야 해요."
                       if med else "오브젝트 나오기 1분 전에는 귀환해서 정비하고 근처에 있어야 해요.")
                    + " 반대편에서 얻은 것(포탑·오브젝트·킬)도 없었어요.",
                    3, ev))
            elif ours:
                ev = [self.mine(f"{mmss(t)} 우리 팀 {obj} 먹음")]
                rv.strengths.append(Lesson(f"{mmss(t)} {obj} 획득", f"{josa(obj, '을를')} 챙겼어요.", 1, ev))

        # 7) 시야·카정·킬관여율
        if c:
            minutes = rv_minutes = max(self.store._x("SELECT duration_s FROM matches WHERE match_id=?",
                                                      [rv.match_id])[0][0] / 60, 1)
            vpm = (me["vision_score"] or 0) / minutes
            rv.facts.update(vision_pm=vpm, vision_bench=c.get("vision_pm"))
            if c.get("vision_pm"):
                verdict = "bad" if vpm < c["vision_pm"] * 0.75 else "good" if vpm > c["vision_pm"] * 1.15 else "neutral"
                ev = metric("분당 시야 점수", f"{vpm:.2f}", f"{c['vision_pm']:.2f}", verdict,
                            f"시야 점수 {me['vision_score']} / {rv_minutes:.0f}분",
                            f"{cname} 평균 분당 시야 점수 {c['vision_pm']:.2f} (n={n})", n)
                if verdict == "bad":
                    rv.lessons.append(Lesson("시야 작업 부족",
                                             f"분당 시야 점수 {vpm:.2f}로 고티어 평균({c['vision_pm']:.2f})보다 낮아요. "
                                             f"오브젝트 1분 전 와드와 제어 와드(이번 판 {me['control_wards']}개, "
                                             f"평균 {c['control_wards']:.1f}개)를 늘리세요.", 1, ev))
            kp = (me["kills"] + me["assists"]) / max(team_kills, 1)
            verdict = "bad" if kp < c["kp"] - 0.1 else "good" if kp > c["kp"] + 0.1 else "neutral"
            metric("킬관여율", pct(kp), pct(c["kp"]), verdict, f"킬관여율 {pct(kp)}",
                   f"{cname} 평균 킬관여율 {pct(c['kp'])} (n={n})", n)
            metric("카정한 몬스터", f"{me['enemy_jungle_minions']}", f"{c['enemy_jungle_cs']:.1f}", "neutral",
                   f"상대 정글 몬스터 처치 {me['enemy_jungle_minions']}",
                   f"{cname} 평균 상대 정글 몬스터 처치 {c['enemy_jungle_cs']:.1f} (n={n})", n)

        # 8) 레벨 구간 교전 (적 정글과)
        if ejg:
            d = self.stats.duels(s, champ)
            mine_duels = []
            for e in events:
                if e["type"] != "CHAMPION_KILL" or e["ts_ms"] >= 900000:
                    continue
                won = e["victim_id"] == ejg["participant_id"] and self.involved(e, pid)
                lost = e["victim_id"] == pid and self.involved(e, ejg["participant_id"])
                if won or lost:
                    lvl = (fr.get(int(e["ts_ms"] // 60000)) or {}).get("level") or 1
                    band = "1-3" if lvl <= 3 else "4-5" if lvl <= 5 else "6+"
                    mine_duels.append((e["ts_ms"] / 1000, band, won))
            for t, band, won in mine_duels[:2]:
                if band in d and d[band]["fights"] >= 15:
                    rate = d[band]["won"] / d[band]["fights"]
                    ev = [self.mine(f"{mmss(t)} 상대 정글과 싸움 {'승' if won else '패'} ({BAND_KO[band]})"),
                          self.bench(f"{cname} {BAND_KO[band]} 정글 1:1 승률 {pct(rate)} (n={d[band]['fights']})",
                                     d[band]["fights"])]
                    if not won and rate < 0.45:
                        rv.facts["bad_band_fight"] = True
                        rv.lessons.append(Lesson(f"{mmss(t)} 레벨 불리할 때 싸움",
                                                 f"{BAND_KO[band]}에 상대 정글과 싸워서 졌어요. 고티어 {cname}도 이 레벨대 정글 1:1 승률이 "
                                                 f"{pct(rate)}로 낮은 편이라, 이 레벨대엔 싸우지 말고 파밍했어야 해요.", 2, ev))

        # 9) 턴: 첫 귀환 시각, 오브젝트 직전 귀환, 골드 들고 사망
        self.turn_review(rv, events)

    def turn_review(self, rv: Review, events: list[dict]) -> None:
        s, me = self.scope, self.me
        pid, champ, team = me["participant_id"], me["champion_id"], me["team_id"]
        cname = self.name(champ)
        mine = [v for v in self.visits if v.participant_id == pid]
        first = next((v for v in mine if not v.death_back), None)
        rv.facts["first_recall_s"] = first.ts_ms / 1000 if first else None
        fr = self.stats.first_recall(s, champ)
        if first and fr and fr["games"] >= 10:
            t = first.ts_ms / 1000
            verdict = "neutral" if fr["p25_s"] <= t <= fr["p75_s"] else "bad" if t > fr["p75_s"] + 60 else "neutral"
            rv.metrics.append(Metric("첫 귀환", mmss(t), f"{mmss(fr['median_s'])} ({mmss(fr['p25_s'])}~{mmss(fr['p75_s'])})",
                                     verdict, [self.mine(f"첫 귀환(첫 아이템 구매) {mmss(t)}"),
                                               self.bench(f"{cname} 첫 귀환 시각(중앙값) {mmss(fr['median_s'])}, "
                                                          f"25~75% {mmss(fr['p25_s'])}~{mmss(fr['p75_s'])} (n={fr['games']})",
                                                          fr["games"])]))

        firsts: dict[str, dict] = {}
        for e in events:
            if e["type"] == "ELITE_MONSTER_KILL" and e["monster_type"] in OBJECTIVE_LANES and e["monster_type"] != "RIFTHERALD":
                firsts.setdefault(e["monster_type"], e)
        for obj, e in firsts.items():
            if e["ts_ms"] > 20 * 60000:
                continue
            lanes = [p["participant_id"] for p in self.by_pid.values()
                     if p["team_id"] == team and p["position"] in OBJECTIVE_LANES[obj]]
            turn = team_turn(self.visits, e["ts_ms"], pid, lanes)
            rv.facts.setdefault("obj_turns", {})[obj] = {"turn": turn, "took": e["team_id"] == team}
            took = e["team_id"] == team
            stats = self.stats.turn_objective(s, obj)
            name = TURN_OBJ_KO[obj]
            t = e["ts_ms"] / 1000
            lo, hi = mmss(t - SETUP_FROM_MS / 1000), mmss(t - SETUP_TO_MS / 1000)
            ev = [self.mine(f"{name} {mmss(t)}에 {'우리' if took else '상대'} 팀이 처음 먹음, 그 직전 우리 팀 상태: {TURN_KO[turn]}")]
            prep = [stats[k] for k in ("sync", "jg_only") if k in stats]
            pg = sum(r["games"] for r in prep)
            if pg and "none" in stats and "late" in stats:
                prep_rate = sum(r["took"] for r in prep) / pg
                none_rate = stats["none"]["took"] / stats["none"]["games"]
                late_rate = stats["late"]["took"] / stats["late"]["games"]
                ev.append(self.bench(f"{name} 귀환 타이밍별 획득률: 미리 귀환 {pct(prep_rate)} (n={pg}), 안 함 {pct(none_rate)} "
                                     f"(n={stats['none']['games']}), 직전 30초 안에 귀환 {pct(late_rate)} (n={stats['late']['games']})",
                                     min(pg, stats["none"]["games"], stats["late"]["games"])))
            else:
                prep_rate = none_rate = late_rate = None
            if turn == "late":
                rv.lessons.append(Lesson(
                    f"{mmss(t)} {name} 직전에 귀환 중",
                    f"{josa(name, '이가')} {mmss(t)}에 잡혔는데, 그 직전 30초 안에 나는 귀환해서 본진에 있었어요."
                    + (f" 고티어에서 이런 팀이 가져간 비율은 {pct(late_rate)}뿐이에요." if late_rate is not None else "")
                    + f" {lo}~{hi} 사이에 미리 귀환해서 정비하고 자리를 잡았어야 해요.", 3, ev))
            # '미리 귀환 안 함'은 지적하지 않는다: 프로·챌린저·플래티넘 모두 40% 안팎만 미리 귀환했고
            # 프로 경기에선 미리 귀환한 팀(62%)과 안 한 팀(63%)의 획득률이 같았다 (research_notes/검증/검증 결과.md).
            elif turn in ("sync", "jg_only") and took:
                rv.strengths.append(Lesson(f"{name} 전 귀환 타이밍 좋음", f"{lo}~{hi}에 미리 귀환해서 {josa(name, '을를')} 가져갔어요.",
                                           1, ev))

        for e in events:
            if e["type"] != "CHAMPION_KILL" or e["victim_id"] != pid or e["ts_ms"] > 20 * 60000:
                continue
            f = self.frames.get(pid, {}).get(int(e["ts_ms"] // 60000)) or {}
            cur = f.get("cur")
            if cur is not None and cur >= 1200:
                rv.facts["gold_death"] = cur
                t = e["ts_ms"] / 1000
                rv.lessons.append(Lesson(
                    f"{mmss(t)} 골드 들고 죽음",
                    f"죽기 직전({int(e['ts_ms'] // 60000)}:00)에 안 쓴 골드를 {cur:,}골드나 들고 있었어요. "
                    f"이만큼 모였으면 싸우기 전에 먼저 귀환해서 템부터 샀어야 해요.", 2,
                    [self.mine(f"{int(e['ts_ms'] // 60000)}:00 보유 골드 {cur:,}, {mmss(t)} 데스")]))
                break


TURN_OBJ_KO = {"DRAGON": "첫 드래곤", "HORDE": "공허 유충"}


# 피드백 제목 키워드 → 학습 개념 (먼저 맞는 것부터)
LESSON_CONCEPTS = [
    ("직전에 귀환", ["recall-timing", "turn-tempo", "objective-setup"]),
    ("귀환 타이밍", ["recall-timing", "turn-tempo", "objective-setup"]),
    ("골드 들고", ["recall-timing"]),
    ("정글링", ["full-clear", "jungle-pathing", "clear-efficiency"]),
    ("풀캠", ["full-clear", "jungle-pathing", "clear-efficiency"]),
    ("정글 몬스터", ["clear-efficiency", "jungle-pathing"]),
    ("데스", ["jungle-tracking", "vision-control", "invading"]),
    ("갱 당함", ["counter-gank", "jungle-tracking", "cross-map"]),
    ("합류 못 하고 내줌", ["objective-setup", "turn-tempo", "cross-map"]),
    ("레벨 불리", ["power-spikes"]),
    ("시야", ["vision-control"]),
    ("정글 골드", ["ganking", "clear-efficiency"]),
    ("획득", ["objective-setup"]),
]


def lesson_concepts(title: str) -> list[str]:
    for key, ids in LESSON_CONCEPTS:
        if key in title:
            return ids
    return []
