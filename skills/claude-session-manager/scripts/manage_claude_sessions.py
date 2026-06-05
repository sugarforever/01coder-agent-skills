#!/usr/bin/env python3
"""List and export Claude Code JSONL session transcripts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("~/.claude/projects").expanduser()
DEFAULT_OUTPUT = Path("~/.claude/session-markdown").expanduser()

# Cap any single tool input/result payload written to the details file. The raw,
# untruncated payload always remains in the source JSONL (linked from the digest).
TOOL_DETAIL_LIMIT = 8000


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List and export Claude Code JSONL sessions to organized Markdown."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--mode",
        choices=("full", "specific"),
        default="full",
        help="full exports all matching sessions; specific lists or exports a chosen session.",
    )
    parser.add_argument(
        "--list-candidates",
        action="store_true",
        help="Print a numbered candidate list instead of exporting.",
    )
    parser.add_argument(
        "--pick",
        type=int,
        help="In specific mode, export the Nth candidate from the numbered candidate list.",
    )
    parser.add_argument("--project", help="Only export project keys containing this text.")
    parser.add_argument("--session", help="Only export session ids or filenames containing this text.")
    parser.add_argument("--since", help="Only export files modified on or after YYYY-MM-DD.")
    parser.add_argument("--limit", type=int, help="Export the N most recently modified matches.")
    parser.add_argument(
        "--include-tool-details-inline",
        action="store_true",
        help="Embed full tool inputs and results in the main Markdown instead of compact details.",
    )
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    since = parse_since(args.since)

    if not source.exists():
        raise SystemExit(f"Source folder does not exist: {source}")

    sessions = find_sessions(source, args.project, args.session, since)
    sessions = sorted(sessions, key=lambda item: item.stat().st_mtime, reverse=True)
    if args.limit:
        sessions = sessions[: args.limit]

    if args.mode == "specific" and (args.list_candidates or not args.pick):
        print_candidates(sessions, source)
        return 0

    if args.mode == "specific":
        if args.pick < 1 or args.pick > len(sessions):
            raise SystemExit(f"--pick must be between 1 and {len(sessions)}")
        sessions = [sessions[args.pick - 1]]
    else:
        sessions = sorted(sessions)

    output.mkdir(parents=True, exist_ok=True)
    exports: list[dict[str, Any]] = []
    warnings: list[str] = []

    for session_file in sessions:
        try:
            export = export_session(session_file, source, output, args.include_tool_details_inline)
            exports.append(export)
        except Exception as exc:  # Keep batch exports useful even if one transcript is odd.
            warnings.append(f"{session_file}: {exc}")

    write_root_index(output, exports, source)

    print(f"Source: {source}")
    print(f"Output: {output}")
    print(f"Exported sessions: {len(exports)}")
    if exports:
        # Print the actual file paths — the folder name is sanitized (leading
        # dashes stripped), so it is not always derivable from the project key.
        print("Files:")
        for export in exports[:50]:
            print(f"- {export['path']}")
        if len(exports) > 50:
            print(f"- ... {len(exports) - 50} more")
    if warnings:
        print(f"Warnings: {len(warnings)}")
        for warning in warnings[:20]:
            print(f"- {warning}")
        if len(warnings) > 20:
            print(f"- ... {len(warnings) - 20} more")
    print(f"Index: {output / 'index.md'}")
    return 0


def print_candidates(sessions: list[Path], source: Path) -> None:
    print(f"Source: {source}")
    print(f"Candidate sessions: {len(sessions)}")
    print("")
    print("| # | Modified | Project | Session | CWD | First user prompt |")
    print("|---:|---|---|---|---|---|")
    for index, path in enumerate(sessions, start=1):
        events, _warnings = read_jsonl(path)
        rel = path.relative_to(source)
        project_key = rel.parts[0] if rel.parts else path.parent.name
        session_id = detect_session_id(events, path)
        modified = dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
        cwd = first_value(events, "cwd") or "unknown"
        prompt = first_user_prompt(events) or "unknown"
        print(
            f"| {index} | `{modified}` | {code_cell(project_key)} | "
            f"{code_cell(short_session_id(session_id))} | {code_cell(cwd)} | "
            f"{markdown_cell(prompt)} |"
        )


def parse_since(value: str | None) -> float | None:
    if not value:
        return None
    day = dt.datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
    return day.timestamp()


def find_sessions(
    source: Path, project_filter: str | None, session_filter: str | None, since: float | None
) -> list[Path]:
    files = [path for path in source.rglob("*.jsonl") if path.is_file()]
    matches = []
    for path in files:
        rel = path.relative_to(source)
        project_key = rel.parts[0] if rel.parts else path.parent.name
        session_id = session_id_from_path(path)
        if project_filter and project_filter.lower() not in project_key.lower():
            continue
        if session_filter:
            text = f"{session_id} {path.name}".lower()
            if session_filter.lower() not in text:
                continue
        if since and path.stat().st_mtime < since:
            continue
        matches.append(path)
    return matches


def export_session(session_file: Path, source: Path, output: Path, inline_tools: bool) -> dict[str, Any]:
    events, warnings = read_jsonl(session_file)
    rel = session_file.relative_to(source)
    project_key = rel.parts[0] if rel.parts else session_file.parent.name
    session_id = detect_session_id(events, session_file)

    project_dir = output / safe_name(project_key)
    tool_dir = project_dir / "tool-details"
    project_dir.mkdir(parents=True, exist_ok=True)
    if not inline_tools:
        tool_dir.mkdir(parents=True, exist_ok=True)

    session_md = project_dir / f"{safe_name(session_id)}.md"
    tool_md = tool_dir / f"{safe_name(session_id)}.tools.md"

    # Where an inline `<tool_call_…>` reference should link for full details.
    # Sidecar mode points at the details file; inline mode points at a same-doc anchor.
    details_href = "" if inline_tools else f"tool-details/{tool_md.name}"

    rendered, tool_sections, stats = render_events(events, inline_tools, details_href)
    first_prompt = first_user_prompt(events)
    timestamps = [extract_timestamp(event) for event in events]
    timestamps = [stamp for stamp in timestamps if stamp]
    cwd = first_value(events, "cwd")

    digest = [
        f"# Claude Session {session_id}",
        "",
        "## Digest",
        "",
        f"- Source: `{session_file}`",
        f"- Project key: `{project_key}`",
        f"- Session id: `{session_id}`",
        f"- CWD: `{cwd or 'unknown'}`",
        f"- Started: `{min(timestamps) if timestamps else 'unknown'}`",
        f"- Ended: `{max(timestamps) if timestamps else 'unknown'}`",
        f"- Events: `{len(events)}`",
        f"- Messages: `{stats['messages']}`",
        f"- Tool uses: `{stats['tool_uses']}`",
        f"- Tool results: `{stats['tool_results']}`",
        f"- First user prompt excerpt: `{inline_code(first_prompt) if first_prompt else 'unknown'}`",
    ]
    if warnings:
        digest.append(f"- Parse warnings: `{len(warnings)}`")
    if tool_sections and not inline_tools:
        digest.append(f"- Tool details: [tool-details/{tool_md.name}](tool-details/{tool_md.name})")

    if stats.get("skipped_noise"):
        digest.append(f"- Collapsed metadata/noise events: `{stats['skipped_noise']}`")

    # In inline mode the details ride along in collapsible <details> next to each
    # call, so there is no separate section or sidecar; in sidecar mode the compact
    # references link out to tool_md.
    body = digest + ["", "## Conversation", ""] + rendered
    session_md.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")

    if tool_sections and not inline_tools:
        tool_md.write_text(
            "\n".join(
                [
                    f"# Tool Details for {session_id}",
                    "",
                    f"- Main transcript: [../{session_md.name}](../{session_md.name})",
                    "",
                ]
                + tool_sections
            ).rstrip()
            + "\n",
            encoding="utf-8",
        )

    write_project_index(project_dir, project_key)

    return {
        "project_key": project_key,
        "session_id": session_id,
        "path": session_md,
        "started": min(timestamps) if timestamps else "",
        "ended": max(timestamps) if timestamps else "",
        "mtime": session_file.stat().st_mtime,
        "tool_uses": stats["tool_uses"],
        "warnings": len(warnings),
    }


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events = []
    warnings = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                warnings.append(f"line {line_no}: {exc}")
                continue
            if isinstance(value, dict):
                events.append(value)
            else:
                warnings.append(f"line {line_no}: expected object, got {type(value).__name__}")
    return events, warnings


def render_events(
    events: list[dict[str, Any]], inline_tools: bool = False, details_href: str = ""
) -> tuple[list[str], list[str], dict[str, int]]:
    turns: list[dict[str, Any]] = []
    tool_sections: list[str] = []
    stats = {"messages": 0, "tool_uses": 0, "tool_results": 0, "skipped_noise": 0}
    pending_tool_results = collect_tool_results(events)

    for idx, event in enumerate(events, start=1):
        message = event.get("message") if isinstance(event.get("message"), dict) else {}
        role = message.get("role") or event.get("role") or event.get("type") or "event"
        timestamp = extract_timestamp(event)

        if role == "tool_use":
            stats["tool_uses"] += 1
            tool_ref = tool_ref_name(stats["tool_uses"])
            tool_id = event.get("id", f"tool-{idx}-{stats['tool_uses']}")
            name = event.get("name", "unknown_tool")
            result = pending_tool_results.get(str(tool_id))
            append_turn(turns, "Claude", timestamp, format_tool_reference(tool_ref, name, event, result, inline_tools, details_href))
            if not inline_tools:
                tool_sections.extend(tool_detail_section(tool_ref, idx, tool_id, name, event, result))
            continue

        if role == "tool_result":
            stats["tool_results"] += 1
            tool_id = event.get("tool_use_id") or event.get("id") or f"tool-result-{idx}"
            pending_tool_results[str(tool_id)] = {"block": event, "structured": event.get("toolUseResult")}
            continue

        if role not in {"user", "assistant"}:
            stats["skipped_noise"] += 1
            continue

        content = message.get("content", event.get("content", ""))
        chunks = content if isinstance(content, list) else [content]
        event_lines: list[str] = []

        for block in chunks:
            if isinstance(block, str):
                if is_noise_text(block):
                    stats["skipped_noise"] += 1
                elif block.strip():
                    event_lines.append(block)
                continue
            if not isinstance(block, dict):
                event_lines.append(format_scalar(block))
                continue

            block_type = block.get("type", "object")
            if block_type == "text":
                text = str(block.get("text", ""))
                if is_noise_text(text):
                    stats["skipped_noise"] += 1
                else:
                    event_lines.append(text)
            elif block_type == "tool_use":
                stats["tool_uses"] += 1
                tool_ref = tool_ref_name(stats["tool_uses"])
                tool_id = block.get("id", f"tool-{idx}-{stats['tool_uses']}")
                name = block.get("name", "unknown_tool")
                result = pending_tool_results.get(str(tool_id))
                event_lines.extend(format_tool_reference(tool_ref, name, block, result, inline_tools, details_href))
                if not inline_tools:
                    tool_sections.extend(tool_detail_section(tool_ref, idx, tool_id, name, block, result))
            elif block_type == "tool_result":
                stats["tool_results"] += 1
            elif block_type in {"thinking", "redacted_thinking"}:
                stats["skipped_noise"] += 1
            else:
                stats["skipped_noise"] += 1

        text = "\n\n".join(part.strip() for part in event_lines if part and part.strip())
        if role == "user" and message_has_only_tool_results(chunks):
            stats["skipped_noise"] += 1
            continue
        if text:
            speaker = "User" if role == "user" else "Claude"
            append_turn(turns, speaker, timestamp, [text])
        else:
            stats["skipped_noise"] += 1

    rendered: list[str] = []
    for turn in turns:
        rendered.extend(render_message_header(turn["speaker"], turn["timestamp"]))
        rendered.append("\n\n".join(turn["parts"]))
        rendered.append("")

    stats["messages"] = len(turns)
    return rendered, tool_sections, stats


def append_turn(turns: list[dict[str, Any]], speaker: str, timestamp: str, parts: list[str]) -> None:
    clean_parts = [normalize_message_flow_markdown(part.strip()) for part in parts if part and part.strip()]
    if not clean_parts:
        return
    if turns and turns[-1]["speaker"] == speaker:
        turns[-1]["parts"].extend(clean_parts)
        if not turns[-1]["timestamp"] and timestamp:
            turns[-1]["timestamp"] = timestamp
        return
    turns.append({"speaker": speaker, "timestamp": timestamp, "parts": clean_parts})


def render_message_header(speaker: str, timestamp: str) -> list[str]:
    prefix = format_local_timestamp(timestamp) if timestamp else "unknown-time"
    return [f"### {prefix} {speaker}:", ""]


def format_local_timestamp(timestamp: str) -> str:
    try:
        value = timestamp.replace("Z", "+00:00")
        parsed = dt.datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.datetime.now().astimezone().tzinfo)
        local = parsed.astimezone()
        return local.strftime("%m-%d %H:%M:%S")
    except ValueError:
        return timestamp


def normalize_message_flow_markdown(text: str) -> str:
    """Keep transcript message flow readable in common Markdown renderers."""
    lines = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            lines.append(line)
            continue
        if not in_fence and stripped.startswith("#"):
            marker = stripped.split(maxsplit=1)
            if marker and set(marker[0]) == {"#"} and len(marker[0]) <= 6:
                indent = line[: len(line) - len(stripped)]
                heading_text = marker[1].strip() if len(marker) > 1 else ""
                lines.append(f"{indent}**{heading_text}**" if heading_text else line)
                continue
        lines.append(line)
    return "\n".join(lines)


def collect_tool_results(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Map tool_use_id -> {"block": <flat tool_result>, "structured": <toolUseResult>}.

    The flat block is what the model saw (a string). The structured `toolUseResult`,
    when present on the same event, carries richer per-tool fields (Bash stdout/stderr,
    Read line counts, AskUserQuestion answers) that make a better rendering.
    """
    results: dict[str, dict[str, Any]] = {}
    for event in events:
        structured = event.get("toolUseResult")
        role = event.get("role") or event.get("type")
        if role == "tool_result":
            tool_id = event.get("tool_use_id") or event.get("id")
            if tool_id:
                results[str(tool_id)] = {"block": event, "structured": structured}
        message = event.get("message") if isinstance(event.get("message"), dict) else {}
        content = message.get("content", event.get("content", ""))
        chunks = content if isinstance(content, list) else [content]
        for block in chunks:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                tool_id = block.get("tool_use_id") or block.get("id")
                if tool_id:
                    results[str(tool_id)] = {"block": block, "structured": structured}
    return results


def tool_ref_name(index: int) -> str:
    return f"tool_call_{index:06d}"


def format_tool_reference(
    ref: str,
    name: str,
    tool_payload: dict[str, Any],
    result_record: dict[str, Any] | None,
    inline: bool,
    details_href: str = "",
) -> list[str]:
    """One scannable line: what tool ran, what it did, what came back, where the rest is."""
    label = f"`<{ref}>` {name}"
    summary = tool_label(name, tool_payload)
    if summary:
        label += f" · {summary}"
    label += f" → {inline_result_signal(name, result_record)}"
    if details_href:
        label += f" · [details]({details_href}#{ref})"

    if not inline:
        return [label]
    return [label] + format_inline_tool_details(name, tool_payload, result_record)


def tool_label(name: str, payload: dict[str, Any]) -> str:
    """A single human-readable label for the call — the most telling input field."""
    tool_input = payload.get("input")
    if not isinstance(tool_input, dict):
        return ""
    # Per-tool preference order: the field a reader most wants to see inline.
    for key in ("description", "skill", "command", "file_path", "path", "pattern", "query", "url"):
        value = tool_input.get(key)
        if value in (None, "", [], {}):
            continue
        if key in ("file_path", "path"):
            return Path(str(value)).name
        return shorten_summary(value, 90)
    questions = tool_input.get("questions")
    if isinstance(questions, list) and questions and isinstance(questions[0], dict):
        return shorten_summary(questions[0].get("question", ""), 90)
    if tool_input:
        key = next(iter(tool_input))
        return shorten_summary(tool_input[key], 90)
    return ""


def shorten_summary(value: Any, limit: int = 120) -> str:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    else:
        text = str(value)
    return shorten(text, limit)


def inline_result_signal(name: str, record: dict[str, Any] | None) -> str:
    """Smallest useful fact about the result: status, line count, error, or chosen answer."""
    if record is None:
        return "pending"
    block = record.get("block") or {}
    structured = record.get("structured")
    is_error = bool(block.get("is_error"))
    flat = block_text(block)

    # AskUserQuestion: the answer the user picked is the point.
    if isinstance(structured, dict) and isinstance(structured.get("answers"), dict):
        picked = "; ".join(str(v) for v in structured["answers"].values() if v)
        if picked:
            return shorten(picked, 120)

    # Bash: stdout/stderr split out.
    if isinstance(structured, dict) and ("stdout" in structured or "stderr" in structured):
        if structured.get("interrupted"):
            return "interrupted"
        stderr = (structured.get("stderr") or "").strip()
        stdout = structured.get("stdout") or ""
        if is_error:
            return f"error: {first_line(stderr or flat)}"
        n = count_lines(stdout)
        return f"ok · {n} line{'s' if n != 1 else ''}" if n else "ok"

    # Read: line counts.
    if isinstance(structured, dict) and isinstance(structured.get("file"), dict):
        total = structured["file"].get("totalLines") or structured["file"].get("numLines")
        return f"{total} lines" if total else "ok"

    if is_error:
        return f"error: {first_line(flat)}"

    n = count_lines(flat)
    if n <= 1:
        return shorten(flat, 80) or "ok"
    return f"ok · {n} lines"


def first_line(text: str, limit: int = 100) -> str:
    stripped = (text or "").strip()
    if not stripped:
        return ""
    return shorten(stripped.splitlines()[0], limit)


def count_lines(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def render_result_detail(record: dict[str, Any] | None, hpre: str = "### ", hsuf: str = "") -> list[str]:
    """Full result body for the details file / inline block, using structured fields when present."""
    def heading(text: str) -> str:
        return f"{hpre}{text}{hsuf}"

    if record is None:
        return [heading("Result"), "", "_Result pending or not captured._", ""]

    block = record.get("block") or {}
    structured = record.get("structured")
    is_error = bool(block.get("is_error"))

    # Bash: separate stdout/stderr and surface interruption.
    if isinstance(structured, dict) and ("stdout" in structured or "stderr" in structured):
        out = [heading("Error" if is_error else "Result"), ""]
        if structured.get("interrupted"):
            out.append("- Interrupted: `true`")
            out.append("")
        stdout = structured.get("stdout") or ""
        stderr = structured.get("stderr") or ""
        out += ["**stdout**", "```", truncate_preserve_lines(stdout, TOOL_DETAIL_LIMIT) if stdout.strip() else "(empty)", "```", ""]
        if stderr.strip():
            out += ["**stderr**", "```", truncate_preserve_lines(stderr, TOOL_DETAIL_LIMIT), "```", ""]
        return out

    # Read: file metadata + content.
    if isinstance(structured, dict) and isinstance(structured.get("file"), dict):
        fobj = structured["file"]
        out = [heading("Result"), ""]
        if fobj.get("filePath"):
            out.append(f"- File: `{fobj['filePath']}`")
        if fobj.get("totalLines") is not None:
            out.append(
                f"- Lines: `{fobj.get('numLines', '?')}` shown of `{fobj['totalLines']}` "
                f"total (from line `{fobj.get('startLine', 1)}`)"
            )
        out.append("")
        content = fobj.get("content") or block_text(block)
        out += ["```", truncate_preserve_lines(content, TOOL_DETAIL_LIMIT), "```", ""]
        return out

    # AskUserQuestion: list each question and the chosen answer.
    if isinstance(structured, dict) and isinstance(structured.get("answers"), dict):
        out = [heading("Result"), ""]
        for question, answer in structured["answers"].items():
            out.append(f"- **{question}** → {answer}")
        out.append("")
        return out

    # Fallback: the flat string the model saw.
    return [
        heading("Error" if is_error else "Result"),
        "",
        "```",
        truncate_preserve_lines(block_text(block), TOOL_DETAIL_LIMIT),
        "```",
        "",
    ]


def format_inline_tool_details(name: str, tool_payload: dict[str, Any], result_record: dict[str, Any] | None) -> list[str]:
    lines = [
        "<details>",
        f"<summary><strong>Tool:</strong> {name}</summary>",
        "",
    ]
    tool_input = tool_payload.get("input")
    if tool_input not in (None, {}, ""):
        lines.extend(
            [
                "**Input:**",
                "```json",
                truncate_preserve_lines(json.dumps(tool_input, ensure_ascii=False, indent=2, sort_keys=True), TOOL_DETAIL_LIMIT),
                "```",
                "",
            ]
        )
    lines.extend(render_result_detail(result_record, hpre="**", hsuf="**"))
    lines.extend(["</details>", ""])
    return lines


def message_has_only_tool_results(chunks: list[Any]) -> bool:
    if not chunks:
        return False
    return all(isinstance(block, dict) and block.get("type") == "tool_result" for block in chunks)


def tool_detail_section(
    ref: str,
    event_index: int,
    tool_id: Any,
    name: str,
    payload: dict[str, Any],
    result_record: dict[str, Any] | None,
) -> list[str]:
    lines = [
        f'<a id="{ref}"></a>',
        f"## `<{ref}>` {name}",
        "",
        f"- Event: `{event_index}`",
        f"- Id: `{tool_id or 'unknown'}`",
        f"- Tool: `{name}`",
        "",
        "### Input",
        "",
        "```json",
        truncate_preserve_lines(json.dumps(payload.get("input", payload), ensure_ascii=False, indent=2, sort_keys=True), TOOL_DETAIL_LIMIT),
        "```",
        "",
    ]
    lines.extend(render_result_detail(result_record))
    return lines


def block_text(block: dict[str, Any]) -> str:
    value = block.get("content", block.get("text", block.get("input", block)))
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def first_user_prompt(events: list[dict[str, Any]]) -> str:
    for event in events:
        message = event.get("message") if isinstance(event.get("message"), dict) else {}
        role = message.get("role") or event.get("role") or event.get("type")
        if role != "user":
            continue
        content = message.get("content", event.get("content", ""))
        text = extract_text(content)
        if text and not is_noise_text(text):
            return shorten(text, 500)
    return ""


def extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(part.strip() for part in parts if part and part.strip())
    return ""


def is_noise_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    noise_prefixes = (
        "<local-command-caveat>",
        "<command-name>",
        "<local-command-stdout>",
        "<local-command-stderr>",
    )
    if stripped.startswith(noise_prefixes):
        return True
    if stripped.startswith("Base directory for this skill:"):
        return True
    if stripped.startswith("The file ") and " has been updated successfully" in stripped:
        return True
    if stripped.startswith("Launching skill:"):
        return True
    return False


def extract_timestamp(event: dict[str, Any]) -> str:
    value = event.get("timestamp") or event.get("created_at") or event.get("createdAt")
    return str(value) if value else ""


def first_value(events: list[dict[str, Any]], key: str) -> Any:
    for event in events:
        if event.get(key):
            return event[key]
    return None


def detect_session_id(events: list[dict[str, Any]], path: Path) -> str:
    for event in events:
        for key in ("sessionId", "session_id", "sessionID"):
            if event.get(key):
                return str(event[key])
    return session_id_from_path(path)


def session_id_from_path(path: Path) -> str:
    if path.name == "transcript.jsonl":
        return path.parent.name
    return path.stem


def write_project_index(project_dir: Path, project_key: str) -> None:
    sessions = sorted(project_dir.glob("*.md"))
    rows = [f"# {project_key}", "", "| Session | Modified |", "|---|---|"]
    for path in sessions:
        if path.name == "index.md":
            continue
        modified = dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
        rows.append(f"| [{path.stem}]({path.name}) | `{modified}` |")
    (project_dir / "index.md").write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")


def write_root_index(output: Path, exports: list[dict[str, Any]], source: Path) -> None:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for export in exports:
        grouped.setdefault(export["project_key"], []).append(export)

    rows = [
        "# Claude Session Markdown Export",
        "",
        f"- Source: `{source}`",
        f"- Generated: `{dt.datetime.now().isoformat(timespec='seconds')}`",
        f"- Sessions exported: `{len(exports)}`",
        "",
        "## Projects",
        "",
        "| Project | Sessions | Latest exported session |",
        "|---|---:|---|",
    ]
    for project_key in sorted(grouped):
        items = sorted(grouped[project_key], key=lambda item: item.get("ended") or item.get("started") or "")
        latest = items[-1]
        project_folder = safe_name(project_key)
        latest_link = f"{project_folder}/{safe_name(latest['session_id'])}.md"
        rows.append(
            f"| [{project_key}]({project_folder}/index.md) | {len(items)} | "
            f"[{latest['session_id']}]({latest_link}) |"
        )
    (output / "index.md").write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")


def inline_code(text: str) -> str:
    return shorten(text, 500).replace("`", "'")


def markdown_cell(text: str) -> str:
    cleaned = shorten(text, 180).replace("|", "\\|").replace("\n", " ")
    return cleaned or "unknown"


def code_cell(text: str) -> str:
    return f"`{markdown_cell(inline_code(text))}`"


def short_session_id(session_id: str) -> str:
    if len(session_id) <= 18:
        return session_id
    return f"{session_id[:8]}...{session_id[-6:]}"


def shorten(text: str, limit: int) -> str:
    collapsed = " ".join(str(text).split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "..."


def truncate_preserve_lines(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    kept = text[:limit].rstrip()
    return f"{kept}\n... (truncated {len(text) - limit} of {len(text)} chars — full payload in source JSONL)"


def format_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def safe_name(value: Any) -> str:
    text = str(value).strip() or "unknown"
    safe = []
    for char in text:
        if char.isalnum() or char in "-_.":
            safe.append(char)
        else:
            safe.append("-")
    result = "".join(safe).strip(".-")
    return result[:180] or "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
