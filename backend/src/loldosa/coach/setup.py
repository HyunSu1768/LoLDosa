"""Claude Code 준비: 찾기 · 로그인 상태 확인 · 공식 설치 스크립트 실행 · 공식 로그인 창 띄우기.

Anthropic 약관(code.claude.com/docs/en/legal-and-compliance): 바이너리를 우리 설치 파일에 넣어 배포하려면 상업 약관 계약이
필요하고, 사용자는 Anthropic 의 공식 흐름으로 직접 로그인해야 한다(앱이 토큰을 받거나 저장하면 안 됨).
그래서 LoLDosa 는
- 바이너리를 넣지 않고, 사용자가 누르면 Anthropic 공식 설치 스크립트를 그대로 실행한다
- 로그인은 새 터미널 창에서 `claude auth login` (공식 브라우저 로그인) 을 띄울 뿐, 토큰은 건드리지 않는다
- 상태는 `claude auth status` (JSON, 종료 코드 0 = 로그인됨) 로만 확인한다
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

INSTALL_WIN = "irm https://claude.ai/install.ps1 | iex"
INSTALL_UNIX = "curl -fsSL https://claude.ai/install.sh | bash"


def find_claude() -> str | None:
    """PATH 를 새로 읽지 않아도 찾게: 환경변수 → PATH → 공식 설치 위치(~/.local/bin)."""
    if env := os.getenv("LOLDOSA_CLAUDE_CLI"):
        return env if Path(env).exists() else None
    if p := shutil.which("claude"):
        return p
    home = Path.home()
    for c in (home / ".local" / "bin" / ("claude.exe" if os.name == "nt" else "claude"),
              home / ".claude" / "local" / "claude"):
        if c.exists():
            return str(c)
    return None


def child_env() -> dict:
    """구독 로그인을 쓰도록: ANTHROPIC_API_KEY 가 있으면 -p 모드가 그 키를 먼저 써서 뺀다 (docs: authentication)."""
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    return env


def status() -> dict:
    """{installed, path, logged_in, auth_method}."""
    cli = find_claude()
    if not cli:
        return {"installed": False, "path": None, "logged_in": False, "auth_method": None}
    try:
        r = subprocess.run([cli, "auth", "status"], capture_output=True, text=True, timeout=20, env=child_env(),
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"installed": True, "path": cli, "logged_in": False, "auth_method": None, "error": str(e)}
    method = None
    try:
        method = json.loads(r.stdout or "{}").get("authMethod")
    except ValueError:
        pass
    return {"installed": True, "path": cli, "logged_in": r.returncode == 0 and method not in (None, "none"),
            "auth_method": method}


def install() -> dict:
    """Anthropic 공식 설치 스크립트를 그대로 실행 (몇십 초~몇 분)."""
    if os.name == "nt":
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", INSTALL_WIN]
    else:
        cmd = ["bash", "-lc", INSTALL_UNIX]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        out = (r.stdout + r.stderr)[-1500:]
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "log": str(e), **status()}
    st = status()
    return {"ok": st["installed"], "log": out, **st}


def open_login() -> dict:
    """새 터미널 창에서 공식 로그인(`claude auth login`)을 띄운다. 브라우저가 열리고 사용자가 직접 로그인한다."""
    cli = find_claude()
    if not cli:
        return {"ok": False, "message": "Claude가 아직 설치되지 않았어요."}
    try:
        if os.name == "nt":
            subprocess.Popen(["cmd", "/c", "start", "Claude 로그인", "cmd", "/k", cli, "auth", "login"], env=child_env())
        elif sys.platform == "darwin":
            script = f'tell application "Terminal" to do script "{cli} auth login"\ntell application "Terminal" to activate'
            subprocess.Popen(["osascript", "-e", script])
        else:
            term = shutil.which("x-terminal-emulator") or shutil.which("gnome-terminal") or shutil.which("xterm")
            if not term:
                return {"ok": False, "message": "터미널을 찾지 못했어요. 터미널에서 `claude auth login` 을 실행해 주세요."}
            subprocess.Popen([term, "-e", cli, "auth", "login"], env=child_env())
    except OSError as e:
        return {"ok": False, "message": str(e)}
    return {"ok": True, "message": "로그인 창을 열었어요. 브라우저에서 Claude 계정으로 로그인해 주세요."}
