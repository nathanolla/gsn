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
METHODS = {"visited", "called", "bought", "website", "official-locator", "community-endorsement"}
STATUSES = {"active", "unverified", "defunct"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# state bounding boxes for geocode sanity (lat_min, lat_max, lon_min, lon_max), all 50 + DC
STATE_BBOX = {
    "AL": (30.1, 35.1, -88.5, -84.8), "AK": (51.0, 71.6, -179.9, -129.0),
    "AZ": (31.3, 37.1, -115.0, -108.9), "AR": (33.0, 36.6, -94.7, -89.6),
    "CA": (32.5, 42.1, -124.5, -114.0), "CO": (36.9, 41.1, -109.1, -101.9),
    "CT": (40.9, 42.1, -73.8, -71.7), "DE": (38.4, 39.9, -75.8, -74.9),
    "DC": (38.8, 39.0, -77.2, -76.9), "FL": (24.3, 31.1, -87.7, -79.9),
    "GA": (30.3, 35.1, -85.7, -80.7), "HI": (18.8, 22.3, -160.3, -154.7),
    "ID": (41.9, 49.1, -117.3, -110.9), "IL": (36.9, 42.6, -91.6, -87.0),
    "IN": (37.7, 41.8, -88.1, -84.7), "IA": (40.3, 43.6, -96.7, -90.1),
    "KS": (36.9, 40.1, -102.1, -94.5), "KY": (36.4, 39.2, -89.6, -81.9),
    "LA": (28.9, 33.1, -94.1, -88.7), "ME": (42.9, 47.5, -71.1, -66.8),
    "MD": (37.8, 39.8, -79.5, -74.9), "MA": (41.2, 42.9, -73.6, -69.9),
    "MI": (41.6, 48.4, -90.5, -82.3), "MN": (43.4, 49.5, -97.3, -89.4),
    "MS": (30.1, 35.1, -91.7, -88.0), "MO": (35.9, 40.7, -95.8, -88.9),
    "MT": (44.3, 49.1, -116.1, -104.0), "NE": (39.9, 43.1, -104.1, -95.2),
    "NV": (35.0, 42.1, -120.1, -114.0), "NH": (42.6, 45.4, -72.6, -70.5),
    "NJ": (38.8, 41.4, -75.6, -73.8), "NM": (31.2, 37.1, -109.1, -102.9),
    "NY": (40.4, 45.1, -79.8, -71.8), "NC": (33.7, 36.7, -84.4, -75.3),
    "ND": (45.9, 49.1, -104.1, -96.5), "OH": (38.3, 42.4, -84.9, -80.5),
    "OK": (33.6, 37.1, -103.1, -94.4), "OR": (41.9, 46.4, -124.6, -116.4),
    "PA": (39.7, 42.3, -80.6, -74.6), "RI": (41.1, 42.1, -71.9, -71.1),
    "SC": (32.0, 35.3, -83.4, -78.5), "SD": (42.4, 46.0, -104.1, -96.4),
    "TN": (34.9, 36.7, -90.4, -81.6), "TX": (25.8, 36.6, -106.7, -93.5),
    "UT": (36.9, 42.1, -114.1, -108.9), "VT": (42.7, 45.1, -73.5, -71.4),
    "VA": (36.5, 39.5, -83.7, -75.1), "WA": (45.5, 49.1, -124.9, -116.9),
    "WV": (37.1, 40.7, -82.7, -77.7), "WI": (42.4, 47.1, -92.9, -86.7),
    "WY": (40.9, 45.1, -111.1, -104.0),
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
            if req not in n or n[req] is None or n[req] == "":
                err(f, f"missing required field: {req}")
            # brands may be an empty list (marques unpublished — an honest state);
            # everything else must be non-empty
            elif req != "brands" and n[req] == []:
                err(f, f"empty required field: {req}")
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
        u = n.get("url")
        if u and not re.match(r"^https?://", str(u)):
            err(f, f"url must be absolute (https://...): {u}")
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
    static_render(features)
    stamp_sw()
    whatsnew()


def stamp_sw():
    """Version the service-worker cache by a content hash so a new build invalidates
    the shell cache (offline updates propagate)."""
    import hashlib
    sw = ROOT / "site" / "sw.js"
    if not sw.exists():
        return
    idx = (ROOT / "site" / "index.html").read_text()
    gj = (ROOT / "site" / "nodes.geojson").read_text()
    h = hashlib.md5((idx + gj).encode()).hexdigest()[:10]
    doc = re.sub(r"/\*BUILD:SWVER\*/[^/]*/\*/", f"/*BUILD:SWVER*/{h}/*/", sw.read_text())
    sw.write_text(doc)
    print(f"sw.js version -> gsn-{h}")


CAP_COLORS = {"full-service": "#1e8a5f", "satellite": "#c98d1f", "depot": "#2f6fbe",
              "performance": "#7a4fc0", "heritage": "#6d7c8c", "knowledge": "#888"}

# In-house capability glyphs (inline SVG inner-paths; adapted from Feather Icons, MIT).
# Single source of truth: used by the static render here AND injected into the page
# for the JS to reuse, so both paths draw identical icons. No hosted images.
ICON_PATHS = {
    "full-service": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "satellite": '<circle cx="12" cy="12" r="9"/><path d="M8.3 12.3 11 15l5-6"/>',
    "depot": '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/>',
    "performance": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "heritage": '<circle cx="12" cy="8" r="6"/><path d="M8.2 13.9 7 22l5-3 5 3-1.2-8.1"/>',
    "knowledge": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 1-4 4v14a3 3 0 0 1 3-3h7z"/>',
}


def icon_svg(cap, cls="micon"):
    inner = ICON_PATHS.get(cap, '<circle cx="12" cy="12" r="7"/>')
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>')


def _replace_sentinel(doc, name, inner):
    """Replace content between <!--BUILD:name--> and <!--/BUILD:name-->. Idempotent."""
    pat = re.compile(re.escape(f"<!--BUILD:{name}-->") + r".*?" + re.escape(f"<!--/BUILD:{name}-->"), re.S)
    repl = f"<!--BUILD:{name}-->{inner}<!--/BUILD:{name}-->"
    return pat.sub(lambda _m: repl, doc)


def static_render(features):
    """Inject real content into index.html at build so the page is meaningful with JS off.
    JS re-renders from nodes.geojson on load and enhances (sort/filter/map/pager)."""
    import html
    def e(s):  # str-coerce (YAML dates aren't strings) then HTML-escape
        return html.escape("" if s is None else str(s))
    index = ROOT / "site" / "index.html"
    doc = index.read_text()
    dates = [f["properties"].get("last_verified") for f in features if f["properties"].get("last_verified")]
    newest = max(dates) if dates else ""

    rows = []
    for f in sorted(features, key=lambda x: (x["properties"]["name"] or "").lower()):
        p = f["properties"]
        cap = (p["capability"] or ["knowledge"])[0]
        color = CAP_COLORS.get(cap, "#888")
        url = p.get("url")
        sw = f'<span class="sw" style="color:{color}">{icon_svg(cap)}</span>'
        if url:
            u = e(url)
            namecell = (f'<a href="{u}" target="_blank" rel="noopener">{sw}</a>'
                        f'<a class="nm" href="{u}" target="_blank" rel="noopener">{e(p["name"])}</a>')
            try:
                host = e(re.sub(r"^www\.", "", url.split("/")[2]))
            except Exception:
                host = e(url)
            link = f'<a href="{u}" target="_blank" rel="noopener">{host}</a>'
        else:
            namecell = f'{sw}<span class="nm">{e(p["name"])}</span>'
            link = ""
        loc = f'{e(p["city"])}, {e(p["state"])}' if p.get("city") else "—"
        caps = e("+".join(p["capability"] or []))
        fns = e(" · ".join(p.get("functions") or []))
        phone = p.get("phone")
        tel = ""
        if phone:
            digits = re.sub(r"[^+0-9]", "", phone)
            tel = f' · <a href="tel:{e(digits)}">{e(phone)}</a>'
        lv = e(p.get("last_verified") or "never")
        rows.append(
            f'<tr><td>{namecell}<br><span class="cap">{caps}</span> · {loc}</td>'
            f'<td class="fnline">{fns}<br>{link}{tel}</td>'
            f'<td><span class="pill">{lv}</span></td></tr>')

    icons_js = "<script>const ICONS=" + json.dumps({c: icon_svg(c) for c in CAP_COLORS}) + ";</script>"
    doc = _replace_sentinel(doc, "ICONS", icons_js)
    doc = _replace_sentinel(doc, "COUNT", str(len(features)).zfill(6))
    doc = _replace_sentinel(doc, "LASTUPD", e(newest) or "—")
    doc = _replace_sentinel(doc, "FOOTUPD", e(newest) or "—")
    doc = _replace_sentinel(doc, "ROWS", "".join(rows))
    index.write_text(doc)
    print(f"static render: {len(rows)} rows injected into index.html")


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
<h1>What's New</h1><p style="text-align:center"><i>from the change log.</i>
<br><a href="index.html">&larr; back to the map</a></p><hr>
<table>{''.join(rows)}</table>
<hr><p style="text-align:center;font-size:13px">The Guzzi Support Network · not affiliated with Piaggio Group</p>
</body></html>"""
    (ROOT / "site" / "whatsnew.html").write_text(page)
    print(f"whatsnew.html: {len(rows)} entries")


if __name__ == "__main__":
    main()
