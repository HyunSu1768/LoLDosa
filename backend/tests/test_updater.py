import httpx
import respx

from loldosa import updater


@respx.mock
def test_check_compares_versions(monkeypatch):
    monkeypatch.setattr(updater, "current_version", lambda: "v0.1.2")
    respx.get(updater.API).mock(return_value=httpx.Response(200, json={
        "tag_name": "v0.1.10", "body": "고친 것", "assets": [{"name": updater.ASSET, "browser_download_url": "https://x/y.zip", "size": 10}]}))
    info = updater.check()
    assert info["available"] is True and info["latest"] == "v0.1.10" and info["url"] == "https://x/y.zip"  # 0.1.10 > 0.1.2 (숫자 비교)


@respx.mock
def test_same_version_or_dev_not_available(monkeypatch):
    respx.get(updater.API).mock(return_value=httpx.Response(200, json={
        "tag_name": "v0.1.2", "assets": [{"name": updater.ASSET, "browser_download_url": "u"}]}))
    monkeypatch.setattr(updater, "current_version", lambda: "v0.1.2")
    assert updater.check()["available"] is False
    monkeypatch.setattr(updater, "current_version", lambda: "dev")
    assert updater.check()["available"] is False


@respx.mock
def test_check_offline():
    respx.get(updater.API).mock(side_effect=httpx.ConnectError("x"))
    assert "error" in updater.check()
