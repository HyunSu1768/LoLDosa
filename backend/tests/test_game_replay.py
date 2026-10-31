import json

import httpx
import pytest

from loldosa.lcu import game_replay as gr
from loldosa.lcu.connection import LcuCredentials

CREDS = LcuCredentials(54321, "pw")


# --- game id ---------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [("KR_8439278219", 8439278219), ("EUW1_7000000001", 7000000001), ("8439278219", 8439278219), (123, 123), (" NA1_5 ", 5)],
)
def test_parse_game_id(raw, expected):
    assert gr.parse_game_id(raw) == expected


@pytest.mark.parametrize("raw", ["", "KR_", "KR_abc", "KR-123", "_123", 0, "KR_0"])
def test_parse_game_id_bad(raw):
    with pytest.raises(ValueError):
        gr.parse_game_id(raw)


# --- install dir -------------------------------------------------------------


def test_install_dir_from_cmdline():
    args = ["LeagueClientUx.exe", "--app-port=1", r"--install-directory=C:\Riot Games\League of Legends", "--x=1"]
    assert str(gr._install_dir_from_cmdline(args)) == r"C:\Riot Games\League of Legends"
    split = ["LeagueClientUx", "--install-directory=/Applications/League", "of", "Legends.app/Contents/LoL", "--y"]
    assert str(gr._install_dir_from_cmdline(split)) == "/Applications/League of Legends.app/Contents/LoL"
    assert gr._install_dir_from_cmdline(["LeagueClientUx.exe"]) is None


def test_install_dir_from_env_lockfile(tmp_path, monkeypatch):
    lock = tmp_path / "lockfile"
    lock.write_text("LeagueClient:1:2:pw:https")
    monkeypatch.setenv("LOLDOSA_LOCKFILE", str(lock))
    assert gr.install_dir_from_lockfile() == tmp_path


# --- game.cfg ----------------------------------------------------------------


def _cfg(tmp_path, text: str | None, newline="\n"):
    d = tmp_path / "Config"
    d.mkdir()
    p = d / "game.cfg"
    if text is not None:
        p.write_bytes(text.replace("\n", newline).encode())
    return p


def test_cfg_existing_key_zero_to_one(tmp_path):
    p = _cfg(tmp_path, "[General]\nWindowMode=2\nEnableReplayApi=0\nCfgVersion=1\n\n[HUD]\nScale=0.5\n", "\r\n")
    changed, path = gr.ensure_replay_api_enabled(tmp_path)
    assert changed and path == p
    assert p.read_bytes() == b"[General]\r\nWindowMode=2\r\nEnableReplayApi=1\r\nCfgVersion=1\r\n\r\n[HUD]\r\nScale=0.5\r\n"
    backup = p.with_name("game.cfg.loldosa.bak")
    assert b"EnableReplayApi=0" in backup.read_bytes()


def test_cfg_missing_key_inserted_in_general(tmp_path):
    p = _cfg(tmp_path, "[General]\nWindowMode=2\n\n[HUD]\nScale=0.5\n")
    assert gr.ensure_replay_api_enabled(tmp_path)[0]
    assert p.read_text() == "[General]\nWindowMode=2\nEnableReplayApi=1\n\n[HUD]\nScale=0.5\n"


def test_cfg_missing_section(tmp_path):
    p = _cfg(tmp_path, "[HUD]\nScale=0.5")
    assert gr.ensure_replay_api_enabled(tmp_path)[0]
    assert p.read_text() == "[HUD]\nScale=0.5\n\n[General]\nEnableReplayApi=1\n"


def test_cfg_missing_file_created(tmp_path):
    p = _cfg(tmp_path, None)
    assert gr.ensure_replay_api_enabled(tmp_path) == (True, p)
    assert p.read_text() == "[General]\nEnableReplayApi=1\n"
    assert not p.with_name("game.cfg.loldosa.bak").exists()


def test_cfg_no_config_dir(tmp_path):
    with pytest.raises(FileNotFoundError):
        gr.ensure_replay_api_enabled(tmp_path / "nope")


def test_cfg_idempotent_and_backup_once(tmp_path):
    p = _cfg(tmp_path, "\ufeff[General]\nEnableReplayApi=0\n")
    assert gr.ensure_replay_api_enabled(tmp_path)[0]
    after = p.read_bytes()
    assert after.startswith(b"\xef\xbb\xbf") and b"EnableReplayApi=1" in after
    assert gr.ensure_replay_api_enabled(tmp_path) == (False, p)
    assert p.read_bytes() == after
    # 사용자가 다시 0 으로 바꿔도 백업은 최초 원본 그대로
    p.write_text("[General]\nEnableReplayApi=0\nX=1\n")
    assert gr.ensure_replay_api_enabled(tmp_path)[0]
    assert p.with_name("game.cfg.loldosa.bak").read_bytes() == b"\xef\xbb\xbf[General]\nEnableReplayApi=0\n"


def test_cfg_case_insensitive_and_spaces(tmp_path):
    p = _cfg(tmp_path, "[general]\nenablereplayapi = 1\n")
    assert gr.ensure_replay_api_enabled(tmp_path) == (False, p)


def test_cfg_path_mac_app_bundle(tmp_path):
    app = tmp_path / "League of Legends.app"
    cfg = app / "Contents" / "LoL" / "Config"
    cfg.mkdir(parents=True)
    (cfg / "game.cfg").write_text("[General]\n")
    assert gr.replay_api_config_path(app) == cfg / "game.cfg"


# --- LCU client --------------------------------------------------------------


async def test_lcu_replay_client_requests():
    seen = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append((req.method, req.url.path, req.content, req.headers.get("authorization")))
        if req.method == "GET":
            return httpx.Response(200, json={"state": "watch", "gameId": 1, "downloadProgress": 0})
        return httpx.Response(204)

    async with gr.LcuReplayClient(CREDS, transport=httpx.MockTransport(handler)) as c:
        assert (await gr.replay_state(c, 1))["state"] == "watch"
        assert await gr.download(c, 1) is None
        await gr.watch(c, 1)
    assert [s[:2] for s in seen] == [
        ("GET", "/lol-replays/v1/metadata/1"),
        ("POST", "/lol-replays/v1/rofls/1/download"),
        ("POST", "/lol-replays/v1/rofls/1/watch"),
    ]
    assert json.loads(seen[1][2]) == {"componentType": "replay-button_match-history"}
    assert seen[0][3].startswith("Basic ")


# --- orchestration -----------------------------------------------------------


class FakeLcu:
    def __init__(self, states):
        self.states = list(states)
        self.calls = []

    async def get(self, path):
        self.calls.append(("GET", path))
        st = self.states.pop(0) if len(self.states) > 1 else self.states[0]
        return st if st is None else {"gameId": 8439278219, **st}

    async def post(self, path, json=None):
        self.calls.append(("POST", path, json))


def replay_api_mock(boot_polls=2, length=1800.0):
    state = {"gets": 0, "posts": []}

    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "GET":
            state["gets"] += 1
            if state["gets"] <= boot_polls:
                raise httpx.ConnectError("not up yet")
            return httpx.Response(200, json={"time": 0.0, "length": length, "paused": False, "seeking": False, "speed": 1.0})
        state["posts"].append(json.loads(req.content))
        return httpx.Response(200, json={"time": 0.0, "length": length})

    return gr.ReplayApiClient(transport=httpx.MockTransport(handler)), state


async def _nosleep(_):
    return None


@pytest.fixture
def cfg_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(gr, "game_process_running", lambda: False)
    _cfg(tmp_path, "[General]\nEnableReplayApi=0\n")
    return tmp_path


async def test_open_replay_happy_path_with_download(cfg_dir):
    lcu = FakeLcu([
        {"state": "checking"},
        {"state": "download"},
        {"state": "downloading", "downloadProgress": 40},
        {"state": "downloading", "downloadProgress": 90},
        {"state": "watch"},
    ])
    api, api_state = replay_api_mock()
    statuses = []
    res = await gr.open_replay_at(
        "KR_8439278219", 600, statuses.append,
        lcu=lcu, replay_api=api, install_dir=cfg_dir, poll_interval=0, sleep=_nosleep,
    )
    assert res["status"] == "ok", res
    assert res["seek_time"] == 585.0 and "9:45" in res["message"]
    posts = [c for c in lcu.calls if c[0] == "POST"]
    assert posts == [
        ("POST", "/lol-replays/v1/rofls/8439278219/download", gr.REPLAY_BODY),
        ("POST", "/lol-replays/v1/rofls/8439278219/watch", gr.REPLAY_BODY),
    ]
    assert api_state["posts"] == [{"time": 585.0, "paused": False, "speed": 1.0}]
    assert any("40%" in s for s in statuses) and any("90%" in s for s in statuses)
    assert any("설정" in s for s in statuses)  # game.cfg 를 새로 켰다는 안내
    assert "EnableReplayApi=1" in (cfg_dir / "Config" / "game.cfg").read_text()
    await api.aclose()


async def test_open_replay_already_watchable_clamps_lead_in(cfg_dir):
    lcu = FakeLcu([{"state": "watch"}])
    api, api_state = replay_api_mock(boot_polls=0)

    async def on_status(_):  # async 콜백도 지원
        return None

    res = await gr.open_replay_at("KR_1", 5, on_status, lcu=lcu, replay_api=api, install_dir=cfg_dir, poll_interval=0, sleep=_nosleep)
    assert res["status"] == "ok"
    assert api_state["posts"][0]["time"] == 0.0
    assert not any("download" in c[1] for c in lcu.calls)
    await api.aclose()


@pytest.mark.parametrize("state", ["missingOrExpired", "lost"])
async def test_open_replay_missing_or_expired(cfg_dir, state):
    lcu = FakeLcu([{"state": state}])
    api, api_state = replay_api_mock()
    res = await gr.open_replay_at("KR_8439278219", 600, lcu=lcu, replay_api=api, install_dir=cfg_dir, sleep=_nosleep)
    assert res["status"] == "error"
    assert "패치" in res["message"]
    assert [c for c in lcu.calls if c[0] == "POST"] == []
    assert api_state["posts"] == [] and api_state["gets"] == 0
    await api.aclose()


async def test_open_replay_incompatible(cfg_dir):
    res = await gr.open_replay_at("KR_1", 60, lcu=FakeLcu([{"state": "incompatible"}]), install_dir=cfg_dir, sleep=_nosleep)
    assert res["status"] == "error" and "버전" in res["message"]


async def test_open_replay_download_timeout(cfg_dir):
    lcu = FakeLcu([{"state": "downloading", "downloadProgress": 1}])
    res = await gr.open_replay_at(
        "KR_1", 60, lcu=lcu, install_dir=cfg_dir, download_timeout_s=0, poll_interval=0, sleep=_nosleep
    )
    assert res["status"] == "error" and "오래" in res["message"]


async def test_open_replay_api_never_comes_up(cfg_dir):
    api, _ = replay_api_mock(boot_polls=10**9)
    res = await gr.open_replay_at(
        "KR_1", 125, lcu=FakeLcu([{"state": "watch"}]), replay_api=api, install_dir=cfg_dir,
        replay_timeout_s=0, poll_interval=0, sleep=_nosleep,
    )
    assert res["status"] == "error" and "2:05" in res["message"]
    await api.aclose()


async def test_open_replay_cfg_changed_while_game_running(cfg_dir, monkeypatch):
    monkeypatch.setattr(gr, "game_process_running", lambda: True)
    lcu = FakeLcu([{"state": "watch"}])
    res = await gr.open_replay_at("KR_1", 60, lcu=lcu, install_dir=cfg_dir, sleep=_nosleep)
    assert res["status"] == "error" and "닫고" in res["message"]
    assert lcu.calls == []


async def test_open_replay_no_client(monkeypatch):
    monkeypatch.setattr(gr, "find_credentials", lambda: None)
    res = await gr.open_replay_at("KR_1", 60)
    assert res == {"status": "error", "message": gr.MSG_NO_CLIENT}


async def test_open_replay_bad_match_id():
    res = await gr.open_replay_at("garbage", 60)
    assert res["status"] == "error"


async def test_open_replay_unknown_game(cfg_dir):
    res = await gr.open_replay_at("KR_1", 60, lcu=FakeLcu([None]), install_dir=cfg_dir, sleep=_nosleep)
    assert res["status"] == "error" and "전적" in res["message"]


async def test_open_replay_with_real_lcu_client_over_mock_transport(cfg_dir):
    """LcuReplayClient + MockTransport 로 HTTP 계층까지 통과시키는 경로 (204 응답 포함)."""
    states = iter(["download", "downloading", "watch"])
    current = {"s": next(states)}

    def handler(req: httpx.Request) -> httpx.Response:
        if req.method == "GET":
            s = current["s"]
            current["s"] = next(states, "watch")
            return httpx.Response(200, json={"state": s, "gameId": 42, "downloadProgress": 50})
        return httpx.Response(204)

    lcu = gr.LcuReplayClient(CREDS, transport=httpx.MockTransport(handler))
    api, api_state = replay_api_mock(boot_polls=1)
    res = await gr.open_replay_at("KR_42", 100, lcu=lcu, replay_api=api, install_dir=cfg_dir, poll_interval=0, sleep=_nosleep)
    assert res["status"] == "ok" and api_state["posts"][0]["time"] == 85.0
    await lcu.aclose()
    await api.aclose()
