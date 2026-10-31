# 교전·한타·조합 개념 (Fighting, Teamfighting & Team Composition) — 플래티넘 정글러용

> 리서치 환경 메모: 이 세션은 WebFetch로 외부 도메인(wiki.leagueoflegends.com, leagueoflegends.fandom.com, mobalytics.gg, namu.wiki)을 열 수 없었음 (DNS 차단). 모든 인용은 **WebSearch 결과 요약/스니펫**에서 가져왔으므로, 앱에 넣기 전에 원문을 열어 정확한 문구를 다시 확인해야 함. 세션 네트워크 설정에서 위 도메인을 허용하면 직접 확인 가능.
> 기준일: 2026-10-31. 확인된 최신 패치 노트: 26.16 ~ 26.20.

## Q1. 개념별 정의, 코칭 인용, 한국 커뮤니티/해설 용어

### Takeaway
핵심 개념(파워 스파이크, 수적 우위, 쿨다운 창, 교전 vs 한타, 이니시/디스인게이지/필, 조합 유형)은 영어권 코칭 사이트에서 일관되게 정의된다. 조합 분류는 출처마다 이름과 개수가 다르지만 돌진(Engage), 픽(Pick/Catch), 포킹(Poke/Siege), 스플릿(Split), 보호(Protect)가 공통 뼈대다. 한국어 용어(한타, 이니시, 포킹, 받아치기, 카정)는 인벤·OP.GG 커뮤니티 용어집에서 확인된다. 다만 "수적 우위"를 공식적으로 정의한 자료는 찾지 못했다.

### Cited Findings

**파워 스파이크 (Power spike / 강해지는 타이밍)**
- 정의: Mobalytics는 파워 스파이크를 "특정 아이템을 얻는 시점에 생기는 강해지는 순간" 등 여러 종류로 분류함 ("power spikes are gained at the point of acquiring a particular item") — [Mobalytics: 5 types of power spikes](https://mobalytics.gg/blog/5-types-league-of-legends-power-spikes-examples/)
- 2레벨: 많은 챔피언이 2레벨에 CC나 올인 스킬을 얻음. 판테온은 2레벨에 W(방패 돌격, 기절 돌진)를 얻고, 오공·신짜오는 "2레벨 올인 잠재력이 매우 강하다"는 예시가 있음 — [Dignitas: Power Spikes Part 1 (Early Game)](https://dignitas.gg/articles/blogs/League-of-Legends/4663/Power-Spikes-in-League-of-Legends-Part-1-Early-Game)
- 3레벨(정글): 그웬은 "3레벨 이후 갱킹이 가능하지만 4레벨 이후가 더 흔하다"; WeCoach는 대부분의 정글러가 2:30쯤 3레벨에 도달한다고 함 — [Mobalytics Gwen jungle guide](https://mobalytics.gg/lol/champions/gwen/guide/jungle); [WeCoach: How to play jungle](https://wecoach.gg/de/blog/article/how-to-play-jungle-in-league-of-legends)
- 6레벨: "가장 잘 알려진 레벨 스파이크". 렝가 가이드는 갱킹 위협을 키우려면 "최대한 빨리 6레벨을 찍어야 한다"고 함 — [Mobalytics Rengar guide](https://mobalytics.gg/lol/champions/rengar/guide)
- 11/16레벨(궁 2·3랭크)과 아이템 스파이크의 일반 원리는 Dignitas 시리즈 Part 2(중반)에서 다룸 — [Dignitas: Power Spikes Part 2 (Mid Game)](https://dignitas.gg/articles/Blogs/League%20of%20Legends/4796/Power-Spikes-in-League-of-Legends-Part-2-Mid-Game)
- **오래된 메커니즘 경고: 신화(Mythic) 아이템은 14.1 패치(2024년 1월, 시즌 14 시작)에서 삭제됨.** Riot은 일부 인기 신화 아이템을 남기되 "정해진 중심 아이템이 아니라 매력적인 선택지"로 바꾸겠다고 함. 삭제 목록에는 Stopwatch(스톱워치), Everfrost, Luden's Tempest, Duskblade, Prowler's Claw, Goredrinker, Divine Sunderer, Galeforce 등이 있음 — [Sportskeeda: Season 14 removes Mythic items](https://www.sportskeeda.com/esports/news-league-legends-season-14-set-completely-remove-mythic-items); [esports.gg: dev update](https://esports.gg/news/league-of-legends/lol-developer-update-three-ranked-resets-a-year-and-mythic-item-system-removal); [Earlygame: Patch 14.1](https://earlygame.com/general-news/lol-patch-14.1-new-season-map-changes-balance-adjustments). → 학습 자료에서는 "신화 완성 스파이크" 대신 **"첫 레전더리 코어 아이템 완성(1코어)"**, "2코어"로 표현해야 함.

**수적 우위 (Numbers advantage)**
- "다른 조건이 같다면 수적 우위가 가장 확실한 플레이다. 미니맵을 보고 머릿수를 세라." ("A numbers advantage, all other things being equal, is the most reliable play in league. You need to look at the mini-map and count heads.") — [Mobafire (Vexroth): Taking uneven fights](https://www.mobafire.com/profile/vexroth-588862/blog/taking-uneven-fights)
- 교전과 갱의 구분: "가장 성공적인 교전은 한 팀이 상대보다 많을 때다. 수적 우위가 이미 늦었을 때야 드러나면 그것을 갱이라고 부른다." ("The most successful skirmishes are those where one team outnumbers the other. In cases where the numbers advantage is only apparent after it's already too late, it's called a gank.") — [Engadget: Summoner's Guidebook (2013, 오래됨)](https://www.engadget.com/2013-10-17-the-summoners-guidebook-how-to-get-through-a-lol-teamfight-ali.html)
- 한국어: "수적 우위"를 정의한 공식·커뮤니티 문서는 이번 검색에서 확인하지 못함(아래 Gaps 참고). "합류"는 OP.GG 용어집에 채팅 표현("합류좀")으로만 나옴 — [OP.GG 톡: 롤 용어 정리](https://talk.op.gg/s/lol/user-news/171256/%EB%A1%A4-%EC%9A%A9%EC%96%B4-%EC%A0%95%EB%A6%AC)

**쿨다운 창 (Cooldown windows / 궁·점멸 빠진 타이밍)**
- Mobatrainer: 상대가 점멸이나 핵심 궁극기가 없을 때 교전을 걸고, 우리 캐리 스킬이 쿨다운일 때는 걸지 말라 — [Mobatrainer: Teamfighting (Patch 26.13)](https://www.mobatrainer.com/guides/teamfighting)
- Tacter(챌린저 서포터 가이드): 교전을 고를 때 가장 중요하게 추적할 것이 쿨다운이며, 특히 소환사 주문. 점멸 없는 캐리는 쉬운 타겟이고, 점멸 개수에서 앞서면 더 그렇다 — [Tacter: Engage theory – when should you start a fight](https://www.tacter.com/lol/guides/engage-theory-when-should-you-start-a-fight-91576de0)
- 챔피언별 예시: 피즈는 E가 핵심 방어 스킬이므로 E가 있을 때는 들어가지 말 것 — [LoLTheory: Fizz](https://loltheory.gg/lol/synergies/fizz)

**교전 vs 한타 (Skirmish vs Teamfight)**
- 한국어 "한타": "팀파이트라고도 불리며 중반부터 시작되는 팀대팀의 충돌" — [OP.GG 톡: 초보들을 위한 롤 용어 해설집](https://talk.op.gg/s/lol/user-news/504139/)
- Mobalytics: 교전(skirmish)은 "보통 중반 무렵 팀원과 함께 적과 벌이는 여러 번의 트레이드나 결투" — [Mobalytics: 4 tips to improve skirmishing](https://mobalytics.gg/blog/lol-4-tips-to-improve-skirmishing/)
- 나무위키: 정글은 "미로같이 꼬인 지형과 레드/블루버프를 두른 중립 몬스터 덕에 소규모 교전이 자주 일어나는 지역이다" — [나무위키: 리그 오브 레전드/용어](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%9A%A9%EC%96%B4)
- 정의는 주관적: 2v2를 한타로 보는 사람도 있고 5v5만 한타로 보는 사람도 있음 — [Northeastern DS2500 프로젝트 제안서](https://course.ccs.neu.edu/ds2500sp23/proposals/118.html)

**이니시/디스인게이지/필 (Engage / Disengage / Peel)**
- 이니시: "이니시에이트의 줄임말. 한타를 하게끔 만드는 행위", 이니시에이터 = 한타를 유발하는 챔피언 — [OP.GG 톡 용어 해설집](https://talk.op.gg/s/lol/user-news/504139/); [인벤: 한타를 지배한다. 이니시에이터! (2012, 오래됨)](https://www.inven.co.kr/board/lol/2766/901)
- 필(peel): LoL 위키는 필을 "백라인, 즉 보호해 주는 아군 뒤에 서는 캐리를 지키는 것"으로 정의하고, 아군에게서 적의 시선을 돌린다면 다이브도 필이 될 수 있다고 함 ("In terms of teamfighting, peeling refers to protecting carries who are often positioned in the backline, meaning behind their protective allies.") — [LoL Wiki: Peeling](https://wiki.leagueoflegends.com/en-us/Peeling)
- 이니시/디스인게이지 해설 — [LoLTheory: Engage & Disengage](https://blog.loltheory.gg/engage-disengage-lol/); [LoLTheory: What is peeling](https://blog.loltheory.gg/what-is-peeling-league-of-legends/)
- 받아치기(counter-engage): 인벤 조합 정리 글이 포킹 조합과 함께 받아치기 전문 챔피언으로 케넨·브라움을 언급함. 정확한 정의 문구는 확보하지 못함 — [인벤: 롤에서 나오는 정석 조합의 종류 (2021)](https://www.inven.co.kr/board/lol/3369/2281418)

**프론트라인/백라인, 포지셔닝, 타겟 선정, 플랭크**
- "프론트라인 챔피언은 필이나 이니시를 할 수 있을 만큼 가까이 있어야 하지만, 팀이 아무 대응도 못 하는 사이 혼자 맞을 만큼 깊이 들어가서는 안 된다." 하이퍼캐리(징크스, 아펠리오스)는 프론트라인 뒤에 서고, 다이버(카밀)는 "옆으로 돌아 들어가 적 원딜을 지운다" — [Metabot: Teamfight positioning guide](https://metabot.gg/en/league/guides/teamfight-positioning-guide)
- 타겟 선정 원칙: "가장 가까운 안전한 타겟을 쳐라. 확신이 없으면 가장 가까운 안전한 타겟으로 돌아가라." ("Hit the closest safe target.") 거리 유지를 깨뜨리는 킬 욕심은 경계 — [Boostroom: Teamfighting basics – target selection, spacing and win conditions](https://boostroom.com/blog/teamfighting-basics-target-selection-spacing-and-win-conditions)
- 플랭크 시야: "적 정글 깊숙이 와드 하나만 있어도 탑이나 미드가 한타 도중 적 백라인 뒤로 텔레포트할 수 있다" — [Metabot](https://metabot.gg/en/league/guides/teamfight-positioning-guide)
- 한타 일반 — [Dignitas: The Art of Team Fighting](https://dignitas.gg/articles/blogs/League-of-Legends/14236/the-art-of-team-fighting-in-league-of-legends); [Mobalytics: Die less in teamfights](https://mobalytics.gg/blog/lol-die-less-in-teamfights/)
- 카이팅: 이번 검색에서는 전용 가이드를 찾지 못함(Gaps).

**조합 유형 (Team composition archetypes)**
- 돌진/이니시(Engage): 5v5 한타를 찾는 조합. 상대는 사거리 밖에 있거나 먼저 포킹해서 대응함 — [ProComps: The ENGAGE comp](https://procomps.gg/blog/engage-gamestyle.html); [Mobalytics: How to play the engage comp](https://mobalytics.gg/blog/lol-how-to-play-the-engage-team-comp/)
- 픽(Pick/Catch): "2v1, 3v2 같은 교전에서 머릿수로 앞서 적을 잡는" 조합 — [ProComps hub: Team comp matchups](https://hub.procomps.gg/?p=1024)
- 포킹/시즈(Poke/Siege): 장거리 피해, 디스인게이지, 명중률이 매우 중요함 — [ProComps hub](https://hub.procomps.gg/?p=1024); 한국어 "포킹: 상대에게 원거리 스킬을 지속적으로 날려 상대에게 체력적 압박을 가하는 행위" — [OP.GG 톡](https://talk.op.gg/s/lol/user-news/504139/)
- 스플릿(Split): 1-4 또는 1-3-1로 나눠 솔로 플레이어가 포탑을 미는 조합 — [ProComps hub](https://hub.procomps.gg/?p=1024); [Mobalytics: How to play 1-3-1](https://mobalytics.gg/blog/lol-how-to-play-1-3-1/); [Mobalytics: Split push comp](https://mobalytics.gg/blog/lol-how-to-split-push-comp/); [Gfinity: What is 1-4](https://www.gfinityesports.com/league-of-legends/league-of-legends-what-is-1-4/)
- 보호(Protect): 모든 자원을 하이퍼캐리에게 몰아주고 그 주변을 지킴. "보호는 이니시와 픽 조합을 모두 카운터하지만 교전에서는 이기지 못한다" — [ProComps: PROTECT comp guide (2022)](https://hub.procomps.gg/2022/08/protectcomp-a-complete-guide-to-league-of-legends-team-gamestyles/)
- 상성(champbop): "Attack(돌진)은 Split과 Siege에 강하고 Protect와 Catch에 약하다", "Protect는 Catch와 Attack에 강하고 Split과 Siege에 약하다" — [Champbop: Team compositions explained](https://champbop.com/league-of-legends-team-compositions-explained/)
- 이름 차이: Champbop은 Attack/Catch/Protect/Siege/Split, ProComps는 Engage/Pick/Protect/Siege/Split에 Balanced 추가. Poke와 Siege를 하나로 묶는 출처도 있음 — [Champbop](https://champbop.com/league-of-legends-team-compositions-explained/); [ProComps hub](https://hub.procomps.gg/?p=1024)
- 한국어 분류: 인벤 "정석 조합의 종류" 글이 돌진·포킹·받아치기 등을 나열함 — [인벤 (2021)](https://www.inven.co.kr/board/lol/3369/2281418)

**스케일링 vs 초반 조합**
- 후반 조합은 "후반에 빛나므로 초중반을 최소 손실로 버텨야 한다"; 스플릿 조합의 대응법은 스플리터를 초반에 늦추거나, 미드에 2~3명만 있을 때 교전을 거는 것 — [Mobalytics: How to split push](https://mobalytics.gg/blog/how-to-split-push-in-league-of-legends/); [LoLTheory: Split push](https://blog.loltheory.gg/split-push-lol/)
- 스케일링 개념 — [Dignitas: Understanding scaling](https://dignitas.gg/articles/blogs/League-of-Legends/10567/understanding-scaling-in-league-of-legends)

**드래프트 (플렉스/카운터/밴)**
- 플렉스 픽: "여러 포지션에서 쓸 수 있는 챔피언. 어느 라인으로 갈지 모르면 카운터하기 어려우므로 초반 픽으로 좋다"; "플렉스 픽을 하면 우리가 포지션을 공개하기 전에 상대가 카운터를 먼저 확정하게 만든다" — [Mobalytics: Picks & bans guide](https://mobalytics.gg/blog/picks-bans-guide/); [GuildOrder: Draft and champ select theory](https://guildorder.com/games/league/guides/draft-and-champ-select-theory)
- 카운터 픽: 레드 사이드가 마지막 픽을 가지므로 모든 적 픽을 본 뒤 카운터를 고를 수 있음 — [GuildOrder](https://guildorder.com/games/league/guides/draft-and-champ-select-theory)
- 밴: 우리 픽을 숨기는 것뿐 아니라 상대 조합의 핵심 캐리를 지우는 데도 쓸 것. "당신에게 쓰인 밴은 우리 정글의 이니시 챔피언이나 미드의 플렉스 픽에 쓰이지 않은 밴이다" — [GuildOrder](https://guildorder.com/games/league/guides/draft-and-champ-select-theory) (출처 신뢰도: 중간, 검증 안 된 통계 포함)
- 10밴 체계는 2017 시즌 도입 — [RiftFeed: LoL draft explained](https://riftfeed.gg/guides/lol-draft-everything-you-need-to-know)
- 딜 비율(AD/AP): 정글 가이드들이 팀 조합을 보고 탱커가 필요한지 딜러가 필요한지, AP/AD 균형을 맞추라고 함 — [Hotspawn: How to play jungler](https://www.hotspawn.com/league-of-legends/guide/how-to-play-jungler-in-league-of-legends); [Samurai Gamers: Jungling guide](https://samurai-gamers.com/league-of-legends/jungling-guide/)

### Inferences
- 플래티넘 학습 자료에는 Champbop/ProComps 분류를 합쳐 쓰는 것을 권장: 돌진(Engage) / 픽(Pick) / 포킹·시즈(Poke) / 스플릿·1-3-1(Split) / 보호(Protect). 받아치기(disengage/counter-engage)는 독립 조합이라기보다 보호·포킹 조합의 하위 특성으로 설명하는 것이 자연스러움.
- "상성" 표(돌진>포킹·스플릿, 보호>돌진·픽, 스플릿·포킹>보호)는 가위바위보 형태라 정글러가 기억하기 쉬움. 다만 출처는 코칭 블로그의 의견이며 데이터 근거는 없음.
- 신화 아이템 관련 문구가 있는 2023년 이전 가이드는 "1코어"로 바꿔 읽어야 함.

### Gaps
- "수적 우위"를 한국 해설·커뮤니티가 정의한 문장, 그리고 LCK 해설(인벤·포모스 인터뷰)의 직접 인용은 찾지 못함. namu.wiki·inven을 직접 열 수 없어 나무위키 "조합" 문서도 확인 못 함.
- 카이팅(kiting), 딜 프로필(AD/AP 비율 기준치)을 다룬 신뢰할 만한 전용 가이드는 찾지 못함.
- Skill Capped와 ProGuides 자료는 이번 검색에 잡히지 않음.
- 11/16레벨 스파이크의 구체적인 인용문은 확보하지 못함(Dignitas Part 2 본문 미확인).

## Q2. 정글러가 승리 조건을 파악하고 그에 맞춰 플레이하는 법

### Takeaway
코칭 자료들은 공통으로 챔피언 선택 단계에서 "우리 승리 조건은? 상대 승리 조건은?"을 묻고, 강한 쪽(또는 가장 쉬운 승리 조건)을 중심으로 플레이하며, 상대 스플리터나 캐리를 초반에 늦추라고 조언한다. 정량 데이터는 없고 코칭 의견뿐이다.

### Cited Findings
- 챔피언 선택에서 자기 챔피언의 승리 조건부터 확인할 것. 초반 챔피언은 적극적인 초반 플레이가 필요함 — [Mobalytics: 6 tips to be a better jungler](https://mobalytics.gg/blog/lol-6-tips-better-jungler/)
- 팀 픽을 보고 가장 크게 영향을 줄 수 있는 곳을 찾고, 상대 강약점과 비교할 것. "강한 쪽 중심으로 플레이하고, 팀의 가장 쉬운 승리 조건을 우선하라." 상대 정글이 더 강하면 이길 수 없는 교전을 시작하지 않도록 동선을 조심할 것 — [Hotspawn: How to play jungler](https://www.hotspawn.com/league-of-legends/guide/how-to-play-jungler-in-league-of-legends) / [Samurai Gamers](https://samurai-gamers.com/league-of-legends/jungling-guide/) (검색 요약에서 출처 구분이 모호함)
- 승리 조건을 Plan A → Plan B로 보는 프레임: "내 승리 조건은? 상대 승리 조건은?" — [r/Jungle_Mains 미러 (2023)](https://lr.in.psf.lt/r/Jungle_Mains)
- 챔피언별 예: 마스터 이는 "6레벨까지 파밍하고 Devourer(포식자) 스택을 쌓는 것"이 주된 승리 조건 — [Mobafire: Picking a jungler](https://www.mobafire.com/profile/vexroth-588862/blog/picking-a-jungler) (**오래됨: Enchantment: Devourer는 이미 삭제된 아이템이므로 개념 예시로만 쓸 것**)
- 상황별 원칙: "뒤처지면 우리 조합은 상대가 파고들 수 있는 가장 약한 승리 조건만큼만 강하고, 앞서면 가장 강한 승리 조건만큼 강하다" — [r/summonerschool (2016, 오래됨)](https://r.datuan.dev/5bmaug)
- 스플릿 상대 대응: 상대 게임 플랜이 스플리터에 달려 있으니 초반에 그를 늦출 것; 스플리터가 보이면 바로 교전을 걸 것 — [Mobalytics: Split push comp](https://mobalytics.gg/blog/lol-how-to-split-push-comp/); [Mobalytics: 1-3-1](https://mobalytics.gg/blog/lol-how-to-play-1-3-1/)
- 쿨다운 기반 판단: 상대 점멸이나 궁극기가 빠졌을 때 교전을 강제할 것 — [Mobatrainer (26.13)](https://www.mobatrainer.com/guides/teamfighting)

### Inferences
- 정글러용 픽창 체크리스트(합성):
  1. 양 팀을 5개 조합 유형으로 분류
  2. 각 팀의 스파이크 타이밍(초반 2·3·6레벨 / 1~2코어 / 후반) 비교
  3. "강한 쪽·가장 쉬운 승리 조건" 라인 선택 → 첫 동선과 갱 방향 결정
  4. 상대 승리 조건(스플리터, 하이퍼캐리)을 어떻게 늦출지 정함
  5. 우리 팀에 프론트라인과 AP/AD 균형이 부족하면 정글 픽으로 메움
- 조합별 정글 역할: 돌진 조합이면 이니시/플랭크, 보호 조합이면 필과 시야, 픽 조합이면 수적 우위 교전과 캐치, 스플릿 조합이면 반대 사이드 오브젝트 교환, 스케일링 조합이면 카정 방어·대칭 정글·손해 최소화.

### Gaps
- LCK 정글러(예: 캐니언, 오너 등)가 승리 조건을 설명한 인터뷰 직접 인용은 확보하지 못함(인벤/포모스 접근 불가).
- 플래티넘 구간에서 조합 유형별 승률 데이터는 찾지 못함.

## Q3. 최신 시즌 수치 (데스 타이머 공식, 현상금) — 패치 표기

### Takeaway
2026 시즌(26.01)에서 데스 타이머와 현상금 체계가 크게 바뀌었다는 위키 기록이 있다. 26.16에서는 1~8레벨 초반 데스 타이머가 줄었고, 26.3에서는 현상금 감소 속도가 완화됐으며, 25.09에서는 레벨에 따른 기본 킬 골드 상승이 도입됐다. 다만 여러 수치가 출처끼리 충돌하므로 앱 반영 전에 원문 확인이 꼭 필요하다.

### Cited Findings

**데스 타이머 (Death timer / 부활 대기 시간)**
- **26.16 (가장 최근 확인):** 1~8레벨 초반 데스 타이머를 12/14/16/19/22/25/28/30초에서 **10/12/14/17/20/23/26/29초**로 줄임. 9레벨 이상은 변경 없음. 같은 패치에서 초반 귀환 가속(Homeguard)을 없애고 15분부터 활성화되도록 옮김 — [Patch 26.16 notes (Riot)](https://www.leagueoflegends.com/en-us/news/game-updates/league-of-legends-patch-26-16-notes/)
- **26.01 (시즌 2026 시작):** 레벨별 기본 타이머가 1레벨 12초에서 16레벨 40초까지 오름. 게임 시간 배율이 **25분부터**(기존 10분) 적용되고, 증가량은 15초마다 5%(기존 30초마다 0.25%), **최대치는 27:30에 50%**(기존 72:00에 133%) — [LoL Wiki: V26.01](https://wiki.leagueoflegends.com/en-us/V26.01) (검색 요약 기준. 표현이 일부 모호하므로 원문 확인 필요)
- 충돌 1: LoL Wiki "Death" 페이지 스니펫에는 "15분 이후 30초마다 증가, 15~30분 0.425%, 30~45분 0.3%, 상한 50%, 최대 타이머는 55분·18레벨"이라는 설명이 있음. 이는 26.01 이전 공식이거나 캐시된 옛 버전으로 보임. 또 다른 스니펫의 "Level × 2 + 4" 공식은 같은 페이지의 표와 맞지 않음 — [LoL Wiki: Death](https://wiki.leagueoflegends.com/en-us/Death)
- 충돌 2: Swiftplay 패치 기록 페이지에는 133.3% 상한이 나옴(별도 모드이거나 옛 값) — [LoL Wiki: Swiftplay patch history](https://wiki.leagueoflegends.com/en-us/Swiftplay/Patch_history)
- 14.16(2024년 8월): 텔레포트가 라인을 잃지 않는 유일한 방법이 되지 않도록 데스 타이머를 조정함 — [Sportskeeda: Patch 14.16 notes](https://www.sportskeeda.com/esports/league-legends-patch-14-16-notes-august-14-2024-azir-buffs-corki-nerfs-death-timers-adjustments)
- 칼바람(Howling Abyss)은 레벨에만 의존: 11~40초 — [LoL Wiki: Death](https://wiki.leagueoflegends.com/en-us/Death)

**킬 골드·현상금 (Gold / Bounty)**
- **25.09:** 기본 킬 골드가 7~18레벨 구간에서 레벨마다 10g씩 올라 **최대 420g**. 양성 현상금 누적을 전투가 끝난 뒤로 미뤄서, 1대1 맞교환에서 먼저 죽은 쪽에게 셧다운이 붙지 않도록 함 — [Patch 25.09 notes (Riot)](https://www.leagueoflegends.com/en-us/news/game-updates/patch-25-09-notes/)
- **26.01:** 위키 요약에 따르면 "단계형(tiered) 현상금이 제거되어 킬 현상금이 더 이상 연속 킬/연속 데스에 기반하지 않음". 골드 현상금 21→20, 기본 경험치 현상금 32→31 — [LoL Wiki: V26.01](https://wiki.leagueoflegends.com/en-us/V26.01) (**검색 모델의 요약이므로 정확도 확인 필요**)
- **26.3:** 사망 시 현상금 감소가 "2.5골드당 1"에서 "3.5골드당 1"로, 파밍으로 인한 현상금 재증가가 "5골드당 1"에서 "7골드당 1"로 바뀜(시즌 초 너무 빠른 현상금 감소를 완화) — [Patch 26.3 notes (Riot)](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-3-notes/); [dtgre: Patch 26.3 bounty guide](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html)
- **26.19:** 클래식 모드에서 일부 챔피언(트위스티드 페이트, 질리언)이 죽어 있는 동안 받던 추가 골드·경험치를 제거 — [Patch 26.19 notes (Riot)](https://www.leagueoflegends.com/en-us/news/game-updates/league-of-legends-patch-26-19-notes/)
- 오브젝트 현상금: 오브젝트 현상금이 켜지면 지고 있는 팀원들의 챔피언 셧다운 골드는 억제됨 — [LoL Wiki: Objective bounties](https://wiki.leagueoflegends.com/en-us/Objective_bounties)
- 한 번의 킬 보상 상한은 1000골드 — [LoL Fandom: Kill](https://leagueoflegends.fandom.com/wiki/Kill) (예전 시즌 기준일 수 있음)
- 기본 킬 300g + 연속 킬 골드라는 옛 설명은 25.09 이전 자료 — [Riot boards: Upcoming bounty changes (오래됨)](https://boards.na.leagueoflegends.com/en/c/developer-corner/BQEfgyrs-upcoming-bounty-changes?show=rundown)
- 현상금 개념 해설 — [Dignitas: Bounty hunting guide](https://dignitas.gg/articles/blogs/Unknown/13752/bounty-hunting-in-league-of-legends-a-comprehensive-guide)

### Inferences
- 정글러에게 주는 의미(26.16 기준):
  - 초반(1~8레벨) 데스 타이머가 10~29초로 짧아, 초반 킬 뒤에 바로 오브젝트(공허 유충·드래곤)로 전환할 시간 창이 좁음 → 킬 직후 곧장 오브젝트를 칠지 판단해야 함.
  - 26.01 공식이 맞다면 25분 이후 타이머가 빠르게 늘어 27:30에 최대(+50%)가 됨 → 27분 이후 한타 하나로 바론/장로·넥서스까지 이어질 수 있음. "후반 한타 한 번 = 게임"이라는 점을 강조할 것.
  - 25.09 이후 킬 골드가 레벨에 따라 오르므로(최대 420g) 후반 킬이 더 비쌈. 26.3 이후 현상금은 더 천천히 줄어듦.
  - 오브젝트 현상금이 켜지면 지는 팀의 셧다운 골드가 억제되므로, 앞서는 팀 정글러는 그 상태에서 무리한 교전으로 상대에게 역전 골드를 주지 않도록 조심해야 함.
- 위키 "Death" 페이지 스니펫(15분 시작, 55분 최대)과 V26.01(25분 시작, 27:30 최대)이 충돌함. 2026 시즌 자료가 더 최신이므로 V26.01과 26.16을 우선하되, 원문 확인 전까지는 "확인 필요" 표시를 붙일 것.

### Gaps
- 26.01 이후 정확한 레벨별 기본 타이머 전체 표(9~18레벨)와 시간 배율 공식의 원문은 열 수 없어 확정하지 못함(wiki.leagueoflegends.com 차단).
- 26.01의 "단계형 현상금 제거" 이후 현재 셧다운 골드를 계산하는 정확한 공식(어시스트 골드, 첫 킬 골드 포함)은 확인하지 못함.
- 26.17~26.20 패치에서 데스 타이머나 현상금이 더 바뀌었는지는 확인하지 못함(26.20 페이지 헤더가 이상하다는 검색 측 경고 있음).
