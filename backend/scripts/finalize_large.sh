#!/bin/bash
# 대량 수집 후처리: 배포 통계 + 챌린저 갭 기준표 다시 만들기
# 사용: bash scripts/finalize_large.sh <수집 data_dir> <검증 자료 dir(/tmp/val: pro·challenger 등)>
set -e
DATA=${1:-../data}; VAL=${2:-/tmp/val}; PROD=/tmp/prod_large
cd "$(dirname "$0")/.."
mkdir -p "$DATA/raw"; cp -n "$VAL"/raw/*.json.gz "$DATA/raw/" 2>/dev/null || true   # 프로·검증 경기 원본도 한곳에
rm -rf "$PROD"
.venv/bin/python scripts/build_production_stats.py "$DATA/raw" "$PROD" --min-patch 16.19 \
  apex="$DATA/matches.duckdb#apex" apex="$VAL/pro_players.json" \
  diamond="$DATA/matches.duckdb#diamond" emerald="$DATA/matches.duckdb#emerald" platinum="$DATA/matches.duckdb#platinum"
cp -r "$DATA/ddragon" "$PROD/"
LOLDOSA_DATA_DIR="$PROD" .venv/bin/loldosa analyze | tail -1 | cut -c1-120
LOLDOSA_DATA_DIR="$PROD" .venv/bin/loldosa bundle export
.venv/bin/python scripts/build_gap_reference.py "$DATA/raw" src/loldosa/learn/gap_reference.json \
  pro="$VAL/pro_players.json" challenger="$VAL/challenger_players.json" apex="$DATA/matches.duckdb#apex" \
  platinum="$DATA/matches.duckdb#platinum" emerald="$DATA/matches.duckdb#emerald" diamond="$DATA/matches.duckdb#diamond"
.venv/bin/python scripts/within_player.py "$DATA/raw" "$DATA/matches.duckdb" 6 | tail -3   # 같은 플레이어 안 비교 → 1순위 고르기
.venv/bin/python -m pytest -q | tail -1
