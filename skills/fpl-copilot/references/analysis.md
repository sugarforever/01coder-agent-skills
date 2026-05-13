# FPL Analysis Playbook

All formulas match the fpl-bot web app. Use these exact calculations for consistent analysis across all agents.

All SQL queries run against: `sqlite3 ~/.fplcopilot/fplcopilot.db`

---

## 1. Player Metrics

### Projected Points

Hybrid formula weighting recent form more than season average:

```
projected = points_per_game * 0.4 + recent_avg * 0.6
```

- `points_per_game`: from `players` table (season PPG from FPL API)
- `recent_avg`: average `total_points` from last 4 gameweek stats where `minutes > 0`
- If < 4 games played, `recent_avg` falls back to `points_per_game`

**Confidence levels:**
- `high`: 4+ games with minutes
- `medium`: 2-3 games
- `low`: 0-1 games

**Projected value:** `projected_points / (now_cost / 10.0)` — points per million

```sql
-- Get recent average and confidence for all players
SELECT
  p.id, p.web_name, p.points_per_game,
  COALESCE(r.recent_avg, p.points_per_game) AS recent_avg,
  p.points_per_game * 0.4 + COALESCE(r.recent_avg, p.points_per_game) * 0.6 AS projected,
  COALESCE(r.games, 0) AS games_played,
  CASE
    WHEN COALESCE(r.games, 0) >= 4 THEN 'high'
    WHEN COALESCE(r.games, 0) >= 2 THEN 'medium'
    ELSE 'low'
  END AS confidence
FROM players p
LEFT JOIN (
  SELECT player_id, AVG(total_points) AS recent_avg, COUNT(*) AS games
  FROM (
    SELECT player_id, total_points,
      ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY gameweek_id DESC) AS rn
    FROM player_gameweek_stats
    WHERE minutes > 0
  ) WHERE rn <= 4
  GROUP BY player_id
) r ON p.id = r.player_id
WHERE p.status = 'a'
ORDER BY projected DESC
LIMIT 20;
```

### VAPM (Value Added Per Million)

```
vapm = total_points / (now_cost / 10.0)
```

```sql
SELECT web_name, position, total_points, now_cost,
  ROUND(total_points * 10.0 / now_cost, 2) AS vapm
FROM players
WHERE minutes > 0
ORDER BY vapm DESC
LIMIT 20;
```

### Nailedness

How likely a player starts. Based on minutes played in last 5 gameweeks, capped at 1.0.

```
nailedness = MIN(1.0, SUM(minutes) / (games * 90))
```

```sql
SELECT player_id, p.web_name,
  MIN(1.0, CAST(SUM(s.minutes) AS REAL) / (COUNT(*) * 90)) AS nailedness
FROM (
  SELECT player_id, minutes,
    ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY gameweek_id DESC) AS rn
  FROM player_gameweek_stats
) s
JOIN players p ON s.player_id = p.id
WHERE s.rn <= 5
GROUP BY s.player_id
ORDER BY nailedness DESC;
```

### ICT Trend

Compare average ICT index of last 3 GWs vs the 3 GWs before that. Requires 6 samples. Positive = improving, negative = declining.

```
ict_trend = avg(GW[-1..-3]) - avg(GW[-4..-6])
```

```sql
SELECT player_id, p.web_name,
  AVG(CASE WHEN rn <= 3 THEN ict_index END) AS recent_ict,
  AVG(CASE WHEN rn BETWEEN 4 AND 6 THEN ict_index END) AS previous_ict,
  ROUND(
    AVG(CASE WHEN rn <= 3 THEN ict_index END) -
    AVG(CASE WHEN rn BETWEEN 4 AND 6 THEN ict_index END),
  2) AS ict_trend
FROM (
  SELECT player_id, ict_index,
    ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY gameweek_id DESC) AS rn
  FROM player_gameweek_stats
) s
JOIN players p ON s.player_id = p.id
WHERE s.rn <= 6
GROUP BY s.player_id
HAVING COUNT(CASE WHEN rn <= 3 THEN 1 END) = 3
   AND COUNT(CASE WHEN rn BETWEEN 4 AND 6 THEN 1 END) = 3
ORDER BY ict_trend DESC
LIMIT 20;
```

### Sustainable Form

Players who score consistently high (high average + low variance). Rewards reliability over one-off hauls.

```
sustainability_score = recent_avg / (1 + stdev * 0.3)
```

- Minimum 3 games played with minutes > 0
- Filter: `recent_avg >= 3` points per game
- Computed over last 6 gameweek stats

```sql
SELECT player_id, p.web_name, p.position, t.short_name,
  ROUND(AVG(total_points), 1) AS recent_avg,
  COUNT(*) AS games,
  ROUND(AVG(total_points) / (1.0 + SQRT(AVG(total_points * total_points) - AVG(total_points) * AVG(total_points)) * 0.3), 2) AS sustainability
FROM (
  SELECT player_id, total_points,
    ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY gameweek_id DESC) AS rn
  FROM player_gameweek_stats
  WHERE minutes > 0
) s
JOIN players p ON s.player_id = p.id
JOIN teams t ON p.team_id = t.id
WHERE s.rn <= 6
GROUP BY s.player_id
HAVING COUNT(*) >= 3 AND AVG(total_points) >= 3
ORDER BY sustainability DESC
LIMIT 15;
```

### Availability Flags

Determine a player's availability for display:

| Status | Chance of Playing | Flag | Label |
|--------|-------------------|------|-------|
| `u` | any | Unavailable | AFCON, loan, etc. |
| `i` or `s` | any | Injured/Suspended | Out |
| `d` | any | Doubtful | 25-75% likely |
| `a` | null or 100 | Available | No flag needed |
| `a` | >= 75 | Likely | Probably plays |
| `a` | 25-74 | Doubtful | Uncertain |
| `a` | < 25 | Unlikely | Probably out |

```sql
-- Players with availability concerns
SELECT web_name, position, t.short_name, status, chance_of_playing, news,
  CASE
    WHEN status = 'u' THEN 'UNAVAILABLE'
    WHEN status IN ('i', 's') THEN 'OUT'
    WHEN status = 'd' THEN 'DOUBTFUL'
    WHEN chance_of_playing IS NULL OR chance_of_playing = 100 THEN 'AVAILABLE'
    WHEN chance_of_playing >= 75 THEN 'LIKELY'
    WHEN chance_of_playing >= 25 THEN 'DOUBTFUL'
    ELSE 'UNLIKELY'
  END AS availability
FROM players p
JOIN teams t ON p.team_id = t.id
WHERE status != 'a' OR (chance_of_playing IS NOT NULL AND chance_of_playing < 100)
ORDER BY status, chance_of_playing;
```

---

## 2. Team Metrics

### xG Differential

Aggregate expected goals from player gameweek stats grouped by team and venue:

```sql
SELECT p.team_id, t.short_name,
  ROUND(SUM(CASE WHEN pgs.was_home = 1 THEN pgs.expected_goals ELSE 0 END), 2) AS xg_for_home,
  ROUND(SUM(CASE WHEN pgs.was_home = 0 THEN pgs.expected_goals ELSE 0 END), 2) AS xg_for_away,
  ROUND(SUM(pgs.expected_goals), 2) AS xg_for_total,
  ROUND(SUM(CASE WHEN pgs.was_home = 1 THEN pgs.expected_goals_conceded ELSE 0 END), 2) AS xg_against_home,
  ROUND(SUM(CASE WHEN pgs.was_home = 0 THEN pgs.expected_goals_conceded ELSE 0 END), 2) AS xg_against_away,
  ROUND(SUM(pgs.expected_goals_conceded), 2) AS xg_against_total,
  ROUND(SUM(pgs.expected_goals) - SUM(pgs.expected_goals_conceded), 2) AS xg_diff,
  COUNT(DISTINCT pgs.fixture_id) AS matches
FROM player_gameweek_stats pgs
JOIN players p ON pgs.player_id = p.id
JOIN teams t ON p.team_id = t.id
WHERE pgs.minutes > 0
GROUP BY p.team_id
ORDER BY xg_diff DESC;
```

### Team Momentum

Compare rolling (last 3 matches) xG averages vs season averages. Uses **delta** (not ratio):

```
attack_delta  = rolling_xg_for_per_match - season_xg_for_per_match
defence_delta = season_xg_against_per_match - rolling_xg_against_per_match
```

**Thresholds (per match, +- 0.3):**

| Signal | Condition | Meaning | Actionable |
|--------|-----------|---------|------------|
| Hot attack | `attack_delta >= 0.3` | Creating more than usual | Own their attackers |
| Cold attack | `attack_delta <= -0.3` | Creating less | Target with defenders (clean sheets) |
| Leaky defence | `defence_delta <= -0.3` | Conceding more | Target with attackers/midfielders |
| Solid defence | `defence_delta >= -0.3` | Conceding less | Avoid targeting |
| Stable | Between thresholds | No significant change | N/A |

To compute, you need to:
1. Get season per-match xG averages (from xG Differential query above, divide totals by matches)
2. Get last 3 fixtures for each team and aggregate xG from player stats for those fixtures
3. Compare the two

### Weighted FDR

Adjusts raw Fixture Difficulty Rating using team strength matchup:

```
weighted_fdr = base_fdr * venue_multiplier * strength_adjustment
```

Where:
- `venue_multiplier`: **0.92** (home) or **1.08** (away)
- `defence_factor = (opponent_attack_strength - team_defence_strength) / 1000`
- `attack_factor = (team_attack_strength - opponent_defence_strength) / 1000`
- `strength_adjustment = 1 + defence_factor - attack_factor * 0.5`
- Clamped to **1.0 - 5.0**, rounded to 1 decimal

**Which strength columns to use:**
- Home team: `strength_attack_home`, `strength_defence_home`; opponent uses `_away` variants
- Away team: `strength_attack_away`, `strength_defence_away`; opponent uses `_home` variants

```sql
-- Upcoming fixtures with weighted FDR for a team
SELECT f.id, f.gameweek_id, f.kickoff_time,
  CASE WHEN f.home_team_id = {TEAM_ID} THEN 1 ELSE 0 END AS is_home,
  CASE WHEN f.home_team_id = {TEAM_ID} THEN at.short_name ELSE ht.short_name END AS opponent,
  CASE WHEN f.home_team_id = {TEAM_ID} THEN f.home_difficulty ELSE f.away_difficulty END AS base_fdr,
  -- Compute weighted FDR inline
  ROUND(MIN(5.0, MAX(1.0,
    (CASE WHEN f.home_team_id = {TEAM_ID} THEN f.home_difficulty ELSE f.away_difficulty END)
    * (CASE WHEN f.home_team_id = {TEAM_ID} THEN 0.92 ELSE 1.08 END)
    * (1.0
      + (CASE WHEN f.home_team_id = {TEAM_ID}
          THEN (at.strength_attack_away - ht.strength_defence_home) ELSE (ht.strength_attack_home - at.strength_defence_away) END) / 1000.0
      - (CASE WHEN f.home_team_id = {TEAM_ID}
          THEN (ht.strength_attack_home - at.strength_defence_away) ELSE (at.strength_attack_away - ht.strength_defence_home) END) * 0.5 / 1000.0
    )
  )), 1) AS weighted_fdr
FROM fixtures f
JOIN teams ht ON f.home_team_id = ht.id
JOIN teams at ON f.away_team_id = at.id
WHERE (f.home_team_id = {TEAM_ID} OR f.away_team_id = {TEAM_ID})
  AND f.finished = 0
ORDER BY f.gameweek_id
LIMIT 6;
```

**FDR Labels:**
| Range | Label |
|-------|-------|
| <= 1.5 | Very Easy |
| <= 2.5 | Easy |
| <= 3.5 | Medium |
| <= 4.5 | Hard |
| > 4.5 | Very Hard |

---

## 3. Decision Frameworks

### Captain Pick

Rank candidates by fixture-adjusted projected points:

```
captain_score = projected_points * (6 - opponent_weighted_fdr) / 5
```

Present the top 3 options with:
- Projected points
- Opponent + venue (H/A) + weighted FDR
- Recent form (last 3 GW points)
- Reasoning

### Transfer Suggestions

1. Filter targets: same position as outgoing player, affordable within budget
2. Compute: `projected_gain = target.projected - current.projected`
3. Only suggest if gain > 0
4. Sort by projected gain descending, return top 5 per transfer slot

**Reason tiers** (check in order, use first match):
- **Form-based**: when target's `recent_avg > current * 1.3` — "{name} is in better recent form ({X} vs {Y} pts/game)"
- **Value-based**: when target's `projected_value > current * 1.2` — "{name} offers better value ({X} vs {Y} pts/m)"
- **Points-based**: default — "{name} has higher projected points ({X} vs {Y})"

### Rotation Pairs

Find two budget players at the same position with complementary home/away schedules:

1. Filter candidates: available, position = DEF or GKP
2. Default max price: **GKP <= £4.5m** (45 units), **DEF <= £5.0m** (50 units)
3. Take top 50 by total points
4. For each pair (must be different teams):
   - Match their fixtures by gameweek
   - Count gameweeks with perfect H/A split (one home, one away)
   - `rotation_score = (perfect_rotations / total_gameweeks) * 100`
5. Each GW: recommend the player with lower weighted FDR
6. Sort by rotation score desc, then combined price asc. Return top 10.

### Chip Timing

| Chip | When to Use |
|------|-------------|
| **Bench Boost** | When all 15 squad players have easy fixtures (FDR <= 2) |
| **Triple Captain** | On highest-projected player with FDR 1-2 |
| **Wildcard** | When 5+ squad players have FDR >= 4 over next 5 GWs |
| **Free Hit** | For blank/double gameweeks or fixture pile-ups |

```sql
-- Check chips remaining
SELECT chip_type FROM chip_usage;
-- Available: WILDCARD, FREE_HIT, BENCH_BOOST, TRIPLE_CAPTAIN minus what's already used
```

---

## 4. Common Queries

### Top Players by Form

```sql
SELECT p.web_name, p.position, t.short_name, p.form, p.total_points,
  ROUND(p.now_cost / 10.0, 1) AS price
FROM players p
JOIN teams t ON p.team_id = t.id
WHERE p.status = 'a'
ORDER BY p.form DESC
LIMIT 15;
```

### Best Value Players

```sql
SELECT p.web_name, p.position, t.short_name, p.total_points,
  ROUND(p.now_cost / 10.0, 1) AS price,
  ROUND(p.total_points * 10.0 / p.now_cost, 2) AS vapm
FROM players p
JOIN teams t ON p.team_id = t.id
WHERE p.status = 'a' AND p.minutes > 500
ORDER BY vapm DESC
LIMIT 15;
```

### Budget Picks by Position

```sql
SELECT p.web_name, t.short_name, p.form, p.total_points,
  ROUND(p.now_cost / 10.0, 1) AS price,
  ROUND(p.total_points * 10.0 / p.now_cost, 2) AS vapm
FROM players p
JOIN teams t ON p.team_id = t.id
WHERE p.position = '{POSITION}' AND p.status = 'a'
  AND p.now_cost <= {MAX_COST}  -- e.g., 60 for £6.0m
ORDER BY vapm DESC
LIMIT 10;
```

### Player Match History

Requires `sync.sh player <id>` first:

```sql
SELECT pgs.gameweek_id AS gw, t.short_name AS opponent,
  CASE WHEN pgs.was_home THEN 'H' ELSE 'A' END AS venue,
  pgs.total_points AS pts, pgs.minutes AS mins,
  pgs.goals AS g, pgs.assists AS a, pgs.bonus AS bns,
  ROUND(pgs.expected_goals, 2) AS xg,
  ROUND(pgs.expected_assists, 2) AS xa
FROM player_gameweek_stats pgs
JOIN teams t ON pgs.opponent_team_id = t.id
WHERE pgs.player_id = {PLAYER_ID}
ORDER BY pgs.gameweek_id DESC;
```

### Differential Picks (Low Ownership, High Form)

```sql
SELECT p.web_name, p.position, t.short_name, p.form, p.selected_by_percent,
  ROUND(p.now_cost / 10.0, 1) AS price
FROM players p
JOIN teams t ON p.team_id = t.id
WHERE p.status = 'a' AND p.form >= 5.0 AND p.selected_by_percent < 10.0
ORDER BY p.form DESC;
```
