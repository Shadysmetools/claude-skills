---
name: staged-coding-6-gate
description: "staged-coding stage 6 - self-check (the gate). A fresh checker subagent runs a bug hunt, a security review and a simplicity review against the diff until clean, plus a silent-failure sweep and quote-or-demote finding rules. Signs its ledger line on finish. Triggers: /staged-coding-6-gate, or invoked in order by /staged-coding."
---

# Stage 6 - self-check (the gate)

Part of the `/staged-coding` chain. Runs after stage 5 (house style) and before stage 7 (logged-in
browser). The conductor carries the cross-cutting rules; read them there.

## Inputs

- The full diff since the branch was cut.
- The ticket (for spec-compliance: what was actually asked).
- Whether the diff touches security-sensitive surface (auth, payments, credentials, data access).

## Who runs it: a FRESH checker, never the builder

Stage 6 is a CHECKPOINT, not build work. Spawn a **fresh subagent on `config.checker_model`** (Agent
tool, the strongest model you have, maximum effort), handed only the diff and the ticket, never the
builder's chat history. It signs with `--by <seat>@<checker_model>`, so judge != author is visible
in the ledger and `sign.py check` can verify it. If the checker model is unavailable, use the next
strongest and say so in the evidence line.

## What to do

All of the following, in order, fixing findings until clean:

1. **Bug hunt** - e.g. `/code-review`, or a bug-radar style skill scaled to the diff's size and risk.
2. **Security review** - `/security-review`; mandatory on any security-touching diff.
3. **Simplicity review** - a YAGNI/simplify pass (e.g. `/simplify`): hunt what can be deleted from your own change.
4. **Silent-failure sweep** - hunt exactly five shapes:
   - empty catch blocks;
   - log-and-forget (caught, logged, execution continues as if nothing happened);
   - dangerous fallbacks (`.catch(() => [])`, defaults that mask a failed call);
   - error propagation that loses the stack;
   - missing timeout or rollback on external calls.
   Re-check every row of stage 3.5's failure-modes table against the code as built.

**A PR opened against a known-failing gate defeats the entire pipeline.** Do not proceed to stage 7
until this is clean. Record whether it was clean on the FIRST attempt (the `first_pass_gate_rate`
metric); inflating it by silently retrying is a governance failure, not a rounding error.

### Finding rules

(a) **Quote or demote.** Every finding is written
`[SEVERITY] (confidence N/10) file:line - description` and MUST quote the exact code line that
motivates it. Cannot quote it -> confidence capped at 4 and the finding goes to an appendix, never
presented as real. Only findings >= 8/10 surface as gate findings. This kills plausible-but-wrong
findings ("field doesn't exist", "might be None in theory").

(b) **Severity is bound to an action, not a feeling:** Critical = fix before the PR opens; High = fix
before merge; Medium = file a follow-up ticket and say so in the PR; Low = optional, note it.

(c) **Spec compliance first, quality second.** First answer "did it build what the ticket asked"
against the acceptance criteria; only then run the quality passes. The two are independent; neither
reranks the other's findings.

(d) **Dedupe across passes by fingerprint** `path:line:category`. Two passes hitting the same
fingerprint = confidence +1, marked MULTI-CONFIRMED.

## Sign

```
python <staged-coding skill dir>/scripts/sign.py sign 6 ran "<verdict of each pass, first-attempt clean yes/no>" --ticket <id> --by <seat>@<checker_model> --ledger <path resolved at stage 0> [--post]
```

Example ledger line:

```
 6  self-check gate   ran - bug hunt clean, security-review 0 findings, simplify 1 deletion, silent-failure sweep clean - clean on first attempt
```

The commit sha recorded here is the gate sha: if code changes after it, stage 9 sends the run back
through this stage.

## Hand-off

- A diff with zero open Critical/High findings and every Medium filed as its own ticket.
- The `first_pass_gate_rate` datapoint (clean on attempt 1, yes/no).
- Confirmation the checkpoint ran as a fresh checker subagent, not the builder marking its own work.
