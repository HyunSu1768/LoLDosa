"""미리 만든 고티어 통계 묶음: API 키·수집 없이 바로 브리핑을 쓰게 한다.

저장소의 bundle/ 에 stats.duckdb.gz + manifest.json 을 넣어 두면, 앱을 처음 켤 때(또는 묶음이 더 새것일 때)
data/stats.duckdb 로 풀어 쓴다. 사용자가 직접 수집·분석한 통계가 더 새것이면 건드리지 않는다.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
import time
from pathlib import Path

MANIFEST = "manifest.json"
STATS_GZ = "stats.duckdb.gz"
LOCAL_MARK = "stats_bundle.json"  # data_dir 에 '어느 묶음을 풀었는지' 기록


def bundle_dir() -> Path | None:
    """LOLDOSA_BUNDLE → 패키지 안 bundle_data → 저장소 루트 bundle/ 순서로 찾는다."""
    cands = []
    if env := os.getenv("LOLDOSA_BUNDLE"):
        cands.append(Path(env))
    here = Path(__file__).resolve()
    cands += [here.parent / "bundle_data", here.parents[3] / "bundle"]
    return next((c for c in cands if (c / MANIFEST).exists()), None)


def export(data_dir: Path, out_dir: Path) -> dict:
    """data_dir/stats.duckdb 를 묶음으로 만든다."""
    import duckdb

    src = data_dir / "stats.duckdb"
    if not src.exists():
        raise FileNotFoundError(f"{src} 가 없어요. `loldosa analyze` 를 먼저 하세요.")
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(src), read_only=True)
    try:
        buckets = dict(con.execute("SELECT bucket, matches FROM match_totals WHERE scope = 'ALL' AND bucket <> 'all'").fetchall())
        patches = [r[0] for r in con.execute("SELECT DISTINCT scope FROM match_totals WHERE scope <> 'ALL' ORDER BY 1 DESC").fetchall()]
    except duckdb.Error:
        buckets, patches = {}, []
    finally:
        con.close()
    with src.open("rb") as f, gzip.open(out_dir / STATS_GZ, "wb", compresslevel=9) as g:
        shutil.copyfileobj(f, g)
    manifest = {"built_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "patches": patches,
                "games": {k: int(v) for k, v in buckets.items()},
                "sha256": hashlib.sha256((out_dir / STATS_GZ).read_bytes()).hexdigest()}
    (out_dir / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifest


def install(data_dir: Path, force: bool = False, bdir: Path | None = None) -> dict | None:
    """묶음이 있고, (통계가 없거나 / 묶음에서 풀었던 통계보다 묶음이 새것이면) 푼다. 푼 manifest 를 돌려준다."""
    bdir = bdir or bundle_dir()
    if not bdir:
        return None
    manifest = json.loads((bdir / MANIFEST).read_text(encoding="utf-8"))
    dst, mark = data_dir / "stats.duckdb", data_dir / LOCAL_MARK
    if dst.exists() and not force:
        if not mark.exists():
            return None  # 사용자가 직접 만든 통계 → 그대로 둔다
        prev = json.loads(mark.read_text(encoding="utf-8"))
        if prev.get("built_at", "") >= manifest["built_at"]:
            return None
    blob = (bdir / STATS_GZ).read_bytes()
    if manifest.get("sha256") and hashlib.sha256(blob).hexdigest() != manifest["sha256"]:
        raise ValueError("통계 묶음이 손상됐어요 (sha256 불일치). 저장소를 다시 받아 주세요.")
    data_dir.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp")
    tmp.write_bytes(gzip.decompress(blob))
    tmp.replace(dst)
    mark.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return manifest


def ensure_ready(data_dir: Path, locale: str = "ko_KR", say=print) -> None:
    """앱 시작 전 준비: 통계 묶음 풀기 + 챔피언 데이터(Data Dragon, 키 필요 없음) 받기."""
    try:
        m = install(data_dir)
        if m:
            say(f"고티어 통계 묶음 설치: 패치 {', '.join(m.get('patches', [])[:2])} · "
                + ", ".join(f"{k} {v}판" for k, v in m.get("games", {}).items()))
    except (OSError, ValueError) as e:
        say(f"통계 묶음 설치 실패: {e}")
    from .ddragon import load_cached

    if load_cached(data_dir, locale) is None:
        import asyncio

        from .ddragon import sync_champions

        try:
            idx = asyncio.run(sync_champions(data_dir, locale))
            say(f"챔피언 데이터 받음: 패치 {idx.version}")
        except Exception as e:  # noqa: BLE001 — 오프라인이어도 앱은 뜨게
            say(f"챔피언 데이터를 못 받았어요 ({e}). 인터넷 연결을 확인하세요.")
