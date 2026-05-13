-- FPL Copilot SQLite Schema
-- All FPL data + user squad management in a single file database.

-- ============================================
-- FPL Data Tables
-- ============================================

CREATE TABLE IF NOT EXISTS teams (
  id                    INTEGER PRIMARY KEY,  -- FPL team ID (1-20)
  name                  TEXT    NOT NULL,      -- e.g., "Arsenal"
  short_name            TEXT    NOT NULL,      -- e.g., "ARS"
  code                  INTEGER NOT NULL,      -- FPL team code
  strength              INTEGER NOT NULL,      -- Overall strength rating
  strength_attack_home  INTEGER NOT NULL,
  strength_attack_away  INTEGER NOT NULL,
  strength_defence_home INTEGER NOT NULL,
  strength_defence_away INTEGER NOT NULL,
  updated_at            TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS gameweeks (
  id             INTEGER PRIMARY KEY,  -- GW number (1-38)
  name           TEXT    NOT NULL,      -- e.g., "Gameweek 1"
  deadline_time  TEXT    NOT NULL,      -- ISO timestamp
  finished       INTEGER NOT NULL DEFAULT 0,
  is_current     INTEGER NOT NULL DEFAULT 0,
  is_next        INTEGER NOT NULL DEFAULT 0,
  average_score  INTEGER,
  highest_score  INTEGER,
  updated_at     TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS players (
  id                          INTEGER PRIMARY KEY,  -- FPL element ID
  fpl_code                    INTEGER NOT NULL,      -- Stable across seasons
  first_name                  TEXT    NOT NULL,
  last_name                   TEXT    NOT NULL,
  web_name                    TEXT    NOT NULL,       -- Display name (e.g., "Salah")
  position                    TEXT    NOT NULL,       -- GKP, DEF, MID, FWD
  team_id                     INTEGER NOT NULL REFERENCES teams(id),
  now_cost                    INTEGER NOT NULL,       -- Price in 0.1m units (130 = £13.0m)
  total_points                INTEGER NOT NULL DEFAULT 0,
  points_per_game             REAL    NOT NULL DEFAULT 0,
  form                        REAL    NOT NULL DEFAULT 0,
  selected_by_percent         REAL    NOT NULL DEFAULT 0,
  minutes                     INTEGER NOT NULL DEFAULT 0,
  goals                       INTEGER NOT NULL DEFAULT 0,
  assists                     INTEGER NOT NULL DEFAULT 0,
  clean_sheets                INTEGER NOT NULL DEFAULT 0,
  goals_conceded              INTEGER NOT NULL DEFAULT 0,
  own_goals                   INTEGER NOT NULL DEFAULT 0,
  penalties_saved             INTEGER NOT NULL DEFAULT 0,
  penalties_missed            INTEGER NOT NULL DEFAULT 0,
  yellow_cards                INTEGER NOT NULL DEFAULT 0,
  red_cards                   INTEGER NOT NULL DEFAULT 0,
  saves                       INTEGER NOT NULL DEFAULT 0,
  bonus                       INTEGER NOT NULL DEFAULT 0,
  expected_goals              REAL    NOT NULL DEFAULT 0,
  expected_assists            REAL    NOT NULL DEFAULT 0,
  expected_goal_involvements  REAL    NOT NULL DEFAULT 0,
  expected_goals_conceded     REAL    NOT NULL DEFAULT 0,
  ict_index                   REAL    NOT NULL DEFAULT 0,
  influence                   REAL    NOT NULL DEFAULT 0,
  creativity                  REAL    NOT NULL DEFAULT 0,
  threat                      REAL    NOT NULL DEFAULT 0,
  status                      TEXT    NOT NULL DEFAULT 'a',  -- a/d/i/s/u
  chance_of_playing            INTEGER,                       -- 0-100, nullable
  news                        TEXT,                           -- Injury/suspension info
  updated_at                  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_players_team_id  ON players(team_id);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);
CREATE INDEX IF NOT EXISTS idx_players_now_cost ON players(now_cost);

CREATE TABLE IF NOT EXISTS fixtures (
  id              INTEGER PRIMARY KEY,  -- FPL fixture ID
  gameweek_id     INTEGER REFERENCES gameweeks(id),
  home_team_id    INTEGER NOT NULL REFERENCES teams(id),
  away_team_id    INTEGER NOT NULL REFERENCES teams(id),
  kickoff_time    TEXT,                  -- ISO timestamp, nullable
  finished        INTEGER NOT NULL DEFAULT 0,
  home_score      INTEGER,
  away_score      INTEGER,
  home_difficulty INTEGER NOT NULL,      -- FDR 1-5
  away_difficulty INTEGER NOT NULL,      -- FDR 1-5
  updated_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_fixtures_gameweek_id  ON fixtures(gameweek_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_home_team_id ON fixtures(home_team_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_away_team_id ON fixtures(away_team_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_kickoff_time ON fixtures(kickoff_time);

CREATE TABLE IF NOT EXISTS player_gameweek_stats (
  player_id                   INTEGER NOT NULL REFERENCES players(id),
  gameweek_id                 INTEGER NOT NULL REFERENCES gameweeks(id),
  fixture_id                  INTEGER NOT NULL REFERENCES fixtures(id),
  opponent_team_id            INTEGER NOT NULL,
  was_home                    INTEGER NOT NULL,  -- 0 or 1
  total_points                INTEGER NOT NULL DEFAULT 0,
  minutes                     INTEGER NOT NULL DEFAULT 0,
  goals                       INTEGER NOT NULL DEFAULT 0,
  assists                     INTEGER NOT NULL DEFAULT 0,
  clean_sheets                INTEGER NOT NULL DEFAULT 0,
  goals_conceded              INTEGER NOT NULL DEFAULT 0,
  own_goals                   INTEGER NOT NULL DEFAULT 0,
  penalties_saved             INTEGER NOT NULL DEFAULT 0,
  penalties_missed            INTEGER NOT NULL DEFAULT 0,
  yellow_cards                INTEGER NOT NULL DEFAULT 0,
  red_cards                   INTEGER NOT NULL DEFAULT 0,
  saves                       INTEGER NOT NULL DEFAULT 0,
  bonus                       INTEGER NOT NULL DEFAULT 0,
  bps                         INTEGER NOT NULL DEFAULT 0,
  expected_goals              REAL    NOT NULL DEFAULT 0,
  expected_assists            REAL    NOT NULL DEFAULT 0,
  expected_goal_involvements  REAL    NOT NULL DEFAULT 0,
  expected_goals_conceded     REAL    NOT NULL DEFAULT 0,
  ict_index                   REAL    NOT NULL DEFAULT 0,
  influence                   REAL    NOT NULL DEFAULT 0,
  creativity                  REAL    NOT NULL DEFAULT 0,
  threat                      REAL    NOT NULL DEFAULT 0,
  value                       INTEGER NOT NULL,  -- Price at this GW (0.1m units)
  transfers_in                INTEGER NOT NULL DEFAULT 0,
  transfers_out               INTEGER NOT NULL DEFAULT 0,
  selected                    INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (player_id, gameweek_id, fixture_id)
);

CREATE INDEX IF NOT EXISTS idx_pgs_player_id       ON player_gameweek_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_pgs_gameweek_id     ON player_gameweek_stats(gameweek_id);
CREATE INDEX IF NOT EXISTS idx_pgs_fixture_id      ON player_gameweek_stats(fixture_id);
CREATE INDEX IF NOT EXISTS idx_pgs_opponent_team_id ON player_gameweek_stats(opponent_team_id);

-- ============================================
-- Sync Metadata
-- ============================================

CREATE TABLE IF NOT EXISTS sync_metadata (
  id                      TEXT PRIMARY KEY DEFAULT 'singleton',
  last_bootstrap_sync     TEXT,
  last_fixtures_sync      TEXT,
  last_player_stats_sync  TEXT,
  last_synced_gameweek    INTEGER
);

INSERT OR IGNORE INTO sync_metadata (id) VALUES ('singleton');

-- ============================================
-- User squads are stored as markdown files in ~/.fplcopilot/squads/
-- See references/squad.md for the format specification.
-- ============================================
