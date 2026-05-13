# HTML Output Style Guide

Self-contained HTML reports for FPL data. Calm, typographic, data-dense — like a stats supplement, not a SaaS dashboard.

## Color tokens

Copy these CSS variables into every report's `<style>` block:

```css
:root {
  --pl-purple: #37003c;       /* primary brand */
  --pl-teal: #00ff87;         /* accent */
  --pl-magenta: #e90052;      /* alert / hard fixture */
  --fdr-1: #00ff87;           /* very easy */
  --fdr-2: #91dfb3;
  --fdr-3: #e8e8e8;
  --fdr-4: #ff6b85;
  --fdr-5: #e90052;           /* very hard */
  --bg: #fafafa;
  --surface: #ffffff;
  --text: #1a1a1a;
  --text-muted: #6b6b6b;
  --border: #e5e5e5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0a0a0a;
    --surface: #161616;
    --text: #f0f0f0;
    --text-muted: #9b9b9b;
    --border: #2a2a2a;
  }
}
```

## Typography

```css
body {
  font-family: ui-sans-serif, -apple-system, "Segoe UI", sans-serif;
  font-size: 15px;
  line-height: 1.55;
  max-width: 1100px;
  margin: 2rem auto;
  padding: 0 1.25rem;
  color: var(--text);
  background: var(--bg);
}
h1, h2, h3 {
  font-family: Georgia, "Times New Roman", serif;
  font-weight: 600;
  letter-spacing: -0.01em;
}
h1 { font-size: 1.75rem; margin-bottom: 0.25rem; }
h2 { font-size: 1.25rem; margin-top: 2rem; }
.subtitle { color: var(--text-muted); font-size: 0.9rem; margin-top: 0; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
th, td { padding: 0.5rem 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }
th { font-weight: 600; font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer; user-select: none; }
```

## Team identity

Render each team as a colored dot + 3-letter code. No external assets.

```html
<span class="team-badge" style="--team-color: #c8102e">
  <span class="team-dot"></span>LIV
</span>
```

```css
.team-badge { display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 600; font-size: 0.85rem; }
.team-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--team-color); border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0; }
```

### Team color reference (2025-26 PL season)

Look up actual season-current teams via `SELECT id, short_name, name FROM teams ORDER BY id;`. Use this table to pick colors.

| Code | Team | Color |
|---|---|---|
| ARS | Arsenal | `#ef0107` |
| AVL | Aston Villa | `#95bfe5` |
| BOU | Bournemouth | `#da291c` |
| BRE | Brentford | `#e30613` |
| BHA | Brighton | `#0057b8` |
| BUR | Burnley | `#6c1d45` |
| CHE | Chelsea | `#034694` |
| CRY | Crystal Palace | `#1b458f` |
| EVE | Everton | `#003399` |
| FUL | Fulham | `#000000` |
| LEE | Leeds | `#ffcd00` |
| LIV | Liverpool | `#c8102e` |
| MCI | Man City | `#6cabdd` |
| MUN | Man United | `#da291c` |
| NEW | Newcastle | `#241f20` |
| NFO | Nottm Forest | `#dd0000` |
| SUN | Sunderland | `#eb172b` |
| TOT | Tottenham | `#132257` |
| WHU | West Ham | `#7a263a` |
| WOL | Wolves | `#fdb913` |

If a team isn't in this table, fall back to `#6b6b6b` (neutral gray) and let the 3-letter code carry identification.

## FDR cells

Color the cell background by FDR. Show opponent code + H/A as text.

```html
<td class="fdr-2"><span class="opp">CHE (H)</span></td>
```

```css
.fdr-1 { background: var(--fdr-1); color: #0a4a2c; }
.fdr-2 { background: var(--fdr-2); color: #0a4a2c; }
.fdr-3 { background: var(--fdr-3); color: #1a1a1a; }
.fdr-4 { background: var(--fdr-4); color: #5a1020; }
.fdr-5 { background: var(--fdr-5); color: #ffffff; }
```

## Status indicators

```html
<span class="status status-d" title="Doubtful">D</span>
<span class="status status-i" title="Injured">I</span>
<span class="status status-s" title="Suspended">S</span>
```

```css
.status { display: inline-block; padding: 0 0.35rem; border-radius: 3px; font-size: 0.7rem; font-weight: 700; }
.status-a { background: var(--fdr-1); color: #0a4a2c; }
.status-d { background: #ffd54f; color: #5a3d00; }
.status-i { background: var(--fdr-5); color: white; }
.status-s { background: #1a1a1a; color: white; }
```

## Icons

Inline lucide SVGs. Define once in `<defs>`, reuse with `<use>`.

```html
<svg width="0" height="0" style="display:none">
  <defs>
    <symbol id="i-up" viewBox="0 0 24 24"><path d="M12 19V5M5 12l7-7 7 7" fill="none" stroke="currentColor" stroke-width="2"/></symbol>
    <symbol id="i-down" viewBox="0 0 24 24"><path d="M12 5v14M19 12l-7 7-7-7" fill="none" stroke="currentColor" stroke-width="2"/></symbol>
    <symbol id="i-alert" viewBox="0 0 24 24"><path d="M12 9v4M12 17h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" fill="none" stroke="currentColor" stroke-width="2"/></symbol>
    <symbol id="i-crown" viewBox="0 0 24 24"><path d="M2 17h20l-2-9-5 4-3-8-3 8-5-4z" fill="currentColor"/></symbol>
    <symbol id="i-shirt" viewBox="0 0 24 24"><path d="M4 4l4-2 4 4 4-4 4 2-2 6h-2v10H8V10H6z" fill="currentColor"/></symbol>
  </defs>
</svg>
<svg width="14" height="14" aria-hidden="true"><use href="#i-up"/></svg>
```

## Light interactivity — sortable tables

Drop this in any report with a data table. Click a column header to sort.

```html
<table data-sortable>
  <thead><tr><th data-type="text">Player</th><th data-type="number">Points</th></tr></thead>
  <tbody><!-- rows --></tbody>
</table>

<script>
document.querySelectorAll('table[data-sortable] th').forEach((th, col) => {
  th.addEventListener('click', () => {
    const tbody = th.closest('table').tBodies[0];
    const rows = [...tbody.rows];
    const type = th.dataset.type || 'text';
    const dir = th.dataset.dir === 'asc' ? -1 : 1;
    th.dataset.dir = dir === 1 ? 'asc' : 'desc';
    rows.sort((a, b) => {
      const av = a.cells[col].dataset.sort ?? a.cells[col].textContent.trim();
      const bv = b.cells[col].dataset.sort ?? b.cells[col].textContent.trim();
      return type === 'number' ? (parseFloat(av) - parseFloat(bv)) * dir : av.localeCompare(bv) * dir;
    });
    rows.forEach(r => tbody.appendChild(r));
  });
});
</script>
```

For cells where display text differs from sort value (e.g., "CHE (H)" but sort by FDR=2), use `data-sort` on the `<td>`.

## Collapsible sections

```html
<details>
  <summary>Why this captain pick?</summary>
  <p>Salah has averaged 7.2 ppg over the last 5 GWs, faces a side that's conceded 9 goals in their last 6 matches, and has a 38% ownership floor that limits downside.</p>
</details>
```

```css
details { margin: 0.5rem 0; }
summary { cursor: pointer; font-weight: 600; color: var(--pl-purple); }
details[open] summary { margin-bottom: 0.5rem; }
```

## Anti-patterns — actively avoid

- **Gradient cards per player.** Each player is a row or position node, not a hero card.
- **Glass morphism, blur backgrounds, neumorphism.** Calm and flat.
- **Tailwind / shadcn / any CSS framework.** Pure vanilla.
- **Decorative emoji in headers.** Use SVG icons or nothing.
- **Bouncy or scale-on-hover animations.** Color transitions only.
- **Four shades of purple.** Stick to the tokens above.
- **A "dashboard" feel with 12 KPI cards across the top.** This is a stats report, not a marketing page.
- **External icon CDN, web fonts, image URLs.** Everything inlined.
- **`<div>`-based tables.** Use `<table>`, `<th>`, `<td>` — sortable, semantic, screen-reader-friendly.

## Output mechanics

- **Path**: `~/.fplcopilot/reports/{YYYY-MM-DD}-{slug}.html`
- **Slug**: kebab-case derived from the report subject (e.g. `gw14-strategy`, `salah-vs-haaland`, `wildcard-draft-v2`)
- **Create the directory** if it doesn't exist: `mkdir -p ~/.fplcopilot/reports`
- **After saving**, tell the user the path. On macOS, offer `open <path>`.
