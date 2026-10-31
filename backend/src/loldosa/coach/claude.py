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
3. 표본이 적은(신뢰도 낮음) 근거는 단정하지 말고 '표본 적음'을 밝힌다.
4. 실행 가능한 행동으로 쓴다: 언제(시간대), 어디서, 무엇을. 한국어, 존댓말, 짧게.
5. 근거 문장에 없는 인과관계를 만들지 않는다. 예: 3:00 위치만 보고 몇 캠프를 돌았는지 추측하지 말고, 클리어 방식은 '완료 캠프 수' 근거로만 말한다.
6. 출력은 JSON 하나만. 다른 텍스트 금지.
형식: {"headline": "이번 판 한 줄 운영 방향", "points": [{"phase": "0-3분|3-8분|8-15분|15분+|전체", "text": "...", "evidence": ["E1"]}]}
points 는 3~6개, 시간 순서로."""


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
        hint = ("터미널에서 `claude` 를 실행해 /login 으로 구독 계정에 로그인하세요. "
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


class ClaudeCoach:
    def __init__(self, model: str | None = None, timeout: float = 90.0) -> None:
        self.cli = os.getenv("LOLDOSA_CLAUDE_CLI") or shutil.which("claude")
        self.model = model or os.getenv("LOLDOSA_CLAUDE_MODEL", "sonnet")
        self.timeout = timeout
        self.enabled = bool(self.cli) and os.getenv("LOLDOSA_AI", "1") != "0"

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

    async def coach(self, briefing: dict) -> dict:
        if not self.enabled:
            return {"status": "disabled", "message": "Claude Code CLI 가 없습니다 (설치 후 `claude` 로그인)."}
        valid = {e["id"] for e in briefing.get("evidence", [])}
        try:
            text = await self.run_cli(build_prompt(briefing))
            result = parse_and_validate(text, valid)
            return {"status": "ok", **result}
        except asyncio.TimeoutError:
            return {"status": "error", "message": f"Claude 응답 시간 초과({self.timeout:.0f}초)"}
        except Exception as e:  # noqa: BLE001
            return {"status": "error", "message": str(e)}
