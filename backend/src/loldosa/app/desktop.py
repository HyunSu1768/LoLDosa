"""앱 실행: 로컬 서버 + 데스크톱 창(pywebview). pywebview 가 없으면 브라우저로 연다."""

from __future__ import annotations

import socket
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

from .server import create_app


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

    try:
        import webview  # pywebview
    except ImportError:
        print("pywebview 가 없어 브라우저로 엽니다. 창으로 띄우려면: uv sync --extra app")
        return run(replay, port, browser=True, ai=ai, replay_interval=replay_interval)

    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    while not server.started:
        time.sleep(0.05)
    webview.create_window("LoLDosa · 정글 브리핑", url, width=1180, height=860, min_size=(820, 600))
    webview.start()
    server.should_exit = True
