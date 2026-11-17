---
name: staged-coding-2-restraint
description: "staged-coding stage 2 - restraint (decide what NOT to build). Runs a do-less pass and applies the lane-specific guard - BUG lane against over-building, EPIC lane against under-building. Signs its ledger line on finish. Triggers: /staged-coding-2-restraint, or invoked in order by /staged-coding."
---

# Stage 2 - restraint (decide what NOT to build)

Part of the `/staged-coding` chain. Runs after Stage 1 (recon) and before Stage 2.5 (ask the owner).
Callable alone; the conductor carries the cross-cutting rules.

## Inputs

- What already exists (reuse candidates) and the call path traced in Stage 1
- The lane: BUG (bugs board) or EPIC (product board), set once at the start of the run

## What to do

Run a do-less pass (a YAGNI / minimalism skill if available, e.g. `ponytail`; otherwise do it by
hand). Question whether the task needs to exist at all; reach for the standard library before custom
code, native platform features before dependencies, one line before fifty. A guardrail that is only
referenced, never run, enforces nothing: actually run it.

**The failure direction depends on your lane.** The two lanes drift in OPPOSITE directions, so "be
restrained" means different things:

- **BUG lane -> guard against over-building.** The risk is wandering past the defect into adjacent
  code that was never broken. This is NOT the same as Stage 4's "fix every call site of the same
  defect" rule: widening to every sibling of the SAME defect is required; drifting into unrelated
  nearby code because you are already in the file is the over-building this guard stops. Same file,
  two different instincts. Know which one you are following.
- **EPIC lane -> guard against under-building.** The risk is trimming a slice until it no longer meets
  its own WHEN/THEN/SHALL acceptance criteria and calling the gap "restraint". A slice that misses a
  criterion is not lazy in the good sense; it is incomplete.

Output: a short list of what you will build and what you deliberately will not.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 2 <ran|skipped|n-a> "<one line of evidence>" --ticket <id> --by <seat>@<model> --ledger <path from stage 0> [--post]
```

A good evidence line names what you WILL build, what you will NOT, and which failure direction you
guarded against. Example:

```
2  restraint  ran  - reused <helper>; did NOT build <thing>; BUG lane, guarded against over-building
```

## Hand-off

- The build / will-not-build list, which feeds Stage 2.5's questions (a trimmed scope can turn an
  ambiguity into something worth asking) and Stage 3's plan
