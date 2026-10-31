# KR 솔로랭크 프로/유명 정글러 계정 (검증용)

검증일: 2026-10-31 (Riot API, KR/asia). 기준: Account-v1으로 계정이 조회되고 **AND** 최근 솔랭(queue 420) 5판 중 3판 이상이 `teamPosition == JUNGLE`이면 verified로 본다.
기계 판독용 파일: `pro_accounts.json` (puuid, 마지막 게임 날짜, identity_confidence 포함).

## 2026 LCK 주전 정글 (출처: Sheep Esports 2026 로스터 기사, Inven Global, 한국경제)
T1 Oner / Gen.G Canyon / HLE Kanavi (Peanut 군 복무로 이탈) / KT Cuzz / DK Lucid / Kiwoom DRX Willer + Vincenzo / BNK FEARX Raptor / NS Sponge (DRX에서 이적) / HANJIN BRION GIDEON / DN SOOPers Pyosik

## 검증 통과 (verified = true)

| 선수 | 팀(2026) | Riot ID | 티어 / LP | 최근 5판 중 정글 | 마지막 게임 | 신원 확신도 | 출처 |
|---|---|---|---|---|---|---|---|
| Sponge | NS | `Sponge#gji` | CH 2635 | 5/5 | 10-30 | 중상 (이름만 일치, 태그 출처 없음) | KR 챌린저 래더 스캔 |
| Tarzan | AL (LPL) | `타 잔#KR1` | CH 2329 | 4/5 | 10-17 | 중 (이름만 일치) | KR 챌린저 래더 스캔 |
| Canyon | Gen.G | `JUGKlNG#kr` (L 자리에 소문자 l) | CH 2210 | 5/5 | 10-15 | 높음 | https://op.gg/lol/summoners/kr/JUGKlNG-kr |
| Vincenzo | Kiwoom DRX | `KRX Vincenzo#KR4` | CH 2142 | 4/5 | 10-29 | 중상 | https://op.gg/lol/spectate/list/pro-gamer?region=kr |
| Lucid | DK | `DK Lucid#KR1` | CH 2131 | 5/5 | 10-15 | 높음 | https://op.gg/summoners/kr/DK%20Lucid?hl=en_US |
| Pyosik | DN SOOPers | `DNS Pyosik#KR2` | CH 2077 | 5/5 | 10-31 | 높음 | https://op.gg/lol/summoners/kr/DNS%20Pyosik-KR2 |
| Oner | T1 | `오 너#111` | CH 2062 | 3/5 (원딜 2판) | 10-16 | 높음 (op.gg 태그 T1[Oner]) | https://op.gg/lol/summoners/kr/%EC%98%A4%20%EB%84%88-111 |
| Willer | Kiwoom DRX | `KRX Willer#KRX` | CH 1968 | 4/5 | 10-29 | 높음 | https://op.gg/lol/summoners/kr/KRX%20Willer-KRX |
| Raptor | BNK FEARX | `Raptor#KR123` | MA 1075 | 4/5 | 10-27 | 높음 | https://op.gg/lol/summoners/kr/Raptor-KR123 |
| Cuzz | KT | `Cuzz#KR1` | MA 579 | 4/5 | 10-06 | 높음 | https://op.gg/lol/summoners/kr/Cuzz-KR1 |
| Kanavi | HLE | `vinaka#KR1` | D1 75 (최고 CH 2163, 비활동 강등으로 보임) | 5/5 | 09-11 | 높음 | https://op.gg/lol/summoners/kr/vinaka-KR1 |
| Peanut | 2026 공백 (군 복무, SOOP 방송) | `Peanut#kr11` | D2 75 | 4/5 | 05-17 | 중 | https://op.gg/lol/summoners/kr/Peanut-kr11 |

op.gg 태그 정보는 2026년 op.gg 검색 결과의 스냅샷 기준이다. 이 세션에서는 op.gg, deeplol, namu, fmkorea, trackingthepros를 직접 열 수 없어서 검색 결과 요약으로만 확인했다.

## 기각 / 미발견
- `T1 Oner#KR1` (언랭), `GEN Canyon#정글킹` (언랭), `Kanavi#KR1` (에메랄드), `Cuzz#KDF` (골드), `BRO GIDEON#기드온` (실버, 탑 5/5): 사칭 계정이거나 선점된 닉네임.
- `중승민#중센조`: CH 2366이지만 최근 5판 모두 바텀이라 정글 계정이 아님. Vincenzo 본인 계정인지도 확인되지 않음.
- `Croco#0223`: CH 2401이지만 서폿 4판, 정글 1판. 정글러 Croco(LNG)의 계정인지 확인되지 않아 제외.
- 미발견(이름 변경): `Vincenzo#kr40`, `피그말리온 효과#KR2` (op.gg 태그 NS[Sponge]), `Soopsik#KR2`, `HLE Willer1#KR1`, `GIDEON#KR1`.
- **GIDEON (BRO)**: 현재 계정을 찾지 못함.

## 주의
- 사칭 닉네임이 흔하다 (`T1 Oner#КR1`처럼 키릴 문자 К를 쓴 경우 등). 이름이 아니라 puuid로 고정해서 쓸 것.
- 이번 조회에서는 Oner, Lucid, Canyon의 최근 게임이 10월 중순에 멈춰 있다 (롤드컵 기간).
