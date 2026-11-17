---
name: staged-coding-7-browser
description: "staged-coding stage 7 - get a real logged-in browser. Starts the app locally first, then logs in via cookie import or the configured test account; never a real customer account. Signs its ledger line on finish. Triggers: /staged-coding-7-browser, or invoked in order by /staged-coding."
---

# Stage 7 - get a real logged-in browser

Part of the `/staged-coding` chain. Runs after stage 6 (gate) and before stage 8 (prove it).
Callable alone (e.g. to re-establish a session that expired mid-run). The conductor carries the
cross-cutting rules; read them there.

## Inputs

- A clean diff that passed stage 6.
- The need for a real, logged-in browser session to drive stage 8's proof.

## Decide WHERE you are logging in first

**Local first.** Start the app from your worktree with `config.local_start` and open
`config.local_url`. Proof must run against YOUR diff:
- a diff that touches any path in `config.server_dirs` must be proved with the server running
  locally too, not a local client talking to a deployed API (that never executes your server change);
- logging in to `config.staging_url` proves the deployed build, not your diff - that is stage 10's
  post-merge check, not this one.

**Parallel lanes:** if several runs prove side by side, each gets its own port. Read your port off
the start command's output; never assume the default, and never stop another lane's server to take
its port.

## What to do

Get a real session in the automation browser (Playwright MCP, a Chrome automation tool, or similar):
1. **Cookie import** - import an existing logged-in session (e.g. `/setup-browser-cookies`) for the
   local or test environment; or
2. **Test account** - log in with the credentials in the env vars named by
   `config.test_account.user_env` / `config.test_account.password_env`. Never echo the password.

Rules:
- Never use a real customer's account. Never drive the user's personal browser profile; use a
  dedicated automation browser or profile.
- If the browser tool is busy or jammed, fall through to a fresh isolated session, then to headless.
  "The browser was busy" is not an outcome.
- When the test is what a signed-out stranger sees, deliberately use a clean signed-out session and
  say so.

Verify the session: load an authenticated page and confirm it renders (not the login page).

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 7 ran "<which tool/session, which URL (local/staging), logged in as test account or signed-out by design>" --ticket <id> --by <seat>@<model> --ledger <path resolved at stage 0> [--post]
```

`n-a` only when the change has no screen and no user-reachable effect (e.g. a pure background job),
with that reason. Example ledger line:

```
 7  logged-in browser   ran - local server + client up, test account session verified
```

## Hand-off

- A live, logged-in (or deliberately signed-out) real browser session against your diff, ready for stage 8.
