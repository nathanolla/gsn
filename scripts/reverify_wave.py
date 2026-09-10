#!/usr/bin/env python3
"""Emit a farm-wave TSV re-verifying the N oldest-verified nodes.

The doctrine's freshness promise is a process, not a field: this is the
process. Monthly timer on wkstn1 runs the wave; harvest applies under the
same guarded merge as pass-2 (URLs/dates must survive; unreachable ->
status: unverified, never guessed).
"""
import glob, sys, yaml, os
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
# lane arg: mimo's NATIVE harness broke 2026-09-10 (LiteLLM key scoped to
# /anthropic-mimo only — sq #61); xiaomi = claude-over-passthrough, works
LANE = sys.argv[2] if len(sys.argv) > 2 else "xiaomi"
nodes = []
for f in glob.glob(os.path.join(os.path.dirname(__file__), "..", "nodes", "*.yaml")):
    d = yaml.safe_load(open(f))
    nodes.append((str(d.get("last_verified") or "0000"), f, d))
nodes.sort()
batch = nodes[:N]
RULES = ("You are a re-verification lane for the Guzzi Support Network. For EACH node below, "
 "one at a time (emit as you go): open its url; if alive, confirm it still relates to "
 "motorcycles/Guzzi and refresh last_verified to today; if unreachable after 2 tries, set "
 "status: unverified and append an observation saying so; if the site clearly says CLOSED, "
 "set status: defunct (closed nodes are kept, not deleted). NEVER invent; NEVER reference "
 "guzzitech.com; preserve every existing observation verbatim; output corrected YAML docs "
 "separated by '---'. today=TODAY.\nNODES:\n")
chunks = [batch[i:i+20] for i in range(0, len(batch), 20)]
for i, ch in enumerate(chunks):
    body = RULES + "\n---\n".join(open(f).read() for _, f, _ in ch)
    print(f"{LANE}\tgsn-reverify-{i:02d}\t" + body.replace("\t", "  ").replace("\n", "\\n"))
