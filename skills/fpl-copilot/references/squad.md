# FPL Squad Management

Squads are stored as markdown files in `~/.fplcopilot/squads/` — one file per squad.

---

## 1. Squad File Format

Each squad is a markdown file with YAML frontmatter and structured tables:

```markdown
---
name: MyFplTeam
owner: me
updated: 2026-04-13
gameweek: 32
formation: 3-5-2
---

## Starting XI

| # | Pos | Player | Team | Role |
|---|-----|--------|------|------|
| 1 | GKP | Mamardashvili | LIV | |
| 2 | DEF | Saliba | ARS | |
| 3 | DEF | Virgil | LIV | |
| 4 | DEF | Van Hecke | BHA | |
| 5 | MID | Mbeumo | MUN | |
| 6 | MID | Semenyo | MCI | |
| 7 | MID | Cunha | MUN | |
| 8 | MID | Szoboszlai | LIV | VC |
| 9 | MID | Wilson | FUL | |
| 10 | FWD | Thiago | BRE | C |
| 11 | FWD | Haaland | MCI | |

## Bench

| # | Pos | Player | Team |
|---|-----|--------|------|
| 12 | GKP | Donnarumma | MCI |
| 13 | DEF | Senesi | BOU |
| 14 | FWD | Kroupi.Jr | BOU |
| 15 | MID | Solomon | TOT |

## Chips Used

- (none)

## Transfer Log

| GW | Out | In | Date |
|----|-----|----|------|

## Notes

- Free-form notes, strategy context, things to remember across sessions
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Squad/team name as shown in FPL app |
| `owner` | Yes | Who owns this squad: `me`, a friend's name, or `draft` for planning |
| `updated` | Yes | Date of last update (YYYY-MM-DD) |
| `gameweek` | Yes | Gameweek this squad state reflects |
| `formation` | Yes | Current formation (e.g., `3-5-2`, `4-4-2`) |

### Table Columns

- **#**: Squad position (1-11 starting, 12-15 bench)
- **Pos**: GKP, DEF, MID, FWD
- **Player**: `web_name` from FPL data (must match exactly for lookups)
- **Team**: Short name (ARS, LIV, MCI, etc.)
- **Role**: `C` (captain), `VC` (vice-captain), or blank

### File Naming

Use kebab-case derived from the squad name:
- "MyFplTeam" → `my-fpl-team.md`
- "Dave's Team" → `daves-team.md`
- "Wildcard Draft" → `wildcard-draft.md`

---

## 2. Proactive Persistence Rules

The agent MUST follow these rules — squad persistence is not optional:

### When to Save

| Trigger | Action |
|---------|--------|
| User shares a squad (screenshot, text, list) | Create a new squad file. Ask for a name if unclear. |
| User makes a transfer | Update Starting XI / Bench tables + add to Transfer Log |
| User changes captain or VC | Update the Role column |
| User uses a chip | Add to Chips Used section |
| User changes formation | Update the tables + frontmatter `formation` |
| Strategy analysis completed | Append key findings to Notes section |
| User discusses a friend's squad | Create a separate squad file with `owner: <friend's name>` |

### When to Load

| Trigger | Action |
|---------|--------|
| User says "my squad/team" | List files in `~/.fplcopilot/squads/`, load the one with `owner: me` (or ask if multiple) |
| User names a specific squad | Load that squad file |
| User asks for analysis/advice | Load relevant squad file to provide personalized recommendations |
| Conversation starts with FPL context | Check for existing squads proactively |

### Always Update

After any squad modification:
1. Update the relevant table (Starting XI, Bench, Chips, Transfer Log)
2. Update `updated` date in frontmatter
3. Update `gameweek` if it has changed
4. Write the file back

---

## 3. Multi-Squad Support

Users may track multiple squads:

- **Their own team**: `owner: me` — primary squad for personalized advice
- **Friends' teams**: `owner: Dave` — for comparison or helping friends
- **Draft plans**: `owner: draft` — hypothetical squads for planning (wildcard, free hit)

When multiple squad files exist and the user says "my squad", prefer the file with `owner: me`. If multiple `owner: me` files exist, list them and ask which one.

---

## 4. Squad Rules

These rules apply when validating or building squads:

| Rule | Constraint |
|------|-----------|
| Squad size | Exactly 15 players: 2 GKP, 5 DEF, 5 MID, 3 FWD |
| Starting XI | 11 players: exactly 1 GKP, 3+ DEF, 2+ MID, 1+ FWD |
| Max per team | 3 players from any one Premier League team |
| Budget | Total `now_cost` <= 1000 (= £100.0m) |
| Captain | Exactly 1 `C` + 1 `VC`, both from Starting XI |
| Chips | Each usable once per season: WILDCARD, FREE_HIT, BENCH_BOOST, TRIPLE_CAPTAIN |

### Valid Formations

Any formation with exactly 1 GKP and at least 3 DEF, 2 MID, 1 FWD:
- 3-4-3, 3-5-2, 4-3-3, 4-4-2, 4-5-1, 5-2-3, 5-3-2, 5-4-1

### Validation

Before saving a squad, verify against FPL data:

```sql
-- Check position composition
SELECT position, COUNT(*) FROM players
WHERE web_name IN ('Player1', 'Player2', ...) COLLATE NOCASE
GROUP BY position;

-- Check max 3 per team
SELECT team_id, COUNT(*) FROM players
WHERE web_name IN (...) COLLATE NOCASE
GROUP BY team_id HAVING COUNT(*) > 3;

-- Check budget
SELECT SUM(now_cost) FROM players
WHERE web_name IN (...) COLLATE NOCASE;
```

---

## 5. Operations

### Make Transfer

1. Validate: same position, affordable, max-3-per-team after swap
2. Update Starting XI or Bench table: replace the player
3. Add entry to Transfer Log table
4. Update frontmatter `updated` date

### Set Captain / Vice-Captain

1. Remove existing `C` or `VC` from Role column
2. Set new `C` or `VC` (must be in Starting XI)
3. Save file

### Use Chip

1. Check Chips Used section — must not already be used
2. Add to Chips Used: `- BENCH_BOOST (GW33)`
3. Save file

### Change Formation

1. Move players between Starting XI and Bench
2. Validate new formation (1 GKP, 3+ DEF, 2+ MID, 1+ FWD)
3. Update frontmatter `formation`
4. Renumber squad positions
5. Save file

---

## 6. Score Calculation

### Captain Multiplier

- Captain: **2x** points (or **3x** with Triple Captain chip)
- If captain has 0 minutes, vice-captain gets the multiplier

### Auto-Substitution

When a starter has 0 minutes, substitute from bench in order (#12, #13, #14, #15):

1. Find first bench player who played (minutes > 0)
2. Verify substitution maintains valid formation (1 GKP, 3+ DEF, 2+ MID, 1+ FWD)
3. If valid, make the sub. If not, try next bench player.

### Bench Boost

When active, all bench players' points count (no auto-sub needed).

---

## 7. Squad Analysis

When analyzing a squad, combine the squad file with FPL data:

### Squad Health

Check each player's status and form against the `players` table:

```sql
SELECT p.web_name, p.position, t.short_name, p.form, p.status,
  p.chance_of_playing, p.news
FROM players p
JOIN teams t ON p.team_id = t.id
WHERE p.web_name IN ({squad_player_names}) COLLATE NOCASE
  AND (p.status != 'a' OR p.form < 2.0)
ORDER BY p.form;
```

### Fixture Outlook

Get upcoming fixtures for all squad players' teams — see `analysis.md` for weighted FDR queries.

### Transfer Suggestions

Compare squad players' projected points with available alternatives — see `analysis.md` for the transfer suggestion framework.
