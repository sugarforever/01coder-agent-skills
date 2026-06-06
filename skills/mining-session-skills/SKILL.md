---
name: mining-session-skills
description: Review one completed Claude Code session and propose a skill to create, update, or reuse so similar work goes faster next time. Use when the user asks to "mine a session for skills", "what skill can be created or updated from the session where I…", "extract a skill from this chat", or to review a past session for reusable workflows. Operates on exported session markdown from claude-session-manager. Not for exporting/converting sessions (use claude-session-manager) and not for writing blogs or TODOs from sessions.
---

# Mining Session Skills

## Overview

Review one completed Claude Code session and answer: is there a skill worth creating or updating so this kind of work goes faster next time? A clean "nothing worth making here" is a valid result.

This skill is the judgment layer on top of `claude-session-manager` (the export/normalization layer). It reads exported markdown, not raw JSONL.

## Preconditions

1. **Inventory = skills loaded in THIS session.** Create-vs-update-vs-reuse is decided against the skills already advertised/loaded in the running session. State this limit in the report ("comparison limited to skills loaded this session"). Run this skill where the relevant skills are loaded.
2. **Mining operates on exported markdown** (default `~/.claude/session-markdown`), produced by `claude-session-manager`. If the target session is not exported yet, export it first (step 1.5).

## Why exported markdown, not raw JSONL

Measured: a real session's raw JSONL was ~1.5M tokens (exceeds the context window); the exported compact body was ~91k tokens (17× smaller) with tool payloads deferred to a sidecar. Raw `grep '"type":"user"'` over JSONL is a trap (tool results are `role:user`). Always read/mine the exported markdown. Raw-JSONL byte grep is acceptable ONLY as a location prefilter (step 1).

## Pipeline

Copy this checklist and track progress:

```
- [ ] 1. Locate the session (keyword search; confirm with user)
- [ ] 1.5 Export it if not already exported
- [ ] 2. Read the compact transcript (pull sidecar only as needed)
- [ ] 2.5 Segment into topic arcs
- [ ] 3. Mine friction signals per arc
- [ ] 4. Apply the worth-it gate
- [ ] 5. Decide create / update / reuse
- [ ] 6. Present the proposal
- [ ] 7. On approval, interview + draft
```

### 1. Locate
Search by the user's description. Prefilter optionally with a raw-JSONL byte grep across `~/.claude/projects` (finds which file mentions a keyword without parsing), and/or grep the exported corpus under `~/.claude/session-markdown`. Skip `<local-command-caveat>` / `<command-*>` wrapper noise — the first-prompt excerpt is often a wrapper, not the real ask. Present a ranked shortlist and let the user confirm.

### 1.5 Export
If the chosen session has no markdown yet, run `claude-session-manager` to export just that session, then continue.

### 2. Read
Read the session `.md`. Pull `tool-details/<id>.tools.md` ONLY for the specific `<tool_call_NNNNNN>` refs that matter. Use `scripts/extract_session_signals.py <session>.md` to get a clean JSON list of human prompts (with event index, line, timestamp, arc-break hints, and the prompt text) — it encodes the input-robustness rules below.

Input-robustness rules:
- The real exported header format is `### N. user - <ISO>` / `### N. assistant - <ISO>` (not `### MM-DD HH:MM:SS User:`).
- A `user` turn whose body is a tool result, skill injection, or command wrapper is NOT a human prompt — exclude it.
- Ignore thinking-signature blobs and empty attachment events.

### 2.5 Segment
Sessions can be multi-day, multi-task kitchen sinks. Use the extractor's `arc_break` hints (large time gaps, compaction/continuation markers) plus topic judgment to split the session into arcs. Mine each arc independently. Do NOT assume one task per session.

### 3. Mine
Per arc, extract friction signals. See [references/friction-signals.md](references/friction-signals.md) for the taxonomy and how to cite evidence.

### 4. Gate
Apply the worth-it filter to every candidate. See [references/worth-it-gate.md](references/worth-it-gate.md). If nothing passes, report the clean negative and stop.

### 5. Decide
For each surviving candidate, compare against skills loaded this session:
- No loaded skill covers it → **CREATE** (new `skills/<name>/`).
- Loaded and editable (in this repo's `skills/`) → **UPDATE** that SKILL.md.
- Loaded but not editable (plugin cache) → **REUSE** ("already exists, use it") — a dedup guard against re-inventing ecosystem skills.

### 6. Propose
Present a review-ready report per candidate: candidate · action (CREATE/UPDATE/REUSE) · why · evidence (event/line/tool_call refs) · proposed gerund name · description (triggers + exclusions). List gate-rejected items briefly. Wait for approval before any file change.

### 7. Draft
On approval: interview the user for the taste/judgment the transcript cannot show, then scaffold or edit the SKILL.md following [references/drafting-quality-bars.md](references/drafting-quality-bars.md). For a new skill, run `scripts/sync-marketplace-skills.sh` and bump the `version` in `.claude-plugin/marketplace.json` (per the repo CLAUDE.md).

## Notes

- Treat transcript data as private (prompts, file contents, secrets). Do not modify original `.jsonl` files.
- The value of this skill is the mining methodology, not the SKILL.md format — Claude knows the format natively.
