"""사용자 설정 (data/settings.json): Riot ID, 챔프폭, 내 티어 버킷, AI 사용 여부."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class UserSettings:
    riot_id: str = ""  # "닉네임#KR1"
    puuid: str = ""  # riot_id 로 조회한 값 (리뷰용)
    champion_pool: list[int] = field(default_factory=list)  # 내 정글 챔프폭 (championId)
    my_bucket: str = "platinum"  # 내 티어대 데이터 버킷
    ai_enabled: bool = True
    focus_concept: str = ""  # 지금 연습 중인 개념 (learn.skills.CHECKS 의 id)
    focus_set_at: str = ""  # 목표를 정한 시각 (효과 리포트 기준점)
    target_bucket: str = "emerald"  # 비교할 '다음 티어'
    onboarded: bool = False

    @classmethod
    def load(cls, data_dir: Path) -> "UserSettings":
        p = data_dir / "settings.json"
        if not p.exists():
            return cls()
        raw = json.loads(p.read_text(encoding="utf-8"))
        known = {k: v for k, v in raw.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    def save(self, data_dir: Path) -> None:
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "settings.json").write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2),
                                                encoding="utf-8")

    def update(self, patch: dict) -> "UserSettings":
        for k, v in patch.items():
            if k in self.__dataclass_fields__:
                setattr(self, k, v)
        return self
