"""환경 설정. 레포 루트의 .env 를 읽는다 (커밋 금지)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

import sys


def _home() -> Path:
    """설정·데이터 위치. 소스 실행이면 저장소 루트, 설치 파일(.exe)이면 사용자 폴더 (LOLDOSA_HOME 로 바꿀 수 있음)."""
    if env := os.getenv("LOLDOSA_HOME"):
        return Path(env)
    if getattr(sys, "frozen", False):
        base = Path(os.getenv("LOCALAPPDATA") or Path.home() / ".local" / "share")
        return base / "LoLDosa"
    return Path(__file__).resolve().parents[3]


REPO_ROOT = _home()


KEY_RE = re.compile(r"^RGAPI-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def clean_key(raw: str | None) -> str | None:
    if not raw:
        return None
    key = raw.strip().strip("'\"").strip()
    return key or None


def key_problem(key: str | None) -> str | None:
    """키 형식 문제를 사람이 읽을 문장으로. 문제 없으면 None."""
    if not key:
        return "RIOT_API_KEY 가 비어 있습니다"
    if "xxxx" in key:
        return ".env 에 예시 값(RGAPI-xxxx…)이 그대로 있습니다"
    if not KEY_RE.match(key):
        return f"키 형식이 이상합니다 (길이 {len(key)}자, 'RGAPI-' + 36자여야 함)"
    return None


@dataclass(frozen=True)
class Settings:
    riot_api_key: str | None
    platform: str
    region: str
    locale: str
    data_dir: Path

    @property
    def env_path(self) -> Path:
        return REPO_ROOT / ".env"


def load_settings() -> Settings:
    load_dotenv(REPO_ROOT / ".env")
    data_dir = Path(os.getenv("LOLDOSA_DATA_DIR", REPO_ROOT / "data"))
    if not data_dir.is_absolute():
        data_dir = REPO_ROOT / data_dir
    return Settings(
        riot_api_key=clean_key(os.getenv("RIOT_API_KEY")),
        platform=os.getenv("RIOT_PLATFORM", "kr"),
        region=os.getenv("RIOT_REGION", "asia"),
        locale=os.getenv("LOLDOSA_LOCALE", "ko_KR"),
        data_dir=data_dir,
    )


def save_api_key(key: str, env_path: Path | None = None) -> Path:
    """설정 화면에서 받은 키를 .env 에 저장 (다른 줄은 그대로 둔다)."""
    path = env_path or (REPO_ROOT / ".env")
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    out, done = [], False
    for line in lines:
        if line.strip().startswith("RIOT_API_KEY="):
            out.append(f"RIOT_API_KEY={key}")
            done = True
        else:
            out.append(line)
    if not done:
        out.append(f"RIOT_API_KEY={key}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.environ["RIOT_API_KEY"] = key
    return path
