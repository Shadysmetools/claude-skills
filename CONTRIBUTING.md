# Contributing

Thanks for helping. Issues and pull requests are welcome.

## Adding or changing a skill

1. One skill = one folder: `skills/<skill-name>/SKILL.md` (plus optional reference files next to it).
2. Start the file with YAML frontmatter on single lines:
   ```yaml
   ---
   name: skill-name          # must match the folder name
   description: What it does, and the exact phrases or events that should trigger it.
   ---
   ```
3. Keep the body compact and imperative. Say what to read first, the steps, and the hard rules.
4. Make it portable: no personal paths, hostnames, emails, company names, ticket numbers or secrets.
   Use configurable placeholders (`OWNER/REPO`, `STAGING_URL`, `~/.claude/...`) and document defaults.
5. Anything that writes, pushes, merges, deletes or spends money must state its limits in the skill.
6. Run the validator before you open a PR:
   ```sh
   python scripts/validate_skills.py
   ```
   CI runs the same check on every push and pull request.

## Pull requests

- One skill or one focused change per PR.
- Explain the problem the skill solves and show one real (sanitized) run if you can.
- By contributing you agree your work is licensed under Apache-2.0.
