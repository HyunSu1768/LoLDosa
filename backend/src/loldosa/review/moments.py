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
    lvl = st["level_diff"]
    lanes_say = {k: gold_diff_say(st[f"lane_{k}"], p) for k in ("top", "mid", "bot")}
    facts = [  # 골드는 숫자 대신 아이템으로: 게임 중엔 몇 골드인지 계산할 수 없어서
        f"나: {REGION_KO.get(st['region'], st['region'])}에 있어요 · 체력 {round(st['hp'] * 100)}% · "
        f"가진 골드로 {can_buy(st['gold'], p)}",
        f"상대 정글과: 레벨 {'같아요' if not lvl else f'내가 {abs(lvl)} 높아요' if lvl > 0 else f'내가 {abs(lvl)} 낮아요'} · "
        f"골드 {gold_diff_say(st['gold_diff'], p, us='내')}",
        f"상대 정글은 실제로 {'탑' if st['enemy_side_top'] else '봇'} 쪽에 있었어요 (그때 보였는지는 시야에 따라 달라요)",
        "라인: " + " · ".join(f"{n} {lanes_say[k]}" for k, n in (("top", "탑"), ("mid", "미드"), ("bot", "봇"))),
        "오브젝트: " + (", ".join(f"{o['name']} {o['text']}" for o in objs) if objs else "당분간 없어요")
        + (f" · 용 개수 차이 {signed(st['dragon_diff'])}" if st["dragon_diff"] else ""),
    ]
    lanes = {"top": st["lane_top"], "mid": st["lane_mid"], "bot": st["lane_bot"]}
    lane_items = {k: {**gold_as_items(st[f"lane_{k}"], p), "say": lanes_say[k], "ahead": st[f"lane_{k}"] > 0} for k in lanes}
    return {"units": units, "objectives": objs, "facts": facts, "team": team, "minute": m, "lanes": lanes, "lane_items": lane_items}


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
        good = [c["action"] for c in crowd if c["share"] >= GOOD_SHARE]
        mine_c = next((c for c in crowd if c["action"] == mine), None)
        best = crowd[0] if crowd else None
        if mine in good:
            verdict = f"비슷한 상황 고티어의 {round(mine_c['share'] * 100)}%도 같은 선택을 했어요."
        elif best:
            verdict = (f"비슷한 상황 고티어는 주로 '{best['label']}'{josa(best['label'], '을를')[-1]} 골랐어요"
                       f"({round(best['share'] * 100)}%). 내 선택 '{ACTION_KO[mine]}'{josa(ACTION_KO[mine])[-1]} "
                       f"{round(mine_c['share'] * 100) if mine_c else 0}%뿐이었어요.")
        else:
            verdict = "비슷한 상황 데이터가 부족해요."
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
