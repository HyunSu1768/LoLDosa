from loldosa.analysis.items import FALLBACK, can_buy, gold_as_items, gold_diff_say


def test_gold_as_items_ladder():
    assert gold_diff_say(80) == "거의 같아요"
    assert gold_diff_say(420) == "우리가 롱소드 1개쯤 앞서요"
    assert gold_diff_say(-700) == "우리가 롱소드 2개쯤 밀려요"
    assert gold_as_items(1300)["text"] == "B.F. 대검 1개쯤"
    assert gold_as_items(2000)["text"] == "B.F. 대검 1개 반쯤"
    assert gold_as_items(6000, FALLBACK)["text"] == "완성 아이템 2개쯤"


def test_can_buy():
    assert can_buy(759) == "롱소드 2개를 살 수 있어요"
    assert can_buy(100) == "아직 롱소드도 못 사요"
    assert can_buy(1700).startswith("B.F. 대검을 살 수 있어요")
