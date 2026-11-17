---
name: kpi-healer
description: Self-healing loop for your product KPIs. Reads every open or regressed KPI issue, re-verifies it against live data, clusters issues by root cause, files real bugs only after a two-agent verify/refute bar, spawns fix agents that open PRs (never merge), and updates each issue's status with evidence. Triggers - "/kpi-healer", "heal the KPIs", "work the KPI issues", or a daily KPI-healer routine.
---

# KPI Healer

"Self-healing workers checking every KPI issue, verifying it and updating it, so the KPIs get
smarter every day." The healer never trusts yesterday's status: every run re-proves each issue
from live data, then either closes it with evidence, escalates it, or ships a fix PR.

## Configuration (`KPI_HOME`, default `./kpi`)

| Item | What it is |
|---|---|
| `scorecards/<date>.json` | Today's KPI scorecard: `[{ "id", "category", "value", "target", "status": "green|amber|red" }]`. If missing, run your scorer command (`SCORER_CMD`) first. |
| Issue store | One row per issue: `id, kind, category, status (open/acknowledged/regressed/auto_resolved/resolved), evidence, last_seen_at, ticket, pr`. Any table or a `issues.jsonl` file works. If it does not exist yet, build the list from the scorecard and say so. |
| `KPI-OWNERS.md` | Category -> owner agent/role (e.g. "Ingestion -> backend agent"). |
| `KPI-PLAN.md` | Targets and dates per KPI (context only). |
| Tracker | GitHub repo/project (or any tracker with search + create). |

Credentials come from your environment or a secrets file; never print them.

## Who runs it
Run as a tech-lead agent. It dispatches the category **owner agents** from `KPI-OWNERS.md`, but only
for categories with red KPIs or new/regressed issues, max 3 in parallel. Each owner runs steps 1-5
for its own KPIs and writes `owners/<category>/<date>.md`; the tech lead consolidates into
`healer/<date>.md`.

## Loop (per run)

0. **Optional pre-checks.** Run any cheap verifier jobs you have (e.g. an independent quality check
   such as `transcription-check`) and treat their failures as issues like any other.
0.5. **Optional bounded auto-retry** for transient failures (timeouts, 429/5xx, rate limits) on items
   your app can safely re-run:
   - Only retry items whose failure cause is clearly transient. Never retry user-side, missing-file
     or "no fault" cases, or anything a user already retried.
   - Write the issue row as `open` BEFORE the call, so a crash still counts as the one retry.
   - **One retry per item, ever.** Afterwards mark it `resolved` (verified healthy) or `regressed`
     (left for a human, never retried again).
   - Hard daily caps on count (e.g. 5) and spend (e.g. $0.50). Stop on any unpriced or unmeasurable spend.
1. **Verify.** For each open, acknowledged or regressed issue, re-check the condition against live
   data: the exact query and its counts, never memory.
   - Gone -> `auto_resolved` with evidence.
   - Still true -> keep it; refresh `last_seen_at` and evidence.
   - Someone marked it resolved but it is still true -> `regressed`.
2. **Cluster.** Group open issues by root cause (same check + same reason + same code path).
   One cluster = one ticket.
3. **Ticket.** For each cluster without a ticket, search the tracker (all states) for a duplicate.
   - Duplicate -> link it and comment the new evidence.
   - New -> apply the **two-agent bar**: an independent verifier (not the finder) must reproduce it,
     AND an adversarial refuter told to prove it wrong must fail. File only if it survives; link it.
4. **Fix.** For each ticketed cluster without an open PR, spawn ONE fix agent that:
   - creates its own branch in a fresh worktree (`git worktree add -b <branch> ...`),
   - writes a failing test first, then the fix,
   - pushes only its own branch and opens a PR referencing the ticket.
   Record the PR on the issue.
5. **Update.**
   - Every open/acknowledged/regressed issue gets one recheck entry with its query and result.
   - Every category in `KPI-OWNERS.md` gets one owner report per run, even if it is "checked, nothing to do".
   - Reject any status change without evidence.
   - Re-run the scorer and write `healer/<date>.md`: verified / auto-resolved / regressed / new
     tickets / PRs opened / blocked, each with evidence and links.
   - **Time budget** (for scheduled runs, e.g. a 45-minute kill): dispatch nothing new after ~20 min;
     write the report by ~38 min and end the turn even if agents are still running.
6. **Tell the user**: one line per change.

## Limits (change only on the user's say-so)
- **Never merge** a PR, never promote to production, never push to a shared branch. PRs only.
- **Data writes:** only the issue store and its event/report logs, plus the bounded retry in 0.5.
  No writes to user data.
- **Agents:** max 4 at once, max 3 new fix PRs per run.
- **Paid APIs:** none beyond the normal Claude run, except jobs with an explicit daily cap. Other
  vendor calls need the user's per-run OK.
- **Evidence or it didn't happen:** every status change carries the query/log/API field that proves it.
  An unverifiable issue stays `open` with "needs human check", never resolved.
- No customer names or secrets in reports, tickets or chat messages.
