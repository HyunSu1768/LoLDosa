"""Data Dragon: 패치 버전과 챔피언 메타데이터 (공식 정적 데이터)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import httpx

BASE = "https://ddragon.leagueoflegends.com"


@dataclass(frozen=True)
class Champion:
    id: int  # 숫자 키 (LCU/Match-V5 의 championId)
    key: str  # 영문 식별자 (e.g. "LeeSin")
    name: str  # 로케일 이름 (e.g. "리 신")
    tags: tuple[str, ...]


class ChampionIndex:
    def __init__(self, version: str, champions: dict[int, Champion]) -> None:
        self.version = version
        self._by_id = champions

    def __len__(self) -> int:
        return len(self._by_id)

    def get(self, champion_id: int) -> Champion | None:
        return self._by_id.get(champion_id)

    def name(self, champion_id: int) -> str:
        if not champion_id:
            return "-"
        c = self._by_id.get(champion_id)
        return c.name if c else f"#{champion_id}"

    @classmethod
    def from_ddragon_json(cls, payload: dict) -> "ChampionIndex":
        champs = {
            int(c["key"]): Champion(int(c["key"]), c["id"], c["name"], tuple(c.get("tags", ())))
            for c in payload["data"].values()
        }
        return cls(payload["version"], champs)


def cache_path(data_dir: Path, version: str, locale: str) -> Path:
    return data_dir / "ddragon" / version / f"champion.{locale}.json"


async def latest_version(http: httpx.AsyncClient) -> str:
    resp = await http.get(f"{BASE}/api/versions.json")
    resp.raise_for_status()
    return resp.json()[0]


async def sync_champions(data_dir: Path, locale: str = "ko_KR", version: str | None = None) -> ChampionIndex:
    """최신(또는 지정) 패치의 챔피언 목록을 받아 캐시한다."""
    async with httpx.AsyncClient(timeout=20.0) as http:
        version = version or await latest_version(http)
        path = cache_path(data_dir, version, locale)
        if not path.exists():
            resp = await http.get(f"{BASE}/cdn/{version}/data/{locale}/champion.json")
            resp.raise_for_status()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(resp.text, encoding="utf-8")
    return load_cached(data_dir, locale, version)


def load_cached(data_dir: Path, locale: str = "ko_KR", version: str | None = None) -> ChampionIndex | None:
    """캐시된 챔피언 목록 (version 미지정 시 가장 최근 것). 없으면 None."""
    root = data_dir / "ddragon"
    if version is None:
        versions = sorted(
            (p.name for p in root.glob("*") if (p / f"champion.{locale}.json").exists()),
            key=_version_key,
        ) if root.exists() else []
        if not versions:
            return None
        version = versions[-1]
    path = cache_path(data_dir, version, locale)
    if not path.exists():
        return None
    return ChampionIndex.from_ddragon_json(json.loads(path.read_text(encoding="utf-8")))


def _version_key(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split(".") if x.isdigit())
