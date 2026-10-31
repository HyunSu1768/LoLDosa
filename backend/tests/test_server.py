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


def test_settings_and_review_endpoints(monkeypatch, tmp_path):
    monkeypatch.setenv("LOLDOSA_DATA_DIR", str(tmp_path))
    app = create_app(replay=SAMPLE, replay_interval=0.01, ai=False)
    with TestClient(app) as client:
        r = client.put("/api/settings", json={"riot_id": "test#KR1", "champion_pool": [64]})
        assert r.json()["champion_pool"] == [64]
        assert client.get("/api/settings").json()["riot_id"] == "test#KR1"
        assert client.get("/api/review/matches").json() == []
        assert client.get("/api/review/KR_1").status_code == 400
        assert isinstance(client.get("/api/champions").json(), list)


def test_home_and_focus(monkeypatch, tmp_path):
    monkeypatch.setenv("LOLDOSA_DATA_DIR", str(tmp_path))
    app = create_app(replay=SAMPLE, replay_interval=0.01, ai=False)
    with TestClient(app) as client:
        h = client.get("/api/home").json()
        assert h["onboarded"] is False and h["focus"] is None and h["skills"]
        assert client.put("/api/focus", json={"concept": "nope"}).status_code == 400
        r = client.put("/api/focus", json={"concept": "full-clear"}).json()
        assert r["focus"]["id"] == "full-clear" and r["focus"]["goal"]
        h = client.get("/api/home").json()
        assert h["onboarded"] and h["focus"]["id"] == "full-clear"
        idx = client.get("/api/learn").json()
        assert idx["concepts"] and any(c["measurable"] for c in idx["concepts"])
        c = client.get("/api/learn/full-clear").json()
        assert c["is_focus"] and c["goal"]
        assert client.post("/api/learn/full-clear/quiz", json={"correct": True}).json()["total"] == 1


def test_review_endpoint_with_personal_match(monkeypatch, tmp_path):
    """개인 경기가 있을 때 복기 API 가 핵심 배움·개념 체크까지 만들어 내는지."""
    import gzip
    import json as _json

    from loldosa.review.sync import PERSONAL_DB
    from loldosa.settings import UserSettings
    from loldosa.store.matches import MatchStore

    fx = Path(__file__).parent / "fixtures" / "match1.json.gz"
    d = _json.load(gzip.open(fx, "rt"))
    st = MatchStore(tmp_path, filename=PERSONAL_DB)
    st.ingest(d["match"], d["timeline"], "personal")
    puuid = st._x("SELECT puuid FROM participants WHERE position='JUNGLE' LIMIT 1")[0][0]
    mid = d["match"]["metadata"]["matchId"]
    st.close()
    UserSettings(puuid=puuid, riot_id="t#1", focus_concept="full-clear", onboarded=True).save(tmp_path)
    monkeypatch.setenv("LOLDOSA_DATA_DIR", str(tmp_path))
    app = create_app(replay=SAMPLE, replay_interval=0.01, ai=False)
    with TestClient(app) as client:
        rv = client.get(f"/api/review/{mid}").json()
        assert "key_lesson" in rv and isinstance(rv["checks"], list)
        for l in rv["lessons"]:
            assert all("id" in c and "title" in c for c in l["concepts"])
        assert client.get("/api/review/matches").json()[0]["match_id"] == mid
