"""문구 점검 (토스 '잡초 제거기' 발상): 화면에 나가는 한국어 문장에서 규칙 위반을 찾는다.

규칙 (docs/DESIGN.md §3)
- 해요체: 「~습니다」「~십시오」 금지, 「되어요」→「돼요」
- 명사형 종결 금지: 문장 끝 「~함」「~음」「~됨」「~완료」「~불가」「~없음」 (예: '가져감' → '가져가요')
- 화살표로 문장 잇기 금지: 「A → B」 는 문장으로
- 보조 버튼 「취소」 금지 → 「닫기」/「다음에」
- 영어 단위 금지: min, sec
사용: python scripts/lint_copy.py [--strict]   (위반 수만큼 종료 코드)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "loldosa"
FILES = [*ROOT.glob("briefing/*.py"), *ROOT.glob("review/*.py"), *ROOT.glob("learn/skills.py"), *ROOT.glob("analysis/decisions.py"),
         *ROOT.glob("analysis/gap.py"), *ROOT.glob("app/server.py"), *ROOT.glob("lcu/livegame.py"), *ROOT.glob("app/static/js/*.js")]
RULES = [
    ("합니다체", re.compile(r"(습니다|십시오|니까\?)")),
    ("되어요", re.compile(r"되어요")),
    ("명사형 종결", re.compile(r"[가-힣](함|음|됨|완료|불가|없음|부족|요망|필요)(?=[\"'`)\]}]|\s*$|\s*\(|[.,·]\s)")),
    ("화살표 문장", re.compile(r" → ")),
    ("취소 버튼", re.compile(r"[\"'`>]취소[\"'`<]")),
    ("영어 단위", re.compile(r"\d\s?(min|sec)\b")),
]
# 받침 ㅁ 으로 끝나는 마지막 낱말 = 명사형 종결 후보 ('씀', '많음', '가져감'). 원래 ㅁ 으로 끝나는 낱말은 뺀다.
KEEP_M = {"다음", "처음", "마음", "지금", "조금", "이름", "사람", "가끔", "마침", "점", "캠", "플래티넘", "게임", "팀", "타임", "아이템", "템", "시스템", "프로그램", "카운터정글링꿈", "꿈", "범", "참", "밤", "봄", "몸", "힘", "섬", "쯤", "줌", "품", "놈", "삶", "앎", "젊"}


def m_ending(text: str) -> bool:
    for w in re.findall(r"([가-힣]+)(?=\s*(?:\(|[\"'`)\]}.,·]|$))", text):
        last = w[-1]
        code = ord(last) - 0xAC00
        if 0 <= code <= 11171 and code % 28 == 16 and w not in KEEP_M and not any(w.endswith(k) for k in KEEP_M):
            return True
    return False


STR = re.compile(r"""(f?"[^"\n]*[가-힣][^"\n]*"|`[^`]*[가-힣][^`]*`|'[^'\n]*[가-힣][^'\n]*')""")


def main() -> int:
    n = 0
    for f in FILES:
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if s.startswith(("#", "//", "/*", "*", '"""')):
                continue
            for m in STR.finditer(line):
                text = re.sub(r"다음|처음|마음|알 수 없음", "", m.group(0))  # 명사형 종결이 아닌 낱말
                if m_ending(text):
                    n += 1
                    print(f"{f.relative_to(ROOT)}:{i}: [받침ㅁ 종결] {text[:110]}")
                    continue
                for name, rx in RULES:
                    if rx.search(text):
                        n += 1
                        print(f"{f.relative_to(ROOT)}:{i}: [{name}] {text[:110]}")
    print(f"위반 {n}개")
    return min(n, 1) if "--strict" in sys.argv else 0


sys.exit(main())
