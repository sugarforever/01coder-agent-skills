#!/usr/bin/env bash
# FPL Copilot — Data Sync Script
# Syncs Fantasy Premier League data into a local SQLite database.
#
# Usage:
#   sync.sh bootstrap              # Teams, gameweeks, players
#   sync.sh fixtures               # All fixtures
#   sync.sh player <id>            # Single player's match-by-match history
#   sync.sh player-stats           # All players' histories (~60s)
#   sync.sh all                    # bootstrap + fixtures + player-stats
#
# Options:
#   --force                        # Bypass freshness checks

set -euo pipefail

# ============================================
# Configuration
# ============================================

FPL_API="https://fantasy.premierleague.com/api"
DATA_DIR="${HOME}/.fplcopilot"
DB="${DATA_DIR}/fplcopilot.db"
SCHEMA_DIR="$(cd "$(dirname "$0")" && pwd)"
SCHEMA="${SCHEMA_DIR}/schema.sql"

BOOTSTRAP_TTL=21600   # 6 hours in seconds
RATE_LIMIT_MS=0.1     # 100ms between player API calls

# ============================================
# Helpers
# ============================================

log()  { echo "[FPL Copilot] $*"; }
warn() { echo "[FPL Copilot] WARNING: $*" >&2; }
die()  { echo "[FPL Copilot] ERROR: $*" >&2; exit 1; }

now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

seconds_since() {
  local ts="$1"
  if [ -z "$ts" ] || [ "$ts" = "null" ]; then
    echo 999999
    return
  fi
  local now_epoch ts_epoch
  now_epoch=$(date -u +%s)
  if date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts" +%s >/dev/null 2>&1; then
    ts_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts" +%s 2>/dev/null || echo 0)
  else
    ts_epoch=$(date -d "$ts" +%s 2>/dev/null || echo 0)
  fi
  echo $(( now_epoch - ts_epoch ))
}

sql() { sqlite3 "$DB" "$@"; }

# Import CSV data into a table via INSERT OR REPLACE
# Usage: csv_upsert <table_name> <csv_file> <column_list>
csv_upsert() {
  local table="$1" csvfile="$2" columns="$3"
  local tmptable="_import_${table}"

  # Create a temp table with no constraints, import CSV, then upsert
  sql <<EOSQL
.mode csv
CREATE TEMP TABLE IF NOT EXISTS ${tmptable} AS SELECT ${columns} FROM ${table} LIMIT 0;
DELETE FROM ${tmptable};
.import --skip 1 ${csvfile} ${tmptable}
INSERT OR REPLACE INTO ${table} (${columns}) SELECT ${columns} FROM ${tmptable};
DROP TABLE IF EXISTS ${tmptable};
EOSQL
}

# ============================================
# Init
# ============================================

init_db() {
  mkdir -p "$DATA_DIR"
  if [ ! -f "$DB" ]; then
    log "Creating database at $DB"
  fi
  sql < "$SCHEMA"
}

# ============================================
# JQ Filters (written to temp files to avoid quoting issues)
# ============================================

write_jq_filters() {
  JQ_TEAMS=$(mktemp)
  cat > "$JQ_TEAMS" << 'JQEOF'
def map_pos: if . == 1 then "GKP" elif . == 2 then "DEF" elif . == 3 then "MID" elif . == 4 then "FWD" else "MID" end;
def nn: . // "";
def nz: (. | tonumber) // 0;
def bl: if . then 1 else 0 end;
.teams | [.[] | [.id, .name, .short_name, .code, .strength, .strength_attack_home, .strength_attack_away, .strength_defence_home, .strength_defence_away, $now]] | (["id","name","short_name","code","strength","strength_attack_home","strength_attack_away","strength_defence_home","strength_defence_away","updated_at"] | @csv), (.[] | @csv)
JQEOF

  JQ_GAMEWEEKS=$(mktemp)
  cat > "$JQ_GAMEWEEKS" << 'JQEOF'
def bl: if . then 1 else 0 end;
.events | [.[] | [.id, .name, .deadline_time, (.finished | bl), (.is_current | bl), (.is_next | bl), (.average_entry_score // ""), (.highest_score // ""), $now]] | (["id","name","deadline_time","finished","is_current","is_next","average_score","highest_score","updated_at"] | @csv), (.[] | @csv)
JQEOF

  JQ_PLAYERS=$(mktemp)
  cat > "$JQ_PLAYERS" << 'JQEOF'
def map_pos: if . == 1 then "GKP" elif . == 2 then "DEF" elif . == 3 then "MID" elif . == 4 then "FWD" else "MID" end;
def nz: (. | tonumber) // 0;
def bl: if . then 1 else 0 end;
.elements | [.[] | [
  .id, .code, .first_name, .second_name, .web_name,
  (.element_type | map_pos), .team, .now_cost, .total_points,
  (.points_per_game | nz), (.form | nz), (.selected_by_percent | nz),
  .minutes, .goals_scored, .assists, .clean_sheets, .goals_conceded,
  .own_goals, .penalties_saved, .penalties_missed, .yellow_cards,
  .red_cards, .saves, .bonus,
  (.expected_goals | nz), (.expected_assists | nz),
  (.expected_goal_involvements | nz), (.expected_goals_conceded | nz),
  (.ict_index | nz), (.influence | nz), (.creativity | nz), (.threat | nz),
  .status, (.chance_of_playing_next_round // ""), (.news // ""), $now
]] | (["id","fpl_code","first_name","last_name","web_name","position","team_id","now_cost","total_points","points_per_game","form","selected_by_percent","minutes","goals","assists","clean_sheets","goals_conceded","own_goals","penalties_saved","penalties_missed","yellow_cards","red_cards","saves","bonus","expected_goals","expected_assists","expected_goal_involvements","expected_goals_conceded","ict_index","influence","creativity","threat","status","chance_of_playing","news","updated_at"] | @csv), (.[] | @csv)
JQEOF

  JQ_FIXTURES=$(mktemp)
  cat > "$JQ_FIXTURES" << 'JQEOF'
def bl: if . then 1 else 0 end;
[.[] | [
  .id, (.event // ""), .team_h, .team_a, (.kickoff_time // ""),
  (.finished | bl), (.team_h_score // ""), (.team_a_score // ""),
  .team_h_difficulty, .team_a_difficulty, $now
]] | (["id","gameweek_id","home_team_id","away_team_id","kickoff_time","finished","home_score","away_score","home_difficulty","away_difficulty","updated_at"] | @csv), (.[] | @csv)
JQEOF

  JQ_PLAYER_STATS=$(mktemp)
  cat > "$JQ_PLAYER_STATS" << 'JQEOF'
def nz: (. | tonumber) // 0;
def bl: if . then 1 else 0 end;
.history | [.[] | [
  .element, .round, .fixture, .opponent_team, (.was_home | bl),
  .total_points, .minutes, .goals_scored, .assists, .clean_sheets,
  .goals_conceded, .own_goals, .penalties_saved, .penalties_missed,
  .yellow_cards, .red_cards, .saves, .bonus, .bps,
  (.expected_goals | nz), (.expected_assists | nz),
  (.expected_goal_involvements | nz), (.expected_goals_conceded | nz),
  (.ict_index | nz), (.influence | nz), (.creativity | nz), (.threat | nz),
  .value, .transfers_in, .transfers_out, .selected
]] | (["player_id","gameweek_id","fixture_id","opponent_team_id","was_home","total_points","minutes","goals","assists","clean_sheets","goals_conceded","own_goals","penalties_saved","penalties_missed","yellow_cards","red_cards","saves","bonus","bps","expected_goals","expected_assists","expected_goal_involvements","expected_goals_conceded","ict_index","influence","creativity","threat","value","transfers_in","transfers_out","selected"] | @csv), (.[] | @csv)
JQEOF
}

cleanup_jq_filters() {
  rm -f "$JQ_TEAMS" "$JQ_GAMEWEEKS" "$JQ_PLAYERS" "$JQ_FIXTURES" "$JQ_PLAYER_STATS" 2>/dev/null || true
}

# ============================================
# Bootstrap Sync
# ============================================

sync_bootstrap() {
  local force="${1:-false}"

  if [ "$force" != "true" ]; then
    local last_sync
    last_sync=$(sql "SELECT last_bootstrap_sync FROM sync_metadata WHERE id='singleton';")
    local age
    age=$(seconds_since "$last_sync")
    if [ "$age" -lt "$BOOTSTRAP_TTL" ]; then
      log "Bootstrap data is fresh (synced $(( age / 60 ))m ago). Use --force to override."
      return 0
    fi
  fi

  log "Fetching bootstrap-static from FPL API..."
  local tmpjson tmpcsv
  tmpjson=$(mktemp)

  if ! curl -sf "${FPL_API}/bootstrap-static/" -o "$tmpjson"; then
    rm -f "$tmpjson"
    die "Failed to fetch bootstrap-static"
  fi

  local now
  now=$(now_iso)

  # --- Teams ---
  local team_count
  team_count=$(jq '.teams | length' "$tmpjson")
  log "Syncing $team_count teams..."

  tmpcsv=$(mktemp)
  jq -r --arg now "$now" -f "$JQ_TEAMS" "$tmpjson" > "$tmpcsv"
  csv_upsert "teams" "$tmpcsv" "id,name,short_name,code,strength,strength_attack_home,strength_attack_away,strength_defence_home,strength_defence_away,updated_at"
  rm -f "$tmpcsv"

  # --- Gameweeks ---
  local gw_count
  gw_count=$(jq '.events | length' "$tmpjson")
  log "Syncing $gw_count gameweeks..."

  tmpcsv=$(mktemp)
  jq -r --arg now "$now" -f "$JQ_GAMEWEEKS" "$tmpjson" > "$tmpcsv"
  csv_upsert "gameweeks" "$tmpcsv" "id,name,deadline_time,finished,is_current,is_next,average_score,highest_score,updated_at"
  rm -f "$tmpcsv"

  # --- Players ---
  local player_count
  player_count=$(jq '.elements | length' "$tmpjson")
  log "Syncing $player_count players..."

  tmpcsv=$(mktemp)
  jq -r --arg now "$now" -f "$JQ_PLAYERS" "$tmpjson" > "$tmpcsv"
  csv_upsert "players" "$tmpcsv" "id,fpl_code,first_name,last_name,web_name,position,team_id,now_cost,total_points,points_per_game,form,selected_by_percent,minutes,goals,assists,clean_sheets,goals_conceded,own_goals,penalties_saved,penalties_missed,yellow_cards,red_cards,saves,bonus,expected_goals,expected_assists,expected_goal_involvements,expected_goals_conceded,ict_index,influence,creativity,threat,status,chance_of_playing,news,updated_at"
  rm -f "$tmpcsv"

  rm -f "$tmpjson"

  sql "UPDATE sync_metadata SET last_bootstrap_sync = '$now' WHERE id = 'singleton';"

  log "Bootstrap sync complete: $team_count teams, $gw_count gameweeks, $player_count players"
}

# ============================================
# Fixtures Sync
# ============================================

sync_fixtures() {
  local force="${1:-false}"

  if [ "$force" != "true" ]; then
    local today today_end count
    today=$(date -u +%Y-%m-%dT00:00:00Z)
    today_end=$(date -u +%Y-%m-%dT23:59:59Z)
    count=$(sql "SELECT COUNT(*) FROM fixtures WHERE kickoff_time >= '$today' AND kickoff_time <= '$today_end';" 2>/dev/null || echo "0")
    if [ "$count" -eq 0 ] 2>/dev/null; then
      log "No fixtures today. Use --force to override."
      return 0
    fi
  fi

  log "Fetching fixtures from FPL API..."
  local tmpjson tmpcsv
  tmpjson=$(mktemp)

  if ! curl -sf "${FPL_API}/fixtures/" -o "$tmpjson"; then
    rm -f "$tmpjson"
    die "Failed to fetch fixtures"
  fi

  local now
  now=$(now_iso)

  local fixture_count
  fixture_count=$(jq 'length' "$tmpjson")
  log "Syncing $fixture_count fixtures..."

  tmpcsv=$(mktemp)
  jq -r --arg now "$now" -f "$JQ_FIXTURES" "$tmpjson" > "$tmpcsv"
  csv_upsert "fixtures" "$tmpcsv" "id,gameweek_id,home_team_id,away_team_id,kickoff_time,finished,home_score,away_score,home_difficulty,away_difficulty,updated_at"
  rm -f "$tmpcsv" "$tmpjson"

  sql "UPDATE sync_metadata SET last_fixtures_sync = '$now' WHERE id = 'singleton';"

  log "Fixtures sync complete: $fixture_count fixtures"
}

# ============================================
# Player Stats Sync (single player)
# ============================================

sync_single_player() {
  local player_id="$1"

  local tmpjson tmpcsv
  tmpjson=$(mktemp)

  if ! curl -sf "${FPL_API}/element-summary/${player_id}/" -o "$tmpjson"; then
    rm -f "$tmpjson"
    warn "Failed to fetch element-summary for player $player_id"
    return 1
  fi

  local stat_count
  stat_count=$(jq '.history | length' "$tmpjson")

  if [ "$stat_count" -eq 0 ]; then
    rm -f "$tmpjson"
    return 0
  fi

  tmpcsv=$(mktemp)
  jq -r -f "$JQ_PLAYER_STATS" "$tmpjson" > "$tmpcsv"
  csv_upsert "player_gameweek_stats" "$tmpcsv" "player_id,gameweek_id,fixture_id,opponent_team_id,was_home,total_points,minutes,goals,assists,clean_sheets,goals_conceded,own_goals,penalties_saved,penalties_missed,yellow_cards,red_cards,saves,bonus,bps,expected_goals,expected_assists,expected_goal_involvements,expected_goals_conceded,ict_index,influence,creativity,threat,value,transfers_in,transfers_out,selected"
  rm -f "$tmpcsv" "$tmpjson"

  log "Player $player_id: $stat_count gameweek records synced"
}

# ============================================
# Player Stats Sync (batch)
# ============================================

sync_all_player_stats() {
  local force="${1:-false}"

  if [ "$force" != "true" ]; then
    local last_gw latest_finished
    last_gw=$(sql "SELECT last_synced_gameweek FROM sync_metadata WHERE id='singleton';")
    latest_finished=$(sql "SELECT MAX(id) FROM gameweeks WHERE finished = 1;")

    if [ -z "$latest_finished" ] || [ "$latest_finished" = "" ]; then
      log "No finished gameweeks. Nothing to sync."
      return 0
    fi

    if [ -n "$last_gw" ] && [ "$last_gw" != "" ] && [ "$latest_finished" -le "$last_gw" ] 2>/dev/null; then
      log "No new finished gameweek (last synced: GW$last_gw, latest finished: GW$latest_finished). Use --force to override."
      return 0
    fi

    log "New gameweek detected: GW$latest_finished (last synced: ${last_gw:-none})"
  fi

  local player_ids
  player_ids=$(sql "SELECT id FROM players ORDER BY id;")
  local total
  total=$(echo "$player_ids" | wc -l | tr -d ' ')
  local success=0 fail=0 current=0

  log "Syncing player stats for $total players..."

  while IFS= read -r pid; do
    [ -z "$pid" ] && continue
    current=$(( current + 1 ))
    if sync_single_player "$pid" 2>/dev/null; then
      success=$(( success + 1 ))
    else
      fail=$(( fail + 1 ))
    fi

    if [ $(( current % 50 )) -eq 0 ]; then
      log "Progress: $current/$total ($success synced, $fail failed)"
    fi

    sleep "$RATE_LIMIT_MS"
  done <<< "$player_ids"

  local latest_finished
  latest_finished=$(sql "SELECT MAX(id) FROM gameweeks WHERE finished = 1;")
  local now
  now=$(now_iso)
  sql "UPDATE sync_metadata SET last_player_stats_sync = '$now', last_synced_gameweek = $latest_finished WHERE id = 'singleton';"

  log "Player stats sync complete: $success/$total synced ($fail failed)"
}

# ============================================
# Full Sync
# ============================================

sync_all() {
  log "Starting full sync..."
  sync_bootstrap "true"
  sync_fixtures "true"
  sync_all_player_stats "true"
  log "Full sync complete."
}

# ============================================
# Main
# ============================================

main() {
  local command="${1:-}"
  local force="false"

  for arg in "$@"; do
    if [ "$arg" = "--force" ] || [ "$arg" = "-f" ]; then
      force="true"
    fi
  done

  for cmd in curl jq sqlite3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      die "Required command not found: $cmd"
    fi
  done

  init_db
  write_jq_filters
  trap cleanup_jq_filters EXIT

  case "$command" in
    bootstrap)
      sync_bootstrap "$force"
      ;;
    fixtures)
      sync_fixtures "$force"
      ;;
    player)
      local player_id="${2:-}"
      if [ -z "$player_id" ]; then
        die "Usage: sync.sh player <player_id>"
      fi
      sync_single_player "$player_id"
      ;;
    player-stats)
      sync_all_player_stats "$force"
      ;;
    all)
      sync_all
      ;;
    *)
      echo "FPL Copilot Sync"
      echo ""
      echo "Usage:"
      echo "  sync.sh bootstrap              # Sync teams, gameweeks, players"
      echo "  sync.sh fixtures               # Sync fixtures"
      echo "  sync.sh player <id>            # Sync single player history"
      echo "  sync.sh player-stats           # Sync all player histories"
      echo "  sync.sh all                    # Full sync (everything)"
      echo ""
      echo "Options:"
      echo "  --force                        # Bypass freshness checks"
      exit 1
      ;;
  esac
}

main "$@"
