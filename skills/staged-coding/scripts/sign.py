#!/usr/bin/env python3
"""Stage signer for the staged-coding pipeline (stdlib only).

Every stage, when it finishes, appends ONE clock-stamped line to the run's ledger
(JSONL): stage, verdict, evidence, signer, machine time, git commit sha, and the
sha256 of any attached evidence files. Optionally posts the same line as a
comment on the ticket (`--post`, uses the GitHub CLI), so the tracker's own
server clock becomes a second timeline no agent controls.

Usage:
  sign.py sign <stage> <ran|skipped|n-a> "<evidence>" --ticket ID --by SEAT@MODEL
          --ledger PATH [--attach FILE ...] [--post]
  sign.py check  --ledger PATH [--all]   # exit 3 + list of unsigned stages
  sign.py render --ledger PATH           # prints the STAGE LEDGER block for the PR body

`check` ignores stage 10 unless --all is given (stage 10 signs right before the PR).
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys

STAGES = [
    ("0", "chase open PRs"), ("1", "recon"), ("2", "restraint"), ("2.5", "ask the owner"),
    ("3", "plan + council"), ("3.5", "pre-mortem"), ("4", "build (TDD)"), ("5", "house style"),
    ("6", "self-check gate"), ("7", "logged-in browser"), ("8", "prove it"),
    ("8.5", "design match"), ("9", "verification"), ("9.5", "refuter on the FIX"), ("10", "land"),
]
STAGE_IDS = [s for s, _ in STAGES]
VERDICTS = ("ran", "skipped", "n-a")


def git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def read(path):
    p = pathlib.Path(path)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_sign(a):
    if a.stage not in STAGE_IDS:
        sys.exit(f"unknown stage {a.stage}; expected one of {STAGE_IDS}")
    if a.verdict not in VERDICTS:
        sys.exit(f"verdict must be one of {VERDICTS}")
    if "@" not in a.by:
        sys.exit("--by must look like <seat>@<model> so judge != author can be checked")
    lines = read(a.ledger)
    rnd = 1 + sum(1 for l in lines if l["stage"] == a.stage)
    entry = {
        "ticket": a.ticket, "stage": a.stage, "round": rnd, "verdict": a.verdict,
        "evidence": a.evidence, "by": a.by,
        "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sha": git("rev-parse", "--short", "HEAD"),
        "attachments": {f: sha256(f) for f in (a.attach or [])},
    }
    if a.post:
        body = f"stage {a.stage} {a.verdict} (round {rnd}) by {a.by}: {a.evidence}"
        r = subprocess.run(["gh", "issue", "comment", str(a.ticket), "--body", body],
                           capture_output=True, text=True)
        entry["posted"] = r.stdout.strip() if r.returncode == 0 else f"FAILED: {r.stderr.strip()}"
    with open(a.ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry))


def latest(lines):
    by = {}
    for l in lines:
        by[l["stage"]] = l
    return by


def cmd_check(a):
    by = latest(read(a.ledger))
    want = STAGE_IDS if a.all else [s for s in STAGE_IDS if s != "10"]
    missing = [s for s in want if s not in by]
    builder = by.get("4", {}).get("by", "").split("@")[-1]
    same = [s for s in ("6", "8.5", "9.5")
            if s in by and by[s]["verdict"] == "ran" and builder and by[s]["by"].split("@")[-1] == builder]
    for s in missing:
        print(f"MISSING stage {s}")
    for s in same:
        print(f"JUDGE==AUTHOR stage {s} signed by the builder's model ({builder})")
    return 3 if (missing or same) else 0


def cmd_render(a):
    lines = read(a.ledger)
    by = latest(lines)
    ticket = next((l["ticket"] for l in lines), "?")
    print(f"STAGE LEDGER - {ticket}")
    for sid, label in STAGES:
        l = by.get(sid)
        if not l:
            print(f" {sid:<4}{label:<20} MISSING")
            continue
        rnd = f" (round {l['round']})" if l["round"] > 1 else ""
        print(f" {sid:<4}{label:<20} {l['verdict']:<8}- {l['evidence']}{rnd} . signed {l['at']} by {l['by']} . at {l['sha']}")
    gate = by.get("6", {}).get("sha")
    if gate:
        n = git("rev-list", "--count", f"{gate}..HEAD") or "?"
        print(f"gate sha {gate} . {n} commits since")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sign")
    s.add_argument("stage"); s.add_argument("verdict"); s.add_argument("evidence")
    s.add_argument("--ticket", required=True); s.add_argument("--by", required=True)
    s.add_argument("--ledger", required=True); s.add_argument("--attach", nargs="*")
    s.add_argument("--post", action="store_true")
    c = sub.add_parser("check"); c.add_argument("--ledger", required=True); c.add_argument("--all", action="store_true")
    r = sub.add_parser("render"); r.add_argument("--ledger", required=True)
    a = p.parse_args()
    return {"sign": cmd_sign, "check": cmd_check, "render": cmd_render}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
