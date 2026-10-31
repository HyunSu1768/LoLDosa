# 라인전·웨이브 관리 핵심 개념 (플래티넘 정글러용 학습 자료)

> **방법 메모 (먼저 읽을 것)**
> - 이 세션에서 WebFetch로 열려고 한 호스트는 모두 "outside the session's allowed network domains"로 막혔다: esports.gg, blog.loltheory.gg, www.sheepesports.com, lolmeta.gg, games.gg. 이전 세션 노트에 따르면 leagueoflegends.com, wiki.leagueoflegends.com, leagueoflegends.fandom.com, mobalytics.gg, riftpatchnotes.com도 막혀 있었다.
> - 그래서 **아래 인용은 모두 검색 도구가 돌려준 스니펫/요약**이다. 앱에 그대로 싣기 전에 원문과 대조해야 한다. 특히 Riot 패치노트의 수치가 그렇다. 원문을 보려면 위 도메인들을 세션 네트워크 설정에서 허용해야 한다.
> - **중복 회피**: 웨이브 상태 정의, 라인 주도권, 귀환 동기화, 26.1 미니언 스폰 상수(첫 웨이브 0:30, 30s/25s/20s 주기, 첫 대포 1:30), 치터 리콜 기본 정의는 `research_notes/롤 턴 개념과 정글 운영/english_tempo_wave_prio.md`의 §2·§3·§4·§6과 `korean_turn_concept.md`의 §3에 이미 있다. 여기서는 그 내용을 **요약 참조만** 하고 아래를 새로 다룬다: 포탑 방패/골드, 포탑 어그로, 레벨 레이스, 스펠 추적, 다이브, 라인 스왑, 26.10 미니언 어그로 변경, 사이드 관리, 정글러 활용법.
> - 출처 표기의 "(스니펫)"은 검색 요약을 통해 확인했다는 뜻이다.

---

## 1. 각 개념의 정확한 정의와 메커니즘 (한국어 용어 vs 영어 코칭 용어)

### Takeaway
라인전 개념은 거의 모두 **"웨이브가 어디에 있고, 누가 먼저 움직일 수 있는가"**라는 질문으로 모인다. 웨이브 상태(슬로우 푸시·빠른 푸시·프리징·크래시·바운스·빅웨이브)가 시간 창을 만든다. 그 창을 다시 레벨 레이스, 포탑 방패, 다이브, 스펠 쿨다운이 결정한다. 정글러는 "웨이브 위치 + 상대 점멸 유무 + 레벨"을 보고 갱·다이브·방패 압박 여부를 고른다.

### Cited Findings

#### 1-1. 웨이브 상태 (슬로우 푸시 / 빠른 푸시(하드 푸시, 박기) / 프리징 / 크래시 / 바운스 / 빅웨이브)
상세 정의는 기존 노트 `english_tempo_wave_prio.md` §2를 본다. 아래는 정글러 관점에서 새로 추가한 인용이다.
- 용어 대응: 프리징 = freeze, "라인을 그대로 유지시키는 것". 빅웨이브(big wave/stacked wave)의 장점은 "라인 주도권을 얻게 되는 것". — [나무위키 리그 오브 레전드/전략](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%A0%84%EB%9E%B5) (기존 노트에서 재인용)
- 오브젝트 전 슬로우 푸시: "Roughly a minute before a dragon or Rift Herald, build a slow push. When it crashes, the enemy has to choose between the objective and their tower." — [LoL Theory wave management](https://blog.loltheory.gg/wave-management-league-of-legends/) (스니펫)
- 갱과 웨이브 위치: "If you are pushing the wave under their tower, your Jungler may be unable to gank for you... if you want the Jungler to gank, you need to have the wave in a position where they can gank for you, such as in the middle of the lane or near to your tower" — [Mobalytics gank setup](https://mobalytics.gg/blog/gank-setup/) (스니펫)
- "The single biggest factor is wave position. If the enemy is pushed past the halfway point toward your laner's tower, they have a long run back to safety." / "Keep the wave on your side. Don't perma-push." — [LoL Theory, What Is a Gank](https://blog.loltheory.gg/what-is-gank-league-of-legends/) (스니펫)
- **26.10(2026년 5월 12일) 미니언 어그로 변경**: 적 미니언을 공격해도 더 이상 미니언 어그로가 끌리지 않는다. Riot의 설명은 "removing this action entirely from aggroing minions to prevent it feeling like minions sometimes randomly change their target"였다. 예전에는 프리징 중인 웨이브에 평타 한 번만 쳐도 어그로가 끌려 프리징이 2초 만에 깨졌는데, 이제는 **프리징을 유지하기가 쉬워졌다**. 고립된 미니언으로 별도의 슬로우 푸시를 만드는 테크닉도 사라졌다. 프로 선수들 사이에서 반발이 있었다(Drew Levin, Gen.G Arnold 코멘트). — [PCGamesN 26.10 minion aggro](https://pcgamesn.com/league-of-legends/lol-patch-26-10-minion-aggro-changes); [Upcomer: pro backlash](https://upcomer.com/league-of-legends-patch-26-10-minion-aggro-change-faces-surprising-pro-backlash/); [rdy.gg](https://rdy.gg/en/lol/news/lol-minion-aggro-changes); [esports.gg 26.10](https://esports.gg/guides/league-of-legends/lol-minions-aggro-patch-26-10/) (모두 스니펫)
  - 주의: 이 변경은 "적 미니언 공격 시"의 어그로 규칙이다. 위키의 미니언 우선순위 1순위인 "Enemy champions attacking an allied champion"(적 챔피언이 아군 챔피언을 공격하면 미니언이 그 적을 노림)은 별개 규칙이고, 이번에 바뀌었다는 근거는 찾지 못했다. — [LoL Wiki Minion](https://wiki.leagueoflegends.com/en-us/Minion_(League_of_Legends)) (스니펫)

#### 1-2. 라인 주도권 (lane priority, "prio")
- 정의와 오브젝트 연결은 기존 노트 `english_tempo_wave_prio.md` §3, `korean_turn_concept.md` §3에 있다. 핵심 인용: 프리오는 "your minion wave is pushed toward the enemy tower, so your opponent has to stay and farm while you're free to move first." — [MOBA Champion](https://www.mobachampion.com/blog/lane-priority-in-lol/) (기존 노트)

#### 1-3. 견제/딜교환 (trading / harass)
- 26.10 이전에는 "미니언을 때리면 어그로가 끌린다"는 규칙이 딜교 계산에 들어갔다. 지금은 적 챔피언을 직접 공격할 때만(위키 우선순위 1번) 미니언 어그로가 의미 있게 작동한다고 볼 수 있다. 이 문장은 위 26.10 출처들을 종합한 것이다. 26.10 이후 딜교 요령을 정리한 1차 코칭 자료는 찾지 못했다. Gaps 참고.
- 레벨 2 선점 후 딜교: "take full priority in the lane with the extra stats and ability you gain from level two" — [Sheep Esports, 2026-02-27](https://www.sheepesports.com/articles/new-level-two-first-wave-strategy-gives-top-lane-instant-priority/en) (스니펫)

#### 1-4. CS·막타 (last hitting / CS)
- 26.1에서 웨이브가 더 자주(14분 이후 25초, 30분 이후 20초) 나오지만, 대포 웨이브에서 근접 미니언 1기가 빠지고(30분 이후에는 근접 1, 원거리 1) 슈퍼·대포 미니언의 가치가 낮아졌다. 기존 노트 §6의 [Riot 26.1 노트](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/)를 재참조했다.
- 26.10: Minion Slayer(미니언 학살자 계열) 대 미니언 온힛 보너스가 조정됐다. 대포 미니언 대상 값은 현재 체력의 6%에서 5%로 내려갔다. — [riftpatchnotes minions](https://www.riftpatchnotes.com/lol/system/minions) (스니펫)

#### 1-5. 대포 웨이브 (cannon wave, 대포 웨이브/대포 미니언)
- 첫 대포는 3번째 웨이브(26.1 기준 1:30 스폰)다. 15분까지는 3웨이브마다 1기이고, 이후 주기는 기존 노트 §6에 있다. 14:00/15:05 경계는 미확인이다.
- "Never recall on a cannon wave unless forced to." — 기존 노트 §2 ([Boosting Market](https://boostingmarket.com/blogs/lol-wave-management-guide/))

#### 1-6. 치터 리콜 (cheater recall, 한국어로도 "치터 리콜")
- 용어는 분석가 **Nick "LS" De Cesare**가 만들었다. "Geprägt wurde der Begriff vom LoL-Analysten Nick „LS" De Cesare." 방법은 "die dritte Welle, die erste Kanonen-Welle, mit voller Wucht in den gegnerischen Turm zu shoven. Direkt nachdem diese Welle einschlägt, startest du deinen Recall." — [WeCoach DE](https://wecoach.gg/de/blog/article/how-to-cheater-recall-in-league-of-legends) (스니펫)
- **구버전 수치 경고**: "~3:00에 크래시, 450–500g"은 26.1 이전 기준이다. 기존 노트 §2를 본다. 26.1 이후 첫 대포 웨이브는 약 35초 앞당겨졌다.

#### 1-7. 로밍 (roaming)
- 미드의 로밍 공식: "Crash the wave, walk to a side lane, make a play, return to mid before the next wave crashes into your tower." 미드는 다음 경우에 슬로우 푸시를 늦춘다: "When you see an immediate opportunity in a side lane (enemy bot lane fighting, your jungler diving top)." — [Dodge.gg Mid Lane Guide 2026](https://www.dodge.gg/en-US/lol/news/mid-lane-guide-2026) (스니펫. 해당 문장이 이 페이지의 것인지 검색 요약이 명확히 구분하지 않았다)
- "Don't slow push mid when the enemy jungler could dive you." — 같은 검색 결과(Dodge.gg 또는 LoL Theory) (스니펫)

#### 1-8. 라인 스왑 (lane swap)
- **2025 (25.05)**: Riot이 "Lane Swap Detector"를 도입했다. 적 비정글 챔피언 2명이 탑이나 미드에 나타나면 1차 포탑이 95% 피해 감소를 받았고, 모든 포탑의 Fortification 버프가 제거됐다. Riot 리드 디자이너는 이 조치를 "temporary, heavy-handed by necessity"라고 했다. — [Sheep Esports: Riot heavily nerfing lane swaps](https://sheepesports.com/articles/lol-riot-patches-out-lane-swaps/en); [LoL Wiki Lane Swap Detector](https://wiki.leagueoflegends.com/en-us/Lane_Swap_Detector); [esports.gg](https://esports.gg/news/league-of-legends/league-of-legends-swing-at-lane-swaps-community-erupts/) (스니펫)
- 감지기의 부작용으로 "bad actors on your team may simply sit in your lane, proc-ing the lane swap detector" 문제가 지적됐다. — [Know Your Meme 정리](https://amp.knowyourmeme.com/memes/events/league-of-legends-anti-lane-swap-mechanic-controversy) (스니펫. 2차 출처)
- **2026**: 탑·미드·바텀에 **포지션 퀘스트(role quests)**가 생기고 "Lane Swap Detected"는 영구 제거된다. 퀘스트 진행도가 배정 라인에 묶여 있어 스왑이 억제된다. — [Dotesports: all changes S1 2026](https://dotesports.com/league-of-legends/news/all-changes-league-of-legends-season-1-2026) (스니펫, 2차 출처). 반론으로 "Early lane swaps are starving top laners of matchup consistency"라며 스왑이 여전히 나온다는 분석도 있다. — [eXputer](https://exputer.com/features/lol-early-lane-swaps-top-lane-matchup-consistency/) (스니펫)
- 솔로랭크 플래티넘에서는 계획된 스왑이 드물다. 프로 경기 시청 이해용 개념으로 다루면 된다(추론).

#### 1-9. 다이브 / 포탑 다이브 (tower dive, 다이브)와 포탑 어그로 규칙 (tower aggro)
- **기본 우선순위**: 포탑은 사거리 안의 최우선 대상을 "until it dies, leaves the 750 attack range, or becomes untargetable" 동안 계속 공격한다. 기본적으로 미니언이 챔피언보다 먼저다. — [LoL Theory tower dive](https://blog.loltheory.gg/tower-dive-lol/); [Scan LoL 101](https://scan.co.uk/info/guide/leagueoflegends101) (스니펫)
- **챔피언 보호 규칙(어그로 전환)**: "if an enemy champion deals damage to an allied champion within 1400 range of the turret, the turret immediately switches to that enemy champion, regardless of priority." — [LoL Theory](https://blog.loltheory.gg/tower-dive-lol/) (스니펫. 1400 수치는 공식 위키에서 재확인 필요)
- **어그로 해제**: "If the turret is shooting you and you start attacking an enemy minion, the turret does not automatically switch off." 해제하려면 사거리 밖으로 나가거나 대상 지정 불가가 되어야 한다. — [Mobafire advanced tower guide (2012, 구버전)](https://www.mobafire.com/league-of-legends/build/advanced-tower-guide-possible-trolling-249073) (스니펫)
- **Warming Up(누적 피해)**: 공식 위키 요약은 챔피언을 한 번 맞힐 때마다 피해가 +50%, 최대 +150%다. 마지막으로 챔피언을 맞힌 지 5초가 지나면 초기화되고, **대상을 바꿔도 초기화되지 않는다**. 구 Fandom 버전은 40%/120%였는데, 구버전으로 보인다. — [LoL Wiki Turret](https://wiki.leagueoflegends.com/en-us/Turrets) vs [Fandom Turret](https://leagueoflegends.fandom.com/wiki/Turret) (스니펫, **수치 충돌**)
- "three or four shots is enough to kill any squishy and most bruisers outright at outer turret damage levels." 볼리베어 궁극기 다이브는 포탑이 공격을 멈추므로 Warming Up을 무시한다. — [LoL Theory](https://blog.loltheory.gg/tower-dive-lol/) (스니펫, 비공식)
- **Reinforced Armor**: 주변에 적 미니언이나 소환된 전령이 없으면 포탑이 받는 피해가 80% 줄어든다. 마지막 대상이 죽거나 사라진 뒤 3초 지연 후 재활성화된다. — [LoL Theory](https://blog.loltheory.gg/tower-dive-lol/) (스니펫); [LoL Wiki Reinforced Armor](https://wiki.leagueoflegends.com/en-us/Reinforced_Armor_(Turret_Item))
- 다이브 실패 위험: 미드-정글 다이브를 잘못 판단하면 "giving a double or triple kill to the enemy top-laner or the bot lane can be disastrous." — [Sportskeeda](https://www.sportskeeda.com/esports/what-mid-jungle-prio-professional-league-legends) (기존 노트 재인용)

#### 1-10. 포탑 방패(포탑 플레이트, turret plates)와 방패 골드
§2(2026 변경)에서 자세히 다룬다.

#### 1-11. 레벨 우위 (2/3/6 레벨 레이스, level 2/3/6 race)
- **바텀(2인 라인)**: 레벨 2에는 첫 웨이브와 그다음 근접 미니언 3기가 필요하다. "reaching level 2 takes one wave of minions plus three melee minions". 미니언을 하나라도 놓치면 동시에 레벨 2를 찍지 못한다. 상대보다 먼저 "first nine minions"를 처리하는 것이 핵심이다. — [Red Bull macro timing windows](https://www.redbull.com/us-en/the-importance-of-the-macro-game-timing-windows); [Mobalytics 6 tips from your ADC (support guide)](https://mobalytics.gg/blog/lol-6-tips-from-your-adc-a-supports-guide/) (스니펫. 문맥상 바텀 기준)
- **탑 레벨 2 신(新)전략 (26.4, 2026년 2월)**: KaguraMVP(챌린저)가 공개했다. 미드가 첫 미니언을 빨리 잡아 미드 웨이브를 탑보다 먼저 맞닿게 하고, 탑 라이너가 탑 미니언이 죽기 전에 강을 건너 경험치를 챙겨 **첫 웨이브만으로 레벨 2**를 찍는다. 수혜 챔피언은 "Sett, Darius, Pantheon, Riven, or Trundle"이다. 상대가 레벨 타이머를 신경 쓰는 고티어에서 잘 통하고 "less consistent in lower elo"라고 했다. — [Sheep Esports 2026-02-27](https://www.sheepesports.com/articles/new-level-two-first-wave-strategy-gives-top-lane-instant-priority/en) (스니펫)
- **정글 레벨 3**: 표준 공격 동선은 3캠프로 레벨 3을 찍은 뒤 가까운 라인을 갱하는 것이고, 첫 갱 창은 약 2:30–3:00이다. 더 위험한 "level 2 cheese gank"(버프 1개 + 작은 캠프 1개)는 실패하면 크게 손해 본다. — [Dodge.gg Jungle Guide 2026](https://www.dodge.gg/en-US/lol/news/jungle-guide-2026) (스니펫. 26.1에서 첫 웨이브가 0:30으로 당겨진 것이 이 시간에 반영됐는지는 불명확)
- 정글러는 보통 3레벨(스킬 3개)부터 갱을 다닌다. 라이너는 2번째 웨이브를 민 직후 갱 방지 와드를 쓴다. — [Threads @learn.ezlol](https://www.threads.com/@learn.ezlol/post/DHw4jKAzXRS) (기존 노트 재인용)

#### 1-12. 소환사 주문 추적 (점멸·점화 쿨타임, summoner spell tracking)
- **점멸(Flash)**: 기본 쿨다운 300초. — [LoL Fandom Flash](https://leagueoflegends.fandom.com/wiki/Flash) (스니펫). 최근 점멸 변경은 26.4의 "Cursor epic monster priority radius reduced to 125 from 300"으로, 쿨다운 변경이 아니다. — [riftpatchnotes summoner spells](https://www.riftpatchnotes.com/lol/system/summoner-spells) (스니펫)
- **점화(Ignite)**: **180초는 구버전**이다. 25.9에서 180초에서 210초로 늘었다. — [riftpatchnotes Ignite](https://www.riftpatchnotes.com/lol/spell/ignite) (스니펫)
- 소환사 주문 가속은 표기 쿨다운이 아니라 재충전 시간만 줄인다. — [LoL Wiki Summoner spells](https://wiki.leagueoflegends.com/en-us/Summoner_spells) (스니펫)
- 갱 판단: "Summoner spells — is Flash down? Tab to check or ask your laner. A flashless target is roughly twice as easy to kill." — [LoL Theory, What Is a Gank](https://blog.loltheory.gg/what-is-gank-league-of-legends/) (스니펫. "2배"는 저자의 경험칙이다)

#### 1-13. 매치업 지식 (matchup knowledge)
- 레벨 2 강자로 Sett, Darius, Pantheon, Riven, Trundle이 꼽혔다(위 Sheep 기사). 이들 상대로 아군 탑이 레벨 2를 먼저 내주면 2:00 전후로 탑이 위험해진다는 신호다(추론).
- 매치업별 파워 스파이크를 체계적으로 정리한 2026 1차 자료는 이번 세션에서 확보하지 못했다. Gaps 참고.

#### 1-14. 중후반 사이드 라인 관리 (side-lane management)
- "ADCs rotate mid after lane as this is the safest lane for them due to it being the shortest." 사이드 웨이브는 "go to side lanes to catch waves only; don't push them out"이다. — 검색 요약 내 가이드/Reddit 답변(출처 페이지 미특정. [LoL Theory wave mgmt](https://blog.loltheory.gg/wave-management-league-of-legends/), [guildorder lane-phase wave management](https://guildorder.com/games/league/guides/lane-phase-wave-management) 중 하나) (스니펫, 신뢰도 낮음)
- 탑은 길고 고립되어 있어서 "a top laner who shoves mindlessly into an isolated lane is farming for the enemy jungler." — 같은 검색 결과(Dodge.gg/LoL Theory) (스니펫)
- 26.3: Riot은 "too difficult for teams to convert a winning teamfight into meaningful progress toward the enemy base, while split-pushing strategies have allowed towers to fall a little too quickly"라고 판단했다. 그래서 포탑 임시 저항(Bulwark, 방패당 저항)을 **20–100에서 30–50으로**(주변 적 챔피언 수 기반) 바꿨다. 커뮤니티 해석은 "솔로 푸시는 어려워지고 팀 푸시는 쉬워졌다"이다. — [Riot Patch 26.3 Notes](https://www.leagueoflegends.com/en-au/news/game-updates/patch-26-3-notes/); [esports.gg 26.3](https://esports.gg/guides/league-of-legends/lol-patch-notes-26-3-champions-bounties-turret-plates-vision/); [dtgre 26.3 해설](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html) (스니펫)

### Inferences
- **한국어 vs 영어 용어 대응표** (커뮤니티 관용 표현. 개별 출처는 위·기존 노트에 있다):
  | 한국어 | 영어 | 비고 |
  |---|---|---|
  | 라인 박기 / 밀어넣기 / 빠른 푸시 | fast push, hard shove, crash | "박다" = 포탑에 크래시 |
  | 쌓아 밀기, 빅웨이브 만들기 | slow push, stack, big wave | |
  | 프리징, 라인 당기기 | freeze, hold | "당기기"는 프리징 직전 상태를 넓게 지칭 |
  | 라인 튕김 / 되돌아옴 | bounce | |
  | 주도권, 라인 주도권, 선턴 | (lane) priority, prio, tempo | |
  | 딜교(딜교환), 견제 | trading, harass, poke | |
  | 막타, CS | last hit, CS | |
  | 대포 웨이브 | cannon wave, siege wave | |
  | 치터 리콜 | cheater recall | LS가 만든 용어 |
  | 로밍 | roam | |
  | 라인 스왑 | lane swap | |
  | 다이브 | tower dive | |
  | 포탑 방패(플레이트), 방패 골드 | turret plates, plate gold | |
  | 포탑 어그로 | tower aggro | |
  | 2렙 싸움, 6렙 타이밍 | level 2/3/6 race / spike | |
  | 점멸 체크, 스펠 체크 | flash timer, spell tracking | |
  | 사이드 관리, 스플릿 | side-lane management, split push | |
- 26.10으로 프리징을 걸기는 쉬워졌다. 플래티넘 구간에서는 라이너들이 프리징을 더 자주 쓰거나 "의도치 않게" 유지할 가능성이 있다. 정글러에게는 "적이 프리징을 걸었는데 아군 라이너가 미니언을 받으러 들어가는" 상황(=적 정글 갱 각)이나, 반대로 "아군 프리징으로 적이 과하게 나오는" 상황(=우리 갱 각)이 늘어날 수 있다. 데이터로 확인되지 않은 추론이다.
- 6레벨 레이스(궁극기 선점)는 출처를 확보하지 못했다. 원칙적으로 2/3레벨과 같은 논리(먼저 찍는 쪽이 일시적 우위)를 쓰지만, 수치(필요 미니언 수)는 미확인이다.

### Gaps
- **솔로 라인 레벨 2/3/6에 필요한 정확한 미니언 수**를 신뢰할 출처로 확보하지 못했다. 흔히 "첫 웨이브 + 근접 1기 = 솔로 레벨 2"라고 하지만 이번 세션에서 출처를 찾지 못했다. 위키의 Experience 페이지에서 확인해야 한다.
- 26.10 이후 딜교 요령과 프리징 테크닉을 다룬 코칭 콘텐츠(Coach Curtis, LS, Skill Capped)는 접근하지 못했다.
- 포탑 어그로 1400 범위, Warming Up 50%/150% 수치를 공식 위키 원문으로 대조하지 못했다(fetch 차단).
- 매치업 데이터는 이 프로젝트의 로컬 DB(정글 매치업 통계)로 보완하는 편이 현실적이다(추론).

---

## 2. 2026 시즌 관련 변경점 (26.1 미니언·포탑 방패·미니언 대 포탑 피해 등)

### Takeaway
2026 시즌에서 라인전 시간표와 포탑 경제가 크게 바뀌었다. **첫 웨이브 0:30**(기존 노트 참조). 포탑 방패는 **14분에 사라지지 않고 영구**이며, 대신 **11분부터 가치가 분당 10g씩 깎여 최대 −40g**이다. 2차·3차 포탑에도 방패가 생겼다. **미니언의 구조물 피해는 55%에서 60%**로 올랐다. 이후 26.3에서 솔로 스플릿이 너프됐고, 26.10에서 미니언 어그로 규칙이 바뀌었다. 영어/한국어 가이드 대부분이 아직 "14분 방패 소멸, 1:05 첫 웨이브"를 쓰고 있으니 **구버전으로 표시**해야 한다.

### Cited Findings
- **사전 발표(2025년 12월 개발자 업데이트)**: "Tier 1 turret plates no longer disappear after 14 minutes." "Tier 2 and 3 turrets gain three plates each, with gold granted plate-by-plate instead of only on tower kills." — [esports.gg lane & turret changes 2026](https://esports.gg/news/league-of-legends/lane-turret-changes-lol-2026/); [Sheep Esports S1 2026](https://www.sheepesports.com/en/all/articles/league-of-legends-2026-s1-gameplay-changes-atakhan-removed-new-plates-on-t2-and-t3-nashor-back); 한국어 공식: [개발 인사이드 2026 시즌 1 게임플레이 미리보기](https://www.leagueoflegends.com/ko-kr/news/dev/dev-2026-season-one-gameplay-preview/); [아이뉴스24](https://www.inews24.com/view/1913046) (스니펫)
- **최종 26.1 패치(2026년 1월)**: 사전 발표와 다른 점이 있다(**발표와 최종 사이 충돌**).
  - "All turrets except Nexus turrets now have permanent turret plates"이고 2차(inner)·억제기 포탑은 **방패 5개**다(사전 발표는 3개).
  - 방패 획득 트리거는 잃은 체력 "10/25/45/70/100%"다.
  - "plate value reduces by 10g per minute at minute 11, capped at -40"
  - "local gold from turret kill has been removed (was 250g), replaced by gold distributed through the new plate system"
  - 1차 포탑은 11분부터 방어력·마법저항력이 분당 15씩 줄어 최대 −60이다.
  - 2차 포탑은 방패 5개에 총 600골드가 분배된다.
  - 출처: [Riot Patch 26.1 Notes](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [LoL Wiki V26.01](https://wiki.leagueoflegends.com/en-us/V26.01); [Leaguepedia Patch 26.01](https://lol.fandom.com/wiki/Patch_26.01); [lolmeta.gg Turret plates and the clock](https://lolmeta.gg/learn/turret-plates-and-the-clock) (모두 스니펫. 검색 요약이 각 문장의 정확한 출처를 구분하지 않았다)
- **1차 포탑 방패 기본 골드**: 한 출처는 "125에서 120으로" 줄었다고 한다. 다른 출처는 "outer turrets plate breaking granting 160 gold (divided among nearby champions)"라고 한다(**충돌**). "untaken plate is still worth 120 gold at forty minutes"라는 문장은 11분 감쇠 규칙과 모순된다. — [esports.gg 26.3 / altchar / dtgre 검색 요약](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html); [lolmeta.gg](https://lolmeta.gg/learn/turret-plates-and-the-clock) (스니펫)
- 첫 포탑 골드와 첫 킬 골드가 별도 보상으로 돌아왔다: "First Blood and First Turret gold return as discrete rewards: 100 gold and 300 gold". — [esports.net S1 2026 guide](https://www.esports.net/wiki/guides/lol-season-changes-2026/) (스니펫)
- **미니언 대 구조물 피해**: 26.1에서 55%에서 60%로 올랐다. riftpatchnotes는 이 항목을 "nerf" 머리말 아래 두었는데, 증가와 모순되니 표기 오류로 보인다. — [riftpatchnotes minions](https://www.riftpatchnotes.com/lol/system/minions); [Mobalytics all season changes](https://mobalytics.gg/lol/guides/all-season-changes-guide) (스니펫)
- **26.3**: Bulwark 방패당 임시 저항이 20–100에서 30–50으로 바뀌었다(위 1-14). 같은 패치에서 현상금(bounty) 감가가 빨라졌다. — [Riot Patch 26.3 Notes](https://www.leagueoflegends.com/en-au/news/game-updates/patch-26-3-notes/); [Leaguepedia 26.03](https://lol.fandom.com/wiki/Patch_26.03) (스니펫)
- **26.4**: 점멸의 에픽 몬스터 커서 우선순위 반경이 300에서 125로 줄었다(쿨다운 불변). — [riftpatchnotes summoner spells](https://www.riftpatchnotes.com/lol/system/summoner-spells) (스니펫)
- **26.10**: 미니언 어그로 변경(위 1-1), Minion Slayer 대포 대상 6%에서 5%로. — 위 출처들
- **26.12**: 소환사 주문 변경은 강타 버그 수정뿐("dying before it upgraded at 48 seconds would keep it at one charge")이다. — [riftpatchnotes summoner spells](https://www.riftpatchnotes.com/lol/system/summoner-spells) (스니펫)
- **라인 스왑**: 2026년에 Lane Swap Detector가 제거되고 포지션 퀘스트로 대체됐다(위 1-8).
- **텔레포트**: LCK 선수들은 2026 프리시즌 패치 후에도 "Teleport still essential for top lane"이라고 했다. — [Inven Global datalab](https://www.invenglobal.com/datalab/articles/20054/lck-players-react-to-2026-preseason-patch-teleport-still-essential-for-top-lane-jungle-rewards-underwhelming) (기사 제목 스니펫)

### Inferences
- **구버전 경고 목록** (학습 자료에서 "옛날 정보" 배지를 달아야 할 항목):
  1. "포탑 방패는 14:00에 사라진다" → 26.1부터 영구이고, 11분부터 가치가 감쇠한다.
  2. "방패당 160g" 또는 "125g" → 26.1 이후 값은 120g으로 보인다(미확정). 11분 이후 −10g/분으로 최저 약 80g이다. 80g은 내 계산이며 출처가 명시한 값이 아니다.
  3. "포탑 파괴 시 로컬 골드 250g" → 제거됐고 방패로 분배된다.
  4. "점화 180초" → 210초(25.9~).
  5. "첫 웨이브 1:05, 첫 대포 2:05, 치터 리콜 ~3:00" → 약 35초 당겨졌다(기존 노트 §6).
  6. "미니언을 치면 미니언 어그로가 끌린다" → 26.10부터 아니다.
  7. "라인 스왑하면 포탑 95% 피해 감소" → 2025년 규칙이고 2026년에 제거됐다.
- **정글러에게 주는 의미**: 방패가 영구가 되면서 "14분 전에 방패를 따야 한다"는 마감 압박이 "11분 전이 가장 비싸다"로 바뀌었다. 첫 전령/유충 타이밍과 겹치는 **8–11분 구간의 방패 압박**이 상대적으로 가치가 높다. 11분 이후 1차 포탑은 저항도 줄어(−15/분) 깨기가 쉬워진다.
- 미니언의 구조물 피해가 60%로 오르고 웨이브가 더 자주 와서, 크래시된 웨이브를 방치하면 포탑 손실이 예전보다 빠르다. "턴을 쓰러 갔다가 포탑 방패를 잃는" 비용이 커졌다(추론).

### Gaps
- 1차 포탑 방패 기본 골드(120 vs 125 vs 160)와 26.1 이후 추가 조정 여부를 Riot 원문으로 확인하지 못했다. 이번 세션에서 leagueoflegends.com fetch가 차단됐다.
- 2차·3차 포탑 방패 수(3개 vs 5개)는 최종 패치(5개)가 우선이지만 원문 미확인이다.
- 26.1 이후 웨이브 이동 시간(사이드 32초, 미드 22초)이 바뀌었는지 미확인이다(기존 노트와 동일한 갭).
- 2026 시즌 중간(26.13 이후 10월까지)의 라인/포탑 변경은 이번 검색에서 나오지 않았다. 추가 확인이 필요하다.

---

## 3. 정글러는 각 개념을 어떻게 활용하는가 (프리징 갱, 다이브 타이밍, 방패 타이밍, 레벨 2/3 치즈, 점멸 타이머)

### Takeaway
정글러의 판단은 4가지 신호로 정리된다. **(1) 웨이브 위치**: 적이 중앙선을 넘어 아군 포탑 쪽으로 나와 있으면 갱. **(2) 상대 점멸 유무**: 점멸이 빠지면 갱 성공률이 크게 오른다. **(3) 레벨**: 우리 라이너가 레벨 우위를 잡았는지. **(4) 다이브 조건**: 웨이브가 적 포탑에 박혀 있고, 탱커가 어그로를 받을 수 있고, 적 정글이 반대편에 있는지. 2026년에는 여기에 **포탑 방패 가치 시계(11분)**가 추가됐다.

### Cited Findings
- **프리징·당겨진 라인 갱**: 적이 아군 포탑 쪽으로 밀고 나와 있으면 "they have a long run back to safety" — [LoL Theory](https://blog.loltheory.gg/what-is-gank-league-of-legends/). 반대로 "pushing the wave under their tower, your Jungler may be unable to gank... tower aggression and tower shots" — [Mobalytics gank setup](https://mobalytics.gg/blog/gank-setup/) (스니펫)
  - **충돌 메모**: 한 챌린저 강의 요약은 "If the enemy laners are pushing towards your team's tower, it becomes difficult to execute a successful gank."라고 한다. [videohighlight: Challenger Explains One Concept](https://videohighlight.com/v/0dQFQQEcIf0) (스니펫). 이 문장은 "적이 웨이브를 밀고 있는 중(=적 미니언이 많아 우리 라이너가 갇힌 상태)"을 가리키는 듯하다. "적이 중앙선을 넘어 과하게 나와 있음"과는 다른 상황으로 해석된다. 원문 맥락은 미확인이다.
- **점멸 체크**: "is Flash down? Tab to check or ask your laner. A flashless target is roughly twice as easy to kill." — [LoL Theory](https://blog.loltheory.gg/what-is-gank-league-of-legends/) (스니펫). 점멸 300초, 점화 210초(위 1-12).
- **레벨 2/3 치즈 갱**: 3캠프 레벨 3 갱 창은 2:30–3:00이다. 버프+1캠프 "level 2 cheese gank"는 고위험이다. — [Dodge.gg Jungle Guide 2026](https://www.dodge.gg/en-US/lol/news/jungle-guide-2026) (스니펫). 탑 레벨 2 선점 전략(26.4)은 아군 탑이 쓰면 2:00 이전 탑 압박, 적 탑이 쓰면 아군 탑이 위험하다는 신호다. — [Sheep Esports](https://www.sheepesports.com/articles/new-level-two-first-wave-strategy-gives-top-lane-instant-priority/en) (스니펫)
- **다이브 타이밍과 어그로**: 아군이 적 챔피언을 먼저 때리면 그 아군이 포탑 어그로를 받는다(1400 범위 규칙). 어그로를 받은 챔피언은 사거리를 벗어나거나 대상 지정 불가가 되기 전까지 계속 맞는다. Warming Up은 5초 동안 맞지 않으면 초기화되고, 대상을 바꿔도 유지된다. 그래서 **어그로를 넘겨받은 두 번째 다이버는 이미 데워진 포탑에 맞는다**. — 위 1-9 출처들 (스니펫). 1차 포탑 3–4발로 대부분 챔피언이 죽는다. — [LoL Theory tower dive](https://blog.loltheory.gg/tower-dive-lol/) (스니펫)
- **슬로우 푸시와 오브젝트 연계**: 오브젝트 약 1분 전 슬로우 푸시를 쌓으면, 크래시 때 상대가 오브젝트와 포탑 중 하나를 골라야 한다. — [LoL Theory wave management](https://blog.loltheory.gg/wave-management-league-of-legends/) (스니펫)
- **미드-정글 로밍 연계**: 미드는 "your jungler diving top" 같은 사이드 기회가 보이면 슬로우 푸시를 미룬다. — [Dodge.gg Mid Lane Guide 2026](https://www.dodge.gg/en-US/lol/news/mid-lane-guide-2026) (스니펫)
- **사이드 관리와 정글러**: 고립된 탑 라이너의 무리한 푸시는 적 정글러에게 먹잇감이 된다(위 1-14). 26.3 이후 솔로 스플릿 효율이 떨어져 팀 단위 푸시가 상대적으로 유리하다. — [Riot 26.3](https://www.leagueoflegends.com/en-au/news/game-updates/patch-26-3-notes/) (스니펫)

### Inferences (정글러 실전 체크리스트, 출처 종합 + 추론)
- **프리징 걸린 라인**
  - *적이 프리징(아군 포탑 쪽이 아니라 적 포탑 앞에 라인이 서 있음)*: 아군 라이너가 미니언을 받으러 들어가면 적 정글 갱각이다. 정글러가 해 줄 일은 둘이다. ① 적 라인 뒤쪽(적 포탑과 라인 사이) 측면에서 갱해 프리징을 깨 주기(라이너가 웨이브를 밀어 리셋할 시간을 번다), ② 그 라인 근처 시야와 카운터갱 대기.
  - *아군이 프리징*: 적 라이너가 길게 나와 있으므로 가장 쉬운 갱각이다. 퇴로가 길다.
- **다이브 체크리스트**: ① 우리 웨이브가 적 포탑에 박히는 중이거나 박힌 상태(미니언이 포탑을 먼저 맞게 함), ② 어그로를 받을 탱커/돌진형이 있음, 어그로 교대 시 Warming Up 누적 유지를 계산, ③ 적 점멸·정화·텔레포트 빠짐, ④ 적 정글 위치를 반대편에서 확인, ⑤ 첫 타격자는 체력이 많은 쪽, 포탑을 맞다가 5초 동안 빠져 있으면 리셋.
- **포탑 방패 타이밍 (2026)**: 11분 이전이 방패 1개당 가치가 가장 높다. 전령 등을 쓴 방패 압박은 8–11분에 집중하는 편이 좋다. 11분 이후 1차 포탑은 저항이 줄어(−15/분, 최대 −60) 방패보다 **포탑 철거 자체**의 의미가 커진다. 2차 포탑에도 방패 골드가 있어서 "1차 포탑 깬 후 바로 2차 방패 압박"도 골드 원천이 된다.
- **레벨 레이스 활용**: 첫 갱은 아군 라이너가 레벨 우위(2렙 선점)를 잡은 라인에 3캠프 후(2:30–3:00) 간다. 26.1의 0:30 첫 웨이브 때문에 라이너 레벨 타이밍도 예전 가이드보다 약 35초 빠르다는 점을 감안한다.
- **점멸 타이머**: 상대 점멸이 빠진 시각 +300초(5:00)를 채팅이나 핑으로 공유한다(점멸 쿨 감소 룬/아이템 미고려). 점멸이 빠진 라인은 다음 3–4분간 우선 갱 대상이다. 점화는 210초다.
- **치터 리콜 대응**: 26.1 기준 첫 대포 웨이브(1:30 스폰)가 박히는 직후에 적 라이너가 귀환할 수 있다. 그 순간은 우리 라이너가 혼자 미니언을 먹게 되는 창이다. 정글러는 그 라인의 방패나 적 정글 캠프를 노릴 수 있다.
- **흔한 실수 (정글러 관점)**
  1. 적 포탑에 박혀 있는 라인(우리 라이너가 밀고 있음)에 갱을 가서 포탑 어그로 때문에 실패한다.
  2. 점멸 있는 상대에게 레벨 2/3 치즈 갱을 가서 동선이 크게 손해 난다.
  3. 다이브할 때 첫 타격을 체력 낮은 딜러가 해서 포탑 어그로로 죽는다.
  4. 프리징 걸린 라인을 그대로 둔다. 아군 라이너가 계속 CS와 경험치를 잃는다.
  5. 구버전 상식("14분 전에 방패")에 따라 13분대에 무리하게 방패를 압박한다. 2026에는 마감이 없고 11분부터 가치만 줄어든다.
  6. 사이드 라인 웨이브를 놔두고 오브젝트를 시작해 포탑과 방패를 잃는다(26.1 미니언 구조물 피해 60%).

### Gaps
- Coach Curtis, LS, Skill Capped, Broken by Concept의 정글 갱/다이브 원문 콘텐츠는 검색 결과에 나오지 않았다. 인벤/OP.GG 한국어 정글 다이브 팁도 이번 검색에서 확보하지 못했다(관련 검색어에 무관한 결과만 나왔다).
- "점멸 없는 대상은 2배 쉽다"는 비공식 경험칙이고, 통계 근거는 없다. 이 프로젝트의 Match-V5 타임라인으로 검증하는 방법을 고려할 수 있다(`timeline_metrics.md` 참조).
- 26.10 미니언 어그로 변경이 플래티넘 구간의 갱 성공률이나 프리징 빈도에 준 영향을 다룬 데이터나 분석은 찾지 못했다.
