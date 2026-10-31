"""설치 파일(.exe) 진입점: 더블클릭하면 통계 묶음·챔피언 데이터 준비 후 앱 창을 띄운다."""
import sys

from loldosa.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["app"]))
