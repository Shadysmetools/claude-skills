---
name: staged-coding-9-verify
description: "staged-coding stage 9 - refuse to lie. Builds the claim table (every claim this run made, how it was mechanically checked, disposition verified/failed/unsupported/unverifiable), audits plan completion, grades the CARD against the code in both directions, and checks the gate is not stale. Signs its ledger line on finish. Triggers: /staged-coding-9-verify, or invoked in order by /staged-coding."
---

# Stage 9 - refuse to lie

Part of the `/staged-coding` chain. Runs after stage 8.5 (design match) and before stage 9.5 (the
refuter). The conductor carries the cross-cutting rules; read them there.

## Inputs

- Every claim made across this run: stage evidence lines, numbers, file references, behaviour
  claims, citations
- Stage 8's evidence (what you clicked, what you saw, the screenshots). That is this stage's proof,
  not a fresh one
- The gate sha from stage 6, to check staleness
- The ticket card's own text

## What to do

Do not claim done; prove it. Run a verification-before-completion skill if available. The evidence
from stage 8 is the proof and goes in the PR body.

### (a) The claim table

Extract EVERY claim this run has made (numbers like "fixed 7 rows", file references, behaviour like
"the server now returns 400", citations) and give each a row:

| claim | mechanical check (grep count, file exists, query, re-run test) | disposition |
|---|---|---|

Dispositions are exactly **`verified` / `failed` / `unsupported` / `unverifiable`**.
- Any `failed` -> back to stage 4.
- Any `unsupported` claim is DELETED from the PR body and the card. An unbacked number does not ship;
  it dies here.
- `unverifiable` stays, labelled as such, with the reason.

### (b) Plan-completion audit

Every plan item / slice criterion gets DONE / PARTIAL / NOT_DONE / CHANGED / UNVERIFIABLE. A concrete
file path must resolve to DONE or NOT_DONE by checking it exists, never UNVERIFIABLE. Be conservative
with DONE, generous with CHANGED, honest with UNVERIFIABLE.

### (c) "Pre-existing failure" needs receipts

Before calling any failing test or check "pre-existing, not mine", run it on `config.base_branch` and
show it fails there too. Without that repro the claim is deleted.

### (d) Burden of proof is on the claim

Uncertain resolves to FAIL, never pass-by-default. Critique your own checks: flag any assertion a
wrong output could satisfy (a file that exists but is empty is not a pass).

### (e) Staleness

Run `python <staged-coding skill dir>/scripts/sign.py render --ledger <path>` and read the
`gate sha ... N commits since` tail. N>0 means code changed after stage 6's gate ran: re-run stage 6
before proceeding. Any code change after the last test run means the tests re-run too.

## The card-vs-code grade (BLOCKING, both directions)

This is not (b) again. (b) grades the plan YOU made. This grades the CARD: what the ticket promised,
in its own words. Every other stage asks "is the code I wrote correct?"; none asks "does the code
cover what the card promised?" A builder who implements two of five claims, proves those two and signs
honestly produces an all-green run and a false card.

### Direction 1 - over-claiming (the card promises more than exists)

Open the card. Extract EVERY claim in it as its own row (the card's sentences, not your plan or
summary). For each: **IMPLEMENTED / NOT IMPLEMENTED / PARTIAL (name exactly which part)**, with the
file and line that settles it.

**Any NOT IMPLEMENTED or PARTIAL means the slice is NOT DONE.** Write that on the card in plain words
and do not let it move forward wearing a completed label. A slice that ships at 3 of 5 with its card
unchanged is worse than an unfinished slice honestly marked: the board then lies to whoever reads it
next, including the project owner at the approval gate.

**The tell: claims phrased as PROHIBITIONS** ("cannot", "never", "is blocked", "stays hidden") are the
most likely to be unbuilt. A missing lock looks exactly like a working one until someone tries the
door. Grade every prohibition by finding the code that refuses, not by failing to find code that allows.

### Direction 2 - under-claiming (look for the mirror failure deliberately)

- **Code that exists and no claim covers.** Consequence: it gets rebuilt (a duplicate system), or it
  changes behaviour nobody signed off on.
- **A claim the card marks not-done or partial that is actually done.** Consequence: shipped work
  sits invisible and unpromoted, and someone spends a day rebuilding it.

An epic can be understated as easily as overstated; understatement costs a rebuild rather than an
outage, which is why nobody looks for it. **Report both directions in the same table.**

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 9 ran "<one line of evidence>" --ticket <id> --by <seat>@<model> --ledger <path resolved at stage 0> [--post]
```
(or `skipped "<reason>"` / `n-a "<reason>"`). A good evidence line names the claim-table counts, the
plan-audit result, the card-vs-code grade, and the staleness count. Example:

```
 9  verification   ran - claims: 11 verified, 0 failed, 2 unsupported (deleted); plan 6 DONE; card 5/5 implemented, 0 under-claimed; gate 0 commits since
```

## Hand-off

- A PR body carrying only verified claims; every `unsupported` one already deleted
- The plan-completion audit and the card-vs-code table, per slice
- Confirmation the gate is not stale (0 commits since stage 6, or stage 6 re-run)
