---
name: staged-coding-5-style
description: "staged-coding stage 5 - house style (front-end only). Applies your framework's best-practices skill to any diff that touched front-end code; n-a on server-only diffs. Signs its ledger line on finish. Triggers: /staged-coding-5-style, or invoked in order by /staged-coding."
---

# Stage 5 - house style (front-end only)

Part of the `/staged-coding` chain. Runs after stage 4 (build) and before stage 6 (gate). Callable
alone (e.g. to re-run the style pass on someone else's front-end diff). The conductor carries the
cross-cutting rules; read them there.

## Inputs

- The diff from stage 4, and whether it touched any path under `config.frontend_dirs` or is server-only.

## What to do

If the diff touched front-end code, apply your framework's best-practices skill (e.g. a React
best-practices skill: rendering, data fetching, bundle size, re-render rules) and fix what it finds
in the changed code. If you have no such skill, apply your repo's documented front-end conventions.

If the change is server-only, sign `n-a` with a one-line note. Do not restyle code the diff did not touch.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 5 ran "<specific best-practice findings addressed>" --ticket <id> --by <seat>@<model> --ledger <path resolved at stage 0> [--post]
python <staged-coding skill dir>/scripts/sign.py sign 5 n-a "server-only diff" --ticket <id> --by <seat>@<model> --ledger <path resolved at stage 0> [--post]
```

Example ledger line:

```
 5  house style   n-a - server-only diff
```

## Hand-off

- A style-clean diff (or the honest `n-a` for server-only work), ready for stage 6.
