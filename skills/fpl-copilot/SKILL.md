---
name: fpl-copilot
version: 1.2.0
description: "Fantasy Premier League copilot: syncs live FPL data, analyzes players/teams/fixtures, manages your fantasy squad, and generates self-contained HTML reports for squads, fixtures, transfers, captain picks, and gameweek strategy. Use when the user asks about FPL, player stats, transfer advice, captain picks, fixture difficulty, gameweek strategy, or squad management."
metadata:
  requires:
    bins: ["curl", "jq", "sqlite3"]
---

# FPL Copilot

Fantasy Premier League data sync, analysis, and squad management.

- **FPL data**: SQLite database at `~/.fplcopilot/fplcopilot.db`
- **User squads**: Markdown files in `~/.fplcopilot/squads/`

## When to Use

Activate this skill when the user mentions:
- FPL, Fantasy Premier League, fantasy football (UK context)
- Player stats, form, price, points, xG, xA, ICT, ownership
- Transfer advice, who to buy/sell, budget options
- Captain pick, vice-captain, chip timing
- Fixture difficulty, FDR, schedule, easy/hard fixtures
- Gameweek deadline, scores, standings, averages
- Squad management, team composition, formation
- Team analysis: momentum, xG differential, leaky defences, hot attacks
- Rotation pairs, differential picks, value picks

## Quick Start

### 1. Check Data Freshness

```bash
sqlite3 ~/.fplcopilot/fplcopilot.db "SELECT * FROM sync_metadata;"
```

If the database doesn't exist or data is stale, sync first.

### 2. Sync Data

```bash
SYNC="${CLAUDE_PLUGIN_ROOT}/skills/fpl-copilot/references/sync.sh"

# First time or daily refresh
$SYNC bootstrap              # Teams, gameweeks, ~600 players (~5s)
$SYNC fixtures               # All 380 fixtures (~2s)

# On demand — single player's match history
$SYNC player 328             # e.g., Salah's detailed GW-by-GW stats

# Batch — all players' histories (slow, ~60s, rate-limited)
$SYNC player-stats

# Everything at once
$SYNC all

# Bypass freshness checks
$SYNC bootstrap --force
```

### 3. Query and Analyze

```bash
# All queries go through sqlite3
sqlite3 ~/.fplcopilot/fplcopilot.db "SELECT web_name, position, form, total_points, now_cost FROM players ORDER BY form DESC LIMIT 10;"
```

Read `references/analysis.md` for formulas and example SQL queries.
Read `references/squad.md` for squad management, persistence format, and multi-squad support.

## Output Format: HTML vs Markdown

Many FPL outputs are inherently spatial or color-coded — formation, FDR matrix, transfer comparison. For those, generate a self-contained **HTML report** instead of a markdown table. For quick lookups and one-shot answers, stay in markdown.

### When to output HTML

| Output type | Format | Template |
|---|---|---|
| Squad view (formation, bench, totals) | HTML | `templates/squad-view.html` |
| Fixture difficulty matrix (teams × next N GWs) | HTML | `templates/fixture-matrix.html` |
| Transfer comparison (out → in, deltas) | HTML | `templates/transfer-comparison.html` |
| Captain ranking with reasoning | HTML | `templates/captain-ranking.html` |
| Gameweek strategy report (squad + fixtures + recs) | HTML | `templates/gameweek-report.html` |
| Single-stat lookup ("Salah's form?") | markdown | — |
| Short reasoning ("Bench Haaland this week?") | markdown | — |
| Deadline, price changes, one-line answers | markdown | — |
| 3-row SQL result | markdown | — |

Heuristic: if the user will *refer back to it, share it, or scan it visually* → HTML. If they glance and move on → markdown.

### Universal rules for HTML output

1. **Single self-contained `.html` file.** No build step. CSS in `<style>`, JS in `<script>`, SVG inlined.
2. **Vanilla HTML/CSS/JS only.** No Tailwind, no shadcn, no external CDN, no web fonts.
3. **Mobile responsive.** Include `<meta name="viewport" content="width=device-width, initial-scale=1">`. Layout survives a phone viewport.
4. **Save to** `~/.fplcopilot/reports/{YYYY-MM-DD}-{slug}.html`. Create the directory with `mkdir -p` if missing.
5. **Tell the user the path** after saving. On macOS, offer `open <path>` to view in their default browser.
6. **Adapt the template, don't write from scratch.** Read the matching file in `templates/`, replace the placeholder data with real values from SQL, save the result.

**Before generating any HTML report, read `references/html-output.md`** for color tokens, typography, the team-color table, the sortable-table snippet, and the list of anti-patterns to avoid.

## Reference Docs

Read these BEFORE answering questions in their domain:

| Doc | When to Read |
|-----|-------------|
| `references/api.md` | Understanding FPL API endpoints and data structure |
| `references/analysis.md` | Computing metrics (VAPM, projected points, FDR, momentum, etc.) |
| `references/squad.md` | Squad persistence, management, multi-squad, scoring rules |
| `references/schema.sql` | Understanding database tables and columns |
| `references/html-output.md` | Styling rules, color tokens, team colors, anti-patterns for HTML reports |

## Squad Persistence

Squads are stored as markdown files in `~/.fplcopilot/squads/` — one file per squad. This enables multi-squad support (user's own team, friends' teams, draft plans).

**Proactive persistence rules — the agent MUST follow these:**

1. **On squad identification**: When the user shares their squad (screenshot, text, or any format), immediately save it to `~/.fplcopilot/squads/`. Ask for a name if unclear.
2. **On squad changes**: When the user makes a transfer, changes captain, uses a chip, or modifies their squad in any way, update the squad file immediately after confirming the change.
3. **On conversation start**: If the user asks about "my squad" or "my team", check `~/.fplcopilot/squads/` for existing squad files first. List available squads if multiple exist.
4. **On analysis**: After generating a strategy report or analysis, update the squad file's Notes section with key takeaways.
5. **Multi-squad**: Users may discuss multiple squads (their own, friends', draft plans). Each gets its own file. The user can specify which squad by name.
6. **File naming**: Use kebab-case slugs derived from the squad name (e.g., `my-fpl-team.md`, `daves-team.md`, `wildcard-draft.md`).

Read `references/squad.md` for the full markdown format specification.

## Agent Rules

1. **Always check freshness** before answering data questions. If `sync_metadata` shows stale data (bootstrap > 6h, fixtures on match day > 2h), run the sync script first.
2. **Always check for saved squads** when the user asks about "my squad/team". Read `~/.fplcopilot/squads/` before asking the user to re-share.
3. **Never guess player IDs.** Look up by name:
   ```sql
   -- Try exact web_name first, then partial, then full name
   SELECT * FROM players WHERE web_name = 'Salah' COLLATE NOCASE;
   SELECT * FROM players WHERE web_name LIKE '%salah%' COLLATE NOCASE;
   SELECT * FROM players WHERE (first_name || ' ' || last_name) LIKE '%salah%' COLLATE NOCASE;
   ```
4. **Price units**: `now_cost` is in 0.1m units. `130` = £13.0m. Always display as `£X.Xm`.
5. **Position codes**: GKP, DEF, MID, FWD (mapped from API's 1, 2, 3, 4).
6. **Status codes**: `a`=available, `d`=doubtful, `i`=injured, `s`=suspended, `u`=unavailable.
7. **FDR scale**: 1 (very easy) to 5 (very hard).
8. **Normalize by price** when comparing players: value = points / (cost in millions).
9. **Fetch player detail on demand**: Only run `sync.sh player <id>` when the user asks about a specific player's match-by-match performance. Don't batch-fetch unless explicitly needed.
10. **Proactively persist squads**: Always save/update squad files after any squad-related interaction. Never rely on conversation context alone.
11. **Generate HTML for spatial outputs**: Any request that maps to a template in `templates/` — "plan gameweek" / "next gameweek team" → `gameweek-report.html`; "show/view my squad", formation, bench → `squad-view.html`; "compare transfer", out → in → `transfer-comparison.html`; "captain pick" with reasoning → `captain-ranking.html`; fixture run / FDR matrix → `fixture-matrix.html` — MUST produce the HTML file (saved to `~/.fplcopilot/reports/{YYYY-MM-DD}-{slug}.html`) and report the path with an `open <path>` hint on macOS. Markdown is only for one-line / single-stat lookups, short reasoning, deadlines, price changes, or ≤3-row SQL results.
