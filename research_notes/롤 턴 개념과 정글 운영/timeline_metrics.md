# Measuring LoL tempo / "turn" concepts from Riot Match-V5 timeline data

Scope: which Match-V5 timeline fields exist (2025–2026), what proxies can stand in for recalls, lane priority, synced backs and objective setup, what earlier work exists, and what 1-minute sampling limits. Sources were partly restricted in this session. medium.com, sol.sbc.org.br, oracleselixir.com, mobalytics.gg and lol.fandom.com were blocked or returned 403, so several prior-work items are known only from search snippets and are flagged as such. Some findings are **empirical checks on this repo's own DuckDB** (`/home/user/LoLDosa/data/matches.duckdb`: 633 matches, 170,510 participant-frames, 258,284 events). Those are marked "[local data]".

## Q1. Which fields exist in the Match-V5 timeline?

### Takeaway
Every participantFrame includes `currentGold`, `totalGold`, `goldPerSecond`, `position`, `xp`, `level`, `minionsKilled`, `jungleMinionsKilled`, `timeEnemySpentControlled`, `championStats` and `damageStats`. Frames come once per `frameInterval` (60,000 ms), so the snapshot fields are sampled once a minute. Events carry millisecond `timestamp`s, and ITEM_PURCHASED / ITEM_SOLD / ITEM_UNDO / ITEM_DESTROYED are among the event types. Item events are the only fine-grained timing signal for shopping, which happens only in base. One catch: **the LoLDosa collector currently throws away item events and `currentGold`**, so recall detection needs a re-collection or a schema change.

### Cited Findings
- Community OpenAPI schema (`MingweiSamuel/riotapi-schema`, generated from Riot's API) defines `match-v5.InfoTimeLineDto` = {endOfGameResult, **frameInterval** (required), gameId, participants, **frames** (required)} — [riotapi-schema openapi-3.0.0.json](https://raw.githubusercontent.com/MingweiSamuel/riotapi-schema/gh-pages/openapi-3.0.0.json)
- `match-v5.FramesTimeLineDto` = {events, participantFrames, timestamp} — [same](https://raw.githubusercontent.com/MingweiSamuel/riotapi-schema/gh-pages/openapi-3.0.0.json)
- `match-v5.ParticipantFrameDto` (all fields required): championStats, **currentGold**, damageStats, **goldPerSecond**, jungleMinionsKilled, level, minionsKilled, participantId, **position**, timeEnemySpentControlled, totalGold, xp — [same](https://raw.githubusercontent.com/MingweiSamuel/riotapi-schema/gh-pages/openapi-3.0.0.json)
- `ChampionStatsDto` includes **health, healthMax**, power/powerMax (mana), movementSpeed, armor, MR, AD, AP, abilityHaste and others. `DamageStatsDto` holds cumulative damage done, damage to champions and damage taken, split by physical/magic/true — [same](https://raw.githubusercontent.com/MingweiSamuel/riotapi-schema/gh-pages/openapi-3.0.0.json)
- `match-v5.EventsTimeLineDto` (only `timestamp` and `type` are required) has these properties: timestamp, realTimestamp, type, itemId, participantId, levelUpType, skillSlot, creatorId, wardType, level, assistingParticipantIds, bounty, killStreakLength, killerId, position, victimDamageDealt, victimDamageReceived, victimId, killType, laneType, teamId, multiKillLength, killerTeamId, monsterType, monsterSubType, buildingType, towerType, afterId, beforeId, goldGain, gameId, winningTeam, transformType, name, shutdownBounty, actualStartTime, featType, featValue, victimTeamfightDamageDealt, victimTeamfightDamageReceived — [same](https://raw.githubusercontent.com/MingweiSamuel/riotapi-schema/gh-pages/openapi-3.0.0.json)
- Event types documented by Cassiopeia include CHAMPION_KILL, WARD_PLACED, WARD_KILL, BUILDING_KILL, ELITE_MONSTER_KILL, ITEM_PURCHASED, ITEM_SOLD, ITEM_DESTROYED, ITEM_UNDO and SKILL_LEVEL_UP, along with mode-specific types — [Cassiopeia match docs](https://cassiopeia.readthedocs.io/en/stable/cassiopeia/match.html)
- The Bayes Esports format docs give ITEM_SOLD / ITEM_UNDO examples and say `type` is the only field guaranteed in every event — [Bayes EMH format](https://docs.bayesesports.com/docs-data-portal/pro_match/emh_format)
- A Riot developer gist shows `currentGold` next to `totalGold` in each participant frame (example: 377 current against 8,777 total) — [RiotTuxedo gist](https://gist.github.com/RiotTuxedo/ab04ac027546f711ce820faed394295b) (seen in a search snippet only)
- A Riot developer-relations issue says Match-V5 participant position is only available every 60 seconds — [developer-relations #668](https://github.com/RiotGames/developer-relations/issues/668) (search snippet). Issue #603 (Feb 2022, closed Jan 2023) complained that the timeline endpoint had no official docs at all, with no Riot reply in the thread — [developer-relations #603](https://github.com/RiotGames/developer-relations/issues/603)
- [local data] Observed event types and counts in the LoLDosa DB: WARD_PLACED 144,061; WARD_KILL 34,999; CHAMPION_KILL 31,527; TURRET_PLATE_DESTROYED 30,587; BUILDING_KILL 6,451; ELITE_MONSTER_KILL 5,125; CHAMPION_SPECIAL_KILL 4,838; DRAGON_SOUL_GIVEN 696. These exist in live 2025–26 data, but this list is filtered by the collector's `KEEP_EVENTS`, so it is not the full set — `/home/user/LoLDosa/backend/src/loldosa/store/matches.py` lines 93–96
- [local data] The collector keeps only x, y, level, xp, totalGold, jungleMinionsKilled and minionsKilled per frame. It **drops currentGold, goldPerSecond, championStats (health) and damageStats**, and drops ITEM_*, LEVEL_UP, SKILL_LEVEL_UP and the other non-kept events — `/home/user/LoLDosa/backend/src/loldosa/store/matches.py` (~lines 288–310)
- [local data] Minute-0 frame positions give the fountain spawn coordinates. Blue averages about (411, 421) with x in 130–662. Red averages about (14,299, 14,397) with x in 14,055–14,589.

### Inferences
- The best recall signal is the ITEM_PURCHASED (and ITEM_UNDO/ITEM_SOLD) timestamps. Shopping is possible only in fountain, apart from rare exceptions such as particular champion or rune mechanics, so a cluster of purchase events gives a recall timestamp to the millisecond. The frame snapshots cannot do this.
- `championStats.health / healthMax` could separate "recalled because low HP" from "recalled to spend gold". Only the minute snapshot is available for it.
- To use any of this in LoLDosa, add ITEM_PURCHASED / ITEM_SOLD / ITEM_UNDO / ITEM_DESTROYED (with itemId and participantId) to `KEEP_EVENTS`, and store currentGold, goldPerSecond and health in `frames`.

### Gaps
- I could not read Riot's own match-v5 timeline docs page, which has historically been incomplete (see #603). The schema above is community-generated, but it is the standard reference used by the riotwatcher and Cassiopeia libraries.
- I could not confirm whether names like OBJECTIVE_BOUNTY_PRESTART / FEAT_UPDATE appear as event `type` values. The `featType`/`featValue` and `actualStartTime` properties in the schema suggest Feats-of-Strength and objective-bounty events exist, but that is unverified.

## Q2. How have analysts/academics detected recalls or "tempo" from timeline data?

### Takeaway
I found **no published, validated recall-detection method for Match-V5 timelines**: no paper, open-source project or analytics-site write-up surfaced. Public LoL analytics, including the win-prediction literature, uses minute-level aggregates such as gold/XP/CS diffs and objective counts, not back timings. Tempo and recall timing are discussed qualitatively in coaching guides. Pro data providers (Bayes/GRID) have higher-frequency feeds, but those are separate from Match-V5.

### Cited Findings
- Searches for timeline recall detection (fountain position, ITEM_PURCHASED, currentGold drop) returned only gameplay guides, with no data methods — e.g. [Mobalytics recall timers](https://mobalytics.gg/blog/lol-5-best-recall-timers/), [mid.gg recall timing](https://mid.gg/guides/recall-timing), [metabot.gg back timing](https://metabot.gg/en/league/guides/when-to-recall-back-timing-economy)
- Guide-level domain facts:
  - The recall channel is 8 seconds and breaks on damage or CC — [mid.gg](https://mid.gg/guides/recall-timing)
  - "Tempo is who gets to act first on the map, and recall timing decides it more often than kills do" — [mid.gg](https://mid.gg/guides/recall-timing)
  - Recall about 1 to 1.5 minutes before an objective. "Recalling later than 1 minute is not advised … you'll lose priority" — [Mobalytics](https://mobalytics.gg/blog/lol-5-best-recall-timers/), [statup.gg](https://statup.gg/post/perfect-recall-timing-in-league-of-legends)
  - Clear the wave just before the cannon wave, then recall — [statup.gg](https://statup.gg/post/perfect-recall-timing-in-league-of-legends)
- Academic minute-level work:
  - "From Outcome Prediction to Advantage Construction: A Temporal and Spatial Attribution Framework for League of Legends" (SBGames, Brazil) models a match as a causal minute-level sequence with spatial attribution and short-horizon forecasting. This is the closest academic work to spatiotemporal tempo analysis. Search snippet only; the host was blocked — [SBGames paper](https://sol.sbc.org.br/index.php/sbgames/article/view/45416)
  - "Win Prediction from the Snowball Effect Perspectives" (Korea Univ., GEM 2022) feeds 76 per-position in-game features into LSTM/GRU/RNN models and reports accuracy above 91% — [Korea Univ. pure](https://pure.korea.ac.kr/en/publications/win-prediction-from-the-snowball-effect-perspectives/)
  - "League of Legends: Real-Time Result Prediction" reports LightGBM at 81.62% average accuracy when 60–80% of game time has elapsed — [paperswithcode](https://cs.paperswithcode.com/paper/league-of-legends-real-time-result-prediction)
  - "Role-Sensitive Analysis of Positional Contributions and Win Prediction in MOBA Esports" (2025) reports XGB accuracy of 0.8686 and AUC of 0.9512 on 2024 data — [GNU scholarworks](https://scholarworks.gnu.ac.kr/item/1965e757-c3b8-4cd5-8f8e-c7bd13217ed0)
  - An IEEE DataPort dataset, "League of Legends Esports Player Game Data (2019–2024)", exists — [IEEE DataPort](https://ieee-dataport.org/node/14569)
- Pro data providers: Bayes Esports' EMH format is a separate, richer pro-match event format (it includes item sold/undo events) and is not Match-V5 — [Bayes EMH](https://docs.bayesesports.com/docs-data-portal/pro_match/emh_format)
- [local data] Across minutes 3–30, only **2.55%** of participant-frames (n=145,260) fall in a fountain box (x,y < 1200 or x,y > 13,600).

### Inferences
- The 2.55% figure supports the view that minute snapshots catch only a fraction of recalls. Rough estimate: about 15–25 s in base per recall (8 s channel plus shopping and healing) and a recall every 3–4 minutes would put a player in base about 7–12% of the time, so snapshots probably miss most recalls. This is my estimate, not a sourced figure.
- A practical recall detector, in order of signal quality, would combine:
  - (a) **ITEM_PURCHASED clusters**: purchases by one participant within about 10–20 s of each other count as one shop visit. Exclude the minute-0 to 1:30 starting buy, and exclude events without purchases such as consumables bought on a respawn after death.
  - (b) **Snapshot in fountain**: the frame position falls in the fountain box.
  - (c) **currentGold drop**: currentGold(t) < currentGold(t−1) + goldEarned(t−1→t), where goldEarned = Δ totalGold. Any drop means gold was spent, which requires being in base.
  - (d) **Death disambiguation**: purchases within the respawn window after a CHAMPION_KILL with victimId = player are a "death back", not a voluntary recall, and should be tagged separately.
  - (e) **Large position jump**: a jump between consecutive frames to near the fountain, then back out toward the lane.
- "Tempo" in the analytical sense (who acts first after a recall) could be measured as the **time from a recall (purchase cluster) to the next on-map action**: the first WARD_PLACED, CHAMPION_KILL or plate/objective event by that player or team. This is a derived proposal, not prior work.

### Gaps
- No Oracle's Elixir, Mobalytics GPI, op.gg, iTero or Riot-esports-analyst method for recall/tempo detection could be verified; their sites were blocked (403) in this session. Oracle's Elixir is known for minute-mark diff columns, e.g. gold/XP/CS diffs at 10/15 and turret plates, but I could not fetch its definitions page to confirm the exact column names.
- I found no open-source GitHub project that specifically infers recalls from Match-V5. A targeted GitHub code search for `ITEM_PURCHASED` together with "recall" or "back" was not run (tool budget) and is a reasonable next step.

## Q3. Proposed metrics for lane priority, synced backs and objective setup, and their limits under 1-minute sampling

### Takeaway
No standard public "lane priority" metric exists; it is defined qualitatively as being able to push first and move first. Usable proxies from Match-V5: lane CS diff and its first difference, XP/level diff, TURRET_PLATE_DESTROYED timestamps (exact), lane-opponent deaths and recalls (event-timed), and position depth past river from snapshots. Synced backs and objective setup can be computed reliably only from event timestamps (item purchases, kills, ELITE_MONSTER_KILL). Position-based presence near pits is a coarse 1-minute snapshot and badly undercounts.

### Cited Findings
- Lane priority definitions:
  - The ability to push a wave faster than the opponent, or a wave position that lets one player react to map events first. "Priority is essentially the position of your minion or creep wave within your lane" — [Dignitas lane priority guide](https://dignitas.gg/articles/the-pro-unspoken-rule-of-league-a-lane-priority-guide), [Jackarias analysis](https://jackariasanalysis.wordpress.com/2020/01/02/league-dota-lane-priority-2-365/), [agatasmurf](https://agatasmurf.com/prio-league-of-legends/)
  - Priority is converted into tempo and vision (roaming, invading, warding) — [Dignitas: Transitioning lane priority into tempo](https://dignitas.gg/articles/blogs/League-of-Legends/10280/transitioning-lane-priority-into-tempo-and-vision-control)
- A "Solo-Laner Index" uses regression on pro data and treats lane priority as one component of solo-lane performance, but gives no explicit formula. Search snippet; the host was blocked — [Medium: Solo-Laner Index](https://medium.com/swlh/creating-a-solo-laner-index-higher-order-statistics-league-of-legends-esports-faa2fac996f6)
- No standard public lane-priority metric from Riot or analytics sites turned up in an extended search (same sources as above).
- Objective setup guidance: recall about 60–90 s before an objective spawns so you can return, ward and hold priority — [Mobalytics](https://mobalytics.gg/blog/lol-5-best-recall-timers/), [metabot.gg objectives](https://metabot.gg/en/league/guides/objectives-dragon-baron-herald-grubs)
- Sampling limit: position is only every 60 s — [developer-relations #668](https://github.com/RiotGames/developer-relations/issues/668); `frameInterval` is a required timeline field — [riotapi-schema](https://raw.githubusercontent.com/MingweiSamuel/riotapi-schema/gh-pages/openapi-3.0.0.json)

### Inferences (proposed proxy definitions for LoLDosa)
These are design proposals derived from the fields above. None is a validated prior-work metric.

**Lane priority proxies, per lane, per minute t, laner vs. the opponent in the same `teamPosition`:**
- `ΔCS_lane(t)` = minionsKilled diff, plus its slope `ΔCS(t) − ΔCS(t−1)`. A positive and rising slope suggests the laner is clearing faster or the opponent is missing waves.
- `ΔXP(t)` and level-lead minutes, e.g. first to reach level 2/3/6 using LEVEL_UP event timestamps, which are exact to the ms. Not currently stored.
- **Plates**: TURRET_PLATE_DESTROYED (laneType plus killer or team) gives exact-time evidence of a push. Plates fall off at 14:00 in current patches; I did not re-verify this for 2026.
- **Depth**: project the frame position onto the lane axis and measure distance past river. Being past the river in your own lane at a snapshot loosely implies pushing. This is noisy because it is a single instant.
- **Opponent absence**: the lane opponent was dead (CHAMPION_KILL victim) or in base (recall detector) while the laner was alive in lane. That means the laner has "prio" by definition for that window, which is event-timed and therefore precise.
- Limits: at 1-min sampling you cannot see wave state (minion positions are not in the API at all), freezes or slow pushes. CS diff confounds farming skill with priority, and depth confounds pushing with getting zoned or roaming.

**Synced backs (jungler and laner):**
- Recall time = first ITEM_PURCHASED in a cluster, minus about 8–10 s for the channel and walk. Call the backs synced if |t_jg − t_laner| ≤ N s, with N = 20–30 s.
- Then measure what follows within about 60–90 s: a joint return (lane plus jungle), CHAMPION_KILL with an assist overlap, or plate/objective events.
- Limits: purchases can be delayed (standing in base) or absent (backing just to heal), which gives false negatives. Using frame-position or currentGold drops alone yields only a minute-level bucket ("same minute"), which is too coarse to call a back synced.

**Objective setup (dragon, grubs, herald, baron, atakhan):**
- Spawn times are fixed by game rules; the next spawn after a kill can be derived from ELITE_MONSTER_KILL timestamps plus the respawn timer.
- Two candidate features:
  - **Pre-objective recall**: the share of team members with a recall (purchase cluster) in the window [spawn − 90 s, spawn − 45 s].
  - **Presence**: the count of team members within R units (about 2,500–3,000) of the pit at the last frame before spawn.
- Then compare which team got the ELITE_MONSTER_KILL (killerTeamId) and any CHAMPION_KILLs near the pit position in the ±60 s window.
- Limits: the presence snapshot may be up to 59 s before spawn and misses rotations. WARD_PLACED events include a position (stored in local data as x,y), so **ward placements near the pit before spawn** are an event-timed and more reliable "setup" proxy than champion positions.

**Tempo/"turn" accounting:**
- Treat each recall or death as a team "turn spent" and each plate, objective, kill or invade (enemy jungle CS; the `enemyJungleMonsterKills` challenge is in match data but only as a whole-game total) as a "turn used".
- A team-level sequence of event-timed turns avoids most of the 1-min sampling problem, because it relies on event timestamps rather than frame snapshots.

### Gaps
- No ground-truth recall labels exist publicly to validate a purchase-cluster detector against. Spectator or replay (.rofl) parsing or the Live Client Data API (local game only) would be needed, and neither is available for historical Match-V5 games.
- Minion and wave positions are not exposed anywhere in Match-V5, so true wave state cannot be measured; only indirect proxies are possible.
- The exact current (2026 patch) objective spawn and respawn timers and the plate fall-off time were not re-verified in this session.
