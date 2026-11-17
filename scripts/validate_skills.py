#!/usr/bin/env python3
"""Validate that every skills/*/SKILL.md has `name` and `description` frontmatter.

Checks: frontmatter block exists, `name` is present and matches the folder name,
`description` is present and non-empty. Stdlib only. Exit 1 on any failure.
"""
import json
import pathlib
import re
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


def check_staged_coding(names):
    """The staged-coding conductor must reference only stage skills that exist,
    every stage folder must be referenced, and its config template must be valid JSON."""
    conductor = ROOT / "staged-coding" / "SKILL.md"
    if not conductor.exists():
        return []
    errors = []
    referenced = set(re.findall(r"/(staged-coding-[0-9.]+-[a-z]+)", conductor.read_text(encoding="utf-8")))
    stages = {n for n in names if n.startswith("staged-coding-")}
    for missing in referenced - stages:
        errors.append(f"staged-coding: conductor references missing skill {missing}")
    for orphan in stages - referenced:
        errors.append(f"{orphan}: not listed in the staged-coding conductor")
    try:
        json.loads((ROOT / "staged-coding" / "config.example.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"staged-coding: config.example.json invalid ({exc})")
    return errors


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
    errors += check_staged_coding({p.parent.name for p in skills})
    for e in errors:
        print("FAIL", e)
    print(f"{len(skills) - len({e.split(':')[0] for e in errors})}/{len(skills)} skills valid")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
