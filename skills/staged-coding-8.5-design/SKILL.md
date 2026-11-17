---
name: staged-coding-8.5-design
description: "staged-coding stage 8.5 - design match. A FRESH reviewer on config.checker_model judges the built screen against the approved mockup (EPIC lane) or the pre-fix screen (BUG lane), element by element, and returns one word - rebuild, fix or ship. Frontend diffs only. Signs its ledger line on finish. Triggers: /staged-coding-8.5-design, or invoked in order by /staged-coding."
---

# Stage 8.5 - design match (does it look like what was approved, not just work)

Part of the `/staged-coding` chain. Runs after stage 8 proves the feature WORKS and before stage 9.
It is its own signed stage because a sub-paragraph inside another stage leaves no ledger line when
skipped. The conductor carries the cross-cutting rules.

**The failure this stage closes:** an acceptance criterion written as behaviour ("WHEN a user clicks
share, THEN the panel SHALL open") is satisfied by ANY panel that opens. Stage 8 asks "does it work";
this stage asks "does it match what was approved".

**Backend-only diff -> `n-a`, in one line.** Do not manufacture a screenshot for work with no screen.

If the project has a design-review skill or design system checker, run it on the built screen too;
if its verdict contradicts this stage's, say so in the ledger line rather than picking silently.

## Lane difference

- **EPIC lane:** the reference is the approved mockup attached to the epic or slice card (the images
  the project owner approved, not a later-edited design file). **No mockup and the slice changes a
  screen? The epic skipped its own design gate. Say so and STOP. Never invent the design mid-build.**
- **BUG lane:** there is no mockup by design. Judge the AFTER screen against (1) the BEFORE screen,
  with the defect visibly gone, and (2) neighbouring screens / the existing design system, for
  regressions. Same element table, same TYPE/MATERIAL rows, same one-word verdict. Stop-on-missing-
  mockup never fires on the bug lane.

## Inputs

- The reference: approved mockup (EPIC) or BEFORE screen + neighbours (BUG)
- **BEFORE screenshot**: the screen on pre-fix code (stage 8's rig with the old code, or staging
  before the merge)
- **AFTER screenshots in every state the mockup shows**: happy, empty, error, loading. Named
  `<interaction>-before.png` / `<interaction>-after-<state>.png`

## The judge is fresh, and it is not the builder

Spawn a FRESH subagent on `config.checker_model` (if unavailable, a different strong model, announced
in the evidence). Hand it ONLY the three image sets and the slice's own acceptance criterion. **Never
the builder's summary, never the chat history.** It builds its element inventory from the screenshots
FIRST, before reading anything the builder wrote, so it cannot be anchored by the builder's framing.

## The reviewer's method (put this in its prompt)

1. **Inventory first.** List every salient element visible in the AFTER screenshots (layout regions,
   controls, text, states) before consulting the mockup or the criterion.
2. **Classify every built element and every mockup element** as exactly one of: **match** /
   **acceptable adaptation** / **missing** / **contradicted** / **added without approval**. An
   adaptation counts as intentional only if it cites evidence: a recorded answer from the project
   owner (stage 2.5), an accessibility need, a product truth. **An uncited deviation is a defect,
   not a choice.**
3. **Two mandatory rows on top: TYPE and MATERIAL.** TYPE = does the typography carry the mockup's
   character (scale, weight, hierarchy), not merely "text is present". MATERIAL = flat-CSS imitation
   where the mockup shows depth, texture or photography. Imitation material is the most reliable mark
   of machine-made design.
4. **Judge every state the mockup shows.** A matching happy path with an unstyled error state is `fix`.
5. **The verdict is derived from the table, never felt, and is exactly one word:**
   **`rebuild`** (the structure is wrong) / **`fix`** (named elements off, list attached) / **`ship`**.
   The builder and the conductor report that word verbatim; they have no authority to soften it.

## The loop

- **`ship`** -> sign and proceed to stage 9.
- **`fix` / `rebuild`** -> back to stage 4 with the reviewer's list. **Shares stage 8's
  `config.max_prove_rounds` cap**: rounds here and in stage 8 count together, then STOP with an
  honest `blocked`.
- **Re-score after a fix:** the SAME reviewer re-reads the SAME screenshot paths (fresh captures to
  the same names, never names it invents), marks each prior finding `resolved / partial / unresolved`,
  and separately hunts for **up to 3 NEW regressions the fix itself introduced**. `partial` or
  `unresolved` can never recompute to `ship`.

## Evidence lands on the card

Attach mockup + before + after to the SLICE card with numbered display names (`0 MOCKUP ...`,
`1 BEFORE ...`, `2 AFTER ...`, since attachment lists rarely preserve upload order), and put the
classification table in the same note. Stage 10 rolls this up; the images must prove THIS slice's claim.

## Sign

Signed by the REVIEWER's identity, not the builder's; that is the point:

```
python <staged-coding skill dir>/scripts/sign.py sign 8.5 ran "verdict: ship - 12 match, 2 cited adaptations, 0 missing; states happy/empty/error" --ticket <id> --by <seat>@<checker model> --ledger <path resolved at stage 0> --attach "0 MOCKUP panel.png" "1 BEFORE panel.png" "2 AFTER panel-happy.png" [--post]
```
(or `n-a "backend-only diff, no screen"`, signed by the builder). A good evidence line carries the
one-word verdict, the classification counts, the round, and which states were judged. Example:

```
 8.5 design match   ran - verdict: ship (round 2: 2 resolved, 0 new regressions), states happy/empty/error
```

## Hand-off

- Stage 9's claim table inherits "matches the approved mockup" as a verified claim, with this
  signature as its check.
- Stage 10 attaches nothing new for design; it only verifies this stage's numbered set landed.
