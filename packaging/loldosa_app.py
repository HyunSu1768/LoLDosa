"""설치 파일(.exe) 진입점: 더블클릭하면 통계 묶음·챔피언 데이터 준비 후 앱 창을 띄운다.

창 모드(.exe --windowed) 에는 콘솔이 없어 sys.stdout/stderr 가 None 이다. 그대로 print 하면 바로 죽어서,
출력은 데이터 폴더의 loldosa.log 로 보낸다 (설정 > 진단 기록 zip 에 같이 들어간다).
"""
import logging
import sys


def _redirect_output() -> None:
    if sys.stdout is not None and sys.stderr is not None:
        return
    from loldosa.config import load_settings

    data_dir = load_settings().data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    log = open(data_dir / "loldosa.log", "a", encoding="utf-8", buffering=1)  # noqa: SIM115 — 앱 종료까지 열어 둔다
    sys.stdout = sys.stdout or log
    sys.stderr = sys.stderr or log
    logging.basicConfig(stream=log, level=logging.INFO)


if __name__ == "__main__":
    _redirect_output()
    from loldosa.cli import main

    sys.exit(main(sys.argv[1:] or ["app"]))
