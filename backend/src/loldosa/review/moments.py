"""'그 순간으로 돌아가기': 내 경기의 판단 지점을 문제로 만들고, 비슷한 상황의 고티어 선택·결과를 붙인다."""

from __future__ import annotations

from ..analysis.decisions import (ACTION_CONCEPTS, ACTION_KO, ACTIONS, classify_action, load_match,
                                  outcome, similar, state_vector, summarize)
from ..analysis.geometry import relative_region
from ..analysis.items import can_buy, gold_as_items, gold_diff_say, prices as item_prices
from ..analysis.turns import shop_visits
from ..briefing.engine import josa, mmss, signed
from ..ddragon import ChampionIndex

PIT = {"dragon": (9866, 4414), "baron": (5007, 10471)}
REGION_KO = {"own_jungle": "우리 정글", "enemy_jungle": "상대 정글", "river": "강가", "top": "탑 라인",
             "mid": "미드 라인", "bot": "봇 라인", "base": "본진", "unknown": "?"}
MAX_MOMENTS = 4
GOOD_SHARE = 0.2  # 비슷한 상황 고티어의 20% 이상이 고른 행동은 '괜찮은 선택'


def pick_minutes(md, pid: int, epid: int, team: int) -> list[tuple[int, str, int]]:
    """(분, 이유, 우선순위) — 데스 > 상대 정글 갱 > 오브젝트 > 3:00."""
    out = []
    for e in md.events:
        t = e["ts_ms"] / 1000
        if e["type"] == "CHAMPION_KILL" and e["victim_id"] == pid and t < 900:
            out.append((int((t - 30) // 60), f"{mmss(t)}에 죽기 30초 전", 0))
        elif (e["type"] == "CHAMPION_KILL" and t < 600 and e["victim_id"] != pid
              and md.parts.get(e["victim_id"], {}).get("team") == team
              and (e["participant_id"] == epid or epid in (e["assists"] or []))
              and relative_region(team, e["x"], e["y"]) in ("top", "mid", "bot")):
            out.append((int((t - 30) // 60), f"{mmss(t)} 상대 정글 갱 직전", 1))
    firsts = {}
    for e in md.events:
        if e["type"] == "ELITE_MONSTER_KILL" and e["monster_type"] in ("DRAGON", "HORDE"):
            firsts.setdefault(e["monster_type"], e)
    for mt, e in firsts.items():
        t = e["ts_ms"] / 1000
        if t < 1200:
            name = "첫 드래곤" if mt == "DRAGON" else "공허 유충"
            out.append((int(t // 60) - 1, f"{name}({mmss(t)}) 1분 전", 2))
    out.append((3, "3:00 정글링 직후 첫 판단", 3))
    seen, picked = set(), []
    for m, why, pri in sorted(out, key=lambda x: (x[2], x[0])):
        if m < 2 or m > 19 or m in seen:
            continue
        seen.add(m)
        picked.append((m, why, pri))
        if len(picked) >= MAX_MOMENTS:
            break
    return sorted(picked)


def _ieyo(word: str) -> str:
    """받침 있으면 '이에요', 없으면 '예요'."""
    base = word.split(" (")[0].rstrip(")") if word else ""  # '카정 (상대 정글)' → '카정' 기준으로
    c = ord(base[-1]) - 0xAC00 if base else -1
    return f"{word}{'이에요' if 0 <= c <= 11171 and c % 28 else '예요'}"


def last_seen(md, epid: int, t_ms: float) -> dict | None:
    """상대 정글이 정확한 시각과 위치로 드러난 마지막 순간 (킬·데스·어시스트·오브젝트). 그 판단 시점 이전만."""
    best = None
    for e in md.events:
        if e["ts_ms"] > t_ms or e.get("x") is None:
            continue
        involved = (e["type"] == "CHAMPION_KILL" and (e["participant_id"] == epid or e["victim_id"] == epid
                                                     or epid in (e["assists"] or [])))
        involved = involved or (e["type"] == "ELITE_MONSTER_KILL" and e["participant_id"] == epid)
        if involved and (best is None or e["ts_ms"] > best["ts_ms"]):
            best = e
    if not best:
        return None
    return {"t": best["ts_ms"] / 1000, "x": best["x"], "y": best["y"], "ago": (t_ms - best["ts_ms"]) / 1000,
            "what": "오브젝트" if best["type"] == "ELITE_MONSTER_KILL" else "싸움"}


# 정답 기준: 많이 고른 것(인기)이 아니라 2분 뒤 결과. 데스·오브젝트를 골드로 환산한 대략값 (추정)
DEATH_COST, OBJ_VALUE, MIN_SHARE, MIN_N, NEAR, POPULAR, WORSE = 700, 400, 0.08, 5, 150, 0.2, 400


def score_actions(crowd: list[dict]) -> list[dict]:
    """정답 = 비슷한 상황 고수의 20% 이상이 고른 선택. 결과 1위는 참고 배지(best)로만 표시한다.

    검증 (research_notes/검증, 프로 120판 vs 플래티넘 154판, 실제 선택이 정답에 든 비율):
    - 많이 고른 것(20%↑)      : 52.7% vs 44.4% (차이 8.3%p) ← 실력을 가장 잘 가름
    - 인기 + 결과 나쁜 것 제외 : 43.5% vs 37.7% (5.8%p)
    - 2분 뒤 결과 1위만        : 27.1% vs 24.8% (2.3%p) ← 행동별 표본이 작고 상황 영향이 커서 노이즈
    """
    for c in crowd:
        ok = c["share"] >= MIN_SHARE and c.get("n", 0) >= MIN_N and c.get("swing") is not None
        c["score"] = round((c["swing"] or 0) - DEATH_COST * c["died"] + OBJ_VALUE * c["obj"]) if ok else None
    scored = [c for c in crowd if c["score"] is not None]
    top = max((c["score"] for c in scored), default=None)
    for c in crowd:
        c["best"] = top is not None and c["score"] is not None and c["score"] >= top - NEAR
    return [c["action"] for c in crowd if c["share"] >= POPULAR]


def _prices() -> dict:
    from ..config import load_settings

    return item_prices(str(load_settings().data_dir))


def snapshot(md, champs: ChampionIndex, pid: int, epid: int, team: int, m: int, st: dict) -> dict:
    units = []
    for q, p in md.parts.items():
        f = md.frames.get((q, m))
        if not f or f["x"] is None:
            continue
        c = champs.get(p["champion_id"])
        units.append({"x": f["x"], "y": f["y"], "key": c.key if c else "", "name": c.name if c else "",
                      "ally": p["team"] == team, "me": q == pid, "enemy_jungler": q == epid,
                      "level": f["level"], "hp": round((f["hp"] / f["hp_max"]) * 100) if f.get("hp") is not None and f.get("hp_max") else None,
                      "position": p["position"]})
    objs = []
    if st["to_dragon"] < 999:
        objs.append({"name": "드래곤", "x": PIT["dragon"][0], "y": PIT["dragon"][1],
                     "text": "지금 있어요" if st["to_dragon"] == 0 else f"{mmss(st['to_dragon'])} 뒤"})
    if st["to_grub"] < 999:
        objs.append({"name": "유충", "x": PIT["baron"][0], "y": PIT["baron"][1],
                     "text": "지금 있어요" if st["to_grub"] == 0 else f"{mmss(st['to_grub'])} 뒤"})
    elif st["to_herald"] < 999:
        objs.append({"name": "전령", "x": PIT["baron"][0], "y": PIT["baron"][1],
                     "text": "지금 있어요" if st["to_herald"] == 0 else f"{mmss(st['to_herald'])} 뒤"})
    p = _prices()
    lvl = int(round(st["level_diff"]))
    lanes_say = {k: gold_diff_say(st[f"lane_{k}"], p) for k in ("top", "mid", "bot")}
    facts = [  # 골드는 숫자 대신 아이템으로: 게임 중엔 몇 골드인지 계산할 수 없어서
        f"나: {REGION_KO.get(st['region'], st['region'])}에 있어요 · 체력 {round(st['hp'] * 100)}% · "
        f"가진 골드로 {can_buy(st['gold'], p)}",
        f"상대 정글과: 레벨 {'같아요' if not lvl else f'내가 {abs(lvl)} 높아요' if lvl > 0 else f'내가 {abs(lvl)} 낮아요'} · "
        f"골드 {gold_diff_say(st['gold_diff'], p, us='내')}",
        "라인: " + " · ".join(f"{n} {lanes_say[k]}" for k, n in (("top", "탑"), ("mid", "미드"), ("bot", "봇"))),
        "오브젝트: " + (", ".join(f"{o['name']} {o['text']}" for o in objs) if objs else "당분간 없어요")
        + (f" · 용 개수 차이 {signed(st['dragon_diff'])}" if st["dragon_diff"] else ""),
    ]
    seen = last_seen(md, epid, m * 60_000)
    ejg_name = (champs.get(md.parts[epid]["champion_id"]).name if champs.get(md.parts[epid]["champion_id"]) else "상대 정글")
    facts.insert(2, f"상대 정글({ejg_name})을 마지막으로 본 건 {mmss(seen['t'])} {REGION_KO.get(relative_region(team, seen['x'], seen['y']), '')}"
                    f" ({int(seen['ago'])}초 전 {seen['what']})" if seen else f"상대 정글({ejg_name})은 게임 시작 뒤 아직 모습을 드러낸 적이 없어요")
    ef = md.frames.get((epid, m)) or {}
    truth_region = relative_region(team, ef.get("x"), ef.get("y")) if ef.get("x") is not None else "unknown"
    track = {"q": "상대 정글은 지금 어느 쪽에 있을까요?", "answer": "top" if st["enemy_side_top"] else "bot",
             "choices": [{"id": "top", "label": "탑 쪽"}, {"id": "bot", "label": "봇 쪽"}],
             "truth": f"실제로는 {REGION_KO.get(truth_region, truth_region)}({'탑' if st['enemy_side_top'] else '봇'} 쪽)에 있었어요"}
    lanes = {"top": st["lane_top"], "mid": st["lane_mid"], "bot": st["lane_bot"]}
    lane_items = {k: {**gold_as_items(st[f"lane_{k}"], p), "say": lanes_say[k], "ahead": st[f"lane_{k}"] > 0} for k in lanes}
    for u in units:  # 상대 정글은 실제 위치를 숨긴다 (그 순간 내가 볼 수 있었던 정보로만 판단하게). 답한 뒤에 보여 준다
        if u["enemy_jungler"]:
            u["hidden"] = True
    return {"units": units, "objectives": objs, "facts": facts, "team": team, "minute": m, "lanes": lanes, "lane_items": lane_items,
            "last_seen": seen, "track": track}


def swing_say(v, p) -> str:
    """2분 뒤 팀 골드 변화 → '팀이 롱소드 1개쯤 벌어요' / '팀이 롱소드 1개쯤 잃어요'."""
    if v is None:
        return "-"
    it = gold_as_items(v, p)
    if not it["count"]:
        return "팀 골드 그대로"
    return f"팀이 {it['text']} {'벌어요' if v > 0 else '잃어요'}"


def build_moments(con, stats, champs: ChampionIndex, match_id: str, puuid: str) -> list[dict]:
    md = load_match(con, match_id)
    me = next((q for q, p in md.parts.items() if p["puuid"] == puuid), None)
    if me is None or md.parts[me]["position"] != "JUNGLE":
        return []
    team = md.parts[me]["team"]
    epid = next((q for q, p in md.parts.items() if p["position"] == "JUNGLE" and p["team"] != team), None)
    if epid is None:
        return []
    visits = shop_visits(md.purchases, [(e["victim_id"], e["ts_ms"]) for e in md.events if e["type"] == "CHAMPION_KILL"])
    allies = [q for q, p in md.parts.items() if p["team"] == team]
    enemies = [q for q, p in md.parts.items() if p["team"] != team]
    out = []
    for m, why, _ in pick_minutes(md, me, epid, team):
        if (me, m) not in md.frames or (epid, m) not in md.frames or (me, m + 1) not in md.frames:
            continue
        st = state_vector(md, me, epid, team, m)
        st["minute"] = m
        mine = classify_action(md, me, team, m, visits)
        res = outcome(md, me, team, allies, enemies, m)
        pool, label = stats.decision_pool(m)
        pool = [r for r in pool if r.get("match_id") != match_id]  # 같은 경기는 비교 대상에서 뺀다
        neigh = similar(pool, st, k=60)
        crowd = summarize(neigh)
        pr = _prices()
        for c in crowd:
            c["swing_say"] = swing_say(c.get("swing"), pr)
        top = [c["action"] for c in crowd[:3]]
        choices = [a for a in ACTIONS if a in set(top + [mine]) or a in ("recall", "farm")][:6]
        good = score_actions(crowd)
        mine_c = next((c for c in crowd if c["action"] == mine), None)
        best = crowd[0] if crowd else None
        best_out = max((c for c in crowd if c.get("best")), key=lambda c: c["score"], default=None)
        if mine in good:
            verdict = f"비슷한 상황 고티어의 {round(mine_c['share'] * 100)}%도 같은 선택을 했어요."
        elif best:
            verdict = (f"비슷한 상황 고티어는 주로 '{best['label']}'{josa(best['label'].split(' (')[0], '을를')[-1]} 골랐어요"
                       f"({round(best['share'] * 100)}%). 내 선택 '{ACTION_KO[mine]}'{josa(ACTION_KO[mine].split(' (')[0])[-1]} "
                       f"{round(mine_c['share'] * 100) if mine_c else 0}%뿐이었어요.")
        else:
            verdict = "비슷한 상황 데이터가 부족해요."
        if best_out and best_out["action"] != (best or {}).get("action"):
            end = "이에요" if _ieyo(best_out["label"]).endswith("이에요") else "예요"
            verdict += f" 참고로 2분 뒤 결과가 가장 좋았던 건 '{best_out['label']}'{end}."
        out.append({
            "minute": m, "t": m * 60, "reason": why,
            "snapshot": snapshot(md, champs, me, epid, team, m, st),
            "choices": [{"action": a, "label": ACTION_KO[a]} for a in choices],
            "mine": {"action": mine, "label": ACTION_KO[mine], "swing": res["swing"], "swing_say": swing_say(res["swing"], pr),
                     "died": res["died"], "obj": res["obj"]},
            "crowd": crowd, "k": len(neigh), "pool_label": label, "good": good, "verdict": verdict,
            "concepts": list(dict.fromkeys(ACTION_CONCEPTS[mine] + (ACTION_CONCEPTS[best["action"]] if best else []))),
        })
    return out
