---
name: worktree-shipper
description: Safely close out a git worktree after shipping. Verifies everything is committed, pushed and merged, THEN removes the worktree and its branch; refuses to delete anything that would lose work. Use when the user says "/worktree-shipper", "ship this worktree", "close the worktree", "clean up worktrees after merge", or after a PR from a worktree merges.
---

# Worktree Shipper: commit, verify, then delete

Mechanizes "delete the worktree after merge" WITHOUT the risk of deleting unshipped work. Works on
any repo.

## Configuration
- **Search roots**: the current repo by default; the user may name more folders. Worktrees are
  whatever `git worktree list` reports (commonly under `.claude/worktrees/`).
- **Protected branches** `PROTECTED`: default `main, master, develop` plus any long-lived deploy or
  staging branches the user names. These are never deleted, pushed to or treated as candidates.
- **Deploy branches** `DEPLOY_BRANCHES`: branches that count as "merged into" (default `main`; add
  staging branches if your flow merges there first).

## Procedure (per worktree; if no arg, list all candidates and ask)

1. **Identify**: `git -C <repo> worktree list --porcelain`. Never operate on the main checkout or on
   a checkout of a `PROTECTED` branch.
2. **Committed?** `git -C <wt> status --porcelain`. Dirty -> STOP and show the files. Attended: offer
   to commit them (conventional message) on the worktree's own branch. Headless: refuse and report
   `needs input:`.
3. **Pushed?** `git -C <wt> log @{u}..HEAD --oneline` (no upstream = unpushed). Unpushed -> push the
   branch with `git push -u origin <branch>`. NEVER to a protected branch, never `--force`.
4. **Merged?** Prefer `gh pr list --head <branch> --state merged` or
   `gh pr view <branch> --json state,mergedAt`; fall back to `git branch -r --merged origin/<b>` for
   each `DEPLOY_BRANCHES` entry. Merged into ANY deploy branch counts. Not merged -> do NOT delete;
   report the status (PR open? no PR?) and stop. Offer to open a draft PR if none exists.
5. **Delete (only after steps 2-4 all pass)**:
   - `git -C <repo> worktree remove <wt>` (no `--force`; if it refuses, something is dirty, go back to step 2)
   - `git -C <repo> branch -d <branch>` (lowercase `-d` only; it refuses if unmerged)
   - `git -C <repo> worktree prune`
6. **Receipt**: one line per worktree: removed (branch, merged-into, PR number) or kept (exact reason
   and what is needed).

## Batch mode ("clean up all worktrees")
Classify every worktree first:

| Bucket | Meaning |
|---|---|
| FINISHED | clean, pushed, merged |
| NEEDS-INPUT | dirty, unpushed, or ambiguous |
| ACTIVE | commits in the last few days, PR open |
| PARKED | old, unmerged, no PR |

Show the table, then delete ONLY the FINISHED bucket after one confirmation. Never touch the rest.

## Hard rules
- Never `worktree remove --force`, never `branch -D`, never delete a dirty or unmerged worktree, never touch stashes.
- Anything ambiguous (detached HEAD, missing remote, merge conflicts) -> report, don't guess.
