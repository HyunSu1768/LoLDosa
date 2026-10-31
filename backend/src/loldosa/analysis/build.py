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
WITH start AS (
    SELECT f.match_id, f.pid, arg_min(c.camp, (f.x - c.cx) ^ 2 + (f.y - c.cy) ^ 2) AS start_camp
    FROM gfr f JOIN camps c ON c.team_id = f.team_id
    WHERE f.minute = 1 GROUP BY ALL
), at3 AS (
    SELECT match_id, pid, rel_region(team_id, x, y) AS route3, map_side(x, y) AS side3
    FROM gfr WHERE minute = 3
), at10 AS (
    SELECT match_id, pid,
           max(gold_diff) FILTER (WHERE minute = 5) AS gd5,
           max(gold_diff) FILTER (WHERE minute = 10) AS gd10,
           max(gold_diff) FILTER (WHERE minute = 15) AS gd15,
           max(xp_diff) FILTER (WHERE minute = 10) AS xpd10
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
SELECT g.*, s.start_camp, a.route3, a.side3, t.gd5, t.gd10, t.gd15, t.xpd10,
       fg.first_gank_ms, fg.first_gank_lane, fg.first_gank_outcome,
       coalesce(ea.takedowns10, 0) AS takedowns10, coalesce(ea.deaths10, 0) AS deaths10,
       coalesce(ea.jungle_fights5, 0) AS jungle_fights5
FROM g
LEFT JOIN start s USING (match_id, pid)
LEFT JOIN at3 a USING (match_id, pid)
LEFT JOIN at10 t USING (match_id, pid)
LEFT JOIN fg USING (match_id, pid)
LEFT JOIN early ea USING (match_id, pid);

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
    avg(enemy_jungle_minions) AS enemy_jungle_cs, avg(vision_score) AS vision,
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
SELECT sc.scope, sc.bucket, x.champ AS champion_id, x.start_camp, x.route3, x.side3,
    count(*) AS games, sum(win) AS wins, avg(gd10) AS gd10
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

    "gank_targets": """
WITH ganks AS (
    SELECT x.match_id, x.team_id, x.first_gank_lane AS lane, (x.first_gank_outcome = 'kill')::INT AS killed,
        CASE x.first_gank_lane WHEN 'top' THEN 'TOP' WHEN 'mid' THEN 'MIDDLE' ELSE 'BOTTOM' END AS pos
    FROM gxo x WHERE x.first_gank_ms IS NOT NULL
)
SELECT sc.scope, sc.bucket, k.lane, CASE WHEN p.team_id = k.team_id THEN 'ally' ELSE 'enemy' END AS rel,
    p.champion_id, count(*) AS ganks, avg(k.killed) AS kill_rate
FROM ganks k
JOIN src.participants p ON p.match_id = k.match_id
    AND (p.position = k.pos OR (k.lane = 'bot' AND p.position = 'UTILITY'))
JOIN sc ON sc.match_id = k.match_id GROUP BY ALL""",

    "gank_lane_base": """
SELECT sc.scope, sc.bucket, first_gank_lane AS lane, count(*) AS ganks,
    avg((first_gank_outcome = 'kill')::INT) AS kill_rate, quantile_cont(first_gank_ms, 0.5) / 1000 AS median_s
FROM gxo x JOIN sc USING (match_id) WHERE first_gank_ms IS NOT NULL GROUP BY ALL""",

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

# 아군 4명 평균 AP 성향 기준. Data Dragon 수치 분포를 보고 정한 값
AD_CUT, AP_CUT = 0.42, 0.58


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
        con.execute("CREATE TABLE champ_meta AS SELECT * FROM _cm").fetchall()
        con.unregister("_cm")
        con.execute(PREP.format(camps=camps_sql_values())).fetchall()

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
