"""브리핑 데이터 모델. UI 와 LLM 모두 이 JSON 을 받는다."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Evidence:
    id: str  # "E1"
    text: str  # 사람이 읽는 근거 문장 (수치 포함)
    source: str  # 데이터 출처 라벨
    games: int | None = None  # 표본 수
    confidence: str | None = None  # 높음/보통/낮음
    url: str | None = None


@dataclass
class Item:
    text: str
    kind: str = "fact"  # fact(근거 그대로) | inference(근거에서 도출한 판단)
    evidence: list[str] = field(default_factory=list)


@dataclass
class Card:
    id: str
    title: str
    headline: str  # 요약 카드에 보이는 한 줄
    items: list[Item] = field(default_factory=list)  # 펼치면 보이는 상세

    def add(self, text: str, *evidence: str, kind: str = "fact") -> None:
        self.items.append(Item(text, kind, [e for e in evidence if e]))


@dataclass
class Recommendation:
    champion_id: int
    name: str
    score: float  # 예상 승률 (0~1)
    key: str = ""  # Data Dragon 영문 키 (아이콘)
    reasons: list[Item] = field(default_factory=list)


@dataclass
class Briefing:
    stage: str
    my_champion: int = 0
    my_champion_name: str = ""
    enemy_jungler: int = 0
    enemy_jungler_name: str = ""
    scope_label: str = ""
    notes: list[str] = field(default_factory=list)
    picks: list[Recommendation] = field(default_factory=list)
    bans: list[Recommendation] = field(default_factory=list)
    cards: list[Card] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class EvidenceLog:
    def __init__(self) -> None:
        self.items: list[Evidence] = []

    def add(self, text: str, source: str, games: int | None = None, confidence: str | None = None,
            url: str | None = None) -> str:
        eid = f"E{len(self.items) + 1}"
        self.items.append(Evidence(eid, text, source, games, confidence, url))
        return eid
