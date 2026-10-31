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

## 화면 구성 — 학습 루프

LoLDosa 는 **연습 목표 하나 → 게임 전 브리핑 → 경기 복기 → 개념 학습**을 반복하도록 짜여 있습니다.

- **홈**: 지금 연습 중인 목표, 최근 경기에서 그 목표를 지켰는지(✓/✗ 점), 경기 기록으로 잰 **실력 지도**(개념별 달성률),
  다음에 할 일. 처음 켜면 Riot ID → 첫 목표를 고르는 안내가 나옵니다.
- **게임 전 브리핑**: 챔피언 선택 중 자동 갱신. 맨 위에 **이번 판 연습 목표**, 그 아래 **이번 판 플랜**(시작·첫 갱·주의·오브젝트·턴).
  줄마다 **왜?**를 누르면 관련 개념 설명이 그 자리에서 펼쳐집니다. 챔선이 끝나도 로딩 화면 동안 유지됩니다.
- **경기 복기**: `닉네임#태그`로 경기를 불러오면 자동 분석. 경기마다 **이 경기에서 하나만 배운다면**(핵심 피드백 + 개념),
  **개념 체크**(풀클리어·귀환 타이밍·오브젝트 준비·트래킹 등 9개를 경기 기록으로 판정), 그 밖의 피드백, AI 복기,
  10분 동선 미니맵. "다음 판 연습 목표로" 버튼으로 루프가 이어집니다.
- **개념 학습**: 60개 개념(라인·웨이브·턴 / 정글 / 오브젝트·시야 / 교전·조합 / 중후반 운영 / 실력 향상).
  정의·이렇게 하세요·정글러라면·자주 하는 실수·확인 퀴즈·2026 수치(패치·미검증 표시)·출처. 🎯 표시는 경기로 측정되는 개념입니다.
- 화면 곳곳의 점선 밑줄 용어(풀클리어, 우선권, 귀환 …)에 마우스를 올리면 설명이, 누르면 개념 페이지가 열립니다.
- **설정**: Riot ID, 챔프폭(추천 픽이 이 안에서), 비교 티어(기본 플래티넘), AI 사용 여부.

개념 내용은 `reports/롤 핵심 개념 학습 자료.md`, `reports/롤 턴 개념과 정글 운영.md` 리서치에서 왔습니다(검색 결과 기반, 미검증 수치는 표시).

## 실력을 올리는 장치들

- **그 순간으로 돌아가기 (판단 훈련)**: 경기 복기에서 내 판단 지점(죽기 30초 전, 상대 정글 갱 직전, 오브젝트 1분 전, 3:00)을
  그 시각의 미니맵·상황과 함께 문제로 냅니다. 먼저 고르고 나면, 비슷한 상황의 고티어 정글러 60명이 다음 1분에 무엇을 했고
  2분 뒤 팀 골드·데스·오브젝트가 어땠는지 보여줍니다. 틀린 장면은 '오늘의 복습'으로 다시 나옵니다.
- **리플레이로 이 장면 보기**: 롤 클라이언트에서 그 경기 리플레이를 받아 해당 시각 15초 전으로 이동합니다.
  처음 한 번 `game.cfg` 에 `EnableReplayApi=1` 을 켜고(원본은 `game.cfg.loldosa.bak` 로 백업) 리플레이를 엽니다.
  리플레이는 최근 경기·현재 패치만 받을 수 있어요.
- **비교 기준 셋**: 복기 비교표에서 이번 판 / 내 최근 평균 / 다음 티어(설정, 기본 에메랄드) / 고티어를 함께 봅니다.
  다음 티어 칸은 그 티어 경기를 모아야 채워집니다 (`update` 기본값에 에메랄드 포함).
- **숙련도·오늘의 복습**: 개념마다 경기 체크·판단 훈련·퀴즈를 합친 숙련도(0~100). 틀린 장면과 약한 개념은
  1·2·4·8·16일 간격으로 다시 나옵니다.
- **효과 리포트**: 연습 목표를 정한 날 전후로 목표 지킨 비율·승률·랭크 변화를 비교합니다(경기를 불러올 때 랭크를 기록).
- **1분 이미지 트레이닝**: 챔피언 선택 중 고티어 실제 한 판의 첫 6분 동선(풀캠 / 4~5캠프 / 3캠 갱)과 상대 정글의
  대표 동선을 미니맵으로 재생합니다.

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
| `reprocess` | 보관된 원본으로 경기 테이블 재생성 (저장 항목이 늘어난 업데이트 후 1회) |
| `ai check` | Claude Code 구독 호출 확인 |
| `review '닉네임#태그'` | 내 최근 경기 리뷰를 터미널에 출력 (`--count`, `--show`) |
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
