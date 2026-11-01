# Phase-by-phase jungle game management (운영) playbook, Season 2026 (patch 26.x), for a Platinum–Diamond solo queue jungler

> **Method note (read first).** Today is 2026-11-01. In this session WebFetch was blocked for every domain I tried: leagueoflegends.com, dodge.gg, x.com, inven.co.kr, gamerstogether.cz, lol-coaching.net and boosteria.org all returned ENOTFOUND (outside the allowed network domains). Every finding below therefore comes from **WebSearch result summaries and snippets**, or from earlier research notes in this repo that were built the same way. I could not read any full page. Quoted text is what the search tool extracted. Verify every number against the Riot patch notes before publishing.
>
> **The brief's phase frame needs four corrections for 2026:**
> 1. **Atakhan is removed.** It does not exist in Season 2026, so the 14–20 phase has no Atakhan decision.
> 2. **Plates no longer fall off at 14:00.** They are permanent and also sit on inner and inhibitor turrets.
> 3. **Baron is back at 20:00.**
> 4. **Grubs spawn at 8:00 as one set**, not at 5:00 or 6:00.
>
> I found **no 2026 transcript-level coaching content** from Coach Curtis, Broken by Concept, Skill Capped or LS. Their names did not appear in any 2026 search result, so the coaching layer here comes from 2026-dated guide sites (Boosteria, mid.gg, Boosting Market, Boostroom, lol-coaching.net, dodge.gg, nerfplz) and Korean sources (나무위키, 인벤, FMKorea, ggmate, vortexgaming). Those guide sites are commercial and of mid-to-low authority.
>
> Related files: `research_notes/롤 핵심 개념 학습 자료/objectives_vision.md` (objective stats and rewards), `macro_midlate.md` (Baron calls, split push, inhibitors), and `research_notes/롤 턴 개념과 정글 운영/jungler_turn_sync.md` (backs, sync, 90/60/30 countdown). This file arranges that material by phase and adds new 2026 timing data.

## Q0. 2026 rules that every phase depends on (timer sheet)

### Takeaway
Season 2026 (26.1, Jan 2026) changed the map in several ways:
- Atakhan, Blood Roses and Feats of Strength are gone.
- Baron moved back to 20:00.
- Plates became permanent, and turrets crystallize over time (Crystalline Overgrowth).
- Epic monsters got tankier.
- Minions and camps spawn earlier: minions at 0:30, camps at 0:55. Older pages say 3:30 for first Scuttle; 26.1-era guides say 2:55, which is unresolved.

Grubs (8:00) → Herald (15:00–19:45) → Baron (20:00) is the top-side sequence. Dragons at 5:00 with 5:00 respawns are the bot-side clock.

### Cited Findings
**Removed systems and the reasons**
- Atakhan "has been removed from the game and will no longer spawn". Blood Roses and Feats of Strength were also removed. Riot framed this as easing the objective load on junglers. — [Riot Patch 26.1 Notes](https://www.leagueoflegends.com/en-gb/news/game-updates/patch-26-1-notes/); [Sportskeeda 26.1](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes)
- Korean press gave Riot's reason as: Atakhan had entrenched a fight-centred '우르르 메타' ("everyone-rushes-in meta"), so Riot removed 아타칸·무력행사 and moved minion spawn time and cadence earlier. LCK players said "라인전도 빨리 시작하고, 바론도 20분에 나오기 때문에 템포가 좀 빨라졌다" ("laning starts earlier and Baron comes at 20, so the tempo got a bit faster"), and that Baron matters more now. — [Daum/News, '아타칸 삭제' 2026 LCK컵 개막](https://v.daum.net/v/20260114130516662); [인벤 LCK컵 미디어데이 2026 패치 키워드](https://www.inven.co.kr/webzine/news/?news=312571&site=lol)

**Early spawn timers**
- Minions spawn at **0:30**. Wolves, Blue, Red and Raptors spawn at **0:55**; Gromp and Krugs at **1:07**. — search summary of [lol-coaching.net pathing guide](https://lol-coaching.net/blog/how-to-path-as-a-jungler-in-league-of-legends) / [Boostroom pathing 2026](https://boostroom.com/blog/ungle-pathing-explained-clear-routes-timings-and-first-ganks) / [leagueoflegendsgames.com Jungle 2026](https://leagueoflegendsgames.com/jungle/)
- 나무위키 independently says camps spawn 35 s earlier than before in 2026 (정글몹이 기존보다 35초 빨리 생성) and epic monster durability increased. 1:30 − 0:35 = 0:55, which is consistent. — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C))
- **Scuttle conflict:** 26.1-era guides say first Scuttle spawns at **2:55** and attribute that to Riot's 26.1 notes ([lol-coaching.net / Boostroom search summary](https://lol-coaching.net/blog/how-to-play-jungle-in-league-of-legends)). The earlier repo note (`jungler_turn_sync.md` §4) cited 3:30 ([League Coach Merch 2026](https://www.leaguecoachmerch.com/best-jungle-clear-path-2026/)). A 35 s shift (3:30 → 2:55) matches the camp shift, so **2:55 is more likely current**. It is still unverified on the Riot page.

**Grubs, Herald, Baron**
- Grubs: one group of three at **8:00**, no respawn (since 25.09). Untaken grubs "leave for good at 14:45". — [nerfplz Voidgrubs/Herald guide](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html) (URL dated 2026/11, so treat with caution); [nerfplz Season 16 objectives](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html)
- Herald: **15:00**, despawns **19:45**. Baron: **20:00**, respawns 6:00 after each kill. — [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html); [Sportskeeda 26.1](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes)

**Dragons**
- First spawn 5:00, respawn 5:00. Soul goes to the first team to four. Elder spawns 6:00 after soul and respawns every 6:00.
- 26.1: drakes have up to +35% effective HP (more for the team approaching soul), and Dragon Vengeance is 15/30/45%. — [objectives_vision.md citing Riot 26.1](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-26-1-notes/); [인벤 2026 시즌 기획 (드래곤 스택 피해 감소율 7%→15%)](https://www.inven.co.kr/webzine/news/?news=311766&site=lol)

**Turrets**
- Plates are **permanent**, no longer fall at 14:00, and exist on all non-Nexus turrets. This rewards "smaller incremental pushes". — [esports.gg lane & turret changes 2026](https://esports.gg/news/league-of-legends/lane-turret-changes-lol-2026/); [altchar: turrets reworked to reward pushing and split-pushing](https://www.altchar.com/game-news/league-of-legends-2026-is-reworking-turrets-to-reward-pushing-and-split-pushing-afxfK7o4YZ0U); [esports-news.co.uk 26.1](https://esports-news.co.uk/2026/01/07/league-of-legends-patch-26-1-kicks-off-the-new-year-with-huge-changes/)
- **Crystalline Overgrowth** (wiki and guides):
  - Crystals start growing on a turret 90 s after its activation ("1:40 game time"). Growth is deferred while enemies are nearby, and it does not activate under backdoor protection.
  - The next enemy champion to attack the turret consumes it for bonus true damage. The damage stays at minimum for 60 s, scales linearly for 240 s, then holds at maximum.
  - — [LoL Wiki Turrets (search summary)](https://wiki.leagueoflegends.com/en-us/Turrets); [games.gg Crystalline Overgrowth explained (DE)](https://games.gg/de/league-of-legends/guides/league-of-legends-crystalline-overgrowth-erklärt/)
- Outer turret decay: outer turrets lose 10 armor and 15 MR per minute from 11:00 to 15:00, capped at −40/−60. This is a resist decay, not a gold change. — [LoL Wiki Turrets / Fortification (search summary)](https://wiki.leagueoflegends.com/en-us/Fortification). *Unverified on the Riot page.*
- First turret gives 300 g again. Plate resists were changed in 26.3 (20–100 → 30–50 per plate). — [objectives_vision.md citing thegamehaus 26.1 and dtgre 26.3](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html)

**Jungle and Smite**
- Junglers take half damage from non-epic monsters. Jungle quest needs 35 stacks (was 40). Smite damage is 600/1000/1400. — [esports.gg 26.1 notes](https://esports.gg/guides/league-of-legends/lol-patch-notes-26-1/); [Strafe 26.01 rundown](https://www.strafe.com/news/read/lo-l-patch-26-01-rundown-of-the-biggest-changes-in-season-16/)
- **Inven:** the 2026 design lowers the jungler's early intervention power but strengthens their role as the "설계자" (designer) of mid–late objective fights. Epic monster HP +15%. — [인벤 2026 시즌 기획](https://www.inven.co.kr/webzine/news/?news=311766&site=lol) (search summary)

**Grub rewards**
- Grub gold cut from 210 to 90 total, and XP from 80 to 65 per grub. — [vortexgaming 2026 시즌1 정글 분석](https://vortexgaming.io/postdetail/635801). The post's date is unclear, so check it.

### Inferences
- With camps at 0:55 and a full clear taking ~2:00–2:15, a full clear ends about **2:50–3:10**. That is right at the (probable) 2:55 Scuttle spawn, so "full clear → Scuttle" is the natural default route in 2026.
- Turrets get weaker and more crystallized over time, and plates never disappear. Pressure on a turret therefore never "expires" at 14:00 the way it used to, and repeated small pushes (Herald, side waves) keep paying off.

### Gaps
- Exact 26.1 Scuttle time (2:55 vs 3:30) is not confirmed against the Riot page, which was blocked.
- I did not confirm whether the post-14:00 wave cadence still changes in 2026. The earlier note says 25 s after 14:00.

---

## Q1. Pre-3:00 (level 1–3, first clear, Scuttle): what to do

### Takeaway
- **Default:** full clear (6 camps) ending around 2:50–3:10, then Scuttle or a gank on the side that has priority.
- **Alternative:** a 3-camp clear into a gank, only when a lane state clearly offers a kill.
- A Season 16 pro tip: don't start Raptors. If the enemy started Raptors, skip Scuttle and recall immediately so you can meet them on their second clear.
- **Plan the clear backward from what you want at 5:00 (Dragon) and 8:00 (Grubs).** Choose the start side so the clear ends on the side of the objective you want.

### Cited Findings
**Clear timing and choice**
- A fast full clear finishes around "2:50 to 3:10", with slower clears near 3:20. Another guide: "full clear runs from 0:55 to about 3:00, with the Scuttle decision at 2:55". — search summary of [lol-coaching.net](https://lol-coaching.net/blog/how-to-path-as-a-jungler-in-league-of-legends) / [Boostroom pathing 2026](https://boostroom.com/blog/ungle-pathing-explained-clear-routes-timings-and-first-ganks) / [Boosting Market pathing](https://boostingmarket.com/blogs/lol-jungle-pathing-guide/)
- Griffin (account GriffinHQ_ on X, ~March 2026, Season 16):
  - "Dont ever start raptors (maybe <5% of games its good...)".
  - "If enemy starts raptors dont go for scuttle after full clear, just instantly recall buy items and meet them at their raptors at 3:20-…" (the snippet is truncated).
  - — [Griffin on X](https://x.com/GriffinHQ_/status/2028991766662398097) (search snippet only; I could not verify who the author is)
- First back: back after a full clear plus Scuttle, or after three camps into a gank/Scuttle, once you can afford ~500–1,000 g (component, control ward). A full clear plus Scuttle puts you at level 4 around 3:30–4:00. — [Buyboosting](https://buyboosting.com/blog/jungle-pathing-and-clear-routes-league-of-legends/); [Boosting Market recall timing](https://boostingmarket.com/blogs/lol-recall-timing-guide/) (via `jungler_turn_sync.md` §4; these timings predate the 35 s shift, so subtract ~0:35)
- Korean pre-back order when not full-clearing: "'이득보기 > 아군 정글몹 사냥 > 귀환' 이 순으로 짜는 것이 좋음" ("plan it as: take a gain → farm your own camps → recall"). — [DCinside 정글학개론 (2019–20, older)](https://gall.dcinside.com/board/view/?id=leagueoflegends3&no=7330222)

**Lane states and role quests**
- 26.1 role quests reward staying in lane, so lane swaps are fewer and laning "matters more". Gank targets are therefore stable lane matchups. — [인벤 LCK컵 미디어데이](https://www.inven.co.kr/webzine/news/?news=312571&site=lol)
- Inven says junglers' early intervention power was deliberately lowered in 2026. — [인벤 2026 시즌 기획](https://www.inven.co.kr/webzine/news/?news=311766&site=lol)

### Inferences (checklist)
- **0:00–0:55:** set the plan. Which lane has priority at level 2–3? Which objective do you want at 5:00 or 8:00? End your clear on that side.
- **~2:50–3:10:** finish the clear. If a lane crashed with priority on the Scuttle side, take Scuttle (2:55?). If the enemy jungler is shown on the other side, take your Scuttle uncontested or gank there.
- **By ~3:30–4:00:** recall with ~500+ g, unless a gank or Scuttle play is live. Avoid stacking a Scuttle fight when your laners lack priority.

### Gaps
- I found no 2026 high-elo coach source with a full-clear vs 3-camp win-rate argument.
- Griffin's post is a single source, and the full text could not be retrieved.

---

## Q2. 3:00–8:00 (first Dragon at 5:00, Grubs setup for 8:00, first recall, tempo)

### Takeaway
The first Dragon at 5:00 lines up with your second full-clear timer, which is why 2026 guides call it the "natural" first objective. A Season 16 view rates the first Dragon above Grubs, because crystallized turrets cut grub value. Other guides recommend trading: take Grubs while the enemy takes Dragon, then contest the next Dragon.

For the 8:00 Grubs, the side with top/mid priority, ideally won by an earlier gank, should arrive first. Korean analysis says the 8:00 grub fight shapes the 10-minute first-item timing.

### Cited Findings
**Dragon vs Grubs**
- Griffin: "first Dragon is almost always more valuable than grubs this season", because with crystalized turrets "grubs lose a lot of the value they had". Grubs "are still good for exp so it is ok to take one grub for the exp then leave the rest". "First dragon is timed perfectly with 2nd full clear timer". An early dragon can threaten soul around 20 minutes with priority. — [Griffin on X](https://x.com/GriffinHQ_/status/2028991766662398097) (search summary)
- Contrary view from a 2026 jungle guide: "taking two or three grubs before contesting the second Dragon is often the correct play". It recommends trading, taking Grubs while the enemy takes Dragon and then contesting the next Dragon. — [dodge.gg Jungle Guide 2026](https://www.dodge.gg/en-US/lol/news/jungle-guide-2026) (search summary; ~7 months old)
- 나무위키: whether you take grubs/Herald or stack early drakes "아군 전체의 파워커브를 보고 결정" (is decided by your whole team's power curve). If behind, "유충/용이 동시에 등장한 타이밍에 1용 or 3유충 정도만 먹고 잘 버틴다" (when grubs and drake are both up, take just one drake or the three grubs and hold on). — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C))
- Korean beginner guide (2026): don't force the first Dragon ("첫 드래곤은 무리하지 않는다"), never concede the soul-point fourth Dragon, and take vision around the pit first. — [ggmate 롤 정글 입문 가이드 2026](https://ggmate.gg/blog/lol-guide-jungle)

**Grubs setup and value**
- FMKorea analysis: the result of the grub fight strongly affects the 10-minute first-item timing ("교전 결과가 10분 1코어 타이밍에 영향을 크게 줌"). It advises securing lane priority through ganks ("갱킹을 통해 라인 주도권을 확보") so your side arrives at the 8:00 setup first. It also says top-side river vision matters more than the C-bush ("C자 부시보단 탑쪽 사이드 시야가 더 중요함"). — [FMKorea 유충 생성 시간 변화에 따른 메타 변화 해설](https://www.fmkorea.com/8437440299) (written around an earlier grub-timer patch; principle only)
- Grubs' value is turret damage, not gold. Taking the third grub denies Hunger of the Void to the enemy. Soloing grubs goes badly because they spawn voidmites that Smite cannot target. — [nerfplz Voidgrubs/Herald](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html)
- Skipped grubs are gone for good, while a skipped Dragon gets replaced. — [nerfplz Voidgrubs/Herald](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html) (search summary)

**Recall and sync**
- Back before every Dragon spawn, not during it. The classic failure is clearing a full side and recalling *as* Dragon spawns. Ping recall timing so laners can match, and recall after the wave crashes. — [mid.gg recall timing](https://mid.gg/guides/recall-timing) (via `jungler_turn_sync.md` §3)
- After the enemy jungler ganks bot, the opposite side gets "roughly 20 to 30 seconds of tempo". — [Boosting Market tracking](https://boostingmarket.com/blogs/lol-jungle-tracking-guide/)

### Inferences (checklist)
- **~3:30–4:00:** first back, with a control ward.
- **~4:00–4:30:** clear the bot-side camps toward the pit. Bot and support crash, then ward the pit and river (see Q4).
- **5:00:** Dragon if bot/mid have priority. Otherwise trade: take top-side camps, crab, or plates on the opposite side.
- **~6:30–7:00:** recall again if you have gold. Ask top and mid to crash.
- **7:30:** ward top river and the grub pit.
- **8:00:** Grubs with top/mid priority. Without priority, take one grub for XP and leave (Griffin), or trade for the second Dragon (~10:00 if the first fell at 5:00).
- **The 2026 rule for Dragon vs Grubs:**
  - Dragon when you can only get one cleanly. The pro view: the soul race starts early, and grubs are worth less against crystallized turrets.
  - Grubs instead when the team has top-side lane strength and Dragon is not contestable.

### Gaps
- No Oracle's Elixir or LCK 2026 statistic on first-Dragon vs Grubs win rates was found.

---

## Q3. 8:00–14:00 (second Dragon, Grubs window, first tower; plates no longer fall)

### Takeaway
- **Bot side:** second Dragon around 10:00 (5:00 respawn) and, if both are taken, a third around 15:00.
- **Top side:** Grubs if not taken by 14:45.
- **Turrets:** first-turret gold (300 g) and permanent plates. Outer turrets lose resists 11:00–15:00, so first towers fall more easily in this window.
- **No 14:00 plate deadline.** The urgency to cash in early pressure shifts to "Grubs despawn at 14:45, Herald arrives at 15:00".

### Cited Findings
- Grubs window is "roughly 8:00 to 14:45", and Herald arrives at 15:00. — [nerfplz Voidgrubs/Herald](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html)
- Outer turret decay 11:00–15:00 (−10 armor / −15 MR per minute, capped at −40/−60). — [LoL Wiki Turrets / Fortification](https://wiki.leagueoflegends.com/en-us/Fortification) (search summary)
- Plates are permanent, which rewards "partial success when sieging and encourag[es] smaller incremental pushes". — [esports.gg lane & turret changes 2026](https://esports.gg/news/league-of-legends/lane-turret-changes-lol-2026/)
- Trade Grubs and Dragon rather than coin-flip. If priority isn't there, trade or skip. — [Boosteria objective priorities](https://boosteria.org/guides/comprehensive-guide-objective-management-in-league) (via `jungler_turn_sync.md` §2); [dodge.gg 2026](https://www.dodge.gg/en-US/lol/news/jungle-guide-2026)
- 26.1 tankier drakes and higher Dragon Vengeance (15/30/45%) make contesting a team that is ahead in drakes harder, so the drake count matters more for the team ahead. — [Riot 26.1 via objectives_vision.md](https://www.leagueoflegends.com/en-sg/news/game-updates/patch-26-1-notes/)

### Inferences (checklist)
- **~9:00–9:30:** reset if you have ~1,000+ g before the ~10:00 Dragon. The 90/60/30 countdown applies (Q4).
- **After grubs:** go bot or mid with the team to use Hunger of the Void on a turret. With permanent plates, every hit adds up.
- **~12:00–14:00:** watch Grubs despawn (14:45) and Herald (15:00). Avoid starting a third Dragon fight (~15:00) out of position. Know which side you'll be on at 15:00.

### Gaps
- No 2026 source gave per-plate gold for inner turrets or the post-14:00 lane-swap and tower-trade conventions.

---

## Q4. Vision setup before objectives (timing in seconds, ward types, sweeping)

### Takeaway
The converged countdown:
- **~90 s:** reset and spend gold.
- **~60 s:** Control Ward in or next to the pit, and lanes start shoving.
- **~45 s:** deep ward on the enemy approach.
- **~30 s:** river-entrance ward and sweep.

Faelights are 2026 mushroom rings that turn any ward placed on them into a superward. They add strong pre-objective spots near the river entrances, but a Control Ward in the pit is still usually better for denying vision.

### Cited Findings
- mid.gg sequence: Control Ward in the pit at 60 s before spawn, a deep ward on the enemy approach at 45 s, and a river-entrance ward at 30 s. Baron is set up the same way, mirrored. — [mid.gg warding guide](https://mid.gg/guides/warding) (search summary)
- Boosting Market: Control Ward in the pit 60–90 s before Baron. — [Boosting Market vision score](https://boostingmarket.com/blogs/lol-vision-score-guide/) (search summary)
- Boosteria: "One minute before it matters, do the setup checklist: reset, clear toward, vision, lane priority." Its 90/60/30 plan: "Reset if you need to spend gold; you can't fight dragon with half-bought items." — [Boosteria pathing basics](https://boosteria.org/guides/lol-jungle-pathing-basics-tempo-tracking-gank-windows); [Boosteria objective priorities](https://boosteria.org/guides/comprehensive-guide-objective-management-in-league)
- Faelights:
  - "When you place any ward on a Faelight ring, it becomes a superward".
  - Guides count about 12 spots and cite a ~45 s bonus-reveal window. The spots near jungle–river entrances are the useful ones.
  - A pit Control Ward tends to beat a Faelight ward for denial.
  - Counts and spots differ between guides.
  - — [games.gg Season 2026](https://games.gg/league-of-legends/guides/league-of-legends-season-2026-everything-new-demacia/); [guides-factory warding 2026](https://guides-factory.com/guides/lol-warding-guide); [gameboost Faelights](https://gameboost.com/blog/league-of-legends-faelights); [loltheory warding 2026](https://blog.loltheory.gg/warding-guide-lol/) (search summaries)
- 26.3: "the River Pixel Brush reveal region cuts off before scuttle pad and epic pit entrance". — [u.gg 26.3](https://u.gg/lol/news/patch-26-3-notes-league-of-legends) (via objectives_vision.md)
- Common mistakes: burning Smite charges ~45 s before Dragon, recalling as the objective spawns, and dying with 1,200+ unspent gold. — [Boosteria](https://boosteria.org/guides/lol-jungle-pathing-basics-tempo-tracking-gank-windows), [mid.gg](https://mid.gg/guides/recall-timing), [Disciplined Jungler](https://disciplinedjungler.com/guides/jungle-tempo/) (via jungler_turn_sync §7)
- Korean: take the vision around the pit first ("드래곤 둥지 주변 시야를 먼저"). Prefer top-side river vision for grubs. — [ggmate 2026](https://ggmate.gg/blog/lol-guide-jungle); [FMKorea](https://www.fmkorea.com/8437440299)

### Inferences
- Stealth Ward cap is 3 per player, so the jungler should save a Control Ward and one trinket charge for the 60 s and 30 s steps. Supports should sweep (Oracle) the pit about 30 s out.
- The team that set vision first holds the 선턴 (first turn) on the objective. See the term list below.

### Gaps
- The Faelight Korean client name was not verified ("요정등불" is a guess from the earlier notes). Exact Faelight locations conflict between guides.

---

## Q5. 14:00–20:00 mid game (Herald 15:00, third Dragon, side lanes, vision; no Atakhan)

### Takeaway
This phase is now Herald (15:00–19:45) plus the third Dragon (~15:00), heading into a 20:00 Baron.

- **Herald is a turret-taking tool.** If you can't convert it into at least one structure before Baron spawns, the five minutes of map presence were wasted.
- **Side lanes become more valuable** because permanent plates and Crystalline Overgrowth let small pushes stack up.
- **Basic 1-3-1 / 1-4 rules still apply:** the side laner must survive 1v1 and push fast, and the team must be able to fight 4v4 or 4v5.

### Cited Findings
- Herald: "if you can't convert her into at least one structure before Baron spawns at twenty, you've spent five minutes of map presence for a buff that expired". — [nerfplz Voidgrubs/Herald](https://www.nerfplz.com/2026/11/voidgrubs-and-rift-herald-explained-10.html) / [nerfplz S16](https://www.nerfplz.com/2026/08/every-summoners-rift-objective.html) (search summary; attribution between the two pages unclear)
- 26.1 cut Herald's rewards (240 XP), and 26.12 adjusted Herald. — [riftpatchnotes Herald](https://www.riftpatchnotes.com/lol/system/rift-herald) (via objectives_vision.md)
- 2026 turret changes reward pushing and split-pushing. Side-lane pressure "becomes more valuable because small progress stacks up". — [altchar](https://www.altchar.com/game-news/league-of-legends-2026-is-reworking-turrets-to-reward-pushing-and-split-pushing-afxfK7o4YZ0U); [GameRiv turret changes 2026](https://gameriv.com/new-turret-changes-coming-to-league-of-legends-in-2026/)
- 26.3 plate resists went from 20–100 to 30–50 per plate. Commentators read this as making solo pushes harder and group pushes easier, which pulls the other way from the 26.1 split-push incentive. — [dtgre 26.3](https://www.dtgre.com/2026/02/lol-patch-26-3-bounty-turret-plate-guide.html)
- OP.GG lane macro guide: after the first turret falls, a jungler who is strong 1v1 can roam alone while the laners make a 1-3-1. This is a pre-2026 general guide. — [OP.GG Lane-Specific Macro Play](https://talk.op.gg/s/lol/user-news/752718/Lane-Specific%20Macro%20Play%20(Standard%20Guide)?tl=en)
- Split-push preconditions: "your team can fight 4v5 or 4v4 ... and you can push waves quickly". Counter: "fight the enemy when they're split up". — [Mobalytics split push](https://mobalytics.gg/lol/guides/how-to-split-push) (updated Oct 2025; principles unchanged)
- 나무위키:
  - 스플릿 푸시 is hard to use when "한 명이라도 자리를 비우면 한타에서 대패" (one absence loses the teamfight).
  - 1-3-1 = 탑1·미드3·봇1.
  - 날개 운영 = pushing all three lanes from mid game on.
  - — [나무위키 용어](https://namu.wiki/w/%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C/%EC%9A%A9%EC%96%B4)
- Swiftplay rules differ: no grubs or Herald, two drakes for soul. Treat any "Herald removed" or "two drakes = soul" line as Swiftplay, not Ranked. — [BoostPirate Swiftplay 2026](https://boostpirate.com/guides/lol-swiftplay-explained); objectives_vision.md

### Inferences (checklist)
- **~14:00:** if Grubs are up and uncontested, finish them before 14:45. Otherwise reset by ~14:00–14:15 for the 15:00 Herald or third Dragon. Pick one, and take the other side's camps or a tower as the trade.
- **Herald:** use it immediately on a mid or side outer turret. Mid opens the map for Baron vision. Don't hold it past ~19:00.
- **Side-lane assignment (사이드 배치):** the best duelist or split-pusher takes the side lane where the next objective is not. The jungler plays on the objective side with the mid and support group, warding the next objective's river 60–90 s early.
- **~18:30:** begin Baron vision (Q6). Inhibitor-side turrets are now plated too, so every siege leaves damage.

### Gaps
- No 2026 Korean pro-coach transcript on 사이드 운영 was found.
- No LCK 2026 analytics on Herald usage rate were found.

---

## Q6. 20:00+ (Baron, soul, Elder, closing, resets)

### Takeaway
- **Baron (20:00, respawns 6:00 after each kill):** start it on a numbers advantage after a pick or won fight, or when the enemy is committed elsewhere. Clear vision first.
- **Hand of Baron** is a ~3-minute siege window. Use it to take structures with waves, not to chase kills.
- **Close games around 20–25 minutes, when your spike peaks:** take Baron or Elder, regroup, then push an inhibitor.
- **Reset on time for item spikes** rather than overstaying for one more wave.
- **Soul vs Baron:** compare how close each team is to soul, who arrives first, and whether Baron can reach a turret before the buff expires.
- **Elder** spawns 6:00 after soul. It is the final forcing tool, so treat its timer as a fight timer.

### Cited Findings
- Baron spawns at 20:00 and respawns 6 minutes after every death. — [nerfplz Baron guide 2026](https://www.nerfplz.com/2026/10/baron-nashor-guide-spawn-timers-three.html)
- Each game rolls one of three Baron forms that alter the pit terrain (from 25.S1, still in 2026). — [nerfplz Baron guide](https://www.nerfplz.com/2026/10/baron-nashor-guide-spawn-timers-three.html)
- Closing guides (2026):
  - Best window to end is 20–25 min at peak spike.
  - The sequence is Baron or Elder → regroup → inhibitor.
  - Reset on time for item spikes rather than overstay.
  - Clear vision around Baron, start or posture to start it, and take it after a fight.
  - — [Boosteria close games 2026](https://boosteria.org/guides/close-games-lol-2026-convert-leads-faster); [Boostroom close out games 2026](https://boostroom.com/blog/how-to-close-out-games-turning-a-lead-into-a-clean-win); [Boosting Market close out](https://boostingmarket.com/blogs/lol-how-to-close-out-games/); [Boosting Market objective decision tree](https://boostingmarket.com/blogs/lol-objective-priority-guide/) (search summaries)
- Soul vs Baron: compare soul proximity, who arrives first, and whether Baron can reach a turret before the buff expires. — [Boosting Market objective priority](https://boostingmarket.com/blogs/lol-objective-priority-guide/) (search summary)
- Baron call rule: start "after a pick, a lost teamfight on the enemy side..." or when "you cannot lose even if they all-in'd you at Baron". Never recall while the team is dancing around Baron or Elder. — [Mobalytics Baron tips](https://mobalytics.gg/lol/guides/5-tips-to-secure-the-baron-safely); [Mobafire Q&A](https://www.mobafire.com/league-of-legends/question/quot-calling-quot-baron-233) (via macro_midlate.md)
- Hand of Baron lasts 180 s (since V9.23), with no 26.x duration change found. 26.1 cut Baron's gold ("Elder-like treatment"). — [LoL Wiki Hand of Baron](https://wiki.leagueoflegends.com/en-us/Hand_of_Baron); [Sportskeeda 26.1](https://www.sportskeeda.com/esports/league-legends-patch-26-1-notes)
- Elder:
  - Spawns 6:00 after soul and respawns 6:00. 26.1 gave it ~20% more effective HP.
  - Its buff executes below 20% max HP and lasts 150 s.
  - "Elder plus a soul is the standard way a team closes ... treat the Elder timer as a fight timer and get vision down long before it lands." — [nerfplz Dragons 2026](https://www.nerfplz.com/2026/10/lol-dragons-explained-10-things-pit.html)
  - Wiki pages: [LoL Wiki Elder Dragon](https://wiki.leagueoflegends.com/en-us/Elder_Dragon) (via objectives_vision.md)
- Inhibitors respawn after 5:00, and a downed inhibitor adds super minions to that lane. — [LoL Wiki Inhibitors](https://wiki.leagueoflegends.com/en-us/Inhibitors)
- LCK players in Jan 2026 said Baron's importance went up with the 20:00 spawn. — [인벤 LCK컵 미디어데이](https://www.inven.co.kr/webzine/news/?news=312571&site=lol)
- Griffin: with priority, an early first Dragon "can threaten Dragon Soul around 20 minutes". The 20:00 Baron and the first soul point can therefore land together. — [Griffin on X](https://x.com/GriffinHQ_/status/2028991766662398097)
- **Conflict:** guides disagree on the Baron buff numbers (time-scaling vs a fixed 3-minute window). — [search summary across Boosteria/Boosting Market](https://boostingmarket.com/blogs/lol-objective-priority-guide/)

### Inferences (checklist)
- **~18:30–19:00:** reset and buy. A Control Ward goes in the Baron pit or brush by ~19:00 (60–90 s rule), and the mid and side waves get shoved.
- **20:00:** don't face-check. Start Baron only with a numbers advantage or the enemy committed on the far side (bot Dragon, soul fight).
- **After Baron:** half-time recall, buy, then push two lanes with Baron-empowered waves. Hit a plated inner or inhibitor turret, then reset before the buff ends. Don't dive Nexus turrets 4v5.
- **Soul point:** if the enemy is at soul point and Dragon spawns within ~60 s of Baron, prioritize denying soul unless Baron can be done before they arrive. At 3 drakes yourself, Dragon Vengeance makes your soul fight easier.
- **Elder:** start vision 90 s early and treat it as the deciding fight. Don't start it while the enemy's Smite can enter freely.

### Gaps
- No 2026 LCK statistic on Baron-to-win conversion, and no average Baron time post-change.
- Baron buff numbers conflict between sources.

---

## Q7. Tempo / turn concepts and Korean community terms, mapped to phase decisions

### Takeaway
Korean 운영 talk is built on **턴 (turn)**: which team can move first. That depends on **라인 주도권 / 라인 프리오 (lane priority)**, **선턴 / 후턴 (first vs second turn)**, and **템포 (tempo)**, meaning arriving on time with items. The 2026 phase decisions reduce to two rules:
1. Win the turn before each spawn by crashing lanes and resetting 60–90 s early.
2. If you lack the turn, **교환 (trade)** for an objective on the opposite side instead of contesting.

### Cited Findings
- Prior Korean research: taking the 유충 or 전령 initiative and then grabbing the **선턴** to lock vision is the emphasized flow. — `research_notes/롤 턴 개념과 정글 운영/korean_turn_concept.md` (sources therein)
- After an enemy gank on one side, the other side gets about 20–30 s of tempo for a play. — [Boosting Market tracking](https://boostingmarket.com/blogs/lol-jungle-tracking-guide/)
- "A crash you do nothing with is wasted." — [mid.gg wave management](https://mid.gg/guides/wave-management) (via jungler_turn_sync)
- Korean: a laner who needs to back may "한 타이밍 먼저 귀환을 하고 라인을 정글러에게 먹이기도 한다" (recall one timing early and let the jungler eat the wave). — [나무위키 정글](https://namu.wiki/w/%EC%A0%95%EA%B8%80(%EB%A6%AC%EA%B7%B8%20%EC%98%A4%EB%B8%8C%20%EB%A0%88%EC%A0%84%EB%93%9C))

**Korean terms list (sources above unless noted)**
- 운영 = macro.
- 턴 / 선턴 / 후턴.
- 라인 주도권 / 프리오 / 라인 프리.
- 템포.
- 교환 / 맞교환 = trading objectives.
- 크로스맵 = cross-map.
- 사이드 운영 / 스플릿 푸시 / 1-3-1 / 1-4 / 날개 운영.
- 시야 장악 / 시야 작업 = vision control.
- 스위핑 = sweeping, or 렌즈 (the red-trinket name).
- 제어 와드 = control ward.
- 한타 = teamfight.
- 끊기 / 끊어먹기 = picks.
- 굴리기 / 스노우볼.
- 정비 / 리셋 = reset.
- 귀환 타이밍 = recall timing.
- 풀캠 / 3캠 = full clear / 3-camp.
- 바위게 (Scuttle).
- 유충 (Grubs).
- 전령 / 전령의 눈.
- 용 / 드래곤.
- 영혼 / 영혼 포인트 (soul point).
- 장로 (Elder).
- 바론 / 바론 버프 / 바론 스틸.
- 포탑 방패 / 플레이트 (plates).
- 1코어 / 2코어 (first and second item).
- 우르르 메타 (the 2025 Atakhan-era group-up meta). — [Daum](https://v.daum.net/v/20260114130516662)
- 설계자 (the jungler as objective "designer"). — [인벤](https://www.inven.co.kr/webzine/news/?news=311766&site=lol)

### Inferences: one-line phase rules for solo queue
- **Pre-3:00:** full clear toward the side whose lanes have priority. Take Scuttle at ~2:55 only with lane priority.
- **3:00–8:00:**
  - Back by ~3:30–4:00.
  - Bot priority → 5:00 Dragon. No priority → trade on the opposite side.
  - Top/mid priority → 8:00 Grubs (or one grub for XP).
- **8:00–14:00:** second Dragon ~10:00 with a 90 s reset. Cash grubs into turrets. Outer turrets are weakest 11:00–15:00. Clear grubs by 14:45.
- **14:00–20:00:** Herald 15:00 → a turret before 19:45. Third Dragon ~15:00. One side lane pushes away from the objective, and Baron vision goes in at 18:30–19:00.
- **20:00+:** Baron only on a numbers advantage. Spend the buff on structures. Treat soul and Elder as fight timers. Reset on time and don't overstay.

### Gaps
- No 2026 Korean coach video transcript defining 턴 for this season was found in this session; see the earlier repo notes.
- Pro-level cross-map trade rules from LCK 2026 analysis articles (Inven Global, Oracle's Elixir) were not surfaced by search.
