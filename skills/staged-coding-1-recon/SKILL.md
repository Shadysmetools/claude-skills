---
name: staged-coding-1-recon
description: "staged-coding stage 1 - recon (read before you write). Traces the real call path, checks live database state in every environment, and forces the caller list, live data and the ticket's instruction into the evidence before any hypothesis is allowed. Signs its ledger line on finish. Triggers: /staged-coding-1-recon, or invoked in order by /staged-coding."
---

# Stage 1 - recon (read before you write)

Part of the `/staged-coding` chain. Runs after Stage 0 (chase) and before Stage 2 (restraint).
Callable alone (e.g. to re-run recon on someone else's PR); the conductor carries the cross-cutting
rules.

## Inputs

- The ticket (or, for an epic, every slice) and its lane, from Stage 0
- The repo's architecture map, if it has one (e.g. `docs/architecture/CODEBASE-MAP.md`)
- Read-only access to live data: `config.database.read_only_query_cmd` (or an equivalent MCP) for
  each environment, plus any app-level read API
- Your notes on each external vendor the change touches (how it is wired for you, which keys and
  clients it uses, and known past defects with that vendor). Read them first if they exist: a known
  defect class is cheaper to look up than to re-derive.

## What to do

**Trace the real call path** of whatever you are about to touch. State plainly what already exists
before proposing to build anything new. Reuse beats build: a second parallel implementation of
something that already exists is a classic "dual-system" bug.

**Live-state READ.** Source and docs describe intent; they do not describe what is stored. Before
assuming the defect lives in the code, look at the real data the ticket is about (query the relevant
tables read-only) and the real server state (env config, a running process, a queue depth) if either
is plausibly involved. Sometimes the problem isn't in the code: the numbers in the database don't
match what the user sees, and reading source forever will never reveal that. Skip only when the
ticket is genuinely code-only (copy fix, build config, pure refactor) and say so in one line. Skip by
judgment, never by default.

**Schema truth, in every environment.** If the change references a column, a status value or a
migration, confirm it exists in the LIVE database of both staging and production, and **count rows;
do not merely check that the query succeeds.** A retired column can return empty rather than an
error, so a query that runs proves nothing; and a migration file in the repo is not a migration that
reached the database. Fires on schema-referencing diffs only.

## Forcing rules

(a) **BUG lane: red command first.** Before forming any hypothesis, name ONE command you have
already run that goes RED on this exact symptom and will go GREEN when fixed (a failing test, a curl
returning the wrong body, a CLI diff, a headless-browser step, a query returning the wrong count). No
red command -> no hypothesis, and this stage does not sign `ran`. Building the feedback loop is most
of debugging.

(b) **Forced facts.** The evidence line must contain three things or the stage did not run:
1. the caller list: how many call sites, in which files (summarised grep output, not "I checked");
2. the real data shape read LIVE: table + row count, or the actual value seen;
3. the ticket's instruction, quoted verbatim in one line.
Forcing the facts out works; asking "are you sure you checked?" does not.

(c) **Candidate-bound scope.** Once the defect's file is named, read THAT file and its import chain.
Wanting to grep the whole repo again signals the candidate was wrong: say so in the evidence rather
than widening silently.

(d) **Note the touched area's conventions in one line** (naming, error-handling style, where tests
live) so the fix does not introduce a style a reviewer then has to flag.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 1 <ran|skipped|n-a> "<one line of evidence>" --ticket <id> --by <seat>@<model> --ledger <path from stage 0> [--post]
```

Missing any of the three forced facts means the stage did not run. Example:

```
1  recon  ran  - traced X->Y->Z; 4 call sites in 3 files; live read: 7 of 7 rows stale; ticket says "..."
```

## Hand-off

- What already exists (reuse candidates) and the call path traced
- Live-state and schema-truth findings, per environment
- The touched area's conventions, in one line
- All of this feeds Stage 2's restraint list and Stage 3's plan
