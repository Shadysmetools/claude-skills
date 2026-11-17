---
name: staged-coding-3.5-premortem
description: "staged-coding stage 3.5 - pre-mortem. Before any code exists, table every way the change can fail silently, plus rollback and migration safety. Signs its ledger line on finish. Triggers: /staged-coding-3.5-premortem, or invoked in order by /staged-coding."
---

# Stage 3.5 - pre-mortem (what breaks, and does anyone see it)

Part of the `/staged-coding` chain. Runs after stage 3's plan and before stage 4 writes any code.
Callable alone, but the conductor carries the cross-cutting rules (unit of work = the whole epic,
lane, which model builds vs checks, the ledger law, stop conditions). Read those there.

**Why this stage exists.** Stage 6 hunts swallowed errors AFTER the code is written. Nothing asks
"what happens when this throws and nobody is watching" BEFORE. Lesson: one unguarded call on a null
can blank a whole page while every check stays green. A pre-mortem is cheap before the code exists
and expensive to reconstruct after it ships.

## Inputs

- The plan from stage 3 (or, on a mechanical ticket that skipped 3, the ticket plus stage 1's traced call path).
- The lane (BUG or EPIC) and the list of files/paths the change will touch.
- Stage 1's live-state read (what the real data looks like).

## What to do

### 1. The failure-modes table - every touched code path gets a row

| CODEPATH | FAILURE MODE | RESCUED? | TEST? | USER SEES? | LOGGED? |
|---|---|---|---|---|---|

One row per code path the change touches: the render expression, the API call, the DB write, the
queue read. For each: what can fail (null, timeout, empty result, partial write, double-fire), is it
caught, is there a test for that path, what the user sees when it happens, does it log.

**Mechanical rule, no judgment: any row with RESCUED = N, TEST = N and USER SEES = silent/blank is a
CRITICAL GAP.** It does not proceed to stage 4 as-is: either the plan grows a rescue plus a test for
it, or the row is explicitly accepted with a reason on the ticket.

A small ticket produces a small table; two rows is a fine pre-mortem for a one-line fix. Do not pad
it, and do not skip it because the fix "obviously can't fail".

### 2. The five production lenses - yes/no each, one line each

Security & Auth - Data Integrity - Payments & Webhooks - Operations - User Experience.
For each: does this change touch it, and if yes, what is the failure cost there. Data Integrity
specifically asks: **are retries idempotent for every write and webhook this change touches** (can
the same action fire twice without double-writing)?

### 3. Rollback plan - one sentence, written now

How does this change get undone if it is wrong on staging or production? Usually one line ("revert
the squash commit"). If the honest answer is "it can't be" (a data repair, a migration that drops
something), that is a **council marker (c) trigger - the council sits before stage 4** (see stage 3).
A change with no stated rollback and no council is not eligible to build.

### 4. Migration safety - only when the diff will touch database migrations

Write the checklist stage 4 must obey (stage 4 applies it; you declare it):
- no full-table locks;
- no `NOT NULL` added without a default;
- indexes created concurrently where the database supports it;
- schema migrations and data migrations never mixed in one file;
- renames via expand-contract (add new, backfill, switch readers, drop old - separate migrations);
- tested against production-sized data, not an empty table.

**A migration file in the repo is not a migration that reached the database** - name which
environment(s) it must land in. No migration in the diff: one line, "no migrations touched."

### Output

The table, lenses and rollback sentence go into the plan file (or, when stage 3 was skipped as
mechanical, into the run folder as `premortem.md`). Every accepted TEST? = N row becomes a test
stage 4 writes FIRST. The pre-mortem is stage 4's test list, not a ceremony.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 3.5 ran "<rows> failure rows, <n> critical gaps closed, rollback: <one word>, migrations: <touched|none>" --ticket <id> --by <seat>@<model> --ledger <path resolved at stage 0> [--post]
```

(`skipped "<reason>"` or `n-a "<reason>"` are allowed, but think hard first: this stage exists
precisely because small fixes skip it.) Example ledger line:

```
 3.5 pre-mortem   ran - 4 rows, 1 critical gap (null render path) -> test added to plan, rollback: revert, migrations: none
```

## Hand-off

- Stage 4 receives the failure-modes table (every accepted TEST? = N row is a test it writes first) and the migration checklist if one applies.
- Stage 6's silent-failure sweep re-checks the same rows against the code as built.
- Stage 10's PR body carries the rollback sentence (its "Revert:" line).
