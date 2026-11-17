---
name: staged-coding-3-plan
description: "staged-coding stage 3 - plan (only if it needs one), plus a cross-model council that sits inside this stage only when one of four markers fires. Records alternatives considered and appends decisions to disk as they are made. Signs its ledger line on finish. Triggers: /staged-coding-3-plan, or invoked in order by /staged-coding."
---

# Stage 3 - plan (only if it needs one) + council (only on the four markers)

Part of the `/staged-coding` chain. Runs after Stage 2.5 (ask the owner) and before Stage 3.5
(pre-mortem, which reads this plan) and Stage 4 (build). Callable alone (e.g. to re-plan a ticket
that came back from Stage 4 needing a different approach); the conductor carries the cross-cutting
rules, including the "council vs refuter" comparison, which is not repeated here.

## Inputs

- The ticket / slices from Stage 1 and the build / will-not-build list from Stage 2
- The owner's answers from Stage 2.5 (or its "nothing unclear" receipt)
- `config.checker_model` and `config.council_second_opinion` (optional second-vendor CLI)

## What to do

### Plan (only if it needs one)

If the approach is not obvious, write a plan (a plan-writing skill if available, e.g.
`writing-plans`) and name the unknowns. Small mechanical ticket -> skip and say so. If the ticket's
scope feels wrong or underspecified, grill yourself on it (e.g. `grill-me`) rather than guessing.
Self-grilling interrogates YOU; Stage 2.5 interrogates the OWNER. They are not substitutes.

### Council - only on the four markers

The builder writes the code on every ticket (on `config.builder_model`). A council of two advisors
(`config.checker_model` plus, ideally, a second vendor via `config.council_second_opinion`), run in
parallel and told to disagree with each other, sits **only** when a ticket hits one of four markers:

- **(a)** it touches login, credentials, payments or data access;
- **(b)** two or more prior failed attempts at the same defect;
- **(c)** it is irreversible or touches live production data;
- **(d)** the constraints genuinely contradict each other.

Everything else proceeds without one. Most bug fixes have one right answer; two advisors debating an
obvious fix is theatre that slows the queue. Spend cross-model disagreement on real judgment calls.

How a council runs: write a short brief (problem, constraints, the proposed design, what you are
unsure of); give it to each advisor independently; collect verdicts; run one more round where each
sees the other's view if they disagree; record the outcome. The council is advisory: the owner may
overrule it. **When it is overruled, keep its findings**; only the recommendation was rejected, and
a trap the council found can still save the fix.

## Recording rules

(a) **Any plan records "Alternatives considered - and why not", one line each.** A future session
re-litigating the same trade-off needs the rejected options more than the chosen one.

(b) **Every decision is appended to the plan file on disk the moment it is made**, as one table row:
decision | why | confidence 1-10. Never accumulate decisions in conversation context to write up later.

(c) **Each council round ends with a coherence mark**: "this round's verdict matches the prior round:
yes/no", so a reader sees convergence without re-reading transcripts.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 3 <ran|skipped|n-a> "<one line of evidence>" --ticket <id> --by <seat>@<model> --ledger <path from stage 0> [--post]
```

Sign once, covering both halves: whether a plan was written or genuinely skipped, and **which of the
four markers were checked** (not just that none fired; self-judged difficulty under-fires, which is
why the markers are objective). If a council sat, name its verdict and whether the owner overruled
it. Examples:

```
3  plan + council  n-a  - mechanical, approach unambiguous; markers checked: (a) no auth/data, (b) no prior attempts, (c) not production-facing, (d) constraints clear
3  plan + council  ran  - marker (c) irreversible; 2 advisors; verdict: ship part 1 only; OVERRULED by owner, findings kept
```

## Hand-off

- The plan (or the "skipped, mechanical" note) with its alternatives-considered table
- The decision rows appended to disk as they were made
- The council's verdict if one sat, whether it was overruled, and its findings (kept either way),
  for Stage 3.5's pre-mortem and Stage 4's build. Say plainly whether a plan exists for 3.5 to read.
