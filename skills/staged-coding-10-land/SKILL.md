---
name: staged-coding-10-land
description: "staged-coding stage 10 - land. Get the owner's OK on the local proof, open the PR with the signed ledger, merge to staging, prove it live, publish the proof and update the card, then OPEN (never merge) the production PR and stop. Signs its ledger line twice. Triggers: /staged-coding-10-land, or invoked in order by /staged-coding."
---

# Stage 10 - land it, merge it, prove it live, report it, open the door to production

Part of the `/staged-coding` chain. Runs last, after stage 9.5's refuter survives. The conductor
`/staged-coding` carries the cross-cutting rules; read them there. Settings come from
`.staged-coding.json` (`config.<key>`).

## Inputs

- The surviving refuter verdict from stage 9.5 (a killed claim never reaches this stage)
- The ledger file with every prior stage signed (the one path resolved at stage 0)
- Evidence: the stage-6 gate findings, the stage-8 browser-proof screenshots
- The ticket id (or every slice id, for an epic) and the working branch

## Before anything: the ledger must be complete

```
python <staged-coding skill dir>/scripts/sign.py check --ledger <ledger path>
```

Exit 3 lists every unsigned stage (and any checkpoint signed by the builder's own model). An
unsigned stage means the pipeline is not done, whatever the code looks like. Stage 10 is excluded
by default because it signs right before the PR opens. Always pass the same `--ledger` path every
stage used; a different path reports every stage MISSING.

Then `sign.py render --ledger <ledger path>` prints the STAGE LEDGER block. Read its tail:
`gate sha <sha> . N commits since` - N>0 means code changed after the stage-6 gate ran. Go back and
re-run stage 6 first.

## What to do

The builder owns the whole loop: PR, merge to staging, card, live proof, report, production PR.
"A PR exists" is not done; a pile of correct, unmerged drafts helps nobody.

0. **Show the project owner the local proof and wait for their word - BEFORE the PR exists.**
   Post, in order: (a) one line naming what the ticket asked for, (b) the stage-8 screenshot of the
   change working on `config.local_url`, (c) for a fix or guard, the BEFORE image too (a fix with no
   failing before-image proves nothing), (d) the one-line live-data check if the ticket writes
   anything. Ask with a multiple-choice question (approve / change something / stop), never a prose
   question.
   **Their answer is the gate. `gh pr create` does not run before it.** Lesson: correct code still
   ships wrong (a reason hidden in a tooltip, a feature built on the wrong page); one look from the
   person who asked catches it while it is cheap.

   **Owner not reachable: HOLD. No PR, no time limit, no "declare the deviation" escape.** But
   holding is not going quiet - a session that ends takes unwritten state with it. In the same turn:
   - write the proof down (screenshots at a durable path, ledger signed, card updated);
   - send the approval request up to whoever can reach the owner (manager seat / `SendMessage`),
     naming ticket, screenshot path and the one question;
   - keep working on anything independent; if nothing can proceed, say so and ask for an instruction.
   Never record approval that was not given.

   Once approved, move the card to the `Local proof` column (`config.card_columns`) and post the
   published proof link on it (see step 6). If the bug board has no such column (its stages mean
   "where the code lives"), move or mirror the card to a board that does and leave a pointer comment;
   never invent a stage.

1. **Open the PR - not a draft** (`gh pr create --base <config.staging_branch>`, no `--draft`).
   - **Cut your branch from `origin/<config.staging_branch>`**, always. A branch cut from a base
     that has drifted carries unrelated commits and comes out conflicting.
   - **One PR per ticket** (one per epic for epic work - all slices built together in one run). A
     batch cannot be partially reverted and nobody can review it. Never open a PR carrying another
     worker's commits.
   - **The PR carries its screenshot**: a PR that proves itself in an image is seconds to review.
   - Paste the stage-6 gate findings and stage-8 evidence into the body. Reference the ticket on its
     own line in whatever exact form your ticket-gate CI parses, and reference the slice the CODE
     delivers, not a sibling slice that holds its specs. If your gate requires the card to be in a
     given column first, move it before opening.
   - Add a one-line revert path while everything still works:
     `Revert: git revert --no-edit <squash-merge sha>` (for an already-promoted change: "open a revert PR").
   - **Scan at the sink:** write the exact body to a temp file, scan THAT file for secrets
     (tokens, passwords, `Bearer`/`api_key` shapes, the test account's password), then send that same
     file. Same for every card or comment post.

2. **Merge it to `config.staging_branch`** once checks pass: `gh pr merge --merge --delete-branch`.

3. **Move the card** to the column meaning "landed on staging" - only after the merge happened.

4. **Prove it live on `config.staging_url`** in a real browser and screenshot it. Stage 8's local
   proof does not excuse this. Depth scales with the diff: docs-only -> skip (say so); config-only ->
   surface answers and the changed value is live; backend -> drive the endpoint and read logs;
   frontend -> full drive plus screenshot. Name the depth in the evidence line.

5. **Write the whole outcome on the card**: what changed, the merge, the live result, the
   screenshot. The card is the record - not the PR, not a chat message.

6. **Emit and PUBLISH the proof page. Every ticket.** Proof a non-coder cannot open is a claim with
   a screenshot filed somewhere else.
   - Build one self-contained HTML page: plain-English "what was broken" and "what is different now",
     before/after screenshots **embedded as data URIs**, the checks that ran with results, ticket and
     PR links, and a "deliberately not done" list. **No screenshot -> no page.**
   - **Render and measure it before calling it delivered**: open it, check
     `document.body.scrollWidth` vs the viewport, confirm zero page errors.
   - **Publish it via `config.proof_publish`** (an artifact host, a public pages site, image comments
     on the PR) and post THAT link. A `proof.html` committed to a private repo shows raw markup and
     is not proof. Keep the local file as the durable record.
   - Link it from three places: a PR comment, the card, and the report to the owner.
   - **An epic with N slices owes N+1 artifacts**: one per slice proving that slice's own acceptance
     criteria, on that slice's card, plus a roll-up on the epic proving the whole journey end to end
     as a real user lives it. The roll-up is new work, not a concatenation - slices can each pass
     while the assembled feature is unusable. A ticket without slices owes exactly one.

7. **Attach before and after IMAGES to the slice card. This gates production.**
   - (a) Images, not PDFs - they preview inline. Number them (`1 BEFORE ...`, `2 AFTER ...`).
   - (b) On the SLICE, never the epic. The epic carries only a roll-up line: "N of M slices proven".
   - (b2) The image must prove THAT ticket's own claim. Identical images on two cards is a smell:
     justify it explicitly or replace it. Prove the decisive half, not the photogenic half - for an
     invisible behaviour (server refusal, skipped job, denied permission) capture the two responses,
     the log line, or the query output before and after. State the environments when before and
     after came from different machines.
   - (c) **No before/after pair -> no production merge.** Staging is unaffected.
   - (d) No screen at all (background job, data repair): the card must say in plain words how it was
     proven instead - the test red before and green after, the query and its output, the live check.
     An honest "no image, here is the evidence" is a record; an irrelevant screenshot is worse than
     nothing.
   - Upload files from disk with your tracker's CLI/API (never paste base64 into the conversation),
     save images where they survive the session, then **list the card's attachments and paste the
     returned ids into your report**. Mark the card with a line `PROOF: screenshot - <what you did and
     saw>` (or `PROOF: fault-drill - ...` / `PROOF: none-possible - <reason>`) on every ticket the PR
     names. Writing `PROOF: screenshot` with nothing attached is worse than an honest `none-possible`.
   - Re-read your own posted note: escaped markup renders as unreadable text.

8. **Open the production pull request - and STOP there.** The ticket is not done without it; a fix
   nobody promotes lives on staging forever.
   ```
   gh pr create --base <config.prod_branch> --head <promotion branch> --title "[<seat>][<slug>] promote: <one line>" --body-file <body>
   ```
   - **NEVER `gh pr merge` a PR targeting `config.prod_branch`.** Opening is the builder's; merging is
     the owner's, always. Any production gate holding it is the gate working.
   - Step 7(c) gates the MERGE, not the OPEN: open the PR even when evidence is thin and NAME the gap
     prominently in its body. A promotion silently held back is indistinguishable from one nobody cut.
   - **Promote your own work and nobody else's - and check it.** Right after opening, run
     `gh pr view <n> --json commits --jq '.commits | length'`. If it carries more than your commits,
     close it, cut a fresh branch from `origin/<config.prod_branch>`, `git cherry-pick <your merge sha>`,
     confirm `git diff origin/<config.prod_branch>..HEAD --stat` is exactly your files, and open from there.
   - Body: STAGE LEDGER, full clickable ticket URL(s), an `Agent: <seat> . run <n>` line, the revert line.
   - **Then tell the owner in plain words: it is done, the proof is on the ticket, and the
     production PR is open and waiting for their click.** That sentence is the deliverable.
   - Anything publishing to the public web still waits for the owner's own click.

### The line

The builder writes, merges to staging, proves, reports, and opens the door to production. The owner
walks through it. Any temptation to merge a PR aimed at `config.prod_branch` -> stop.

### State + report

Record per ticket: id, slug, worktree path, branch, PR URL, gate verdict (first attempt clean?),
stage-8 round count, stage-9.5 verdict (and Stage 4 rounds it cost if killed), live-proof result and
depth, evidence paths, merge sha, card column, attachment ids, production PR URL.

Report in **plain English** - assume a non-coder reader. Open with three lines: what you did, what
changed for them, what you need from them. Define technical terms on first use.

Self-report exactly one of: **DONE** / **DONE_WITH_CONCERNS** / **NEEDS_CONTEXT** / **BLOCKED**.

## Sign it - TWICE

Stage 10's signature is read by CI before the stage finishes, so it signs at two milestones.

**Round 1 - the instant before `gh pr create`:**
```
python <staged-coding skill dir>/scripts/sign.py sign 10 ran "PR opening - ledger complete; merge, live proof and production PR follow" --ticket <id> --by <seat>@<model> --ledger <ledger path>
python <staged-coding skill dir>/scripts/sign.py check --all --ledger <ledger path>   # must exit 0
python <staged-coding skill dir>/scripts/sign.py render --ledger <ledger path>        # -> PR body
```
Without round 1 the render shows `10 land MISSING` and an honest PR fails the gate.

**Round 2 - the LAST act, after the production PR is open and the owner has been told:**
```
python <staged-coding skill dir>/scripts/sign.py sign 10 ran "staging PR merged <sha>, card moved, live-proof <depth>, production PR open <url>" --ticket <id> --by <seat>@<model> --ledger <ledger path> --attach <ledger path> --post
```
Then refresh ONLY the ledger block in the existing PR body - never replace the whole body:
```
gh pr view <n> --json body -q .body > body.md
# replace the lines from "STAGE LEDGER" through the "gate sha" line with a fresh `sign.py render`
gh pr edit <n> --body-file body.md
```
Every other line (ticket reference, `Agent:` line, revert line, evidence) must survive byte for
byte; a body wiped by a bare render fails the ticket gate on the already-merged PR. Attach the
ledger file to the card too - cleanup is about to delete the local copy.

**Worktree cleanup happens ONLY AFTER round 2** (the ledger lives in the worktree). Use the
`worktree-shipper` skill, and only remove worktrees under prefixes you own; anything else is
someone's workspace - refuse and report.

## Hand-off

- A ledger whose stage-10 evidence still reads "PR opening - ledger complete" means round 2 never
  signed: the next run's stage 0 treats that PR as UNFINISHED, not done.
- The open production PR - the next run's stage 0 chases it (status, merged?, rebase if stale).
- The card, carrying the full write-up and awaiting the owner's review of the production PR.
- Any evidence gap named honestly in the production PR body, so the next run picks it up.
