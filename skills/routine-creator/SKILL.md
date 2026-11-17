---
name: routine-creator
description: Mint a new scheduled Claude Code routine in one step (wrapper script, OS scheduler entry, log file, registry line), following the ops-manager pattern. Also lists and removes routines. Use when the user says "/routine-creator", "create a routine", "schedule a routine", "new daily/weekly task", "list my routines", or "remove routine X".
---

# Routine Creator

A routine is a headless `claude -p "<prompt>"` run on a schedule by your OS. LOCAL routines are the
default because they can see your sessions, worktrees, folders and local state. Offer a cloud
scheduler (for example the built-in `schedule` skill) ONLY when the task needs no local access
(e.g. pure GitHub or tracker watching).

## Paths (configurable)

| Thing | Default |
|---|---|
| Routine home `ROUTINES_HOME` | `~/.claude/ops-manager` |
| Wrapper | `$ROUTINES_HOME/routines/run-<slug>.cmd` (Windows) or `run-<slug>.sh` (macOS/Linux) |
| Log | `$ROUTINES_HOME/logs/<slug>.log` |
| Registry | `$ROUTINES_HOME/routines.jsonl` |
| Task name prefix `ROUTINE_PREFIX` | `Claude` (task name = `"<prefix> <Name>"`) |
| Claude binary | `claude` on PATH (use the absolute path if the scheduler's PATH lacks it) |

## Create (from args, or ask briefly: name, cadence, prompt, working dir)

1. **Derive** the slug, task name, wrapper path, log path and working dir (default: current project).
2. **Wrapper** (write the file, exact pattern):

   Windows `run-<slug>.cmd`:
   ```bat
   @echo off
   cd /d "<workdir>"
   call claude -p "<prompt>" >> "<log>" 2>&1
   ```
   macOS/Linux `run-<slug>.sh` (then `chmod +x`):
   ```sh
   #!/bin/sh
   cd "<workdir>" && claude -p "<prompt>" >> "<log>" 2>&1
   ```
   The prompt is usually a slash-skill invocation (`/some-skill args`) so the logic lives in a skill,
   not in the wrapper. If the routine needs a new skill, create `~/.claude/skills/<slug>/SKILL.md`
   too (frontmatter `name` + `description` with clear triggers, compact body).
3. **Schedule**:
   - Windows: `schtasks /Create /F /TN "<task name>" /SC DAILY|WEEKLY /ST HH:MM [/D SUN] /TR "<wrapper>"`.
     Verify with `schtasks /Query /TN "<task name>" /FO LIST` and quote the Next Run Time back.
   - macOS/Linux: add a crontab line (`crontab -l` then append), e.g. `0 8 * * * /path/run-<slug>.sh`,
     and show the resulting line back.
   Times are machine-local.
4. **Register**: append one JSON line to the registry:
   `{"name","slug","cadence","prompt","wrapper","log","created"}`. `ops-manager` reads this so every
   routine appears in the morning brief.

## List
Windows: `schtasks /Query /FO LIST | findstr "<prefix>"`; macOS/Linux: `crontab -l`. Join with the
registry and show name, cadence, next run and the last 5 log lines.

## Remove (needs the user's explicit confirmation per routine)
Delete the scheduler entry (`schtasks /Delete /TN "<task name>" /F`, or remove the crontab line),
delete the wrapper, and mark the registry line `"removed":"<date>"` (never rewrite history).
Never delete the log or any skill file unless asked.

## Hard rules
- Never schedule anything that pushes, merges, deletes or spends money unless its skill body states
  explicit, user-approved limits.
- One routine = one wrapper = one registry line. No inline multi-command scheduler strings (quoting
  breaks; that is why wrappers exist).
