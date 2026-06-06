#!/usr/bin/env python3
"""Extract clean human prompts + arc-boundary hints from an exported Claude session markdown.

Encodes the input-robustness rules from the mining-session-skills spec:
- tolerate the real exported header format `### N. <type> - <ISO>`
- distinguish human prompts from tool results / skill injections / command wrappers
- flag likely topic-arc boundaries (large time gaps, compaction/continuation markers)

Usage:
    python3 extract_session_signals.py <exported-session>.md
Outputs JSON to stdout: {session_file, human_prompt_count, prompts: [...]}.
Each prompt: {event_index, line, timestamp, arc_break, arc_break_reason, text}.
"""
import datetime
import json
import re
import sys

HEADER = re.compile(r'^### (\d+)\. ([a-z0-9-]+)(?: - (.+))?\s*$')
ARC_GAP_SECONDS = 2 * 60 * 60  # >2h between human prompts hints a new topic arc

# Body prefixes that mark a `user` turn as NON-human (tool plumbing / skill injection)
NONHUMAN_PREFIXES = (
    '- Tool result',
    '- Tool error',
    '[{',
    '{ "',
    '{"',
    'Base directory for this skill',
)
# Substrings that mark a turn as a command/local wrapper, not a human prompt
WRAPPER_SUBSTR = (
    '<local-command-caveat',
    '<command-message',
    '<command-name',
    '<local-command-stdout',
)
# Markers that hint a conversation boundary (compaction / continuation)
ARC_MARKERS = (
    'continued from a previous conversation',
    'ran out of context',
    'Compacted',
)


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError:
        return None


def is_human(kind, body_text):
    if kind != 'user':
        return False
    t = body_text.strip()
    # discard sub-4-char ACK turns ("ok", "y", "好的")
    if len(t) <= 3:
        return False
    if any(t.startswith(p) for p in NONHUMAN_PREFIXES):
        return False
    if any(w in t for w in WRAPPER_SUBSTR):
        return False
    return True


def parse_turns(lines):
    """Yield ((event_index, kind, ts_str), start_line, body_lines)."""
    cur = None
    start = 0
    buf = []
    for i, ln in enumerate(lines, 1):
        m = HEADER.match(ln)
        if m:
            if cur:
                yield cur, start, buf
            cur = (int(m.group(1)), m.group(2), m.group(3))
            start = i
            buf = []
        elif cur:
            buf.append(ln)
    if cur:
        yield cur, start, buf


def extract(path):
    with open(path, encoding='utf-8') as fh:
        lines = fh.read().splitlines()
    prompts = []
    prev_ts = None
    for (idx, kind, ts_s), start, buf in parse_turns(lines):
        body = '\n'.join(buf).strip()
        if not is_human(kind, body):
            continue
        ts = parse_ts(ts_s)
        reasons = []
        if any(mk in body for mk in ARC_MARKERS):
            reasons.append('compaction/continuation marker')
        if ts and prev_ts and (ts - prev_ts).total_seconds() > ARC_GAP_SECONDS:
            reasons.append(f'>{ARC_GAP_SECONDS // 3600}h gap from previous prompt')
        prompts.append({
            'event_index': idx,
            'line': start,
            'timestamp': ts_s,
            'arc_break': bool(reasons),
            'arc_break_reason': '; '.join(reasons),
            'text': body,
        })
        if ts:
            prev_ts = ts
    return {'session_file': path, 'human_prompt_count': len(prompts), 'prompts': prompts}


def main(argv):
    if len(argv) != 2:
        print('usage: extract_session_signals.py <exported-session>.md', file=sys.stderr)
        return 2
    json.dump(extract(argv[1]), sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
