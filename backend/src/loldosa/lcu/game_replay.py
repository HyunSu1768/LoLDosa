"""지난 게임의 리플레이를 롤 클라이언트에서 열고 원하는 인게임 시각으로 이동.

(챔선 세션 녹화 재생은 `replay.py` — 이 모듈과는 별개다.)

흐름
1. LCU 접속 정보 찾기 (클라이언트가 켜져 있어야 함)
2. `Config/game.cfg` 의 `[General] EnableReplayApi=1` 보장
   - 이 설정은 *새로 뜨는* 게임/리플레이 프로세스에만 적용된다.
3. LCU 리플레이 API
   - GET  /lol-replays/v1/metadata/{gameId}          → {"state", "gameId", "downloadProgress"}
   - POST /lol-replays/v1/rofls/{gameId}/download    body {"componentType": "..."}
   - POST /lol-replays/v1/rofls/{gameId}/watch       body {"componentType": "..."}
   state 값: checking / found / download / downloading / retryDownload / watch /
             incompatible / missingOrExpired / lost / unsupported / error
4. 인게임 Replay API (https://127.0.0.1:2999, 자체 서명 인증서, 인증 없음)
   - GET  /replay/playback  → {"time", "length", "paused", "seeking", "speed"}
   - POST /replay/playback  body {"time": t, "paused": bool, "speed": 1.0}
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import os
import re
import tempfile
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, Protocol, Self

import httpx
import psutil

from .connection import (
    PROCESS_NAMES,
    LcuCredentials,
    candidate_lockfiles,
    find_credentials,
)

log = logging.getLogger(__name__)

REPLAY_API_URL = "https://127.0.0.1:2999"
# 클라이언트 매치 기록의 리플레이 버튼이 보내는 값. 이 값은 텔레메트리용 문맥이라
# 다른 문자열도 받아 주는 것으로 알려져 있지만, 클라이언트와 같은 값을 쓴다.
COMPONENT_TYPE = "replay-button_match-history"
REPLAY_BODY = {"componentType": COMPONENT_TYPE}

LEAD_IN_S = 15.0
BACKUP_SUFFIX = ".loldosa.bak"

# 바로 볼 수 있음
WATCHABLE_STATES = {"watch"}
# 내려받기를 시작해야 함 (LCU 실제 값은 "download", 일부 문서 표기는 "downloadable")
DOWNLOADABLE_STATES = {"download", "downloadable", "retryDownload"}
# 잠시 기다리면 바뀌는 상태
PENDING_STATES = {"checking", "found", "downloading"}
EXPIRED_STATES = {"missingOrExpired", "lost"}
INCOMPATIBLE_STATES = {"incompatible"}

GAME_PROCESS_NAMES = {"League of Legends.exe", "League of Legends"}
_CLIENT_PROCESS_NAMES = PROCESS_NAMES | {"LeagueClient.exe", "LeagueClient"}
_INSTALL_DIR_PREFIX = "--install-directory="
_MATCH_ID_RE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9]*_)?(\d+)$")

StatusCallback = Callable[[str], Any]


# ---------------------------------------------------------------------------
# 게임 ID
# ---------------------------------------------------------------------------


def parse_game_id(match_id: str | int) -> int:
    """Match-V5 id("KR_8439278219") 또는 숫자 → LCU 가 쓰는 숫자 gameId."""
    if isinstance(match_id, int) and not isinstance(match_id, bool):
        if match_id <= 0:
            raise ValueError(f"게임 ID 가 이상해요: {match_id!r}")
        return match_id
    m = _MATCH_ID_RE.match(str(match_id).strip())
    if not m or int(m.group(1)) <= 0:
        raise ValueError(f"게임 ID 형식이 이상해요: {match_id!r}")
    return int(m.group(1))


# ---------------------------------------------------------------------------
# 설치 폴더 / game.cfg
# ---------------------------------------------------------------------------


def _install_dir_from_cmdline(args: list[str]) -> Path | None:
    for i, arg in enumerate(args):
        arg = arg.strip('"')
        if arg.startswith(_INSTALL_DIR_PREFIX):
            value = arg[len(_INSTALL_DIR_PREFIX):].strip('"')
            # 공백이 든 경로가 따옴표 없이 여러 인자로 쪼개진 경우를 이어 붙인다.
            for rest in args[i + 1:]:
                if rest.startswith("--"):
                    break
                value += " " + rest.strip('"')
            return Path(value) if value else None
    return None


def install_dir_from_lockfile() -> Path | None:
    """롤 설치 폴더(lockfile 과 Config/ 가 있는 폴더)를 추정한다.

    Windows: C:\\Riot Games\\League of Legends
    macOS:   /Applications/League of Legends.app/Contents/LoL
    순서: LOLDOSA_LOCKFILE → 실행 중인 클라이언트의 --install-directory= → 기본 lockfile 위치.
    """
    if env := os.getenv("LOLDOSA_LOCKFILE"):
        p = Path(env)
        if p.exists():
            return p.parent
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            if proc.info["name"] in _CLIENT_PROCESS_NAMES and (d := _install_dir_from_cmdline(proc.info["cmdline"] or [])):
                return d
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    for path in candidate_lockfiles():
        if path.exists():
            return path.parent
    return None


def replay_api_config_path(install_dir: str | os.PathLike[str]) -> Path:
    """install_dir 의 game.cfg 경로. 표준은 Config/game.cfg 이고, 구버전 배치도 찾아본다."""
    base = Path(install_dir)
    candidates = [base / "Config" / "game.cfg", base / "Game" / "Config" / "game.cfg", base / "DATA" / "CFG" / "game.cfg"]
    # macOS 에서 .app 폴더를 넘긴 경우
    if base.suffix == ".app":
        candidates.insert(0, base / "Contents" / "LoL" / "Config" / "game.cfg")
    for c in candidates:
        if c.is_file():
            return c
    return candidates[0]


def _set_general_key(text: str, key: str, value: str) -> tuple[str, bool]:
    """INI 텍스트의 [General] 섹션에 key=value 를 보장. 다른 줄은 그대로 둔다."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)

    def is_section(line: str) -> bool:
        s = line.strip()
        return s.startswith("[") and s.endswith("]")

    start = next((i for i, l in enumerate(lines) if l.strip().lower() == "[general]"), None)
    if start is None:
        prefix = text
        if prefix and not prefix.endswith(("\n", "\r")):
            prefix += newline
        if prefix.strip():
            prefix += newline
        return f"{prefix}[General]{newline}{key}={value}{newline}", True

    end = next((i for i in range(start + 1, len(lines)) if is_section(lines[i])), len(lines))
    for i in range(start + 1, end):
        raw = lines[i]
        name, sep, cur = raw.partition("=")
        if sep and name.strip().lower() == key.lower():
            if cur.strip() == value:
                return text, False
            ending = raw[len(raw.rstrip("\r\n")):] or newline
            lines[i] = f"{name.strip()}={value}{ending}"
            return "".join(lines), True

    # 키가 없으면 섹션의 마지막 비어 있지 않은 줄 뒤에 넣는다.
    insert_at = end
    while insert_at - 1 > start and not lines[insert_at - 1].strip():
        insert_at -= 1
    prev = lines[insert_at - 1]
    if not prev.endswith(("\n", "\r")):
        lines[insert_at - 1] = prev + newline
    lines.insert(insert_at, f"{key}={value}{newline}")
    return "".join(lines), True


def ensure_replay_api_enabled(install_dir: str | os.PathLike[str]) -> tuple[bool, Path]:
    """game.cfg 에 EnableReplayApi=1 을 보장. (바꿨는지, 파일 경로) 를 돌려준다.

    - 원본은 처음 한 번만 game.cfg.loldosa.bak 으로 백업한다.
    - 파일이 없으면 Config 폴더가 있을 때만 새로 만든다.
    - 바뀐 설정은 새로 실행되는 게임/리플레이부터 적용된다(이미 떠 있는 게임은 재시작 필요).
    """
    path = replay_api_config_path(install_dir)
    if path.is_file():
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig", errors="surrogateescape")
    elif path.parent.is_dir():
        raw, bom, text = None, False, ""
    else:
        raise FileNotFoundError(f"롤 설정 폴더를 찾지 못했어요: {path.parent}")

    new_text, changed = _set_general_key(text, "EnableReplayApi", "1")
    if not changed:
        return False, path

    if raw is not None:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if not backup.exists():
            backup.write_bytes(raw)

    data = new_text.encode("utf-8", errors="surrogateescape")
    if bom:
        data = b"\xef\xbb\xbf" + data
    fd, tmp = tempfile.mkstemp(prefix=".game.cfg.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    log.info("EnableReplayApi=1 설정: %s", path)
    return True, path


def game_process_running() -> bool:
    """게임(또는 리플레이) 프로세스가 떠 있는지."""
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] in GAME_PROCESS_NAMES:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


# ---------------------------------------------------------------------------
# HTTP 클라이언트
# ---------------------------------------------------------------------------


class ReplayLcu(Protocol):
    async def get(self, path: str) -> Any: ...
    async def post(self, path: str, json: Any = None) -> Any: ...


def _body(resp: httpx.Response) -> Any:
    if resp.status_code == 204 or not resp.content:
        return None
    try:
        return resp.json()
    except ValueError:
        return resp.text


class LcuReplayClient:
    """리플레이 기능에 필요한 최소 LCU 클라이언트 (GET/POST)."""

    def __init__(self, creds: LcuCredentials, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._http = httpx.AsyncClient(
            base_url=creds.base_url,
            auth=("riot", creds.password),
            verify=False,
            timeout=10.0,
            transport=transport,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def get(self, path: str) -> Any:
        resp = await self._http.get(path)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return _body(resp)

    async def post(self, path: str, json: Any = None) -> Any:
        resp = await self._http.post(path, json=json)
        resp.raise_for_status()
        return _body(resp)


async def replay_state(client: ReplayLcu, game_id: int) -> dict | None:
    """GET /lol-replays/v1/metadata/{gameId}. 클라이언트가 모르는 게임이면 None."""
    data = await client.get(f"/lol-replays/v1/metadata/{game_id}")
    return data if isinstance(data, dict) else None


async def download(client: ReplayLcu, game_id: int) -> None:
    await client.post(f"/lol-replays/v1/rofls/{game_id}/download", json=REPLAY_BODY)


async def watch(client: ReplayLcu, game_id: int) -> None:
    await client.post(f"/lol-replays/v1/rofls/{game_id}/watch", json=REPLAY_BODY)


class ReplayApiClient:
    """인게임 Replay API (https://127.0.0.1:2999). 리플레이가 실행 중일 때만 응답한다."""

    def __init__(self, base_url: str = REPLAY_API_URL, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._http = httpx.AsyncClient(base_url=base_url, verify=False, timeout=5.0, transport=transport)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def playback(self) -> dict | None:
        """현재 재생 상태. 아직 리플레이가 안 떴으면 None."""
        try:
            resp = await self._http.get("/replay/playback")
        except httpx.TransportError:
            return None
        if resp.status_code != 200:
            return None
        data = _body(resp)
        return data if isinstance(data, dict) else None

    async def wait_for_replay(
        self, timeout_s: float = 90.0, poll_interval: float = 1.0, sleep: Callable[[float], Awaitable[None]] = asyncio.sleep
    ) -> dict | None:
        """Replay API 가 응답하고 리플레이 길이가 잡힐 때까지 기다린다. 시간 초과면 None."""
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_s
        while True:
            pb = await self.playback()
            if pb is not None and float(pb.get("length") or 0) > 0:
                return pb
            if loop.time() >= deadline:
                return None
            await sleep(poll_interval)

    async def seek(self, time_s: float, paused: bool = True, speed: float | None = 1.0) -> dict | None:
        body: dict[str, Any] = {"time": float(time_s), "paused": paused}
        if speed is not None:
            body["speed"] = speed
        resp = await self._http.post("/replay/playback", json=body)
        resp.raise_for_status()
        data = _body(resp)
        return data if isinstance(data, dict) else None


# 모듈 수준 편의 함수 (요구 시그니처)
async def wait_for_replay(timeout_s: float = 90.0) -> dict | None:
    async with ReplayApiClient() as api:
        return await api.wait_for_replay(timeout_s)


async def seek(time_s: float, paused: bool = True) -> dict | None:
    async with ReplayApiClient() as api:
        return await api.seek(time_s, paused=paused)


# ---------------------------------------------------------------------------
# 오케스트레이션
# ---------------------------------------------------------------------------


def _fmt_time(t: float) -> str:
    m, s = divmod(int(max(0, t)), 60)
    return f"{m}:{s:02d}"


def _ok(message: str, **extra: Any) -> dict:
    return {"status": "ok", "message": message, **extra}


def _err(message: str, **extra: Any) -> dict:
    return {"status": "error", "message": message, **extra}


MSG_NO_CLIENT = "롤 클라이언트가 켜져 있지 않아요. 클라이언트를 켜고 로그인한 뒤 다시 시도해 주세요."
MSG_EXPIRED = (
    "이 게임의 리플레이는 더 이상 받을 수 없어요. 리플레이는 현재 패치에서 한 최근 게임만 "
    "보관되고, 패치가 바뀌거나 시간이 지나면 사라져요. 다른 서버(지역) 계정의 게임도 받을 수 없어요."
)
MSG_INCOMPATIBLE = (
    "이 리플레이는 지금 게임 버전과 맞지 않아서 열 수 없어요. 리플레이는 그 게임을 한 패치에서만 "
    "재생할 수 있어서, 패치가 바뀐 뒤에는 볼 수 없어요."
)
MSG_UNSUPPORTED = "이 게임 모드는 리플레이를 지원하지 않아요."


async def open_replay_at(
    match_id: str,
    time_s: float,
    on_status: StatusCallback | None = None,
    *,
    lead_in_s: float = LEAD_IN_S,
    download_timeout_s: float = 120.0,
    replay_timeout_s: float = 90.0,
    poll_interval: float = 1.0,
    creds: LcuCredentials | None = None,
    install_dir: str | os.PathLike[str] | None = None,
    lcu: ReplayLcu | None = None,
    replay_api: ReplayApiClient | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> dict:
    """match_id 게임의 리플레이를 열고 time_s 보다 lead_in_s 초 앞에서 재생을 시작한다.

    반환: {"status": "ok"|"error", "message": "...(해요체)", ...}
    lcu / replay_api / creds / install_dir 는 테스트나 재사용을 위한 주입점이다.
    """

    async def status(msg: str) -> None:
        log.info(msg)
        if on_status is not None:
            r = on_status(msg)
            if inspect.isawaitable(r):
                await r

    try:
        game_id = parse_game_id(match_id)
    except ValueError:
        return _err(f"게임 ID 형식을 알아볼 수 없어요: {match_id}")

    own_lcu = lcu is None
    if lcu is None:
        creds = creds or find_credentials()
        if creds is None:
            return _err(MSG_NO_CLIENT)
        lcu = LcuReplayClient(creds)

    own_api = replay_api is None
    try:
        # 1) Replay API 설정
        cfg_note = ""
        cfg_dir = install_dir if install_dir is not None else install_dir_from_lockfile()
        if cfg_dir is None:
            await status("롤 설치 폴더를 못 찾아서 리플레이 API 설정은 건너뛸게요.")
        else:
            try:
                changed, cfg_path = ensure_replay_api_enabled(cfg_dir)
            except OSError as e:
                log.warning("game.cfg 수정 실패: %s", e)
                await status("리플레이 시점 이동 설정(game.cfg)을 바꾸지 못했어요. 리플레이는 열지만 시점 이동은 안 될 수 있어요.")
            else:
                if changed:
                    if game_process_running():
                        return _err(
                            "리플레이 시점 이동 설정을 켜 뒀어요. 이 설정은 새로 여는 게임부터 적용돼서, "
                            "지금 열려 있는 게임(리플레이)을 닫고 다시 시도해 주세요."
                        )
                    cfg_note = "리플레이 시점 이동 설정을 켜 뒀어요. 이번에 여는 리플레이부터 적용돼요."
                    await status(cfg_note)
                    log.info("game.cfg 갱신: %s", cfg_path)

        # 2) 메타데이터 / 다운로드
        loop = asyncio.get_running_loop()
        await status("리플레이 상태를 확인하고 있어요.")
        meta = await replay_state(lcu, game_id)
        if meta is None:
            return _err("클라이언트가 이 게임을 찾지 못했어요. 클라이언트의 전적 화면에서 이 게임을 한 번 열어 본 뒤 다시 시도해 주세요.")

        deadline = loop.time() + download_timeout_s
        download_requested = False
        last_progress = -1
        while True:
            state = str(meta.get("state") or "")
            if state in WATCHABLE_STATES:
                break
            if state in EXPIRED_STATES:
                return _err(MSG_EXPIRED, state=state)
            if state in INCOMPATIBLE_STATES:
                return _err(MSG_INCOMPATIBLE, state=state)
            if state == "unsupported":
                return _err(MSG_UNSUPPORTED, state=state)
            if state == "error":
                return _err("클라이언트에서 리플레이를 받다가 오류가 났어요. 잠시 뒤 다시 시도해 주세요.", state=state)
            if state in DOWNLOADABLE_STATES and (not download_requested or state == "retryDownload"):
                await status("리플레이를 내려받기 시작할게요.")
                await download(lcu, game_id)
                download_requested = True
            elif state == "downloading":
                progress = int(meta.get("downloadProgress") or 0)
                if progress != last_progress:
                    last_progress = progress
                    await status(f"리플레이를 내려받는 중이에요... {progress}%")
            if loop.time() >= deadline:
                return _err("리플레이 내려받기가 너무 오래 걸려요. 클라이언트 전적 화면에서 상태를 확인하고 다시 시도해 주세요.", state=state)
            await sleep(poll_interval)
            meta = await replay_state(lcu, game_id) or {}

        # 3) 리플레이 실행
        await status("리플레이를 여는 중이에요. 게임 화면이 뜰 때까지 잠시 기다려 주세요.")
        await watch(lcu, game_id)

        if replay_api is None:
            replay_api = ReplayApiClient()
        pb = await replay_api.wait_for_replay(replay_timeout_s, poll_interval=poll_interval, sleep=sleep)
        if pb is None:
            return _err(
                "리플레이는 열었지만 시점 이동 기능에 연결하지 못했어요. 리플레이가 뜨면 직접 "
                f"{_fmt_time(time_s)} 근처로 이동해 주세요."
            )

        target = max(0.0, float(time_s) - lead_in_s)
        length = float(pb.get("length") or 0)
        if length > 0:
            target = min(target, max(0.0, length - 1.0))
        await replay_api.seek(target, paused=False)
        msg = f"리플레이를 {_fmt_time(target)}부터 재생할게요. ({_fmt_time(time_s)} 장면 {int(lead_in_s)}초 전)"
        if cfg_note:
            msg = f"{cfg_note} {msg}"
        await status(msg)
        return _ok(msg, game_id=game_id, seek_time=target)
    except httpx.TransportError:
        return _err("롤 클라이언트와 연결이 끊겼어요. 클라이언트가 켜져 있는지 확인하고 다시 시도해 주세요.")
    except httpx.HTTPStatusError as e:
        log.warning("리플레이 요청 실패: %s", e)
        return _err(f"클라이언트가 리플레이 요청을 거절했어요 (HTTP {e.response.status_code}). 게임 중이거나 업데이트 중이면 끝난 뒤 다시 시도해 주세요.")
    finally:
        if own_lcu and isinstance(lcu, LcuReplayClient):
            await lcu.aclose()
        if own_api and replay_api is not None:
            await replay_api.aclose()
