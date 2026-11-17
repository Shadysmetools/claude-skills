#!/usr/bin/env python3
"""Validate that every skills/*/SKILL.md has `name` and `description` frontmatter.

Checks: frontmatter block exists, `name` is present and matches the folder name,
`description` is present and non-empty. Stdlib only. Exit 1 on any failure.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "skills"


def frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return None  # no closing ---


def main():
    skills = list(ROOT.glob("*/SKILL.md"))
    skills.sort()
    if not skills:
        print(f"no SKILL.md files under {ROOT}")
        return 1
    errors = []
    for path in skills:
        folder = path.parent.name
        fm = frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{folder}: missing or unterminated frontmatter")
            continue
        if not fm.get("name"):
            errors.append(f"{folder}: missing name")
        elif fm["name"] != folder:
            errors.append(f"{folder}: name '{fm['name']}' does not match folder")
        if not fm.get("description"):
            errors.append(f"{folder}: missing or empty description")
    for e in errors:
        print("FAIL", e)
    print(f"{len(skills) - len({e.split(':')[0] for e in errors})}/{len(skills)} skills valid")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
