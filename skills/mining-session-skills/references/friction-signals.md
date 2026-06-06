# Friction signals (step 3)

Read the mined arc and look for these signals. Each is a clue that reusable knowledge changed hands. Always capture the evidence reference (event index / line from `extract_session_signals.py`, or a `<tool_call_NNNNNN>` ref) so the proposal is auditable.

## Signal taxonomy

1. **User corrections / redirections** — "no, do X instead", "主语有冲突", "that's not what I meant". The strongest signal: the model did the obvious thing and the user had to steer. Capture what the model assumed vs. what the user wanted.
2. **Repeated manual tool sequences** — the same ordered set of commands run several times (e.g. fetch → translate → cite → publish). Recurrence = automatable workflow.
3. **Dead-ends & backtracking** — the model tried an approach, abandoned it, tried another. The successful path is worth encoding; the dead-ends are worth warning against.
4. **Domain knowledge the user supplied** — conventions, gotchas, project rules the model could not have known ("always quote the original at the top", "check the reply thread for corrections"). This is the highest-value skill content.
5. **Recurring asks** — the user typed essentially the same prompt more than once across the arc (or you know from context they do it often). Per Simon Willison: repeated prompts → make a skill.

## How to record evidence

For each candidate, list 2–4 concrete references: `event 6`, `event 7`, or `<tool_call_000012>` from the sidecar. The proposal must let the user verify the claim without re-reading the whole session. Pull the sidecar (`tool-details/<id>.tools.md`) only for the specific refs that matter.
