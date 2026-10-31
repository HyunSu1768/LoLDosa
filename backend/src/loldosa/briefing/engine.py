"""챔피언 선택 상태 + 통계 DB → 브리핑.

모든 문장은 근거(Evidence)를 참조한다. kind="inference" 인 항목은 근거에서 규칙으로
도출한 판단이며, 어떤 근거에서 나왔는지 evidence 목록으로 남긴다.
"""

from __future__ import annotations

import itertools
import math

from ..analysis.build import AD_CUT, AP_CUT
from ..analysis.geometry import CAMP_KO, map_side, team_camps
from ..analysis.query import Scope, StatsDB, confidence, logit, shrink, sigmoid
from ..ddragon import ChampionIndex
from ..lcu.champselect import ChampSelectState, Stage
from ..sources.guides import TOPIC_KO
from .models import Briefing, Card, EvidenceLog, Item, PlanLine, Recommendation

SRC_TIMELINE = "Riot Match-V5 타임라인"
LANE_KO = {"top": "탑", "mid": "미드", "bot": "봇"}
POS_KO = {"TOP": "탑", "JUNGLE": "정글", "MIDDLE": "미드", "BOTTOM": "원딜", "UTILITY": "서폿"}
LCU_POS = {"top": "TOP", "jungle": "JUNGLE", "middle": "MIDDLE", "bottom": "BOTTOM", "utility": "UTILITY"}
LANE_POS = {"top": "TOP", "mid": "MIDDLE", "bot": "BOTTOM"}
REGION_KO = {"own_jungle": "우리 정글", "enemy_jungle": "상대 정글", "river": "강가", "top": "탑 라인",
             "mid": "미드 라인", "bot": "봇 라인", "base": "본진(귀환·사망)", "unknown": "알 수 없음"}
ROLE_ORDER = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]


def pct(x: float | None) -> str:
    return "-" if x is None else f"{x * 100:.0f}%"


def mmss(sec: float | None) -> str:
    if sec is None:
        return "-"
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def josa(word: str, pair: str = "은는") -> str:
    """받침 유무에 따라 은/는, 이/가, 과/와, 을/를, 으로/로 선택."""
    ch = word[-1] if word else ""
    final = (ord(ch) - 0xAC00) % 28 if "가" <= ch <= "힣" else 0
    if pair == "으로":
        return word + ("으로" if final and final != 8 else "로")  # ㄹ 받침은 '로'
    return word + (pair[0] if final else pair[1])


MIN_INFER = 15  # 판단(inference)을 내리기 위한 최소 표본 수


def signed(x: float | None, unit: str = "") -> str:
    return "-" if x is None else f"{x:+.0f}{unit}"


class BriefingEngine:
    def __init__(self, stats: StatsDB, champs: ChampionIndex, guides_path=None, settings=None) -> None:
        self.stats = stats
        self.champs = champs
        self.guides_path = guides_path
        self.settings = settings  # UserSettings (챔프폭, 내 티어 버킷)

    @property
    def pool(self) -> set[int]:
        return set(self.settings.champion_pool) if self.settings else set()

    @property
    def my_bucket(self) -> str:
        return self.settings.my_bucket if self.settings else "platinum"

    def name(self, cid: int) -> str:
        return self.champs.name(cid)

    def key(self, cid: int) -> str:
        c = self.champs.get(cid)
        return c.key if c else ""

    # ------------------------------------------------------------------ entry

    def build(self, state: ChampSelectState) -> Briefing:
        b = Briefing(stage=state.stage.value)
        if not self.stats.available:
            b.notes.append("통계 DB가 없어요. `loldosa update`로 수집·분석을 먼저 실행하세요.")
            return b
        with self.stats.session():
            return self._build(state, b)

    def _build(self, state: ChampSelectState, b: Briefing) -> Briefing:
        s = self.stats.pick_scope("apex")
        self.scope = s
        self.ev = EvidenceLog()
        self.facts: dict = {}
        b.scope_label = s.label
        if state.me and not state.is_jungle and state.my_position:
            b.notes.append(f"이번 판 포지션이 정글이 아니에요({state.my_position}). 정글 정보만 보여드려요.")

        roles = self.infer_enemy_roles(s, state)
        enemy_jg = roles.get("JUNGLE", 0)
        me = state.me
        my_champ = (me.champion_id or me.intent_id) if me else 0

        if state.stage in (Stage.PLANNING, Stage.BANNING, Stage.PRE_MY_PICK):
            b.picks, b.picks_outside = self.recommend_picks(s, state, enemy_jg)
            if state.stage in (Stage.PLANNING, Stage.BANNING):
                b.bans = self.recommend_bans(s, state, my_champ)

        if my_champ:
            b.my_champion, b.my_champion_name = my_champ, self.name(my_champ)
            if enemy_jg:
                b.enemy_jungler, b.enemy_jungler_name = enemy_jg, self.name(enemy_jg)
            if me and not me.locked:
                b.notes.append(f"{self.name(my_champ)}: 아직 픽 확정 전이라 미리보기예요.")
            b.cards = [
                self.card_route(s, state, my_champ, enemy_jg),
                self.card_ganks(s, state, my_champ, enemy_jg, roles),
                self.card_matchup(s, my_champ, enemy_jg),
                self.card_objectives(s, state, my_champ, roles),
                self.card_comp(s, state, my_champ, roles),
                self.card_insights(my_champ, enemy_jg),
            ]
            b.cards = [c for c in b.cards if c and c.items]
            b.plan = self.build_plan(my_champ, enemy_jg)
            b.paths = self.paths_for(state, my_champ, enemy_jg)
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
        """실제 경기 피해 데이터 기반 (표본 적은 챔피언은 Data Dragon 수치)."""
        prof = self.stats.profiles(champ_ids)
        meta = [prof[c] for c in champ_ids if c in prof and prof[c]["ap_share"] is not None]
        if not meta:
            return "unknown", 0.5, 0
        ap = sum(m["ap_share"] for m in meta) / len(meta)
        front = sum(bool(m["frontline"]) for m in meta)
        prof = "ad_heavy" if ap < AD_CUT else "ap_heavy" if ap > AP_CUT else "balanced"
        return prof, ap, front

    # ------------------------------------------------------------ picks / bans

    def recommend_picks(self, s: Scope, state: ChampSelectState, enemy_jg: int,
                        n: int = 5) -> tuple[list[Recommendation], list[Recommendation]]:
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
        pool = self.pool
        if pool:
            chosen = [t for t in scored if t[1] in pool][:n]
            best_in = chosen[0][0] if chosen else 0
            # 챔프폭 밖인데 확실히 더 나은 것만 참고로 (예상 승률 +2%p 이상)
            outside = [t for t in scored if t[1] not in pool and t[0] >= best_in + 0.02][:2]
        else:
            chosen, outside = scored[:n], []
        return self._recs(chosen), self._recs(outside)

    def _recs(self, scored: list) -> list[Recommendation]:
        out = []
        for score, cid, parts in scored:
            rec = Recommendation(cid, self.name(cid), score, self.key(cid), in_pool=cid in self.pool)
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
                rec.reasons.append(Item(f"프로 대회 {pro['games']}경기 승률 {pct(pro['wins'] / pro['games'])} (참고용, 추천 점수엔 안 넣음)",
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
                                      [Item(f"주의할 메타 챔피언: {text}", "fact", [eid])]))
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
        eid = self.e(f"{self.name(champ)} {'블루' if team == 100 else '레드'} 진영 시작 캠프(1:00 위치에서 가장 가까운 캠프, "
                     f"두 캠프 사이 위치는 제외): "
                     f"{text} (n={tot})", tot)
        return text, eid, side_share

    def card_route(self, s, state, champ, enemy_jg) -> Card:
        team = state.my_team_id
        card = Card("route", "시작·초반 정글링", "")
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
            e2 = self.e(f"{self.name(champ)} 3:00까지 먹은 캠프 수(정글 CS ÷ 4, 바위게는 2:55에 나와서 대부분 캠프 몫): {parts} (n={tot})", tot)
            card.add(f"3:00까지 먹은 캠프: {parts}", e2)

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
                    e3 = self.e(f"{self.name(champ)} {CLEAR_KO[kind]} 판의 3:00 위치: {text} (n={n})", n)
                    card.add(f"{CLEAR_KO[kind]}인 판의 3:00 위치: {text}", e3)

            fr = self.stats.first_recall(s, champ)
            if fr and fr["games"] >= 5:
                e4 = self.e(f"{self.name(champ)} 첫 귀환 시각(중앙값, 죽어서 귀환한 건 제외) {mmss(fr['median_s'])}, "
                            f"25~75%: {mmss(fr['p25_s'])}~{mmss(fr['p75_s'])} (n={fr['games']})", fr["games"])
                card.add(f"첫 귀환: 중앙값 {mmss(fr['median_s'])} (보통 {mmss(fr['p25_s'])}~{mmss(fr['p75_s'])})", e4)
            main_kind, main_share = max(share.items(), key=lambda kv: kv[1])
            starts = self.stats.start_camps(s, champ, team)
            st_tot = sum(r["games"] for r in starts)
            self.facts["start"] = {
                "camp": CAMP_KO[starts[0]["start_camp"]] if starts else None,
                "camp_share": starts[0]["games"] / st_tot if starts else 0,
                "camp_eid": eid, "clear": main_kind, "share": share, "eid": e2, "n": tot}
            if tot >= MIN_INFER:
                if main_kind == "full_clear" and main_share >= 0.5:
                    card.headline = f"{self.name(champ)}: 주로 풀캠 (3:00까지 6캠프 {pct(main_share)})"
                    card.add(f"고티어 {josa(self.name(champ))} 대부분 3분 안에 풀캠을 하고, 그 뒤 바위게(2:55 등장)나 "
                             f"라인으로 가요.", e2, kind="inference")
                elif share["three_or_less"] >= 0.35:
                    card.headline = f"{self.name(champ)}: 3캠만 먹고 일찍 갱 가는 판이 많음 ({pct(share['three_or_less'])})"
                    card.add(f"고티어 {josa(self.name(champ))} 3캠만 먹고 갱이나 카정을 가는 판이 많아요.",
                             e2, kind="inference")
                else:
                    card.headline = f"{self.name(champ)}: 풀캠·3캠 갱 섞어서 씀 (풀캠 {pct(share['full_clear'])})"
            else:
                card.headline = f"{self.name(champ)}: 초반 정글링 데이터 부족 (n={tot})"
        if enemy_jg:
            et, eeid, _ = self._start_line(s, enemy_jg, state.enemy_team_id)
            if et:
                card.add(f"상대 {self.name(enemy_jg)} 예상 시작 캠프: {et}", eeid)
            sides = self.stats.sides(s, enemy_jg, state.enemy_team_id)
            for col, when in (("side3", "3:00"), ("side4", "4:00")):
                d = sides[col]
                n = sum(d.values())
                if not n:
                    continue
                top = d.get("top", 0) / n
                eid = self.e(f"적 {self.name(enemy_jg)}({'블루' if state.enemy_team_id == 100 else '레드'}) {when} 위치: "
                             f"탑 사이드 {pct(top)} / 봇 사이드 {pct(1 - top)} (n={n})", n)
                card.add(f"상대 {self.name(enemy_jg)} {when} 위치: 탑 사이드 {pct(top)} / 봇 사이드 {pct(1 - top)}", eid)
                if n >= MIN_INFER and max(top, 1 - top) >= 0.65:
                    side = "탑" if top >= 0.5 else "봇"
                    card.add(f"{when} 전후 상대 정글은 {side} 사이드에 있을 확률이 높아요({pct(max(top, 1 - top))}). "
                             f"그 시간 {side} 사이드 라인은 상대 갱과 바위게 싸움을 조심하세요.", eid, kind="inference")
                    if col == "side3":
                        card.headline += f" · 상대 {self.name(enemy_jg)} 3:00 {side} 사이드 {pct(max(top, 1 - top))}"
                        self.facts["enemy_side3"] = {"side": side, "share": max(top, 1 - top), "eid": eid}
            trans = self.stats.side_transition(s)
            for start in ("top", "bot"):
                rows = [r for r in trans if r["start_side"] == start]
                n = sum(r["games"] for r in rows)
                if n >= MIN_INFER:
                    opp3 = sum(r["games"] for r in rows if r["side3"] != start) / n
                    same4 = sum(r["games"] for r in rows if r["side4"] == start) / n
                    eid = self.e(f"고티어 정글러가 {LANE_SIDE_KO[start]} 사이드에서 시작하면 3:00에 반대 사이드 {pct(opp3)}, "
                                 f"4:00에 시작 사이드 {pct(same4)} (n={n})", n)
                    card.add(f"게임 중 상대 정글 시작 위치가 보이면: {LANE_SIDE_KO[start]} 사이드 시작 → 3:00 반대편 {pct(opp3)}, "
                             f"4:00 다시 {LANE_SIDE_KO[start]} 사이드 {pct(same4)}", eid)
        if not card.headline:
            card.headline = "데이터 부족"
        return card

    def card_ganks(self, s, state, champ, enemy_jg, roles) -> Card:
        card = Card("ganks", "갱 타이밍·갈 라인", "")
        fg = self.stats.first_ganks(s, champ)
        tot = sum(r["games"] for r in fg)
        if tot:
            parts = ", ".join(f"{LANE_KO[r['lane']]} {pct(r['games'] / tot)}" for r in fg)
            med = sorted(fg, key=lambda r: -r["games"])[0]
            eid = self.e(f"{self.name(champ)} 8분 이전 라인에서 처음 킬이 난 위치: {parts}; 가장 많은 {LANE_KO[med['lane']]} "
                         f"보통 시각(중앙값) {mmss(med['median_s'])} (n={tot}, 킬 없이 끝난 갱 시도는 기록에 없음. "
                         f"어느 라인이 좋은지가 아니라 고티어가 실제로 어디서 첫 킬을 냈는지의 분포)", tot)
            card.add(f"첫 킬이 난 라인 분포(참고): {parts}, 가장 흔한 {josa(LANE_KO[med['lane']])} 보통 "
                     f"{mmss(med['median_s'])}쯤", eid)
        curve = {r["minute"]: r for r in self.stats.curve(s, champ)}
        if 3 in curve:
            eid = self.e(f"{self.name(champ)} 평균 레벨: 3분 {curve[3]['level']:.1f}, "
                         f"6분 {curve.get(6, curve[3])['level']:.1f} (n={curve[3]['games']})", curve[3]["games"])
            card.add(f"평균 레벨 3분 {curve[3]['level']:.1f} / 6분 {curve.get(6, curve[3])['level']:.1f}", eid)

        if tot:
            self.facts["gank_time"] = {"lane": med["lane"], "median_s": med["median_s"], "eid": eid}

        # 갱 반응은 티어마다 달라서, 내 티어대(기본 플래티넘) 표본이 충분하면 그걸 우선 쓴다
        mine = Scope(s.scope, self.my_bucket)
        if not self.stats.has_rows("gank_exposure", mine):
            mine = Scope("ALL", self.my_bucket)
        bases = {"mine": self.stats.gank_exposure_base(mine), "apex": self.stats.gank_exposure_base(s)}

        def exposure(pos: str, champ_id: int):
            x = self.stats.gank_exposure(mine, pos, champ_id) if bases["mine"] else None
            if x and x["games"] >= MIN_INFER:
                return x, bases["mine"].get(pos), mine
            x = self.stats.gank_exposure(s, pos, champ_id)
            return x, bases["apex"].get(pos), s

        allies = self.ally_roles(state)
        scores = []
        for lane, positions in (("top", ["TOP"]), ("mid", ["MIDDLE"]), ("bot", ["BOTTOM", "UTILITY"])):
            parts, refs, comp, why, n_min = [], [], [], [], 10**9
            for pos in positions:
                enemy, ally = roles.get(pos, 0), allies.get(pos, 0)
                if enemy:
                    x, b, sc = exposure(pos, enemy)
                    if x and b and x["games"] >= 5:
                        v = shrink(x["died_to_jg"] * x["games"], x["games"], b["died_to_jg"], k=20)
                        comp.append(v - b["died_to_jg"])
                        n_min = min(n_min, x["games"])
                        refs.append(self.e(f"적 {self.name(enemy)}({POS_KO[pos]}): 8분 전 상대 정글이 낀 킬에 죽은 판 "
                                           f"{pct(x['died_to_jg'])}, {POS_KO[pos]} 평균 {pct(b['died_to_jg'])} "
                                           f"(n={x['games']})", x["games"], sc))
                        parts.append(f"적 {josa(self.name(enemy))} 갱에 죽는 판 {pct(x['died_to_jg'])} (평균 {pct(b['died_to_jg'])})")
                        if v - b["died_to_jg"] >= 0.04:
                            why.append(f"적 {josa(self.name(enemy), '이가')} 정글 갱에 잘 죽음")
                if ally:
                    x, b, sc = exposure(pos, ally)
                    if x and b and x["games"] >= 5:
                        v = shrink(x["kill_with_jg"] * x["games"], x["games"], b["kill_with_jg"], k=20)
                        comp.append(v - b["kill_with_jg"])
                        n_min = min(n_min, x["games"])
                        refs.append(self.e(f"아군 {self.name(ally)}({POS_KO[pos]}): 8분 전 아군 정글과 함께 킬을 낸 판 "
                                           f"{pct(x['kill_with_jg'])}, {POS_KO[pos]} 평균 {pct(b['kill_with_jg'])} "
                                           f"(n={x['games']})", x["games"], sc))
                        parts.append(f"아군 {josa(self.name(ally))} 정글과 킬 내는 판 {pct(x['kill_with_jg'])} "
                                     f"(평균 {pct(b['kill_with_jg'])})")
                        if v - b["kill_with_jg"] >= 0.04:
                            why.append(f"아군 {josa(self.name(ally), '이가')} 갱 호응이 좋음")
                if ally and enemy:
                    lm = self.stats.lane_matchup(s, pos, ally, enemy)
                    if lm and lm["games"] >= 3:
                        refs.append(self.e(f"{POS_KO[pos]} {self.name(ally)} vs {self.name(enemy)}: 10분 골드 "
                                           f"{signed(lm['gd10'])}, 승률 {pct(lm['wins'] / lm['games'])} (n={lm['games']})",
                                           lm["games"]))
                        parts.append(f"라인전 10분 골드 {signed(lm['gd10'])}")
            if parts:
                card.add(f"{LANE_KO[lane]} — " + ", ".join(parts), *refs)
            if comp:
                scores.append((sum(comp) / len(comp), lane, refs, n_min, why))
        if len(scores) >= 2:
            scores.sort(key=lambda t: -t[0])
            best, second = scores[0], scores[1]
            if best[3] >= MIN_INFER and best[0] - second[0] >= 0.05:
                card.headline = f"먼저 갱 갈 곳: {LANE_KO[best[1]]}" + (f" ({', '.join(best[4][:2])})" if best[4] else "")
                card.add(f"{LANE_KO[best[1]]} 갱 성공률이 다른 라인보다 평균 대비 {best[0] * 100:.0f}%p 높아요.",
                         *best[2], kind="inference")
                self.facts["gank_lane"] = {"lane": best[1], "why": best[4], "eids": best[2]}
            else:
                card.headline = "라인별 갱 성공률 차이 작음 → 라인 주도권 있는 쪽으로"
        if not card.headline:
            card.headline = (f"첫 갱 주로 {LANE_KO[fg[0]['lane']]}" if tot else "상대 라이너가 정해지면 갱 갈 곳을 알려드려요")
        return card

    def _duel_line(self, s, champ, enemy=None) -> tuple[str, str, int] | None:
        d = self.stats.duels(s, champ, enemy)
        n = sum(r["fights"] for r in d.values())
        if n < 5:
            return None
        parts = [f"{BAND_KO[band]} {pct(d[band]['won'] / d[band]['fights'])}({d[band]['fights']}회)"
                 for band in ("1-3", "4-5", "6+") if band in d]
        who = f"vs {self.name(enemy)}" if enemy else "모든 상대 정글"
        eid = self.e(f"{self.name(champ)} {who}: 15분 전 정글러끼리 킬 교환에서 이긴 비율, 내 레벨별 "
                     + ", ".join(parts) + f" (총 {n}회)", n)
        return ", ".join(parts), eid, n

    def card_matchup(self, s, champ, enemy_jg) -> Card | None:
        card = Card("matchup", "상대 정글 상성", "")
        general = self._duel_line(s, champ)
        if general:
            card.add(f"{self.name(champ)} 정글 1:1 승률(레벨별, 모든 상대): {general[0]}", general[1])
            d = self.stats.duels(s, champ)
            weak = [b for b in ("1-3", "4-5", "6+") if b in d and d[b]["fights"] >= MIN_INFER
                    and d[b]["won"] / d[b]["fights"] < 0.45]
            strong = [b for b in ("1-3", "4-5", "6+") if b in d and d[b]["fights"] >= MIN_INFER
                      and d[b]["won"] / d[b]["fights"] > 0.55]
            self.facts["duel"] = {"weak": weak, "strong": strong, "eid": general[1]}
        if not enemy_jg:
            card.headline = "상대 정글 아직 모름"
            card.add("상대 정글이 정해지면 1:1 상성과 시간대별 골드 차이를 보여줘요.")
            return card
        m = self.stats.matchup(s, champ, enemy_jg)
        if not m:
            card.headline = f"vs {self.name(enemy_jg)}: 기록 없음"
            card.add(f"{self.scope.label}에서 {self.name(champ)} vs {self.name(enemy_jg)} 정글 기록이 아직 없어요.")
            return card
        adj = shrink(m["wins"], m["games"], k=15)
        vs = self._duel_line(s, champ, enemy_jg)
        if vs:
            card.add(f"vs {self.name(enemy_jg)} 1:1 승률(레벨별): {vs[0]}", vs[1])
        eid = self.e(f"{self.name(champ)} vs {self.name(enemy_jg)} 정글 승률 {pct(m['win_rate'])} (보정 {pct(adj)}), "
                     f"골드 차 5분 {signed(m['gd5'])} / 10분 {signed(m['gd10'])} / 15분 {signed(m['gd15'])} "
                     f"(n={m['games']})", m["games"])
        card.add(f"승률 {pct(m['win_rate'])} (보정 {pct(adj)}), 골드 차 5분 {signed(m['gd5'])}, "
                 f"10분 {signed(m['gd10'])}, 15분 {signed(m['gd15'])}", eid)
        e2 = self.e(f"이 상성에서 내 10분 전 킬관여 {m['takedowns10']:.1f} / 데스 {m['deaths10']:.1f}, "
                    f"5분 전 정글·강가 교전 {m['jungle_fights5']:.2f}회, 게임 전체 상대 정글 몬스터 처치 {m['enemy_jungle_cs']:.1f} "
                    f"(n={m['games']})", m["games"])
        card.add(f"10분 전 킬관여 {m['takedowns10']:.1f} / 데스 {m['deaths10']:.1f}, "
                 f"5분 전 정글 싸움 {m['jungle_fights5']:.2f}회, 게임 전체 카정한 몬스터 {m['enemy_jungle_cs']:.1f}", e2)
        curve = [r for r in self.stats.matchup_curve(s, champ, enemy_jg) if r["minute"] >= 3]
        if len(curve) >= 5 and m["games"] >= 5:
            ahead = [r["minute"] for r in curve if r["gold_diff"] > 100]
            behind = [r["minute"] for r in curve if r["gold_diff"] < -100]
            desc = []
            if ahead:
                desc.append(f"{ahead[0]}~{ahead[-1]}분 골드 앞섬")
            if behind:
                desc.append(f"{behind[0]}~{behind[-1]}분 골드 밀림")
            e3 = self.e(f"{self.name(champ)} vs {self.name(enemy_jg)} 분당 평균 골드 차: "
                        + ", ".join(f"{r['minute']}분 {signed(r['gold_diff'])}" for r in curve[::2])
                        + f" (n={m['games']})", m["games"])
            if desc:
                card.add("시간대: " + ", ".join(desc), e3)
        if m["games"] < MIN_INFER:
            card.add(f"아직 {m['games']}판뿐이라 이 상성은 판단하기 어려워요.", eid, kind="inference")
        elif m["gd5"] is not None and m["gd5"] < -150:
            card.add(f"이 상성은 5분에 정글 골드가 평균 {abs(m['gd5']):.0f} 밀려요. 초반 정글 1:1은 불리한 편이니 "
                     f"라인 주도권 있는 쪽으로 움직이세요.", eid, kind="inference")
        elif m["gd5"] is not None and m["gd5"] > 150:
            card.add(f"이 상성은 5분에 정글 골드가 평균 {m['gd5']:.0f} 앞서요. 초반 정글 싸움과 바위게 싸움에서 유리해요.",
                     eid, kind="inference")
        if m["games"] >= MIN_INFER and m["gd5"] is not None:
            self.facts["matchup"] = {"gd5": m["gd5"], "adj": adj, "eid": eid}
        verdict = ("판 수 부족" if m["games"] < MIN_INFER else
                   "유리" if adj > 0.52 else "불리" if adj < 0.48 else "팽팽")
        card.headline = f"vs {self.name(enemy_jg)}: {verdict} (보정 승률 {pct(adj)}, n={m['games']})"
        return card

    def card_objectives(self, s, state, champ, roles) -> Card:
        card = Card("objectives", "오브젝트 운영", "")
        o = self.stats.objectives(s)
        if o:
            eid = self.e(f"첫 유충(중앙값) {mmss(o['first_grub_median_s'])}, 첫 드래곤 {mmss(o['first_dragon_median_s'])}, "
                         f"전령 {mmss(o['herald_median_s'])}, 첫 바론 {mmss(o['baron_median_s'])} (n={o['matches']}경기)",
                         o["matches"])
            card.add(f"오브젝트 처치 시각(중앙값): 유충 {mmss(o['first_grub_median_s'])}, 드래곤 {mmss(o['first_dragon_median_s'])}, "
                     f"전령 {mmss(o['herald_median_s'])}, 바론 {mmss(o['baron_median_s'])}", eid)
            self.facts["obj_times"] = {"grub": o["first_grub_median_s"], "dragon": o["first_dragon_median_s"], "eid": eid}
        imp = self.stats.objective_impact(s)
        names = {"first_dragon": "첫 드래곤", "first_grub": "첫 유충", "grubs_majority": "유충 2마리 이상",
                 "herald": "전령", "first_baron": "첫 바론", "atakhan": "아타칸"}
        if imp:
            parts = [f"{names[k]} {pct(v['win_rate_when_taken'])}" for k, v in imp.items() if v["games"] >= 10]
            if parts:
                n = max(v["games"] for v in imp.values())
                eid = self.e("오브젝트 먹은 팀 승률: " + ", ".join(parts) + f" (n≈{n})", n)
                card.add("먹은 팀 승률: " + ", ".join(parts), eid)
        self._turn_facts(s, o)
        for obj, tf in self.facts.get("turns", {}).items():
            card.add(f"{OBJ_TURN_KO[obj]} 귀환 타이밍별 획득률: 미리 귀환 {pct(tf['rate']['prep'])} / 안 함 {pct(tf['rate']['none'])} / "
                     f"직전 30초 안에 귀환 {pct(tf['rate']['late'])}", tf["eid"])
            if tf["useful"]:
                card.add(f"{josa(OBJ_TURN_KO[obj], '이가')} 잡히기 직전 30초 안에 귀환하면 거의 내줘요. "
                         f"귀환이 필요하면 0:40~2:30 전에 끝내 두세요. (미리 귀환 자체의 효과는 프로 경기 검증에서 뚜렷하지 않았어요)",
                         tf["eid"], kind="inference")
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
                card.headline = "봇 라인전 유리 예상 → 드래곤 쪽 위주로 운영"
                self.facts["obj_side"] = {"side": "dragon", "eids": refs}
                card.add("10분 골드 기준 봇 듀오가 탑보다 유리해요. 봇 주도권을 살려서 드래곤 나오기 전에 귀환해서 정비하세요.",
                         *refs, kind="inference")
            elif side_score["top"] - side_score["bot"] > 200:
                card.headline = "탑 라인전 유리 예상 → 유충·전령 쪽 위주로 운영"
                self.facts["obj_side"] = {"side": "grub", "eids": refs}
                card.add("10분 골드 기준 탑이 봇보다 유리해요. 탑 주도권을 살려서 유충 나오는 시간에 맞춰 움직이세요.",
                         *refs, kind="inference")
        if not card.headline:
            card.headline = (f"유충 {mmss(o['first_grub_median_s'])} · 드래곤 {mmss(o['first_dragon_median_s'])} 시간 맞춰 준비"
                             if o else "데이터 부족")
        return card

    def card_comp(self, s, state, champ, roles) -> Card:
        card = Card("comp", "팀 조합·승리 플랜", "")
        allies = [a.champion_id for a in state.allies if a.champion_id]
        enemies = [x.champion_id for x in state.enemies if x.champion_id]
        if len(allies) >= 3:
            prof, ap, front = self.damage_profile(allies)
            card.add(f"우리 팀 딜 구성: {PROFILE_KO.get(prof, prof)} (AP 비중 {pct(ap)}), 앞라인 {front}명",
                     self.ev.add(f"우리 팀 딜 구성: 챔피언별 실제 AP 딜 비중 평균 {pct(ap)}, 맞아 주는 챔피언(앞라인) {front}명",
                                 SRC_PROFILE))
        if len(enemies) >= 3:
            prof, ap, front = self.damage_profile(enemies)
            card.add(f"상대 팀 딜 구성: {PROFILE_KO.get(prof, prof)} (AP 비중 {pct(ap)}), 앞라인 {front}명",
                     self.ev.add(f"상대 팀 딜 구성: 챔피언별 실제 AP 딜 비중 평균 {pct(ap)}, 맞아 주는 챔피언(앞라인) {front}명",
                                 SRC_PROFILE))

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
                card.add(f"후반 힘(35분+ 승률 − 25분 전 승률): 아군 {sa[0] * 100:+.1f}%p / 적 {se[0] * 100:+.1f}%p", eid)
                if sa[0] - se[0] > 0.04:
                    card.headline = "우리가 후반 조합 → 초반 손해 줄이고 오브젝트 맞교환하며 버티기"
                    self.facts["scaling"] = {"who": "ally", "eid": eid}
                    card.add("우리 팀이 후반 조합이에요. 초반엔 무리하게 싸우지 말고 시야 잡고 오브젝트 맞교환하며 버티세요.",
                             eid, kind="inference")
                elif se[0] - sa[0] > 0.04:
                    card.headline = "적 팀이 후반형 → 25분 전 굴려서 마무리"
                    self.facts["scaling"] = {"who": "enemy", "eid": eid}
                    card.add("상대가 후반 조합이에요. 초반 갱과 오브젝트로 차이를 벌리고 25분 전후에 끝내세요.",
                             eid, kind="inference")
                else:
                    card.headline = "양 팀 후반 힘 차이 작음 (4%p 미만)"
        d = self.stats.duration(s, champ)
        if d:
            parts = [f"{k} {pct(v['wins'] / v['games'])}(n={v['games']})" for k, v in sorted(d.items(), key=lambda kv: DUR_ORDER.index(kv[0]))]
            card.add(f"{self.name(champ)} 게임 시간별 승률: " + ", ".join(parts),
                     self.e(f"{self.name(champ)} 정글 게임 시간별 승률: " + ", ".join(parts), sum(v["games"] for v in d.values())))
        if not card.headline:
            card.headline = "조합이 정해지면 업데이트"
        return card

    def _turn_facts(self, s, o) -> None:
        """오브젝트 직전 귀환 턴: 고티어에서 '미리 귀환'한 팀이 실제로 더 가져갔는지."""
        for obj, med_key in (("DRAGON", "first_dragon_median_s"), ("HORDE", "first_grub_median_s")):
            t = self.stats.turn_objective(s, obj)
            if not {"none", "late"} <= t.keys():
                continue
            prep = [t[k] for k in ("sync", "jg_only") if k in t]
            pg, pt = sum(r["games"] for r in prep), sum(r["took"] for r in prep)
            if not pg:
                continue
            rate = {"prep": pt / pg, "none": t["none"]["took"] / t["none"]["games"],
                    "late": t["late"]["took"] / t["late"]["games"]}
            n = min(pg, t["none"]["games"], t["late"]["games"])
            name = OBJ_TURN_KO[obj]
            eid = self.e(f"{name}이 처음 잡히기 2:30~0:40 전에 정글이 귀환(아이템 구매)한 팀의 획득률 {pct(rate['prep'])} (n={pg}), "
                         f"미리 귀환 안 한 팀 {pct(rate['none'])} (n={t['none']['games']}), "
                         f"직전 30초 안에 정글이 귀환한 팀 {pct(rate['late'])} (n={t['late']['games']})", n)
            med = (o or {}).get(med_key)
            self.facts.setdefault("turns", {})[obj] = {
                "rate": rate, "n": n, "eid": eid, "median": med,
                "useful": n >= MIN_INFER * 2 and rate["prep"] - rate["none"] >= 0.05}

    def paths_for(self, state, champ: int, enemy_jg: int) -> dict:
        """고티어 실제 동선 하나(메도이드)를 클리어 방식별로. 상대 정글은 가장 흔한 방식 하나."""
        out = {"mine": [], "enemy": None}
        team = state.my_team_id
        style_ko = {"full_clear": "풀캠", "partial": "4~5캠프 후 개입", "three_or_less": "3캠 갱"}
        for style in ("full_clear", "partial", "three_or_less"):
            m = self.stats.path_medoid(champ, team, style)
            if m:
                out["mine"].append({"style": style, "label": style_ko[style], "games": m["games"],
                                    "minutes": m["points"]["minutes"], "events": m["points"]["events"]})
        out["mine"].sort(key=lambda x: -x["games"])
        if enemy_jg:
            m = self.stats.path_medoid(enemy_jg, state.enemy_team_id, "any")
            if m:
                out["enemy"] = {"games": m["games"], "minutes": m["points"]["minutes"], "events": m["points"]["events"],
                                "name": self.name(enemy_jg)}
        return out

    # ------------------------------------------------------------ plan

    def build_plan(self, champ: int, enemy_jg: int) -> list[PlanLine]:
        """카드에서 모은 사실로 '이번 판 플랜'을 쉬운 말로. 근거가 없으면 그 줄은 만들지 않는다."""
        f, me, plan = self.facts, self.name(champ), []
        st = f.get("start")
        if st and st["n"] >= MIN_INFER:
            sh = st["share"]
            if st["clear"] == "full_clear" and sh["full_clear"] >= 0.5:
                how = f"3분 안에 풀캠 (고티어 {me} {pct(sh['full_clear'])})"
            elif sh["three_or_less"] >= 0.35:
                how = f"3캠만 먹고 바로 갱·카정 (고티어 {me} {pct(sh['three_or_less'])})"
            else:
                how = (f"풀캠({pct(sh['full_clear'])})이 기본, 라인 상황이 좋으면 4~5캠프 먹고 갱"
                       f"({pct(sh['partial'])})")
            camp = f"{st['camp']} 시작 → " if st["camp"] and st["camp_share"] >= 0.4 else ""
            plan.append(PlanLine("시작", camp + how, [e for e in (st["camp_eid"], st["eid"]) if e]))

        gl, gt = f.get("gank_lane"), f.get("gank_time")
        when = f"{mmss(gt['median_s'])} 전후" if gt else "4분 전후"
        if gl:
            why = f" — {', '.join(gl['why'][:2])}" if gl["why"] else ""
            plan.append(PlanLine("첫 갱", f"{when} {LANE_KO[gl['lane']]} 먼저 갱{why}",
                                 gl["eids"] + ([gt["eid"]] if gt else [])))
        elif gt:
            plan.append(PlanLine("첫 갱", f"{when}, 라인별 차이가 작으니 라인 주도권 있는 쪽으로 첫 갱",
                                 [gt["eid"]]))

        warn, warn_ev = [], []
        es = f.get("enemy_side3")
        if es:
            other = "봇" if es["side"] == "탑" else "탑"
            warn.append(f"3:00엔 상대 {josa(self.name(enemy_jg), '이가')} {es['side']} 쪽에 있을 확률 {pct(es['share'])} → "
                        f"그 시간엔 {other} 쪽 바위게·갱이 안전")
            warn_ev.append(es["eid"])
        mu = f.get("matchup")
        if mu and mu["gd5"] < -150:
            warn.append(f"{self.name(enemy_jg)} 상대로 5분 골드가 평균 {abs(mu['gd5']):.0f} 밀림 → 초반 정글 1:1 피하기")
            warn_ev.append(mu["eid"])
        du = f.get("duel")
        if du and du["weak"]:
            warn.append(f"{josa(me)} {'·'.join(BAND_KO[x] for x in du['weak'])} 정글 싸움 승률이 낮음 → 그 레벨대엔 싸우지 말고 파밍")
            warn_ev.append(du["eid"])
        elif du and du["strong"]:
            warn.append(f"{josa(me)} {'·'.join(BAND_KO[x] for x in du['strong'])} 정글 싸움 승률이 높음 → 그 레벨대엔 싸움·카정 노려볼 만함")
            warn_ev.append(du["eid"])
        if warn:
            plan.append(PlanLine("주의", " / ".join(warn), warn_ev))

        ot, os_ = f.get("obj_times"), f.get("obj_side")
        has_turn = any(t["useful"] and t["median"] for t in f.get("turns", {}).values())
        reset = "" if has_turn else ", 7:30쯤 귀환해서 정비하고 먼저 자리 잡기"
        if ot:
            if os_:
                target = "첫 드래곤" if os_["side"] == "dragon" else "공허 유충"
                lane = "봇" if os_["side"] == "dragon" else "탑"
                t = ot["dragon"] if os_["side"] == "dragon" else ot["grub"]
                plan.append(PlanLine("오브젝트", f"{lane} 라인전이 유리 → {target} 먼저 (고티어 보통 {mmss(t)}), "
                                     f"{reset.lstrip(', ') or '라인 주도권 유지'}", os_["eids"] + [ot["eid"]]))
            else:
                plan.append(PlanLine("오브젝트", f"고티어 기준 유충 {mmss(ot['grub'])}, 드래곤 {mmss(ot['dragon'])}쯤 첫 싸움 "
                                     f"→ 주도권 있는 쪽 오브젝트로{reset}", [ot["eid"]]))
        turns = f.get("turns", {})
        for obj in ("DRAGON", "HORDE"):
            tf = turns.get(obj)
            if tf and tf["useful"] and tf["median"]:
                lo, hi = tf["median"] - 150, tf["median"] - 40
                plan.append(PlanLine("귀환", f"{OBJ_TURN_KO[obj]}(고티어 {mmss(tf['median'])}) 직전 30초엔 본진에 있지 않기 "
                                     f"→ 그때 귀환한 팀은 {pct(tf['rate']['late'])}만 가져감. 귀환할 거면 {mmss(lo)}~{mmss(hi)}에", [tf["eid"]]))
                break
        sc = f.get("scaling")
        if sc:
            text = ("상대가 후반 조합 → 오브젝트로 차이 벌려서 25분 전후에 끝내기" if sc["who"] == "enemy"
                    else "우리가 후반 조합 → 초반 손해만 피하고 오브젝트 맞교환으로 시간 벌기")
            plan.append(PlanLine("운영", text, [sc["eid"]]))
        for line in plan:
            line.concepts = PLAN_CONCEPTS.get(line.title, [])
        return plan

    def card_insights(self, champ: int, enemy_jg: int) -> Card:
        card = Card("insights", "프로 기록·가이드", "")
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
            card.add(f"최근 프로 대회({period})에서 {self.name(champ)} 정글 기록이 없어요.",
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
SRC_PROFILE = "Riot Match-V5 챔피언별 피해량 (10판 미만 챔피언은 Data Dragon 수치)"


LANE_SIDE_KO = {"top": "탑", "bot": "봇"}
CLEAR_KO = {"full_clear": "풀캠(6캠프)", "partial": "4~5캠프", "three_or_less": "3캠 이하"}

PROFILE_KO = {"ad_heavy": "AD 위주", "ap_heavy": "AP 위주", "balanced": "AD/AP 균형", "unknown": "알 수 없음"}
DUR_ORDER = ["<25", "25-30", "30-35", "35+"]
PLAN_CONCEPTS = {
    "시작": ["full-clear", "jungle-pathing"], "첫 갱": ["ganking", "lane-priority"],
    "주의": ["jungle-tracking", "power-spikes"], "오브젝트": ["objective-setup", "lane-priority"],
    "귀환": ["turn-tempo", "recall-timing"], "운영": ["win-condition", "scaling-comp"],
}
OBJ_TURN_KO = {"DRAGON": "첫 드래곤", "HORDE": "공허 유충"}
BAND_KO = {"1-3": "1~3레벨", "4-5": "4~5레벨", "6+": "6레벨 이후"}
