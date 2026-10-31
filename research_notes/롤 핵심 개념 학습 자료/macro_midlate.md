# League of Legends Mid/Late-Game Macro Concepts (for a Platinum jungler learning library)

> Scope note: This file covers concepts that come after the laning phase. Tempo, wave states, lane priority, recall sync, cross-map trades and objective spawn timers are already covered in `/home/user/LoLDosa/research_notes/롤 턴 개념과 정글 운영/` (english_tempo_wave_prio.md §5–6, jungler_turn_sync.md §5–6). They are not repeated here, only referenced.
>
> Key 2026 constants from that earlier research (Patch 26.1, Jan 2026), restated only because later concepts depend on them:
> - Atakhan removed.
> - Baron spawns at **20:00** and respawns **6:00** after each kill.
> - Rift Herald spawns at 15:00 and despawns at 19:45.
> - Elder spawns after a soul, then every 6:00.
> - Waves spawn every 25 s after 14:00 and every 20 s after 30:00.
>
> **Research limitation:** In this session, WebFetch could not reach mobalytics.gg, nerfplz.com and similar domains (DNS block). Every finding below comes from **search-result snippets/summaries**, not full-page reads. "Exact quotes" are the text the search tool returned and should be re-checked on the page before they are published in the app. The domains that need allowing are mobalytics.gg, nerfplz.com, wiki.leagueoflegends.com and namu.wiki.

## Q1. Coaching definitions and decision rules per concept (baron calls, numbers, death timers, sieging, splitting, etc.)

### Takeaway
Across sources the decision rule is consistent: **start Baron or Elder only after a numbers advantage or a bought death timer**, or when the enemy is pulled elsewhere. Never start because "it's up."

Split-push and 1-3-1 setups require that **the remaining 4 can fight 4v5 or 4v4** and that the splitter has fast waveclear.

Hard mechanics that frame mid/late decisions:
- Plates fall at 14:00.
- First-turret bonus is 300 g.
- Hand of Baron lasts 180 s.
- Inhibitors respawn after 5:00.
- Elder executes enemies below 20% HP.
- Death timers scale with level and game time.
- Objective bounties are the main comeback system and were last re-tuned in 26.6.

### Cited Findings

**Transition from laning to mid game (포탑 방패/플레이트 소멸, 첫 포탑 — "turret plates gone, first tower")**
- Turret plating: "Plates fall and all of the following associated bonuses disappear at 14:00 game time." As plates are lost, the turret "gains increasing damage resistance, thus becoming harder to destroy." — [LoL Wiki, Fortification](https://wiki.leagueoflegends.com/en-us/Fortification) (snippet)
- First turret: "The local reward for destroying the first turret (also referred to as 'Turret First Blood' and 'First Turret gold') grants 300 bonus gold." — [LoL Wiki, Turrets](https://wiki.leagueoflegends.com/en-us/Turrets) (snippet). It is unconfirmed whether any 2026 patch changed this value.
- A 2026 analysis mentions season changes to turrets and vision. One example: Homeguard "can reach Tier 1 turrets in the early game, and minion waves in the mid-to-late game", which affects how fast teams rotate after the first tower falls. — [vortexgaming.io](https://vortexgaming.io/en/postdetail/606346) (snippet; details not verified)
- From the earlier research: after 14:00, waves come every 25 s instead of 30 s. Plate removal and the faster cadence happen at the same moment. — see `english_tempo_wave_prio.md` §6 ([Riot Patch 26.1 Notes](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/))

**Grouping vs splitting / side lane assignment / 1-3-1 / 1-4 (스플릿 푸시 "split push", 사이드 "side lane", 1-3-1, 1-4)**
- Mobalytics on the 1-3-1: these are "basically split push team compositions, with 2 champions in the solo lane while 2 or 3 champions stay in the other lane". The aim is to "not die and apply pressure to multiple places at once". It also stresses vision, timing, and being ready to group as 5. The page was listed as updated Oct 31, 2025. — [Mobalytics, How to Play 1-3-1](https://mobalytics.gg/blog/lol-how-to-play-1-3-1/) (snippet)
- Mobalytics' split-push precondition: "your team can fight 4v5 or 4v4 and do so successfully, and you can push waves quickly and clear them fast." Its counter-split advice: "you must fight the enemy when they're split up." — [Mobalytics, How to split push](https://mobalytics.gg/lol/guides/how-to-split-push); [Mobalytics split push comp](https://mobalytics.gg/blog/lol-how-to-split-push-comp/) (snippets)
- Community guide on beating split pushes: waveclear counters it, "if you cannot get to the tower to do damage, it doesn't really help." — [r/summonerschool, A basic guide to split pushing (2016)](https://r.datuan.dev/r/summonerschool/comments/59o9ad/a_basic_guide_to_split_pushing/) (old, but the principle still holds)
- 1-4 explainer — [Gfinity, What is 1-4?](https://www.gfinityesports.com/league-of-legends/league-of-legends-what-is-1-4/) (only the title was surfaced; content not retrieved)
- 나무위키 (Korean wiki):
  - 스플릿 푸시 = 일부 인원을 사이드에 분산 배치해 여러 라인을 동시에 압박 ("split push = spread some members to the side lanes to pressure several lanes at once").
  - 한쪽 사이드 라이너가 일방적으로 밀리면 본대가 추가 병력을 보내야 해 한타에서 취약해짐 ("if one side laner is pushed in one-sidedly, the main group must send more people and becomes weak in teamfights").
  - 한 명이라도 자리를 비우면 한타에서 대패하거나 잘릴 수 있는 상황에서는 쓰기 어렵다 ("hard to use when even one absence can mean a lost teamfight or getting picked off").
  - 1-3-1 = 탑 1, 미드 3, 봇 1로 전 라인을 압박하는 스플릿 운영 ("a split setup with 1 top, 3 mid, 1 bot pressuring every lane"); 2015 시즌 T1 사례 ("T1's 2015 season as the example").
  - 날개 운영 = 중반 이후 3라인을 모두 밀면서 운영하는 스타일 ("'wing' play = pushing all three lanes from mid game on").
  - — [나무위키, 리그 오브 레전드/용어](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%9A%A9%EC%96%B4); [나무위키, 용어/은어](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%9A%A9%EC%96%B4/%EC%9D%80%EC%96%B4) (search summaries drawn from several revisions; wording differs between revisions)
- 1-3-1 is "community shorthand, not a wiki-defined term: one champion top, three around mid or an objective, one bot." — search summary of a Mobalytics-style explainer (source URL not clearly identified; low confidence)

**Picks / catches (끊기, 끊어먹기, 잘라먹기 — "picking off / cutting off")**
- 나무위키 defines 끊어먹기 (also called 짤라내기 / 끊어내기) as 적 한두 명이 팀에서 떨어져 있을 때 여럿이 몰려가 제거하거나, 한타 중 그랩 같은 스킬로 먼저 잡는 행위 ("when one or two enemies are separated from their team, several players collapse and kill them; or catching someone first with a skill like a grab during a teamfight"). It notes that this buys time to regroup when you are being pushed (밀리는 상황에서 정비 시간을 버는 데 전략적 의미), and that it matters more the later the game goes (후반으로 갈수록 효과가 크다). — [나무위키, 용어/은어](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%9A%A9%EC%96%B4/%EC%9D%80%EC%96%B4) (search summary)
- Community advice is to create the numbers lead first: "If you can ambush someone or set up a tent somewhere, you will get the numbers lead over the enemy." — [Mobafire Q&A, "Calling" Baron](https://www.mobafire.com/league-of-legends/question/quot-calling-quot-baron-233) (snippet)

**Baron setup and calls (바론 콜 — "Baron call")**
- Start-Baron rule (search summary of several guides): start "after a pick, a lost teamfight on the enemy side, or a bought-out death timer that leaves fewer than five enemies able to contest". Another phrasing: "the ideal time to start Baron is when you have a numbers advantage (e.g., after winning a teamfight) or when the enemy team is distracted by other objectives." — [Mobalytics, 5 tips to secure the baron safely](https://mobalytics.gg/lol/guides/5-tips-to-secure-the-baron-safely); [Mobalytics, 4 tips secure baron](https://mobalytics.gg/blog/4-tips-secure-baron-league-of-legends/); [nerfplz Baron guide 2026](https://www.nerfplz.com/2026/10/baron-nashor-guide-spawn-timers-three.html) (snippets; attribution to a specific page is approximate)
- Mobafire community rule: call Baron when "your team has a numbers advantage over an enemy team (i.e. 2 enemies are dead) such that you cannot lose even if they all-in'd you at Baron." — [Mobafire Q&A](https://www.mobafire.com/league-of-legends/question/quot-calling-quot-baron-233)
- "You should never recall if your team is dancing around objectives like the Baron or Elder Dragon, as they will use the numbers advantage to win the fight." — (search snippet; probably from [Mobalytics recall timers](https://mobalytics.gg/blog/lol-5-best-recall-timers/), not verified)
- Hand of Baron: granted to all living teammates for **180 s**. It was cut from 210 s in V9.23. Recall is also halved (see earlier notes). — [LoL Wiki, Hand of Baron](https://wiki.leagueoflegends.com/en-us/Hand_of_Baron) (snippet)
- 2026 changes: 26.1 gave Baron "an Elder-like treatment (reduced overall gold reward)", and its spawn no longer corrupts Red/Blue buff (from the earlier research). 26.13 contains only a bug fix that centers Baron's spawn location. No 26.x change to buff duration was found. — [riftpatchnotes Baron](https://www.riftpatchnotes.com/lol/unit/baron-nashor); [Riot 26.1 notes](https://www.leagueoflegends.com/en-us/news/game-updates/patch-26-1-notes/)
- **Spawn time conflict:** one riftpatchnotes entry says "Initial spawn timer increased to 25:00 from 20:00" in 25.S1.1. That was the 2025 Atakhan era, and 26.1 reverted it to 20:00. The 2026 guides say 20:00.
- Pro pattern (low-reliability commercial source): top teams take full river vision right after Baron spawns and force the objective. — [onepiece.gg, early baron setups](https://onepiece.gg/early-baron-setups-punish-weak-lol-scaling-composition/)

**Elder setup / soul point fights (장로 드래곤 "Elder Dragon", 영혼 포인트 "soul point")**
- Elder buff: executes enemies "below 20% of their maximum health", after a 0.5 s delay. It is "granted to all living members of the slayer's team." — [LoL Wiki (Dragon Slayer / Aspect)](https://wiki.leagueoflegends.com/en-us/Infernal_Might) (snippet)
- Setup advice: the team that is ahead should "control vision, push the enemy out of river, and make sure the opposing Smite cannot easily enter the play." — [earlygame.com, Is Elder Dragon too strong?](https://earlygame.com/news/lol/league-of-legends-is-elder-dragon-actually-too-strong) (snippet)
- "Elder plus a soul is the standard way a team closes at forty minutes, so treat the Elder timer as a fight timer and get vision down long before it lands." — [nerfplz, Dragons explained (2026)](https://www.nerfplz.com/2026/10/lol-dragons-explained-10-things-pit.html) (search summary; single blog)
- Conflict: guildorder.com says Elder spawns "35-min+ after first soul". This contradicts the official wiki's 6:00-after-soul. Treat guildorder as unreliable. — [guildorder objectives reference](https://guildorder.com/games/league/wiki/objectives-reference)
- Elder buff duration was **not found** (see Gaps).

**Inhibitor / super minion pressure (억제기 "inhibitor", 슈퍼 미니언 "super minion")**
- Inhibitors respawn after a flat **5:00** ("since the V1.0.0.96, it is a consistent 5 minutes"). — [LoL Wiki, Inhibitors](https://wiki.leagueoflegends.com/en-us/Inhibitors) (snippet)
- "If a team's inhibitor is destroyed, one super minion spawns for the enemy team on the same lane... If all of a team's inhibitors are destroyed, two super minions spawn on each lane." — [LoL Wiki, Minion](https://wiki.leagueoflegends.com/en-us/Minion_(League_of_Legends)) (snippet)
- How many super waves per inhibitor down: the wiki says "a Super Minion in each wave for the next 8 minion waves". "Usually two minion waves before the Inhibitor completely recovers will not have any Super Minions", which "prevents the Inhibitor from instantly being destroyed again". — [LoL Wiki, Inhibitors](https://wiki.leagueoflegends.com/en-us/Inhibitors). **Conflict:** Mobalytics describes one super minion every 30 s for the full 5:00 (about 10 waves). — [Mobalytics wave management](https://mobalytics.gg/blog/wave-management/). Note that the 26.1 cadence of 25 s/20 s waves changes this count, and 26.1 also lowered super minion value (earlier notes).

**Death timers / respawn timing calls (데스 타이머 "death timer", 부활 시간 "respawn time")**
- LoL Wiki: death timers increase with champion level and with game time. "Total death time = BRW + BRW × TIFx", where BRW is the base respawn wait and TIF is the time-impact factor. Game-time scaling starts after 15 min, and TIF "has a hard cap of 50%." — [LoL Wiki, Death](https://wiki.leagueoflegends.com/en-us/Death) (search summary)
- The Chinese fandom wiki states "the exact formula used to determine the death timer's duration is unknown", so the base table is an estimate. — [LoL Fandom (zh), Death](https://leagueoflegends.fandom.com/zh/wiki/Death)
- **Conflicting numbers:** gameboost lists 6 s (lvl 1) to 52.5 s (lvl 18) from level alone. nerfplz (2026) gives a maximum of 78.75 s at level 18 "once the game clock multiplier caps at 55 minutes". 52.5 × 1.5 = 78.75, which fits the 50% cap, so the two may be consistent (base vs. capped). — [gameboost, death timer](https://gameboost.com/definitions/league-of-legends/death-timer); [nerfplz, Dying in LoL (2026)](https://www.nerfplz.com/2026/10/dying-in-lol-10-things-that-happen.html) (snippets)
- Staggered deaths: "If you can stagger the enemy death timers however, you can often win the game much earlier than you normally could." — [NERFPLZ, Top 10 Tips for Super Long Games (2017)](https://nerfplz.com/2017/01/top-10-tips-for-super-long-games.html) (old)
- Timer tracking matters — [Dignitas, keeping and maintaining timers](https://dignitas.gg/articles/blogs/League-of-Legends/6991/the-importance-of-keeping-and-maintaining-timers-in-league-of-legends) (only the title was surfaced)

**Playing from behind (역전 — "comeback": bounties, objective bounties, defensive play, waveclear)**
- Objective bounties are "a negative feedback (comeback) system that creates opportunities for a losing team to earn a moderate gold boost by taking down marked turrets and other objectives". They appear "15 seconds after" the gap crosses the threshold. — [LoL Wiki, Objective bounties](https://wiki.leagueoflegends.com/en-us/Objective_bounties) (snippet)
- History:
  - 2021 values: Baron/Elder 500 g, Dragon/Herald 500 g, outer turret 250 g (likely outdated).
  - 14.21: grubs count toward the gap; XP is weighted less and gold more; bounties "deactivate swiftly if the losing team makes a comeback".
  - 2025: mini-rework so bounties no longer fully reset on a champion death.
  - 25.09: further tweaks.
  - **26.6** "updated and cleaned up Objective bounty formulas" (latest found).
  - — [LoL Wiki](https://wiki.leagueoflegends.com/en-us/Objective_bounties); [Sportskeeda 14.21 bounty changes](https://www.sportskeeda.com/esports/all-bounty-changes-league-legends-patch-14-21-explained); [esports.gg, next bounty changes](https://esports.gg/news/league-of-legends/next-lol-bounty-changes-should-mean-less-snowballing-devs-hope/); [Riot, Quick Gameplay Thoughts 2/25: Comeback Mechanics](https://www.leagueoflegends.com/en-us/news/dev/quick-gameplay-thoughts-2-25-comeback-mechanics/)
- Riot's design intent (Korean dev blog): 스노우볼 = 작은 이득을 바탕으로 더 큰 이득을 얻어 승기를 굳히는 방식 ("snowball = using small gains to get bigger gains and lock in the win"). Riot tunes so early leads matter but "초반에 승패가 결정되지 않을 정도" ("not so much that the early game decides the result"). — [Riot KR, 2020년 2월 게임플레이에 대한 단상 3](https://www.leagueoflegends.com/ko-kr/news/dev/2020-february-quick-gameplay-thought-3/); [Riot KR, 게임플레이에 대한 단상 13.16](https://www.leagueoflegends.com/ko-kr/news/dev/quick-gameplay-thoughts-13-16/)
- Anti-snowball systems listed: shutdown bounties, objective comeback gold, faster early respawns. — [loltheory, Snowballing in LoL](https://blog.loltheory.gg/snowballing-lol/) (unofficial blog)
- Waveclear as a stall tool. A Riot designer (Ghostcrawler): "if you get trapped in your base the game should be over pretty quickly, I think we have too much waveclear". Waveclear serves both stalling and snowballing because it lets a team push, roam and invade. — [Inven Global](https://www.invenglobal.com/lol/articles/4568/riot-ghostcrawler-if-you-get-trapped-in-your-base-the-game-should-be-over-pretty-quickly-i-think-we-have-too-much-waveclear)
- Behind as a laner: build defensively, manage waves to limit trades. "Because you are behind, you have to respect the enemy and understand that warding can be difficult." — [Mobalytics, 5 ways to play behind (top), updated Oct 2025](https://mobalytics.gg/blog/5-ways-play-behind-top-lane/) (snippet)
- Scaling: scaling champions "need to limit falling behind in the early game as it will make your late game weaker." — [Mobalytics, best scaling champs](https://mobalytics.gg/blog/lol-5-best-scaling-champs/)
- Coaches teach junglers "when to trade objectives, when to stall and sacrifice one, and when to commit fully." Smite contests matter most "when the objective's health is low and both teams are ready to contest." — [WeCoach (IT), jungle coaching](https://wecoach.gg/it/blog/article/everything-you-need-to-know-about-league-of-legends-jungle-coaching) (snippet)

**Playing from ahead (스노우볼/굴리기 — "snowballing", closing games, not throwing)**
- Official wiki definition of snowball: one team's objective success leads to chained further successes that widen the gap. It has two axes: resources (XP, gold, permanent buffs) and map tempo. — [LoL Wiki, Snowball](https://wiki.leagueoflegends.com/en-us/Snowball) (search summary)

**Jungle role late game (vision around Baron/Dragon, smite threat, flank/peel)**
- Zoning definition: holding an area with threat to deny enemy movement and vision, in order to take an objective or stop the enemy from taking one. — [LoL Wiki, Zoning](https://wiki.leagueoflegends.com/en-us/Zoning) (search summary)
- Elder/Baron setup: deny the enemy Smite entry (earlygame, above). Securing Baron rests on "proper timers, vision, and team coordination." — [Metafy jungle class](https://metafy.gg/@hope-59dadca7/sessions/jungle-class-dwcSRPg6pWV) (listing snippet)
- Korean press example of a 바론 스틸 ("Baron steal") turning the game into a Nexus push — [inews24](https://www.inews24.com/view/1005412) (search summary)

### Inferences
- **Practical Baron/Elder call rule synthesized from the sources** (inference; no single source gives this exact form):
  - Start when (a) you are up at least 1 and ideally 2 players and their timers exceed the time to kill Baron, or (b) after a won fight, or (c) when the enemy is visibly committed elsewhere, such as a side wave or the opposite objective. Waves pushed and vision cleared are prerequisites.
  - Compare the enemy's longest respawn timer with your Baron kill time. Late-game timers approach 50–79 s (cap logic above). A long timer means a safe Baron; a short one means you need waves pushed first.
- **Siege after Baron:** 180 s of buff. Hand of Baron empowers nearby minions, so the value comes from pushing two lanes with the buff, not ARAMing mid. This is inferred from buff duration plus the split-push principles. The "how to use Baron" guides were not retrieved in full ([Mobalytics, make the most of Baron](https://mobalytics.gg/?p=12563)).
- **Inhibitor timing:** the inhibitor returns after 5:00 and the last ~2 waves have no super minions. The pressure window is therefore about the first 3–4 minutes after the kill, which is when side-lane splitting or a Baron call is strongest.
- **Playing from behind for junglers:**
  - Watch for bounty markers (gold flows to the losing team for objectives and turrets).
  - Use waveclear to stall.
  - Trade or concede objectives rather than coin-flip them.
  - Look for picks (끊기), which 나무위키 itself says matter more as the game goes on.
- **Tower take order** (outer → plates before 14:00 → inner and inhibitor) and **crossmap plays** are only lightly sourced here. Cross-map trades are covered in the earlier notes (jungler_turn_sync.md §5).

### Gaps
- No full-text coaching source was retrieved for: tower take order, 1-4 specifics, siege mechanics (e.g., poke sieging, when to dive a tier-2), side-lane assignment rules (who catches which side wave late game), shotcalling and ping etiquette, Elder buff duration, Baron power-play minion buff numbers in 2026, and 2026 objective bounty values after 26.6. All of these were blocked by fetch restrictions or produced no results.
- Coach Curtis, Skill Capped, ProGuides, LS and Broken by Concept: searches returned no usable content (mostly build pages and spam). These are **not represented**. Their YouTube or courses would need manual review.
- The death-timer formula is officially "unknown"; the values are community estimates.
- Whether 26.x changed first-turret gold (300) or plate timing (14:00) was not confirmed.

## Q2. Platinum-specific macro mistakes per coaches/data

### Takeaway
Little specific, reliable material exists. Most "Platinum mistakes" content is coaching sales copy. The recurring themes are: staying on the map too long, fighting without setup, ignoring wave states, bad recall/item timing, tunnel vision, recalling before an objective is decided, and collapsing a split-push comp by over-sending to one side.

### Cited Findings
- Coaching listing: "Staying too long on the map, random fights without setup, ignoring wave states, bad recall or item timing, tunnel visioning." — [Metafy, coaching low elo habits](https://metafy.gg/@jimlolll/sessions/coaching-low-elo-habits-ThvBWhEVgtJ) (sales copy)
- "I've coached dozens of players stuck in Gold and Platinum, and almost every time, the issue comes down to macro gameplay." — [GrowthNavigate, 5 macro mistakes that keep you hardstuck](https://www.growthnavigate.com/5-macro-mistakes-that-keep-you-hardstuck-and-how-to-fix-them) (single coach's opinion)
- A Challenger coach guide claims to cover "the 3 most common macro-game mistakes keeping players stuck in Platinum", but the mistakes themselves were not visible. — [Metafy, Iron-to-Challenger macro system](https://metafy.gg/guides/view/the-iron-to-challenger-macro-system-3-mist-OCcuR2EPGTF)
- Recalling while objectives are contested: "never recall if your team is dancing around objectives like the Baron or Elder" — (search snippet, Mobalytics recall article, see Q1)
- Splitting when the team cannot afford the absence: hard to use when 한 명이라도 자리를 비우면 한타에서 대패하거나 잘릴 수 있는 ("even one missing player can mean a lost teamfight or a pick-off"). — [나무위키 용어](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%9A%A9%EC%96%B4)
- Not respecting returning enemies: "avoid overcommitting when dangerous champions are about to return" (death-timer tip). — search summary ([nerfplz long games](https://nerfplz.com/2017/01/top-10-tips-for-super-long-games.html))

### Inferences
- Likely Platinum jungler macro mistakes, mapped from the cited themes (inference, not data-backed):
  1. Starting Baron without a numbers advantage or pushed waves ("it's up, let's do it").
  2. Not tracking death timers, so overstaying after a won fight or missing a Baron window.
  3. All five grouping mid after the first tower ("ARAM mid") while side waves crash into your own towers.
  4. Recalling or farming camps right before Elder or Baron spawns.
  5. Facechecking for vision when behind instead of sweeping with the group.
  6. Not watching Smite-steal or flank threat; the jungler stands where they can't Smite.
- The LoLDosa Platinum timeline data could check (1), (2) and (4) directly (Baron kill events vs. kills in the preceding 60 s, and recall events before objective spawns). See timeline_metrics.md in the earlier notes.

### Gaps
- No quantitative study of Platinum macro mistakes was found. Op.gg, Mobalytics and Riot data blogs were not reached. This is a candidate for LoLDosa's own data analysis.

## Q3. Korean caster/coach vocabulary (운영, 굴리기, 스노우볼, 역전각, 끊기, 시야 장악, etc.)

### Takeaway
나무위키's 용어 and 용어/은어 pages and Riot's Korean dev blogs are the citable Korean sources. They define 스플릿 푸시, 1-3-1, 날개 운영, 끊어먹기 (끊기) and 스노우볼. Several high-frequency caster terms (운영, 굴리기, 역전각, 시즈, 바론 콜, 시야 장악) had **no retrieved definition**. Their meanings below are standard community usage, marked unsourced.

### Cited Findings
- **스노우볼 (snowball):** 작은 이득을 바탕으로 더 큰 이득을 얻어 승기를 굳히는 방식 ("using small gains to get bigger gains and lock in the win") — [Riot KR dev blog 2020-02](https://www.leagueoflegends.com/ko-kr/news/dev/2020-february-quick-gameplay-thought-3/)
- **끊어먹기 / 끊기 / 잘라먹기 / 짤라내기 ("picking off / cutting off"):** 떨어진 적 1–2명을 다수로 제거, 또는 한타 중 그랩류로 먼저 잡기 ("several players killing 1–2 separated enemies, or catching someone first with a grab-type skill in a teamfight") — [나무위키 용어/은어](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%9A%A9%EC%96%B4/%EC%9D%80%EC%96%B4)
- **스플릿 푸시 / 사이드 ("split push / side lane"), 1-3-1, 날개 운영 ("wing play")** — [나무위키 용어](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%9A%A9%EC%96%B4)
- **바론 스틸 ("Baron steal")** used in Korean esports press — [inews24](https://www.inews24.com/view/1005412)
- T1's play style documented on 나무위키 (an example of 운영 discourse) — [나무위키, T1/리그 오브 레전드/플레이 스타일](https://namu.wiki/w/T1/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%ED%94%8C%EB%A0%88%EC%9D%B4%20%EC%8A%A4%ED%83%80%EC%9D%BC)
- Korean-English LoL term list — [bo3.gg (ko), LoL terms](https://bo3.gg/ko/articles/lol-terms-players-should-know) (not read)

### Inferences
Standard usage, **unsourced in this session**. Verify against 나무위키 before publishing.
- **운영 (macro / "operation"):** the overall management of the map and objectives, as opposed to 피지컬/한타 (mechanics/teamfights).
- **굴리기 ("rolling"):** turning a lead into more leads; synonymous with 스노우볼링 (snowballing).
- **역전각 ("comeback angle"):** a window or opportunity to reverse a losing game. Note: a search-tool summary guessed "an entry angle from the opposite side". That guess is **wrong** and should be ignored.
- **시즈 ("siege"):** sustained poke/pressure on a turret.
- **바론 콜 ("Baron call"):** the shotcall to start Baron.
- **시야 장악 ("vision control"):** controlling vision in an area (wards plus sweeping). Closest cited concept: zoning ([LoL Wiki Zoning](https://wiki.leagueoflegends.com/en-us/Zoning)).
- **English ↔ Korean mapping for the library** (inference):

| English | Korean |
|---|---|
| macro | 운영 |
| snowball | 스노우볼/굴리기 |
| pick/catch | 끊기 |
| comeback opportunity | 역전각 |
| siege | 시즈/공성 |
| split push | 스플릿/사이드 운영 |
| 1-3-1 | 1-3-1 |
| 1-4 | 1-4 스플릿 |
| Baron call | 바론 콜 |
| vision control | 시야 장악 |
| death timer | 데스 타이머/부활 시간 |
| objective bounty | 오브젝트 현상금 |
| shutdown | 현상금/셧다운 |
| super minions | 슈퍼 미니언 |
| inhibitor | 억제기 |
| plates | 포탑 방패 |

### Gaps
- No full-text 나무위키 page or LCK interview was read (namu.wiki fetch is blocked; only search summaries were available). No 인벤 tip articles surfaced. Terms 운영, 굴리기, 역전각, 시즈, 바론 콜 and 시야 장악 still need a citable Korean definition.
