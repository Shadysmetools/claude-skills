---
name: staged-coding-0-chase
description: "staged-coding stage 0 - chase what's already open (and stage 0.5 - pick a ticket if none was handed to you). Re-checks every PR this pipeline opened previously, resolves the run's ledger path, and when self-selecting enforces strict severity order. Signs its ledger line on finish. Triggers: /staged-coding-0-chase, or invoked in order by /staged-coding."
---

# Stage 0 - chase what's already open (+ Stage 0.5 - pick a ticket)

Part of the `/staged-coding` chain. Runs FIRST, every run, before Stage 1 (recon). Callable alone
(e.g. to re-check a prior run's open PRs without starting a new ticket), but the conductor
`/staged-coding` is the normal door and carries the cross-cutting rules (unit of work = the whole
epic, lane = bug vs epic, which model builds vs checks, the ledger law, stop conditions). Read those
there; do not duplicate them here.

## Inputs

- `.staged-coding.json` in the repo root (see the conductor's `config.example.json`)
- `state/pipeline-prs.json` (or your own equivalent): the list of PRs this pipeline opened previously
- Whether the project owner or a dispatching agent already named a specific ticket (decides whether
  Stage 0.5 runs at all)
- Read/write access to `config.boards.bugs` and `config.boards.product`
- `config.home_checkout` on `config.base_branch` and clean. It is the read-only home base: never
  branch or commit inside it.

## What to do

### Resolve the ledger path (once, for the whole run)

The ledger is `<worktree>/.staged-ledger-<ticket>.jsonl` (add it to `.git/info/exclude`). Resolve it
here and pass the SAME path as `--ledger` on every sign call for the rest of the run, including
calls made by checkpoint subagents. A subagent has its own working directory; letting it pick a path
silently forks the ledger and makes `check` report stages missing that genuinely ran.

### Stage 0 - chase what's already open (run FIRST, every run)

For every PR this pipeline opened previously and has not yet confirmed live:

| Found state | Action |
|---|---|
| Merged + deployed | Check the live surface (a post-deploy check if you have one). Clean -> mark the ticket genuinely done. |
| Merged, not yet verified | Verify now. This is the step that closes "chase to live". |
| Open, quiet for 2+ runs | Rebase on the latest `origin/<config.base_branch>`, re-run the Stage 6 gate, and name it in the report as awaiting a human click. |
| Open, conflicting | Resolve conflicts, push, report. |
| Branch merged but new commits stacked on it | Cut a fresh branch off `origin/<config.base_branch>` carrying that work forward and open a new PR. A merged PR's branch is dead; commits added after the merge route nowhere. |

Nothing open -> say so in one line and continue. Never skip this stage; it is half the point.

### Stage 0.5 - pick a ticket if none was handed to you

If the project owner or a dispatching agent already named a ticket, work that one and skip this.

EPIC lane: self-selection simply follows the slice order the epic's own plan already sets.

BUG lane self-selection:
- **Strict severity order.** Finish every open P0 before touching any P1; every P1 before any P2;
  and so on. Never interleave.
- **Pull only from `config.boards.bugs.ready_states`** (e.g. Backlog, Planning): the states a ticket
  sits in before code exists for it, which is exactly this pipeline's window.
- **Never pull from the new / untriaged column.** A card there may not have passed your
  verification bar yet (independent verify + failed adversarial refute). Working an unverified
  candidate as if it were a confirmed defect is the failure this exclusion prevents.
- **Never pick a ticket because it looks easy or sits near something you just touched.** Severity
  order only, no convenience picks.

## Supporting rules

(a) **PR age policy for chased PRs.** Open and quiet 7 days -> post a nudge comment naming what it
waits on; 14 days -> report it as stale to the project owner; 30 days -> propose closing, with what
the branch carries. NEVER auto-close: a PR carrying work is salvaged first.

(b) **"Flaky or real?" before calling a PR blocked on CI.** Re-run the failed check once. Passes ->
note `flaky` on the PR and move on; fails again -> it is real, and the PR is blocked.

(c) **A chase failure on one PR (API error, unresolvable conflict) does not abort the run.** Log it
in the ledger evidence and continue. Only the ticket's own stages are critical path.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 0 <ran|skipped|n-a> "<one line of evidence>" --ticket <id> --by <seat>@<model> --ledger <path resolved above> [--post]
```

Sign as `0` once, folding any Stage 0.5 outcome into the same line. A good evidence line names every
PR checked with its state and the action taken (or says plainly nothing was open), and, if a ticket
was self-selected, which one and why it was next in the queue. Example:

```
0  chase open PRs  ran  - 2 open from prior runs, both rebased; self-selected the next P0 in Backlog
```

## Hand-off

- The ticket to work (handed in or self-selected) and its lane (bug vs epic)
- The ledger path, to be passed explicitly to every later stage
- Confirmation that no previously opened PR was left unaddressed this run
- The home checkout confirmed on `config.base_branch` and clean, ready for Stage 1
