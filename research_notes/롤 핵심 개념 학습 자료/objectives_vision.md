# Objectives and Vision Concepts (Season 2026), for a Platinum jungler's learning library

> **Method note (read first):** WebFetch was blocked in this session. www.leagueoflegends.com, www.riftpatchnotes.com and esports.gg all returned "ENOTFOUND, outside allowed network domains". Earlier sessions also found wiki.leagueoflegends.com, mobalytics.gg and nerfplz.com blocked. **All findings below come from WebSearch result summaries and snippets, not full-page reads.** Text in quotation marks is the search tool's extracted text from the cited page. I could not check it against the page. Before publishing any number, verify it on the [Riot 26.1 patch notes](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/) and the LoL Wiki once those domains are allowed. Today is 2026-10-31, and the live patch is about 26.21 ([Inven 26.21 patch notes](https://www.inven.co.kr/board/lol/3329/680)). Some nerfplz URLs carry dates of 2026/11 or 2026/12, which is after today, so treat them cautiously.
>
> **Extends rather than duplicates** `research_notes/롤 턴 개념과 정글 운영/jungler_turn_sync.md` §6. That section already holds the 2026 timer table: Grubs 8:00, Dragon 5:00 with 5:00 respawn, Herald 15:00 until 19:45, Baron 20:00 with 6:00 respawn, Elder 6:00 respawn, Scuttle 3:30, camps 2:15 and buffs 5:00. It also covers the Atakhan, Blood Roses and Feats removal, and the 90/60/30 s setup guidance from Boosteria and mid.gg. This file adds buff values, rewards, patch history, vision mechanics and how-to content.

---

## Q1. Exact current mechanics, timers and buff values per objective (with patch noted)

### Takeaway
Season 2026 (patch 26.1, Jan 7–8 2026) simplified the objective set:
- **Atakhan, Blood Roses and Feats of Strength were removed.**
- **Baron spawns at 20:00 again** and gives less gold.
- **Drakes got tankier** (up to +35% effective HP), and Dragon Vengeance was raised to 15/30/45%.
- **Herald's rewards were cut** (240 XP).
- **Turret plates became permanent** and were added to inner and inhibitor turrets.
- **First turret gives 300 g again.**
- **Faelights** were added as a new vision mechanic.

Later patches made smaller changes:
- 26.3: champion bounties, plate resists and the Stealth Ward cooldown.
- 26.11: Hunger of the Void buff.
- 26.12: Herald and Smite adjustments.

Several exact numbers conflict between sources, and those are flagged inline.

### Cited Findings

**Patch 26.1 headline objective changes (all summaries of the Riot notes and their coverage)**
- Atakhan "has been removed from the game and will no longer spawn". Blood Roses and Feats of Strength were also removed. The rationale was that they made the game "extremely objective-focused". — [Riot Patch 26.1 Notes](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [Sportskeeda 26.1](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes); [games.gg Season 2026](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/)
- "first Turret destroyed once again grants +300g". First blood went back to 100 g. — [Riot 26.1 (Korean search set)](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/); [thegamehaus 26.1](https://thegamehaus.com/league-of-legends/full-lol-patch-26-1-patch-notes-for-demacia/2026/01/07/)
- Turret plates are now **permanent** (they no longer fall off at 14:00) and exist on **inner and inhibitor turrets** too. — [thegamehaus 26.1](https://thegamehaus.com/league-of-legends/full-lol-patch-26-1-patch-notes-for-demacia/2026/01/07/); [esports-news.co.uk](https://esports-news.co.uk/2026/01/07/league-of-legends-patch-26-1-kicks-off-the-new-year-with-huge-changes/) (search summary). *This supersedes the "plates fall at 14:00" assumption in the prior `timeline_metrics.md`.*

**Dragons (드래곤 / 용, Elemental Drakes 원소 드래곤)**
- First spawn 5:00, respawn 5:00 after each kill. The 2026 timers are in the prior notes §6. — [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoner's-rift-objective.html)
- Patch 26.1: "Elemental Drakes will have up to 35% more effective HP, increased further for teams who approach Dragon Soul". **Dragon Vengeance** (damage reduction against the team closer to soul) went from 7/14/21% to **15/30/45%**, and its bonus damage to champions was removed. One guide says drake kill gold rose to 75. — [Riot 26.1](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-26-1-notes/); [agatasmurf 2026](https://agatasmurf.com/league-of-legends-dragons/); [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html)
- Mountain drakes now get "15% more health instead of extra armor and magic resist" (since 26.1). — [senseos dragons guide](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/) (search summary)
- **Per-stack Dragon Slayer buffs.** A senseos guide says it was checked against 26.21 on Oct 25 2026. Values are 1 to 4 stacks:
  - **Infernal (화염)**, Infernal Might: +3% AD/AP per stack, so 3/6/9/12%.
  - **Mountain (대지)**, Mountainous Vigor: armor/MR from 5% to 20%.
  - **Ocean (바다)**, Oceanic Will: regenerates 2% to 8% of missing HP every 5 s.
  - **Cloud (바람)**, Cloudbringer's Grace: slow resist and out-of-combat movement speed from 5% to 20%.
  - **Hextech (마법공학)**, Hextech Prowess: 5/10/15/20 ability haste and 5/10/15/20% attack speed.
  - **Chemtech (화학공학)**, Chemtech Blight: tenacity and heal/shield power from 6% to 24%.
  - — [senseos](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/); [LoL Wiki Dragon Slayer](https://wiki.leagueoflegends.com/en-us/Dragon_Slayer); [agatasmurf](https://agatasmurf.com/league-of-legends-dragons/)
- **Dragon Soul (용의 영혼)** on standard Summoner's Rift: "The first team to four takes Dragon Soul, and Elder Dragon follows 6 minutes later". The soul element is the one that transformed the map, which happens after the second drake.
  - Cloud Soul gives 15% bonus movement speed (down from 20% in 25.S1.3).
  - Chemtech Soul gives 13% damage and damage reduction below 50% HP (up from 11% in 25.S1.3).
  - Ocean Soul: damaging enemies heals "150 base" and restores "100 base mana over 4 seconds", at 30% effectiveness against minions and monsters.
  - Mountain Soul: a shield after 5 s without taking damage.
  - — [senseos](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/); [agatasmurf](https://agatasmurf.com/league-of-legends-dragons/)
- **Conflict, now resolved:** a search summary of the Riot 26.1 notes said "Dragon Soul is now awarded if a team manages to kill both Elemental Drakes" and "Elder Dragon now spawns at 15:00". On cross-check, these lines refer to **Swiftplay**, where only two drakes spawn. The standard Rift rule is still four drakes. No source confirmed a two-drake soul on standard SR. — [Riot 26.1](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-26-1-notes/); [senseos](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/)
- **Rift terrain changes (협곡 지형 변화):** the only detailed source is old (Dignitas, about 2020):
  - Mountain adds walls near the pit.
  - Ocean adds brush around the pit and buff camps.
  - Infernal removes brush and opens new jungle paths.
  - Cloud and Hextech/Chemtech add their own map changes.
  - Treat this as **older mechanics**. No 2026 source detailed current terrain. — [Dignitas Elemental Terrain Guide](https://dignitas.gg/articles/blogs/Unknown/14573/weathering-the-rift-elemental-terrain-guide)
- **Elder Dragon (장로 드래곤):**
  - It replaces elemental drakes once a team has soul and respawns every 6:00. — [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html); [senseos](https://senseos.gg/guides/league-of-legends/dragons-and-dragon-soul/)
  - 26.1: "Elder Dragon will have around 20% more effective HP but should otherwise feel similar". — [Riot 26.1](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-26-1-notes/)
  - Buff: **Aspect of the Dragon (장로 드래곤의 위상)** for **150 s** goes to all *living* teammates. Damaging a champion below **20% max HP** triggers **Elder Immolation**, which executes after 0.5 s. It is negated by invulnerability and minimum-HP effects but can trigger on untargetable enemies. The older 180 s figure (patch 10.18) is outdated. — [LoL Wiki Elder Dragon](https://wiki.leagueoflegends.com/en-us/Elder_Dragon); [Wiki buff template](https://wiki.leagueoflegends.com/en-us/Template:Buff_data_Aspect_of_the_Dragon); [riftpatchnotes Elder](https://www.riftpatchnotes.com/lol/unit/elder-dragon)

**Void Grubs (공허 유충)**
- Spawn **8:00**, three grubs, **no respawn since 25.09**. If untaken, they "leave for good at 14:45 (or 14:55 if they're mid-fight)". — [nerfplz Voidgrubs/Herald guide](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html) (URL date after today, so caution); [gamerstogether.cz 2026](https://gamerstogether.cz/en/lol-jungle-objectives-guide/)
- When a fight starts, and every 12 s while it continues, each grub spawns 4 voidmites. **Smite cannot target voidmites.** — [nerfplz](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html)
- Rewards:
  - Each grub gives a team stack of Touch of the Void and "65 XP … per grub".
  - Gold goes only to the killer. One source says 30 g per grub.
  - A Korean guide says 26.1 cut grub gold from 210 to 90 total and XP from 80 to 65.
  - Three grubs give **Hunger of the Void**: allied voidmites that attack turrets.
  - — [nerfplz](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html); [vortexgaming 2026 시즌1 정글 분석](https://vortexgaming.io/postdetail/635801)
- Patch 26.11 (May 27 2026): Hunger of the Void summoned voidmite health went from 60% to **100% of a melee minion**. — [riftpatchnotes Void Grubs](https://www.riftpatchnotes.com/lol/system/void-grubs) (search summary)
- **Conflict:** one Korean reprint of the patch notes says "공허 유충이 삭제되었습니다" (Void Grubs were deleted). Every other 2026 source, including 26.11 changes to grubs, shows grubs still exist. That line is probably a Swiftplay-mode line or a reprint error. — [ruliweb 26.1 reprint](https://bbs.ruliweb.com/news/board/300007/read/2339910) vs [riftpatchnotes 26.11](https://www.riftpatchnotes.com/lol/system/void-grubs)

**Rift Herald (협곡의 전령)**
- Spawns **15:00** in the top pit and is replaced by Baron at 20:00. It despawns 19:45 (prior notes). — [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html)
- Patch 26.1:
  - "Experience reduced to 240 at all levels from 309/318/330 (at level 6/8/11). Experience radius increased to 2000 from 600."
  - Gold goes to the killer only, 100 g.
  - Eye cooldown went from 8 to 6 s.
  - 50% more damage to non-champions.
  - Herald was "Most recently adjusted in Patch 26.12 (June 9, 2026)".
  - — [Riot 26.1](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/); [thegamehaus](https://thegamehaus.com/league-of-legends/full-lol-patch-26-1-patch-notes-for-demacia/2026/01/07/); [riftpatchnotes Herald](https://www.riftpatchnotes.com/lol/system/rift-herald) (search summaries)
- **Eye of the Herald (전령의 눈)** usage, last known mechanics from patch 14.22 (2024), with no 2026 update found:
  - The Eye is lost after 4 minutes if unused.
  - When summoned, Herald starts with 1 charge and mounts or charges a turret, dealing "150 damage plus 25% of her current health to the turret and herself".
  - She gains another charge only "after assisting in destroying an enemy turret".
  - — [LoL Wiki Eye of the Herald](https://wiki.leagueoflegends.com/Eye_of_the_Herald); [Leaguepedia](https://lol.fandom.com/wiki/Eye_of_the_Herald)
- **Conflict:** one search snippet of the Riot notes said Herald "has been removed". This is again almost certainly the Swiftplay section. — [Riot 26.1](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/)

**Baron Nashor (내셔 남작 / 바론)**
- 26.1: spawn "25:00 ⇒ 20:00", respawn 6:00. Baron's spawn no longer corrupts Red/Blue buffs. Baron received "Elder-like treatment" with reduced gold. — [Sportskeeda 26.1](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes); [games.gg](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/)
- **Gold conflict:** "1525 → 850" total value is attributed to **Baron** in one search summary and to **Herald** in another. I could not resolve which. — [search summary citing esports-news.co.uk](https://esports-news.co.uk/2026/01/07/league-of-legends-patch-26-1-kicks-off-the-new-year-with-huge-changes/)
- Korean guide: Baron came back at 20 min with higher durability and more skillshot damage. — [vortexgaming](https://vortexgaming.io/postdetail/635801)
- Buff **Hand of Baron (내셔 남작의 손길)**:
  - Lasts 180 s, or until the holder dies.
  - Gives bonus AD/AP, which "is set when the team takes the buff and does not grow over time".
  - Gives an empowered recall and empowered nearby minions.
  - — [LoL Wiki Hand of Baron](https://wiki.leagueoflegends.com/en-us/Hand_of_Baron); [nerfplz Baron guide](https://www.nerfplz.com/2026/10/baron-nashor-guide-spawn-timers-three.html)
- **Baron variants / pit terrain:** each game randomly picks one of three Baron forms, which stays for the whole match. games.gg names them Territorial, Hunting and All-Seeing, and each changes the pit's surrounding terrain. These forms date from 2025 (25.S1) and apparently persist in 2026. — [nerfplz Baron guide](https://www.nerfplz.com/2026/10/baron-nashor-guide-spawn-timers-three.html); [games.gg beginner's guide](https://games.gg/league-of-legends/guides/league-of-legends-beginners-guide/)
- nerfplz claims that in Season 16, Voidborn scuttlers reveal enemies and wards in their death area. This is **unconfirmed** by official notes. — [nerfplz Baron guide](https://www.nerfplz.com/2026/10/baron-nashor-guide-spawn-timers-three.html)
- **Baron power play (바론 버프 굴리기):** no 2026-specific source surfaced. See Gaps.

**Atakhan (아타칸)**: removed in 26.1 and **does not exist in Season 2026**. Treat any guide that mentions Atakhan, Blood Roses or Feats of Strength as 2025 or older. — [Riot 26.1](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [inven post-era discussion](https://www.inven.co.kr/board/lol/3370/571311)

**New 2026 map/vision mechanic: Faelights (Korean name unverified; possibly "요정등불")**
- "Faelights are rings of glowing mushrooms placed at specific map locations. When you place any ward on a Faelight ring, it becomes a superward", which gives extra vision beyond normal ward range. — [games.gg 26.1](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/); [Sportskeeda 26.1](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes)
- 26.3: "the River Pixel Brush reveal region cuts off before scuttle pad and epic pit entrance". — [u.gg 26.3](https://u.gg/lol/news/patch-26-3-notes-league-of-legends) / [patched.gg 26.3](https://patched.gg/games/league-of-legends/patch-263-notes) (search summary)

**Turrets / inhibitors (포탑 / 억제기) basics, 2026**
- Plates are permanent and extend to inner and inhibitor turrets (26.1). First turret gives 300 g. — sources above.
- 26.3: plate temporary resists went from "20–100 per plate → 30–50 per plate". Commentators read this as making solo pushes harder and group pushes easier. — [dtgre 26.3 guide](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html); [u.gg 26.3](https://u.gg/lol/news/patch-26-3-notes-league-of-legends) (search summary)
- Inhibitor respawn time and turret stats for 2026 were not found. See Gaps.

**Objective bounties and comeback mechanics (오브젝트 현상금)**
- LoL Wiki (current page, undated):
  - Objective bounties are a team-level comeback system on SR only.
  - "accrual is now based on the enemy's gold lead exclusively".
  - They scale "at a rate of 10% of the team gold deficit, capped at 1000 gold per objective".
  - Claiming one "cancels all other objective bounties on the map".
  - — [LoL Wiki Objective bounties](https://wiki.leagueoflegends.com/en-us/Objective_bounties)
- esports.gg: Riot made bounty changes aimed at "less snowballing", with bounties "turning off quicker". "Gold, Turrets, and Voidgrubs" now weigh more heavily in the bounty algorithm. The date is unclear. — [esports.gg](https://esports.gg/news/league-of-legends/next-lol-bounty-changes-should-mean-less-snowballing-devs-hope/)
- 26.3 champion bounties: devalue rate on death went from "1 per 2.5 gold given out -> 1 per 3.5 gold given out", and farming-based increments slowed from 1/5 to 1/7. — [u.gg 26.3](https://u.gg/lol/news/patch-26-3-notes-league-of-legends); [dtgre](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html)
- Riot design intent: comebacks "have to be earned", and teams far ahead "have a lot of agency to prevent or mitigate bounty claims". — [Riot Quick Gameplay Thoughts: Comeback Mechanics](https://www.leagueoflegends.com/en-us/news/dev/quick-gameplay-thoughts-2-25-comeback-mechanics/)
- Older flat values (500 g for Baron, Elder, Dragon and Herald; 250 g for outer turrets) date from about 2021 and are **outdated**. — [afkgaming](https://afkgaming.com/esports/news/what-are-objective-bounties-in-league-of-legends)

**Smite (강타)**
- 15 s cooldown. Deals 600 true damage to medium and large monsters. It becomes Unleashed Smite after the pet is fed (the riftpatchnotes page says 15 treats; another entry on the same site says 20, which is a conflict).
- Primal Smite (upgraded) deals 1400 monster damage (up from 1200). Sources say this changed in 26.1 or 26.12, which also conflicts.
- 26.12 added 20–160 Smite damage to pets.
- 26.4: omnivamp no longer applies to Smite or Ignite.
- — [riftpatchnotes Smite](https://www.riftpatchnotes.com/lol/spell/smite); [riftpatchnotes Primal Smite](https://www.riftpatchnotes.com/lol/spell/primal-smite); [sheepesports 26.4](https://www.sheepesports.com/articles/league-of-legends-patch-26-4-omnivamp-no-longer-applies-to-smite-and-ignite/en)

**Vision items and rules (시야)**
- **Stealth Ward (투명 와드):** "Limit 3 Stealth Wards on the map per player", and Warding Totem wards count toward this cap. Duration starts at about 90 s and scales with average team level. — [LoL Wiki Stealth Ward](https://leagueoflegends.fandom.com/wiki/Stealth_Ward); [Leaguepedia Vision guide](https://lol.fandom.com/wiki/New_To_League/Gameplay/Vision); [wecoach junglers vision](https://wecoach.gg/blog/article/league-of-legends-vision-control-warding-guide-for-junglers)
- **Deep Ward:** Stealth and Totem wards placed in the enemy jungle or the river get more health and duration. — [LoL Wiki Warding](https://wiki.leagueoflegends.com/en-us/Warding) (search summary)
- **Control Ward (제어 와드):**
  - One per player on the map.
  - No duration; it lasts until destroyed or replaced.
  - Costs 75 g.
  - 26.1 role quests: supports pay 40 g after completing their quest and can store 2 in the Role Quest slot.
  - — [Mobalytics vision guide](https://mobalytics.gg/blog/lol-warding-guide/); [games.gg 26.1](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/)
- **Trinkets (장신구):**
  - Warding Totem (와드 토템) cooldown: 26.1 changed it from 210–120 s to 170–90 s by level. 26.3 changed it again to **210–90 s by level** (both values come from search summaries).
  - Oracle Lens (예언자의 렌즈) duration: 6 s → **8 s** (26.1).
  - Farsight Alteration (망원형 개조): available after level 9. It reveals an area for about 2 s and leaves a ward with no timer that dies when it spots an enemy champion.
  - — [games.gg 26.1](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/); [u.gg 26.3](https://u.gg/lol/news/patch-26-3-notes-league-of-legends); [nerfplz trinkets](https://www.nerfplz.com/2026/12/trinkets-explained-10-rules-of-free-slot.html) (URL dated after today, so caution)
- **Vision score (시야 점수):** "Vision Score = (1 point per minute of ward lifetime provided) + (1 point per minute of ward lifetime denied)". Riot calls it a "loose measurement". Modifiers reduce score for wards near your own base (up to about −50% at base walls) or where allied vision already exists. — [LoL Wiki Vision score](https://wiki.leagueoflegends.com/en-us/Vision_score); [LoL Theory vision score](https://blog.loltheory.gg/vision-score-lol/)

### Inferences
- The 2026 objective timeline is:
  - 3:30 Scuttle
  - 5:00 Drake
  - 8:00 Grubs, once only, gone at 14:45
  - Drakes every 5:00
  - 15:00 Herald
  - 20:00 Baron
  - Elder after soul
- With Atakhan gone and plates now permanent, turret gold matters more for the whole game. Grubs' Hunger of the Void (buffed in 26.11) and Herald feed into that turret gold, so top-side objectives convert to gold through turrets rather than directly.
- The Dragon Vengeance increase means that when the enemy is near soul, contesting the drake by DPS is harder. The jungler's Smite and steal threat, or zone control, matter more.

### Gaps
- None of the numbers could be verified on the primary Riot or Wiki pages because fetches were blocked. The domains www.leagueoflegends.com, wiki.leagueoflegends.com, riftpatchnotes.com and esports.gg need to be allowed.
- 2026 values for Infernal, Mountain and Hextech soul, Hand of Baron AD/AP numbers, and the 2026 Baron and Herald gold split (the 1525 → 850 attribution) remain unconfirmed.
- No 2026 source covers current rift terrain changes, inhibitor respawn time, or whether Herald charge mechanics changed after 14.22.
- I found no 2026 source with Baron power-play specifics (minion buff numbers, siege tactics).
- The official Korean term for Faelights is unverified.

---

## Q2. How coaches recommend junglers set up vision and objectives (incl. control vs trading, smite fights, deep vs defensive wards, sweeping, fog usage)

### Takeaway
Coaches and guides consistently recommend the following:
- **Arrive about 60–90 s early** with a reset and lane priority on the nearby lanes.
- **Sweep before you ward**, then place a control ward in or near the pit and the tri-bush.
- **Deep-ward the enemy jungle entrance** (enemy Blue/Red side) to see their approach.
- **Trade cross-map rather than flip a coin** when you lack priority.

Specific timings vary by source (90 s, 60 s, 30 s, or "a minute-plus"). They are rules of thumb, not fixed numbers.

### Cited Findings
- "Prioritize vision around the next dragon or Baron a minute-plus early". The minute before an objective is the "vision window". — [metabot.gg warding guide](https://metabot.gg/en/league/guides/warding-vision-control-guide); [wecoach jungler vision guide](https://wecoach.gg/blog/article/league-of-legends-vision-control-warding-guide-for-junglers) (search summary; which phrase came from which page is unconfirmed)
- Sweep first: enemy control wards "eat your stealth wards for free", and "vision that arrives when the dragon is already up is too late". — same search set ([metabot.gg](https://metabot.gg/en/league/guides/warding-vision-control-guide); [wecoach](https://wecoach.gg/blog/article/ward-like-a-pro-challenger-league-of-legends-vision-control-ward-guide))
- "Triangle of Control" for Dragon: the dragon pit, plus the tri-bush near the bot tier-1 turret, as control-ward spots. Also put a ward "deep in the enemy jungle, usually by the Blue or Red depending on what side you're on when going for dragon or Baron". — [1v9.gg warding guide](https://1v9.gg/blog/league-of-legends-lol-how-to-ward-complete-guide-tips-tricks); [wecoach](https://wecoach.gg/blog/article/league-of-legends-vision-control-warding-guide-for-junglers) (search summary)
- Prior notes, not repeated in detail here: Boosteria's 90/60/30 plan ("Reset if you need to spend gold"; "One minute before it matters, do the setup checklist: reset, clear toward, vision, lane priority"). Refresh wards about 60 s or about 30 s before spawn, "ideally after pushing the nearby lane". Don't spend both Smite charges on camps when a drake spawns within 45 s. — see `jungler_turn_sync.md` §2 ([Boosteria](https://boosteria.org/guides/lol-jungle-guide-for-beginners))
- Objective trading: "if the enemy jungler shows top, take dragon. If they show bot, take Herald or grubs". "Trade sides, never chase." — prior notes §5 ([LoL Theory](https://blog.loltheory.gg/how-to-play-jungle-lol/); [Level Legendary](https://levellegendary.com/vertical-jungling-splitting-the-map/))
- Objective priority guides for 2026: [LoL Sensei objective priority](https://www.lolsensei.com/en/blog/objective-priority-guide); [Boosteria objectives](https://boosteria.org/guides/league-legends-objectives-guide). Search titles only, with no extractable quotes.
- Vision score benchmarks and how to read them: [LoL Theory "Vision Score… Honest Benchmarks"](https://blog.loltheory.gg/vision-score-lol/). No numbers were extracted.

### Inferences (jungler how-to and common mistakes, synthesized from the sources above; not direct quotes)
- **Setup sequence for a drake:**
  - About 90 s before spawn: finish the current camps and reset with the bot and mid laners.
  - About 60 s before: walk in, sweep with Oracle Lens (now 8 s), and place a control ward in the pit or tri-bush.
  - About 30 s before: put a stealth ward on the enemy's approach (their raptor or blue entrance, or a Faelight ring for wider vision), then hold fog and wait.
- **Deep vs defensive wards:**
  - Deep wards (enemy jungle entrances) tell you *where* the enemy is coming from, which lets you choose to fight or trade.
  - Defensive wards (your own jungle and flank) stop picks while you are on the objective.
  - When you are behind, use defensive vision and plan to trade the objective rather than contest it.
- **Fog of war usage:** clearing enemy vision around the pit lets you start the objective unseen, or lets your team flank from fog. Standing in your own vision while the enemy's is cleared gives you the information advantage.
- **Smite fights:**
  - Track the enemy Smite (the 15 s cooldown) and the objective's HP against Smite damage. Primal Smite deals 1400 to monsters.
  - Enemy junglers near the pit with Smite up are the steal risk, so zone them before bursting the objective.
  - On Grubs, voidmites cannot be Smited, so do not waste Smite on them.
- **Common mistakes:**
  - Warding after the objective spawns.
  - Placing stealth wards before sweeping, so the enemy control ward kills them.
  - Contesting without lane priority.
  - Full-clearing and recalling as the objective spawns (this one is in the prior notes).
  - Burning Smite on camps right before spawn.
  - Fighting into Dragon Vengeance when the enemy is on soul point instead of zoning.
  - Chasing the enemy jungler instead of cross-trading.

### Gaps
- No full-text coach source (pro coach interview, ProGuides, Mobalytics full page) could be read. Specific quotes on 90/60/30 setups come from search snippets only.
- No Korean coach or 인벤 guide on 2026 vision setup was retrieved. Namu Wiki's 와드 and 오브젝트 pages were not fetched.
- No source on how Faelights change standard warding spots around Dragon and Baron in practice.
