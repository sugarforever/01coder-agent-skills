#!/usr/bin/env python3
"""List and export Codex JSONL session transcripts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("~/.codex/sessions").expanduser()
DEFAULT_ARCHIVED_SOURCE = Path("~/.codex/archived_sessions").expanduser()
DEFAULT_OUTPUT = Path("~/.codex/session-markdown").expanduser()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List and export Codex JSONL sessions to organized Markdown."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--include-archived",
        action="store_true",
        help="Also scan ~/.codex/archived_sessions.",
    )
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
        help="Embed full tool details in the main Markdown instead of a sidecar file.",
    )
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    since = parse_since(args.since)

    if not source.exists():
        raise SystemExit(f"Source folder does not exist: {source}")

    sessions = find_sessions(source, args.project, args.session, since)
    if args.include_archived and DEFAULT_ARCHIVED_SOURCE.exists():
        sessions.extend(find_sessions(DEFAULT_ARCHIVED_SOURCE.resolve(), args.project, args.session, since))
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
        project_key = project_key_for(path, source)
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
        project_key = project_key_for(path, source)
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
    project_key = project_key_for(session_file, source)
    session_id = detect_session_id(events, session_file)

    project_dir = output / safe_name(project_key)
    tool_dir = project_dir / "tool-details"
    project_dir.mkdir(parents=True, exist_ok=True)
    if not inline_tools:
        tool_dir.mkdir(parents=True, exist_ok=True)

    rendered, tool_sections, stats = render_events(events)
    first_prompt = first_user_prompt(events)
    timestamps = [extract_timestamp(event) for event in events]
    timestamps = [stamp for stamp in timestamps if stamp]
    cwd = first_value(events, "cwd")

    session_md = project_dir / f"{safe_name(session_id)}.md"
    tool_md = tool_dir / f"{safe_name(session_id)}.tools.md"

    digest = [
        f"# Codex Session {session_id}",
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

    body = digest + ["", "## Timeline", ""] + rendered
    if inline_tools and tool_sections:
        body += ["", "## Tool Details", ""] + tool_sections
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


def render_events(events: list[dict[str, Any]]) -> tuple[list[str], list[str], dict[str, int]]:
    rendered: list[str] = []
    tool_sections: list[str] = []
    stats = {"messages": 0, "tool_uses": 0, "tool_results": 0}

    for idx, event in enumerate(events, start=1):
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        payload_type = payload.get("type")
        role = payload.get("role") or event.get("role") or event.get("type") or "event"
        timestamp = extract_timestamp(event)
        title = f"### {idx}. {role}"
        if timestamp:
            title += f" - {timestamp}"
        rendered.append(title)
        rendered.append("")
        stats["messages"] += 1 if payload_type == "message" else 0

        if payload_type in {"function_call", "custom_tool_call", "tool_search_call"}:
            stats["tool_uses"] += 1
            tool_id = payload.get("call_id") or payload.get("id") or f"tool-{idx}-{stats['tool_uses']}"
            name = payload.get("name") or payload_type or "unknown_tool"
            rendered.append(f"- Tool use `{name}` (`{tool_id}`)")
            rendered.append("")
            tool_sections.extend(tool_detail_section("Tool Use", idx, tool_id, name, payload))
            continue

        if payload_type in {"function_call_output", "custom_tool_call_output", "tool_search_output"}:
            stats["tool_results"] += 1
            tool_id = payload.get("call_id") or payload.get("id") or f"tool-result-{idx}"
            status = "error" if payload.get("is_error") else "result"
            rendered.append(f"- Tool {status} (`{tool_id}`): {shorten(block_text(payload), 240)}")
            rendered.append("")
            tool_sections.extend(tool_detail_section("Tool Result", idx, tool_id, None, payload))
            continue

        if payload_type == "session_meta":
            rendered.append(f"- CWD: `{payload.get('cwd', 'unknown')}`")
            rendered.append(f"- Source: `{payload.get('source', 'unknown')}`")
            rendered.append("")
            continue

        content = payload.get("content", event.get("content", ""))
        chunks = content if isinstance(content, list) else [content]
        event_lines: list[str] = []

        for block in chunks:
            if isinstance(block, str):
                if block.strip():
                    event_lines.append(block)
                continue
            if not isinstance(block, dict):
                event_lines.append(format_scalar(block))
                continue

            block_type = block.get("type", "object")
            if block_type in {"text", "input_text", "output_text"}:
                event_lines.append(str(block.get("text", "")))
            elif block_type == "tool_use":
                stats["tool_uses"] += 1
                tool_id = block.get("id", f"tool-{idx}-{stats['tool_uses']}")
                name = block.get("name", "unknown_tool")
                event_lines.append(f"- Tool use `{name}` (`{tool_id}`)")
                tool_sections.extend(tool_detail_section("Tool Use", idx, tool_id, name, block))
            elif block_type == "tool_result":
                stats["tool_results"] += 1
                tool_id = block.get("tool_use_id") or block.get("id") or f"tool-result-{idx}"
                status = "error" if block.get("is_error") else "result"
                event_lines.append(f"- Tool {status} (`{tool_id}`): {shorten(block_text(block), 240)}")
                tool_sections.extend(tool_detail_section("Tool Result", idx, tool_id, None, block))
            elif block_type in {"thinking", "redacted_thinking"}:
                event_lines.append(f"[{block_type}] {shorten(block_text(block), 500)}")
            else:
                event_lines.append(f"[{block_type}] {shorten(block_text(block), 500)}")
                tool_sections.extend(tool_detail_section("Content Block", idx, block.get("id"), None, block))

        text = "\n\n".join(part.strip() for part in event_lines if part and part.strip())
        if text:
            rendered.append(text)
        elif not chunks:
            rendered.append("_No message content._")
        rendered.append("")

    return rendered, tool_sections, stats


def tool_detail_section(
    label: str, event_index: int, tool_id: Any, name: str | None, payload: dict[str, Any]
) -> list[str]:
    heading = f"## {label}: {name or tool_id or 'unknown'}"
    return [
        heading,
        "",
        f"- Event: `{event_index}`",
        f"- Id: `{tool_id or 'unknown'}`",
        "",
        "```json",
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
    ]


def block_text(block: dict[str, Any]) -> str:
    value = block.get("content", block.get("text", block.get("input", block)))
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def first_user_prompt(events: list[dict[str, Any]]) -> str:
    for event in events:
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        role = payload.get("role") or event.get("role") or event.get("type")
        if role != "user":
            continue
        content = payload.get("content", event.get("content", ""))
        text = extract_text(content)
        if text:
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
            elif isinstance(block, dict) and block.get("type") in {"text", "input_text", "output_text"}:
                parts.append(str(block.get("text", "")))
        return "\n".join(part.strip() for part in parts if part and part.strip())
    return ""


def extract_timestamp(event: dict[str, Any]) -> str:
    value = event.get("timestamp") or event.get("created_at") or event.get("createdAt")
    return str(value) if value else ""


def first_value(events: list[dict[str, Any]], key: str) -> Any:
    for event in events:
        if event.get(key):
            return event[key]
        payload = event.get("payload")
        if isinstance(payload, dict) and payload.get(key):
            return payload[key]
    return None


def detect_session_id(events: list[dict[str, Any]], path: Path) -> str:
    for event in events:
        payload = event.get("payload")
        if isinstance(payload, dict):
            for key in ("id", "session_id", "sessionId"):
                if payload.get(key):
                    return str(payload[key])
        for key in ("sessionId", "session_id", "sessionID"):
            if event.get(key):
                return str(event[key])
    return session_id_from_path(path)


def session_id_from_path(path: Path) -> str:
    stem = path.stem
    if stem.startswith("rollout-"):
        parts = stem.split("-")
        if len(parts) >= 5:
            return "-".join(parts[-5:])
    return stem


def project_key_for(path: Path, source: Path) -> str:
    if source.name == "archived_sessions":
        return "archived"
    try:
        rel = path.relative_to(source)
    except ValueError:
        return path.parent.name
    if len(rel.parts) >= 4:
        return "/".join(rel.parts[:3])
    return rel.parts[0] if rel.parts else path.parent.name


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
        "# Codex Session Markdown Export",
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
