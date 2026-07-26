#!/usr/bin/env python3
"""GSN build: validate nodes/*.yaml against the schema, compile site/nodes.geojson.

The schema is the moderation (§1.3): a submission that fails here bounces in CI
before any human looks at it. Exit non-zero on any violation.
"""
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAYERS = {"franchise", "independent", "knowledge"}
CAPABILITIES = {"full-service", "satellite", "depot", "performance", "heritage", "knowledge"}
METHODS = {"visited", "called", "bought", "website", "official-locator"}
STATUSES = {"active", "unverified", "defunct"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# coarse state bounding boxes for geocode sanity (lat_min, lat_max, lon_min, lon_max)
STATE_BBOX = {
    "NC": (33.7, 36.7, -84.4, -75.3), "VA": (36.5, 39.5, -83.7, -75.1),
    "SC": (32.0, 35.3, -83.4, -78.5), "TN": (34.9, 36.7, -90.4, -81.6),
    "GA": (30.3, 35.1, -85.7, -80.7), "TX": (25.8, 36.6, -106.7, -93.5),
    "WI": (42.4, 47.1, -92.9, -86.7), "MO": (35.9, 40.7, -95.8, -89.0),
    "CA": (32.5, 42.1, -124.5, -114.0), "NY": (40.4, 45.1, -79.8, -71.8),
}

errors = []


def err(f, msg):
    errors.append(f"{f.name}: {msg}")


def main():
    nodes = []
    files = sorted((ROOT / "nodes").glob("*.yaml"))
    if not files:
        print("no nodes found", file=sys.stderr)
        sys.exit(1)
    seen = set()
    for f in files:
        try:
            n = yaml.safe_load(f.read_text())
        except yaml.YAMLError as e:
            err(f, f"YAML parse error: {e}")
            continue
        for req in ("id", "name", "country", "layer", "capability", "brands",
                    "functions", "observations", "last_verified", "verified_by", "status"):
            if req not in n or n[req] in (None, [], ""):
                err(f, f"missing required field: {req}")
        if errors and errors[-1].startswith(f.name):
            continue
        if not SLUG.match(str(n["id"])):
            err(f, "id must be a lowercase slug")
        if n["id"] in seen:
            err(f, "duplicate id")
        seen.add(n["id"])
        if f.stem != n["id"]:
            err(f, f"filename must match id ({n['id']})")
        if n["layer"] not in LAYERS:
            err(f, f"illegal layer: {n['layer']}")
        caps = n["capability"] if isinstance(n["capability"], list) else [n["capability"]]
        for c in caps:
            if c not in CAPABILITIES:
                err(f, f"illegal capability: {c}")
        if not isinstance(n["functions"], list) or not n["functions"]:
            err(f, "functions must be a non-empty list (a node without functions is a pin)")
        if n["status"] not in STATUSES:
            err(f, f"illegal status: {n['status']}")
        if not DATE.match(str(n["last_verified"])):
            err(f, "last_verified must be YYYY-MM-DD")
        for o in n["observations"]:
            if not (isinstance(o, dict) and DATE.match(str(o.get("date", "")))
                    and o.get("method") in METHODS and o.get("fact")):
                err(f, f"malformed observation: {o}")
        lat, lon, st = n.get("lat"), n.get("lon"), n.get("state")
        if (lat is None) != (lon is None):
            err(f, "lat/lon must both be set or both null")
        if lat is not None and st in STATE_BBOX:
            a, b, c, d = STATE_BBOX[st]
            if not (a <= lat <= b and c <= lon <= d):
                err(f, f"coords ({lat},{lon}) outside claimed state {st}")
        nodes.append(n)

    if errors:
        print("SCHEMA VALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print("  -", e, file=sys.stderr)
        sys.exit(1)

    features = []
    for n in nodes:
        props = {k: n.get(k) for k in ("id", "name", "city", "state", "country", "layer",
                                       "brands", "functions", "url", "phone",
                                       "last_verified", "verified_by", "status")}
        props["capability"] = n["capability"] if isinstance(n["capability"], list) else [n["capability"]]
        props["observations"] = n["observations"]
        geom = None
        if n.get("lat") is not None:
            geom = {"type": "Point", "coordinates": [n["lon"], n["lat"]]}
        features.append({"type": "Feature", "geometry": geom, "properties": props})

    # §9: images are minimal by doctrine; any that exist must carry zero EXIF
    # (GPS/timestamps/device ids) and appear in docs/attribution.md.
    imgs = [p for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp")
            for p in ROOT.rglob(ext) if ".git" not in p.parts]
    if imgs:
        try:
            from PIL import Image
            attribution = (ROOT / "docs" / "attribution.md")
            attr_text = attribution.read_text() if attribution.exists() else ""
            for ip in imgs:
                exif = Image.open(ip).getexif()
                if len(exif):
                    print(f"EXIF metadata present in {ip.relative_to(ROOT)} — strip it "
                          f"(exiftool -all= / PIL re-save); the leak must be impossible.",
                          file=sys.stderr)
                    sys.exit(1)
                if ip.name not in attr_text:
                    print(f"{ip.relative_to(ROOT)} missing from docs/attribution.md "
                          f"(path → source → license)", file=sys.stderr)
                    sys.exit(1)
        except ImportError:
            print("Pillow required to validate images (pip install pillow)", file=sys.stderr)
            sys.exit(1)

    gj = {"type": "FeatureCollection",
          "features": features,
          "properties": {"generated_by": "gsn build.py", "count": len(features)}}
    out = ROOT / "site" / "nodes.geojson"
    out.write_text(json.dumps(gj, indent=1, ensure_ascii=False, default=str))
    print(f"OK: {len(nodes)} nodes validated -> {out.relative_to(ROOT)}")
    whatsnew()


def whatsnew():
    """The old 'What's New' page, for free: rendered from the git log (§10)."""
    import subprocess, html
    try:
        log = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--date=short", "-40",
             "--format=%ad\x1f%s", "--", "nodes/", "doctrine.md", "methodology.md"],
            capture_output=True, text=True, check=True).stdout
    except Exception:
        print("whatsnew: git unavailable, skipping")
        return
    rows = []
    for line in log.splitlines():
        if "\x1f" not in line:
            continue
        d, subj = line.split("\x1f", 1)
        rows.append(f"<tr><td><tt>{d}</tt></td><td>{html.escape(subj)}</td></tr>")
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>What's New — GSN</title>
<style>body{{background:#efefea;color:#111;font:16px/1.5 "Times New Roman",Times,serif;max-width:820px;margin:0 auto;padding:16px}}
a{{color:#0000EE}}a:visited{{color:#551A8B}}h1{{text-align:center}}hr{{border:0;border-top:3px double #c8102e}}
table{{border-collapse:collapse;width:100%;background:#fff;border:2px outset #999;font-size:14px}}
td{{border-top:1px solid #ccc;padding:5px 8px;vertical-align:top}}</style></head><body>
<h1>What's New</h1><p style="text-align:center"><i>rendered straight from the git log — the database's own diary.</i>
<br><a href="index.html">&larr; back to the map</a></p><hr>
<table>{''.join(rows)}</table>
<hr><p style="text-align:center;font-size:13px">The Guzzi Support Network · not affiliated with Piaggio Group</p>
</body></html>"""
    (ROOT / "site" / "whatsnew.html").write_text(page)
    print(f"whatsnew.html: {len(rows)} entries")


if __name__ == "__main__":
    main()
