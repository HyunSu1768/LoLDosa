"""목표 판 수까지 티어를 돌아가며 수집 (끊겨도 다시 실행하면 이어서).

사용: python scripts/collect_target.py apex=4000 diamond=2000 emerald=2000 platinum=2000 [--days 30]
한 번에 버킷당 최대 300판씩 받고 다음 버킷으로 넘어가서, 중간에 멈춰도 티어별로 고르게 쌓인다.
"""
import subprocess
import sys
import time

import duckdb

from loldosa.config import load_settings

args = [a for a in sys.argv[1:] if "=" in a]
days = sys.argv[sys.argv.index("--days") + 1] if "--days" in sys.argv else "30"
targets = {k: int(v) for k, v in (a.split("=") for a in args)}
db = load_settings().data_dir / "matches.duckdb"


def counts() -> dict:
    con = duckdb.connect(str(db), read_only=True)
    try:
        return dict(con.execute("SELECT bucket, count(*) FROM matches GROUP BY 1").fetchall())
    finally:
        con.close()


stall: dict[str, int] = {}
while True:
    c = counts()
    left = {b: t - c.get(b, 0) for b, t in targets.items() if c.get(b, 0) < t and stall.get(b, 0) < 3}
    print(time.strftime("%H:%M"), "현재", {b: c.get(b, 0) for b in targets}, flush=True)
    if not left:
        break
    for b in left:
        before = counts().get(b, 0)
        subprocess.run([sys.executable, "-m", "loldosa.cli", "collect", "--bucket", b, "--players", "80",
                        "--per-player", "20", "--days", days, "--max-matches", "300"])
        got = counts().get(b, 0) - before
        stall[b] = stall.get(b, 0) + 1 if got == 0 else 0  # 세 번 연속 0판이면 그 버킷은 멈춤
        print(f"  {b}: +{got}", flush=True)
print("완료", counts(), flush=True)
