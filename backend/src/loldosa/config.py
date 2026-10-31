"""환경 설정. 레포 루트의 .env 를 읽는다 (커밋 금지)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    riot_api_key: str | None
    platform: str
    region: str
    locale: str
    data_dir: Path


def load_settings() -> Settings:
    load_dotenv(REPO_ROOT / ".env")
    data_dir = Path(os.getenv("LOLDOSA_DATA_DIR", REPO_ROOT / "data"))
    if not data_dir.is_absolute():
        data_dir = REPO_ROOT / data_dir
    return Settings(
        riot_api_key=os.getenv("RIOT_API_KEY") or None,
        platform=os.getenv("RIOT_PLATFORM", "kr"),
        region=os.getenv("RIOT_REGION", "asia"),
        locale=os.getenv("LOLDOSA_LOCALE", "ko_KR"),
        data_dir=data_dir,
    )
