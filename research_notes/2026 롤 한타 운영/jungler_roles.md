# 정글러의 한타 역할: 챔피언 분류별 역할과 조합에 따른 한타 플랜 (2026 시즌)

> 조사 환경 메모: 이번 세션에서는 웹 페이지 본문(WebFetch)이 막혀 있었다(wiki.leagueoflegends.com, blog.loltheory.gg 둘 다 ENOTFOUND, 세션 네트워크 허용 목록 밖). 그래서 웹 출처는 **검색 결과 요약/스니펫**으로만 확인했다. 대신 1차 데이터는 직접 확인했다:
> (a) 로컬 Data Dragon 파일 `data/ddragon/16.21.1/champion.ko_KR.json`(Riot 공식 정적 데이터, 최신 패치),
> (b) 로컬 수집 경기 원본 `data/raw/*.json.gz`(KR 서버 match-v5, 4,616판 중 앞 1,500판의 JUNGLE 포지션 참가자 집계). 아래에서 "[로컬 DDragon]", "[로컬 match-v5]"로 표시했다. 로컬 데이터의 티어 구성은 이번에 따로 확인하지 못했다(duckdb 모듈이 없어 DB 조회 실패).

## 1. 정글 분류별 한타 역할: 할 일, 서는 위치, 들어가는 타이밍, 노릴 대상, 흔한 실수 (와 그 이유)

### Takeaway
분류마다 한타 일이 다르다. 탱커 이니시는 "먼저 들어가 묶고 그다음 필링", 다이버/브루저는 "아군 이니시나 적 핵심 CC가 빠진 뒤 후방 진입", 암살자는 "시야 밖 측면에서 기다리다 고립되거나 빈사인 딜러를 마무리", AP/메이지는 "광역 CC·딜을 시야 밖 각에서 꽂기", 캐리/스커미셔는 "앞에서부터 녹이고(front-to-back) 적 CC가 빠진 뒤 정리". 모든 분류가 공통으로 기준 삼는 것은 **적의 핵심 쿨다운(CC/필링)이 빠졌는가**와 **아군이 따라 들어올 수 있는가**다.

### Cited Findings
**공식 분류 정의 (위키, 검색 스니펫)**
- 공식 LoL 위키는 Vanguard·Warden을 Tank 아래에, Juggernaut·Diver를 Fighter 아래에 둔다. Vanguard 강점: 내구력·이니시·묶기 / 약점: 기동성·디스인게이지·사거리. Warden 강점: 내구력·아군 보호·디스인게이지 / 약점: 기동성·딜. Diver 강점: 딜·기동성·이니시, "우선순위 대상을 골라 무는 데" 특화. Juggernaut는 딜과 탱킹을 모두 하지만 거리를 좁히기 어렵다. 분류 카테고리에는 Vanguard 15명, Warden 7명, Diver 19명, Juggernaut 14명이 있다 — [LoL Wiki: Category:Champions by class](https://wiki.leagueoflegends.com/en-us/Category:Champions_by_class), [LoL Wiki: Tank](https://wiki.leagueoflegends.com/en-us/Champion_classes/Tank), [LoL Wiki: Diver](https://wiki.leagueoflegends.com/en-us/Diver) (본문은 막혀 있어 검색 요약으로만 확인)

**탱커 이니시 정글 (세주아니/자크/아무무/람머스/마오카이)**
- 2026 탱커 가이드는 탱커를 잘하려면 한타 흐름을 읽고 쿨다운에 맞춰 이니시 타이밍을 잡으며, 이니시와 필링 중 무엇을 할지 고르는 것이 핵심이라고 한다 — [dodge.gg Tank Guide (2026)](https://www.dodge.gg/en-US/lol/news/tank-guide-2026)
- 하드 이니시(대상을 묶어 팀이 딜 쿨다운을 쏟을 수 있게 함)와 소프트 이니시(팀이 위치를 바꾸거나 쫓아가야 함)는 다르다. 흔한 실수: **버스트 없이 회복 조합에 하드 이니시** — 적 백라인이 소라카/소나/유미이고 아군 딜이 지속 딜이면, 회복이 묶어 둔 시간을 흡수해 버린다 — [LoLTheory: Engage & Disengage](https://blog.loltheory.gg/engage-disengage-lol/)
- 자크: E로 진입 → Q·W로 묶기 → R로 마무리, 적을 뭉쳐 R 효과를 키우고 백라인을 흔드는 것이 기본 콤보. 다른 가이드는 "캐리를 물어 묶고, 풀콤보를 쓴 뒤 필링으로 전환"하라고 한다. 자크 R은 이니시와 필링 둘 다에 쓰인다 — [metabot.gg Zac guide](https://metabot.gg/tr_TR/league/guides/Zac)(검색 요약)
- 세주아니: R은 게임에서 손꼽히는 이니시 궁극기로, 주 대상을 기절시키고 주변을 둔화시킨다. Q 돌진은 처음 맞은 챔피언에서 멈추므로 대상 앞에 다른 챔피언이 있으면 백라인까지 못 간다 — [Strafe: How to Play Sejuani](https://www.strafe.com/news/read/winters-wrath-how-to-play-sejuani-in-league-of-legends/), [metabot.gg Sejuani](https://metabot.gg/en/league/champion/Sejuani/guide). 2017년 빌드 가이드의 규칙(오래된 자료): "궁은 맞힐 수 있는 우선 대상에게만, 아니면 아군 백라인이 무너질 때까지 아껴라. 탱커·서폿에게 쓰지 마라" — [MOBAFire Sejuani 7.16 guide](https://www.mobafire.com/league-of-legends/build/7-16-stoneborn-mastery-op-420171) **(오래된 자료)**
- 일반 한타 가이드: 탱커는 적 백라인을 흔들고 스킬을 최대한 받아내 아군 딜러가 맞지 않게 하는 역할이다 — [Hotspawn: How To Teamfight](https://www.hotspawn.com/league-of-legends/guide/how-to-teamfight-in-league-of-legends)
- 한국 공략: 아무무는 광역 CC로 한타를 무너뜨리는 돌격형 탱커 정글로, 적 진영 한가운데로 뛰어들어 여러 명을 함께 묶는 것이 기본 진입. 람머스는 강한 물리 방어로 적 원딜을 무력화하고 기동성으로 기습 이니시를 거는 탱커 정글. 람머스 공략은 아군 옆에서 스킬을 아꼈다가 들어오는 적을 떼어주는 역할도 권한다 — [lolstats.gg 아무무](https://lolstats.gg/ko/champions/amumu/guide), [lolstats.gg 람머스](https://lolstats.gg/ko/champions/rammus/guide), [lolstats.gg 마오카이](https://lolstats.gg/ko/champions/maokai/guide)
- 탱커 정글은 팀을 받쳐주는 역할이며, 싸고 효율 좋은 체력·방어 아이템과 적은 골드로 굴러가는 빌드를 산다 — [Hotspawn: How To Play Jungler](https://www.hotspawn.com/league-of-legends/guide/how-to-play-jungler-in-league-of-legends)

**다이버/브루저 정글 (리 신/신 짜오/바이/자르반/오공/헤카림)**
- 신 짜오: 돌진(E)이 진입기이자 주 이니시. 궁극기 R(Crescent Guard)은 4초 동안 나머지 적의 피해를 막아 대상 하나를 고립시킨다. 리 신은 와드 점프로 빠질 수 있지만 신 짜오는 E로 들어가면 빠져나올 수단이 없다 — [dodge.gg Xin Zhao Build (2026)](https://www.dodge.gg/en-US/lol/news/xin-zhao-build-2026)
- 리 신은 후반으로 갈수록 긴 한타보다 끊기·이니시·필링을 맡는다. 기동성이 높고 포탑 어그로를 풀 수 있어 다이브도 잘한다 — [tacter Lee Sin jungle guide](https://www.tacter.com/lol/guides/lee-sin-jungle-build-guide-b9979949), [dodge.gg Xin Zhao 2026](https://www.dodge.gg/en-US/lol/news/xin-zhao-build-2026) (검색 요약. 두 문장 중 어느 쪽이 어느 출처인지는 확인 못 함)
- 한국 공략: 오공은 시야 밖에서 다가가 한타를 부수는 브루저 정글, 다이애나는 표식 후 순식간에 거리를 좁혀 한타를 부순다 — [lolstats.gg 오공](https://lolstats.gg/ko/champions/wukong/against), [lolstats.gg 다이애나](https://lolstats.gg/ko/champions/diana/against)
- 인벤 글에서 브루저는 상대가 누구든 교전을 벌이는 전투형 챔피언이다. 잘 크면 강하지만 성장이 막히면 팀에 부담이 된다 — [인벤 게시글](https://www.inven.co.kr/board/3369/2525422)(검색 요약)
- 바이, 자르반, 헤카림의 한타 타이밍을 직접 다룬 2026 자료는 찾지 못했다(아래 Gaps 참고).

**암살자 정글 (카직스/렝가/이블린/케인/녹턴/샤코)**
- 카직스: 한타에 바로 뛰어들지 말고, 체력이 낮은 적이 드러날 때까지 기다렸다 도약하라. 측면으로 돌아 핵심 대상에게 E를 닿게 하고, 후반에는 모습을 드러내지 않아야 기습 이점이 생긴다. 적이 미니언이나 아군 옆에 있으면 고립이 아니라 Q 피해가 약하니 떨어질 때까지 기다려라. "아군이 적을 갈라놓은 **뒤에** 들어가라" — [tacter Kha'Zix guide (14.20)](https://tacter.com/lol/guides/khazix-build-guides-runes-items-abilities-and-more-patch-1420-56c68a2), [tacter Kha'Zix coordination](https://tacter.com/lol/guides/perfect-coordination-between-khazix-and-his-teammates-e39e1b17), [tapin.gg Kha'Zix beginner](https://tapin.gg/blogs/khazix-beginner-guide-league-of-legends) (14.20 기준 일부는 **오래된 자료**)
- 이블린: W를 누르면 적이 들어온다는 걸 알고 부쉬로 숨으니 예언자의 렌즈(Farsight)로 대응을 막아라. 궁극기는 적의 쿨다운이 빠졌을 때 맞춰 써라. 싸움이 불리하면 아군이 싸우고 있어도 빠져서 회복하고 쿨을 기다려라 — [Skill Capped Evelynn jungle](https://www.skill-capped.com/lol/guides/builds/evelynn/jungle)(검색 요약)
- 인벤: 정글 암살자의 역할은 확실하고 빠른 딜로 초반에 갱을 가서 적 라이너를 무너뜨리는 것이다 — [인벤 게시글](https://www.inven.co.kr/board/lol/3262/581)(검색 요약). 다른 가이드는 암살자 정글의 단점으로 한타 기여가 매우 적다는 점을 든다 — 검색 요약 출처: [GameSkinny: Know your role](https://www.gameskinny.com/26epg/how-to-play-lol-know-your-role) **(오래된 일반 가이드)**

**AP/메이지 정글 (릴리아/다이애나/피들스틱/브랜드/카서스/탈리야)**
- 피들스틱 정글의 26.9 패치 추천 세팅은 감전 + 마법공학 로켓 벨트(진입용 돌진 아이템) — [U.GG Fiddlesticks jungle](https://u.gg/lol/champions/fiddlesticks/build/jungle)(검색 요약)
- 메이지 정글의 시야 밖 진입·궁극기 타이밍을 다룬 2026 자료는 찾지 못했다. 검색 결과는 승률·카운터 페이지뿐이었다.

**캐리/스커미셔 정글 (그레이브즈/킨드레드/마스터 이/벨베스/비에고/니달리)**
- 캐리 정글은 팀에 딜을 더하려고 존재한다. 최대한 파밍하고 초반 정글 싸움을 피하며, 갱은 적게 가되 가면 킬을 노린다 — [Hotspawn: How To Play Jungler](https://www.hotspawn.com/league-of-legends/guide/how-to-play-jungler-in-league-of-legends)
- 벨베스: 주 이니시 챔피언이 아니므로 아군이 이니시한 뒤 들어가라. 2v2·3v3 교전에 강하고, 피해를 받아줄 탱커 앞라인이 있어야 정리할 수 있다 — [tacter Bel'Veth coordination](https://www.tacter.com/lol/guides/perfect-coordination-between-belveth-and-her-teammates-8164f15b)
- 킨드레드: 교전 중 적을 늑대 영역(W) 안에 두는 게 좋고, 이동을 막는 CC에 매우 약하니 필링이 중요하다 — [LoLTheory Kindred synergies](https://loltheory.gg/lol/synergies/kindred)(검색 요약)
- 그레이브즈: 적이 뭉쳐 있으면 여러 챔피언을 뚫기 어려워 핵심 대상을 잡지 못한다(대응 측 조언). 본인은 E(Quickdraw)로 계속 움직이며 적 사거리 바로 밖에 있어야 한다 — [Mobalytics Graves counters](https://mobalytics.gg/lol/champions/graves/counters)
- 마스터 이는 상대 필링에 약하다고 소개된다 — [thespike.gg best junglers](https://www.thespike.gg/league-of-legends/champions/best-junglers)(검색 요약)
- 공통 위치 원칙: 위험 바로 밖에 서서 압박을 주면 적이 나쁜 싸움을 걸도록 유도할 수 있다. 적 정글이 안 보이면 측면에 있다고 보고 한 칸 더 뒤에 서라 — [MOBATrainer: Teamfighting (26.10)](https://mobatrainer.com/learn/teamfighting)

### Inferences
- **분류별 한타 플레이북**(위 출처의 공통 원칙에 실제 게임 지식을 더한 정리. 흔한 실수와 그 이유 포함):

| 분류 | 할 일 | 서는 위치 | 들어갈 때 | 노릴 대상 | 흔한 실수 (이유) |
|---|---|---|---|---|---|
| 탱커 이니시 (Vanguard) | 첫 진입으로 적 여러 명 또는 딜러 묶기 → 그다음 필링 | 아군 맨 앞, 적 딜러 쪽으로 붙는 각 | 적 핵심 디스인게이지/점멸이 빠졌거나 아군 딜러가 사거리 안에 있을 때 | 적 원딜·미드(뭉쳐 있으면 광역 CC 다수) | 아군 딜러가 멀리 있는데 혼자 진입 (따라올 사람이 없어 CC만 낭비), 회복 조합에 하드 이니시 (회복이 묶어 둔 시간을 흡수), 세주아니 Q가 앞라인에 막힘 |
| 다이버/브루저 (Diver) | 후방 진입으로 적 딜러 하나 지우기, 또는 아군 이니시 직후 따라 들어가기 | 측면 또는 아군 이니시 바로 뒤 | 적 핵심 CC(서폿 궁·점멸·존야)가 빠진 직후 | 적 원딜·미드 | 적 CC가 남아 있는데 먼저 진입 (신 짜오처럼 빠질 수단이 없으면 그대로 사망), 앞라인을 치느라 시간 낭비 |
| 암살자 | 시야 밖에서 기다렸다가 고립됐거나 빈사인 딜러 지우기 | 시야 밖 측면·후방(부쉬, 적 정글) | 한타가 시작되고 적이 스킬을 쓴 뒤(2~3초 후). 적이 갈라졌을 때 | 고립된 원딜·메이지·서폿 | 한타 시작부터 들어가 집중 CC 맞기, 미니언이나 아군 옆에 있는 대상 노리기 (카직스 고립 보너스 없음), 핑크와드 진입로로 들어가기 |
| AP/메이지 | 광역 CC·딜을 시야 밖에서 꽂기 (피들 R, 릴리아 R, 카서스 R, 탈리야 벽) | 시야 밖 측면, 아군 앞라인 뒤 | 적이 뭉쳤을 때. 아군 이니시와 동시이거나 직후 | 뭉친 적 다수 / 카서스는 빈사인 적 | 와드가 있는 곳에서 진입해 끊기기, 적이 흩어졌는데 궁 낭비 |
| 캐리/스커미셔 | 지속 딜로 적을 앞에서부터 녹이고 리셋해서 정리 | 아군 앞라인 뒤 (그레이브즈·킨드레드는 원딜처럼) | 적 CC가 빠진 뒤 (마스터 이·벨베스·비에고는 아군 이니시 뒤) | 사거리 안의 가장 가까운 적, 리셋이 되면 다음 적 | 먼저 진입해 CC를 다 맞기, 앞라인 없이 정면 싸움 |

### Gaps
- 바이·자르반·헤카림·릴리아·카서스·탈리야·녹턴·샤코의 2026 한타 타이밍을 다룬 주 출처는 찾지 못했다(본문 접근이 막혔고 검색 결과는 승률 페이지뿐).
- Skill Capped / Mobalytics / ProGuides의 정글 분류별 한타 강좌 본문은 확인하지 못했다.

## 2. 아군 조합(이니시/보호/포킹)과 적 위협(암살자, 다이브, 포킹, CC 연계)에 따라 정글러의 일이 어떻게 바뀌는가

### Takeaway
조합 유형(이니시·끊기·보호·포킹/공성·스플릿)이 한타 계획을 정한다. 정글러는 분류상 기본 역할이 있어도, 아군에 앞라인이 없으면 앞라인을 맡고, 적에 다이버나 암살자가 많고 아군에 캐리가 있으면 필링을 맡고, 적 CC가 많으면 진입 타이밍을 늦춘다.

### Cited Findings
- 조합은 보통 5가지로 나눈다: **이니시**(5대5 한타를 목표로 하며 가장 흔함. 한쪽이 반응하기 전에 묶이면 쿨다운의 절반도 쓰기 전에 끝난다), **끊기(픽)**(2대1·3대2로 수적 우위를 만듦, 시야에 크게 의존), **보호**(하이퍼캐리 한 명을 키우고 지킴, 뭉쳐 다니고 캐리를 혼자 두지 않음), **포킹/공성**(멀리서 깎아 낸 뒤 싸움, 디스인게이지와 스킬샷 정확도가 중요), **스플릿**(1대1 강한 챔피언이 옆 라인을 압박하고 나머지는 버티거나 4대4) — [procomps.gg Engage comp](https://procomps.gg/blog/engage-gamestyle.html), [Mobalytics: Clash comps](https://mobalytics.gg/blog/lol-best-clash-team-comps-and-counters/), [r/summonerschool wiki Team Comps](https://r.datuan.dev/r/summonerschool/wiki/101/teamcomps), [EarlyGame Team-Comp Archetypen](https://earlygame.com/de/lol/lol-guide-team-comps)
- 출처마다 조합 간 상성이 다르다(예: 보호 조합이 함께 움직이면 끊기 조합을 이긴다는 곳도 있고, 보호 조합은 스플릿·공성에 약하다는 곳도 있다). 커뮤니티 경험칙으로만 봐야 한다 — 위 출처들 사이 상충
- 모든 팀원이 따라올 수 있을 때만 진입하고, 아군이 스플릿 중이거나 라인을 먹고 있을 때는 이니시하지 말라 — [Mobalytics: Clash comps](https://mobalytics.gg/blog/lol-best-clash-team-comps-and-counters/)
- 회복이 강한 조합에 버스트 없이 하드 이니시하면 실패한다 — [LoLTheory: Engage & Disengage](https://blog.loltheory.gg/engage-disengage-lol/)
- 측면 텔레포트 시야: 적 정글 깊숙이 와드를 두면 탑·미드가 한타 도중 적 백라인 뒤로 텔레포트할 수 있다 — [MOBATrainer: Teamfighting (26.13)](https://www.mobatrainer.com/guides/teamfighting)
- 한국 공략 공통: 아군 암살자가 원딜을 노리면 무리하게 적 뒷라인으로 가지 말고 원딜 곁에서 적을 떼어내는 역할(필링)에 집중하라 — [lolstats.gg 노틸러스](https://lolstats.gg/ko/champions/nautilus/guide), [lolstats.gg 람머스](https://lolstats.gg/ko/champions/rammus/guide)
- 킨드레드처럼 이동을 막는 CC에 약한 캐리는 필링이 중요하다 — [LoLTheory Kindred](https://loltheory.gg/lol/synergies/kindred); 벨베스는 피해를 받아줄 탱커 앞라인이 필요하다 — [tacter Bel'Veth](https://www.tacter.com/lol/guides/perfect-coordination-between-belveth-and-her-teammates-8164f15b)

### Inferences
- **조합·위협별 수정 규칙** (위 원칙을 앱용 if-then으로 정리한 것. 개별 규칙마다 따로 근거가 있지는 않다):
  1. **아군에 앞라인이 없다** (정글 제외 Tank/Vanguard/Juggernaut가 0명) → 정글이 탱커/다이버면 "첫 진입 + 스킬 받기"를 맡는다. 정글이 암살자/캐리면 정면 한타를 피하고 끊기·측면 위주로 간다. 이유: 받아줄 사람이 없으면 아군 딜러가 먼저 맞는다(벨베스는 앞라인이 필요하다는 근거와 같은 논리).
  2. **적에 다이버/암살자가 2명 이상이고 아군에 하이퍼캐리가 있다** → 정글(탱커·와든형·CC 많은 챔프)은 진입 대신 아군 캐리 옆에서 필링. 이유: 아군 캐리가 살아 있어야 이긴다(보호 조합 원칙, 한국 공략의 필링 권장).
  3. **적 CC가 많다** (적 Vanguard·Catcher 다수, 적 CC 수치 높음) → 다이버·암살자·캐리 정글은 적 핵심 CC가 빠진 **다음에** 진입. 탱커 정글은 먼저 들어가 CC를 받아 낸다. 이유: 먼저 들어간 사람이 CC를 다 맞는다.
  4. **적에 하이퍼캐리가 있다** (스케일링 원딜, 마스터 이 등) → 정글의 목표 1순위는 그 캐리. 탱커는 그 캐리에게 CC, 암살자·다이버는 그 캐리를 측면에서 노린다. 하이퍼캐리 대상이 보호받고 있으면 끊기로 먼저 잡는다(끊기 조합 원칙).
  5. **적이 포킹/공성 조합이다** → 오래 서 있으면 진다. 정글은 이니시 각(측면·시야 밖)을 만들거나 적 정글로 들어가 시야를 지운다. 아군이 이니시가 없으면 오브젝트 전에 미리 자리를 잡는 대신 반대편에서 이득을 본다. 이유: 포킹 조합은 디스인게이지와 거리에 의존한다.
  6. **아군이 포킹 조합이다** → 정글은 진입하지 말고 아군 앞에서 적 진입을 막는다(와든 역할) / 적이 체력이 깎인 뒤에만 진입.
  7. **적 회복(인챈터) 조합 + 아군 지속 딜** → 하드 이니시 대신 끊기·고통스러운 상처 우선.

### Gaps
- 조합 유형별 정글 승률 같은 정량 근거는 찾지 못했다. 위 규칙은 경험칙이다.

## 3. 앱에서 쓸 수 있는 기계 판독 신호 (DDragon 태그, 위키 하위 분류, match-v5 수치)와 한타 역할 매핑 규칙

### Takeaway
Data Dragon 태그는 너무 거칠어서 단독으로는 정글 분류에 맞지 않는다(그레이브즈·킨드레드=Marksman, 마스터 이=Fighter/Assassin, 릴리아=Fighter/Mage, 아무무=Tank/Support). 위키 하위 분류를 수작업 표로 붙이고, match-v5의 `challenges.teamDamagePercentage`, `challenges.damageTakenOnTeamPercentage`, `challenges.enemyChampionImmobilizations`(분당)로 보정하는 3단 구조가 현실적이다.

### Cited Findings
- Data Dragon `champion.json`의 `tags`는 Fighter·Mage·Assassin·Tank·Support·Marksman 6종이며, 한 챔피언에 최대 2개가 붙는다 — [hextechdocs: Data Dragon](https://hextechdocs.dev/data-dragon/), [golio datadragon](https://pkg.go.dev/github.com/Saz4nd0ra/golio/datadragon). 한 커뮤니티 프로젝트는 ddragon 데이터, 특히 스킬과 아이템 수치가 부정확하다고 지적한다 — [J4NN0/league-of-legends-fight-tactics](https://github.com/J4NN0/league-of-legends-fight-tactics)
- **[로컬 DDragon 16.21.1] 실제 정글 챔피언 태그** (`data/ddragon/16.21.1/champion.ko_KR.json`에서 직접 읽음):
  - 탱커: 세주아니 [Tank], 람머스 [Tank], 자크 [Tank, Fighter], 아무무 [Tank, Support], 마오카이 [Tank, Support], 스카너 [Tank, Fighter], 누누 [Tank, Mage], 뽀삐 [Tank, Fighter]
  - 다이버/브루저: 리 신 [Fighter, Assassin], 바이 [Fighter, Assassin], 신 짜오 [Fighter, Tank], 자르반 4세 [Fighter, Tank], 오공 [Fighter, Tank], 헤카림 [Fighter, Tank], 우디르/워윅/볼리베어/트런들/쉬바나/렉사이 [Fighter, Tank], 판테온/암베사/브라이어 [Fighter, Assassin], 자헨 [Fighter]
  - 암살자: 카직스 [Assassin], 샤코 [Assassin], 탈론 [Assassin], 키아나 [Assassin], 렝가 [Assassin, Fighter], 나피리 [Assassin, Fighter], 이블린 [Assassin, Mage], 엘리스 [Assassin, Mage], 에코 [Assassin, Mage], 케인 [Fighter, Assassin], 녹턴 [Fighter, Assassin]
  - AP/메이지: 카서스 [Mage], 피들스틱 [Mage, Support], 브랜드 [Mage, Support], 탈리야 [Mage, Support], 자이라 [Mage, Support], 아이번 [Support, Mage], 릴리아 [Fighter, Mage], 그라가스 [Fighter, Mage], 다이애나 [Fighter, Assassin]
  - 캐리: 그레이브즈 [Marksman], 킨드레드 [Marksman], 마스터 이 [Fighter, Assassin], 벨베스 [Fighter], 비에고 [Fighter, Assassin], 니달리 [Assassin, Mage]
- **[로컬 match-v5] 필드 존재 확인**: 참가자 객체에 `timeCCingOthers`, `totalTimeCCDealt`(최상위)와 `challenges.teamDamagePercentage`, `challenges.damageTakenOnTeamPercentage`, `challenges.enemyChampionImmobilizations`, `challenges.killParticipation`, `challenges.saveAllyFromDeath`, `challenges.immobilizeAndKillWithAlly`가 실제로 들어 있다. Riot이 공개한 match-v5 예시에도 `timeCCingOthers`, `totalTimeCCDealt`가 있다 — [RiotTuxedo match-v5 sample gist (2021)](https://gist.github.com/RiotTuxedo/c8e2d29d12fc1e405ade267def036362)
- **[로컬 match-v5] 정글 포지션 챔피언별 평균** (KR, 1,500판, 25판 이상인 챔피언만. dmg=팀 내 챔피언 피해 비중, taken=팀 내 받은 피해 비중, cc=분당 timeCCingOthers 초, imm=분당 enemyChampionImmobilizations):

| 챔피언 | 판수 | dmg | taken | cc/분 | imm/분 |
|---|---|---|---|---|---|
| LeeSin | 385 | .186 | .231 | 0.78 | 0.61 |
| Sylas | 161 | .187 | .269 | 0.89 | 1.15 |
| Qiyana | 156 | .211 | .212 | 0.72 | 0.88 |
| Nidalee | 150 | .205 | .228 | 0.38 | 0.00 |
| Jayce | 119 | .243 | .196 | 0.54 | 0.80 |
| Vi | 107 | .156 | .219 | 1.00 | 2.01 |
| Talon | 106 | .202 | .234 | 0.21 | 0.01 |
| Viego | 105 | .182 | .229 | 0.59 | 0.59 |
| Graves | 96 | .204 | .190 | 0.76 | 0.01 |
| MonkeyKing | 95 | .176 | .227 | 0.62 | 0.60 |
| JarvanIV | 89 | .171 | .206 | 0.79 | 0.47 |
| Elise | 77 | .189 | .196 | 0.94 | 0.46 |
| Naafiri | 75 | .202 | .225 | 0.32 | 0.01 |
| Hecarim | 72 | .177 | .273 | 0.67 | 1.62 |
| Khazix | 68 | .212 | .219 | 0.32 | 0.01 |
| Chogath | 68 | .172 | .286 | 2.01 | 0.59 |
| Lillia | 66 | .199 | .259 | 0.90 | 0.27 |
| Kayn | 58 | .191 | .249 | 0.55 | 0.26 |
| MasterYi | 51 | .211 | .209 | 0.26 | 0.00 |
| XinZhao | 46 | .189 | .281 | 0.90 | 0.62 |
| Shaco | 42 | .189 | .188 | 0.89 | 1.26 |
| Kindred | 40 | .234 | .222 | 0.45 | 0.00 |
| Ekko | 39 | .170 | .242 | 0.69 | 0.15 |
| Nocturne | 38 | .179 | .248 | 5.32 | 0.29 |
| Zac | 36 | .158 | .268 | 1.51 | 3.15 |
| Diana | 36 | .196 | .205 | 0.45 | 0.40 |
| Rengar | 32 | .215 | .245 | 0.65 | 0.21 |
| Zed | 30 | .224 | .219 | 0.38 | 0.01 |
| RekSai | 30 | .167 | .275 | 1.03 | 0.71 |
| Briar | 29 | .196 | .252 | 1.02 | 1.03 |
| Pantheon | 27 | .187 | .219 | 0.81 | 0.64 |
| Shyvana | 27 | .216 | .229 | 0.55 | 0.29 |
| Taliyah | 27 | .220 | .179 | 1.04 | 0.90 |
| Karthus | 26 | .276 | .214 | 0.77 | 0.00 |

  (집계 스크립트: /tmp/agg.py, 입력 `data/raw/*.json.gz` 앞 1,500개. 세주아니·아무무·람머스·마오카이는 표본이 25판 미만이라 빠졌다.)

### Inferences
- **수치 해석**:
  - `enemyChampionImmobilizations`/분은 **하드 CC를 가진 진입형**을 잘 가른다: 자크 3.15, 바이 2.01, 헤카림 1.62, 샤코 1.26(상자 공포), 실라스 1.15 vs 카직스·탈론·그레이브즈·킨드레드·마스터 이·니달리·나피리·제드·카서스 ≈0. 탱커/다이버와 암살자/캐리를 가르는 데 가장 깔끔한 신호.
  - `timeCCingOthers`는 잡음이 크다: 녹턴 5.32, 초가스 2.01처럼 공포·침묵·둔화 계열이 부풀려진다. 단독 규칙으로 쓰지 말 것.
  - `damageTakenOnTeamPercentage`가 ≥0.26이면 앞라인 역할(초가스 .286, 신 짜오 .281, 렉사이 .275, 헤카림 .273, 실라스 .269, 자크 .268, 릴리아 .259). ≤0.20이면 뒤에서 딜하는 역할(탈리야 .179, 샤코 .188, 그레이브즈 .190, 제이스 .196, 엘리스 .196).
  - `teamDamagePercentage`가 ≥0.21이면 캐리형(카서스 .276, 제이스 .243, 킨드레드 .234, 제드 .224, 탈리야 .220, 쉬바나 .216, 렝가 .215, 카직스 .212, 마스터 이 .211). ≤0.17이면 셋업형(자크 .158, 바이 .156, 렉사이 .167, 에코 .170, 자르반 .171).
  - 2026 KR 정글 메타에는 비전통 정글(실라스, 키아나, 제이스, 탈론, 나피리, 제드, 초가스)이 많이 나온다. 수작업 표만 쓰면 이 챔피언들을 놓치므로 기본값(태그 + 수치) 규칙이 필요하다.
- **권장 규칙** (앱용, 위 수치에서 정한 기준값이며 외부 검증은 없음):
  1. 1단(수작업 표 우선): 위키 하위 분류가 있으면 그대로 쓴다. Vanguard→`engage_tank`, Warden→`peel_tank`, Diver→`diver`, Juggernaut→`bruiser_front`, Assassin→`assassin`, Skirmisher→`skirmisher_carry`, Burst/Battlemage/Artillery→`mage`, Marksman→`skirmisher_carry`(그레이브즈·킨드레드), Catcher/Enchanter→`utility`(아이번).
  2. 2단(표에 없을 때 DDragon 태그): 첫 태그가 Tank→`engage_tank`. Fighter+Tank→`diver`. Fighter+Assassin→imm/분 ≥0.4이면 `diver`, 아니면 `skirmisher_carry`. Assassin 단독 또는 첫 태그 Assassin→`assassin`. Mage 첫 태그→`mage`. Marksman→`skirmisher_carry`.
  3. 3단(수치 보정, 최소 30판): imm/분 ≥1.2이고 taken ≥0.25 → `engage_tank` 쪽으로 올림. imm/분 <0.1이고 dmg ≥0.20 → `assassin`(taken <0.23) 또는 `skirmisher_carry`. taken ≥0.26 → 한타 플랜에서 "앞라인 수" 1명으로 계산.
  4. 조합 집계용 파생값: 팀의 `frontline_count` = taken 비중 기대값 ≥0.25이거나 Tank 태그인 챔피언 수. `team_cc_index` = 다섯 명의 imm/분 합. `enemy_dive_threat` = 적 diver+assassin 수. 이 값으로 2절의 규칙 1~7을 실행한다.

### Gaps
- 공식 위키의 챔피언별 하위 분류 목록(어떤 정글이 Vanguard/Diver/Skirmisher인지)은 본문 접근이 막혀 확인하지 못했다. 위키 `Module:ChampionData/data`가 이 정보의 기계 판독 출처지만 접근 불가 — [LoL Wiki Module:ChampionData/data](https://wiki.leagueoflegends.com/en-us/Module:ChampionData/data). 네트워크 허용 목록에 `wiki.leagueoflegends.com`를 추가하면 가져올 수 있다.
- 로컬 데이터의 티어 구성과 패치 범위는 확인하지 못했다. 기준값은 티어별로 다시 맞춰야 한다.
- `challenges` 필드의 공식 정의 문서는 확인하지 못했다(필드 존재만 로컬 원본으로 확인).

## 4. 한국 커뮤니티 용어

### Takeaway
한국 공략은 "탱커 이니시 / 브루저 / 암살자 정글 / 캐리 정글 / 필링 / 후방 진입·측면 진입·시야 밖 진입"을 쓴다. 앱 문구도 이 용어를 그대로 쓰는 게 자연스럽다.

### Cited Findings
- "돌격형 탱커 정글러", "광역 CC로 한타를 무너뜨리는", "진입", "판을 깔아준다"(아무무) — [lolstats.gg 아무무](https://lolstats.gg/ko/champions/amumu/guide); "기습 이니시"(람머스) — [lolstats.gg 람머스](https://lolstats.gg/ko/champions/rammus/guide)
- "필링"(아군 딜러 옆에서 CC로 적을 떼어냄), "페이링"(같은 뜻의 다른 표기), "뒷라인" — [lolstats.gg 노틸러스](https://lolstats.gg/ko/champions/nautilus/guide), [lolstats.gg 람머스](https://lolstats.gg/ko/champions/rammus/guide)
- "시야 밖에서 접근", "한타를 파괴하는 브루저 정글러"(오공) — [lolstats.gg 오공](https://lolstats.gg/ko/champions/wukong/against)
- "브루저"(전투형 챔피언, 잘 크면 강하고 성장이 막히면 팀에 부담) — [인벤 게시글](https://www.inven.co.kr/board/3369/2525422)
- "암살자 정글"(확실하고 빠른 딜로 초반 갱) — [인벤 게시글](https://www.inven.co.kr/board/lol/3262/581)
- "성장형 캐리 정글러", "카운터 정글링"(그레이브즈) — [lolstats.gg 그레이브즈](https://lolstats.gg/ko/champions/graves/guide)

### Inferences
- 앱 용어 대응(제안): engage_tank=탱커 이니시(돌격형 탱커), peel_tank=보호형 탱커(필링), diver=돌진형 브루저(다이버), bruiser_front=전사형 브루저, assassin=암살자 정글, mage=AP 정글(메이지), skirmisher_carry=캐리 정글(성장형). 행동 용어: 이니시(선진입), 후방 진입/뒷라인 진입, 측면 진입, 시야 밖 진입(어둠 속 진입), 필링, 받아내기(탱킹), 끊기(픽), 포킹, 앞에서부터 녹이기, 마무리(정리).
- "후방 진입", "측면 진입"이라는 정확한 표현이 쓰인 한국 출처는 찾지 못했다. 위 출처들은 "뒷라인", "시야 밖에서 접근"을 썼다.

### Gaps
- 나무위키 정글러·역할군 문서와 인벤 정글 공략 본문은 검색에 나오지 않았고 직접 열 수도 없었다.
