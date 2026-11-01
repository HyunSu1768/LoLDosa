from loldosa.app.dock import place

WORK = (0, 0, 1920, 1040)  # 1080p, 작업 표시줄 제외


def test_dock_right_of_client_when_space():
    # 기본 클라이언트 1280x720 을 1080p 가운데에 두면 양쪽 320px → 오른쪽에 320 폭으로 붙음
    assert place((320, 160, 1600, 880), WORK, 480) == ("right", 1600, 160, 320, 720)
    assert place((100, 0, 1820, 720), WORK, 480) is None  # 양쪽 100px: 안 붙임
    # 왼쪽에 붙여 둔 클라이언트 → 오른쪽에 붙고 높이·위치가 같다
    side, x, y, w, h = place((0, 100, 1280, 820), WORK, 480)
    assert (side, x, y, w, h) == ("right", 1280, 100, 480, 720)


def test_dock_left_when_right_is_full_and_shrinks_to_space():
    side, x, y, w, h = place((600, 0, 1920, 720), WORK, 480)
    assert side == "left" and x + w == 600 and w == 480
    side, x, y, w, h = place((0, 0, 1500, 720), WORK, 480)  # 오른쪽 420px: 그만큼만
    assert side == "right" and w == 420


def test_dock_clamps_height_to_work_area():
    _, _, y, _, h = place((0, -20, 1280, 1100), WORK, 480)
    assert y == 0 and h == 1040


def test_win32_calls_run_without_client():
    """Windows CI 에서만: 롤 클라이언트가 없을 때 tick 이 조용히 넘어가고, 모니터 작업 영역을 읽을 수 있는지."""
    import os

    import pytest

    if os.name != "nt":
        pytest.skip("Windows 전용")
    import ctypes

    from loldosa.app import dock

    d = dock.Docker("LoLDosa 테스트 없는 창")
    d.tick()
    assert dock.state["docked"] is False and dock.state["client"] is False
    l, t, r, b = d._work_area(ctypes.windll.user32.GetDesktopWindow())
    assert r > l and b > t
