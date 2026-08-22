#!/usr/bin/env python3
"""Emit a farm-wave TSV verifying open GitHub suggestions/corrections.

Reads public issues (no auth) labeled suggestion/correction; each becomes a
verification task. Rider reports, machine verifies, lead reviews and lands.
"""
import json, urllib.request, sys
API = "https://api.github.com/repos/nathanolla/gsn/issues?state=open&per_page=50"
req = urllib.request.Request(API, headers={"User-Agent": "gsn-intake/1.0",
                                           "Accept": "application/vnd.github+json"})
issues = json.load(urllib.request.urlopen(req, timeout=30))
lanes = 0
for it in issues:
    labels = {l["name"] for l in it.get("labels", [])}
    if not ({"suggestion", "correction"} & labels):
        continue
    kind = "suggestion" if "suggestion" in labels else "correction"
    body = (it.get("body") or "").replace("\t", "  ")[:4000]
    prompt = ("You are a verification lane for the Guzzi Support Network. A rider filed this "
      f"{kind} (github issue #{it['number']}: {it['title']!r}). Verify it INDEPENDENTLY: "
      "find the shop's site/locator/club evidence, confirm or refute each claim, and output "
      "either a complete node YAML draft (schema like existing nodes/, with dated sourced "
      "observations, final line 'review: pending') or a short VERDICT paragraph explaining "
      "what could not be verified. NEVER invent; NEVER reference guzzitech.com. "
      f"today=TODAY.\n\nISSUE BODY:\n{body}")
    print(f"mimo\tgsn-intake-{it['number']}\t" + prompt.replace("\n", "\\n"))
    lanes += 1
print(f"# {lanes} intake lanes", file=sys.stderr)
