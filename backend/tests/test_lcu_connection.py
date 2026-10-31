import pytest

from loldosa.lcu.connection import parse_cmdline, parse_lockfile


def test_parse_lockfile():
    c = parse_lockfile("LeagueClient:12345:54321:s3cr3t-Tok_en:https\n")
    assert (c.port, c.password, c.protocol) == (54321, "s3cr3t-Tok_en", "https")
    assert c.base_url == "https://127.0.0.1:54321"


def test_parse_lockfile_bad():
    with pytest.raises(ValueError):
        parse_lockfile("garbage")


def test_parse_cmdline_mac_style():
    args = [
        "/Applications/League of Legends.app/Contents/LoL/LeagueClient.app/Contents/Frameworks/LeagueClientUx",
        "--riotclient-auth-token=xxx",
        "--app-port=61234",
        "--remoting-auth-token=AbC-123_x",
    ]
    c = parse_cmdline(args)
    assert c and c.port == 61234 and c.password == "AbC-123_x"


def test_parse_cmdline_missing():
    assert parse_cmdline(["LeagueClientUx.exe", "--app-port=1"]) is None
