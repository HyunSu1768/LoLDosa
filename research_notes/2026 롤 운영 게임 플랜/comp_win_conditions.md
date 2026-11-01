# 조합(Team Composition)이 게임 플랜과 승리 조건을 정하는 방식 (2026 시즌, 플래티넘~다이아 솔로랭크)

> 조사 범위 메모: 이 세션에서는 페이지 본문 가져오기(WebFetch)가 막혀 있었습니다(leagueoflegends.com, mobalytics.gg, procomps.gg 모두 DNS 실패). 그래서 아래 인용 내용은 모두 **웹 검색 결과에 나온 요약문**에서 가져왔고, 원문 전체를 읽어 확인한 것이 아닙니다. 정확한 숫자는 Riot 공식 26.1 패치 노트(https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/)와 대조해야 합니다. 조합 이론을 다룬 자료 상당수는 시즌 표기가 없거나 오래된 글이므로(2012~2020) 따로 표시했습니다.
>
> **2026 시즌 핵심 변경 (중요):** 아타칸(Atakhan), 핏빛 장미, 힘의 위업(Feats of Strength)은 26.1에서 **삭제**되었습니다. 의뢰 내용은 이 둘을 2026 목표물로 가정했지만, 앱 규칙에 아타칸/위업 분기를 넣으면 안 됩니다.

## 1. 분석가들이 쓰는 조합 유형과 각 유형의 승리 조건, 싸울 위치, 선호 목표물

### Takeaway
여러 자료가 거의 같은 5가지 유형을 씁니다: 한타/진입(Engage), 픽/캐치(Pick), 보호(Protect), 포킹/공성(Poke/Siege), 스플릿(Split, 1-3-1 포함). 여기에 받아치기(disengage/counter-engage)와 앞뒤 한타(front-to-back)를 추가하는 자료도 있습니다. 유형마다 무엇으로 이기는지가 다르므로, 앱이 조합을 판정할 때 이 승리 조건을 기준으로 삼으면 됩니다.

### Cited Findings
- 5분류 체계 두 가지: "Attack, Catch, Protect, Siege, Split"과 "Engage, Pick, Protect, Siege, Split". 이름만 다르고 내용은 같습니다. — [procomps.gg Team Comp Matchups](https://hub.procomps.gg/?p=1024); [Champbop](https://champbop.com/league-of-legends-team-compositions-explained/) (검색 요약 기준, 날짜 미상)
- **진입/한타(Engage)**: 가장 흔한 유형이며 attack comp, wombo combo, all-in comp라고도 부릅니다. 팀이 같이 움직여 정면 한타로 이기는 것이 승리 조건입니다. 딜러가 한 명뿐인데 그 딜러가 먼저 죽으면 크게 약해집니다. — [procomps.gg ENGAGE](https://procomps.gg/blog/engage-gamestyle.html); [Champbop](https://champbop.com/league-of-legends-team-compositions-explained/)
- 진입 조합은 자기 조건에서 싸움을 열고 대상을 묶어 한타를 시작합니다. 받아치기와 스플릿에 약합니다. — [Mobalytics team comps guide (2025년 12월 업데이트로 표시)](https://mobalytics.gg/lol/guides/everything-you-need-to-know-about-team-comps-and-teamfighting); [unrankedsmurfs](https://www.unrankedsmurfs.com/blog/the-counters-to-poke-engage-sustain)
- **포킹/공성(Siege)**: 사거리 우위로 안전한 거리에서 체력을 깎습니다. 공성 조합은 킬이나 한타 없이도 이길 수 있습니다(타워 철거). — [procomps.gg SIEGE](https://procomps.gg/blog/siege-gamestyle.html); [procomps.gg SIEGE guide](https://hub.procomps.gg/?p=961)
- 포킹은 상대 체력을 계속 깎아서 싸우거나 목표물을 지킬 수 없게 만듭니다. 수동적으로 깎으면서 이기며, 진입 조합이 무리하게 먼저 들어오도록 만듭니다. — [Mobalytics](https://mobalytics.gg/lol/guides/everything-you-need-to-know-about-team-comps-and-teamfighting); [nerfplz (2016)](https://www.nerfplz.com/2016/12/team-composition-building-101.html)
- **픽/캐치(Pick)**: 시야를 많이 장악하고 상대를 한 명씩 잡습니다. — [earlygame.com (독일어)](https://earlygame.com/de/lol/lol-guide-team-comps)
- **보호(Protect)**: 하이퍼캐리 한 명에게 자원을 몰아주고 그 챔피언 중심으로 플레이합니다. 후반에 가장 강한 조합으로 꼽힙니다. — [Champbop](https://champbop.com/league-of-legends-team-compositions-explained/); [procomps.gg](https://hub.procomps.gg/?p=1024)
- 정글러가 캐리를 맡는 보호 조합도 있습니다(예: 트위치 정글을 팀이 지켜줌). — [Mobalytics](https://mobalytics.gg/lol/guides/everything-you-need-to-know-about-team-comps-and-teamfighting) (검색 요약)
- **스플릿**: 강한 1:1 챔피언, 나머지 팀의 강한 웨이브 클리어, 빠져나갈 수단이 필요합니다. 상대를 갈라놓고 여러 목표물을 동시에 압박하는 것이 승리 조건입니다. — [Champbop](https://champbop.com/league-of-legends-team-compositions-explained/)
- **1-3-1**은 가장 오래된 조합 중 하나이며, 솔로랭크에서 흔히 쓰이는 기본 운영입니다. — [Mobalytics 1-3-1](https://mobalytics.gg/?p=59779) (검색 요약)
- 스플릿 운영(한국어 설명): 사이드에서 상대를 압도해 인원을 끌어들인 뒤 텔레포트로 수적 우위 한타를 열거나 딜러를 직접 잡습니다. 1-3-1은 한 명이 사이드에서 성장하고 나머지가 상대 스플릿을 막는 방식입니다. — [lolstats.gg 잭스 가이드](https://lolstats.gg/ko/champions/jax/guide); [인벤 G2 운영 분석 (2019)](https://www.inven.co.kr/board/lol/2971/30710)
- **앞뒤 한타(Front-to-back)**: 지속 딜과 긴 교전에 강한 챔피언을 고르게 섞은 순수 한타 조합입니다. 승리 조건이 명확하지만 돌진 조합에 약합니다. — [Champbop](https://champbop.com/league-of-legends-team-compositions-explained/)
- **받아치기(Disengage)**: 상대가 들어오거나 너무 앞으로 나오기를 기다렸다가 받아쳐서 교전을 뒤집습니다. — [Mobalytics counter-engage](https://mobalytics.gg/lol/guides/how-to-counter-engage-team-comp); [unrankedsmurfs](https://www.unrankedsmurfs.com/blog/the-counters-to-poke-engage-sustain)
- 한국 경기 기사에 나온 용어 사례: '포킹 조합'(니달리·바루스·이즈리얼 원거리 포킹), '돌진 조합'의 역습이 포킹 조합의 타워 철거를 막은 사례, '강제 한타 개시(이니시에이팅)' 조합, 받아치기. — [inews24 (2016)](https://www.inews24.com/view/959666); [게임메카 롤챔스 기사](https://www.gamemeca.com/view.php?gid=455727)
- 포킹은 상대가 한곳에 모여 있을 때 묶어두고 일점사하기 쉽습니다. — [게임메카](https://www.gamemeca.com/view.php?gid=458407) (검색 요약)

### Inferences
- 앱 표준 분류 제안 (한국어 표기 / 내부 키):
  - 한타·돌진 조합 (`ENGAGE`): 승리 조건은 5:5 정면 한타. 싸울 위치는 좁은 정글 길목과 강가 목표물 앞(드래곤·전령·바론 둥지)으로, 진입 거리가 짧은 곳입니다. 목표물은 시간이 정해진 목표물을 이용해 한타를 강요하는 쪽을 선호합니다.
  - 포킹·공성 조합 (`SIEGE`): 승리 조건은 타워 철거, 그리고 체력을 깎은 뒤 목표물 확보. 싸울 위치는 넓은 중앙 라인과 타워 앞으로, 상대가 돌아 들어올 길이 없는 곳입니다. 목표물은 타워·포탑 골드(26.1에서 2·3차 타워에도 방패 골드 추가, 아래 2장 참고)이고, 시간 맞춘 목표물 앞에서 미리 깎아두는 것을 선호합니다.
  - 픽 조합 (`PICK`): 승리 조건은 시야 장악 후 한 명을 잡고 그 즉시 목표물을 가져가는 것. 싸울 위치는 상대 정글과 사이드 라인 입구입니다.
  - 보호 조합 (`PROTECT`): 승리 조건은 캐리가 성장할 때까지 버티고 후반에 앞뒤 한타로 이기는 것. 싸울 위치는 넓은 곳, 아군 시야 안, 수비 쪽입니다.
  - 스플릿·1-3-1 조합 (`SPLIT`): 승리 조건은 사이드 압박으로 상대를 갈라놓아 목표물을 교환하거나 수적 우위를 만드는 것. 5:5 정면 한타는 피합니다.
  - 받아치기 조합 (`DISENGAGE`): 승리 조건은 상대 진입을 받아쳐서 이기는 것. 아군 진영, 길목 수비에서 싸웁니다.
  - 난전 조합 (`SKIRMISH`): 자료에서 독립 유형으로 다룬 경우를 찾지 못했습니다. 2~3인 소규모 교전과 픽/돌진의 중간 성격으로 분류하는 것을 권합니다.
- 한 조합이 두 유형을 동시에 가질 수 있습니다(예: 진입 + 픽). 앱은 하나로 고르지 말고 유형별 점수 벡터를 계산한 뒤 주 유형과 부 유형을 정하는 것이 안전합니다.

### Gaps
- 2025~2026년 LCK/LPL 분석 기사 중 '드래프트 승리 조건'을 체계적으로 정리한 글은 찾지 못했습니다(검색 결과는 픽밴 통계와 선수 인터뷰가 대부분).
- 나무위키 '조합' 문서는 검색에 나오지 않아 확인하지 못했습니다. '스커미시(난전) 조합'을 독립 유형으로 정의한 출처도 찾지 못했습니다.
- '승리 플랜', '후반 조합', '초반 조합'을 정의한 한국어 출처는 찾지 못했습니다. 다만 업계에서 흔히 쓰는 말입니다.

## 2. 초반 힘과 후반 힘 판단, 그리고 그에 따른 플랜 변화

### Takeaway
초반 조합은 대체로 2코어 이전에 강하고, 후반 조합은 템이 다 갖춰졌을 때 강합니다. 초반 조합은 상대가 강해지기 전에 싸우고 템포로 이득을 굴려야 하고, 후반 조합은 상대가 강한 시점에 싸움을 피하면서 목표물을 교환해야 합니다. 2026에는 공허 유충과 전령이 강화되고 아타칸이 삭제되어 초반 탑 쪽 목표물의 가치가 커졌습니다.

### Cited Findings
- 강해지는 시점은 상대와 비교한 상대적 강함으로 이해해야 합니다. 초반 조합은 2코어 완성 전에 가장 강하고, 후반 조합은 빌드가 완성되면 가장 강합니다. 후반의 한 번 죽음은 대부분의 아이템보다 더 큰 기회를 만듭니다. — [nerfplz Power Spikes Explained (2026-09)](https://www.nerfplz.com/2026/09/power-spikes-explained-when-you-are.html) (검색 요약)
- 상대에 후반 챔피언이 많고 우리 팀에는 없다면, 상대가 강해지기 전에 싸워야 합니다. — [Mobalytics](https://mobalytics.gg/lol/guides/everything-you-need-to-know-about-team-comps-and-teamfighting) (검색 요약)
- 정글러는 자기 매치업만 보고 템포를 정하는 경우가 많습니다. 후반형 정글러라도 라인들이 일찍 끝내야 하는 조합이면 파밍만 할 수 없고 템포를 강요해야 합니다. 템포를 강요하면 팀이 상대의 강한 시점을 버티고 자기 강한 시점까지 갈 수 있습니다. — [Dignitas, Controlling Tempo (오래된 글)](https://dignitas.gg/articles/controlling-tempo-a-junglers-guide)
- 레벨 2는 가장 빠른 실질적 우위이고, 레벨 3은 초반 스킬 구성이 다 갖춰져 많은 챔피언이 이동기나 탈출기를 얻는 시점입니다. — [nerfplz (2026)](https://www.nerfplz.com/2026/09/power-spikes-explained-when-you-are.html) (검색 요약)
- **2026 목표물 구성 (26.1)**:
  - 아타칸·핏빛 장미·힘의 위업 삭제. 바론은 20분 등장으로 복귀. 퍼블과 첫 타워 골드 보상이 각각 100과 300으로 복귀. — [esports.gg](https://esports.gg/news/league-of-legends/atakhan-feats-of-strength-league-of-legends-2026); [Sheep Esports](https://www.sheepesports.com/en/all/articles/league-of-legends-2026-s1-gameplay-changes-atakhan-removed-new-plates-on-t2-and-t3-nashor-back)
  - Riot은 '목표물 피로'를 줄이기 위해 아타칸을 삭제했고, 유충과 전령의 효과를 조금 강화했다고 밝혔습니다. — [esports.gg](https://esports.gg/news/league-of-legends/atakhan-feats-of-strength-league-of-legends-2026); [dotesports](https://dotesports.com/league-of-legends/news/all-changes-league-of-legends-season-1-2026)
  - 2·3차 타워에 새로 방패 골드가 생겼습니다(Sheep Esports 제목에 "New Plates on T2 & T3"). — [Sheep Esports](https://www.sheepesports.com/en/all/articles/league-of-legends-2026-s1-gameplay-changes-atakhan-removed-new-plates-on-t2-and-t3-nashor-back)
  - 공허 유충: 체력 250→1300, 처치자 골드 20→30(전체 골드 삭제), 처치자만 골드를 받음, 미니언·구조물 대상 피해 +50%, 26.1에서 시작 레벨이 7로 변경. 이후 26.11과 26.17에서도 바뀌었습니다. — [riftpatchnotes Void Grubs](https://www.riftpatchnotes.com/lol/system/void-grubs); [games.gg](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/)
  - 유충 캠프는 8:00에 3마리가 한 번만 등장하고, 14:45(전투 중이면 14:55)에 사라집니다. — [nerfplz Every Objective (2026-08)](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html); [LoL Wiki Voidgrub camp](https://wiki.leagueoflegends.com/en-us/Voidgrub_camp)
  - 전령: 15:00 등장(25.9에서 16:00→15:00), 눈 재사용 대기시간 8→6, 미니언·구조물 대상 피해 +50%, 처치자 100골드, 돌진 피해 3000 고정. 14:00이라고 적은 오래된 Fandom 페이지도 있습니다. — [riftpatchnotes Rift Herald](https://www.riftpatchnotes.com/lol/unit/rift-herald); [games.gg](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/)
  - 바론은 20분 등장이며, 시간 대신 레벨 11부터 레벨에 비례해 강해집니다. — [nerfplz (2026-08)](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html)
  - 드래곤: 원소 드래곤이 더 단단해졌고, 드래곤 복수 피해 감소가 7/14/21%에서 15/30/45%로 올랐으며(챔피언 대상 추가 피해는 삭제), 처치 골드는 25→75. 장로 드래곤은 15:00에 등장하고 체력이 약 20% 올랐습니다. — [games.gg](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/); [thegamehaus](https://thegamehaus.com/league-of-legends/full-lol-patch-26-1-patch-notes-for-demacia/2026/01/07/); [Riot 26.1](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/)
- **역할 퀘스트 (26.1)**:
  - 탑: 무료 텔레포트, 또는 이미 텔레포트를 들었다면 보호막 텔레포트 강화. 레벨 상한이 20으로 오른다는 출처도 있습니다. 레벨 3까지 탑 외 라인 미니언 골드와 경험치가 줄어 라인 스왑을 억제합니다.
  - 정글: 퀘스트 완료 시 펫과 강타가 강화되고(강타 1400이라는 출처 있음), 큰 몬스터마다 골드와 경험치 +10.
  - 원딜: 신발이 퀘스트 칸으로 가서 사실상 7번째 아이템 칸이 생깁니다.
  - 서폿: 제어 와드 40골드, 퀘스트 칸에 2개까지 보관.
  - 수치는 출처마다 다릅니다. — [esports.gg 26.1](https://esports.gg/guides/league-of-legends/lol-patch-notes-26-1/); [nerfplz Role Quests (2026-08)](https://www.nerfplz.com/2026/08/role-quests-explained-what-every-lane.html); [cache.esports.gg](https://cache.esports.gg/news/league-of-legends/league-of-legends-2026-role-quests)
- LCK 선수들은 시즌 전 인터뷰에서 텔레포트 유무가 초중반에 너무 큰 차이를 만든다고 했고, 정글 퀘스트 보상은 라이너 보상보다 약하다고 평가했습니다. — [Inven Global](https://www.invenglobal.com/articles/20054/lck-players-react-to-2026-preseason-patch-teleport-still-essential-for-top-lane-jungle-rewards-underwhelming)

### Inferences (앱 규칙 초안)
- 강함 곡선 점수 = 챔피언별 시간대 가중치(초반 1~6레벨 / 중반 1~2코어 / 후반 3코어 이상)의 팀 합. 두 팀 곡선의 차이로 아래 상황 중 하나를 고릅니다.
  - **우리 초반 > 상대 초반 (특히 정글과 2:2 라인)**: 8:00 유충을 탑·미드 우선권과 함께 3마리 노리기. 첫 드래곤과 퍼블·첫 타워 골드(100/300)를 노리는 템포 플레이. 정글은 2·3레벨 강한 시점에 갱킹하고 상대 정글에 침투. 2·3차 타워 방패 골드까지 굴려서 "상대 2코어 전에" 끝내기.
  - **우리 후반 > 상대 초반**: 첫 귀환 전 싸움 피하기. 유충은 탑 우선권이 없으면 포기하고 반대편 드래곤과 교환. 정글은 상대 정글 동선 반대쪽에서 파밍하고 강한 라이너 근처 수비 와드 설치. 상대가 2코어를 갖추기 전에는 5:5 한타 금지. 드래곤 영혼이나 장로(복수 피해 감소 강화로 따라잡기가 쉬워짐)와 20분 이후 바론 시점에 승부.
  - **둘 다 후반**: 라인 관리와 시야 중심. 정글은 효율적인 파밍과 퀘스트를 우선하고, 목표물은 우선권이 있는 쪽에서만 가져갑니다.
  - **둘 다 초반**: 첫 교전 시점(레벨 3과 첫 유충)의 위치 선점이 승패를 가릅니다.
- 아타칸이 삭제되어 14~20분 사이에 시간 맞춘 대형 목표물이 사라졌습니다(전령 15:00과 드래곤만 남음). 후반 조합이 버티기 쉬워졌을 가능성이 있지만 추정입니다.

### Gaps
- 챔피언별 초반/후반 가중치를 공개적으로 정량화한 데이터셋은 찾지 못했습니다. 앱 자체 통계(게임 시간대별 승률)로 만들어야 합니다.
- 26.11과 26.17의 유충·전령 변경 수치는 확인하지 못했습니다. 현재(26.21 전후) 값은 패치 노트와 대조해야 합니다.

## 3. 조합 유형 간 상성과 양쪽의 플레이 방법

### Takeaway
가장 흔히 쓰는 상성 모델은 가위바위보입니다: 포킹 < 진입 < 받아치기 < 포킹. 여기에 진입 조합은 스플릿에 약하다는 축이 더해집니다. 단, 출처마다 상성 순환 구조가 다르므로 앱은 고정된 '이긴다/진다' 판정 대신 경향으로 표현해야 합니다.

### Cited Findings
- 포킹은 진입 조합이 무리하게 먼저 들어오도록 만들고, 진입은 받아치기와 스플릿에 약하며, 받아치기는 포킹에 집니다(받아칠 대상인 진입이 없으면 받아치기가 무력해짐). — [Mobalytics](https://mobalytics.gg/lol/guides/everything-you-need-to-know-about-team-comps-and-teamfighting); [unrankedsmurfs](https://www.unrankedsmurfs.com/blog/the-counters-to-poke-engage-sustain)
- 다른 모델(4유형 순환): 포킹 < 회복 < 올인 < 받아치기 < 포킹. — [nerfplz (2016, 오래된 글)](https://www.nerfplz.com/2016/12/team-composition-building-101.html)
- 또 다른 모델: 회복은 포킹을 잘 받아내지만 진입에 더 약합니다. — [unrankedsmurfs](https://www.unrankedsmurfs.com/blog/the-counters-to-poke-engage-sustain)
- 공격(진입) 조합은 스플릿과 공성 조합에 약합니다. — [Champbop](https://champbop.com/league-of-legends-team-compositions-explained/)
- 앞뒤 한타 조합은 돌진에 약합니다. — [Champbop](https://champbop.com/league-of-legends-team-compositions-explained/)
- 보호 조합의 대응: 스플릿 푸셔 주변 시야를 확보하고, 공성 조합을 상대할 때는 빠르게 싸움을 엽니다. — [procomps.gg](https://hub.procomps.gg/?p=1024)
- 진입 조합 상대로는 들어오기 전에 포킹으로 깎아두고, 받아치기 조합이라면 뭉쳐서 플레이합니다. — 검색 요약 (Mobalytics counter-engage / unrankedsmurfs)
- 한국 사례: 포킹 조합이 타워를 빨리 밀었지만 돌진 조합의 역습에 계속 당해 더 이득을 보지 못했습니다(2016 롤챔스). — [게임메카](https://www.gamemeca.com/view.php?gid=455727)
- 솔로랭크 통계(Mobalytics, Red Bull 재게재, 날짜 미상): 7가지 조합 중 스플릿, 카이팅, 픽이 선택률의 약 85%를 차지했습니다. 범위 광역(AoE) 조합은 게임 이해도와 손이 낮은 하위 티어에서 더 잘 통하고, 상위 티어에서는 플레이어가 대처법을 익혀 스플릿 비중이 줄어듭니다. 실제 승률 수치는 차트에만 있어 확인하지 못했습니다. — [Red Bull / Mobalytics](https://www.redbull.com/us-en/mobalytics-high-level-team-comp-analysis)

### Inferences (상성 규칙 초안: 우리 → 상대)
- 포킹 vs 진입: 포킹 측은 시간 맞춘 목표물 30~60초 전에 먼저 도착해 시야를 잡고 깎은 뒤 확보하고, 진입 길목을 와드로 보며 정면 대치를 유지합니다. 진입 측은 측면과 정글로 돌아가 근접 각을 만들고, 포킹 측이 시야를 잡기 전에 목표물 둥지를 선점합니다. 체력이 깎이면 싸우지 말고 목표물을 교환합니다.
- 진입 vs 받아치기: 진입 측은 정면 진입을 피하고 측면 진입, 시야 차단, 상대 핵심 받아치기 스킬이 빠진 순간을 노립니다. 스플릿으로 상대를 강제로 움직이게 만드는 것도 방법입니다. 받아치기 측은 먼저 싸우지 말고 목표물을 내주는 척 받아칩니다.
- 받아치기 vs 포킹: 받아치기 측은 진입 수단이 없으면 대치 중에 깎이기만 하므로, 사이드 운영과 파밍으로 시간을 끌거나 픽으로 승부합니다(받아치기 조합에도 순간 진입 하나는 필요).
- 한타 vs 스플릿: 한타 측은 4:1 상황에서 빠르게 목표물을 강요하고 스플릿 챔피언의 텔레포트 쿨을 확인합니다. 스플릿 측은 정면 5:5를 피하고 반대편 목표물이 등장하기 직전에 사이드를 밉니다. 2026 탑 퀘스트 텔레포트 보상 때문에 스플릿 후 합류가 쉬워졌을 수 있습니다(추정).
- 픽 vs 공성: 공성 측이 대치하려고 시야를 넓히는 순간이 픽 조합의 기회입니다. 공성 측은 뭉쳐 다니고 정글에 혼자 들어가지 않습니다.
- 솔로랭크 플래티넘~다이아 보정: 범위 광역 진입(예: 말파이트·오리아나·아무무) 조합의 가치를 상향하고, 1-3-1처럼 소통이 필요한 계획은 '권장 계획'이 아니라 '선택지'로 표시하는 것을 권합니다(Mobalytics 통계 해석 기반).

### Gaps
- 2025~2026 솔로랭크에서 조합 유형별 승률을 수치로 검증한 출처는 찾지 못했습니다(Mobalytics 차트는 날짜 미상이고 수치도 미확인).

## 4. 라인 우선권과 어느 쪽에서 플레이할지 (봇 사이드 vs 탑 사이드)

### Takeaway
라인 우선권이 정글이 안전하게 움직일 수 있는 쪽을 정합니다. 탑·미드 우선권이 있으면 8:00 유충과 15:00 전령으로, 봇·미드 우선권이 있으면 드래곤으로 갑니다. 우선권이 없는 쪽 목표물은 반대편 목표물과 교환합니다.

### Cited Findings
- 정글이 탑과 봇 양쪽 캠프를 먹는 수직 정글링은 상대 자원을 빼앗지만, 침투하는 쪽 라인 우선권이 필요합니다. — 2026 정글 가이드 [dodge.gg](https://www.dodge.gg/en-US/lol/news/jungle-guide-2026) / [buildzcrank](https://buildzcrank.com/en/blog/jungle-guide-lol-2026/) (검색 요약, SEO 성격 글)
- 상대 정글이 봇에서 시작했다면 아군 탑 정글은 침투 걱정 없이 돌 수 있습니다. — 같은 2026 정글 가이드들 (검색 요약)
- 봇 우선권이 있고 상대 정글이 탑에 보이면 드래곤을 견제 없이 먹을 수 있습니다. 봇이 라인을 밀어두고 미드가 강가 입구를 지키면 드래곤이 깔끔하게 나옵니다. — [boostingmarket objective priority](https://boostingmarket.com/blogs/lol-objective-priority-guide/); [boosteria](https://boosteria.org/guides/comprehensive-guide-objective-management-in-league) (2025)
- 탑과 미드가 먼저 움직일 수 있으면 정글이 유충을 시작하고 라이너 한 명이 입구를 지킵니다. 탑 우선권이 있을 때는 두 번째 드래곤 전에 유충 2~3마리를 먹는 것이 대체로 옳습니다. 유충을 먹으면서 상대에게 드래곤을 내주고 다음 드래곤을 견제하는 교환도 권장됩니다. 웨이브 하나를 통째로 버리거나 타워를 노출하게 되면 유충을 포기합니다. — [boostingmarket](https://boostingmarket.com/blogs/lol-objective-priority-guide/); [boostingmarket early game](https://boostingmarket.com/blogs/lol-early-game-guide/)
- 유충과 전령 등장 시간은 출처마다 다릅니다(유충 5:00 vs 8:00, 전령 8:00 / 14:00 / 15:00). 2026 기준으로는 유충 8:00, 전령 15:00이 가장 일관된 값입니다(위 2장 참고). — 검색 결과 상충

### Inferences (사이드 규칙 초안)
- 사이드 점수 = (탑 매치업 우세 + 미드 매치업 우세 + 정글 초반력 비교) vs (봇 2:2 우세 + 미드 + 정글).
  - 탑 쪽 점수가 높으면: 탑 쪽에서 시작해 8:00 유충 3마리를 노리고, 이후 15:00 전령으로 2·3차 타워 방패 골드까지 굴립니다. 드래곤은 상대에게 교환으로 내줘도 됩니다.
  - 봇 쪽 점수가 높으면: 봇 쪽에서 시작하거나 끝내는 동선으로 첫 드래곤(5:00 전후, 확인 필요)을 노리고, 유충 타이밍에는 드래곤 쪽에서 교환합니다.
  - 아군 후반 캐리가 있는 라인 쪽은 수비(커버)하고, 우세한 초반 라인 쪽은 공격합니다.
- 포킹·공성 조합은 전령이나 유충 미니언 강화(구조물 피해 +50%)와 상성이 좋으므로 탑 쪽 목표물 가중치를 높입니다. 보호·후반 조합은 드래곤 영혼과 장로 가중치를 높입니다(추정).
- 2026 탑 퀘스트가 라인 스왑을 억제하므로 표준 라인 배치를 전제로 해도 됩니다.

### Gaps
- 2026 첫 드래곤 등장 시간은 이번 검색에서 확인하지 못했습니다(이전 시즌은 5:00).
- 사이드 선택과 승률의 관계를 다룬 정량 연구는 찾지 못했습니다.

## 5. 앱이 쓸 수 있는 측정 가능한 챔피언 속성과 데이터 소스

### Takeaway
Data Dragon `champion.json`에는 `tags`(최대 2개, Fighter/Tank/Mage/Assassin/Marksman/Support)와 `info`(attack/defense/magic/difficulty 각 0~10)만 있습니다. 이 값은 오래되고 대략적이라 조합 판정에는 부족합니다. 진입·포킹·웨이브 클리어·사거리·후반력 같은 속성은 수작업 태그 테이블(또는 LoL Wiki 세부 클래스)과 앱 자체 경기 통계로 보충해야 합니다.

### Cited Findings
- Data Dragon 챔피언 항목에는 title, blurb, info, image, tags가 있고, `info`는 Attack·Defense·Magic·Difficulty 정수(0~10)입니다. 예: 아리 magic 8, attack 3, defense 4, difficulty 5. — [golio datadragon (Go 패키지)](https://pkg.go.dev/github.com/Saz4nd0ra/golio/datadragon); [Cassiopeia docs](https://cassiopeia.readthedocs.io/en/latest/cassiopeia/champion.html)
- LoL Wiki는 attack/defense 값을 오래된(archaic) 클라이언트 평가(0~10)라고 부릅니다. — [LoL Wiki Module:ChampionData/data](https://wiki.leagueoflegends.com/en-us/Module:ChampionData/data)
- Data Dragon 데이터는 부정확하며, 특히 스킬 데이터와 아이템 수치가 그렇습니다(Riot 데이터 래퍼 측 지적). 대안으로 Meraki `lolstaticdata`가 있습니다. — [meraki-analytics/lolstaticdata](https://github.com/meraki-analytics/lolstaticdata); [hextechdocs Data Dragon](https://hextechdocs.dev/data-dragon/)
- Riot/Wiki 클래스 체계: Controller(Enchanter, Catcher), Fighter(Juggernaut, Diver), Mage(Burst, Battlemage, Artillery), Marksman, Slayer(Assassin, Skirmisher), Tank(Vanguard, Warden), Specialist. Wiki 분류 기준 인원수 예시: Artillery 8, Catcher 10, Diver 19, Enchanter 12, Juggernaut 14, Vanguard 15, Warden 7(날짜 미상). — [LoL Wiki Category:Champions by class](https://wiki.leagueoflegends.com/en-us/Category:Champions_by_class); [Strafe](https://www.strafe.com/articles/read/league-of-legends-champion-classes/)
- Guild Order 같은 제3자 사이트는 비공식 라벨(예: "Engage support")을 씁니다. — 검색 요약

### Inferences (앱 속성 스키마 제안)
| 속성 | 소스 | 조합 판정에 쓰는 방식 |
|---|---|---|
| 피해 유형 비율 (AD/AP/고정) | Meraki 데이터 또는 수작업, 경기 데이터의 `magicDamageDealtToChampions` / `physicalDamageDealtToChampions` 평균 | 한쪽이 80% 이상이면 "상대가 방어템 하나로 대응 가능" 경고 |
| 진입 도구 (거리, 범위 CC) | Wiki 세부 클래스(Vanguard/Catcher/Diver) + 수작업 0~3점 | `ENGAGE` 점수 |
| 받아치기·보호 도구 | Warden/Enchanter + 수작업 | `DISENGAGE`/`PROTECT` 점수 |
| 포킹 (사거리, 장거리 스킬) | Artillery + 기본 공격 사거리(`stats.attackrange`) | `SIEGE` 점수 |
| 웨이브 클리어 | 수작업 0~3 | 공성·스플릿 가능 여부, 4:1 버티기 가능 여부 |
| 1:1·사이드 능력 | Juggernaut/Skirmisher + 수작업 | `SPLIT` 점수 |
| 픽 도구 (원거리 단일 CC, 은신, 기습) | Catcher/Assassin + 수작업 | `PICK` 점수 |
| 탱키함 | `info.defense`(대략적), Tank 태그 | 앞라인 유무 (0이면 앞뒤 한타 불가) |
| 강함 곡선 (초반/중반/후반) | 앱 자체 경기 통계(게임 시간대별 승률 기울기) | 2장의 템포 규칙 |
| 6레벨 강한 시점 | 수작업 플래그 | "6레벨 이후 갱킹·합류" 규칙 |
| 정글 초반력 (침투, 갱킹 강도) | 앱 자체 통계 (첫 갱킹 시간, 15분 골드 차이) | 정글 동선 규칙 |
- `info.attack`·`info.magic`만으로 피해 유형을 추정하면 오류가 큽니다(예: AP/AD 혼합 챔피언, 빌드에 따라 달라지는 챔피언). 경기 데이터의 실제 피해 비율이 더 정확합니다(추정).

### Gaps
- 진입·웨이브 클리어·후반력을 공개 라이선스로 태그한 커뮤니티 데이터셋은 이번 조사에서 확인하지 못했습니다.
- Riot 공식 `champion.json` 스키마 문서는 찾지 못했고, 필드 설명은 제3자 출처에 기반합니다.

## 6. 한국어 용어 정리 (앱 표시용)

### Takeaway
한국 커뮤니티와 중계에서는 한타 조합, 돌진 조합, 포킹 조합, 스플릿(운영) 조합, 픽(암살) 조합, 받아치기(역이니시), 후반 조합, 초반 조합을 씁니다. 앱 문구도 이 표현을 따르면 됩니다.

### Cited Findings
- '포킹 조합', '돌진 조합', '강제 한타 개시(이니시에이팅)', 반격(받아치기)이 경기 기사에 쓰인 사례. — [inews24](https://www.inews24.com/view/959666); [게임메카](https://www.gamemeca.com/view.php?gid=455727)
- 스플릿 푸시와 1-3-1 운영의 한국어 설명. — [lolstats.gg 잭스](https://lolstats.gg/ko/champions/jax/guide); [인벤 (2019)](https://www.inven.co.kr/board/lol/2971/30710)

### Inferences
- 제안 용어 매핑: `ENGAGE`=한타·돌진 조합, `SIEGE`=포킹·공성 조합, `PICK`=픽(끊어먹기) 조합, `PROTECT`=캐리 보호(지키기) 조합, `SPLIT`=스플릿 조합(1-3-1), `DISENGAGE`=받아치기 조합, 강함 곡선=초반 조합/후반 조합(밸류 조합), 승리 조건=승리 플랜.

### Gaps
- '픽 조합', '승리 플랜', '밸류 조합'의 한국어 정의 출처(나무위키, 한국 코치 유튜브)는 이번 검색에서 확인하지 못했습니다.
