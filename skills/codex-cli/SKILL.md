---
name: codex-cli
description: Use when an agent needs to delegate a task to the OpenAI Codex CLI from another agent environment such as Claude Code, OpenClaw, or similar. Covers checking whether Codex CLI is installed, running one-off Codex prompts with `codex exec`, resuming sessions, collecting outputs, attaching images or files as input with `-i`/stdin, and handling Codex image generation including finding and reporting generated image file paths.
---

# Codex CLI

Use this skill when the user asks this agent to talk to Codex, consult Codex, delegate a coding/review/research task to Codex CLI, or ask Codex to generate an image.

The core interface is:

```bash
codex exec "prompt"
```

For automation, prefer non-interactive `codex exec` over interactive `codex`.

## First Check

Before using Codex CLI, verify it is available:

```bash
command -v codex
codex --version
codex exec --help
```

If `codex` is missing, tell the user Codex CLI is not available in this environment and stop. Do not simulate a Codex response.

If `codex exec --help` is available, use it as the source of truth for the installed CLI flags. Codex CLI changes over time.

## One-Off Task Workflow

Use this for normal delegation:

```bash
codex exec -C "$PWD" -s read-only "Review this repository and identify likely bugs"
```

For tasks that may edit files, use the sandbox the user requested or the host agent allows:

```bash
codex exec -C "$PWD" -s workspace-write "Implement the requested change"
```

For a response file:

```bash
codex exec -C "$PWD" -o /tmp/codex-last-message.md "Summarize this project"
```

For machine-readable events:

```bash
codex exec -C "$PWD" --json -o /tmp/codex-last-message.md "Analyze this project"
```

If the prompt is long, pass it via stdin:

```bash
codex exec -C "$PWD" - < /tmp/prompt.txt
```

When using shell commands from another agent, avoid dangerous flags unless the user explicitly asked for them. Prefer `read-only` for review, planning, critique, image generation, and analysis.

## Prompt Shape

For non-trivial tasks, shape the delegated prompt with OpenAI's Codex best-practices structure:

```text
Goal:
Context:
Constraints:
Done when:
```

Keep the prompt scoped to one task. For complex implementation work, ask Codex for a plan first in `read-only` mode, then run a separate write task after the plan is accepted.

## Session Resume

Codex emits a session id in normal startup output and in JSONL events as `thread.started`.

To resume:

```bash
codex exec resume <session-id> "Continue from the previous task"
```

If the installed CLI supports a different resume syntax, follow `codex exec resume --help`.

## Image and File Input

Codex cannot browse or read image files on its own. To let Codex *see* an image, attach it explicitly with `-i`/`--image`. This is the input side; image generation (below) is the output side.

Attach a single image:

```bash
codex exec -C "$PWD" -s read-only -i screenshot.png "Explain the error shown here"
```

Attach multiple images. Both forms work — comma-separated or a repeated flag:

```bash
codex exec -i before.png,after.png "Compare these two UI states"
codex exec -i mock1.png -i mock2.png "Which layout is closer to the spec?"
```

Best practices:

- Put `-i` flags before the prompt text.
- Use common raster formats: PNG (best for screenshots/UI, lossless) or JPEG. Keep images reasonably small; very large images slow the request.
- Combine images with a clear text instruction — the image alone is rarely enough context.
- For visual review/analysis, pair with `-s read-only` so Codex inspects but does not edit.

For **non-image files** there is no attach flag. Two options:

- Let Codex read the file from the workspace: point it at the directory with `-C "$PWD"` and name the file in the prompt (`"Review src/auth.ts"`). Use this for files already in the repo.
- Pipe file contents via stdin. With a prompt also present, stdin is appended to the prompt as a `<stdin>` block:

```bash
codex exec -C "$PWD" "Summarize the attached log" < /tmp/build.log
```

## Image Generation Workflow

Codex can generate images through its built-in image generation tool when asked through `codex exec`.

Example:

```bash
codex exec "Generate a black banana image with aspect ratio 16:9"
```

Important behavior:

- Built-in image generation commonly saves files under `$CODEX_HOME/generated_images/<codex-session-id>/`.
- If `CODEX_HOME` is unset, use `~/.codex/generated_images/<codex-session-id>/`.
- Codex may not print the path in its final response.
- The agent using this skill must proactively locate and report generated image paths after image generation.
- The PNG metadata may not expose the exact image model. Do not claim a specific backend model unless Codex output, CLI logs, or metadata clearly show it.

### Finding Generated Images

After any Codex image-generation request, find the image path before replying.

First extract the Codex session id from output if available. It may look like:

```text
session id: 019e8cbf-5054-7131-9440-ee592f0d8a17
```

Then check:

```bash
ls -l "${CODEX_HOME:-$HOME/.codex}/generated_images/<session-id>"
```

If the session id is not known, list recent generated images:

```bash
find "${CODEX_HOME:-$HOME/.codex}/generated_images" -type f -maxdepth 3 -print
```

When possible, sort by modification time:

```bash
find "${CODEX_HOME:-$HOME/.codex}/generated_images" -type f -maxdepth 3 -print0 \
  | xargs -0 ls -lt
```

If the user requested a project asset, copy or move the selected image into the project after generation if permissions allow. Never leave a project-referenced asset only under `$CODEX_HOME/generated_images`.

### Verifying Aspect Ratio

If the user requested a specific aspect ratio, verify dimensions before answering.

On macOS:

```bash
sips -g pixelWidth -g pixelHeight /path/to/image.png
```

Portable fallback:

```bash
file /path/to/image.png
```

Report actual dimensions and whether they match approximately or exactly. Many generated images use nearest integer dimensions, so a 16:9 request may produce dimensions like `1672 x 941`, which is effectively 16:9 but not mathematically exact.

## Reporting Results

For normal Codex tasks, report:

- command used, summarized if long
- Codex status or final answer
- any files Codex changed, if known
- any limitations, errors, or missing permissions

For image tasks, always report:

- generated image path
- actual dimensions if available
- whether the path is in `$CODEX_HOME` or copied into the project
- whether the exact image model is known or not

Example response:

```text
Codex generated the image here:
/Users/me/.codex/generated_images/019e.../ig_....png

Actual size: 1672 x 941, effectively 16:9.
The output does not expose the exact image backend model, so I cannot verify whether it was gpt-image-2.
```

## Failure Handling

If Codex exits with network, auth, or model refresh errors, report the error plainly and include the relevant stderr lines.

If Codex claims it generated an image but no image file exists under `$CODEX_HOME/generated_images`, say so explicitly and do not invent a path.

If the host agent cannot read `$CODEX_HOME/generated_images`, ask the user to grant access or run:

```bash
find "${CODEX_HOME:-$HOME/.codex}/generated_images" -type f -maxdepth 3 -print0 | xargs -0 ls -lt
```

## Safety Notes

Do not pass secrets to Codex unless the user explicitly asks and understands the risk.

Use `read-only` for consultation. Use `workspace-write` only when Codex is expected to edit files. Avoid `danger-full-access` unless the user explicitly requested it in a controlled environment.

Do not claim Codex performed work solely from its final message. When file changes matter, inspect the filesystem or Git diff after the run.
