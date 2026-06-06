# Drafting quality bars (step 7)

Apply when scaffolding a new SKILL.md or editing an existing one. These are the bars reputable authors (Anthropic docs, Jesse Vincent, Simon Willison) converge on.

## Frontmatter
- `name`: gerund form preferred (`translating-posts-to-blogs`), lowercase + hyphens only, no reserved words (`anthropic`, `claude`), ≤ 64 chars.
- `description`: third person; state **what** it does AND **when** to use it AND **exclusions** ("Not for X — use Y"). The exclusion line is the single most valuable defense against mis-triggering. ≤ 1024 chars.

## Body
- Concise — assume Claude is already smart. Only capture what it would not know: conventions, non-obvious procedures, edge cases, project-specific rules. Cut any sentence that explains a concept a capable reader already knows.
- Body < 500 lines. Split overflow into `references/*.md`, linked **one level deep** from SKILL.md (no nested reference chains).
- Match degrees of freedom to task fragility: high-freedom prose for judgment tasks; exact, low-freedom scripts/commands for fragile sequences.
- No all-caps imperatives (`MUST`/`NEVER`) without a reason — they cause over-application.
- No happy-path-only docs — include known failure modes.
- No time-sensitive phrasing — use an "old patterns" section for deprecated info.
- Chinese content follows the repo's `personal-chinese-writing-style` skill.

## Interview before drafting
The transcript shows mechanics, not the *why*. Before writing, ask the user for the taste/judgment/rationale the session cannot reveal. Capture that — it is the actual value.

## Repo integration (for CREATE)
- New skill dir under `skills/<name>/`.
- Run `scripts/sync-marketplace-skills.sh` to register it in `marketplace.json` (never hand-edit `skills[]`).
- Bump the `version` field in `.claude-plugin/marketplace.json`.
