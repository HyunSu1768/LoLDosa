from loldosa.riot.ratelimit import SlidingWindowLimiter, parse_limits


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_parse_limits():
    assert parse_limits("20:1,100:120") == [(20, 1.0), (100, 120.0)]
    assert parse_limits(None) == []


def _fill(lim, clock, n):
    for _ in range(n):
        assert lim.wait_time() == 0
        lim._history.append(clock())


def test_short_window():
    clock = FakeClock()
    lim = SlidingWindowLimiter([(20, 1.0), (100, 120.0)], clock=clock, safety=0)
    _fill(lim, clock, 20)
    assert lim.wait_time() == 1.0
    clock.t = 1.0
    assert lim.wait_time() == 0


def test_long_window():
    clock = FakeClock()
    lim = SlidingWindowLimiter([(20, 1.0), (100, 120.0)], clock=clock, safety=0)
    for sec in range(5):
        clock.t = float(sec * 2)
        _fill(lim, clock, 20)
    clock.t = 10.0
    # 100회 다 씀 → 가장 오래된(t=0) 요청이 120초 창을 벗어날 때까지
    assert lim.wait_time() == 110.0


def test_retry_after_block():
    clock = FakeClock()
    lim = SlidingWindowLimiter([(20, 1.0)], clock=clock, safety=0)
    lim.block_for(5)
    assert lim.wait_time() == 5
