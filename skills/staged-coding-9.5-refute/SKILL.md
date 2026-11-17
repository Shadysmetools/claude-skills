---
name: staged-coding-9.5-refute
description: "staged-coding stage 9.5 - the refuter. A FRESH agent on a model different from the builder, handed only the diff, tries to prove the FIX wrong on its own path and keeps attacking each repaired form until a round comes back clean. Blocking - a kill sends the fix back to stage 4. Signs its ledger line on finish. Triggers: /staged-coding-9.5-refute, or invoked in order by /staged-coding."
---

# Stage 9.5 - the refuter

Part of the `/staged-coding` chain. Runs after stage 9 (verification) and before stage 10 (land).
The conductor carries the cross-cutting rules.

**This is not the council (stage 3).** The council runs BEFORE code exists, on the DESIGN, only on its
markers, and is advisory. The refuter runs AFTER code exists, on the ACTUAL DIFF, on EVERY fix, and is
blocking. Neither can substitute for the other: a council can find that the obvious design does
nothing; only a refuter can find that the built code missed a path.

## Inputs

- **The diff itself.** Never a description of the bug it claims to fix: a defect description invites
  the refuter to re-confirm the defect instead of reviewing the fix. Attach the diff; do not summarize it.
- **Never** the builder's reasoning, file:line citations, queries, method, PR body or ticket text.
- The findings stages 6 and 9 already caught, so the refuter hunts what they missed.

## Who runs it

A FRESH subagent on `config.checker_model`, handed only the inputs above, never the builder's chat
history. **The model must differ from every agent that touched the fix**, author and earlier checkers
included. If the usual split collapsed (an override or fallback put the builder on the checker model),
pick a model none of them used and say so. Four agents on one model agreeing is one agent agreeing
with itself four times.

**Why the path matters more than the headcount:** a second agent handed the author's own query will
"confirm" a wrong claim; a refuter handed only the claim is structurally forced onto a different path.
The bar is verify PLUS refute, never verify twice.

Verifying a DEFECT is real and verifying a FIX is correct are different questions; clearing the first
proves nothing about the second. If a dispatch prompt can be satisfied by re-confirming the original
bug report, it is the wrong prompt.

## Dispatch (paste into the refuter's prompt)

> "Before doing anything else, create `<verdict file path>` and write your current status to it.
> Update it as you go; your final verdict must be in it when you finish. Do not rely on your reply
> reaching the dispatcher; the file is the only channel that counts.
>
> You are reviewing a code change, not a bug report. You receive only the diff: no author reasoning,
> no PR body, no file:line citations, no ticket text. Find your own way into the code from the diff.
> Your job is not to confirm the defect this fix claims to solve; it is to find every way THIS DIFF is
> wrong, incomplete or unsafe. Earlier checks already found: <list>. Find what they MISSED:
> cross-cutting, integration and failure-mode gaps. Assume every completion and readiness claim may be
> wrong. Report; never repair. Give each finding a confidence 0-10."

**Read the verdict file; never wait on a reply.** Silence is not a verdict either way. Do not chase a
silent checker repeatedly or respawn an identical retry expecting a different result. If the file is
still empty after a reasonable window, record the check as **UNDELIVERED**, never as passed.

## Attack checklist (reuse every time)

- Does the guard condition enumerate every real state, or only the states the fix's own test data
  produced?
- Do both ends of the wire (the check and the screen or service it feeds) share ONE definition of the
  same concept, or has the fix quietly introduced a second one?
- Does anything the old path did silently stop happening under the new one (error handling, a field
  sent to a provider, a side effect)?
- Is any wording, label or state the change introduces false in some reachable state?
- Did a previously disabled control become live, wired to a call the server rejects?
- **Sharpest: does the change's OWN TEST mock away the exact failure it would otherwise catch?** Read
  every mock the diff adds or touches and ask what real response it stands in for.

## Rules of the loop

- **The refuter NEVER repairs.** It reports; the builder fixes. A verifier that fixes has become the
  author, and judge != author dies.
- **Confidence >= 7/10 triggers a repair round**; below that, findings are recorded as "noted, not
  blocking", so the loop converges instead of thrashing on hedges. Each round notes whether its
  verdict is coherent with the last round's.
- **Hard-block list:** any finding touching concurrency/races, data loss, auth/permissions or payments
  sends the fix back to stage 4 regardless of confidence or how green everything else is.
- **Refuter kills the claim -> back to stage 4** with what it found. Same honesty rule as stage 8's
  false-success case.
- **Keep attacking the REPAIRED form until a round comes back clean.** Each repair carries its own
  fresh bug: a common pattern is round 1 finds a missed path, round 2 finds a race the repair
  introduced. One round is not enough on changes touching concurrency or live data.
- **Refuter fails to kill it -> proceed to stage 10.**

## Non-skippable on money, auth, entitlements and customer data

For any change touching money, billing, entitlements, authentication or customer data, **`skipped` is
not an available signature.** The stage runs, or the fix does not ship: not to staging, not to
production. Lesson: a fix with a large passing test suite, browser proof in two states, four
same-model checkers and green CI still shipped two customer-facing defects that a different-model
refuter, handed only the diff, found in minutes.

Outside that scope this stage may be skipped with a stated reason, but every fix should get one.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 9.5 ran "<one line of evidence>" --ticket <id> --by <seat>@<checker model> --ledger <path resolved at stage 0> [--post]
```
(or `skipped "<reason>"` / `n-a "<reason>"`, except on money, billing, entitlements, auth or
customer-data changes). A good evidence line gives the round-by-round verdict and, if killed, what was
missed. Example:

```
 9.5 refuter on FIX   ran - round 1 REFUTED (missed the poller path) -> fixed; round 2 REFUTED (repair introduced a race) -> fixed; round 3 SURVIVES
```

## Hand-off

- The fix in its SURVIVED state, with the full refutation history (every round, finding and repair)
  carried into the PR body and the card
- Confirmation no hard-block finding (concurrency, data loss, auth, payments) is still open
- A fix that never reached SURVIVES does not proceed to stage 10; it stays in the stage 4 loop
