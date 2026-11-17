---
name: golden-qa-regression
description: Run a browser QA regression of a live web app against a prebuilt golden reference and test matrix. Drives a real authenticated browser, captures screenshots, console and network evidence, compares each step with the written Expected Result, and writes PASS/FAIL/BLOCKED plus new bugs back into the matrix. Use when the user says "/golden-qa-regression", "run the qa regression", "qa the matrix", "run the golden-reference tests", or asks for a full regression pass. Self-contained - runs in a fresh session.
---

# Golden-Reference QA Regression

You execute a prebuilt QA kit against a running app. **The kit is the oracle**: never invent
expected behavior, read it.

## The kit (configure paths once, e.g. in the repo's CLAUDE.md)

| Item | Default | Contents |
|---|---|---|
| `MATRIX` | `qa/TEST-MATRIX.xlsx` (or `.csv`) | sheet `Test Cases`; columns `ID, Feature Area, Entry Route, Precondition, Test Data, Steps, Expected Result, Persona, Priority, Status, Notes / Evidence, Linked Bug` |
| `GOLDEN` | `qa/happy-paths/<area>.md` | what "correct" looks like per area |
| `PLAYBOOK` | `qa/PLAYBOOK.md` | click-by-click action scripts per case (optional) |
| `RUNBOOK` | `qa/QA-RUNBOOK.md` | safety rules for this app |
| `FIXTURES` | `qa/REAL-DATA-SCENARIOS.md` | named test data |
| `EVIDENCE` | `qa/_evidence/` | screenshots per case |
| `APP_URL` | `https://app.example.com` | the app under test |

No matrix yet? Offer to draft one from the golden reference first, and stop until the user approves it.

## Step 0: Authenticate
Prefer importing the user's already-logged-in browser session (cookie import) into the QA browser,
or let the user log in once and take over. Verify: load an authenticated page and confirm it renders
(not the login page). If it bounces to login, STOP and ask.

## Step 0.5: Production safety rails (non-negotiable)
- Reads anywhere. **Writes and destructive actions only inside a sandbox** (e.g. a project named
  `__QA_SANDBOX__` created by the QA account).
- **Never complete a payment or change a plan.** For billing, assert the UI / error code and cancel
  before any charge.
- Never delete real accounts, projects or data; never act on another user's pending items.
- Anything that needs a destructive action on real data -> mark `BLOCKED` ("needs sandbox/staging").

## Step 1: Load the work list
Default scope = rows with `Status = Not Run`, **Critical first**, then by Feature Area. Let the user
narrow it ("just Auth", "only Critical"). For each case, also read its area's golden file and its
playbook steps if present.

## Step 2: Run each case in the browser
Use a browser automation tool (Playwright MCP, Chrome automation, etc.). For each case:
1. Set persona context: new user -> empty sandbox; heavy user -> populated account.
2. Navigate to `Entry Route`; satisfy `Precondition`; apply `Test Data` (fixtures where named).
3. Execute `Steps`.
4. **Capture evidence**: screenshot to `EVIDENCE/<ID>.png`, key console logs, and the load-bearing
   network request (`METHOD path -> status`).
5. **Compare** observed vs `Expected Result`. Negative / empty / blocked cases PASS when handled
   gracefully (right message, right status code, no crash).

## Step 3: Write the verdict
Write back to the matrix row: `Status` = PASS / FAIL / BLOCKED and `Notes / Evidence` = a one-line
verdict plus evidence (e.g. `POST /api/items 200; item listed`). On FAIL, append a row to a `Bug Log`
sheet (summary, severity P0-P3, area, suspected root cause `file:line` if known) and put its ID in
`Linked Bug`. Recompute the summary tallies. Use a small script (e.g. Python `openpyxl`) rather than
hand-editing; if the file is open in Excel, writes fail, so ask the user to close it.

## Step 4: Scale it
Batch by area. Drive ONE authenticated browser sequentially for anything that writes (a shared
browser cannot truly parallelize). You may fan out READ-ONLY assertion cases to parallel QA subagents.

## Step 5: Evidence standard and known-bug regression
- **Never mark PASS without proof** (screenshot, clean console, 2xx body, or a DB row).
- Re-verify every entry already in the `Bug Log` and mark fixed / still broken with evidence.

## Step 6: Session report
Counts (PASS / FAIL / BLOCKED, per area), new bugs (IDs + severity), and top regressions. Point the
user at the updated matrix and the evidence folder.
