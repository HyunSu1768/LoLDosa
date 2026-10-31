"""matches.duckdb → stats.duckdb 집계.

모든 통계는 (scope, bucket) 별로 저장한다.
- scope: 패치("16.21") 또는 'ALL'(수집 기간 전체)
- bucket: apex | platinum | all
표본 수(games)를 항상 같이 저장하고, 판단(신뢰도/보정)은 query 계층에서 한다.

주의: 타임라인으로 관측할 수 없는 것(킬로 이어지지 않은 갱 시도, 개별 캠프 처치 순서)은
추정하지 않는다. 동선은 1분 단위 위치로만 분류한다.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pyarrow as pa

from ..ddragon import ChampionIndex
from . import turns
from .geometry import SQL_MACROS, camps_sql_values

PREP = """
CREATE TEMP TABLE sc AS
    SELECT match_id, patch AS scope, bucket FROM src.matches
    UNION ALL SELECT match_id, 'ALL', bucket FROM src.matches
    UNION ALL SELECT match_id, patch, 'all' FROM src.matches
    UNION ALL SELECT match_id, 'ALL', 'all' FROM src.matches;

CREATE TEMP TABLE team_kills AS
    SELECT match_id, team_id, sum(kills) AS kills FROM src.participants GROUP BY ALL;

-- 정글러 1명 = 1행
CREATE TEMP TABLE g AS
SELECT p.match_id, m.duration_s, p.team_id, p.participant_id AS pid, p.champion_id AS champ,
       p.win::INT AS win, e.participant_id AS epid, e.champion_id AS echamp,
       p.kills, p.deaths, p.assists, p.enemy_jungle_minions, p.vision_score, p.control_wards,
       (p.kills + p.assists) / greatest(tk.kills, 1) AS kp
FROM src.participants p
JOIN src.matches m USING (match_id)
JOIN src.participants e ON e.match_id = p.match_id AND e.position = 'JUNGLE' AND e.team_id <> p.team_id
JOIN team_kills tk ON tk.match_id = p.match_id AND tk.team_id = p.team_id
WHERE p.position = 'JUNGLE';

-- 정글러 vs 상대 정글러, 분 단위
CREATE TEMP TABLE gfr AS
SELECT g.match_id, g.pid, g.team_id, f.minute, f.x, f.y, f.level, f.jungle_cs,
       f.total_gold - ef.total_gold AS gold_diff,
       f.xp - ef.xp AS xp_diff,
       f.level - ef.level AS level_diff
FROM g
JOIN src.frames f ON f.match_id = g.match_id AND f.participant_id = g.pid
JOIN src.frames ef ON ef.match_id = g.match_id AND ef.participant_id = g.epid AND ef.minute = f.minute
WHERE f.minute BETWEEN 1 AND 25;

CREATE TEMP TABLE camps AS SELECT * FROM (VALUES {camps}) t(team_id, camp, cx, cy);

-- 시작 캠프(1:00 위치에서 가장 가까운 자기 진영 캠프), 3:00 위치, 이른 갱
CREATE TEMP TABLE gx AS
WITH dist AS (
    SELECT f.match_id, f.pid, c.camp, sqrt((f.x - c.cx) ^ 2 + (f.y - c.cy) ^ 2) AS d,
           row_number() OVER (PARTITION BY f.match_id, f.pid ORDER BY (f.x - c.cx) ^ 2 + (f.y - c.cy) ^ 2) AS rk
    FROM gfr f JOIN camps c ON c.team_id = f.team_id
    WHERE f.minute = 1
), start AS (
    -- 1:00 위치가 두 캠프 사이(거리 차 {start_margin} 미만)면 시작 캠프를 단정하지 않는다
    SELECT a.match_id, a.pid, CASE WHEN b.d - a.d >= {start_margin} THEN a.camp END AS start_camp,
           map_side(f1.x, f1.y) AS start_side
    FROM dist a JOIN dist b ON a.match_id = b.match_id AND a.pid = b.pid AND a.rk = 1 AND b.rk = 2
    JOIN gfr f1 ON f1.match_id = a.match_id AND f1.pid = a.pid AND f1.minute = 1
), at3 AS (
    -- 정글 몬스터 CS 는 캠프당 4씩 오른다. 스커틀은 3:30 생성이라 3:00 값은 캠프 수만 반영
    SELECT match_id, pid, rel_region(team_id, x, y) AS route3, map_side(x, y) AS side3,
           jungle_cs // 4 AS camps3,
           CASE WHEN jungle_cs // 4 >= 6 THEN 'full_clear'
                WHEN jungle_cs // 4 >= 4 THEN 'partial'
                ELSE 'three_or_less' END AS clear3
    FROM gfr WHERE minute = 3
), at4 AS (
    SELECT match_id, pid, map_side(x, y) AS side4 FROM gfr WHERE minute = 4
), at10 AS (
    SELECT match_id, pid,
           max(gold_diff) FILTER (WHERE minute = 5) AS gd5,
           max(gold_diff) FILTER (WHERE minute = 10) AS gd10,
           max(gold_diff) FILTER (WHERE minute = 15) AS gd15,
           max(xp_diff) FILTER (WHERE minute = 10) AS xpd10,
           max(jungle_cs) FILTER (WHERE minute = 10) AS jungle_cs10
    FROM gfr GROUP BY ALL
), kills AS (
    SELECT g.match_id, g.pid, e.ts_ms, region(e.x, e.y) AS reg,
           CASE WHEN (e.victim_id <= 5) = (g.team_id = 100) THEN 'death' ELSE 'kill' END AS outcome
    FROM g JOIN src.events e ON e.match_id = g.match_id AND e.type = 'CHAMPION_KILL'
    WHERE e.participant_id = g.pid OR e.victim_id = g.pid OR list_contains(e.assists, g.pid)
), fg AS (
    SELECT match_id, pid,
           min(ts_ms) AS first_gank_ms,
           arg_min(reg, ts_ms) AS first_gank_lane,
           arg_min(outcome, ts_ms) AS first_gank_outcome
    FROM kills WHERE ts_ms < 480000 AND reg IN ('top', 'mid', 'bot') GROUP BY ALL
), early AS (
    SELECT match_id, pid,
           count(*) FILTER (WHERE ts_ms < 600000 AND outcome = 'kill') AS takedowns10,
           count(*) FILTER (WHERE ts_ms < 600000 AND outcome = 'death') AS deaths10,
           count(*) FILTER (WHERE ts_ms < 300000 AND reg NOT IN ('top', 'mid', 'bot', 'base')) AS jungle_fights5
    FROM kills GROUP BY ALL
)
SELECT g.*, s.start_camp, s.start_side, a.route3, a.side3, a.camps3, a.clear3, t.gd5, t.gd10, t.gd15, t.xpd10,
       t.jungle_cs10,
       fg.first_gank_ms, fg.first_gank_lane, fg.first_gank_outcome,
       coalesce(ea.takedowns10, 0) AS takedowns10, coalesce(ea.deaths10, 0) AS deaths10,
       coalesce(ea.jungle_fights5, 0) AS jungle_fights5, a4.side4
FROM g
LEFT JOIN start s USING (match_id, pid)
LEFT JOIN at3 a USING (match_id, pid)
LEFT JOIN at10 t USING (match_id, pid)
LEFT JOIN fg USING (match_id, pid)
LEFT JOIN early ea USING (match_id, pid)
LEFT JOIN at4 a4 USING (match_id, pid);

-- 경기별 오브젝트
CREATE TEMP TABLE obj AS
SELECT match_id,
    arg_min(team_id, ts_ms) FILTER (WHERE monster_type = 'DRAGON') AS first_dragon_team,
    min(ts_ms) FILTER (WHERE monster_type = 'DRAGON') AS first_dragon_ms,
    arg_min(team_id, ts_ms) FILTER (WHERE monster_type = 'HORDE') AS first_grub_team,
    min(ts_ms) FILTER (WHERE monster_type = 'HORDE') AS first_grub_ms,
    count(*) FILTER (WHERE monster_type = 'HORDE' AND team_id = 100) AS grubs_100,
    count(*) FILTER (WHERE monster_type = 'HORDE' AND team_id = 200) AS grubs_200,
    arg_min(team_id, ts_ms) FILTER (WHERE monster_type = 'RIFTHERALD') AS herald_team,
    min(ts_ms) FILTER (WHERE monster_type = 'RIFTHERALD') AS herald_ms,
    arg_min(team_id, ts_ms) FILTER (WHERE monster_type = 'ATAKHAN') AS atakhan_team,
    min(ts_ms) FILTER (WHERE monster_type = 'ATAKHAN') AS atakhan_ms,
    arg_min(team_id, ts_ms) FILTER (WHERE monster_type = 'BARON_NASHOR') AS baron_team,
    min(ts_ms) FILTER (WHERE monster_type = 'BARON_NASHOR') AS baron_ms
FROM src.events WHERE type = 'ELITE_MONSTER_KILL' GROUP BY match_id;

CREATE TEMP TABLE gxo AS
SELECT gx.*,
    (o.first_dragon_team = gx.team_id)::INT AS own_first_dragon,
    (o.first_grub_team = gx.team_id)::INT AS own_first_grub,
    CASE WHEN gx.team_id = 100 THEN o.grubs_100 ELSE o.grubs_200 END AS own_grubs,
    (o.herald_team = gx.team_id)::INT AS own_herald,
    (o.baron_team = gx.team_id)::INT AS own_first_baron,
    CASE WHEN gx.duration_s < 1500 THEN '<25' WHEN gx.duration_s < 1800 THEN '25-30'
         WHEN gx.duration_s < 2100 THEN '30-35' ELSE '35+' END AS dur_bucket
FROM gx LEFT JOIN obj o USING (match_id);

-- 상점 방문(귀환) — 규칙은 analysis/turns.py 와 같다
CREATE TEMP TABLE visits AS
WITH p AS (
    SELECT match_id, participant_id AS pid, ts_ms,
        ts_ms - lag(ts_ms) OVER (PARTITION BY match_id, participant_id ORDER BY ts_ms) AS gap
    FROM src.events WHERE type = 'ITEM_PURCHASED' AND ts_ms >= {start_ms}
), s AS (SELECT * FROM p WHERE gap IS NULL OR gap > {gap_ms})
SELECT s.match_id, s.pid, s.ts_ms,
    EXISTS (SELECT 1 FROM src.events d WHERE d.match_id = s.match_id AND d.type = 'CHAMPION_KILL'
            AND d.victim_id = s.pid AND d.ts_ms >= s.ts_ms - {death_ms} AND d.ts_ms < s.ts_ms) AS death_back
FROM s;

-- 첫 드래곤 / 첫 유충 직전 각 팀의 '턴' 상태
CREATE TEMP TABLE obj_turns AS
WITH firsts AS (
    SELECT match_id, monster_type, min(ts_ms) AS t, arg_min(team_id, ts_ms) AS taker
    FROM src.events WHERE type = 'ELITE_MONSTER_KILL' AND monster_type IN ('DRAGON', 'HORDE')
    GROUP BY ALL
), teams AS (
    SELECT f.*, tm.team_id FROM firsts f CROSS JOIN (VALUES (100), (200)) tm(team_id)
), roles AS (
    SELECT t.*, p.participant_id AS pid, p.position FROM teams t
    JOIN src.participants p ON p.match_id = t.match_id AND p.team_id = t.team_id
), v AS (
    SELECT r.*, vi.ts_ms AS vt, vi.death_back FROM roles r
    JOIN visits vi ON vi.match_id = r.match_id AND vi.pid = r.pid
), flags AS (
    SELECT t.match_id, t.monster_type, t.t, t.taker, t.team_id,
        bool_or(v.position = 'JUNGLE' AND NOT v.death_back AND v.vt BETWEEN t.t - {setup_from} AND t.t - {setup_to}) AS jg_setup,
        bool_or(v.position = 'JUNGLE' AND v.vt BETWEEN t.t - {late_from} AND t.t) AS jg_late
    FROM teams t LEFT JOIN v ON v.match_id = t.match_id AND v.team_id = t.team_id AND v.monster_type = t.monster_type
    GROUP BY ALL
), sync AS (
    SELECT j.match_id, j.monster_type, j.team_id, true AS synced
    FROM v j JOIN v l ON l.match_id = j.match_id AND l.team_id = j.team_id AND l.monster_type = j.monster_type
    WHERE j.position = 'JUNGLE' AND NOT j.death_back AND NOT l.death_back
      AND j.vt BETWEEN j.t - {setup_from} AND j.t - {setup_to}
      AND abs(l.vt - j.vt) <= {sync_ms}
      AND ((j.monster_type = 'DRAGON' AND l.position IN ('BOTTOM', 'UTILITY', 'MIDDLE'))
        OR (j.monster_type = 'HORDE' AND l.position IN ('TOP', 'MIDDLE')))
    GROUP BY ALL
)
SELECT f.*, coalesce(s.synced, false) AS synced,
    CASE WHEN f.jg_late THEN 'late' WHEN s.synced THEN 'sync' WHEN f.jg_setup THEN 'jg_only' ELSE 'none' END AS turn,
    (f.taker = f.team_id)::INT AS took
FROM flags f LEFT JOIN sync s USING (match_id, monster_type, team_id);

-- 아군 4명 조합 성향
CREATE TEMP TABLE ally_profile AS
SELECT g.match_id, g.pid,
       avg(cm.ap_share) AS ally_ap,
       sum(cm.frontline::INT) AS ally_frontline
FROM g JOIN src.participants a ON a.match_id = g.match_id AND a.team_id = g.team_id AND a.participant_id <> g.pid
JOIN champ_meta cm ON cm.champion_id = a.champion_id
GROUP BY ALL;
"""

OUTPUTS = {
    "champ_stats": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id,
    count(*) AS games, sum(win) AS wins,
    avg(kills) AS kills, avg(deaths) AS deaths, avg(assists) AS assists, avg(kp) AS kp,
    avg(gd10) AS gd10, avg(gd15) AS gd15, avg(xpd10) AS xpd10,
    avg(takedowns10) AS takedowns10, avg(deaths10) AS deaths10,
    avg(enemy_jungle_minions) AS enemy_jungle_cs, avg(vision_score) AS vision, avg(control_wards) AS control_wards,
    avg(jungle_cs10) AS jungle_cs10, avg(camps3) AS camps3, avg(deaths) AS deaths_game,
    avg(vision_score / (duration_s / 60.0)) AS vision_pm,
    avg(own_first_dragon) AS first_dragon_rate, avg(own_first_grub) AS first_grub_rate,
    avg(own_grubs) AS grubs, avg(own_herald) AS herald_rate,
    avg(first_gank_ms) / 1000 AS first_gank_s,
    avg((first_gank_ms IS NOT NULL)::INT) AS early_gank_rate,
    avg((first_gank_outcome = 'kill')::INT) FILTER (WHERE first_gank_ms IS NOT NULL) AS first_gank_kill_rate
FROM gxo x JOIN sc USING (match_id) GROUP BY ALL""",

    "match_totals": """
SELECT scope, bucket, count(*) AS matches FROM sc GROUP BY ALL""",

    "ban_stats": """
SELECT sc.scope, sc.bucket, b.champion_id, count(DISTINCT b.match_id) AS banned
FROM src.bans b JOIN sc USING (match_id) GROUP BY ALL""",

    "matchups": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, x.echamp AS enemy_id,
    count(*) AS games, sum(win) AS wins,
    avg(gd5) AS gd5, avg(gd10) AS gd10, avg(gd15) AS gd15,
    avg(takedowns10) AS takedowns10, avg(deaths10) AS deaths10,
    avg(jungle_fights5) AS jungle_fights5,
    avg(enemy_jungle_minions) AS enemy_jungle_cs,
    avg(own_first_dragon) AS first_dragon_rate, avg(own_grubs) AS grubs
FROM gxo x JOIN sc USING (match_id) GROUP BY ALL""",

    "duration": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, dur_bucket, count(*) AS games, sum(win) AS wins
FROM gxo x JOIN sc USING (match_id) GROUP BY ALL""",

    "curves": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, f.minute,
    count(*) AS games, avg(f.gold_diff) AS gold_diff, avg(f.xp_diff) AS xp_diff, avg(f.level_diff) AS level_diff,
    avg(f.level) AS level
FROM gfr f JOIN g x USING (match_id, pid) JOIN sc USING (match_id) GROUP BY ALL""",

    "matchup_curves": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, x.echamp AS enemy_id, f.minute,
    count(*) AS games, avg(f.gold_diff) AS gold_diff, avg(f.level_diff) AS level_diff
FROM gfr f JOIN g x USING (match_id, pid) JOIN sc USING (match_id)
WHERE f.minute <= 20 GROUP BY ALL""",

    "start_camps": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, x.team_id, x.start_camp,
    count(*) AS games, sum(win) AS wins
FROM gxo x JOIN sc USING (match_id) WHERE start_camp IS NOT NULL GROUP BY ALL""",

    "routes": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, x.team_id, x.start_camp, x.start_side, x.route3, x.side3,
    x.side4, x.clear3,
    count(*) AS games, sum(win) AS wins, avg(gd10) AS gd10, avg(first_gank_ms) / 1000 AS first_gank_s
FROM gxo x JOIN sc USING (match_id) WHERE route3 IS NOT NULL GROUP BY ALL""",

    "first_ganks": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, x.first_gank_lane AS lane,
    count(*) AS games, sum(win) AS wins,
    avg(first_gank_ms) / 1000 AS avg_s, quantile_cont(first_gank_ms, 0.5) / 1000 AS median_s,
    avg((first_gank_outcome = 'kill')::INT) AS kill_rate
FROM gxo x JOIN sc USING (match_id) WHERE first_gank_ms IS NOT NULL GROUP BY ALL""",

    "presence": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, f.minute, rel_region(f.team_id, f.x, f.y) AS region,
    count(*) AS n
FROM gfr f JOIN g x USING (match_id, pid) JOIN sc USING (match_id)
WHERE f.minute BETWEEN 2 AND 8 GROUP BY ALL""",

    "synergy": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, a.champion_id AS ally_id, a.position AS ally_position,
    count(*) AS games, sum(x.win) AS wins
FROM g x JOIN src.participants a ON a.match_id = x.match_id AND a.team_id = x.team_id AND a.participant_id <> x.pid
JOIN sc ON sc.match_id = x.match_id GROUP BY ALL""",

    "versus": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id, o.champion_id AS enemy_id, o.position AS enemy_position,
    count(*) AS games, sum(x.win) AS wins
FROM g x JOIN src.participants o ON o.match_id = x.match_id AND o.team_id <> x.team_id
JOIN sc ON sc.match_id = x.match_id GROUP BY ALL""",

    "comp_fit": """
SELECT sc.scope, sc.bucket, x.champ AS champion_id,
    CASE WHEN ap.ally_ap < {ad_cut} THEN 'ad_heavy' WHEN ap.ally_ap > {ap_cut} THEN 'ap_heavy' ELSE 'balanced' END AS ally_damage,
    CASE WHEN ap.ally_frontline = 0 THEN 'no_frontline' ELSE 'has_frontline' END AS ally_frontline,
    count(*) AS games, sum(x.win) AS wins
FROM g x JOIN ally_profile ap USING (match_id, pid) JOIN sc ON sc.match_id = x.match_id GROUP BY ALL""",

    "objectives": """
SELECT sc.scope, sc.bucket,
    count(*) AS matches,
    quantile_cont(first_dragon_ms, 0.5) / 1000 AS first_dragon_median_s,
    quantile_cont(first_grub_ms, 0.5) / 1000 AS first_grub_median_s,
    quantile_cont(herald_ms, 0.5) / 1000 AS herald_median_s,
    quantile_cont(atakhan_ms, 0.5) / 1000 AS atakhan_median_s,
    quantile_cont(baron_ms, 0.5) / 1000 AS baron_median_s
FROM obj JOIN sc USING (match_id) GROUP BY ALL""",

    "objective_impact": """
SELECT sc.scope, sc.bucket, k.objective, count(*) AS games, avg(k.taken_win) AS win_rate_when_taken
FROM (
    SELECT match_id, 'first_dragon' AS objective, (first_dragon_team = m.winner_team)::INT AS taken_win
        FROM obj JOIN src.matches m USING (match_id) WHERE first_dragon_team IS NOT NULL
    UNION ALL SELECT match_id, 'first_grub', (first_grub_team = m.winner_team)::INT
        FROM obj JOIN src.matches m USING (match_id) WHERE first_grub_team IS NOT NULL
    UNION ALL SELECT match_id, 'herald', (herald_team = m.winner_team)::INT
        FROM obj JOIN src.matches m USING (match_id) WHERE herald_team IS NOT NULL
    UNION ALL SELECT match_id, 'atakhan', (atakhan_team = m.winner_team)::INT
        FROM obj JOIN src.matches m USING (match_id) WHERE atakhan_team IS NOT NULL
    UNION ALL SELECT match_id, 'first_baron', (baron_team = m.winner_team)::INT
        FROM obj JOIN src.matches m USING (match_id) WHERE baron_team IS NOT NULL
    UNION ALL SELECT match_id, 'grubs_majority',
        (CASE WHEN grubs_100 > grubs_200 THEN 100 ELSE 200 END = m.winner_team)::INT
        FROM obj JOIN src.matches m USING (match_id) WHERE grubs_100 <> grubs_200
) k JOIN sc USING (match_id) GROUP BY ALL""",

    "champ_positions": """
SELECT sc.scope, sc.bucket, p.champion_id, p.position, count(*) AS games, sum(p.win::INT) AS wins
FROM src.participants p JOIN sc USING (match_id) WHERE p.position <> '' GROUP BY ALL""",

    "lane_matchups": """
SELECT sc.scope, sc.bucket, p.position, p.champion_id, o.champion_id AS enemy_id,
    count(*) AS games, sum(p.win::INT) AS wins, avg(f.total_gold - fo.total_gold) AS gd10
FROM src.participants p
JOIN src.participants o ON o.match_id = p.match_id AND o.position = p.position AND o.team_id <> p.team_id
JOIN src.frames f ON f.match_id = p.match_id AND f.participant_id = p.participant_id AND f.minute = 10
JOIN src.frames fo ON fo.match_id = p.match_id AND fo.participant_id = o.participant_id AND fo.minute = 10
JOIN sc ON sc.match_id = p.match_id
WHERE p.position IN ('TOP', 'MIDDLE', 'BOTTOM', 'UTILITY') GROUP BY ALL""",

    "gank_exposure": """
-- 라이너 기준: 8분 전 상대 정글이 관여한 킬에 죽은 판 비율 / 우리 정글과 함께 킬을 낸 판 비율.
-- '킬이 난 갱만 보는' 선택 편향 없이 라이너의 모든 판을 분모로 쓴다.
WITH lane AS (
    SELECT p.match_id, p.team_id, p.participant_id AS pid, p.position, p.champion_id,
           jg.participant_id AS ally_jg, ejg.participant_id AS enemy_jg
    FROM src.participants p
    JOIN src.participants jg ON jg.match_id = p.match_id AND jg.team_id = p.team_id AND jg.position = 'JUNGLE'
    JOIN src.participants ejg ON ejg.match_id = p.match_id AND ejg.team_id <> p.team_id AND ejg.position = 'JUNGLE'
    WHERE p.position IN ('TOP', 'MIDDLE', 'BOTTOM', 'UTILITY')
), ev AS (
    SELECT l.match_id, l.pid,
        max((e.victim_id = l.pid AND (e.participant_id = l.enemy_jg OR list_contains(e.assists, l.enemy_jg)))::INT) AS died_to_jg,
        max((e.victim_id <> l.pid AND (e.participant_id = l.pid OR list_contains(e.assists, l.pid))
             AND (e.participant_id = l.ally_jg OR list_contains(e.assists, l.ally_jg)))::INT) AS kill_with_jg
    FROM lane l JOIN src.events e ON e.match_id = l.match_id AND e.type = 'CHAMPION_KILL' AND e.ts_ms < 480000
    GROUP BY ALL
)
SELECT sc.scope, sc.bucket, l.position, l.champion_id, count(*) AS games,
    avg(coalesce(ev.died_to_jg, 0)) AS died_to_jg, avg(coalesce(ev.kill_with_jg, 0)) AS kill_with_jg
FROM lane l LEFT JOIN ev USING (match_id, pid) JOIN sc ON sc.match_id = l.match_id GROUP BY ALL""",

    "jungle_duels": """
-- 정글러끼리의 킬 교환(한쪽 정글러가 죽고 다른 쪽 정글러가 킬/어시스트), 15분 전, 내 레벨 구간별
WITH d AS (
    SELECT x.match_id, x.champ, x.echamp, e.ts_ms,
        CASE WHEN e.victim_id = x.epid THEN 1 ELSE 0 END AS won,
        f.level
    FROM g x JOIN src.events e ON e.match_id = x.match_id AND e.type = 'CHAMPION_KILL' AND e.ts_ms < 900000
    JOIN src.frames f ON f.match_id = x.match_id AND f.participant_id = x.pid AND f.minute = e.ts_ms // 60000
    WHERE (e.victim_id = x.epid AND (e.participant_id = x.pid OR list_contains(e.assists, x.pid)))
       OR (e.victim_id = x.pid AND (e.participant_id = x.epid OR list_contains(e.assists, x.epid)))
)
SELECT sc.scope, sc.bucket, d.champ AS champion_id, d.echamp AS enemy_id,
    CASE WHEN d.level <= 3 THEN '1-3' WHEN d.level <= 5 THEN '4-5' ELSE '6+' END AS level_band,
    count(*) AS fights, sum(won) AS won
FROM d JOIN sc USING (match_id) GROUP BY ALL""",

    "turn_objective": """
SELECT sc.scope, sc.bucket, o.monster_type AS objective, o.turn, count(*) AS games, sum(o.took) AS took
FROM obj_turns o JOIN sc USING (match_id) GROUP BY ALL""",

    "first_recall": """
WITH f AS (
    SELECT x.match_id, x.champ, min(v.ts_ms) AS first_ms
    FROM g x JOIN visits v ON v.match_id = x.match_id AND v.pid = x.pid AND NOT v.death_back
    GROUP BY ALL
)
SELECT sc.scope, sc.bucket, f.champ AS champion_id, count(*) AS games,
    quantile_cont(first_ms, 0.25) / 1000 AS p25_s, quantile_cont(first_ms, 0.5) / 1000 AS median_s,
    quantile_cont(first_ms, 0.75) / 1000 AS p75_s
FROM f JOIN sc USING (match_id) GROUP BY ALL""",

    "side_transition": """
SELECT sc.scope, sc.bucket, x.clear3, x.start_side, x.side3, x.side4, count(*) AS games
FROM gxo x JOIN sc USING (match_id) WHERE x.start_side IS NOT NULL GROUP BY ALL""",

    "duration_all": """
SELECT sc.scope, sc.bucket, p.champion_id,
    CASE WHEN m.duration_s < 1500 THEN '<25' WHEN m.duration_s < 1800 THEN '25-30'
         WHEN m.duration_s < 2100 THEN '30-35' ELSE '35+' END AS dur_bucket,
    count(*) AS games, sum(p.win::INT) AS wins
FROM src.participants p JOIN src.matches m USING (match_id) JOIN sc USING (match_id) GROUP BY ALL""",
}

PRO_OUTPUTS = {
    "pro_champ": """
SELECT champion_id, count(*) AS games, sum(win::INT) AS wins, count(DISTINCT player) AS players,
    avg(minutes) AS minutes, avg(own_grubs) AS grubs, avg(own_dragons) AS dragons, avg(own_heralds) AS heralds,
    string_agg(DISTINCT regexp_extract(overview, '^([^/]+)', 1), ', ') AS leagues
FROM pro.pro_jungle WHERE champion_id > 0 GROUP BY ALL""",
    "pro_matchups": """
SELECT a.champion_id, b.champion_id AS enemy_id, count(*) AS games, sum(a.win::INT) AS wins
FROM pro.pro_jungle a JOIN pro.pro_jungle b ON a.game_id = b.game_id AND a.team <> b.team
WHERE a.champion_id > 0 AND b.champion_id > 0 GROUP BY ALL""",
    "pro_info": """
SELECT count(DISTINCT game_id) AS games, min(played_at) AS since, max(played_at) AS until
FROM pro.pro_jungle""",
}

# 챔피언 성향: 실제 경기의 피해 데이터로 계산 (표본 10판 미만이면 Data Dragon 수치로 대체)
# - ap_share: 챔피언에게 준 마법 피해 / (마법 + 물리)
# - tank_share: 팀 안에서 받은 피해 + 경감한 피해의 비중 (팀 평균 0.2)
PROFILE_SQL = """
CREATE TABLE champ_profile AS
WITH p AS (
    SELECT champion_id, magic_dmg, physical_dmg,
        (dmg_taken + self_mitigated)::DOUBLE
            / nullif(sum(dmg_taken + self_mitigated) OVER (PARTITION BY match_id, team_id), 0) AS tank_share
    FROM src.participants WHERE magic_dmg IS NOT NULL
), agg AS (
    SELECT champion_id, count(*) AS games,
        sum(magic_dmg)::DOUBLE / nullif(sum(magic_dmg + physical_dmg), 0) AS ap_share, avg(tank_share) AS tank_share
    FROM p GROUP BY champion_id
)
SELECT d.champion_id, coalesce(a.games, 0) AS games,
    CASE WHEN a.games >= 10 THEN a.ap_share ELSE d.ap_share END AS ap_share,
    CASE WHEN a.games >= 10 THEN a.tank_share END AS tank_share,
    CASE WHEN a.games >= 10 THEN a.tank_share >= 0.24 ELSE d.frontline END AS frontline,
    CASE WHEN a.games >= 10 THEN 'match_data' ELSE 'ddragon' END AS source
FROM ddragon_meta d LEFT JOIN agg a USING (champion_id);
CREATE TEMP VIEW champ_meta AS SELECT champion_id, ap_share, frontline FROM champ_profile;
"""
START_MARGIN = 300

# 아군 4명 평균 마법 피해 비중 기준. 실제 경기 분포의 3분위(하위 1/3 = AD 위주, 상위 1/3 = AP 위주)
AD_CUT, AP_CUT = 0.45, 0.54


def build_stats(data_dir: Path, champs: ChampionIndex) -> dict[str, int]:
    src = data_dir / "matches.duckdb"
    out = data_dir / "stats.duckdb"
    tmp = data_dir / "stats.building.duckdb"
    for p in (tmp, Path(str(tmp) + ".wal")):
        p.unlink(missing_ok=True)

    con = duckdb.connect(str(tmp))
    try:
        con.execute(f"ATTACH '{src}' AS src (READ_ONLY)").fetchall()
        con.execute(SQL_MACROS).fetchall()
        meta = champs.all()
        con.register("_cm", pa.Table.from_pydict({
            "champion_id": [c.id for c in meta],
            "ap_share": [c.ap_share for c in meta],
            "frontline": [c.frontline for c in meta],
        }))
        con.execute("CREATE TEMP TABLE ddragon_meta AS SELECT * FROM _cm").fetchall()
        con.unregister("_cm")
        con.execute(PROFILE_SQL).fetchall()
        con.execute(PREP.format(
            camps=camps_sql_values(), start_margin=START_MARGIN,
            start_ms=turns.START_MS, gap_ms=turns.GAP_MS, death_ms=turns.DEATH_WINDOW_MS,
            setup_from=turns.SETUP_FROM_MS, setup_to=turns.SETUP_TO_MS, late_from=turns.LATE_FROM_MS,
            sync_ms=turns.SYNC_MS)).fetchall()

        counts = {}
        for name, sql in OUTPUTS.items():
            con.execute(f"CREATE TABLE {name} AS " + sql.format(ad_cut=AD_CUT, ap_cut=AP_CUT)).fetchall()
            counts[name] = con.execute(f"SELECT count(*) FROM {name}").fetchall()[0][0]

        pro = data_dir / "pro.duckdb"
        if pro.exists():
            con.execute(f"ATTACH '{pro}' AS pro (READ_ONLY)").fetchall()
            for name, sql in PRO_OUTPUTS.items():
                con.execute(f"CREATE TABLE {name} AS {sql}").fetchall()
                counts[name] = con.execute(f"SELECT count(*) FROM {name}").fetchall()[0][0]
            con.execute("DETACH pro").fetchall()

        latest = con.execute(
            "SELECT patch FROM src.matches GROUP BY patch ORDER BY max(game_start) DESC LIMIT 1").fetchall()
        con.execute("CREATE TABLE meta (key VARCHAR, value VARCHAR)").fetchall()
        con.executemany("INSERT INTO meta VALUES (?, ?)", [
            ("built_at", datetime.now(timezone.utc).isoformat(timespec="seconds")),
            ("latest_patch", latest[0][0] if latest else ""),
            ("ddragon_version", champs.version),
        ])
        con.execute("DETACH src").fetchall()
    finally:
        con.close()
    os.replace(tmp, out)
    return counts
