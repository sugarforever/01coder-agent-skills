#!/usr/bin/env python3
"""Dependency-free assert test for extract_session_signals.py.

Run: python3 test_extract_session_signals.py
Exits 0 on success, non-zero (AssertionError traceback) on failure.
"""
import json
import os
import subprocess
import sys
import tempfile

FIXTURE = '''# Claude Session test

## Timeline

### 1. permission-mode

### 5. user - 2026-04-27T15:04:41.796Z

把 tweet 翻译成博客，开头引用原文

### 6. assistant - 2026-04-27T15:04:48.802Z

好的

### 7. user - 2026-04-27T15:05:00.000Z

- Tool result (`toolu_x`): some output

### 9. user - 2026-04-27T15:05:10.000Z

<local-command-caveat>Caveat...</local-command-caveat>

### 11. user - 2026-04-27T15:05:20.000Z

Base directory for this skill: /x

### 20. user - 2026-04-27T18:30:00.000Z

This session is being continued from a previous conversation that ran out of context.
'''


def run(md_path):
    here = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(here, 'extract_session_signals.py')
    out = subprocess.check_output([sys.executable, script, md_path])
    return json.loads(out)


def main():
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(FIXTURE)
        path = f.name
    try:
        data = run(path)
    finally:
        os.unlink(path)

    ps = data['prompts']
    got = [p['text'][:20] for p in ps]
    assert data['human_prompt_count'] == 2, f"expected 2 human prompts, got {data['human_prompt_count']}: {got}"
    # event 5 = a real human prompt, no arc break
    assert ps[0]['event_index'] == 5, ps[0]
    assert ps[0]['text'].startswith('把 tweet'), ps[0]
    assert ps[0]['arc_break'] is False, ps[0]
    # events 7 (tool result), 9 (caveat wrapper), 11 (skill injection) excluded; assistant 6 excluded
    # event 20 = continuation summary: kept but flagged as an arc boundary (marker + >2h gap)
    assert ps[1]['event_index'] == 20, ps[1]
    assert ps[1]['arc_break'] is True, ps[1]
    assert 'gap' in ps[1]['arc_break_reason'], ps[1]
    assert 'marker' in ps[1]['arc_break_reason'] or 'continuation' in ps[1]['arc_break_reason'], ps[1]
    print('OK: all assertions passed')


if __name__ == '__main__':
    main()
