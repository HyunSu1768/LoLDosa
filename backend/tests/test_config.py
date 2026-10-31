from loldosa.config import clean_key, key_problem

GOOD = "RGAPI-12345678-abcd-ef01-2345-6789abcdef01"


def test_clean_key_strips_quotes_and_spaces():
    assert clean_key(f'  "{GOOD}"\r') == GOOD
    assert clean_key("") is None


def test_key_problem():
    assert key_problem(GOOD) is None
    assert "예시" in key_problem("RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    assert "형식" in key_problem(GOOD[:-1])
    assert key_problem(None)
