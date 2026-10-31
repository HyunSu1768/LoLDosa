"""개념 학습 라이브러리: learn/concepts.json (리서치 결과) + data/learn_progress.json (내 진도).

브리핑 플랜 줄과 리뷰 피드백은 관련 개념 id 를 달고 있어서, 화면에서 바로 개념으로 이동할 수 있다.
리뷰에서 지적된 개념은 진도 파일의 flags 에 쌓여 '다시 볼 개념'이 된다.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
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

    def record_checks(self, match_id: str, summary: dict, checks: list[dict]) -> None:
        if not checks:
            return
        self.data["checks"][match_id] = {"date": summary.get("date"), "champion": summary.get("champion"),
                                         "win": summary.get("win"), "checks": checks}
        self.save()

    def record_decision(self, match_id: str, minute: int, choice: str, good: bool, concepts: list[str]) -> None:
        self.data["decisions"] = [d for d in self.data["decisions"]
                                  if not (d["match_id"] == match_id and d["minute"] == minute)]
        self.data["decisions"].append({"match_id": match_id, "minute": minute, "choice": choice, "good": good,
                                       "concepts": concepts,
                                       "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        self.save()

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
