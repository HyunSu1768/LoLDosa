import httpx
import pytest

from loldosa.riot.client import RiotApiError, RiotClient


def make(handler):
    return RiotClient("RGAPI-test", transport=httpx.MockTransport(handler), max_retries=2)


async def test_routing_and_header():
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=[], headers={"X-App-Rate-Limit": "20:1,100:120"})

    async with make(handler) as riot:
        await riot.match_ids("p1", count=5)
        await riot.league_entries("PLATINUM", "I")
    assert seen[0].url.host == "asia.api.riotgames.com"
    assert seen[0].url.params["count"] == "5"
    assert seen[1].url.host == "kr.api.riotgames.com"
    assert seen[1].url.path.endswith("/RANKED_SOLO_5x5/PLATINUM/I")
    assert seen[0].headers["X-Riot-Token"] == "RGAPI-test"


async def test_retries_on_429(monkeypatch):
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"ok": True})

    async with make(handler) as riot:
        assert await riot.match("KR_1") == {"ok": True}
    assert calls["n"] == 2


async def test_404_is_none_and_403_raises():
    def handler(req):
        return httpx.Response(404 if "KR_404" in str(req.url) else 403, text="forbidden")

    async with make(handler) as riot:
        assert await riot.match("KR_404") is None
        with pytest.raises(RiotApiError) as e:
            await riot.match("KR_x")
    assert e.value.status == 403
