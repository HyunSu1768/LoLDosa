#!/bin/bash
# LoLDosa 실행기 (macOS): 더블클릭하면 필요한 것 설치 → 앱 실행
cd "$(dirname "$0")"
if ! command -v uv >/dev/null 2>&1; then
  echo "[LoLDosa] uv 설치 중... (처음 한 번만)"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
[ -f .env ] || { [ -f .env.example ] && cp .env.example .env; }
cd backend
echo "[LoLDosa] 준비 중... (처음엔 1~2분 걸려요)"
uv sync --extra app --quiet || { echo "[LoLDosa] 설치에 실패했어요."; read -r; exit 1; }
uv run loldosa app
