# LoLDosa

정글러를 위한 챔피언 선택 브리핑 도구. 챔피언 선택 화면을 실시간으로 읽고,
직접 수집·분석한 고티어 경기 데이터와 프로 대회 기록, 전문가 가이드를 근거로
픽/밴 추천과 게임 운영 브리핑을 보여줍니다. 기획: [docs/SPEC.md](docs/SPEC.md)

```
챔피언 선택(LCU) ─▶ 브리핑 엔진 ─▶ 앱 창: 추천 픽/밴 · 동선 · 갱 · 적 정글 · 오브젝트 · 조합 · 프로/가이드
                        ▲                  └▶ AI 코치(Claude 구독): 근거 ID 가 달린 문장만 표시
통계 DB ◀─ 분석 ◀─ 수집(Riot API 타임라인) + 프로 대회(Leaguepedia) + 가이드(영상 자막/글)
```

모든 문장에는 근거 칩(`E3 n=120`)이 붙습니다. 마우스를 올리면 원래 수치, 표본 수, 출처가 보이고,
표본이 적으면 판단을 내리지 않고 "표본 부족"으로 표시합니다.

## 설치 (Windows / macOS 공통)

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
uv sync --extra app --extra kb   # app: 데스크톱 창, kb: 유튜브 자막
```

AI 코치와 가이드 추출을 쓰려면 [Claude Code](https://code.claude.com) 를 설치하고 터미널에서 `claude` 를 한 번 실행해
구독 계정으로 로그인해 두세요. API 키는 필요 없습니다.

이후 명령은 모두 `backend/` 폴더에서 `uv run loldosa ...` 로 실행합니다.

## 매일 쓰는 법

```bash
uv run loldosa update      # 패치 데이터 갱신 → 경기 수집 → 프로 기록 → 통계 집계 (게임 안 할 때)
uv run loldosa app         # 브리핑 창 실행 → 롤에서 랭크 챔피언 선택에 들어가면 자동 브리핑
```

- `update` 는 중단해도 다음에 이어서 합니다. 개인 키 한도상 시간당 약 1,500경기까지 받을 수 있습니다.
  기본값은 버킷(마스터+ / 플래티넘)마다 최대 300경기이며 `--max-matches 1000` 처럼 늘릴 수 있습니다.
- 수집 중에는 통계 파일이 잠기지 않도록 `update` 가 끝난 뒤 `app` 을 쓰는 걸 권장합니다
  (`app` 은 집계가 끝난 `stats.duckdb` 만 읽습니다).
- 창 대신 브라우저로 보려면 `uv run loldosa app --browser`, AI 코치를 끄려면 `--no-ai`.

### 전문가 가이드 추가 (선택)

```bash
uv run loldosa guides search "리신 정글 강의" "킨드레드 정글 공략" --max 3
uv run loldosa guides add https://www.youtube.com/watch?v=XXXXXXXXXXX
uv run loldosa guides add-text my_guide.txt --url https://... --title "가이드 제목"
uv run loldosa -v guides list    # -v: 주장까지 출력
```

Claude 가 자막/글에서 조언을 뽑을 때 **원문 인용**을 같이 뽑게 하고, 그 인용이 원문에 실제로 없으면 버립니다.
영상은 인용 위치의 타임스탬프 링크가 근거로 남습니다.

## 게임 없이 테스트

```bash
uv run loldosa app --replay samples/champselect_ranked_jungle.jsonl   # 녹화된 챔선 재생
uv run loldosa lcu watch --record data/my_champselect.jsonl          # 내 실제 챔선 녹화
uv run pytest
```

## 명령 모음

| 명령 | 설명 |
|---|---|
| `doctor` | 키, Claude Code, 롤 클라이언트, 데이터 상태 점검 |
| `ddragon sync` | 최신 패치 챔피언 데이터 |
| `riot check` | API 키 동작 확인 |
| `collect` | 경기·타임라인 수집 (`--bucket apex platinum`, `--max-matches`, `--days`) |
| `pro sync` | Leaguepedia 프로 대회 정글 기록 (`--days 90`) |
| `analyze` | 수집 데이터 → 통계 DB |
| `update` | 위 과정을 한 번에 |
| `app` | 브리핑 앱 |
| `guides search/add/add-text/list` | 전문가 가이드 지식 베이스 |
| `lcu status/watch` | 롤 클라이언트 연결 확인, 챔선 콘솔 출력 |

### 클라이언트를 못 찾을 때

실행 중인 `LeagueClientUx` 프로세스를 먼저 찾고, 없으면 기본 설치 경로의 `lockfile` 을 읽습니다.

- macOS: `/Applications/League of Legends.app/Contents/LoL/lockfile`
- Windows: `C:\Riot Games\League of Legends\lockfile`

다른 곳에 설치했다면 `.env` 에 `LOLDOSA_LOCKFILE=<lockfile 경로>` 를 추가하세요.

## 데이터의 한계 (브리핑을 읽을 때)

- **동선**: 타임라인은 1분 간격 위치만 제공합니다. 시작 캠프는 1:00 위치에서 가장 가까운 캠프, 초반 동선은 3:00 위치로 분류합니다.
- **갱**: 킬로 이어지지 않은 갱 시도는 기록에 남지 않습니다. 갱 통계는 "8분 이전 라인에서 처음 킬이 난 갱" 기준입니다.
- **프로 대회**: 공개 데이터에 위치 정보가 없어 픽·승률·오브젝트 수만 씁니다.
- **승률**: 표본이 적은 값은 50% 쪽으로 보정한 값(보정 승률)을 같이 보여주며, 표본 15경기 미만이면 판단하지 않습니다.

## 주의

- `.env` 와 `data/` 는 커밋하지 않습니다.
- Riot 개발용 키는 24시간마다 만료됩니다. 개인 키(Personal API Key)를 신청하면 만료가 없습니다.
- 개인용 도구입니다. Claude 구독 로그인은 본인 PC 의 Claude Code 를 통해서만 사용합니다.
