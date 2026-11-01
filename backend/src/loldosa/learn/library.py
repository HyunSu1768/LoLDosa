"""개념 학습 라이브러리: learn/concepts.json (리서치 결과) + data/learn_progress.json (내 진도).

브리핑 플랜 줄과 리뷰 피드백은 관련 개념 id 를 달고 있어서, 화면에서 바로 개념으로 이동할 수 있다.
리뷰에서 지적된 개념은 진도 파일의 flags 에 쌓여 '다시 볼 개념'이 된다.
"""

from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CONCEPTS_PATH = Path(__file__).parent / "concepts.json"

# 코드(브리핑·리뷰)에서 참조하는 개념 id. concepts.json 에 반드시 있어야 한다 (테스트로 확인).
REQUIRED_IDS = {
    "turn-tempo", "wave-states", "lane-priority", "recall-timing", "objective-setup", "full-clear",
    "jungle-pathing", "jungle-tracking", "ganking", "counter-gank", "cross-map", "vision-control",
    "power-spikes", "clear-efficiency", "win-condition", "scaling-comp", "invading", "dragon", "void-grubs",
}


def load_library(path: Path = CONCEPTS_PATH) -> dict:
    if not path.exists():
        return {"version": "", "categories": [], "concepts": []}
    return json.loads(path.read_text(encoding="utf-8"))


class Progress:
    def __init__(self, data_dir: Path) -> None:
        self.path = data_dir / "learn_progress.json"
        self.data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        self.data.setdefault("read", {})  # id -> 처음 읽은 시각
        self.data.setdefault("quiz", {})  # id -> {"correct": n, "total": n}
        self.data.setdefault("flags", {})  # id -> [match_id, ...] 리뷰에서 지적된 경기
        self.data.setdefault("decisions", [])  # 판단 훈련 답: {match_id, minute, choice, good, concepts, at}
        self.data.setdefault("srs", {})  # 복습 항목 key -> {box, due, kind, ref}
        self.data.setdefault("ranks", [])  # 랭크 기록 [{at, tier, rank, lp, wins, losses}]
        self.data.setdefault("checks", {})  # match_id -> {"date":..., "champion":..., "checks": [...]}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")

    def mark_read(self, cid: str) -> None:
        self.data["read"].setdefault(cid, datetime.now(timezone.utc).isoformat(timespec="seconds"))
        self.save()

    def record_quiz(self, cid: str, correct: bool) -> None:
        q = self.data["quiz"].setdefault(cid, {"correct": 0, "total": 0})
        q["total"] += 1
        q["correct"] += int(correct)
        self.save()

    def flag(self, concept_ids: set[str], match_id: str) -> None:
        changed = False
        for cid in concept_ids:
            lst = self.data["flags"].setdefault(cid, [])
            if match_id not in lst:
                lst.append(match_id)
                changed = True
        if changed:
            self.save()

    def record_checks(self, match_id: str, summary: dict, checks: list[dict], facts: dict | None = None) -> None:
        if not checks:
            return
        keep = {k: v for k, v in (facts or {}).items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
        self.data["checks"][match_id] = {"date": summary.get("date"), "champion": summary.get("champion"),
                                         "win": summary.get("win"), "checks": checks, "facts": keep}
        self.save()

    def baseline(self, exclude: str | None = None, limit: int = 20) -> dict:
        """내 최근 경기들의 평균(이번 경기 제외) — '지난 나'와 비교."""
        rows = [r for mid, r in sorted(self.data["checks"].items(), key=lambda kv: kv[1].get("date") or "",
                                       reverse=True) if mid != exclude][:limit]
        out: dict[str, float] = {}
        for k in ("camps3", "cs10", "deaths10", "vision_pm", "first_recall_s"):
            vals = [r.get("facts", {}).get(k) for r in rows if r.get("facts", {}).get(k) is not None]
            if len(vals) >= 3:
                out[k] = sum(vals) / len(vals)
        out["games"] = len(rows)
        return out

    # ---- 숙련도 --------------------------------------------------------------

    def mastery(self, cid: str) -> dict:
        """경기 체크(최근 가중) 60% + 판단 훈련 25% + 퀴즈 15%. 있는 것만으로 다시 비율을 맞춘다."""
        parts, n_total = [], 0
        hist = [c for h in self.history(cid, 15) for c in h["checks"] if c["status"] != "na"]
        if hist:
            w = [0.85 ** i for i in range(len(hist))]  # 최근 경기 가중
            parts.append((0.6, sum(wi * (c["status"] == "pass") for wi, c in zip(w, hist)) / sum(w)))
            n_total += len(hist)
        dec = [d for d in self.data["decisions"] if cid in d.get("concepts", [])][-15:]
        if dec:
            parts.append((0.25, sum(d["good"] for d in dec) / len(dec)))
            n_total += len(dec)
        q = self.data["quiz"].get(cid)
        if q and q["total"]:
            parts.append((0.15, q["correct"] / q["total"]))
            n_total += q["total"]
        if not parts:
            return {"score": None, "n": 0, "level": "미측정"}
        wsum = sum(w for w, _ in parts)
        score = round(100 * sum(w * v for w, v in parts) / wsum)
        level = "익힘" if score >= 75 else "익히는 중" if score >= 45 else "약함"
        return {"score": score, "n": n_total, "level": level if n_total >= 3 else "기록 적음"}

    # ---- 반복 학습 (라이트너 상자: 1·2·4·8·16일) ----------------------------------

    BOX_DAYS = [1, 2, 4, 8, 16]

    def schedule(self, key: str, kind: str, ref: dict) -> None:
        if key not in self.data["srs"]:
            self.data["srs"][key] = {"box": 0, "due": date.today().isoformat(), "kind": kind, "ref": ref}
            self.save()

    def due_items(self, limit: int = 8) -> list[dict]:
        today = date.today().isoformat()
        due = [dict(v, key=k) for k, v in self.data["srs"].items() if v["due"] <= today]
        random.Random(today).shuffle(due)
        return due[:limit]

    def grade(self, key: str, correct: bool) -> dict | None:
        it = self.data["srs"].get(key)
        if not it:
            return None
        it["box"] = min(it["box"] + 1, len(self.BOX_DAYS) - 1) if correct else 0
        it["due"] = (date.today() + timedelta(days=self.BOX_DAYS[it["box"]])).isoformat()
        self.save()
        return it

    # ---- 랭크 ----------------------------------------------------------------

    def record_rank(self, entry: dict) -> None:
        snap = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "tier": entry.get("tier"),
                "rank": entry.get("rank"), "lp": entry.get("leaguePoints"), "wins": entry.get("wins"),
                "losses": entry.get("losses")}
        last = self.data["ranks"][-1] if self.data["ranks"] else None
        if not last or any(last.get(k) != snap[k] for k in ("tier", "rank", "lp", "wins", "losses")):
            self.data["ranks"].append(snap)
            self.save()

    def record_lesson_feedback(self, match_id: str, rule: str, ok: bool) -> None:
        """'이 교훈이 맞나요?' 맞아요/아니에요. 규칙별로 모아서, 자꾸 틀리는 규칙은 핵심 교훈에서 뒤로 미룬다."""
        fb = self.data.setdefault("lesson_feedback", {})
        fb[f"{match_id}|{rule}"] = {"rule": rule, "ok": bool(ok), "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        self.save()

    def lesson_rule_stats(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for r in self.data.get("lesson_feedback", {}).values():
            st = out.setdefault(r["rule"], {"ok": 0, "no": 0})
            st["ok" if r["ok"] else "no"] += 1
        return out

    def record_decision(self, match_id: str, minute: int, choice: str, good: bool, concepts: list[str],
                        moment: dict | None = None, track_ok: bool | None = None) -> None:
        if moment is not None and not good:
            self.schedule(f"moment:{match_id}:{minute}", "moment", moment)
        self.data["decisions"] = [d for d in self.data["decisions"]
                                  if not (d["match_id"] == match_id and d["minute"] == minute)]
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.data["decisions"].append({"match_id": match_id, "minute": minute, "choice": choice, "good": good,
                                       "concepts": concepts, "at": now})
        if track_ok is not None:  # 상대 정글 위치 맞히기: '상대 정글 위치 파악' 숙련도에 들어간다
            self.data["decisions"].append({"match_id": match_id, "minute": minute, "choice": "track", "kind": "track",
                                           "good": bool(track_ok), "concepts": ["jungle-tracking"], "at": now})
        self.save()

    def decision_summary(self, days: int = 7) -> dict:
        """최근 N일 판단 훈련: 고수와 같은 선택 수, 상대 정글 추적 정답 수."""
        from datetime import timedelta

        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
        recent = [d for d in self.data["decisions"] if (d.get("at") or "") >= since]
        act = [d for d in recent if d.get("kind") != "track"]
        trk = [d for d in recent if d.get("kind") == "track"]
        return {"total": len(act), "good": sum(1 for d in act if d["good"]),
                "track_total": len(trk), "track_ok": sum(1 for d in trk if d["good"])}

    def history(self, concept: str | None = None, limit: int = 20) -> list[dict]:
        """최근 경기(날짜 내림차순)의 체크 기록. concept 을 주면 그 개념만."""
        rows = sorted(self.data["checks"].items(), key=lambda kv: kv[1].get("date") or "", reverse=True)[:limit]
        out = []
        for mid, r in rows:
            checks = r["checks"] if not concept else [c for c in r["checks"] if c["concept"] == concept]
            out.append({"match_id": mid, "date": r.get("date"), "champion": r.get("champion"), "win": r.get("win"),
                        "checks": checks})
        return out

    def skill_rates(self, limit: int = 10) -> dict[str, dict]:
        """개념별 최근 N경기 달성률 (해당 없음 제외)."""
        out: dict[str, dict] = {}
        for h in self.history(limit=limit):
            for c in h["checks"]:
                if c["status"] == "na":
                    continue
                r = out.setdefault(c["concept"], {"pass": 0, "total": 0})
                r["total"] += 1
                r["pass"] += c["status"] == "pass"
        return out

    def recommended(self, library: dict, limit: int = 6) -> list[dict]:
        """리뷰에서 자주 지적됐고 아직 퀴즈를 못 푼 개념부터."""
        titles = {c["id"]: c for c in library.get("concepts", [])}
        scored = []
        for cid, matches in self.data["flags"].items():
            if cid not in titles:
                continue
            q = self.data["quiz"].get(cid, {"correct": 0, "total": 0})
            mastered = q["total"] and q["correct"] / q["total"] >= 0.8
            scored.append((len(matches) - (2 if mastered else 0), cid, len(matches)))
        scored.sort(reverse=True)
        return [{"id": cid, "title": titles[cid]["title"], "count": n} for _, cid, n in scored[:limit]]


TIER_ORDER = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
DIV = {"IV": 0, "III": 1, "II": 2, "I": 3}
TIER_KO = {"IRON": "아이언", "BRONZE": "브론즈", "SILVER": "실버", "GOLD": "골드", "PLATINUM": "플래티넘",
           "EMERALD": "에메랄드", "DIAMOND": "다이아", "MASTER": "마스터", "GRANDMASTER": "그랜드마스터",
           "CHALLENGER": "챌린저"}


def ladder_points(r: dict) -> int | None:
    """티어·디비전·LP 를 한 줄 점수로 (디비전 100점, 티어 400점)."""
    if not r or r.get("tier") not in TIER_ORDER:
        return None
    t = TIER_ORDER.index(r["tier"])
    if t >= TIER_ORDER.index("MASTER"):
        return TIER_ORDER.index("MASTER") * 400 + (r.get("lp") or 0)
    return t * 400 + DIV.get(r.get("rank"), 0) * 100 + (r.get("lp") or 0)


def rank_label(r: dict | None) -> str:
    if not r:
        return "-"
    return f"{TIER_KO.get(r['tier'], r['tier'])} {r.get('rank') or ''} {r.get('lp')}LP".replace("  ", " ")


def effect_report(progress: "Progress", focus: str, since: str) -> dict | None:
    """연습 목표를 정한 시점 전후 비교."""
    if not focus or not since:
        return None
    cut = since.replace("T", " ")[:16]
    rows = sorted(progress.data["checks"].values(), key=lambda r: r.get("date") or "")

    def summarize(rs):
        f = [c for r in rs for c in r["checks"] if c["concept"] == focus and c["status"] != "na"]
        return {"games": len(rs), "focus_pass": sum(c["status"] == "pass" for c in f), "focus_total": len(f),
                "wins": sum(1 for r in rs if r.get("win"))}

    before = summarize([r for r in rows if (r.get("date") or "") < cut][-20:])
    after = summarize([r for r in rows if (r.get("date") or "") >= cut])
    ranks = progress.data["ranks"]
    start = next((r for r in reversed(ranks) if r["at"] <= since), ranks[0] if ranks else None)
    now = ranks[-1] if ranks else None
    delta = (ladder_points(now) - ladder_points(start)) if start and now and ladder_points(now) is not None \
        and ladder_points(start) is not None else None
    return {"since": cut, "before": before, "after": after, "rank_start": rank_label(start), "rank_now": rank_label(now),
            "rank_delta": delta}
