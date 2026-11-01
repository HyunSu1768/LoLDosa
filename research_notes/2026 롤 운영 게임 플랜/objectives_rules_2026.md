# 2026 Summoner's Rift Objective & Map Rules (patches 26.1 – 26.21), for a jungler game-plan engine

> **Method note (read first).** Today is 2026-11-01 and live is about patch 26.21. WebFetch was blocked for every relevant domain in this session: leagueoflegends.com, wiki.leagueoflegends.com, lol.fandom.com, mobalytics.gg and nerfplz.com all returned ENOTFOUND for "outside allowed network domains". **Every finding below therefore comes from WebSearch result summaries and snippets, not full-page reads.** Quoted text is the search tool's extraction from the cited page, and I could not check it against the page. This file also merges and cross-references two earlier notes from the same project that were built the same way: `research_notes/롤 핵심 개념 학습 자료/objectives_vision.md` and `jungle_fundamentals.md`. Before shipping numbers in the app, verify them on the [Riot 26.1 notes](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/), the [LoL Wiki V26.01](https://wiki.leagueoflegends.com/en-us/V26.01) and the [LoL Wiki Role Quests](https://wiki.leagueoflegends.com/en-us/Role_Quests) page once those domains are allowed.
>
> **Swiftplay trap:** the 26.1 notes have a Swiftplay section that says Void Grubs and Herald "have been removed", that Dragon Soul comes from two drakes, and that Elder spawns at 15:00. Search snippets keep mixing these lines into standard Summoner's Rift (SR) summaries. On standard SR, grubs, Herald and the four-drake soul all still exist. See the conflict notes below.

## 1. Season overview: what 26.1 changed (Jan 7–8, 2026)

### Takeaway
26.1 ("For Demacia") simplified the objective set:
- **Removed:** Atakhan (아타칸), Blood Roses (피의 장미) and Feats of Strength (힘의 위업).
- **Baron (바론):** back to a 20:00 spawn.
- **Restored:** First Blood (선취점) gold of 100 g and first-turret (첫 포탑) gold of 300 g.
- **Turret plates (포탑 방패):** now permanent, and added to inner and inhibitor turrets.
- **New systems:**
  - Crystalline Overgrowth (true-damage crystals on turrets)
  - Faelights (페어라이트, ward-empowering spots)
  - Role Quests (역할군/포지션 퀘스트)
  - Earlier jungle camps (0:55) and minions (0:30)

### Cited Findings
- Atakhan and Feats of Strength were removed, and Baron returns to spawning at 20 minutes. — [Sheep Esports 26.1](https://www.sheepesports.com/en/articles/patch-26-1-new-role-quests-atakhan-and-feats-of-strength-removed-new-items-added/en); [esports.gg 26.1](https://esports.gg/guides/league-of-legends/lol-patch-notes-26-1/); [Sportskeeda 26.1 "Atakhan removed, Faelights added"](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes)
- Blood Roses were removed along with Atakhan. — [exitlag 2026 season](https://www.exitlag.com/news/league-of-legends-2026-season/); [games.gg Season 2026](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/)
- "First blood and first turret gold rewards return at 100 and 300 gold, respectively." — [esports.net 2026 season changes](https://www.esports.net/wiki/guides/lol-season-changes-2026/); [altchar S1 2026](https://www.altchar.com/game-news/league-of-legends-2026-s1-gameplay-changes-atakhan-removed-new-turret-plates-faster-minions-and-vision-upgrades-aXwcS6Y1psgZ)
- Riot's design intent: League had been "largely about teamfighting over neutral objectives". The 2026 changes should make split pushing "relatively more attractive". — [Riot /dev 2026 Season One Gameplay Preview](https://www.leagueoflegends.com/en-gb/news/dev/dev-2026-season-one-gameplay-preview/); [Sheep Esports S1 2026 preview](https://www.sheepesports.com/en/all/articles/league-of-legends-2026-s1-gameplay-changes-atakhan-removed-new-plates-on-t2-and-t3-nashor-back)
- 26.1 Korean patch summaries give these spawn times:
  - "늑대, 블루, 레드, 칼날부리 생성 시간: 55초"
  - "돌거북, 두꺼비 생성 시간: 1분 7초"
  - "바위게 생성 시간: 2분 55초"
  - Minions moved from 1:05 to 0:30, and Baron from 25:00 to 20:00.
  - — [인벤 26.1 패치 노트](https://www.inven.co.kr/board/lol/3329/657); [루리웹 26.1 패치 노트](https://bbs.ruliweb.com/news/board/300007/read/2339910) (snippet, from the earlier project notes)
- 26.1 also removed the team-wide Red/Blue buff sharing that applied after 25:00. Baron's spawn no longer corrupts Red/Blue buffs. — [루리웹 26.1](https://bbs.ruliweb.com/news/board/300007/read/2339910); [Sportskeeda 26.1](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes)

### Inferences
- Any guide or app data that mentions Atakhan, Blood Roses, Feats or 14:00 plate fall-off is 2025 or older. The app should drop those rules for 2026.

### Gaps
- I could not read the full official 26.1 notes, which are reportedly about 83 pages ([mein-mmo](https://mein-mmo.de/en/neue-season-lol-83-seiten-patch-notes,1545050/)).

---

## 2. Void Grubs (공허 유충), Rift Herald (협곡의 전령), Atakhan (아타칸), Baron Nashor (내셔 남작/바론), Elder (장로 드래곤)

### Takeaway
The 2026 top-side timeline:
- **Grubs:** one set of 3 at **8:00**. They do not respawn and despawn around 14:45.
- **Herald:** **15:00**, despawns 19:45.
- **Baron:** **20:00**, respawn **6:00**. Its gold was cut heavily in 26.1.
- **Atakhan:** does not exist in 2026.
- **Elder:** spawns after a team takes soul and respawns every **6:00**. Its buff lasts **150 s** and executes enemies below 20% HP.

### Cited Findings

**Void Grubs (공허 유충)**
- Spawn: 8:00, three grubs, no respawn since 25.09. If untaken they "leave for good at 14:45 (or 14:55 if they're mid-fight)". — [nerfplz Voidgrubs/Herald guide](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html) (the URL is dated after today, so use caution); [gamerstogether.cz 2026](https://gamerstogether.cz/en/lol-jungle-objectives-guide/)
- Rewards:
  - Each grub gives "30 gold to the killer and 65 XP each".
  - Each grub adds a team stack of Touch of the Void.
  - Three grubs grant **Hunger of the Void (공허의 굶주림)**: allied voidmites that attack turrets.
  - A Korean guide says 26.1 cut total grub gold from 210 to 90 and XP from 80 to 65.
  - — [search summary of nerfplz / boostingmarket](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html); [vortexgaming 2026 시즌1 정글 분석](https://vortexgaming.io/postdetail/635801)
- 26.1: "Grubs now deal 50% more damage to non-champions, matching Dragon and Baron". — [Riot 26.1 (en-gb), search summary](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/)
- 26.11 (May 27, 2026): voidmites summoned by Hunger of the Void went from 60% to **100% of a melee minion's health**. — [riftpatchnotes Void Grubs](https://www.riftpatchnotes.com/lol/system/void-grubs) (search summary)
- Fight mechanic: when a fight starts, and every 12 s while it continues, each grub spawns 4 voidmites. Smite cannot target voidmites. — [nerfplz](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html)
- **Conflict:** Korean reprints and Riot snippets say "공허 유충이 삭제되었습니다" (Void Grubs were removed). That is the **Swiftplay** section. 26.11 balanced grubs on SR, so grubs exist on standard SR. — [ruliweb 26.1](https://bbs.ruliweb.com/news/board/300007/read/2339910) vs [riftpatchnotes 26.11](https://www.riftpatchnotes.com/lol/system/void-grubs)

**Rift Herald (협곡의 전령)**
- Spawns **15:00** in the top pit. It despawns at 19:45, before Baron spawns at 20:00. — [nerfplz S16 objectives](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html); [esports.net](https://www.esports.net/wiki/guides/lol-season-changes-2026/)
- 26.1 changes:
  - "Experience reduced to 240 at all levels from 309/318/330 … Experience radius increased to 2000 from 600"
  - Gold goes to the killer only, "100 gold"
  - Eye cooldown 8 → 6 s
  - 50% more damage to non-champions
  - — [Riot 26.1](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/); [thegamehaus 26.1](https://thegamehaus.com/league-of-legends/full-lol-patch-26-1-patch-notes-for-demacia/2026/01/07/) (search summaries)
- riftpatchnotes says Herald was "most recently adjusted in Patch 26.12 (June 9, 2026)". A later search found no details for 26.12. — [riftpatchnotes Rift Herald](https://www.riftpatchnotes.com/lol/system/rift-herald)
- Eye of the Herald (전령의 눈) mechanics, last confirmed at 14.22 (2024), with no 2026 update found:
  - The Eye expires 4 minutes after pickup.
  - Herald charges a turret for "150 damage plus 25% of her current health".
  - She gets a second charge only after assisting a turret kill.
  - — [LoL Wiki Eye of the Herald](https://wiki.leagueoflegends.com/Eye_of_the_Herald)
- **Conflict:** one snippet of the official notes says Herald "has been removed". As with grubs, this is the Swiftplay section. — [Riot 26.1](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/)

**Atakhan (아타칸)**
- Removed in 26.1. It "has been removed from the game and will no longer spawn". — [Riot 26.1 (en-gb)](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [Sheep Esports](https://www.sheepesports.com/en/articles/patch-26-1-new-role-quests-atakhan-and-feats-of-strength-removed-new-items-added/en)
- 2025 history: Riot added Atakhan to fill the 20-minute gap, because "teams typically aren't taking Barons at 20 minutes". — [Riot /dev 2025 Season One preview](https://www.leagueoflegends.com/en-us/news/dev/dev-2025-season-one-gameplay-preview/)

**Baron Nashor (내셔 남작)**
- 26.1: spawn **25:00 → 20:00**, respawn **6:00**. — [Sportskeeda 26.1](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes); [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html)
- 26.1 gold:
  - Total gold went from **1525 to 850**.
  - The killer bonus rose from 25 to 100.
  - The global per-player gold fell from 300 to 150.
  - Baron XP was also reduced (one summary says total experience went from 3,800 to 3,250), and Baron now gets "comeback experience like with dragons".
  - — [esports-news.co.uk 26.1](https://esports-news.co.uk/2026/01/07/league-of-legends-patch-26-1-kicks-off-the-new-year-with-huge-changes/); [Riot 26.1](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/) (search summaries). In the earlier project notes, one summary attributed the 1525 → 850 cut to Herald. This session's search attributed it to Baron with the 25 → 100 and 300 → 150 split. Baron is the more coherent reading: 150 × 5 + 100 = 850.
- 26.1 also says Baron's "experience reward and buff were kept". — [Riot 26.1 (en-gb), search summary](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/)
- Buff, **Hand of Baron (내셔 남작의 손길)**:
  - Lasts 180 s, or until the holder dies.
  - Gives flat AD/AP that is set when the buff is taken.
  - Gives an empowered recall and empowered nearby minions.
  - — [LoL Wiki Hand of Baron](https://wiki.leagueoflegends.com/en-us/Hand_of_Baron); [nerfplz Baron guide](https://www.nerfplz.com/2026/10/baron-nashor-guide-spawn-timers-three.html)
- Baron forms: one of three forms (Territorial, Hunting, All-Seeing) is picked at random each game. Each changes the pit's terrain. The forms date from 25.S1 and still exist in 2026. — [nerfplz Baron guide](https://www.nerfplz.com/2026/10/baron-nashor-guide-spawn-timers-three.html); [games.gg beginner guide](https://games.gg/league-of-legends/guides/league-of-legends-beginners-guide/)
- 26.18: a bug fix stopped Baron's Void Corruption max stacks from exceeding the intended value. There were no other objective changes found in 26.18 to 26.21. — [Riot 26.18 notes](https://www.leagueoflegends.com/en-us/news/game-updates/league-of-legends-patch-26-18-notes/) (search summary)

**Elder Dragon (장로 드래곤)**
- Replaces elemental drakes once a team has Dragon Soul. It spawns 6:00 after soul is taken and respawns every 6:00. — [senseos dragons guide](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/); [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html)
- 26.1: "around 20% more effective HP but should otherwise feel similar". — [Riot 26.1 (en-sg)](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-26-1-notes/)
- Buff: **Aspect of the Dragon (장로 드래곤의 위상)** lasts **150 s** and goes to living teammates. Damaging a champion below **20% max HP** triggers an execute (Elder Immolation) after 0.5 s. — [LoL Wiki Elder Dragon](https://wiki.leagueoflegends.com/en-us/Elder_Dragon)

### Inferences
- The cleanest top-side plan for a jungler in 2026:
  - 8:00 grubs
  - Herald at 15:00, if plates and towers are still up
  - 20:00 Baron
- Baron's gold cut (850 total) makes Baron mainly a siege tool. Its value now comes from the buff converting into turret plates and turrets (see §5), not from the kill gold.

### Gaps
- What 26.12 changed on Herald.
- 2026 Hand of Baron AD/AP values.
- Whether the Herald charge mechanics changed after 14.22.
- Grub HP and Touch of the Void values for 2026.

---

## 3. Dragons (드래곤/용) and Elemental Souls (용의 영혼)

### Takeaway
- **Timing:** first drake at **5:00**, then a respawn **5:00** after each kill.
- **Map change:** after the 2nd drake, the map turns into that soul's rift (협곡 변화).
- **Soul:** the first team to **4** drakes on standard SR wins soul.
- **26.1 changes:**
  - Drakes have up to 35% more effective HP.
  - Dragon Vengeance (용의 복수) damage reduction went to 15/30/45%.

### Cited Findings
- First spawn 5:00, respawn 5:00. — [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoner's-rift-objective.html); [gamerstogether.cz](https://gamerstogether.cz/en/lol-jungle-objectives-guide/)
- 26.1: "Elemental Drakes will have up to 35% more effective HP, increased further for teams who approach Dragon Soul". Dragon Vengeance damage reduction went from 7/14/21% to **15/30/45%**, and its bonus damage to champions was removed. One guide says drake kill gold is 75. — [Riot 26.1 (en-sg)](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-26-1-notes/); [agatasmurf 2026](https://agatasmurf.com/league-of-legends-dragons/)
- Mountain drake: "15% more health instead of extra armor and magic resist" (since 26.1). — [senseos](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/)
- Dragon Slayer stacks at 1 to 4 stacks. The senseos guide says it checked these against 26.21 on Oct 25, 2026.
  - **Infernal (화염):** +3% AD/AP per stack, so 3/6/9/12%.
  - **Mountain (대지):** armor/MR from 5% to 20%.
  - **Ocean (바다):** regenerates 2% to 8% of missing HP every 5 s.
  - **Cloud (바람):** slow resist and out-of-combat movement speed from 5% to 20%.
  - **Hextech (마법공학):** 5/10/15/20 ability haste and 5/10/15/20% attack speed.
  - **Chemtech (화학공학):** tenacity and heal/shield power from 6% to 24%.
  - — [senseos](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/); [LoL Wiki Dragon Slayer](https://wiki.leagueoflegends.com/en-us/Dragon_Slayer)
- Soul values:
  - Cloud Soul: 15% movement speed (down from 20% in 25.S1.3).
  - Chemtech Soul: 13% damage and damage reduction below 50% HP.
  - Ocean Soul: heals "150 base" and restores "100 base mana" over 4 s.
  - Mountain Soul: a shield after 5 s without taking damage.
  - — [senseos](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/); [agatasmurf](https://agatasmurf.com/league-of-legends-dragons/)
- "The first team to four takes Dragon Soul, and Elder Dragon follows 6 minutes later". The soul element is the element of the rift transformation, which happens after the 2nd drake. — [senseos](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/)
- More Faelights appear when the Elemental Rift transforms. — [Riot /dev 2026 preview](https://www.leagueoflegends.com/en-gb/news/dev/dev-2026-season-one-gameplay-preview/) (search summary)
- 26.19: a Malphite interaction fix means Malphite no longer halves Dragon's attack speed. This is not a change to Dragon itself. — [Riot 26.19 notes](https://www.leagueoflegends.com/en-gb/news/game-updates/league-of-legends-patch-26-19-notes/) (search summary)
- **Conflict:** "Dragon Soul … if a team manages to kill both Elemental Drakes" and "Elder … spawns at 15:00" are **Swiftplay** rules, not standard SR. — [Riot 26.1](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-26-1-notes/)

### Inferences
- With vengeance at 45% against the team that is three drakes up, the team behind can rarely contest soul point by raw DPS. Smite timing and zoning decide those fights.

### Gaps
- Current (2026) rift terrain per element. The only detailed source is an old Dignitas guide: Mountain adds walls, Ocean adds brush, Infernal removes brush, and so on. — [Dignitas Elemental Terrain](https://dignitas.gg/articles/blogs/Unknown/14573/weathering-the-rift-elemental-terrain-guide) (old, not 2026)
- Exact 2026 drake gold and XP.

---

## 4. Feats of Strength (힘의 위업): removed in 2026, and what replaced the boots reward

### Takeaway
Feats of Strength **does not exist in 2026** (removed in 26.1). The Tier-3 boots upgrade (3단계 장화) that Feats used to give the whole team is now the **mid-lane Role Quest reward** only.

### Cited Findings
- 2025 rules (history only):
  - A best-of-three race between First Blood, First Tower, and First to three epic monsters.
  - Any 3 grubs counted as one epic monster, and all 6 counted as two.
  - Drakes and Herald counted as one each.
  - Winning upgraded the team's Tier 2 boots and unlocked Tier 3 boots.
  - Riot reworked the First Blood requirement two days after launch, and again in 25.S1.2.
  - Feats replaced the bonus gold from First Blood and First Tower.
  - — [esports.gg Feats explained](https://esports.gg/news/league-of-legends/league-of-legends-new-feats-of-strength-mechanic-explained); [Riot /dev 2025 preview](https://www.leagueoflegends.com/en-us/news/dev/dev-2025-season-one-gameplay-preview/); [dotesports rework](https://dotesports.com/league-of-legends/news/we-messed-up-riot-is-already-reworking-lols-first-blood-feats-of-strength); [Sportskeeda 25.S1.2](https://www.sportskeeda.com/esports/league-legends-patch-25-s1-2-notes-feats-strength-changes-atakhan-nerfs)
- 2026: Feats was removed, and First Blood +100 g and First Turret +300 g were restored. — [esports.net](https://www.esports.net/wiki/guides/lol-season-changes-2026/); [Sheep Esports](https://www.sheepesports.com/en/articles/patch-26-1-new-role-quests-atakhan-and-feats-of-strength-removed-new-items-added/en)
- "The old team-wide boot upgrade now belongs to the mid laner alone." Riot's notes say "Tier 2 boots upgrade to their corresponding Tier 3 boots". — [search summary of games.gg / Riot 26.1](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/)

### Inferences
- The app should not plan "first 3 epic monsters" races. Early objectives are now worth only their own rewards, plus objective bounties.

### Gaps
- None material.

---

## 5. Role Quests (역할군 퀘스트 / 포지션 퀘스트): 2026

### Takeaway
Role Quests were added in 26.1 for all five roles:
- Each player gets the quest for their queued role in champion select. They are not active in Swiftplay.
- Laners earn points from minions, plates, turrets, takedowns and epic monsters. Actions in their assigned lane count double.
- The jungle quest is tied to the jungle pet.
- Rewards were reworked in **26.9** (Season 2) and tuned in **26.16** and **26.19**.

### Cited Findings
- **How it works:**
  - Quests are auto-assigned by queued role, and not active in Swiftplay.
  - Laners earn points from champion kills, epic monster kills, minion kills, plates and turrets.
  - "Minion kills, turret plates, and turret takedowns in your assigned lane award double points."
  - — [exitlag 2026](https://www.exitlag.com/news/league-of-legends-2026-season/); [인벤 26.1 패치노트](https://www.inven.co.kr/board/lol/3329/657); [Riot 26.1](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/)
- **Jungle (정글) quest:**
  - Completes at **35 points**, down from 40 in PBE or pre-release. You earn "one point gained for each treat fed to your jungle pet".
  - Rewards:
    - Upgraded Smite
    - "10 bonus gold and 10 bonus experience" per large monster or camp
    - "4% bonus movement speed in the jungle or river, increased to 8% while out of combat"
  - — [Riot 26.1 (en-gb)](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [LoL Wiki V26.01](https://wiki.leagueoflegends.com/en-us/V26.01); [esports.net](https://www.esports.net/wiki/guides/lol-season-changes-2026/) (snippets)
  - I found no source describing a later jungle-quest change in 26.9 or 26.16. — [guides-factory role quests](https://guides-factory.com/guides/lol-role-quests-guide)
- **Top (탑) quest:**
  - Completes at **1,200 points**.
  - Rewards:
    - 600 XP
    - Level cap raised to **20**
    - A free **Unleashed Teleport** if you didn't take Teleport. If you did take Teleport, you get a shield after teleporting instead.
    - A later guide also lists 11% bonus XP and 80 XP per takedown.
  - 26.19: the free Teleport cooldown went from **420 to 390 s**.
  - — [esports.gg role quests](https://esports.gg/news/league-of-legends/league-of-legends-2026-role-quests/); [senseos role quests](https://senseos.gg/guides/league-of-legends/how-role-quests-work/); [guides-factory](https://guides-factory.com/guides/lol-role-quests-guide)
  - **Conflict:** Sheep Esports wrote "level 19". Most others, and patched.gg, say level 20. — [Sheep Esports](https://www.sheepesports.com/en/articles/patch-26-1-new-role-quests-atakhan-and-feats-of-strength-removed-new-items-added/en) vs [patched.gg 26.1](https://patched.gg/games/league-of-legends/patch-261-notes)
- **Mid (미드) quest:**
  - Completes at **1,350 points**.
  - Original 26.1 rewards: Tier 2 boots upgrade to Tier 3, plus an empowered Recall every 5 minutes (channel 8 → 4 s).
  - **26.9 removed the empowered Recall** and replaced it with +6% AD and +6% AP. A later patch raised that to **8%/8%**.
  - — [Riot 26.1](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [Riot 26.9 notes](https://www.leagueoflegends.com/en-us/news/game-updates/league-of-legends-patch-26-9-notes/); [senseos](https://senseos.gg/guides/league-of-legends/how-role-quests-work/); [LoL Wiki Role Quests](https://wiki.leagueoflegends.com/en-us/Role_Quests)
- **Bot / ADC (원딜) quest:**
  - Completes at **1,350 points**.
  - Rewards:
    - +300 g on completion
    - +2 g per minion for the rest of the game
    - +50 g per takedown, cut to **40 g** in a later patch (26.9 per guides)
    - Boots move into the Role Quest slot, which opens a **7th item slot**
  - — [인벤 26.1](https://www.inven.co.kr/board/lol/3329/657); [esports.gg](https://esports.gg/news/league-of-legends/league-of-legends-2026-role-quests/); [guides-factory](https://guides-factory.com/guides/lol-role-quests-guide)
- **Support (서포터) quest:**
  - Completes at **800 points**. Points come from gold your support item earns.
  - Rewards: Control Wards cost **40 g**, down from 75, and up to **2 Control Wards** can be stored in the Role Quest slot.
  - 26.16: supports who roam early get **33% less minion gold and XP outside bot lane until level 5**.
  - — [Riot 26.1](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [LoL Wiki Role Quests](https://wiki.leagueoflegends.com/en-us/Role_Quests); [senseos](https://senseos.gg/guides/league-of-legends/how-role-quests-work/)
- **26.9 system rework ("Season 2"):**
  - The quest lane area was widened from "outer turret" to anywhere in your lane outside your base.
  - The off-role penalty on last hits and turret/plate gold changed from -50% to -75%, decreasing to 0% as the quest progresses.
  - Passive point gain in the quest lane went from 1.6 to 1.5 points per second.
  - Recalling now pauses passive point gain for 12 s.
  - A new "roaming bank" stores roaming time without losing progress.
  - — [u.gg 26.9](https://u.gg/lol/news/patch-26-9-official-notes-league-of-legends); [patched.gg 26.9](https://patched.gg/games/league-of-legends/league-of-legends-patch-269-notes)

### Inferences
- **Gank planning:**
  - Gank help is worth more for a mid laner close to finishing the quest (Tier-3 boots plus AD/AP) and for a top laner close to finishing (TP and level 20).
  - Ganks that let the enemy farm their quest lane are costly.
  - The roaming bank and the 12-s recall pause slightly soften the cost of a laner roaming with the jungler.
- **Jungle quest pacing:** the quest finishes at 35 treats, so a fast full-clear tempo that kills every large monster speeds up the Smite upgrade and the +10 g/+10 XP per camp. That makes Smite contests at the first drake (5:00) and grubs (8:00) easier.

### Gaps
- **Typical completion times.** I did not find a sourced average minute for each quest.
- **Timing of later reward changes.** The patch number for the mid quest moving from 6% to 8% is unknown. The exact 26.16 support changes beyond roaming are also unknown.
- **Points per action.** The exact table is unconfirmed.

---

## 6. Turrets (포탑), plates (포탑 방패), Crystalline Overgrowth, inhibitors (억제기) and Nexus turrets (넥서스 포탑)

### Takeaway
Plates are **permanent** in 2026. Outer turret plates start at 120 g and lose value from 11:00, down to 80 g. Inner and inhibitor turrets each have 5 plates totaling 600 g. Crystalline Overgrowth rewards attacking a turret after leaving it alone for 90 s. Nexus turrets have no plates.

### Cited Findings
- **Outer turret plates:**
  - Base outer plate value went from 125 to **120 g**.
  - "Plate value reduces by 10g per minute at minute 11, capped at -40", so the minimum is 80 g from about 14:00.
  - Plates are permanent and no longer fall off at 14:00.
  - Outer turrets also lose gold, armor and MR every minute between 11:00 and 15:00.
  - — [Riot 26.1 / LoL Wiki V26.01 search summary](https://wiki.leagueoflegends.com/en-us/V26.01); [esports.net](https://www.esports.net/wiki/guides/lol-season-changes-2026/); [altchar](https://www.altchar.com/game-news/league-of-legends-2026-s1-gameplay-changes-atakhan-removed-new-turret-plates-faster-minions-and-vision-upgrades-aXwcS6Y1psgZ)
- **Inner turrets (2차 포탑):** local gold went from 425/675 to **600 spread across 5 plates**, which are claimed at 10/25/45/70/100% missing HP. — [LoL Wiki V26.01 / Leaguepedia Patch 26.01 (search summary)](https://lol.fandom.com/wiki/Patch_26.01)
- **Inhibitor turrets (3차/억제기 포탑):**
  - Local gold went from 375 to **600 spread across 5 plates**.
  - Health 3500 → **4750**.
  - Regen thresholds changed from 33/66% to **30/75%**.
  - Resists changed.
  - — [Leaguepedia Patch 26.01](https://lol.fandom.com/wiki/Patch_26.01) (search summary)
- **26.3:** plate temporary resists went from "20–100 per plate → 30–50 per plate". — [u.gg 26.3](https://u.gg/lol/news/patch-26-3-notes-league-of-legends); [dtgre 26.3](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html)
- **Crystalline Overgrowth (수정 과성장, Korean name unverified):**
  - It appears after a 90 s startup or cooldown. At that point the next enemy champion attack deals true damage.
  - It does not trigger while backdoor protection is active.
  - It is suppressed if an enemy unit is near the turret at the 90 s mark.
  - Sheep Esports describes it as crystals that "build on turrets, detonate after 3 hits giving the player gold based on the crystals accumulated".
  - — [Leaguepedia/LoL Wiki 26.01 search summary](https://wiki.leagueoflegends.com/en-us/V26.01); [Sheep Esports on X](https://x.com/Sheep_Esports/status/1995526554986610893?lang=en)
- **Nexus turrets:**
  - Health 3000 → **3500**.
  - Resists 70 → **60**.
  - Regen thresholds **40/70%**.
  - They now respawn at **40% HP**, down from 100%.
  - They are the only turrets without plates.
  - — [Riot 26.1 / Leaguepedia search summary](https://lol.fandom.com/wiki/Patch_26.01)
- **First turret:** +300 g (restored in 26.1). — [esports.net](https://www.esports.net/wiki/guides/lol-season-changes-2026/)
- **Inhibitor respawn:** the wiki says a fixed **5:00**. These pages show no 2026 change, but I could not confirm one either way. — [LoL Wiki Inhibitor](https://wiki.leagueoflegends.com/en-us/Inhibitor); [Leaguepedia Inhibitor](https://lol.fandom.com/wiki/Inhibitor_(Structure)) (**not 2026-confirmed**)
- **Riftpatchnotes caution:** that site also lists older per-plate figures of 160 g and 175 g from earlier patches. Do not mix these with the 26.1 values. — [riftpatchnotes Turrets](https://www.riftpatchnotes.com/lol/system/turrets)

### Inferences
- Plate gold no longer has a 14:00 deadline. Top-side objectives therefore convert to gold through turrets for the whole game: grub voidmites (buffed in 26.11), the Herald charge, and the Baron siege.
- Outer plates are worth the most before 11:00 (120 g each), so early drake or grub trades should be weighed against bot or top plates taken during that window.

### Gaps
- Total outer turret gold after 26.1, i.e. plate count and destruction gold.
- Exact Crystalline Overgrowth gold values.
- Inhibitor respawn time in 2026.

---

## 7. Jungle camps, Scuttle (바위게), Smite (강타), pets (정글 펫), Faelights (페어라이트), vision

### Takeaway
- **Camp spawns (26.1):**
  - Buffs, Wolves and Raptors: **0:55**
  - Gromp and Krugs: **1:07**
  - Scuttle: **2:55**
- **Respawns:** apparently unchanged: small camps 2:15, buffs 5:00, Scuttle 2:30.
- **Smite:** 600/1000/1400.
- **Pet:** first evolution at 15 treats.
- **Faelights:** 12 spots where a ward becomes a "superward".

### Cited Findings
- Spawn times: 0:55 (Blue, Red, Wolves, Raptors), 1:07 (Gromp, Krugs), 2:55 (Scuttle, previously 3:30). Minions spawn at 0:30. — [인벤 26.1](https://www.inven.co.kr/board/lol/3329/657); [Sheep Esports 26.1 "jungle camps appear at 55 seconds"](https://www.sheepesports.com/en/articles/patch-26-1-new-role-quests-atakhan-and-feats-of-strength-removed-new-items-added/en); [LoL Wiki Rift Scuttler camp](https://wiki.leagueoflegends.com/en-us/Rift_Scuttler_camp)
- Respawns: small camps 2:15, buffs 5:00, Scuttle 2:30. These come from pre-26.1 pages, but I found no evidence of a change. — [leagueoflegendstools](https://leagueoflegendstools.com/tools/jungle-respawn-timers/)
- Smite: 600/900/1200 → **600/1000/1400** (26.1). Epic monsters have higher resistances in 2026. — [Riot 26.1](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/); [gamerstogether.cz](https://gamerstogether.cz/en/lol-jungle-objectives-guide/)
- Pet: first evolution needs **20 → 15 treats** (26.1), and pet base DPS went from 20–90 to 20–150. — [LoL Wiki Smite](https://wiki.leagueoflegends.com/en-us/Smite); [allthings.how 26.1](https://allthings.how/league-of-legends-patch-26-1-reshapes-the-map-jungle-and-vision-game/)
  - **Conflict:** sources disagree on the final evolution: 25, 35 or 40 treats.
- 26.4: omnivamp no longer applies to Smite or Ignite. 26.12: Smite got a pet damage addition of 20–160. — [sheepesports 26.4](https://www.sheepesports.com/articles/league-of-legends-patch-26-4-omnivamp-no-longer-applies-to-smite-and-ignite/en); [riftpatchnotes Smite](https://www.riftpatchnotes.com/lol/spell/smite)
- Jungle clear speed was "toned down early" so lanes can play before ganks. — [esports.net](https://www.esports.net/wiki/guides/lol-season-changes-2026/) (search summary)
- **Faelights (페어라이트; Korean spelling from the games.gg/ko guide title):**
  - These are predetermined spots. A ward placed there gains extra vision range.
  - Some exist from game start, and more appear when the Elemental Rift transforms.
  - The bonus vision duration is limited "to leave some space for junglers or roaming champions to sneak around".
  - LoL Theory says there are 12 spots, with a "45-second bonus reveal region". This is not cross-confirmed.
  - — [Riot /dev 2026 preview](https://www.leagueoflegends.com/en-gb/news/dev/dev-2026-season-one-gameplay-preview/); [games.gg 페어라이트 가이드](https://games.gg/ko/league-of-legends/guides/리그-오브-레전드-페어라이트-시야-시스템-가이드/); [LoL Theory warding 2026](https://blog.loltheory.gg/warding-guide-lol/)
- **Other vision changes:**
  - Oracle Lens duration 6 → 8 s.
  - Warding Totem cooldown changed to 170–90 s in 26.1, then to 210–90 s in 26.3.
  - Scryer's Bloom respawn timer adjusted, with extra Blooms added.
  - 26.3: the River Pixel Brush reveal region cuts off before the scuttle pad and the epic pit entrance.
  - — [games.gg 26.1](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/); [u.gg 26.3](https://u.gg/lol/news/patch-26-3-notes-league-of-legends)

### Inferences
- Under 0:55 spawns, a full clear finishes around 2:30–2:55, which lines up with Scuttle at 2:55. A 3-camp gank lands around 1:55–2:25. This is derived from the earlier notes and should be validated in a custom game.

### Gaps
- The 2026 jungle XP and gold table per camp.
- The final pet evolution count.
- What 26.16 changed in the jungle: riftpatchnotes says the jungle was "last adjusted in 26.16" without details.

---

## 8. Other macro systems: bounties, recall, homeguard, minions

### Takeaway
Objective bounties are a comeback system: 10% of the gold deficit, capped at 1000 g per objective. 26.3 slowed champion bounty growth. Homeguard always gets you at least to your inhibitor. Minions now spawn at 0:30.

### Cited Findings
- **Objective bounties:**
  - "accrual is now based on the enemy's gold lead exclusively". They scale "at a rate of 10% of the team gold deficit, capped at 1000 gold per objective".
  - Claiming one cancels all other objective bounties.
  - — [LoL Wiki Objective bounties](https://wiki.leagueoflegends.com/en-us/Objective_bounties) (undated)
- **26.3 champion bounties:** the devalue rate went from "1 per 2.5 gold given out" to "1 per 3.5". Farming increments went from 1/5 to 1/7. — [u.gg 26.3](https://u.gg/lol/news/patch-26-3-notes-league-of-legends); [dtgre 26.3](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html)
- **Homeguard:** "Homeguard will always take you at least to your Inhibitor". After 14:00, or once a lane turret falls, it tracks the furthest minion. — [search summary, Leaguepedia Patch 26.01 / nerfplz](https://lol.fandom.com/wiki/Patch_26.01) (the attribution to 26.1 is uncertain)
- **Minions:** first spawn moved from 1:05 to **0:30** (26.1). — [인벤 26.1](https://www.inven.co.kr/board/lol/3329/657); [altchar "faster minions"](https://www.altchar.com/game-news/league-of-legends-2026-s1-gameplay-changes-atakhan-removed-new-turret-plates-faster-minions-and-vision-upgrades-aXwcS6Y1psgZ)
- **Recall:**
  - The standard recall is 8 s. The mid quest's 4 s recall existed only from 26.1 to 26.8.
  - Since 26.9, recalling pauses role-quest passive gain for 12 s.
  - — [Riot 26.1](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [patched.gg 26.9](https://patched.gg/games/league-of-legends/league-of-legends-patch-269-notes)

### Inferences
- With Baron gold cut and Feats removed, objective bounties are among the few sources of large comeback gold on objectives. A team that is behind should plan around bounty-flagged drakes and towers.

### Gaps
- A 2026 objective-bounty activation table: the minimum gold lead, and which objectives can carry bounties.
- Homeguard speed values.
- Exact 26.1 minion wave changes beyond the spawn time.
- Whether 26.20 or 26.21 changed any system. The searches found only champion changes and bug fixes. — [seemeta 26.21](https://seemeta.com/en/lol/patch-notes); [V26.20 wiki header](https://wiki.leagueoflegends.com/en-us/V26.20)
