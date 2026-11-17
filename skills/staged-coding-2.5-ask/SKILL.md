---
name: staged-coding-2.5-ask
description: "staged-coding stage 2.5 - ask the owner what is genuinely unclear (blocking). One batched question set, before any code is written, about product decisions and ticket ambiguities only - never technical unknowns the codebase can answer. Signs its ledger line on finish. Triggers: /staged-coding-2.5-ask, or invoked in order by /staged-coding."
---

# Stage 2.5 - ask the owner what is genuinely unclear (BLOCKING)

Part of the `/staged-coding` chain. Runs after Stage 2 (restraint) and before Stage 3 (plan).
Callable alone (e.g. to interview the owner about someone else's PR before it is built further); the
conductor carries the cross-cutting rules.

## Inputs

- The ticket / slices read together in Stage 1
- The build / will-not-build list from Stage 2
- `config.project_owner`: the person whose decisions this stage collects

## Why this exists

Without it, the pipeline's escape hatches all fire mid-run, on the agent's own judgment, after
building has started: self-grilling interrogates the agent, not the owner, and a `NEEDS_CONTEXT`
self-report at the end is easy to soften. Nothing turns to the owner before work begins.

The failure it prevents: a slice built exactly as written can contradict itself (e.g. a picker whose
headline list is people who cannot open the thing being sent to them), and a run can quietly make a
real product call (e.g. "new records only") that the owner never made.

## What to do

1. **Read every slice together and write down each genuinely open item.** Classify before asking:
   - **Product decision**: only the owner can answer (who sees what, what happens to existing data,
     whether a behaviour is acceptable). **ASK.**
   - **Ambiguity in the ticket**: the words admit two readings that lead to different code. **ASK**,
     naming both readings.
   - **Technical unknown**: the codebase can answer it. **DO NOT ASK.** Go read the code. Search the
     board and the repo before spending the owner's attention.
   - **A dependency the owner already paused or ruled on**: say what it blocks and confirm the slice
     is still wanted now.
2. **One batch, max 4 questions, each with options and a recommendation** (e.g. a single
   `AskUserQuestion` call). Never a prose wall, never one question per turn for independent items.
3. **Nothing genuinely unclear -> say so in ONE line and proceed.** This gate must not become
   ceremony. A mechanical fix with an unambiguous ticket asks nothing and says "nothing unclear,
   proceeding": that sentence is the receipt that the gate ran.
4. **Record the answers in the PR body and on the card**, so the built behaviour traces to a decision
   rather than an assumption.

Do not re-litigate a spec the owner already approved. If your product spec process resolved
something, it is resolved: read the epic before asking. This gate is for what the spec left open or
what has changed since.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 2.5 <ran|skipped|n-a> "<one line of evidence>" --ticket <id> --by <seat>@<model> --ledger <path from stage 0> [--post]
```

A good evidence line names the questions asked and where the answers were recorded (PR body + card),
or is the literal receipt "nothing unclear, proceeding". Silence is neither. Example:

```
2.5  ask the owner  ran  - 3 questions, answers on the card
```

## Hand-off

- The owner's answers (or the "nothing unclear, proceeding" receipt), recorded on the PR body and the
  card, so Stage 3 plans against decisions rather than assumptions
