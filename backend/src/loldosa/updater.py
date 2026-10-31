"""버튼 하나로 업데이트: GitHub Releases 최신 버전 확인 → 내려받기 → 압축 풀기 → 앱 끄고 파일 바꾸고 다시 켜기.

- 설치본(.exe / .app)에서만 동작한다. 소스로 실행 중이면 `git pull` 안내만.
- 내 데이터(통계·복기 기록·설정)는 앱 폴더가 아니라 사용자 폴더(%LOCALAPPDATA%\\LoLDosa 등)에 있어서 그대로 남는다.
- 파일 교체는 앱이 꺼진 뒤에 해야 해서(실행 중인 exe 는 덮어쓸 수 없음) 작은 스크립트를 띄우고 앱은 종료한다.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import threading
import zipfile
from pathlib import Path

import httpx

REPO = os.getenv("LOLDOSA_REPO", "HyunSu1768/LoLDosa")
API = f"https://api.github.com/repos/{REPO}/releases/latest"
ASSET = "LoLDosa-Windows.zip" if os.name == "nt" else "LoLDosa-macOS.zip"

progress: dict = {"state": "idle", "pct": 0, "message": ""}


def current_version() -> str:
    f = Path(__file__).resolve().parent / "VERSION"  # 빌드할 때 Release 태그를 적어 넣는다
    return f.read_text(encoding="utf-8").strip() if f.exists() else "dev"


def _vkey(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    except ValueError:
        return (0,)


def frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def check(timeout: float = 8.0) -> dict:
    """{current, latest, available, notes, can_apply, size}"""
    cur = current_version()
    out = {"current": cur, "latest": None, "available": False, "notes": "", "can_apply": frozen(), "size": None}
    try:
        r = httpx.get(API, timeout=timeout, headers={"Accept": "application/vnd.github+json"}, follow_redirects=True)
        r.raise_for_status()
        rel = r.json()
    except (httpx.HTTPError, ValueError) as e:
        return {**out, "error": f"업데이트를 확인하지 못했어요 ({type(e).__name__})"}
    asset = next((a for a in rel.get("assets", []) if a.get("name") == ASSET), None)
    latest = rel.get("tag_name")
    out.update(latest=latest, notes=(rel.get("body") or "")[:1500], url=asset and asset["browser_download_url"],
               size=asset and asset.get("size"))
    out["available"] = bool(asset) and cur != "dev" and _vkey(latest or "") > _vkey(cur)
    return out


def _app_root() -> Path:
    """교체할 폴더: Windows = LoLDosa.exe 가 있는 폴더, macOS = LoLDosa.app"""
    exe = Path(sys.executable).resolve()
    return exe.parents[2] if sys.platform == "darwin" else exe.parent


def _download(url: str, dst: Path, size: int | None) -> None:
    with httpx.stream("GET", url, follow_redirects=True, timeout=60) as r:
        r.raise_for_status()
        total = size or int(r.headers.get("content-length") or 0)
        done = 0
        with dst.open("wb") as f:
            for chunk in r.iter_bytes(1 << 16):
                f.write(chunk)
                done += len(chunk)
                if total:
                    progress["pct"] = int(done / total * 90)


def _swap_script(new_root: Path, app_root: Path) -> list[str]:
    """앱이 꺼질 때까지 기다렸다가 파일을 바꾸고 다시 켜는 스크립트."""
    pid = os.getpid()
    tmp = Path(tempfile.mkdtemp(prefix="loldosa_upd_"))
    if os.name == "nt":
        bat = tmp / "update.bat"
        bat.write_text(f"""@echo off
:wait
tasklist /FI "PID eq {pid}" | find "{pid}" >nul && (timeout /t 1 /nobreak >nul & goto wait)
robocopy "{new_root}" "{app_root}" /E /R:3 /W:1 /NFL /NDL /NJH /NJS /NP >nul
start "" "{app_root / 'LoLDosa.exe'}"
""", encoding="cp949", errors="replace")
        return ["cmd", "/c", "start", "", "/min", str(bat)]
    sh = tmp / "update.sh"
    sh.write_text(f"""#!/bin/bash
while kill -0 {pid} 2>/dev/null; do sleep 1; done
rm -rf "{app_root}" && ditto "{new_root}" "{app_root}"
open "{app_root}"
""", encoding="utf-8")
    sh.chmod(0o755)
    return ["/bin/bash", str(sh)]


def apply(info: dict, on_exit) -> None:
    """백그라운드에서 내려받기 → 압축 풀기 → 교체 스크립트 실행 → on_exit() 로 앱 종료."""
    def run():
        try:
            if not frozen():
                raise RuntimeError("소스로 실행 중이에요. 저장소에서 git pull 로 업데이트해 주세요.")
            if not info.get("url"):
                raise RuntimeError("이 운영체제용 파일이 Release 에 없어요.")
            progress.update(state="downloading", pct=0, message="새 버전을 내려받는 중이에요")
            work = Path(tempfile.mkdtemp(prefix="loldosa_new_"))
            z = work / ASSET
            _download(info["url"], z, info.get("size"))
            progress.update(state="extracting", pct=92, message="압축을 푸는 중이에요")
            if sys.platform == "darwin":
                subprocess.run(["ditto", "-x", "-k", str(z), str(work)], check=True)
                new_root = work / "LoLDosa.app"
            else:
                with zipfile.ZipFile(z) as f:
                    f.extractall(work)
                new_root = work / "LoLDosa"
            if not new_root.exists():
                raise RuntimeError("내려받은 파일 구조가 예상과 달라요.")
            progress.update(state="restarting", pct=100, message="다시 시작할게요")
            subprocess.Popen(_swap_script(new_root, _app_root()), close_fds=True,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            on_exit()
        except Exception as e:  # noqa: BLE001
            progress.update(state="error", message=str(e))

    progress.update(state="starting", pct=0, message="")
    threading.Thread(target=run, daemon=True).start()
