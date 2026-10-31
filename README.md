# LoLDosa

정글러를 위한 챔피언 선택 브리핑 도구. 기획: [docs/SPEC.md](docs/SPEC.md)

현재 단계: **M0 (기반)** — Riot API 클라이언트, 챔피언 데이터, 롤 클라이언트(LCU) 챔선 감시 CLI.

## 설치 (macOS / Windows 공통)

Python 3.11+ 와 [uv](https://docs.astral.sh/uv/) 가 필요합니다.

```bash
# macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
git clone https://github.com/HyunSu1768/LoLDosa.git
cd LoLDosa
cp .env.example .env          # Windows: copy .env.example .env
# .env 의 RIOT_API_KEY 에 developer.riotgames.com 에서 받은 키 입력

cd backend
uv sync --extra dev
```

이후 명령은 `backend/` 폴더에서 `uv run loldosa ...` 로 실행합니다.

## 테스트 순서

```bash
uv run loldosa doctor            # 환경 점검
uv run loldosa ddragon sync      # 최신 패치 챔피언 데이터 (한국어 이름)
uv run loldosa riot check        # API 키 확인: KR 챌린저 → 경기 1개 타임라인

# 게임 없이: 샘플 챔선 재생
uv run loldosa lcu watch --replay samples/champselect_ranked_jungle.jsonl

# 롤 클라이언트 켜고
uv run loldosa lcu status        # 접속 확인 (소환사명, 현재 단계)
uv run loldosa lcu watch         # 챔선 들어가면 픽/밴이 바뀔 때마다 출력
uv run loldosa lcu watch --record data/my_champselect.jsonl   # 실제 챔선 녹화
uv run pytest                    # 단위 테스트
```

### 클라이언트를 못 찾을 때

실행 중인 `LeagueClientUx` 프로세스를 먼저 찾고, 없으면 기본 설치 경로의 `lockfile` 을 읽습니다.

- macOS: `/Applications/League of Legends.app/Contents/LoL/lockfile`
- Windows: `C:\Riot Games\League of Legends\lockfile`

다른 곳에 설치했다면 `.env` 에 `LOLDOSA_LOCKFILE=<lockfile 경로>` 를 추가하세요.

## 주의

- `.env` 는 커밋하지 않습니다 (`.gitignore` 처리됨).
- Riot 개발용 키는 24시간마다 만료됩니다. `riot check` 가 401/403 이면 재발급하세요.
