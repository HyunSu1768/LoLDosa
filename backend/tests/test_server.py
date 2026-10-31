from pathlib import Path

from fastapi.testclient import TestClient

from loldosa.app.server import create_app

SAMPLE = Path(__file__).parents[1] / "samples" / "champselect_ranked_jungle.jsonl"


def test_ws_streams_briefing(monkeypatch, tmp_path):
    monkeypatch.setenv("LOLDOSA_DATA_DIR", str(tmp_path))
    app = create_app(replay=SAMPLE, replay_interval=0.01, ai=False)
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        st = client.get("/api/status").json()
        assert st["replay"] and st["ai"]["enabled"] is False
        with client.websocket_connect("/ws") as ws:
            msg = ws.receive_json()
            while msg["type"] != "briefing":
                msg = ws.receive_json()
            assert msg["state"]["allies"] and "briefing" in msg
