---
name: staged-coding
description: "The CONDUCTOR of a 16-stage coding pipeline (staged-coding-0-chase through staged-coding-10-land) that takes one ticket or one whole epic from open PRs to a proven, landed change. Fixed order, nothing skipped; every stage signs a clock-stamped evidence ledger; independent fresh-model checkpoints judge the builder's work. Triggers: /staged-coding, work this ticket, build this properly, run the pipeline."
---

# staged-coding: the conductor

A fixed-order implementation pipeline for one repo. This file owns the ORDER, the cross-cutting
rules and the signing law. Each stage is its own skill and must sign its work before the next starts.

Use it on the repo you configured in `.staged-coding.json` (copy `config.example.json` from this
folder to the repo root and fill it in). Small throwaway changes elsewhere do not need it.

## The chain

```
0 chase -> 1 recon -> 2 restraint -> 2.5 ASK THE OWNER -> 3 plan+council -> 3.5 PRE-MORTEM -> 4 BUILD
   -> 5 style -> 6 GATE -> 7 browser -> 8 PROVE IT -> 8.5 DESIGN MATCH -> 9 verify -> 9.5 REFUTER -> 10 land
     (8 or 8.5 fails -> back to 4, SHARED round cap . 9.5 kill -> back to 4 . a stage signs before the next starts)
```

| # | Stage | Skill | Run by | Signs as |
|---|---|---|---|---|
| 0 | chase open PRs (+0.5 pick a ticket) | `/staged-coding-0-chase` | builder | `@<builder_model>` |
| 1 | recon | `/staged-coding-1-recon` | builder | builder |
| 2 | restraint | `/staged-coding-2-restraint` | builder | builder |
| 2.5 | ask the owner | `/staged-coding-2.5-ask` | builder | builder |
| 3 | plan + council | `/staged-coding-3-plan` | builder (council only on the four markers) | builder |
| 3.5 | pre-mortem | `/staged-coding-3.5-premortem` | builder | builder |
| 4 | build (TDD) | `/staged-coding-4-build` | builder | builder |
| 5 | house style | `/staged-coding-5-style` | builder | builder |
| 6 | self-check gate | `/staged-coding-6-gate` | **FRESH subagent on `checker_model`** | `@<checker_model>` |
| 7 | logged-in browser | `/staged-coding-7-browser` | builder | builder |
| 8 | prove it in the browser | `/staged-coding-8-prove` | builder | builder |
| 8.5 | design match (front-end only) | `/staged-coding-8.5-design` | **FRESH subagent on `checker_model`** | `@<checker_model>` |
| 9 | verification | `/staged-coding-9-verify` | builder | builder |
| 9.5 | refuter on the FIX | `/staged-coding-9.5-refute` | **FRESH subagent on `checker_model`** | `@<checker_model>` |
| 10 | land | `/staged-coding-10-land` | builder | builder |

Run each stage by invoking its skill, in order, never skipping. A stage that does not apply still
runs far enough to sign `n-a` with a reason.

Two loops, deliberately:
- **Inner (8 / 8.5 -> 4):** you cannot reach stage 9 until the feature demonstrably works AND matches
  the approved design. The two share ONE cap (`config.max_prove_rounds`, default 3); then stop and
  report honestly.
- **Outer (across runs, stage 0):** every run starts by re-checking the PRs this pipeline opened
  before. Work that stops at "a PR exists" is the disease this pipeline exists to kill.

## The unit of work is the whole epic, not a slice

Build every slice of an epic in ONE run: one branch, one PR. The fixed cost of a run (recon,
gating, browser proof, landing) is large and barely moves with ticket size; on a measured run it was
about 75 of 90 minutes, with 15 minutes of actual coding. Split an epic into four runs and you pay
that four times, re-read the same code four times and open four PRs where one belongs. Holding all
slices in view during recon is also how cross-slice bugs get caught.

Batch the whole epic through stages 1-10 once; build slice by slice inside stage 4; prove every
slice in one stage 8 pass; grade slices separately at the end.

A worker never decides alone to skip a slice. If a slice is genuinely done already or needs an
action only the owner can take, raise it at stage 2.5, get it confirmed, and say so in the report.

## Lane: bug or epic (decide once, at stage 0)

| | BUG lane (`config.boards.bugs`) | EPIC lane (`config.boards.product`) |
|---|---|---|
| ticket source | your bug-filing process | your product spec process |
| next ticket | strict severity: ALL P0 before any P1, then P2; only ready states, never raw ideas | the slice order the epic's plan sets |
| DONE means | the defect no longer reproduces | every WHEN/THEN acceptance criterion passes |
| restraint guards against | **over-building** (drifting past the defect) | **under-building** (missing a stated criterion) |

The lanes fail in opposite directions; stage 2 names which one yours guards against.

## Which model builds, which model checks

- **Build** on `config.builder_model` (default a fast, capable model at high effort), with a fallback model if it is unavailable.
- **Checkpoints** (6, 8.5, 9.5) run as FRESH subagents on `config.checker_model`, handed only what the
  stage needs, never the builder's chat history. **Judge is never the author**: `sign.py check`
  flags any checkpoint signed by the builder's model.
- Using the strongest model to write the code was tried; it worked but cost several times more tokens
  before a single PR. Spend the strong model on judging.

## Council and refuter are two different checks; you need both

| | Council (stage 3) | Refuter (stage 9.5) |
|---|---|---|
| When | BEFORE code | AFTER code |
| On what | the intended design | the actual diff |
| Who | two independent advisors, ideally different vendors | one fresh agent |
| Told to | advise and disagree with each other | destroy the claim; default to refuted |
| Answers | "is this the right thing to build?" | "does what you built actually do it?" |
| Weight | advisory; the owner may overrule | **blocking**; a kill sends you back to stage 4 |
| Fires on | the four markers only | every fix, always |

They cannot substitute for each other. On one real ticket the council found that the obvious
implementation would delete zero rows (no diff existed for a refuter to see), and the refuters then
found that the built fix missed the majority case and that the repair introduced a race. Keep
attacking the REPAIRED form until a round comes back clean: each repair carries its own fresh bug.

"No council marker fired" must be shown: the council's ledger line enumerates the markers checked.
When the council is overruled, keep its findings; only the recommendation was rejected.

## The signing law

Every stage, when it finishes, runs the signer in this folder:

```
python <this skill dir>/scripts/sign.py sign <stage> <ran|skipped|n-a> "<one line of evidence>" \
  --ticket <id> --by <seat>@<model> --ledger <ledger path> [--attach <image> ...] [--post]
```

- Appends a **clock-stamped** line (UTC time, git sha, sha256 of attachments) to the run's ledger.
- `--post` also comments it on the ticket, so the tracker's server clock becomes a second timeline
  no agent controls.
- **One ledger path, resolved once at stage 0** (`<worktree>/.staged-ledger-<ticket>.jsonl`, add it to
  `.git/info/exclude`) and passed explicitly on EVERY call, including checkpoint subagents. A
  subagent has its own working directory; letting it guess forks the ledger.
- **Re-runs append.** Stage 4 signed three times renders `(round 3)`. That is honest history.
- **The PR body's STAGE LEDGER is rendered, never typed**: `sign.py render --ledger <path>`. Stage 10
  runs `sign.py check`, signs itself right before `gh pr create`, then `check --all` and `render`.
- The render ends with `gate sha <sha> . N commits since`. N > 0 means code changed after the stage 6
  gate; stage 9 must send the run back through stage 6.

Safe points to compact context: after 2.5, after 3.5, after 6, after 9.5. Never mid-build (4) or
mid-proof (8).

## The stage ledger: every stage reports, or the run is non-compliant

Each line is exactly one of:
- `ran` plus one line of evidence (what was run, what it returned)
- `skipped: <reason>`, a real reason, in the open
- `n-a: <reason>`, genuinely does not apply (stage 5 on a server-only diff)

```
STAGE LEDGER - <ticket>
 0   chase open PRs      ran     - 2 open from prior runs, both rebased
 1   recon               ran     - traced X -> Y -> Z; live read: 7 of 7 rows stale
 2   restraint           ran     - reused <helper>; did NOT build <thing>
 2.5 ask the owner       ran     - 3 questions, answers on the card
 3   plan + council      n-a     - markers checked: (a) no auth/data (b) no prior attempts (c) not irreversible (d) constraints clear
 3.5 pre-mortem          ran     - 4 rows, 1 critical gap closed
 4   build (TDD)         ran     - red then green, 14 tests
 5   house style         n-a     - server-only diff
 6   self-check gate     ran     - bug hunt clean, security 0 findings, simplicity 1 deletion
 7   logged-in browser   ran     - local app up, test session injected
 8   prove it            ran     - 1 round, screenshot attached
 8.5 design match        ran     - verdict ship; happy/empty/error states
 9   verification        ran     - 6 claims, 6 verified
 9.5 refuter on the FIX  ran     - round 1 REFUTED (missed path) -> fixed; round 2 SURVIVES
 10  land                ran     - merged to staging, proven live, production PR open
```

The three stages that actually get skipped, each with a comfortable excuse:
1. **Stage 4's test-first order.** Tests written after the code pass by construction. If no test
   failed before the code existed, the honest line is `skipped: tests written after the implementation`.
2. **Stage 6's gate.** "CI will run it" is wrong twice: CI runs after the PR, and CI rarely runs a
   security or simplicity review of your own diff. Three passes, named separately.
3. **Stage 9.5's refuter on the FIX, not on the finding.** Refuting the bug report is a different,
   earlier bar. This stage hands a fresh agent "this change fixes it" and lets it attack.

**A rule with no receipt cannot be enforced**: a stage that leaves no trace looks the same as a stage
that never ran. Do not pad the ledger. Honest `skipped` and `n-a` lines are fine; `ran` beside a
stage that did not run is a falsehood on a permanent record.

## Preconditions: refuse to start without these

- `.staged-coding.json` exists in the repo root (else copy `config.example.json` and ask the owner to fill it).
- A ticket: handed in, or self-selected per stage 0.5. Nothing eligible -> stop and ask.
- `config.home_checkout` is on `config.base_branch` and clean. Never branch or commit there; it is
  the read-only home base. All work happens in a worktree.
- Only tickets from `config.boards.bugs` or `config.boards.product`.

## Stop conditions

- A PR opened without the rendered STAGE LEDGER in its body -> non-compliant, whatever the code does.
- `sign.py check` reports a missing stage or judge == author -> the run is not done.
- Stage 6 cannot be made clean -> `BLOCKED`, no PR.
- Stage 8 / 8.5 exhausts the round cap -> `BLOCKED`, no PR, honest hypothesis.
- **The owner has not approved the local proof -> no PR.** Owner unreachable -> HOLD with no time
  limit. Holding is not going quiet: write the proof to disk, sign the ledger, update the card, ask,
  and keep working on anything independent.
- A product decision discovered mid-build -> `NEEDS_CONTEXT`, hand it to the owner, never guess.
  If it was visible in the ticket before the run, stage 2.5 was skipped or careless.
- Stage 2.5 skipped entirely -> non-compliant. Its receipt is the owner's answers or the line
  "nothing unclear, proceeding".
- Never merge into `config.prod_branch`. Merging to `config.staging_branch` after checks pass and
  OPENING the promotion PR are required. Open the door; the owner walks through it.
- Finishing at "merged to staging" is INCOMPLETE: the production PR must be open and the owner told,
  in plain words, that it is waiting for their click.
- No before/after images (or a written substitute) on the card -> do not open the production PR.
- Proof that exists only as a committed file is not proof: many hosts render HTML as source. Publish
  it somewhere viewable (`config.proof_publish`) and link it on the card.
- An epic with N slices owes N+1 proof artifacts: one per slice plus an end-to-end roll-up.
- Stage 8.5: a slice changes a screen but there is no approved design -> STOP; never invent the
  design mid-build.

## Verify before you cite

A file, a comment or a merged PR page is a claim somebody made once; only the code, the running
system and the branch are true now. Before naming a file, key or behavior, check it exists.
