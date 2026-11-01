"""롤 클라이언트 창 바깥쪽에 붙어서 따라다니기 (Windows).

- 롤 클라이언트(LeagueClientUx, 창 클래스 RCLIENT) 창을 찾아서, 오른쪽에 자리가 있으면 오른쪽, 없으면 왼쪽에 붙인다.
  높이는 클라이언트와 같게. 양쪽 다 자리가 없으면(클라이언트가 화면을 꽉 채우면) 붙이지 않고 그대로 둔다.
- 0.3초마다 위치를 보고, 클라이언트를 움직이면 같이 움직인다. 클라이언트가 최소화·숨김(게임 중)이면 건드리지 않는다.
- 클라이언트가 맨 앞으로 오면 우리 창도 바로 그 위로 올린다(포커스는 뺏지 않음). 붙어 있어서 겹치지는 않는다.
- 좌표는 전부 실제 화면 픽셀(물리 픽셀). pywebview(WinForms)는 DPI 인식 모드라 GetWindowRect 값과 단위가 같다.
- 사용자가 우리 창을 직접 끌어서 클라이언트에서 떼어 놓으면 따라가기를 멈춘다(다시 붙이려면 설정 또는 창을 클라이언트 옆에 놓기).
"""

from __future__ import annotations

import ctypes
import logging
import os
import threading
import time
from ctypes import wintypes

log = logging.getLogger(__name__)

DOCK_WIDTH = 480  # 논리 픽셀 (화면 배율을 곱해서 씀). 좁은 화면 레이아웃(≤600px)이 이 폭에 맞춰져 있어요
MIN_SPACE = 300  # 이보다 자리가 좁으면 붙이지 않음 (1080p 가운데 1280 클라이언트면 양쪽 320px)
GAP = 0
DETACH_PX = 40  # 우리 창이 예상 자리에서 이만큼 넘게 벗어나 있으면 사용자가 뗀 것으로 봄

state: dict = {"enabled": True, "docked": False, "side": None, "detached": False, "client": False}


def _rect_t():
    return wintypes.RECT()


def _visible_rect(u32, dwm, hwnd) -> tuple[int, int, int, int] | None:
    """창의 실제 보이는 테두리 (Windows 10+ 의 투명 리사이즈 테두리 제외)."""
    r = _rect_t()
    if dwm is not None and dwm.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(r), ctypes.sizeof(r)) == 0:  # DWMWA_EXTENDED_FRAME_BOUNDS
        return r.left, r.top, r.right, r.bottom
    if u32.GetWindowRect(hwnd, ctypes.byref(r)):
        return r.left, r.top, r.right, r.bottom
    return None


def place(client: tuple[int, int, int, int], work: tuple[int, int, int, int], width: int) -> tuple[str, int, int, int, int] | None:
    """클라이언트 옆 자리 계산 (순수 함수, 테스트용). 반환: (side, x, y, w, h) — 보이는 테두리 기준."""
    cl, ct, cr, cb = client
    wl, wt, wr, wb = work
    right, left = wr - cr - GAP, cl - wl - GAP
    min_space = min(MIN_SPACE, width)
    if right >= min_space:
        side, w = "right", min(width, right)
        x = cr + GAP
    elif left >= min_space:
        side, w = "left", min(width, left)
        x = cl - GAP - w
    else:
        return None
    y = max(ct, wt)
    h = min(cb, wb) - y
    return side, x, y, w, h


class Docker:
    def __init__(self, title: str) -> None:
        self.title = title
        self.u32 = ctypes.windll.user32  # type: ignore[attr-defined]
        try:
            self.dwm = ctypes.windll.dwmapi  # type: ignore[attr-defined]
        except OSError:
            self.dwm = None
        # 64비트에서 창 핸들이 int 로 잘리지 않게 인자·반환 타입을 명시
        u, H, P = self.u32, wintypes.HWND, ctypes.c_void_p
        u.FindWindowW.argtypes, u.FindWindowW.restype = [wintypes.LPCWSTR, wintypes.LPCWSTR], H
        u.GetForegroundWindow.argtypes, u.GetForegroundWindow.restype = [], H
        u.IsWindowVisible.argtypes = u.IsIconic.argtypes = [H]
        u.GetWindowRect.argtypes = [H, P]
        u.SetWindowPos.argtypes = [H, H, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
        u.MonitorFromWindow.argtypes, u.MonitorFromWindow.restype = [H, wintypes.DWORD], wintypes.HMONITOR
        u.GetMonitorInfoW.argtypes = [wintypes.HMONITOR, P]
        if hasattr(u, "GetDpiForWindow"):
            u.GetDpiForWindow.argtypes, u.GetDpiForWindow.restype = [H], wintypes.UINT
        if self.dwm is not None:
            self.dwm.DwmGetWindowAttribute.argtypes = [H, wintypes.DWORD, P, wintypes.DWORD]
        self.last_target = None
        self.was_front = False

    def _client(self):
        h = self.u32.FindWindowW("RCLIENT", "League of Legends")
        if not h or not self.u32.IsWindowVisible(h) or self.u32.IsIconic(h):
            return None
        return h

    def _work_area(self, hwnd) -> tuple[int, int, int, int]:
        class MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

        mon = self.u32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        self.u32.GetMonitorInfoW(mon, ctypes.byref(mi))
        w = mi.rcWork
        return w.left, w.top, w.right, w.bottom

    def tick(self) -> None:
        me = self.u32.FindWindowW(None, self.title)
        cl = self._client()
        state["client"] = bool(cl)
        if not me or not cl or not state["enabled"]:
            state["docked"] = False
            return
        crect = _visible_rect(self.u32, self.dwm, cl)
        mrect = _visible_rect(self.u32, self.dwm, me)
        if not crect or not mrect:
            return
        # 사용자가 우리 창을 끌어서 뗐는지: 지난번 놓은 자리에서 크게 벗어났고, 클라이언트는 그대로일 때
        if self.last_target and not state["detached"]:
            tx, ty = self.last_target[1], self.last_target[2]
            if (abs(mrect[0] - tx) > DETACH_PX or abs(mrect[1] - ty) > DETACH_PX) and crect == self.last_target[5]:
                state["detached"] = True
                state["docked"] = False
                log.info("dock: 사용자가 창을 떼어 놓아서 따라가기를 멈춰요")
        if state["detached"]:
            return
        scale = self.u32.GetDpiForWindow(cl) / 96 if hasattr(self.u32, "GetDpiForWindow") else 1.0
        spot = place(crect, self._work_area(cl), int(DOCK_WIDTH * scale))
        if not spot:
            state["docked"] = False
            return
        side, x, y, w, h = spot
        # 보이는 테두리 → 실제 창 사각형 (투명 테두리 두께만큼 보정)
        r = _rect_t()
        self.u32.GetWindowRect(me, ctypes.byref(r))
        bl, bt, br, bb = mrect[0] - r.left, mrect[1] - r.top, r.right - mrect[2], r.bottom - mrect[3]
        target = (side, x, y, w, h, crect)
        if target[:5] != (self.last_target or (None,))[:5] or (mrect[0], mrect[1], mrect[2] - mrect[0], mrect[3] - mrect[1]) != (x, y, w, h):
            SWP_NOZORDER, SWP_NOACTIVATE = 0x0004, 0x0010
            self.u32.SetWindowPos(me, None, x - bl, y - bt, w + bl + br, h + bt + bb, SWP_NOZORDER | SWP_NOACTIVATE)
        self.last_target = target
        state.update(docked=True, side=side)
        # 클라이언트가 맨 앞으로 오면 우리 창도 그 바로 위로 (포커스는 그대로)
        front = self.u32.GetForegroundWindow() == cl
        if front and not self.was_front:
            HWND_TOP, SWP_NOMOVE, SWP_NOSIZE, SWP_NOACTIVATE = 0, 0x0002, 0x0001, 0x0010
            self.u32.SetWindowPos(me, HWND_TOP, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)
        self.was_front = front


def start(title: str, enabled: bool = True) -> None:
    """앱 창이 뜬 뒤 호출. Windows 가 아니면 아무것도 안 함."""
    state["enabled"] = enabled
    if os.name != "nt":
        return

    def loop():
        try:
            d = Docker(title)
        except Exception as e:  # noqa: BLE001
            log.warning("dock: 시작 실패 %s", e)
            return
        while True:
            try:
                d.tick()
            except Exception as e:  # noqa: BLE001
                log.debug("dock tick: %s", e)
            time.sleep(0.3)

    threading.Thread(target=loop, daemon=True, name="dock").start()


def set_enabled(on: bool) -> None:
    state["enabled"] = on
    if on:
        state["detached"] = False  # 다시 켜면 바로 붙인다
