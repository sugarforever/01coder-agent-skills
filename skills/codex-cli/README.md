# Codex CLI

Delegate a task from one agent environment (Claude Code, OpenClaw, or similar) to the **OpenAI Codex CLI**. Use it to consult Codex for a code review, hand off an implementation pass, run research, or generate an image — all through the non-interactive `codex exec` interface.

## When it triggers

When the user asks this agent to talk to Codex, consult Codex, get a second opinion from Codex, delegate a coding/review/research task to Codex CLI, or ask Codex to generate an image.

## Prerequisites

Codex CLI must be installed and authenticated in the environment. The skill checks first:

```bash
command -v codex
codex --version
codex exec --help
```

If `codex` is missing, the skill tells the user it's unavailable and stops — it never fabricates a Codex response. Because the CLI changes over time, `codex exec --help` is treated as the source of truth for available flags.

## What it does

| Capability | How |
|------------|-----|
| One-off delegation | `codex exec -C "$PWD" -s read-only "..."` |
| File-editing task | `codex exec -C "$PWD" -s workspace-write "..."` |
| Capture output to file | `-o /tmp/codex-last-message.md` |
| Machine-readable events | `--json` |
| Long prompts | pipe via stdin: `codex exec - < prompt.txt` |
| Resume a session | `codex exec resume <session-id> "..."` |
| Image input | attach with `-i`: `codex exec -i a.png,b.png "compare these"` |
| File input | read from `-C` workspace, or pipe text via stdin |
| Image generation | `codex exec "Generate ... 16:9"` + locating the output file |

For non-trivial work it shapes the delegated prompt with Codex's recommended structure (`Goal / Context / Constraints / Done when:`) and, for complex implementation, asks Codex for a `read-only` plan first before running a separate write pass.

### Image and file input note

Codex can't browse files on its own — images must be attached explicitly with `-i`/`--image` (single, comma-separated, or a repeated flag), paired with a text instruction. For non-image files, the skill points Codex at the file via the `-C` workspace or pipes contents through stdin (appended to the prompt as a `<stdin>` block).

### Image generation note

Codex saves generated images under `$CODEX_HOME/generated_images/<session-id>/` (default `~/.codex/...`) and often does **not** print the path. The skill proactively locates the file, verifies dimensions (`sips` on macOS, `file` as fallback), reports the real path, and copies the asset into the project when one was requested — so a project-referenced image never lives only under `$CODEX_HOME`.

## Safety defaults

- Prefer `read-only` for consultation, review, planning, critique, and analysis.
- Use `workspace-write` only when Codex is expected to edit files; avoid `danger-full-access` unless the user explicitly asks in a controlled environment.
- Never pass secrets to Codex without explicit, informed consent.
- Don't claim Codex did work based on its final message alone — inspect the filesystem or git diff when changes matter.

## Structure

```
codex-cli/
├── SKILL.md              # Entry point — full delegation workflow + safety rules
└── agents/
    └── openai.yaml       # Interface metadata (display name, default prompt, invocation policy)
```

## Notes for editing this skill

- This README is for humans. Agents never auto-load it — only `SKILL.md` (its frontmatter at session start, its body when triggered). Anything the agent must act on belongs in `SKILL.md`, not here.
- `agents/openai.yaml` declares `allow_implicit_invocation: true`, so the skill can fire automatically when a request matches its description — keep the `description` trigger phrases accurate.
- After adding or renaming skills, re-sync the catalog with `./scripts/sync-marketplace-skills.sh` from the repo root and bump the `version` in `.claude-plugin/marketplace.json`.
