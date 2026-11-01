"""앱 실행: 로컬 서버 + 데스크톱 창(pywebview). pywebview 가 없으면 브라우저로 연다."""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

from .server import create_app


# 앱 창을 못 띄워 브라우저로 열었을 때 이유 (설정·홈에서 보여 준다)
window_error: str | None = None


def _webview2_version() -> str | None:
    """Windows: Edge WebView2 런타임 설치 버전 (없으면 None). PC마다 설치 여부가 달라요."""
    if os.name != "nt":
        return None
    import winreg

    guid = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
    keys = [(winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{guid}"),
            (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{guid}"),
            (winreg.HKEY_CURRENT_USER, rf"Software\Microsoft\EdgeUpdate\Clients\{guid}")]
    for root, path in keys:
        try:
            with winreg.OpenKey(root, path) as k:
                v = winreg.QueryValueEx(k, "pv")[0]
                if v and v != "0.0.0.0":
                    return v
        except OSError:
            continue
    return None


def window_check() -> tuple[bool, str]:
    """창을 띄우는 데 필요한 부품이 다 있는지 (창은 띄우지 않음). (가능 여부, 이유)"""
    try:
        import webview  # noqa: F401
    except ImportError as e:
        return False, f"창 라이브러리(pywebview)가 설치 파일에 없어요 ({e})"
    if os.name == "nt":
        try:
            import clr  # noqa: F401  pythonnet: Windows 창 부품을 부르는 다리
        except Exception as e:  # noqa: BLE001
            return False, f"pythonnet 을 불러오지 못했어요 ({type(e).__name__}: {e})"
        if not _webview2_version():
            return False, "이 PC에 Microsoft Edge WebView2 런타임이 없어요"
        try:
            from webview.platforms import winforms  # noqa: F401
        except Exception as e:  # noqa: BLE001
            return False, f"Windows 창 부품을 불러오지 못했어요 ({type(e).__name__}: {e})"
        return True, f"WebView2 {_webview2_version()}"
    if sys.platform == "darwin":
        try:
            from webview.platforms import cocoa  # noqa: F401
        except Exception as e:  # noqa: BLE001
            return False, f"macOS 창 부품을 불러오지 못했어요 ({type(e).__name__}: {e})"
        return True, "cocoa"
    return True, "기타 운영체제"


def free_port(preferred: int = 8765) -> int:
    for port in (preferred, 0):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1]
            except OSError:
                continue
    raise RuntimeError("사용 가능한 포트가 없습니다")


def run(replay: Path | None = None, port: int = 8765, browser: bool = False, ai: bool = True,
        replay_interval: float = 2.0) -> None:
    port = free_port(port)
    app = create_app(replay=replay, ai=ai, replay_interval=replay_interval)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    url = f"http://127.0.0.1:{port}/"

    if browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        print(f"LoLDosa: {url}  (Ctrl+C 종료)")
        server.run()
        return

    global window_error
    ok, why = window_check()
    if not ok:
        window_error = why
        print(f"앱 창을 띄우지 못해서 브라우저로 열어요: {why}")
        return run(replay, port, browser=True, ai=ai, replay_interval=replay_interval)
    import webview  # pywebview

    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    while not server.started:
        time.sleep(0.05)
    try:
        webview.create_window("LoLDosa · 정글 코치", url, width=1180, height=860, min_size=(820, 600))
        webview.start()
    except Exception as e:  # noqa: BLE001 — WebView2 가 없는 PC(PC방 등)에서는 브라우저로 연다
        window_error = f"창을 여는 중에 오류가 났어요 ({type(e).__name__}: {e})"
        print(f"앱 창을 띄우지 못해서 브라우저로 열어요: {window_error}")
        webbrowser.open(url)
        try:
            t.join()
        except KeyboardInterrupt:
            pass
    server.should_exit = True
