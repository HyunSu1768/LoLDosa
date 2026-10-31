"""LCU(롤 클라이언트 로컬 API) 접속 정보 찾기. Windows / macOS 지원.

1순위: 실행 중인 LeagueClientUx 프로세스의 인자(--app-port, --remoting-auth-token)
2순위: 설치 폴더의 lockfile ("name:pid:port:password:protocol")
환경변수 LOLDOSA_LOCKFILE 로 lockfile 경로를 직접 지정할 수도 있다.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import psutil

PROCESS_NAMES = {"LeagueClientUx.exe", "LeagueClientUx"}

DEFAULT_LOCKFILES = {
    # PC방·개인 PC 에서 흔한 위치: 드라이브 C~G × (Riot Games, Games\Riot Games, Program Files\Riot Games)
    "win32": [Path(f"{d}:\\{base}\\League of Legends\\lockfile")
              for d in "CDEFG" for base in ("Riot Games", "Games\\Riot Games", "Program Files\\Riot Games", "Riot")],
    "darwin": [
        Path("/Applications/League of Legends.app/Contents/LoL/lockfile"),
        Path.home() / "Applications/League of Legends.app/Contents/LoL/lockfile",
    ],
}

_PORT_RE = re.compile(r"--app-port=(\d+)")
_TOKEN_RE = re.compile(r"--remoting-auth-token=([\w-]+)")


@dataclass(frozen=True)
class LcuCredentials:
    port: int
    password: str
    protocol: str = "https"

    @property
    def base_url(self) -> str:
        return f"{self.protocol}://127.0.0.1:{self.port}"


def parse_lockfile(text: str) -> LcuCredentials:
    parts = text.strip().split(":")
    if len(parts) != 5:
        raise ValueError(f"lockfile 형식이 이상합니다: {text!r}")
    _name, _pid, port, password, protocol = parts
    return LcuCredentials(int(port), password, protocol)


def parse_cmdline(args: list[str]) -> LcuCredentials | None:
    joined = " ".join(args)
    port, token = _PORT_RE.search(joined), _TOKEN_RE.search(joined)
    if port and token:
        return LcuCredentials(int(port.group(1)), token.group(1))
    return None


def from_process() -> LcuCredentials | None:
    """클라이언트 프로세스 인자에서 포트·토큰. 관리자 권한으로 도는 롤이면 인자를 못 읽으므로, 실행 파일 위치의 lockfile 도 본다."""
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            if proc.info["name"] not in PROCESS_NAMES and proc.info["name"] not in ("LeagueClient.exe", "LeagueClient"):
                continue
            if creds := parse_cmdline(proc.info["cmdline"] or []):
                return creds
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        try:
            lock = Path(proc.exe()).parent / "lockfile"
            if lock.exists():
                return parse_lockfile(lock.read_text())
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError, ValueError):
            continue
    return None


def candidate_lockfiles() -> list[Path]:
    paths = []
    if env := os.getenv("LOLDOSA_LOCKFILE"):
        paths.append(Path(env))
    paths += DEFAULT_LOCKFILES.get(sys.platform, [])
    return paths


def from_lockfile() -> LcuCredentials | None:
    for path in candidate_lockfiles():
        if path.exists():
            return parse_lockfile(path.read_text())
    return None


def find_credentials() -> LcuCredentials | None:
    """클라이언트가 안 켜져 있으면 None. LOLDOSA_LOCKFILE 이 있으면 그걸 우선한다."""
    if os.getenv("LOLDOSA_LOCKFILE"):
        return from_lockfile() or from_process()
    return from_process() or from_lockfile()
