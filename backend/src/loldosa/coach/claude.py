"""Claude 구독 플랜으로 AI 코칭: 로컬에 로그인된 Claude Code CLI 를 헤드리스로 호출한다.

규칙
- 브리핑의 근거(Evidence) 목록만 입력으로 준다. 도구·MCP·웹 접근은 모두 끈다.
- 모든 문장은 근거 ID(E1, E2…)를 달아야 하고, 없거나 존재하지 않는 ID 를 단 문장은 버린다.
- 실패하거나 시간이 초과돼도 앱은 규칙 기반 카드만으로 동작한다.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil

SYSTEM = """너는 리그 오브 레전드 정글 코치다. 사용자는 지금 챔피언 선택 화면에 있고, 곧 게임에 들어간다.
반드시 지킬 규칙:
1. 주어진 EVIDENCE 목록에 있는 사실만 사용한다. 너의 사전 지식(챔피언 스킬, 메타, 일반론)으로 사실을 만들지 않는다.
2. 모든 포인트에 근거 ID 를 1개 이상 단다. 근거로 뒷받침되지 않는 내용은 쓰지 않는다.
3. 판 수가 적은(신뢰도 낮음) 근거는 단정하지 말고 '판 수 적음'을 밝힌다.
4. 실행 가능한 행동으로 쓴다: 언제(시간대), 어디서, 무엇을. 한국어 해요체.
   각 포인트는 한 문장, 80자 이내. 숫자는 꼭 필요한 것 하나만. 플래티넘 플레이어가 로딩 화면에서 10초 안에 읽을 수 있게.
5. 근거 문장에 없는 인과관계를 만들지 않는다. 예: 3:00 위치만 보고 몇 캠프를 돌았는지 추측하지 말고, 풀캠 여부는 '먹은 캠프 수' 근거로만 말한다.
6. 출력은 JSON 하나만. 다른 텍스트 금지.
7. 한국 롤 커뮤니티에서 실제로 쓰는 말로 쓴다. 예: 풀캠, 3캠 갱, 라인 주도권, 바위게, 역갱, 카정, 귀환, 오브젝트 세팅, 핑와, 라인 박기, 상대 정글.
   번역투·영어 직역은 쓰지 않는다: 스커틀→바위게, 우선권/프리오→주도권, 리셋→귀환, 스폰→젠·나오다, 클리어 완료→풀캠·먹은 캠프, 개입/관여→갱·합류, ~창(window)→~타이밍, 표본→판 수.
   문장은 짧은 해요체(~해요, ~하세요)로 쓴다. '~합니다', '~입니다'는 쓰지 않는다.
형식: {"headline": "이번 판 한 줄 운영 방향", "points": [{"phase": "0-3분|3-8분|8-15분|15분+|전체", "text": "...", "evidence": ["E1"]}]}
points 는 3~4개, 시간 순서로."""


REVIEW_SYSTEM = """너는 리그 오브 레전드 정글 코치다. 사용자가 끝난 경기를 복기하고 있다.
반드시 지킬 규칙:
1. 주어진 EVIDENCE 목록에 있는 사실만 사용한다. 너의 사전 지식으로 사실을 만들지 않는다.
2. 모든 포인트에 근거 ID 를 1개 이상 단다.
3. 판 수가 적은(신뢰도 낮음) 근거는 단정하지 않는다.
4. 비난하지 말고, 다음 판에 바로 할 수 있는 행동으로 쓴다. 한국어 해요체, 각 포인트 2문장 이내.
5. 근거 문장에 없는 인과관계를 만들지 않는다.
6. 출력은 JSON 하나만.
7. 한국 롤 커뮤니티에서 실제로 쓰는 말로 쓴다. 예: 풀캠, 3캠 갱, 라인 주도권, 바위게, 역갱, 카정, 귀환, 오브젝트 세팅, 핑와, 라인 박기, 상대 정글.
   번역투·영어 직역은 쓰지 않는다: 스커틀→바위게, 우선권/프리오→주도권, 리셋→귀환, 스폰→젠·나오다, 클리어 완료→풀캠·먹은 캠프, 개입/관여→갱·합류, ~창(window)→~타이밍, 표본→판 수.
   문장은 짧은 해요체(~해요, ~하세요)로 쓴다. '~합니다', '~입니다'는 쓰지 않는다.
형식: {"headline": "이 경기 한 줄 총평", "points": [{"phase": "잘한 점|고칠 점|다음 판", "text": "...", "evidence": ["E1"]}]}
points 는 3~5개: 잘한 점 1개, 고칠 점 1~3개, 다음 판 1개."""


def build_review_prompt(review: dict) -> str:
    payload = {
        "summary": review.get("summary"),
        "lessons": [{k: l[k] for k in ("title", "text", "evidence")} for l in review.get("lessons", [])],
        "strengths": [{k: l[k] for k in ("title", "text", "evidence")} for l in review.get("strengths", [])],
        "metrics": review.get("metrics"),
        "EVIDENCE": [{"id": e["id"], "text": e.get("text", ""), "n": e.get("games"),
                      "confidence": e.get("confidence"), "source": e.get("source", "")}
                     for e in review.get("evidence", [])],
    }
    return "아래 경기 리뷰 데이터만 근거로 복기 코칭을 해줘.\n" + json.dumps(payload, ensure_ascii=False, default=str)


WEEKLY_SYSTEM = """너는 한국 롤 정글 코치다. 플레이어의 최근 경기 진단 데이터로 '이번 주 연습 계획'을 짠다.
규칙:
1. 데이터에 있는 것만 말한다. 모든 point 의 evidence 에는 EVIDENCE 의 id 를 하나 이상 넣는다.
2. 숫자는 데이터에 있는 그대로 쓴다. 지어내지 않는다.
3. lever 가 false 인 지표는 '원인'이라고 말하지 말고 습관 표시로만 다룬다.
4. 한 주에 고칠 것은 하나만 고른다. 나머지는 유지하거나 나중으로 미룬다.
5. 문장은 짧은 해요체로 쓴다. '~합니다', '~입니다'는 쓰지 않는다.
6. 출력은 JSON 하나만.
형식: {"headline": "이번 주 한 줄 요약", "points": [{"phase": "좋아진 점|이번 주 고칠 것|다짐|유지할 것", "text": "...", "evidence": ["G1"]}]}
points 는 3~5개."""


def weekly_evidence(gap: dict, skills: list[dict], decisions: dict) -> list[dict]:
    """주간 리포트 근거: 차이 지표(G), 채점 체크(S), 판단 훈련(D)."""
    ev = []
    for i, x in enumerate((gap.get("gaps") or []) + (gap.get("strengths") or []), 1):
        ev.append({"id": f"G{i}", "text": f"{x['label']}: 내 중앙값 {x['mine_text']}"
                   + (f" (이전 {x['before_text']})" if x.get("before_text") else "")
                   + f", 플래티넘 {x['platinum_text']}, 챌린저 {x['target_text']}",
                   "games": x.get("games"), "lever": x.get("lever"), "if_then": x.get("if_then")})
    for i, s in enumerate([s for s in skills if s.get("total")], 1):
        ev.append({"id": f"S{i}", "text": f"{s['title']}: 최근 {s['total']}판 중 {s['pass']}번 지킴", "games": s["total"]})
    if decisions.get("total"):
        ev.append({"id": "D1", "text": f"판단 훈련: {decisions['total']}문제 중 {decisions['good']}개가 고수와 같은 선택"
                   + (f", 상대 정글 추적 {decisions['track_total']}문제 중 {decisions['track_ok']}개 맞힘" if decisions.get("track_total") else ""),
                   "games": decisions["total"]})
    return ev


def build_weekly_prompt(gap: dict, evidence: list[dict]) -> str:
    payload = {"games": gap.get("games"), "progress_before": gap.get("progress_before"),
               "progress_now": gap.get("progress_now"), "EVIDENCE": evidence}
    return "아래 데이터만 근거로 이번 주 연습 계획을 짜줘.\n" + json.dumps(payload, ensure_ascii=False, default=str)


def build_prompt(briefing: dict) -> str:
    cards = [{"title": c["title"], "headline": c["headline"],
              "items": [{"text": i["text"], "kind": i["kind"], "evidence": i["evidence"]} for i in c["items"]]}
             for c in briefing.get("cards", [])]
    evidence = [{"id": e["id"], "text": e.get("text", ""), "n": e.get("games"), "confidence": e.get("confidence"),
                 "source": e.get("source", "")} for e in briefing.get("evidence", [])]
    payload = {
        "my_champion": briefing.get("my_champion_name"),
        "enemy_jungler": briefing.get("enemy_jungler_name") or "미확정",
        "data_scope": briefing.get("scope_label"),
        "cards": cards,
        "EVIDENCE": evidence,
    }
    return ("아래 브리핑 데이터만 근거로 이번 판 정글 운영 방향을 정리해줘.\n"
            + json.dumps(payload, ensure_ascii=False))


def parse_and_validate(text: str, valid_ids: set[str]) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("JSON 응답 없음")
    data = json.loads(m.group(0))
    points, dropped = [], 0
    for p in data.get("points") or []:
        ev = [e for e in (p.get("evidence") or []) if e in valid_ids]
        if not ev or not str(p.get("text", "")).strip():
            dropped += 1
            continue
        points.append({"phase": p.get("phase", ""), "text": p["text"].strip(), "evidence": ev})
    return {"headline": str(data.get("headline", "")).strip(), "points": points, "dropped": dropped}


class CoachError(RuntimeError):
    pass


def parse_envelope(stdout: str) -> dict | None:
    """--output-format json 의 마지막 JSON 줄 (앞에 경고 줄이 섞일 수 있음)."""
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


def explain_failure(envelope: dict | None, stderr: str = "") -> str:
    """CLI 실패 이유 + 해결 방법을 한 문장으로."""
    reason = str((envelope or {}).get("result") or "").strip() or stderr.strip()[-300:] or "알 수 없는 오류"
    status = (envelope or {}).get("api_error_status")
    low = reason.lower()
    if status == 401 or "login" in low or "/login" in low or "authenticat" in low or "api key" in low:
        hint = ("설정에서 'Claude 로그인하기'를 눌러 구독 계정으로 로그인해 주세요. "
                "ANTHROPIC_API_KEY 환경변수가 설정돼 있으면 구독 대신 그 키를 쓰니 지우세요.")
    elif "credit" in low or "balance" in low:
        hint = "API 키 결제로 실행되고 있습니다. ANTHROPIC_API_KEY 환경변수를 지우고 구독 계정으로 로그인하세요."
    elif status == 404 or "model" in low:
        hint = ".env 에 LOLDOSA_CLAUDE_MODEL=sonnet (또는 opus/haiku) 처럼 사용 가능한 모델을 지정하세요."
    elif status == 429 or "limit" in low:
        hint = "구독 사용량 한도에 걸렸습니다. 한도가 풀리면 다시 동작합니다 (카드는 계속 사용 가능)."
    elif "unknown option" in low or "unrecognized" in low:
        hint = "Claude Code 가 오래된 버전입니다. `claude update` 로 업데이트하세요."
    else:
        hint = "`uv run loldosa ai check` 로 자세히 확인하세요."
    return f"{reason} → {hint}"


from .setup import child_env


class ClaudeCoach:
    def __init__(self, model: str | None = None, timeout: float = 90.0) -> None:
        self.model = model or os.getenv("LOLDOSA_CLAUDE_MODEL", "sonnet")
        self.timeout = timeout

    @property
    def cli(self) -> str | None:
        """앱을 켠 뒤에 설치해도 바로 쓰게 매번 찾는다 (PATH 를 새로 읽지 않아도 공식 설치 위치에서 찾음)."""
        from .setup import find_claude

        return find_claude()

    _enabled: bool | None = None  # 테스트 등에서 강제로 켜고 끌 때

    @property
    def enabled(self) -> bool:
        if self._enabled is not None:
            return self._enabled
        return bool(self.cli) and os.getenv("LOLDOSA_AI", "1") != "0"

    @enabled.setter
    def enabled(self, v: bool) -> None:
        self._enabled = v

    def describe(self) -> dict:
        return {"enabled": self.enabled, "cli": self.cli, "model": self.model}

    def command(self, system: str = SYSTEM) -> list[str]:
        return [
            self.cli, "-p",
            "--output-format", "json",
            "--model", self.model,
            "--system-prompt", system,
            "--tools", "",
            "--strict-mcp-config",
            "--no-session-persistence",
        ]

    async def run_cli(self, prompt: str, system: str = SYSTEM) -> str:
        proc = await asyncio.create_subprocess_exec(
            *self.command(system),
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            env=child_env(),
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(prompt.encode("utf-8")), self.timeout)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            proc.kill()
            raise
        envelope = parse_envelope(out.decode("utf-8", "replace"))
        if envelope is None or envelope.get("is_error") or proc.returncode != 0:
            raise CoachError(explain_failure(envelope, err.decode("utf-8", "replace")))
        return envelope.get("result", "")

    async def coach_review(self, review: dict) -> dict:
        if not self.enabled:
            return {"status": "disabled", "message": "Claude가 설치돼 있지 않아요. 설정에서 'Claude 설치하기'를 눌러 주세요."}
        valid = {e["id"] for e in review.get("evidence", [])}
        try:
            text = await self.run_cli(build_review_prompt(review), system=REVIEW_SYSTEM)
            return {"status": "ok", **parse_and_validate(text, valid)}
        except asyncio.TimeoutError:
            return {"status": "error", "message": f"Claude 응답 시간 초과({self.timeout:.0f}초)"}
        except Exception as e:  # noqa: BLE001
            return {"status": "error", "message": str(e)}

    async def weekly(self, gap: dict, evidence: list[dict]) -> dict:
        if not self.enabled:
            return {"status": "disabled", "message": "Claude가 설치돼 있지 않아요. 설정에서 'Claude 설치하기'를 눌러 주세요."}
        try:
            text = await self.run_cli(build_weekly_prompt(gap, evidence), system=WEEKLY_SYSTEM)
            return {"status": "ok", **parse_and_validate(text, {e["id"] for e in evidence}), "evidence": evidence}
        except asyncio.TimeoutError:
            return {"status": "error", "message": f"Claude 응답 시간 초과({self.timeout:.0f}초)"}
        except Exception as e:  # noqa: BLE001
            return {"status": "error", "message": str(e)}

    async def coach(self, briefing: dict) -> dict:
        if not self.enabled:
            return {"status": "disabled", "message": "Claude가 설치돼 있지 않아요. 설정에서 'Claude 설치하기'를 눌러 주세요."}
        valid = {e["id"] for e in briefing.get("evidence", [])}
        try:
            text = await self.run_cli(build_prompt(briefing))
            result = parse_and_validate(text, valid)
            return {"status": "ok", **result}
        except asyncio.TimeoutError:
            return {"status": "error", "message": f"Claude 응답 시간 초과({self.timeout:.0f}초)"}
        except Exception as e:  # noqa: BLE001
            return {"status": "error", "message": str(e)}
