"""챔피언 선택 상태 + 통계 DB → 브리핑.

모든 문장은 근거(Evidence)를 참조한다. kind="inference" 인 항목은 근거에서 규칙으로
도출한 판단이며, 어떤 근거에서 나왔는지 evidence 목록으로 남긴다.
"""

from __future__ import annotations

import itertools
import math

from ..analysis.geometry import CAMP_KO, map_side, team_camps
from ..analysis.query import Scope, StatsDB, confidence, logit, shrink, sigmoid
from ..ddragon import ChampionIndex
from ..lcu.champselect import ChampSelectState, Stage
from ..sources.guides import TOPIC_KO
from .models import Briefing, Card, EvidenceLog, Item, Recommendation

SRC_TIMELINE = "Riot Match-V5 타임라인"
LANE_KO = {"top": "탑", "mid": "미드", "bot": "봇"}
POS_KO = {"TOP": "탑", "JUNGLE": "정글", "MIDDLE": "미드", "BOTTOM": "원딜", "UTILITY": "서폿"}
LCU_POS = {"top": "TOP", "jungle": "JUNGLE", "middle": "MIDDLE", "bottom": "BOTTOM", "utility": "UTILITY"}
LANE_POS = {"top": "TOP", "mid": "MIDDLE", "bot": "BOTTOM"}
REGION_KO = {"own_jungle": "자기 정글", "enemy_jungle": "상대 정글", "river": "강가", "top": "탑 라인",
             "mid": "미드 라인", "bot": "봇 라인", "base": "기지(귀환/사망)", "unknown": "알 수 없음"}
ROLE_ORDER = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]


def pct(x: float | None) -> str:
    return "-" if x is None else f"{x * 100:.0f}%"


def mmss(sec: float | None) -> str:
    if sec is None:
        return "-"
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def josa(word: str, pair: str = "은는") -> str:
    """받침 유무에 따라 은/는, 이/가, 와/과, 을/를 선택."""
    ch = word[-1] if word else ""
    has_final = "가" <= ch <= "힣" and (ord(ch) - 0xAC00) % 28 != 0
    return word + (pair[0] if has_final else pair[1])


MIN_INFER = 15  # 판단(inference)을 내리기 위한 최소 표본 수


def signed(x: float | None, unit: str = "") -> str:
    return "-" if x is None else f"{x:+.0f}{unit}"


class BriefingEngine:
    def __init__(self, stats: StatsDB, champs: ChampionIndex, guides_path=None) -> None:
        self.stats = stats
        self.champs = champs
        self.guides_path = guides_path

    def name(self, cid: int) -> str:
        return self.champs.name(cid)

    def key(self, cid: int) -> str:
        c = self.champs.get(cid)
        return c.key if c else ""

    # ------------------------------------------------------------------ entry

    def build(self, state: ChampSelectState) -> Briefing:
        b = Briefing(stage=state.stage.value)
        if not self.stats.available:
            b.notes.append("통계 DB 가 없습니다. `loldosa update` 로 수집·분석을 먼저 실행하세요.")
            return b
        with self.stats.session():
            return self._build(state, b)

    def _build(self, state: ChampSelectState, b: Briefing) -> Briefing:
        s = self.stats.pick_scope("apex")
        self.scope = s
        self.ev = EvidenceLog()
        b.scope_label = s.label
        if state.me and not state.is_jungle and state.my_position:
            b.notes.append(f"이번 판 포지션이 정글이 아닙니다({state.my_position}). 정글 기준 정보만 제공합니다.")

        roles = self.infer_enemy_roles(s, state)
        enemy_jg = roles.get("JUNGLE", 0)
        me = state.me
        my_champ = (me.champion_id or me.intent_id) if me else 0

        if state.stage in (Stage.PLANNING, Stage.BANNING, Stage.PRE_MY_PICK):
            b.picks = self.recommend_picks(s, state, enemy_jg)
            if state.stage in (Stage.PLANNING, Stage.BANNING):
                b.bans = self.recommend_bans(s, state, my_champ)

        if my_champ:
            b.my_champion, b.my_champion_name = my_champ, self.name(my_champ)
            if enemy_jg:
                b.enemy_jungler, b.enemy_jungler_name = enemy_jg, self.name(enemy_jg)
            if me and not me.locked:
                b.notes.append(f"{self.name(my_champ)} 선택 예정 기준 미리보기입니다.")
            b.cards = [
                self.card_route(s, state, my_champ, enemy_jg),
                self.card_ganks(s, state, my_champ, enemy_jg, roles),
                self.card_matchup(s, my_champ, enemy_jg),
                self.card_objectives(s, state, my_champ, roles),
                self.card_comp(s, state, my_champ, roles),
                self.card_insights(my_champ, enemy_jg),
            ]
            b.cards = [c for c in b.cards if c and c.items]
        b.evidence = self.ev.items
        return b

    # ------------------------------------------------------------ helpers

    def src(self, s: Scope | None = None) -> str:
        return f"{SRC_TIMELINE} · {(s or self.scope).label}"

    def e(self, text: str, games: int | None, s: Scope | None = None) -> str:
        return self.ev.add(text, self.src(s), games, confidence(games) if games is not None else None)

    def infer_enemy_roles(self, s: Scope, state: ChampSelectState) -> dict[str, int]:
        """솔랭 적팀 포지션은 비공개 → 챔피언별 포지션 분포로 가장 그럴듯한 배치를 찾는다."""
        known = [e.champion_id for e in state.enemies if e.champion_id and e.locked]
        if not known:
            return {}
        probs = {}
        for c in known:
            pos = self.stats.positions(s, c)
            tot = sum(pos.values())
            probs[c] = {r: (pos.get(r, 0) + 0.2) / (tot + 1) for r in ROLE_ORDER}
        best, best_p = None, -1.0
        for perm in itertools.permutations(ROLE_ORDER, len(known)):
            p = math.prod(probs[c][r] for c, r in zip(known, perm))
            if p > best_p:
                best, best_p = perm, p
        return {r: c for c, r in zip(known, best)} if best else {}

    def ally_roles(self, state: ChampSelectState) -> dict[str, int]:
        return {LCU_POS.get(a.position, ""): a.champion_id for a in state.allies
                if a.champion_id and a.position and a.cell_id != state.local_cell_id}

    def damage_profile(self, champ_ids: list[int]) -> tuple[str, float, int]:
        meta = [self.champs.get(c) for c in champ_ids if self.champs.get(c)]
        if not meta:
            return "unknown", 0.5, 0
        ap = sum(c.ap_share for c in meta) / len(meta)
        front = sum(c.frontline for c in meta)
        prof = "ad_heavy" if ap < 0.42 else "ap_heavy" if ap > 0.58 else "balanced"
        return prof, ap, front

    # ------------------------------------------------------------ picks / bans

    def recommend_picks(self, s: Scope, state: ChampSelectState, enemy_jg: int, n: int = 5) -> list[Recommendation]:
        pool = self.stats.jungle_pool(s, min_games=5) or self.stats.jungle_pool(s, min_games=1)
        locked = {x.champion_id for x in state.allies + state.enemies if x.locked and x.champion_id}
        unavailable = locked | set(state.ally_bans) | set(state.enemy_bans)
        allies = [a.champion_id for a in state.allies
                  if a.locked and a.champion_id and a.cell_id != state.local_cell_id]
        enemies = [x.champion_id for x in state.enemies if x.locked and x.champion_id and x.champion_id != enemy_jg]
        prof = self.damage_profile(allies)[0] if len(allies) >= 2 else None

        scored = []
        for c in pool:
            cid = c["champion_id"]
            if cid in unavailable:
                continue
            p0 = c["win_rate_adj"]
            L = logit(p0)
            parts: list[tuple[str, float, int]] = [
                (f"{self.name(cid)} 정글 승률 {pct(c['wins'] / c['games'])} (보정 {pct(p0)}), "
                 f"픽률 {pct(c['pick_rate'])}", 0.0, c["games"])]
            if enemy_jg:
                m = self.stats.matchup(s, cid, enemy_jg)
                if m:
                    d = logit(shrink(m["wins"], m["games"], p0, k=15)) - logit(p0)
                    L += d
                    parts.append((f"상대 정글 {self.name(enemy_jg)} 상대 {pct(m['win_rate'])}", d, m["games"]))
            for ally in allies:
                r = self.stats.synergy(s, cid, ally)
                if r:
                    d = 0.5 * (logit(shrink(r["wins"], r["games"], p0, k=30)) - logit(p0))
                    L += d
                    parts.append((f"아군 {josa(self.name(ally), '과와')} 같은 팀일 때 {pct(r['wins'] / r['games'])}", d, r["games"]))
            for en in enemies:
                r = self.stats.versus(s, cid, en)
                if r:
                    d = 0.5 * (logit(shrink(r["wins"], r["games"], p0, k=30)) - logit(p0))
                    L += d
                    parts.append((f"적 {self.name(en)} 상대 {pct(r['wins'] / r['games'])}", d, r["games"]))
            if prof:
                r = self.stats.comp_fit(s, cid, prof)
                if r:
                    d = logit(shrink(r["wins"], r["games"], p0, k=30)) - logit(p0)
                    L += d
                    parts.append((f"아군 조합이 {PROFILE_KO[prof]}일 때 {pct(r['wins'] / r['games'])}", d, r["games"]))
            scored.append((sigmoid(L), cid, parts))

        scored.sort(key=lambda t: -t[0])
        out = []
        for score, cid, parts in scored[:n]:
            rec = Recommendation(cid, self.name(cid), score, self.key(cid))
            # 기본 승률 + 영향이 큰 요인 순으로
            base, rest = parts[0], sorted(parts[1:], key=lambda p: -abs(p[1]))
            for text, d, games in [base] + rest[:3]:
                eid = self.e(f"{text} (n={games})", games)
                label = "" if d == 0 else (" ▲" if d > 0.02 else " ▼" if d < -0.02 else " ·")
                rec.reasons.append(Item(text + label, "fact", [eid]))
            pro = self.stats.pro_champ(cid)
            if pro:
                eid = self.ev.add(f"프로 대회 {self.name(cid)} 정글 {pro['games']}경기, 승률 "
                                  f"{pct(pro['wins'] / pro['games'])}, 선수 {pro['players']}명 ({pro['leagues']})",
                                  SRC_PRO, pro["games"], confidence(pro["games"]))
                rec.reasons.append(Item(f"프로 대회 {pro['games']}경기 승률 {pct(pro['wins'] / pro['games'])} (참고, 점수 미반영)",
                                        "fact", [eid]))
            out.append(rec)
        return out

    def recommend_bans(self, s: Scope, state: ChampSelectState, my_champ: int) -> list[Recommendation]:
        pool = self.stats.jungle_pool(s, min_games=5)
        taken = set(state.ally_bans) | set(state.enemy_bans) | {my_champ}
        out: list[Recommendation] = []
        if my_champ:
            for m in self.stats.worst_matchups(s, my_champ, min_games=3, limit=6):
                if m["enemy_id"] in taken or len(out) >= 2:
                    continue
                text = (f"{josa(self.name(my_champ), '이가')} {self.name(m['enemy_id'])} 상대 정글 승률 "
                        f"{pct(m['wins'] / m['games'])}, 10분 골드 {signed(m['gd10'])}")
                eid = self.e(f"{text} (n={m['games']})", m["games"])
                out.append(Recommendation(m["enemy_id"], self.name(m["enemy_id"]), 1 - m["win_rate_adj"], self.key(m["enemy_id"]),
                                          [Item(f"내 챔피언 카운터: {text}", "fact", [eid])]))
                taken.add(m["enemy_id"])
        threats = sorted(
            (c for c in pool if c["champion_id"] not in taken),
            key=lambda c: -((c["pick_rate"] + c["ban_rate"]) * (c["win_rate_adj"] - 0.47)),
        )
        for c in threats[: 3 if out else 5]:
            text = (f"{self.name(c['champion_id'])} 정글 승률 {pct(c['wins'] / c['games'])}, "
                    f"픽률 {pct(c['pick_rate'])}, 밴률 {pct(c['ban_rate'])}")
            eid = self.e(f"{text} (n={c['games']})", c["games"])
            out.append(Recommendation(c["champion_id"], self.name(c["champion_id"]), c["win_rate_adj"], self.key(c["champion_id"]),
                                      [Item(f"메타 위협: {text}", "fact", [eid])]))
        return out

    # ------------------------------------------------------------ cards

    def _start_line(self, s: Scope, champ: int, team: int) -> tuple[str | None, str | None, dict]:
        rows = self.stats.start_camps(s, champ, team)
        tot = sum(r["games"] for r in rows)
        if not tot:
            return None, None, {}
        side_share: dict[str, float] = {}
        for r in rows:
            cx, cy = team_camps(team)[r["start_camp"]]
            side_share[map_side(cx, cy)] = side_share.get(map_side(cx, cy), 0) + r["games"] / tot
        top = rows[:3]
        text = ", ".join(f"{CAMP_KO[r['start_camp']]} {pct(r['games'] / tot)}" for r in top)
        eid = self.e(f"{self.name(champ)} {'블루' if team == 100 else '레드'} 진영 시작 캠프(1:00 위치 기준): "
                     f"{text} (n={tot})", tot)
        return text, eid, side_share

    def card_route(self, s, state, champ, enemy_jg) -> Card:
        team = state.my_team_id
        card = Card("route", "시작·초반 동선", "")
        text, eid, my_side = self._start_line(s, champ, team)
        if text:
            card.add(f"내 시작 캠프 분포: {text}", eid)
        rows = self.stats.clears(s, champ)
        tot = sum(r["games"] for r in rows)
        if tot:
            by_clear: dict[str, int] = {}
            for r in rows:
                by_clear[r["clear3"]] = by_clear.get(r["clear3"], 0) + r["games"]
            share = {k: by_clear.get(k, 0) / tot for k in CLEAR_KO}
            parts = ", ".join(f"{CLEAR_KO[k]} {pct(v)}" for k, v in share.items())
            e2 = self.e(f"{self.name(champ)} 3:00 시점 완료 캠프 수(정글 CS ÷ 4, 스커틀 생성 전): {parts} (n={tot})", tot)
            card.add(f"3:00까지 클리어: {parts}", e2)

            def where(kind: str) -> tuple[str, int]:
                sub = [r for r in rows if r["clear3"] == kind]
                n = sum(r["games"] for r in sub)
                if not n:
                    return "", 0
                agg: dict[str, int] = {}
                for r in sub:
                    agg[r["route3"]] = agg.get(r["route3"], 0) + r["games"]
                top = sorted(agg.items(), key=lambda kv: -kv[1])[:3]
                return ", ".join(f"{REGION_KO.get(k, k)} {pct(v / n)}" for k, v in top), n

            for kind in ("full_clear", "three_or_less"):
                text, n = where(kind)
                if text and n >= 5:
                    e3 = self.e(f"{self.name(champ)} {CLEAR_KO[kind]} 그룹의 3:00 위치: {text} (n={n})", n)
                    card.add(f"{CLEAR_KO[kind]}인 판의 3:00 위치: {text}", e3)

            main_kind, main_share = max(share.items(), key=lambda kv: kv[1])
            if tot >= MIN_INFER:
                if main_kind == "full_clear" and main_share >= 0.5:
                    card.headline = f"{self.name(champ)}: 풀클리어 중심 (3:00까지 6캠프 {pct(main_share)})"
                    card.add(f"고티어 {josa(self.name(champ))} 대부분 3분 안에 6캠프를 다 돌고, 그 뒤 스커틀(3:30)이나 "
                             f"라인으로 이동합니다.", e2, kind="inference")
                elif share["three_or_less"] >= 0.35:
                    card.headline = f"{self.name(champ)}: 3캠프 후 이른 개입 비중 높음 ({pct(share['three_or_less'])})"
                    card.add(f"고티어 {self.name(champ)}는 3캠프 이하에서 정글을 벗어나 갱·카정을 가는 비율이 높습니다.",
                             e2, kind="inference")
                else:
                    card.headline = f"{self.name(champ)}: 클리어 방식 혼합 (풀클 {pct(share['full_clear'])})"
            else:
                card.headline = f"{self.name(champ)}: 동선 표본 부족 (n={tot})"
        if enemy_jg:
            et, eeid, eside = self._start_line(s, enemy_jg, state.enemy_team_id)
            if et:
                card.add(f"적 {self.name(enemy_jg)} 예상 시작: {et}", eeid)
                side, share = max(eside.items(), key=lambda kv: kv[1])
                etot = sum(r["games"] for r in self.stats.start_camps(s, enemy_jg, state.enemy_team_id))
                if share >= 0.6 and etot >= MIN_INFER:
                    other = "봇" if side == "top" else "탑"
                    card.add(f"적 정글은 {'탑' if side == 'top' else '봇'} 사이드 시작 확률이 높습니다({pct(share)}). "
                             f"초반 3~4분에는 반대편({other}) 사이드 라인이 상대 정글 개입에서 상대적으로 안전합니다.",
                             eeid, kind="inference")
                    card.headline += f" · 적 {self.name(enemy_jg)} {'탑' if side == 'top' else '봇'} 시작 {pct(share)}"
        if not card.headline:
            card.headline = "데이터 부족"
        return card

    def card_ganks(self, s, state, champ, enemy_jg, roles) -> Card:
        card = Card("ganks", "갱킹 타이밍·대상", "")
        fg = self.stats.first_ganks(s, champ)
        tot = sum(r["games"] for r in fg)
        if tot:
            parts = ", ".join(f"{LANE_KO[r['lane']]} {pct(r['games'] / tot)}" for r in fg)
            med = sorted(fg, key=lambda r: -r["games"])[0]
            eid = self.e(f"{self.name(champ)} 8분 이전 라인에서 처음 킬이 난 갱: {parts}; 가장 많은 {LANE_KO[med['lane']]} "
                         f"중앙 시점 {mmss(med['median_s'])}, 그중 우리 쪽이 킬을 낸 비율 {pct(med['kill_rate'])} "
                         f"(n={tot}, 킬 없이 끝난 갱 시도는 타임라인에 남지 않아 제외)", tot)
            card.add(f"첫 갱(킬로 이어진 것) 라인 분포: {parts}, 가장 흔한 {LANE_KO[med['lane']]} 갱 시점 "
                     f"{mmss(med['median_s'])}", eid)
        curve = {r["minute"]: r for r in self.stats.curve(s, champ)}
        if 3 in curve:
            eid = self.e(f"{self.name(champ)} 평균 레벨: 3분 {curve[3]['level']:.1f}, "
                         f"6분 {curve.get(6, curve[3])['level']:.1f} (n={curve[3]['games']})", curve[3]["games"])
            card.add(f"평균 레벨 3분 {curve[3]['level']:.1f} / 6분 {curve.get(6, curve[3])['level']:.1f}", eid)

        base = self.stats.gank_lane_base(s)
        allies = self.ally_roles(state)
        scores = []
        for lane, pos in LANE_POS.items():
            ally, enemy = allies.get(pos, 0), roles.get(pos, 0)
            b = base.get(lane)
            if not b:
                continue
            score = b["kill_rate"]
            refs = []
            line = f"{LANE_KO[lane]}: 킬이 난 첫 갱 중 아군 킬 {pct(b['kill_rate'])}"
            refs.append(self.e(f"{LANE_KO[lane]} 킬이 난 첫 갱 중 갱 쪽이 킬을 낸 비율 전체 평균 {pct(b['kill_rate'])}, "
                               f"중앙 시점 {mmss(b['median_s'])} (n={b['ganks']})", b["ganks"]))
            if enemy:
                t = self.stats.gank_target(s, lane, "enemy", enemy)
                if t and t["ganks"] >= 3:
                    adj = shrink(t["kill_rate"] * t["ganks"], t["ganks"], b["kill_rate"], k=10)
                    score = adj
                    refs.append(self.e(f"적 {self.name(enemy)}({LANE_KO[lane]}) 상대로 킬이 난 첫 갱 중 갱 쪽 킬 {pct(t['kill_rate'])} "
                                       f"(n={t['ganks']})", t["ganks"]))
                    line += f", 적 {self.name(enemy)} 대상 {pct(t['kill_rate'])}"
            if ally and enemy:
                lm = self.stats.lane_matchup(s, pos, ally, enemy)
                if lm and lm["games"] >= 3:
                    refs.append(self.e(f"{POS_KO[pos]} {self.name(ally)} vs {self.name(enemy)}: 10분 골드 "
                                       f"{signed(lm['gd10'])}, 승률 {pct(lm['wins'] / lm['games'])} (n={lm['games']})",
                                       lm["games"]))
                    line += f", 라인전 10분 골드 {signed(lm['gd10'])}"
                    # 라인이 이기는 쪽에 갱 가면 굴리기 쉽고, 지는 라인은 커버가 필요
                    score += max(min(lm["gd10"] / 2000, 0.1), -0.1) * 0.5
            card.add(line, *refs)
            scores.append((score, lane, refs, bool(ally and enemy and len(refs) >= 3)))
        if scores:
            scores.sort(reverse=True)
            best = scores[0]
            n_best = min((ev.games or 0) for ev in self.ev.items if ev.id in best[2]) if best[2] else 0
            if n_best >= MIN_INFER and len(scores) >= 2 and best[0] - scores[1][0] >= 0.03:
                card.headline = f"우선 갱 대상: {LANE_KO[best[1]]}"
                basis = "킬 교환 비율과 라인전 우위를 함께 보면" if best[3] else "킬 교환 비율만 보면"
                card.add(f"갱이 킬로 이어졌을 때 우리 쪽이 이기는 비율 기준으로, {basis} "
                         f"{LANE_KO[best[1]]} 갱 기대값이 가장 높습니다.", *best[2], kind="inference")
            else:
                card.headline = "라인별 갱 기대값 차이가 크지 않음 → 상대 정글 반대편·라인 우선권 기준으로 판단"
        elif tot:
            card.headline = f"첫 갱 주로 {LANE_KO[fg[0]['lane']]}"
        else:
            card.headline = "데이터 부족"
        return card

    def card_matchup(self, s, champ, enemy_jg) -> Card | None:
        card = Card("matchup", "적 정글 매치업", "")
        if not enemy_jg:
            card.headline = "적 정글 미확정"
            card.add("적 정글러가 확정되면 1:1 구도와 시간대별 골드 차이를 보여줍니다.")
            return card
        m = self.stats.matchup(s, champ, enemy_jg)
        if not m:
            card.headline = f"vs {self.name(enemy_jg)}: 표본 없음"
            card.add(f"{self.scope.label}에서 {self.name(champ)} vs {self.name(enemy_jg)} 정글 맞대결 표본이 없습니다.")
            return card
        adj = shrink(m["wins"], m["games"], k=15)
        eid = self.e(f"{self.name(champ)} vs {self.name(enemy_jg)} 정글 승률 {pct(m['win_rate'])} (보정 {pct(adj)}), "
                     f"골드 차 5분 {signed(m['gd5'])} / 10분 {signed(m['gd10'])} / 15분 {signed(m['gd15'])} "
                     f"(n={m['games']})", m["games"])
        card.add(f"승률 {pct(m['win_rate'])} (보정 {pct(adj)}), 골드 차 5분 {signed(m['gd5'])}, "
                 f"10분 {signed(m['gd10'])}, 15분 {signed(m['gd15'])}", eid)
        e2 = self.e(f"이 매치업에서 내 10분 전 킬관여 {m['takedowns10']:.1f} / 데스 {m['deaths10']:.1f}, "
                    f"5분 전 정글·강가 교전 {m['jungle_fights5']:.2f}회, 상대 정글 몬스터 처치 {m['enemy_jungle_cs']:.1f} "
                    f"(n={m['games']})", m["games"])
        card.add(f"10분 전 킬관여 {m['takedowns10']:.1f} / 데스 {m['deaths10']:.1f}, "
                 f"5분 전 정글 교전 {m['jungle_fights5']:.2f}회, 카정 몬스터 {m['enemy_jungle_cs']:.1f}", e2)
        curve = [r for r in self.stats.matchup_curve(s, champ, enemy_jg) if r["minute"] >= 3]
        if len(curve) >= 5 and m["games"] >= 5:
            ahead = [r["minute"] for r in curve if r["gold_diff"] > 100]
            behind = [r["minute"] for r in curve if r["gold_diff"] < -100]
            desc = []
            if ahead:
                desc.append(f"{ahead[0]}~{ahead[-1]}분 골드 우위")
            if behind:
                desc.append(f"{behind[0]}~{behind[-1]}분 골드 열세")
            e3 = self.e(f"{self.name(champ)} vs {self.name(enemy_jg)} 분당 평균 골드 차: "
                        + ", ".join(f"{r['minute']}분 {signed(r['gold_diff'])}" for r in curve[::2])
                        + f" (n={m['games']})", m["games"])
            if desc:
                card.add("시간대: " + ", ".join(desc), e3)
        if m["games"] < MIN_INFER:
            card.add(f"표본이 {m['games']}경기라 매치업 판단은 보류합니다.", eid, kind="inference")
        elif m["gd5"] is not None and m["gd5"] < -150:
            card.add(f"초반(5분) 골드 열세 매치업입니다. 초반 1:1 교전과 카정 대응은 피하고 라인 우선권이 있는 쪽에서 "
                     f"움직이는 편이 안전합니다.", eid, kind="inference")
        elif m["gd5"] is not None and m["gd5"] > 150:
            card.add("초반(5분) 골드 우위 매치업입니다. 상대 동선을 예측해 카정·스커틀 경합으로 격차를 벌릴 수 있습니다.",
                     eid, kind="inference")
        verdict = ("표본 부족" if m["games"] < MIN_INFER else
                   "유리" if adj > 0.52 else "불리" if adj < 0.48 else "팽팽")
        card.headline = f"vs {self.name(enemy_jg)}: {verdict} (보정 승률 {pct(adj)}, n={m['games']})"
        return card

    def card_objectives(self, s, state, champ, roles) -> Card:
        card = Card("objectives", "오브젝트 운영", "")
        o = self.stats.objectives(s)
        if o:
            eid = self.e(f"첫 공허 유충 중앙 {mmss(o['first_grub_median_s'])}, 첫 드래곤 {mmss(o['first_dragon_median_s'])}, "
                         f"전령 {mmss(o['herald_median_s'])}, 첫 바론 {mmss(o['baron_median_s'])} (n={o['matches']}경기)",
                         o["matches"])
            card.add(f"오브젝트 시점 중앙값: 유충 {mmss(o['first_grub_median_s'])}, 드래곤 {mmss(o['first_dragon_median_s'])}, "
                     f"전령 {mmss(o['herald_median_s'])}, 바론 {mmss(o['baron_median_s'])}", eid)
        imp = self.stats.objective_impact(s)
        names = {"first_dragon": "첫 드래곤", "first_grub": "첫 유충", "grubs_majority": "유충 과반",
                 "herald": "전령", "first_baron": "첫 바론", "atakhan": "아타칸"}
        if imp:
            parts = [f"{names[k]} {pct(v['win_rate_when_taken'])}" for k, v in imp.items() if v["games"] >= 10]
            if parts:
                n = max(v["games"] for v in imp.values())
                eid = self.e("오브젝트 획득 팀 승률: " + ", ".join(parts) + f" (n≈{n})", n)
                card.add("획득 팀 승률: " + ", ".join(parts), eid)
        c = self.stats.champ(s, champ)
        if c:
            eid = self.e(f"{self.name(champ)} 팀 첫 드래곤 {pct(c['first_dragon_rate'])}, 첫 유충 {pct(c['first_grub_rate'])}, "
                         f"평균 유충 {c['grubs']:.1f}마리, 전령 {pct(c['herald_rate'])} (n={c['games']})", c["games"])
            card.add(f"{self.name(champ)} 팀 첫 드래곤 {pct(c['first_dragon_rate'])}, 첫 유충 {pct(c['first_grub_rate'])}, "
                     f"유충 평균 {c['grubs']:.1f}", eid)
        # 라인 우위로 오브젝트 방향 판단
        allies = self.ally_roles(state)
        side_score = {}
        refs = []
        for side, positions in (("top", ["TOP"]), ("bot", ["BOTTOM", "UTILITY"])):
            tot, any_ = 0.0, False
            for pos in positions:
                a, en = allies.get(pos), roles.get(pos)
                if a and en:
                    lm = self.stats.lane_matchup(s, pos, a, en)
                    if lm and lm["games"] >= 3:
                        tot += lm["gd10"]
                        any_ = True
                        refs.append(self.e(f"{POS_KO[pos]} {self.name(a)} vs {self.name(en)} 10분 골드 {signed(lm['gd10'])} "
                                           f"(n={lm['games']})", lm["games"]))
            if any_:
                side_score[side] = tot
        if len(side_score) == 2 and min((ev.games or 0) for ev in self.ev.items if ev.id in refs) >= MIN_INFER:
            if side_score["bot"] - side_score["top"] > 200:
                card.headline = "봇 라인 우위 예상 → 드래곤 쪽 운영 우선"
                card.add("10분 골드 기준 봇 듀오가 탑보다 유리합니다. 봇 우선권을 이용해 드래곤 타이밍에 맞춰 리셋하세요.",
                         *refs, kind="inference")
            elif side_score["top"] - side_score["bot"] > 200:
                card.headline = "탑 라인 우위 예상 → 유충·전령 쪽 운영 우선"
                card.add("10분 골드 기준 탑이 봇보다 유리합니다. 탑 우선권을 이용해 유충 타이밍에 맞춰 움직이세요.",
                         *refs, kind="inference")
        if not card.headline:
            card.headline = (f"유충 {mmss(o['first_grub_median_s'])} · 드래곤 {mmss(o['first_dragon_median_s'])} 타이밍 대비"
                             if o else "데이터 부족")
        return card

    def card_comp(self, s, state, champ, roles) -> Card:
        card = Card("comp", "팀 조합·승리 플랜", "")
        allies = [a.champion_id for a in state.allies if a.champion_id]
        enemies = [x.champion_id for x in state.enemies if x.champion_id]
        if len(allies) >= 3:
            prof, ap, front = self.damage_profile(allies)
            card.add(f"아군 피해 성향: {PROFILE_KO.get(prof, prof)} (AP 비중 {pct(ap)}), 앞라인 {front}명",
                     self.ev.add(f"아군 조합 피해 성향 AP {pct(ap)}, 탱커/앞라인 {front}명", "Data Dragon 챔피언 정보"))
        if len(enemies) >= 3:
            prof, ap, front = self.damage_profile(enemies)
            card.add(f"적 피해 성향: {PROFILE_KO.get(prof, prof)} (AP 비중 {pct(ap)}), 앞라인 {front}명",
                     self.ev.add(f"적 조합 피해 성향 AP {pct(ap)}, 탱커/앞라인 {front}명", "Data Dragon 챔피언 정보"))

        def scaling(ids: list[int]) -> tuple[float, int] | None:
            vals, n = [], 0
            for cid in ids:
                d = self.stats.duration(s, cid, "duration_all")
                early, late = d.get("<25"), d.get("35+")
                if early and late:
                    vals.append(shrink(late["wins"], late["games"], k=20) - shrink(early["wins"], early["games"], k=20))
                    n += early["games"] + late["games"]
            return (sum(vals) / len(vals), n) if vals else None

        if len(allies) >= 4 and len(enemies) >= 4:
            sa, se = scaling(allies), scaling(enemies)
            if sa and se and min(sa[1], se[1]) >= MIN_INFER * 4:
                eid = self.e(f"25분 전 대비 35분 후 승률 변화(팀 평균): 아군 {sa[0] * 100:+.1f}%p, 적 {se[0] * 100:+.1f}%p",
                             min(sa[1], se[1]))
                card.add(f"후반 성향(35분+ 승률 − 25분 전 승률): 아군 {sa[0] * 100:+.1f}%p / 적 {se[0] * 100:+.1f}%p", eid)
                if sa[0] - se[0] > 0.04:
                    card.headline = "우리 팀이 후반형 → 초반 손해 최소화, 오브젝트 스택으로 시간 끌기"
                    card.add("아군이 후반으로 갈수록 유리합니다. 초반 무리한 교전보다 시야·오브젝트 교환으로 성장 시간을 버세요.",
                             eid, kind="inference")
                elif se[0] - sa[0] > 0.04:
                    card.headline = "적 팀이 후반형 → 25분 전 굴려서 마무리"
                    card.add("적이 후반으로 갈수록 유리합니다. 초반 갱·오브젝트로 격차를 만들고 25분 전후에 끝내는 운영이 필요합니다.",
                             eid, kind="inference")
                else:
                    card.headline = "양 팀 성장 곡선 비슷 → 오브젝트 한타 위주"
        d = self.stats.duration(s, champ)
        if d:
            parts = [f"{k} {pct(v['wins'] / v['games'])}(n={v['games']})" for k, v in sorted(d.items(), key=lambda kv: DUR_ORDER.index(kv[0]))]
            card.add(f"{self.name(champ)} 게임 시간별 승률: " + ", ".join(parts),
                     self.e(f"{self.name(champ)} 정글 게임 시간별 승률: " + ", ".join(parts), sum(v["games"] for v in d.values())))
        if not card.headline:
            card.headline = "조합 확정 후 갱신"
        return card

    def card_insights(self, champ: int, enemy_jg: int) -> Card:
        card = Card("insights", "프로·전문가 인사이트", "")
        info = self.stats.pro_info()
        pro = self.stats.pro_champ(champ)
        period = ""
        if info and info.get("since"):
            period = f"{str(info['since'])[:10]}~{str(info['until'])[:10]}"
        if pro:
            eid = self.ev.add(
                f"프로 대회({period}) {self.name(champ)} 정글 {pro['games']}경기, 승률 {pct(pro['wins'] / pro['games'])}, "
                f"평균 경기 {pro['minutes']:.1f}분, 팀 유충 {pro['grubs']:.1f} / 드래곤 {pro['dragons']:.1f} / 전령 "
                f"{pro['heralds']:.1f}, 선수 {pro['players']}명, 리그: {pro['leagues']}", SRC_PRO, pro["games"],
                confidence(pro["games"]))
            card.add(f"프로 대회 {pro['games']}경기 승률 {pct(pro['wins'] / pro['games'])}, 팀 평균 유충 {pro['grubs']:.1f} · "
                     f"드래곤 {pro['dragons']:.1f}", eid)
            card.headline = f"프로 대회 {pro['games']}경기 · 승률 {pct(pro['wins'] / pro['games'])}"
        elif info:
            card.add(f"최근 프로 대회({period})에서 {self.name(champ)} 정글 기록이 없습니다.",
                     self.ev.add(f"프로 대회 정글 기록 {info['games']}경기 중 {self.name(champ)} 없음", SRC_PRO))
        if enemy_jg:
            pm = self.stats.pro_matchup(champ, enemy_jg)
            if pm:
                eid = self.ev.add(f"프로 대회 {self.name(champ)} vs {self.name(enemy_jg)} 정글 {pm['games']}경기, "
                                  f"승률 {pct(pm['wins'] / pm['games'])}", SRC_PRO, pm["games"], confidence(pm["games"]))
                card.add(f"프로 대회 vs {self.name(enemy_jg)}: {pm['games']}경기 {pct(pm['wins'] / pm['games'])}", eid)
        for g in self.guides(champ, enemy_jg):
            eid = self.ev.add(f"“{g['quote']}” — {g['title']}{' · ' + g['author'] if g['author'] else ''}",
                              f"가이드: {g['title']}", url=g["url"])
            topic = TOPIC_KO.get(g["topic"], g["topic"])
            card.add(f"[{topic}] {g['text']}", eid, kind="guide")
        if not card.headline:
            n = sum(1 for i in card.items if i.kind == "guide")
            card.headline = f"전문가 가이드 {n}개" if n else "프로·가이드 데이터 없음 (loldosa pro sync / guides add)"
        return card

    def guides(self, champ: int, enemy_jg: int, limit: int = 6) -> list[dict]:
        if not self.guides_path or not self.guides_path.exists():
            return []
        import duckdb

        con = duckdb.connect(str(self.guides_path), read_only=True)
        try:
            cur = con.execute("""
                SELECT c.topic, c.text, c.quote, c.url, s.title, s.author,
                       (c.vs_champion_id = ? AND c.vs_champion_id > 0)::INT AS vs_hit
                FROM guide_claims c JOIN guide_sources s USING (source_id)
                WHERE c.champion_id = ? OR (c.vs_champion_id = ? AND c.vs_champion_id > 0)
                ORDER BY vs_hit DESC, c.extracted_at DESC LIMIT ?""", [enemy_jg, champ, enemy_jg, limit])
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
        finally:
            con.close()


SRC_PRO = "Leaguepedia 프로 대회 기록"


CLEAR_KO = {"full_clear": "6캠프(풀클리어)", "partial": "4~5캠프", "three_or_less": "3캠프 이하"}

PROFILE_KO = {"ad_heavy": "AD 위주", "ap_heavy": "AP 위주", "balanced": "AD/AP 균형", "unknown": "알 수 없음"}
DUR_ORDER = ["<25", "25-30", "30-35", "35+"]
