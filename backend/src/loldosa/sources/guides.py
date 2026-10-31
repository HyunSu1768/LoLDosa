"""전문가 가이드 지식 추출: 유튜브 강의 자막 / 가이드 글 → (주장 + 원문 인용 + 출처) 지식 베이스.

환각 방지
- Claude 는 원문에서 '그대로 옮긴 인용(quote)'과 함께 주장을 뽑는다.
- 인용이 원문에 실제로 있는지 확인하고(공백·문장부호 무시), 없으면 버린다.
- 영상은 인용 위치의 타임스탬프 링크를 출처로 남긴다.
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, urlparse

import duckdb
import httpx

TOPICS = ("route", "gank", "matchup", "objective", "teamfight", "general")
TOPIC_KO = {"route": "동선", "gank": "갱킹", "matchup": "매치업", "objective": "오브젝트",
            "teamfight": "한타", "general": "운영"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS guide_sources (
    source_id VARCHAR PRIMARY KEY, kind VARCHAR, url VARCHAR, title VARCHAR, author VARCHAR,
    language VARCHAR, added_at TIMESTAMP, text_chars INTEGER
);
CREATE TABLE IF NOT EXISTS guide_claims (
    claim_id VARCHAR PRIMARY KEY, source_id VARCHAR, champion_id INTEGER, vs_champion_id INTEGER,
    topic VARCHAR, text VARCHAR, quote VARCHAR, start_s DOUBLE, url VARCHAR, extracted_at TIMESTAMP
);
"""

EXTRACT_SYSTEM = """너는 리그 오브 레전드 정글 강의 내용을 정리하는 편집자다.
주어진 원문(자막 또는 글)에서 정글 플레이에 바로 쓸 수 있는 구체적인 조언만 뽑는다.
규칙:
1. 원문에 실제로 있는 내용만. 너의 지식으로 보충하지 않는다.
2. 각 항목에 원문을 '그대로 복사한' 인용(quote, 10~200자)을 넣는다. 요약하거나 고쳐 쓰지 않는다.
3. champion 은 조언이 해당하는 정글 챔피언의 영어 이름(모든 챔피언 공통이면 null), vs 는 상대 챔피언 영어 이름(없으면 null).
4. topic: route(동선/시작) | gank(갱킹) | matchup(상대 정글) | objective(오브젝트) | teamfight(한타) | general(운영)
5. text 는 한국어 한 문장 요약.
출력은 JSON 하나만: {"claims": [{"champion": "Lee Sin", "vs": null, "topic": "route", "text": "...", "quote": "..."}]}"""


@dataclass
class SourceDoc:
    kind: str  # youtube | text
    url: str
    title: str
    author: str
    language: str
    text: str
    # 자막: (start_s, text) 목록 — 인용 위치의 타임스탬프를 찾는 데 씀
    segments: list[tuple[float, str]] | None = None

    @property
    def source_id(self) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, self.url))


def squash(s: str) -> str:
    return re.sub(r"[\s\W_]+", "", s.lower())


def youtube_id(url: str) -> str:
    u = urlparse(url)
    if u.hostname and "youtu.be" in u.hostname:
        return u.path.strip("/")
    q = parse_qs(u.query)
    if "v" in q:
        return q["v"][0]
    m = re.search(r"/(shorts|embed|live)/([\w-]{6,})", u.path)
    if m:
        return m.group(2)
    if re.fullmatch(r"[\w-]{11}", url):
        return url
    raise ValueError(f"유튜브 영상 ID 를 찾을 수 없습니다: {url}")


async def youtube_meta(video_id: str) -> tuple[str, str]:
    async with httpx.AsyncClient(timeout=15) as http:
        r = await http.get("https://www.youtube.com/oembed",
                           params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"})
    if r.status_code == 200:
        d = r.json()
        return d.get("title", video_id), d.get("author_name", "")
    return video_id, ""


async def load_youtube(url: str, languages=("ko", "en")) -> SourceDoc:
    from youtube_transcript_api import YouTubeTranscriptApi

    vid = youtube_id(url)
    fetched = await asyncio.to_thread(lambda: YouTubeTranscriptApi().fetch(vid, languages=list(languages)))
    segments = [(s.start, s.text) for s in fetched.snippets]
    title, author = await youtube_meta(vid)
    return SourceDoc("youtube", f"https://www.youtube.com/watch?v={vid}", title, author,
                     fetched.language_code, " ".join(t for _, t in segments), segments)


def load_text(path: Path, url: str, title: str, author: str = "", language: str = "ko") -> SourceDoc:
    return SourceDoc("text", url, title, author, language, path.read_text(encoding="utf-8"))


async def search_youtube(query: str, limit: int = 5) -> list[str]:
    """API 키 없이 검색 결과 페이지에서 영상 ID 를 뽑는다."""
    async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "ko,en"}) as http:
        r = await http.get(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    ids: list[str] = []
    for vid in re.findall(r'"videoId":"([\w-]{11})"', r.text):
        if vid not in ids:
            ids.append(vid)
        if len(ids) >= limit:
            break
    return ids


def chunks(doc: SourceDoc, size: int = 12000) -> list[str]:
    text = doc.text
    return [text[i:i + size] for i in range(0, len(text), size)] or [""]


def locate(doc: SourceDoc, quote: str) -> tuple[bool, float | None]:
    """인용이 원문에 있는지, 자막이면 시작 시각(초)."""
    q = squash(quote)
    if len(q) < 6 or q not in squash(doc.text):
        return False, None
    if not doc.segments:
        return True, None
    # 인용 앞부분이 처음 나오는 자막 조각
    head = q[:12]
    acc = ""
    for start, t in doc.segments:
        acc += squash(t)
        if head in acc:
            return True, start
    return True, doc.segments[0][0]


class GuideKB:
    def __init__(self, data_dir: Path) -> None:
        self.path = data_dir / "guides.duckdb"
        data_dir.mkdir(parents=True, exist_ok=True)

    def connect(self, read_only: bool = False):
        con = duckdb.connect(str(self.path), read_only=read_only)
        if not read_only:
            con.execute(SCHEMA).fetchall()
        return con

    def has_source(self, url: str) -> bool:
        if not self.path.exists():
            return False
        con = self.connect()
        try:
            return bool(con.execute("SELECT 1 FROM guide_sources WHERE url=?", [url]).fetchall())
        finally:
            con.close()

    def save(self, doc: SourceDoc, claims: list[dict]) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        con = self.connect()
        try:
            con.execute("DELETE FROM guide_claims WHERE source_id=?", [doc.source_id]).fetchall()
            con.execute("INSERT OR REPLACE INTO guide_sources VALUES (?,?,?,?,?,?,?,?)",
                        [doc.source_id, doc.kind, doc.url, doc.title, doc.author, doc.language, now,
                         len(doc.text)]).fetchall()
            for c in claims:
                con.execute("INSERT INTO guide_claims VALUES (?,?,?,?,?,?,?,?,?,?)", [
                    str(uuid.uuid4()), doc.source_id, c["champion_id"], c["vs_champion_id"], c["topic"],
                    c["text"], c["quote"], c["start_s"], c["url"], now]).fetchall()
        finally:
            con.close()


def validate_claims(doc: SourceDoc, raw: list[dict], name_to_id) -> tuple[list[dict], int]:
    ok, dropped = [], 0
    for c in raw:
        quote = str(c.get("quote") or "")
        found, start = locate(doc, quote)
        topic = c.get("topic") if c.get("topic") in TOPICS else "general"
        if not found or not str(c.get("text") or "").strip():
            dropped += 1
            continue
        url = doc.url + (f"&t={int(start)}s" if start is not None and doc.kind == "youtube" else "")
        ok.append({
            "champion_id": name_to_id(c.get("champion")) if c.get("champion") else 0,
            "vs_champion_id": name_to_id(c.get("vs")) if c.get("vs") else 0,
            "topic": topic, "text": c["text"].strip(), "quote": quote.strip(), "start_s": start, "url": url,
        })
    return ok, dropped


async def extract(doc: SourceDoc, coach, name_to_id, say=print) -> tuple[list[dict], int]:
    """coach: ClaudeCoach (run_cli 사용). 원문을 나눠서 추출하고 인용 검증."""
    all_claims, dropped = [], 0
    parts = chunks(doc)
    for i, part in enumerate(parts, 1):
        say(f"  추출 {i}/{len(parts)}…")
        prompt = (f"출처: {doc.title} ({doc.author})\n원문:\n<<<\n{part}\n>>>")
        text = await coach.run_cli(prompt, system=EXTRACT_SYSTEM)
        m = re.search(r"\{.*\}", text, re.S)
        raw = json.loads(m.group(0)).get("claims", []) if m else []
        ok, d = validate_claims(doc, raw, name_to_id)
        all_claims += ok
        dropped += d
    return all_claims, dropped
