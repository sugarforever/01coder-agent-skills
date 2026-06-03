# Personal Chinese Writing Style

Apply the author's personal Chinese writing style when writing, translating, editing, proofreading, polishing, or publishing **Chinese** content — blog posts, articles, subtitles/captions, tweets, threads, newsletters, and social posts.

The skill's job is not to explain the style back to you. It applies the style to the text and runs a final punctuation pass before delivering.

## When it triggers

Any task that produces or edits Chinese prose. It's also invoked by other skills in this marketplace as a final style pass — `video-planner`, `tweet-insight`, `slides-video`, and `share-reading` all hand their generated Chinese text through it.

## What it enforces

Non-negotiable punctuation in Chinese body text:

- **Quotes** — curved `“` `”`, never straight `"` around Chinese prose
- **Dash** — halfwidth ` - ` (one space each side), never `--`, `——`, or `—`
- **Ellipsis** — `......`, never `……` or `...`
- **Sentence marks** — `，。：；？！、`, never ASCII `, . : ; ? !` between Chinese characters

Plus voice and structure preferences: natural Chinese tech prose over literal translation, no heading numbering, structure carried by the writing rather than fixed templates, and no trust-me filler or empty self-summaries.

Exceptions where these rules don't apply: YAML frontmatter, code blocks, inline code, JSON/config, URLs, file paths, shell commands, exact source quotes, and English-only sentences.

## Structure

```
personal-chinese-writing-style/
├── SKILL.md                          # Entry point — workflow + non-negotiable rules
└── references/                       # Loaded on demand by SKILL.md
    ├── punctuation.md                # Always read for Chinese output
    ├── article-structure.md          # Blog posts, newsletters, long articles, technical writeups
    ├── voice-and-phrasing.md         # Translation, editing, long-form prose
    └── social-media-style.md         # X/Twitter, threads, short social posts
```

`SKILL.md` loads only the reference files a given task needs, keeping context lean.

## Notes for editing this skill

- This README is for humans. Agents never auto-load it — only `SKILL.md` (its frontmatter at session start, its body when triggered) and the `references/` files it explicitly reads. Keep anything the agent must act on inside `SKILL.md` or a referenced file, not here.
- After renaming or adding skills, re-sync the catalog with `./scripts/sync-marketplace-skills.sh` from the repo root and bump the `version` in `.claude-plugin/marketplace.json`.
