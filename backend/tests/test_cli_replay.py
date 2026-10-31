from pathlib import Path

from loldosa.cli import main

SAMPLE = Path(__file__).parents[1] / "samples" / "champselect_ranked_jungle.jsonl"


def test_replay_runs(capsys):
    assert main(["lcu", "watch", "--replay", str(SAMPLE), "--interval", "0"]) == 0
    out = capsys.readouterr().out
    assert "전원 확정" in out
    assert "◀ 나" in out
    assert "챔피언 선택 종료" in out
