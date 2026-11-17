---
name: staged-coding-4-build
description: "staged-coding stage 4 - build, the loop's return point. Test-first in vertical slices, fixes every call site of a shared helper, and stops after three failed attempts at the same defect. Signs its ledger line on finish. Triggers: /staged-coding-4-build, or invoked in order by /staged-coding."
---

# Stage 4 - build (the loop's return point)

Part of the `/staged-coding` chain. Runs after stage 3 (plan) and stage 3.5 (pre-mortem) and before
stage 5 (house style). **This is also the return point of the inner loop**: stage 8 (prove it),
stage 8.5 (design match) and stage 9.5 (refuter) send you back here on a failure. Stages 8 and 8.5
share one cap of `config.max_prove_rounds` rounds before the run must stop and report honestly; a
stage 9.5 kill always comes back here, and the refuter keeps attacking the repaired form. Runs on
`config.builder_model`. The conductor carries the cross-cutting rules; read them there.

## Inputs

- The plan from stage 3 (or its "skipped, mechanical" note) and the council verdict if one sat.
- **Stage 3.5's failure-modes table**: each row with TEST? = N becomes one of the tests written first.
- On a loop-back: what broke, what was tried, and the round count so far.

## What to do

Test-driven development (use a TDD skill if you have one): one failing test -> minimal code to pass
-> repeat. **Vertical slices only**: never write all the tests and then all the code. Each test
responds to what the previous cycle taught you.

On an EPIC, build every slice in this one run, slice by slice inside this stage.

**Shared helpers:** if the fix lives in a shared/exported helper, grep **every** call site and fix or
explicitly defer each one, not just the call site that surfaced the bug.

### Rules

(a) **Three strikes.** Count fix attempts. After the THIRD failed attempt at the same defect, stop:
it is an architecture problem, not a hypothesis problem. Write down what was tried and why each
failed, then ask the project owner (or sit the council; marker (a) has now fired by definition)
before any fourth attempt. Never a fourth attempt on the same theory.

(b) **What counts as RED.** A valid RED is a new test that exercises the buggy path and fails on it.
A compile or syntax error is not RED. `ran` on this stage means a test failed BEFORE the code existed.

(c) **Migration safety.** If the diff touches database migrations, apply the checklist stage 3.5 wrote.

(d) **Tag temporary instrumentation** with a unique marker such as `[DEBUG-<4 hex>]` on every log
line added while debugging. Cleanup before stage 10 is one grep for the tag. Untagged debug logs are
the ones that leak into production.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 4 ran "<red->green cycles, call-site sweep result, migration checklist status, debug tag>" --ticket <id> --by <seat>@<model> --ledger <path resolved at stage 0> [--post]
```

A good evidence line proves the RED happened before the code. If tests were written after the
implementation, the honest line is `skipped "tests written after the implementation"`, not `ran`.
Re-runs append (round 2, round 3) - that is honest history. Example:

```
 4  build (TDD)   ran - red->green, 14 tests; 3 call sites fixed, 0 deferred; no migration touched
```

## Hand-off

- Working code with tests that failed red before they passed green.
- Every call site of a touched shared helper, fixed or explicitly deferred and named.
- Any `[DEBUG-xxxx]` tags still in the diff, flagged for cleanup before stage 10.
- Feeds stage 5 (house style) and stage 6 (gate).
