# 01coder Agent Skills

A marketplace of agent skills by VerySmallWoods — content creation, publishing, analytics, and security scanning. Works with Claude Code, Codex, Cursor, Windsurf, and any other coding agent that supports the [skills.sh](https://github.com/mattpocock/skills) format.

## Install

### Universal (Claude Code · Codex · Cursor · Windsurf · ...)

Uses the [skills.sh installer](https://github.com/mattpocock/skills) by Matt Pocock:

```bash
npx skills@latest add sugarforever/01coder-agent-skills
```

Pick the skills you want and the agents to install them on. Done.

### Claude Code (native marketplace)

```bash
/plugin marketplace add sugarforever/01coder-agent-skills
/plugin install 01coder-skills@01coder-agent-skills
```

New skills are picked up automatically on marketplace update — no reinstall needed.

## Available Skills

### Content & Writing

- **personal-chinese-writing-style** — Personal writing-style preferences (punctuation, structure, voice). Reference when writing, translating, or editing content.
- **video-planner** — Plan videos and prepare publishing materials: read-aloud scripts (口播稿) with per-section screen-share cues, plus title, description, tags, and YouTube chapter timestamps for YouTube and Bilibili.
- **cover-image** — Hand-drawn style article cover image generator with 17 style options and 10 composition layouts.
- **tweet-insight** — Read a tweet plus its linked papers / blogs / system cards, then write an original Chinese share-post in your own words.
- **share-reading** — Draft social-media posts to recommend an article, paper, or resource across X, Substack, and 知识星球.
- **promote-post** — Write a teaser tweet for a published article that opens the story instead of summarizing it — the tweet IS the first bite, not a label on the packaging.
- **slides-video** — Orchestrate slide generation + script writing to produce slides-driven narration videos (口播视频), with each slide mapping 1:1 to one voiceover section.
- **subtitle-correction** — Correct speech-recognition errors in `.srt` subtitle files (Chinese and English) while preserving timestamps.

### Publishing

- **publish-x-article** — Publish Markdown articles to the X (Twitter) Articles editor with proper formatting. Inspired by [wshuyi/x-article-publisher-skill](https://github.com/wshuyi/x-article-publisher-skill).
- **publish-substack-article** — Publish Markdown articles to Substack as drafts, with Markdown-to-HTML conversion.
- **publish-zsxq-article** — Publish Markdown articles to Zsxq (知识星球) as drafts.

### Domain-Specific

- **fpl-copilot** — Fantasy Premier League copilot. Syncs live FPL data into local SQLite, analyzes players/teams/fixtures, generates self-contained HTML reports for gameweek strategy, captain picks, fixture matrices, and transfer comparisons.

### Security Scanning

- **nextjs-security-scan** — Security vulnerability scanner for Next.js and TypeScript/JavaScript projects. OWASP Top 10, XSS, injection, secret scanning, dependency CVEs.
- **python-security-scan** — Security vulnerability scanner for Python projects. Framework-aware checks for Flask, Django, and FastAPI.

### Utilities

- **codex-cli** — Delegate one-off tasks to OpenAI Codex CLI, including coding reviews, implementation passes, and image generation with proactive image path discovery.
- **diagram-to-image** — Convert Mermaid diagrams and Markdown tables to PNG / SVG images for platforms that don't support rich formatting.
- **interactive-input** — Embed interactive UI components (multiple choice, forms, surveys) in chat responses on compatible clients.

#### codex-cli Development Direction

The `codex-cli` skill is intended to let other agents, such as Claude Code or OpenClaw, deliberately consult OpenAI Codex CLI for scoped one-off work. It should behave like a bridge workflow, not a replacement for the host agent: first verify that `codex` is installed, delegate a clearly framed task through `codex exec`, then inspect and report the concrete result.

When improving this skill, keep it focused on practical Codex CLI operation:

- Prefer non-interactive `codex exec` workflows over interactive sessions.
- Shape delegated prompts with Codex best-practices sections: `Goal`, `Context`, `Constraints`, and `Done when`.
- Use `read-only` for planning, review, critique, and image generation unless the user explicitly wants Codex to edit files.
- For implementation tasks, encourage plan-first delegation before write-mode execution.
- For image generation, always locate the generated file under `$CODEX_HOME/generated_images/<session-id>/` or `~/.codex/generated_images/<session-id>/`, verify dimensions when an aspect ratio was requested, and report the path proactively.
- Do not claim a specific image backend model unless Codex output, logs, or metadata prove it.
- Do not trust Codex's final message alone when file changes matter; inspect Git status, diffs, or output files.

Future additions should be small and evidence-oriented: better session-id extraction, safer output parsing, known CLI flag changes, and stronger image/file discovery are aligned with the skill. Broad Codex product documentation, general prompt engineering, or host-agent-specific behavior should stay out unless it directly improves this delegation workflow.

### Integrations

- **add-feishu** — Add Feishu (飞书 / Lark) as an agent channel via WebSocket long connection. No public URL required.

## Creating a New Skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: When to trigger this skill. Be specific about trigger phrases — include Chinese and English if applicable.
   ---
   ```
2. Run `./scripts/sync-marketplace-skills.sh` to regenerate the `skills[]` array in `.claude-plugin/marketplace.json`, then bump the `version` manually.
3. (Optional) Add `references/`, `scripts/`, `assets/`, or `templates/` directories alongside `SKILL.md` for domain knowledge, automation, or report templates.

See [CLAUDE.md](CLAUDE.md) for the full convention.

## Acknowledgements

- The [skills.sh installer](https://github.com/mattpocock/skills) by Matt Pocock — the cross-agent installer used in the universal install path above.
- **publish-x-article** is inspired by and based on [wshuyi/x-article-publisher-skill](https://github.com/wshuyi/x-article-publisher-skill).

## Contributing

Pull requests welcome — new skills or improvements to existing ones. Please follow the structure described in [CLAUDE.md](CLAUDE.md).

## License

[MIT](LICENSE)
