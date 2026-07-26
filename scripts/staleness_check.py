#!/usr/bin/env python3
"""List nodes >18 months since last_verified and upsert one 're-verification wanted'
GitHub issue (a standing, low-effort volunteer menu). No-op if none are stale."""
import datetime, glob, json, subprocess, sys
import yaml

TITLE = "Re-verification wanted"
today = datetime.date.today()
stale = []
for f in sorted(glob.glob("nodes/*.yaml")):
    n = yaml.safe_load(open(f))
    lv = n.get("last_verified")
    if isinstance(lv, str):
        lv = datetime.date.fromisoformat(lv)
    if lv and (today - lv).days > 547:  # ~18 months
        stale.append(n)

nums = json.loads(subprocess.run(
    ["gh", "issue", "list", "--state", "open", "--search", f"{TITLE} in:title",
     "--json", "number"], capture_output=True, text=True).stdout or "[]")
existing = nums[0]["number"] if nums else None

if not stale:
    print("no stale nodes")
    if existing:
        subprocess.run(["gh", "issue", "close", str(existing),
                        "--comment", "All nodes are within 18 months again."])
    sys.exit(0)

body = ("These nodes are 18+ months since last verified. Call or visit, then submit "
        "an observation to refresh them (any listed business, a rider who just called, "
        "anyone):\n\n")
for n in stale:
    body += (f"- [ ] **{n['name']}** ({n.get('city','')}, {n.get('state','')}) — "
             f"{n.get('phone','') or ''} {n.get('url','') or ''} (last {n['last_verified']})\n")

if existing:
    subprocess.run(["gh", "issue", "edit", str(existing), "--body", body])
    print(f"updated issue #{existing} with {len(stale)} stale nodes")
else:
    subprocess.run(["gh", "issue", "create", "--title", TITLE, "--body", body])
    print(f"opened re-verification issue with {len(stale)} stale nodes")
