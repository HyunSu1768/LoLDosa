import json
import os
import stat
import sys

import pytest

from loldosa.coach import setup


@pytest.mark.skipif(sys.platform == "win32", reason="가짜 CLI 는 셸 스크립트")
def test_status_reads_auth_status(tmp_path, monkeypatch):
    fake = tmp_path / "claude"
    fake.write_text('#!/bin/sh\nif [ "$LOGGED" = 1 ]; then echo \'{"authMethod":"claude.ai"}\'; exit 0; fi\n'
                    'echo \'{"authMethod":"none"}\'; exit 1\n')
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("LOLDOSA_CLAUDE_CLI", str(fake))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-be-removed")
    monkeypatch.setenv("LOGGED", "0")
    assert setup.status() == {"installed": True, "path": str(fake), "logged_in": False, "auth_method": "none"}
    monkeypatch.setenv("LOGGED", "1")
    assert setup.status()["logged_in"] is True
    assert "ANTHROPIC_API_KEY" not in setup.child_env()  # 구독 로그인을 쓰도록


def test_not_installed(monkeypatch, tmp_path):
    monkeypatch.setenv("LOLDOSA_CLAUDE_CLI", str(tmp_path / "nope"))
    assert setup.status()["installed"] is False
    assert setup.open_login()["ok"] is False
