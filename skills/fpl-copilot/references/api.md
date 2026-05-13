# FPL API Reference

Base URL: `https://fantasy.premierleague.com/api`

No authentication required. All endpoints are public and free.

## Endpoints

### GET /bootstrap-static/

Returns all core FPL data in a single response.

**Response:**
```json
{
  "events": [...],         // Gameweeks (38 items)
  "teams": [...],          // Premier League teams (20 items)
  "elements": [...],       // Players (~600 items)
  "element_types": [...]   // Position definitions (4 items)
}
```

#### `events[]` (Gameweeks)

| Field | Type | Maps To |
|-------|------|---------|
| `id` | int | `gameweeks.id` |
| `name` | string | `gameweeks.name` |
| `deadline_time` | string (ISO) | `gameweeks.deadline_time` |
| `finished` | bool | `gameweeks.finished` |
| `is_current` | bool | `gameweeks.is_current` |
| `is_next` | bool | `gameweeks.is_next` |
| `average_entry_score` | int\|null | `gameweeks.average_score` |
| `highest_score` | int\|null | `gameweeks.highest_score` |

#### `teams[]` (Premier League Teams)

| Field | Type | Maps To |
|-------|------|---------|
| `id` | int | `teams.id` (1-20) |
| `name` | string | `teams.name` |
| `short_name` | string | `teams.short_name` |
| `code` | int | `teams.code` |
| `strength` | int | `teams.strength` |
| `strength_attack_home` | int | `teams.strength_attack_home` |
| `strength_attack_away` | int | `teams.strength_attack_away` |
| `strength_defence_home` | int | `teams.strength_defence_home` |
| `strength_defence_away` | int | `teams.strength_defence_away` |

#### `elements[]` (Players)

| Field | Type | Maps To |
|-------|------|---------|
| `id` | int | `players.id` |
| `code` | int | `players.fpl_code` |
| `first_name` | string | `players.first_name` |
| `second_name` | string | `players.last_name` |
| `web_name` | string | `players.web_name` |
| `element_type` | int | `players.position` (1→GKP, 2→DEF, 3→MID, 4→FWD) |
| `team` | int | `players.team_id` |
| `now_cost` | int | `players.now_cost` (0.1m units, 130 = £13.0m) |
| `total_points` | int | `players.total_points` |
| `points_per_game` | string | `players.points_per_game` (cast to float) |
| `form` | string | `players.form` (cast to float, last 3 GW avg) |
| `selected_by_percent` | string | `players.selected_by_percent` (cast to float) |
| `minutes` | int | `players.minutes` |
| `goals_scored` | int | `players.goals` |
| `assists` | int | `players.assists` |
| `clean_sheets` | int | `players.clean_sheets` |
| `goals_conceded` | int | `players.goals_conceded` |
| `own_goals` | int | `players.own_goals` |
| `penalties_saved` | int | `players.penalties_saved` |
| `penalties_missed` | int | `players.penalties_missed` |
| `yellow_cards` | int | `players.yellow_cards` |
| `red_cards` | int | `players.red_cards` |
| `saves` | int | `players.saves` |
| `bonus` | int | `players.bonus` |
| `expected_goals` | string | `players.expected_goals` (cast to float) |
| `expected_assists` | string | `players.expected_assists` (cast to float) |
| `expected_goal_involvements` | string | `players.expected_goal_involvements` (cast to float) |
| `expected_goals_conceded` | string | `players.expected_goals_conceded` (cast to float) |
| `ict_index` | string | `players.ict_index` (cast to float) |
| `influence` | string | `players.influence` (cast to float) |
| `creativity` | string | `players.creativity` (cast to float) |
| `threat` | string | `players.threat` (cast to float) |
| `status` | string | `players.status` (a/d/i/s/u) |
| `chance_of_playing_next_round` | int\|null | `players.chance_of_playing` |
| `news` | string | `players.news` |

#### `element_types[]` (Positions)

| id | singular_name | short |
|----|---------------|-------|
| 1 | Goalkeeper | GKP |
| 2 | Defender | DEF |
| 3 | Midfielder | MID |
| 4 | Forward | FWD |

---

### GET /fixtures/

Returns all 380 fixtures for the season.

**Response:** Array of fixture objects.

| Field | Type | Maps To |
|-------|------|---------|
| `id` | int | `fixtures.id` |
| `event` | int\|null | `fixtures.gameweek_id` |
| `team_h` | int | `fixtures.home_team_id` |
| `team_a` | int | `fixtures.away_team_id` |
| `kickoff_time` | string\|null | `fixtures.kickoff_time` |
| `finished` | bool | `fixtures.finished` |
| `team_h_score` | int\|null | `fixtures.home_score` |
| `team_a_score` | int\|null | `fixtures.away_score` |
| `team_h_difficulty` | int | `fixtures.home_difficulty` (FDR 1-5) |
| `team_a_difficulty` | int | `fixtures.away_difficulty` (FDR 1-5) |

---

### GET /element-summary/{player_id}/

Returns detailed per-gameweek history for a single player.

**Response:**
```json
{
  "fixtures": [...],       // Upcoming fixtures for this player
  "history": [...],        // Past gameweek stats (what we sync)
  "history_past": [...]    // Previous season summaries
}
```

#### `history[]` (Per-Gameweek Stats)

| Field | Type | Maps To |
|-------|------|---------|
| `element` | int | `player_gameweek_stats.player_id` |
| `round` | int | `player_gameweek_stats.gameweek_id` |
| `fixture` | int | `player_gameweek_stats.fixture_id` |
| `opponent_team` | int | `player_gameweek_stats.opponent_team_id` |
| `was_home` | bool | `player_gameweek_stats.was_home` |
| `total_points` | int | `player_gameweek_stats.total_points` |
| `minutes` | int | `player_gameweek_stats.minutes` |
| `goals_scored` | int | `player_gameweek_stats.goals` |
| `assists` | int | `player_gameweek_stats.assists` |
| `clean_sheets` | int | `player_gameweek_stats.clean_sheets` |
| `goals_conceded` | int | `player_gameweek_stats.goals_conceded` |
| `own_goals` | int | `player_gameweek_stats.own_goals` |
| `penalties_saved` | int | `player_gameweek_stats.penalties_saved` |
| `penalties_missed` | int | `player_gameweek_stats.penalties_missed` |
| `yellow_cards` | int | `player_gameweek_stats.yellow_cards` |
| `red_cards` | int | `player_gameweek_stats.red_cards` |
| `saves` | int | `player_gameweek_stats.saves` |
| `bonus` | int | `player_gameweek_stats.bonus` |
| `bps` | int | `player_gameweek_stats.bps` |
| `expected_goals` | string | `player_gameweek_stats.expected_goals` (cast) |
| `expected_assists` | string | `player_gameweek_stats.expected_assists` (cast) |
| `expected_goal_involvements` | string | `player_gameweek_stats.expected_goal_involvements` (cast) |
| `expected_goals_conceded` | string | `player_gameweek_stats.expected_goals_conceded` (cast) |
| `ict_index` | string | `player_gameweek_stats.ict_index` (cast) |
| `influence` | string | `player_gameweek_stats.influence` (cast) |
| `creativity` | string | `player_gameweek_stats.creativity` (cast) |
| `threat` | string | `player_gameweek_stats.threat` (cast) |
| `value` | int | `player_gameweek_stats.value` (0.1m units) |
| `transfers_balance` | int | (not stored) |
| `selected` | int | `player_gameweek_stats.selected` |
| `transfers_in` | int | `player_gameweek_stats.transfers_in` |
| `transfers_out` | int | `player_gameweek_stats.transfers_out` |

---

## Rate Limiting

The API is public with no documented rate limits, but:
- Space `/element-summary/` calls by at least 100ms
- Never batch-fetch all ~600 players unless the user explicitly requests it
- Bootstrap and fixtures endpoints handle full-season data in one call — no batching needed
