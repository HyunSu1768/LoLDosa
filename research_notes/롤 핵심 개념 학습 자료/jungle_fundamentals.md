# 정글 기본기 (Jungle Fundamentals) — Platinum 정글러 학습 라이브러리용 리서치 노트

> **Method note (read first).** WebFetch failed for every host tried in this session: wiki.leagueoflegends.com, riftpatchnotes.com, sheepesports.com, namu.wiki. Each returned ENOTFOUND because the host is outside the session's allowed network domains. Everything below therefore comes from **WebSearch result summaries/snippets**. Quotes are the search tool's extracted text and were not checked against full pages. To verify, allow `wiki.leagueoflegends.com`, `leagueoflegends.com`, `namu.wiki`, `inven.co.kr` and re-check the numbers there.
> **No duplication:** the following are already covered in `research_notes/롤 턴 개념과 정글 운영/`, so this file only cross-references them: tempo/턴, lane priority, recall sync, cross-mapping/objective trades, 26.1 objective timers (Dragon 5:00, Grubs 8:00 one-shot, Herald 15:00, Baron 20:00, Atakhan removed) and minion wave constants (first wave 0:30).
> **Big correction to the earlier notes:** `jungler_turn_sync.md` §4/§6 says "Scuttle 3:30" and gives full-clear finish times of 3:15–3:30. Those numbers are **pre-26.1**. Under 26.1, camps spawn at **0:55** and Scuttle at **2:55** (see Q1), so every early timing moves about 35 s earlier.
> Today's date: 2026-10-31. Season 2026, live patch around 26.21.

---

## Q1. Current (2025–2026) jungle mechanics: camp spawns, respawns, Scuttle, Smite, pet/treats, role quest, XP rules, leash

### Takeaway
Patch 26.1 (Jan 2026) moved the jungle about 35 s earlier: buff camps, Wolves and Raptors spawn at **0:55**, Gromp and Krugs at **1:07**, and Scuttle at **2:55**. Smite now deals **600 / 1000 / 1400**. The pet's first evolution needs **15 treats**, and the jungle role quest completes at **35** (down from 40). Respawn timers are unchanged in the sources: small camps 2:15, buffs 5:00, Scuttle 2:30. The camp-level details below are less certain: the final-evolution treat count, exactly when Smite's second charge starts, and the current catch-up XP formula. The sources conflict or are silent on these.

### Cited Findings
**Camp spawn times (initial)**
- 26.1 Korean patch summaries: "늑대, 블루, 레드, 칼날부리 생성 시간: 55초. 돌거북, 두꺼비 생성 시간: 1분 7초. 바위게 생성 시간: 2분 55초." The same summaries list minions moving from 1:05 to 0:30 and Baron from 25:00 to 20:00. — [인벤 26.1 패치 노트](https://www.inven.co.kr/board/lol/3329/657); [루리웹 26.1 패치 노트](https://bbs.ruliweb.com/news/board/300007/read/2339910) (search snippet)
- English third-party sources say the same: "Wolves, Blue Sentinel, Red Brambleback, and Raptors at 0:55, with Gromp and Krugs at 1:07". — [Boosting Market early-game guide](https://boostingmarket.com/blogs/lol-early-game-guide/); [Boosting Market jungle tracking](https://boostingmarket.com/blogs/lol-jungle-tracking-guide/) (snippet). Sheep Esports also reports "jungle camps appear at 55 seconds" in 26.1. — [Sheep Esports 26.1](https://www.sheepesports.com/en/articles/patch-26-1-new-role-quests-atakhan-and-feats-of-strength-removed-new-items-added/en) (snippet)
- Scuttle: the LoL Wiki patch history (via snippet) lists **26.01: initial Scuttle spawn 3:30 → 2:55**. — [LoL Wiki Rift Scuttler camp](https://wiki.leagueoflegends.com/en-us/Rift_Scuttler_camp); [Boostroom Jungle Pathing 2026](https://boostroom.com/blog/ungle-pathing-explained-clear-routes-timings-and-first-ganks)
- **Outdated values to flag:** camps at 1:30 and Scuttle at 3:30 come from pre-26.1 pages, e.g. [leagueoflegendstools respawn timers](https://leagueoflegendstools.com/tools/jungle-respawn-timers/), [Leaguepedia Rift Scuttler](https://lol.fandom.com/wiki/Rift_Scuttler), and one guide "last checked July 2026" that still says 3:30. The older S11–S13 value of 3:15 is also outdated.
- Patch 26.20 (Oct 6 2026) reportedly has no camp or Scuttle spawn-time entry, so the 26.1 timings appear to still stand. A tracker says the jungle was "last adjusted in 26.16 (Aug 11 2026)", but I did not see what 26.16 changed. — search summary citing [riftpatchnotes jungle](https://www.riftpatchnotes.com/lol/system/jungle)

**Respawn timers (after kill)**
- Small camps (Gromp, Krugs, Wolves, Raptors): **2:15**. Red/Blue buffs: **5:00**. Scuttle: **2:30** respawn. — [leagueoflegendstools](https://leagueoflegendstools.com/tools/jungle-respawn-timers/); [expertgamereviews](https://expertgamereviews.com/lol-jungle-timers-tracker-ui-guide/); [Leaguepedia Rift Scuttler](https://lol.fandom.com/wiki/Rift_Scuttler) (snippets; these pages are pre-26.1, but I found no evidence that respawn timers changed)
- Tracking use of respawns: "if you see the enemy jungler take their raptors at 4:00 on a ward, those raptors will respawn at 6:15." — [Boosting Market tracking guide](https://boostingmarket.com/blogs/lol-jungle-tracking-guide/) (snippet)
- 26.1 also **removed the team-wide Red/Blue buff sharing that applied after 25:00**. — [루리웹 26.1 summary](https://bbs.ruliweb.com/news/board/300007/read/2339910); [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C)) (snippet)

**Smite (강타)**
- Base Smite deals 600 true damage to large/medium monsters and enemy minions. It has a 90 s recharge and up to 2 charges. — [LoL Wiki Smite](https://wiki.leagueoflegends.com/en-us/Smite); [Leaguepedia Smite](https://lol.fandom.com/wiki/Smite_(Summoner_Spell)) (snippets)
- 26.1: Smite tiers **600/900/1200 → 600/1000/1400** (base / Unleashed / Primal). — [Riot Patch 26.1 notes](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/) (snippet). Also: "Since Season 2026, epic monsters have higher resistances, and Smite was buffed to 600, 1,000 and 1,400 damage", which makes steals harder for a team without Smite. — [gamerstogether.cz LoL Jungle 2026](https://gamerstogether.cz/en/lol-jungle-objectives-guide/)
- **Conflict on charge timing:** the official wiki snippet says Smite "starts with one charge and gains an additional charge every 90 seconds starting from 0:48". The Fandom snippet says the second charge starts after 1:30. — [LoL Wiki](https://wiki.leagueoflegends.com/en-us/Smite) vs [Fandom](https://leagueoflegends.fandom.com/wiki/Smite). Patch 26.12 (June 9, 2026) has a bug fix about keeping charges "if a player dies before the 48-second upgrade". This supports the existence of a 0:48 timing in 2026. — [riftpatchnotes Smite](https://www.riftpatchnotes.com/lol/spell/smite) (snippet)
- Common rule: "Use one for healing during your jungle clear, and save the other for objective fights." — [gamerstogether.cz](https://gamerstogether.cz/en/lol-jungle-objectives-guide/). Don't spend both charges with Dragon about 45 s away. — previously cited in `jungler_turn_sync.md` (Boosteria / dodge.gg)

**Jungle pet (정글 펫/동반자) and treats (간식)**
- 26.1: first evolution (Unleashed Smite) **20 → 15 treats**. "Unleashed Smite now transforms once a jungle pet is fed 15 treats." — [LoL Wiki Smite](https://wiki.leagueoflegends.com/en-us/Smite); [allthings.how 26.1](https://allthings.how/league-of-legends-patch-26-1-reshapes-the-map-jungle-and-vision-game/) (snippets)
- **Conflict on the final evolution:** the V26.01 wiki snippet says "number of treats required for the final evolution reduced to 25 from 30". The Smite wiki snippet says Primal Smite comes "at 35 treats". A Sept-2026 nerfplz article still says "twenty and forty treats". Older pages list 20/40 (2023 values). — [LoL Wiki V26.01](https://wiki.leagueoflegends.com/en-us/V26.01); [LoL Wiki Smite](https://wiki.leagueoflegends.com/en-us/Smite); [nerfplz, What Happened to Leashing?](https://www.nerfplz.com/2026/09/what-happened-to-leashing-how-leagues.html). Possible reconciliation: the **role quest** counts 35 points ("1 point for each treat fed"), and the quest grants the upgraded Smite. The search tool could not confirm this.
- Jungle Role Quest (introduced with 26.1 role quests): completion **40 → 35 stacks**. Rewards: Upgraded Smite, "10 bonus gold and 10 bonus experience from jungle camps", and "4% bonus movement speed in the jungle or river, increased to 8% while out of combat". — [Riot 26.1 notes](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [LoL Wiki V26.01](https://wiki.leagueoflegends.com/en-us/V26.01) (snippets). Riot says mid-late jungle gold/XP income rises "a little", partly from the faster quest.
- Pet base DPS **20–90 → 20–150** (26.1). — [allthings.how](https://allthings.how/league-of-legends-patch-26-1-reshapes-the-map-jungle-and-vision-game/) (secondary)
- Treat mechanics: after the first evolution, the pet consumes 2 bonus treats on large-monster kills. Pets store 1 bonus treat every 60 s (90 s after the final form). — [Leaguepedia Gustwalker Hatchling](https://lol.fandom.com/wiki/Gustwalker_Hatchling) (snippet; may be pre-2026)
- Final-form perks: **Gustwalker** gives "45% bonus movement speed when you enter a brush". **Scorchclaw** gives Ember charges (burn/slow on hit), "skyrocketing to 100 charges upon killing a large monster". **Mosstomper** gives a shield plus damage reduction, which "now only affects epic monsters". — [Fandom Gustwalker](https://leagueoflegends.fandom.com/wiki/Gustwalker_Hatchling); [LoL Wiki Scorchclaw Pup](https://wiki.leagueoflegends.com/en-us/Scorchclaw_Pup); [Fandom Mosstomper](https://leagueoflegends.fandom.com/wiki/Mosstomper_Seedling) (snippets; exact 2026 numbers unverified)
- Swiftplay only: nearby allies get 30% of the gold from non-epic jungle monsters (26.1). — [Riot 26.1 notes](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/) (snippet)

**Leash (리쉬)**
- nerfplz (Sept 2026) argues that "the mechanic that made leashing work" was removed and junglers now rely on items/pets. Its history: monster-damage increases and jungle starter items in S3, then from S11 the enchantment system was dropped and the starter was rebuilt around Smite upgrades, leading to today's pets. — [nerfplz, What Happened to Leashing?](https://www.nerfplz.com/2026/09/what-happened-to-leashing-how-leagues.html) (fragmentary snippets)
- Start-side tell for tracking: "Whichever buff the enemy laners walk to at 1:20 to 1:40 to help clear is the jungler's start side." — [search set: Shelbion / Boosting Market tracking](https://shelbion.com/blog/track-enemy-jungler/) (snippet). **Flag:** 1:20–1:40 is a pre-26.1 window. Under 0:55 camp spawns, the equivalent window is about 0:55–1:10 (my inference).

**Experience / catch-up XP (경험치 따라잡기)**
- V13.17: a kill or assist below your team's average level grants bonus XP, scaling "up to 60% more experience at 4 full level difference". The same patch adjusted "jungle catch-up rounding". — [LoL Wiki Experience (champion)](https://wiki.leagueoflegends.com/en-us/Experience_(champion)) (snippet)
- History: since V5.23, monsters of a higher level than you grant "up to an additional 50% of their experience bounty" based on the level gap. Riot later announced it would stop granting catch-up XP on every monster and make every camp count for the same CS. I could not confirm the shipped form. — [Fandom Experience](https://leagueoflegends.fandom.com/wiki/Experience_(champion)); [ComicBook, catch-up XP changes](https://comicbook.com/gaming/news/league-of-legends-catch-up-experience-jungle-changes/) (about two years old)
- nerfplz Oct 2026 XP guide: shared-XP gives about 30% more total XP when more than one champion is in range. It calls this the game's "most powerful catch-up mechanic". — [nerfplz XP guide](https://www.nerfplz.com/2026/10/xp-in-lol-10-things-that-decide-how.html) (snippet; jungle-specific section not visible)
- 3-camp level 3: a Season 10 guide says "a 3 camp, level 3 start can be achieved when starting on either buff". No 2026 confirmation found. — [Sportskeeda S10 routes](https://www.sportskeeda.com/esports/league-of-legends-the-best-jungle-routes-for-season-10) (outdated)

### Inferences
- 26.x "first-clear clock" (derived, not sourced): the old full-clear finish times (fast 3:05–3:15 / medium 3:20–3:30 / slow 3:30+) assumed 1:30 spawns. Shifting by 35 s gives about **2:30–2:40 / 2:45–2:55 / 2:55+**. That lines up with Scuttle at 2:55, which was probably Riot's intent. A 3-camp gank would land around **1:55–2:25** instead of 2:30–3:00. Verify in a custom game before teaching these as fact.
- With Smite at 1400 at Primal and epic monster resistance higher, the "smite-off" in a dragon/Baron fight now favors the jungler who reached the final evolution. That makes treat tempo (killing large monsters, not skipping camps) a real objective-control resource.
- Quest rewards (+10 gold / +10 XP per camp, extra MS) reward the jungler who keeps farming mid-game. This supports a "farm between plays" playstyle (see Q5).

### Gaps
- Exact final-evolution treat count in 2026 (25 vs 35 vs 40) and how it maps to the 35-point quest. **Needs the LoL Wiki Smite / Jungle pet pages.**
- Exact Smite 2nd-charge timing (0:48 vs 1:30 after start).
- Current jungle-monster XP/gold table per camp, and whether "3 camps = level 3" still holds after 26.1.
- Current catch-up XP formula for jungle monsters in 2026.
- What 26.16 changed in the jungle.
- Exact current pet perk numbers (Mosstomper shield size, Scorchclaw burn) in 2026.

---

## Q2. Clear types and pathing planning: full clear vs 3-camp, start/end/gank side, clear speed, kiting

### Takeaway
Pathing is planned backward from the goal: decide which lane to gank (or which Scuttle or objective to contest), then pick a start buff so the route ends on that side. Korean sources call this 정버프 (bot-side buff start, ending top) or 역버프 (top-side buff start, ending bot). A **full clear (풀캠)** maximizes gold/XP and treats but gives up tempo. A **3-camp (3캠)** reaches level 3 fast for a gank or invade, but leaves you behind in farm if the play fails. Coaches rank the inputs as **ally lane priority > enemy jungler route > ally CC / enemy escapes**.

### Cited Findings
- 3캠: "빠르게 3레벨을 찍어 바로 갱이나 카정으로 이어지는 동선". If the gank/invade fails, the farm gap to the enemy jungler grows. 풀캠: clear every first-spawn camp then back. Better growth, but "템포가 늦어지고 바위게를 먹기 어렵다". — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C)) (snippet)
- Full-clear start: "블루 진영과 레드 진영 모두 블루 스타트를 하는 게 가장 효율이 좋다". — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C)) / [Inven 동선 정리](https://www.inven.co.kr/board/lol/2766/44624) (snippet; patch context unknown)
- 정버프 vs 역버프: 정버프 "탑 갱킹이나 미드 갱킹으로 연결하기 자연스럽고", 역버프 "바텀 갱킹으로 연결하기 자연스럽다". — search summary of [Inven 정글러 동선 정리](https://www.inven.co.kr/board/lol/2766/44624) / [arca.live 정글의 기초](https://arca.live/b/leagueoflegends/42075081)
- Priority order for the early route: "아군 주도권 > 상대 정글 동선 > 아군 CC 및 적 회피 수단 순서로 고려해서 초반 동선을 설정해야합니다." — [Inven / ygosu 정글 동선 예측](https://m.ygosu.com/board/lo_legend/130943/?searcht=&search=&m3=real_article&frombest=Y&page=1) (snippet; the search tool did not say which page)
- Pre-first-back sequencing: "'이득보기 > 아군 정글몹 사냥 > 귀환' 이 순으로 짜는 것이 좋음". — [DC 정글학개론 (2019–2020)](https://gall.dcinside.com/board/view/?id=leagueoflegends3&no=7330222) (older)
- Example full clear: Blue → Gromp → Wolves → Raptors → Red → Krugs → Scuttle. Full clears suit scaling junglers, 3-camp level-3 ganks suit early junglers. — [Buyboosting pathing](https://buyboosting.com/blog/jungle-pathing-and-clear-routes-league-of-legends/); [lolsuggest pathing](https://lolsuggest.com/blog/jungle-pathing-guide.html) (pre-26.1 timings)
- Clear-speed tiers (pre-26.1): fast 3:05–3:15, medium 3:20–3:30, slow 3:30+. — search summary citing [dodge.gg 2026](https://www.dodge.gg/en-US/lol/news/jungle-guide-2026) / [Boostroom](https://boostroom.com/blog/ungle-pathing-explained-clear-routes-timings-and-first-ganks)
- Wrong-side ending is a tempo error: "if your clear ends on the wrong side thirty seconds before dragon … your pathing put you out of tempo". — cited in `jungler_turn_sync.md` ([Boosteria](https://boosteria.org/guides/lol-jungle-pathing-basics-tempo-tracking-gank-windows))
- Vertical jungling (opposite-side counter-clear) is the main counter to fast clearers. The best counter-clear window against some champions is "pre-6". — [nonagames 2026](https://nonagames.com/2026/04/13/how-to-jungle-path-and-counter-clear-enemy-meta-junglers-in-league-of-legends/); [Level Legendary](https://levellegendary.com/vertical-jungling-splitting-the-map/) (snippets)

### Inferences
- How-to (synthesis): (1) In champ select, list which lane has kill pressure, CC, or a likely early push. (2) Pick the **gank side** first. (3) Choose a start that **ends** near that lane at level 3 or 4: start on the opposite-side buff. (4) If no lane is gankable, full clear toward the side with the better Scuttle/Dragon setup. (5) Check whether the end point is also where you want to be at 5:00 Dragon or 8:00 Grubs.
- Kiting camps (general knowledge, **unsourced**): attack-move, step back between autos so the camp's attack windup misses or the camp walks, pull large camps over the camp's boundary edge and use walls. Platinum mistakes include standing still in camps, leaving Krugs for last on slow champs, and smiting a camp without HP need. No 2026 source on kiting was found. Treat this as coaching consensus to verify.

### Gaps
- No Coach Curtis / Broken by Concept / Skill Capped primary content was retrievable (search never returned them).
- No 26.x-specific measured clear times per champion.

---

## Q3. Tracking the enemy jungler (정글 트래킹)

### Takeaway
Tracking stacks evidence. First, the **start side**: which buff the enemy laners leash, and which bot or top laner is late to lane or low. Second, **champion clear habits**: known preferred routes and clear speed. Third, **sightings**: wards, missing camps, Scuttle, ganks. Fourth, **respawn arithmetic**: seen at a camp at T means the camp is up again at T+2:15. With these, predict where they are and play the opposite side or counter-gank.

### Cited Findings
- Start side tells: the buff the enemy laners walk to is the start side. "If your bot lane arrives late or at lower health, the enemy jungler started bottom side." "If the enemy top laner recalls with low health and no gank happened, the enemy jungler didn't path topside early." — [Shelbion, Track the Enemy Jungler Without Wards](https://shelbion.com/blog/track-enemy-jungler/); [Boosting Market tracking](https://boostingmarket.com/blogs/lol-jungle-tracking-guide/) (snippets)
- Champion route prediction: "정글 챔피언 별로 선호되는 정글 루트가 있습니다. 그것을 이용해서 상대 정글 동선을 예측하는 플레이입니다." — [Inven 정글러 동선 정리](https://www.inven.co.kr/board/lol/2766/44624) (snippet)
- When a deep ward is cleared, infer the unseen from CS counts (나무위키, via snippet). Lens is the jungler's default trinket. — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C))
- Your own farming exposes you: "CS를 먹고 있으면 자신의 위치가 노출되기 때문에 상대 정글러에게 동선을 예측당해 카정, 역갱 등에 당할 수도 있다." — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C))
- Respawn arithmetic: seen at raptors at 4:00 means raptors are back at 6:15. — [Boosting Market](https://boostingmarket.com/blogs/lol-jungle-tracking-guide/)
- Scuttle checkpoint: many junglers finish the first clear and rotate to Scuttle at "3:15–3:45" (pre-26.1; now about 2:55). — search summary of [lol-coaching.net 2026](https://lol-coaching.net/blog/how-to-play-jungle-in-league-of-legends)
- "The worst habit is ganking without knowing where the enemy jungler is." — cited in `jungler_turn_sync.md` (dodge.gg/Boosteria)
- Gank checklist synthesized by the search tool from several 2026 guides: (1) identify start side from laner behavior, (2) check enemy clear speed and full-clear vs early-gank style, (3) check lane state (enemy pushed, no vision, no Flash), (4) time arrival to when the enemy jungler would be finishing the clear on the far side, (5) deep-ward after each gank to track the next rotation. — [dodge.gg 2026](https://www.dodge.gg/en-US/lol/news/jungle-guide-2026); [lolsuggest](https://lolsuggest.com/blog/jungle-pathing-guide.html); [getrivals](https://getrivals.com/guides/lol-jungle-pathing-guide/)

### Inferences
- A Platinum tracking routine (synthesis): at 0:55–1:10, note which buff the enemy laners stand at, then write "start = X". At about 1:45–2:10 the enemy reaches level 3 near the opposite buff, so flag the lane on the **end side** as at risk. At 2:55, Scuttle shows who full-cleared. After every sighting, add 2:15 (small camps) or 5:00 (buffs) and ping the timers.
- The level gap on the scoreboard (enemy jungler level vs. elapsed time) shows whether they are full-clearing or skipping camps. This is unsourced but standard.

### Gaps
- No quantified tracking accuracy data. No primary coach (Curtis, BBC) quotes retrieved.

---

## Q4. Ganking fundamentals and counter-ganking (역갱) / covering

### Takeaway
A good gank needs a **target state**: the enemy is pushed up, lacks vision or Flash, and your laner has CC or damage. It needs an **angle** that dodges wards; side or lane-behind ganks are easy but easy to ward. It needs **timing**: when the enemy jungler is known to be far away. **역갱** means pre-positioning where you predict the enemy jungler will gank or dive. It works best when your lane is low or a big wave has built up, but because the angle is obvious, the enemy may be waiting for it.

### Cited Findings
- 갱 definition: "정글러가 특정 라인에 영향을 끼치는 걸 말합니다", as opposed to 역갱. — [Inven, 정글러의 갱킹 기초가이드](https://www.inven.co.kr/board/lol/2766/34332) (old post)
- 역갱 (나무위키): predict the enemy jungler's gank timing and wait nearby in advance. — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C)) (snippet paraphrase)
- Side gank: "가장 난이도가 쉬운 갱킹이며 동선낭비가 적고 갱킹성공률이 가장 높은 루트입니다. 다만 … 와드를 단 한개만 박아도 대처할수있다". — [Inven 갱킹 기초가이드](https://www.inven.co.kr/board/lol/2766/34332) (old)
- Cover/back-up: "웨이브가 크게 쌓였거나, 아군 팀원의 체력이 좋지 않다면 우선적으로 백업을 가서 다이브에 대비한 역갱 각을 봐야합니다." Caveat: "굉장히 보기쉬운 갱킹 각이기 때문에 상대 정글이 역갱을 보고 있을 위험도 큽니다". — [Inven / 나무위키 (search set)](https://www.inven.co.kr/board/lol/2766/34332)
- Frozen waves: don't force a gank; "웨이브를 타워까지 밀어 넣을때까지 라인 근처에서 백업". — cited in `jungler_turn_sync.md` (나무위키)
- MOBA Trainer (26.13 page): lane priority decides whether you can gank or ward deeper, and you should avoid forcing plays where the enemy has priority. — [MOBA Trainer Ganking](https://www.mobatrainer.com/guides/ganking) (summary, cited in earlier notes)

### Inferences
- Gank checklist for the library (synthesis, partly sourced above): **Where is the enemy jungler? → Enemy wave position (pushed toward you = good) → Enemy Flash / escape up? → My laner's CC + HP + can they follow? → Ward coverage on my approach (lane brush, river, tri) → After: what's next (plates, Scuttle, Dragon, recall)?**
- Platinum mistakes (synthesis): ganking into a crashing or frozen wave under the enemy tower; walking through the warded river brush; ganking a lane with no CC follow-up; staying after a failed gank instead of going back to camps; ignoring a cover chance when your laner is low and the enemy has a big wave.

### Gaps
- No 2026 source covering gank angles, Flash-baiting, or the timing of using CC first vs. laner-first engage. The search explicitly returned nothing on "ganking angles, lane states, flash".

---

## Q5. Invading & counter-jungling (카정), farming vs fighting (정글 효율/개입), power curves, item basics

### Takeaway
Invade only with **information plus priority**: the enemy jungler is seen on the opposite side, your nearby lanes can move first, and your champion can fight or escape. The best windows are right after the enemy shows elsewhere, after you win Scuttle, or after you kill them. Steal buffs and large camps, not small ones. A full-clearing enemy can be punished with a blue invade. Sources say little on farm-vs-fight balance and archetype power curves.

### Cited Findings
- "Invade when you know the enemy jungler is on the opposite side of the map, your nearby lanes have priority, and your champion can fight or escape if caught. The best invade windows are immediately after the enemy jungler shows on a ward or ganks a lane." — [dodge.gg Jungle Guide 2026](https://www.dodge.gg/en-US/lol/news/jungle-guide-2026) / [buildzcrank 2026](https://buildzcrank.com/en/blog/jungle-guide-lol-2026/) (snippet; the search tool did not say which page)
- After winning Scuttle, the enemy's nearby camp is "vulnerable for 30–60 seconds". After killing the enemy jungler, take their nearby camps at once: "This doubles the punishment for their death." — same 2026 search set ([itemgame 2026](https://itemgame.com/en-my/blog/league-of-legends-jungle-macro-guide-2026/), [getrivals](https://getrivals.com/guides/lol-jungle-pathing-guide/))
- Prioritize buffs and large camps. Never invade blind. Vertical vs horizontal counter-jungling: vertical is "splitting the map into two halves along the mid lane", horizontal is "taking the enemy's same side jungle after clearing your own". — [nonagames 2026](https://nonagames.com/2026/04/13/how-to-jungle-path-and-counter-clear-enemy-meta-junglers-in-league-of-legends/); [Level Legendary](https://levellegendary.com/vertical-jungling-splitting-the-map/)
- Against a full-clear enemy: "드물지만 상대가 풀캠프를 시도할 경우 블루 카정을 통해서 막대한 이득을 볼 수 있다". — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C)) (snippet)
- 3캠 risk: a failed gank or invade after 3 camps widens the growth gap. — [나무위키](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C))
- Early spike for the first back is about 500–1,000 gold (pet upgrade, component, control ward). — cited in `jungler_turn_sync.md` (Buyboosting / Boosting Market)
- 26.1 role-quest rewards (+10 gold/XP per camp after completion) raise the value of steady farming mid-late. — [Riot 26.1 notes](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/)
- Meta context: "damage junglers on the rise after patch 26.x". — [zethacraft](https://zethacraft.com/en/blog/damage-junglers-on-the-rise-after-patch-26x-whos-winning-and-why-96) (title only, low-reliability blog)

### Inferences
- Power curves (general knowledge, **unsourced**): early-game junglers (e.g. Lee Sin, Elise, Xin Zhao, Jarvan IV, Rek'Sai) gain value from 3-camp ganks, invades and early Scuttle/Dragon fights. Their value falls off if they farm passively. Scaling junglers (e.g. Karthus, Master Yi, Bel'Veth, Shyvana, Kayn, Viego) want full clears, safe Scuttles and cross-map trades, and should avoid coin-flip fights before their item or level spikes. The rule of thumb is to match pathing to the curve: early types invest tempo into plays, scaling types invest tempo into farm and treats. Verify with a 2026 tier source before publishing champion examples.
- "Farm vs fight" rule (synthesis): intervene (개입) when the expected gain is bigger than the camps lost and the play is reachable before the window closes. Otherwise farm toward the next objective so you arrive with items and full Smite. The quest's mid-game gold makes the farm side somewhat more valuable in 2026.
- Items (general knowledge, **unsourced** for 2026): you start with a pet item, and your first back is usually a component toward the core item plus a control ward. The core build differs by class (AD bruiser / assassin / AP / tank). No 2026 jungle-item source was retrieved.

### Gaps
- No primary data on archetype win rate by game length for 2026 (e.g. from lolalytics). No 2026 jungle-item path source. No coach quotes on farm vs fight.

---

## Q6. Dragon / Void Grub Smite fights (오브젝트 강타 싸움)

### Takeaway
In 2026, epic monsters have more resistance, and Smite reaches 1400 at Primal. Steals are harder, and Smite tier matters. Keep one charge for the objective. Start bot-side objectives when the enemy jungler shows top, and the reverse. On Grubs, Smite can't hit voidmites and grubs heal each other. Stealing the last grub is a low-risk way to take value away.

### Cited Findings
- Epic monsters have higher resistances in 2026, and Smite is 600/1000/1400. — [gamerstogether.cz](https://gamerstogether.cz/en/lol-jungle-objectives-guide/)
- Grubs: 8:00, once only (group of three), "they leave permanently at 14:45. They don't respawn." Smite can't target voidmites. Each grub spawns four voidmites at fight start and every twelve seconds after ("Three grubs is twelve of them at a time"). "Stealing the third grub takes something real off the enemy without going on your record the way a stolen dragon does." — [gamerstogether.cz](https://gamerstogether.cz/en/lol-jungle-objectives-guide/); [nerfplz Voidgrubs & Herald guide](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html) (note: the URL is dated 2026/11, after today's date. Treat it with caution and re-check.)
- Older two-wave grub guides are outdated. — [bo3.gg Void Grubs guide](https://bo3.gg/lol/articles/league-of-legends-void-grubs-guide)
- "If the enemy jungler shows top, that's your cue to start a bottom-side objective, and vice versa." "If your bot lane has priority or the enemy jungler is top, you can sneak an early dragon. The same applies to Void Grubs on the top side." — [gamerstogether.cz](https://gamerstogether.cz/en/lol-jungle-objectives-guide/)

### Inferences
- Smite-fight how-to (synthesis, general knowledge): track the objective HP against **your current Smite tier (1000/1400) plus your next-hit burst**, not just the Smite number. Watch the enemy jungler, not the HP bar, once the objective is under about 2× Smite. Don't Smite early to "secure" when they're out of range. Keep your jungler out of CC range or ask for peel. Vs. a Primal-Smite enemy when you're still on Unleashed, avoid pure 50/50s and force fights before the pit or zone instead.

### Gaps
- No 2026 source quantifying dragon base HP or resistance values. No coach guide on smite-fight positioning was retrieved.

---

## Q7. Korean jungle theory vocabulary (근거 / 템포 / 투자 / 정글 효율 / 개입)

### Takeaway
Korean community sources describe jungle decisions with **주도권** (lane priority, the top input), **동선** (route), **정버프/역버프** (start side), **3캠/풀캠**, **카정**, **역갱**, **백업**, and **이득보기**. Several of the requested terms (**근거**, **투자**, **정글 효율**) had no defining source in the search results. They appear to be coaching jargon, not documented community terms.

### Cited Findings
- Priority order "아군 주도권 > 상대 정글 동선 > 아군 CC 및 적 회피 수단". — [Inven 정글러 동선 정리](https://www.inven.co.kr/board/lol/2766/44624) / [ygosu 상대 정글 동선 예측](https://m.ygosu.com/board/lo_legend/130943/?searcht=&search=&m3=real_article&frombest=Y&page=1)
- "이득보기 > 아군 정글몹 사냥 > 귀환". — [DC 정글학개론](https://gall.dcinside.com/board/view/?id=leagueoflegends3&no=7330222)
- 정버프/역버프, 3캠/풀캠, 블루 카정, 역갱, 백업 definitions: see Q2–Q5 citations ([나무위키](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C)), [Inven](https://www.inven.co.kr/board/lol/2766/34332), [arca.live 정글의 기초](https://arca.live/b/leagueoflegends/42075081), [slideshare 정글러 동선의 이해](https://www.slideshare.net/slideshow/understanding-of-jungler/238466556))
- 턴/템포 vocabulary is already covered in `korean_turn_concept.md`.

### Inferences
- A usable bilingual glossary for the library (term mapping only, not a definition source): 풀캠 = full clear; 3캠 = 3-camp; 정버프/역버프 = bot-side or top-side buff start (Korean convention); 동선 = pathing/route; 카정 = invade/counter-jungle; 역갱 = counter-gank; 백업 = cover; 주도권 = lane priority; 트래킹 = tracking; 강타 = Smite; 간식 = treats; 정글 펫/동반자 = jungle companion; 바위게 = Scuttle Crab; 유충 = Void Grubs; 이득보기 = making a play to gain value; 개입 = intervening in a lane fight.

### Gaps
- "근거 / 투자 / 정글 효율" as named frameworks: no source found. They may come from specific YouTube coaches (e.g. Korean 정글 강의 channels) that were not indexed. Don't present them as standard community terms without a source.
- 나무위키 and Inven could not be fetched in full, so all Korean quotes are snippets. Most Inven/DC posts are 2019–2020, so the vocabulary is valid but the numbers are outdated.
