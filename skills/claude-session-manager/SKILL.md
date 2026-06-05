---
name: claude-session-manager
description: Manage Claude Code session transcripts from local JSONL storage, including listing candidate sessions, exporting full or selected sessions to organized Markdown, inspecting archives, and summarizing tool-call history. Use when the user asks to scan, parse, archive, inspect, recover, summarize, manage, or convert Claude Code sessions, `~/.claude/projects` data, `.jsonl` transcripts, tool-call history, or hard-to-read Claude Code conversation logs.
---

# Claude Session Manager

## Overview

Claude Code stores session transcripts as JSONL files under `~/.claude/projects/<project-key>/<session-id>.jsonl`. Use the bundled manager to list candidates or export sessions into project-organized Markdown transcripts with a digest, timeline, message text, and linked tool-call details.

Default output folder: `~/.claude/session-markdown`. Tell the user before exporting there, and mention any custom output folder they requested.

## Quick Start

Let the user's wording choose the mode when it is clear; otherwise ask them to choose before exporting:

- Full mode: export all matching sessions. Use this for archive, backup, broad search, or "convert all sessions" requests.
- Specific mode: list candidate sessions first, ask the user to pick one, then export only that session.

Run from any directory:

```bash
python3 /path/to/claude-session-manager/scripts/manage_claude_sessions.py
```

Equivalent explicit form:

```bash
python3 /path/to/claude-session-manager/scripts/manage_claude_sessions.py \
  --source ~/.claude/projects \
  --output ~/.claude/session-markdown
```

Useful options:

- `--mode full`: export all matching sessions. This is the default.
- `--mode specific --list-candidates`: print a numbered candidate table and do not export.
- `--mode specific --pick N`: export the Nth candidate from the same filtered candidate list.
- `--project <text>`: only export project folders whose key contains this text.
- `--session <text>`: only export sessions whose id or filename contains this text.
- `--since YYYY-MM-DD`: only export sessions modified on or after this date.
- `--limit N`: export the N most recently modified matching sessions.
- `--include-tool-details-inline`: embed full tool payloads in the main session Markdown instead of sidecar files.

## Specific Mode Candidate Flow

Use this flow when the user wants one session, is unsure which session they need, or asks to inspect recent sessions before converting.

1. Run a candidate list command. Use `--limit 20` by default unless the user asks for a different count.

```bash
python3 /path/to/claude-session-manager/scripts/manage_claude_sessions.py \
  --mode specific \
  --list-candidates \
  --limit 20
```

2. If the user gave a project hint, date, or session id fragment, pass it through the same filters:

```bash
python3 /path/to/claude-session-manager/scripts/manage_claude_sessions.py \
  --mode specific \
  --list-candidates \
  --project my-repo \
  --since 2026-06-01 \
  --limit 20
```

3. Present the numbered candidate rows to the user. The candidate table includes modified time, project key, short session id, cwd, and first user prompt excerpt. These are the selection signals; do not ask the user to inspect raw JSONL paths.
4. After the user chooses a number, rerun with the exact same filters and `--pick N`:

```bash
python3 /path/to/claude-session-manager/scripts/manage_claude_sessions.py \
  --mode specific \
  --pick 3 \
  --limit 20
```

If the user already gives an exact session id or unique fragment, use `--mode specific --session <id-or-fragment> --list-candidates` first when there is any ambiguity. Export with `--pick 1` only when the candidate list has exactly one match.

## Output Layout

The exporter writes:

```text
~/.claude/session-markdown/
├── index.md
└── <project-key>/
    ├── index.md
    ├── <session-id>.md
    └── tool-details/
        └── <session-id>.tools.md
```

Keep the original Claude project key as the folder name. It is stable and avoids guessing at path decoding.

Each session Markdown includes:

- Digest: source path, project key, session id, cwd, timestamps, event/message/tool counts, and first user prompt excerpt.
- Linked tool details file when tool calls or results exist.
- Timeline: user, assistant, system, summary, tool use, and tool result entries in timestamp order.
- Short tool summaries inline, with full JSON or text payloads in the sidecar file by default.

## Workflow

1. Confirm the source folder. Default to `~/.claude/projects`.
2. Ask the user to choose full mode or specific mode if they did not already make the choice.
3. Confirm or announce the output folder. Default to `~/.claude/session-markdown`.
4. For full mode, run the exporter script with any needed filters.
5. For specific mode, list candidates, get the user's chosen number, then export with `--pick`.
6. Report the number of sessions exported, output index path, and any parse warnings.
7. If the user wants a specific session explained, read the generated Markdown first; load the sidecar tool details only when exact tool inputs/results matter.

## Notes

- Treat transcript data as private. It can contain prompts, file contents, command output, secrets accidentally pasted into chat, and tool results.
- Do not delete or modify original `.jsonl` files.
- Prefer sidecar tool details for large sessions. Inline tool payloads can make Markdown hard to search and load.
