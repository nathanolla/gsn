#!/usr/bin/env python3
"""The Desert Index — support-desert metrics for the Guzzi Support Network.

For every US town (GeoNames cities5000, CC-BY 4.0), the great-circle distance
to the nearest *active full-service* node. Published as a neutral finding
(doctrine: not a review, not a ranking of shops — a measurement of geography).

Honesty box (also printed into the report):
- Distances are straight-line miles; road miles are always longer.
- "Full-service" is GSN's evidence-graded category; a desert in our data can
  mean a desert in reality OR a gap in our coverage. Corrections via PR.
- Towns = GeoNames places with population >= 5000; smaller places are farther.

Usage: python3 scripts/desert_index.py [path/to/cities5000.txt]
  The gazetteer is NOT committed (2MB, refreshable):
  curl -sLO https://download.geonames.org/export/dump/cities5000.zip && unzip cities5000.zip
"""
import json
import math
import pathlib
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
MI = 1609.344
TODAY = date.today().isoformat()


def dist_mi(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = math.radians(b[0] - a[0]), math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371e3 * math.asin(math.sqrt(h)) / MI


def load_nodes():
    """(full_service, any_service) — the second set adds satellites, so the
    report can say 'the nearest *anything* is still N miles' and survive the
    obvious 'but there's a dealer in Bismarck' comment (there is; it's a
    satellite, and the table says so)."""
    g = json.loads((ROOT / "site" / "nodes.geojson").read_text())
    fs, anysvc = [], []
    for f in g["features"]:
        p = f["properties"]
        if not (f["geometry"] and p["status"] == "active"):
            continue
        lon, lat = f["geometry"]["coordinates"]
        if "full-service" in p["capability"]:
            fs.append(((lat, lon), p))
        if {"full-service", "satellite"} & set(p["capability"]):
            anysvc.append(((lat, lon), p))
    return fs, anysvc


def load_towns(path):
    towns = []
    for line in open(path, encoding="utf-8"):
        c = line.rstrip("\n").split("\t")
        if c[8] != "US":
            continue
        towns.append({"name": c[1], "state": c[10], "lat": float(c[4]),
                      "lon": float(c[5]), "pop": int(c[14] or 0)})
    return towns


def nearest(ll, fs):
    best, bp = 1e9, None
    for (nll, p) in fs:
        d = dist_mi(ll, nll)
        if d < best:
            best, bp = d, p
    return best, bp


def main():
    gaz = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cities5000.txt"
    if not gaz.exists():
        sys.exit(f"gazetteer not found: {gaz} (see module docstring)")
    fs, anysvc = load_nodes()
    towns = load_towns(gaz)
    for t in towns:
        t["mi"], t["node"] = nearest((t["lat"], t["lon"]), fs)
        t["mi_any"], t["node_any"] = nearest((t["lat"], t["lon"]), anysvc)

    # ---- per-state table (lower 48 + DC; AK/HI reported apart) ----
    by_state = {}
    for t in towns:
        by_state.setdefault(t["state"], []).append(t)
    rows = []
    for st, ts in by_state.items():
        ds = sorted(x["mi"] for x in ts)
        med = ds[len(ds) // 2]
        worst = max(ts, key=lambda x: x["mi"])
        pop = sum(x["pop"] for x in ts) or 1
        far_pop = sum(x["pop"] for x in ts if x["mi"] > 100)
        rows.append({"state": st, "towns": len(ts), "median": med,
                     "worst_mi": worst["mi"], "worst_town": worst["name"],
                     "pct_pop_over_100": 100.0 * far_pop / pop})
    rows.sort(key=lambda r: -r["median"])

    # ---- the ten worst gaps (lower 48): farthest towns, deduped 150 mi ----
    l48 = [t for t in towns if t["state"] not in ("AK", "HI") and t["pop"] >= 5000]
    l48.sort(key=lambda t: -t["mi"])
    gaps, taken = [], []
    for t in l48:
        if all(dist_mi((t["lat"], t["lon"]), (g["lat"], g["lon"])) > 150 for g in taken):
            gaps.append(t)
            taken.append(t)
        if len(gaps) == 10:
            break

    # ---- markdown report ----
    md = [f"# The Desert Index — {TODAY}",
          "",
          "**How far is America from a Guzzi wrench?** For every US town with",
          "5,000+ people, the straight-line distance to the nearest *active,",
          "full-service* node in the [Guzzi Support Network](https://guzzisupport.network/).",
          f"Computed {TODAY} from {len(fs)} full-service nodes and {len(towns):,} towns.",
          "",
          "*A neutral finding, per doctrine: this measures geography, not shops.",
          "Straight-line miles (roads are longer). A desert in our data is either",
          "a desert in reality or a hole in our coverage — corrections via PR",
          "either way. Towns: GeoNames `cities5000`, CC-BY 4.0.*",
          "",
          "## The ten worst gaps in the lower 48",
          "",
          "| # | town | state | population | miles to nearest full-service | which is | nearest service point of any grade |",
          "|---|---|---|---|---|---|---|"]
    for i, t in enumerate(gaps, 1):
        n, na = t["node"], t["node_any"]
        anycell = (f"{t['mi_any']:.0f} mi — {na['name']} ({na['city']}, {na['state']})"
                   if t["mi_any"] < t["mi"] - 1 else "same")
        md.append(f"| {i} | {t['name']} | {t['state']} | {t['pop']:,} | "
                  f"**{t['mi']:.0f}** | {n['name']} ({n['city']}, {n['state']}) | {anycell} |")
    md += ["",
           "## By state — median town-to-wrench distance",
           "",
           "| state | towns | median mi | worst town | worst mi | % of town pop >100 mi |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['state']} | {r['towns']} | {r['median']:.0f} | "
                  f"{r['worst_town']} | {r['worst_mi']:.0f} | {r['pct_pop_over_100']:.0f}% |")
    md += ["",
           "## Method",
           "- Nodes: `site/nodes.geojson`, `status: active`, capability includes"
           " `full-service` (evidence-graded; see methodology.md).",
           "- Nearest node may be in another state or country (borders don't stop riders).",
           "- The last column is the nearest node graded full-service OR satellite —"
           " a satellite can book service and get you diagnosed, without evidenced"
           " wrenching depth (see doctrine.md).",
           "- Median is over towns, not people; the last column is population-share.",
           "- AK and HI are excluded from the top-ten (they would sweep it) but appear"
           " in the state table.",
           "",
           f"*Generated by `scripts/desert_index.py` on {TODAY}. Data ODbL 1.0;"
           " towns © GeoNames, CC-BY 4.0.*"]
    out_md = ROOT / "docs" / f"desert-index-{TODAY[:7]}.md"
    out_md.write_text("\n".join(md) + "\n")
    print(f"wrote {out_md.relative_to(ROOT)}: {len(fs)} FS nodes, "
          f"{len(towns):,} towns, worst gap {gaps[0]['mi']:.0f} mi ({gaps[0]['name']}, {gaps[0]['state']})")

    # ---- retro site page ----
    import html as H
    def anycell(t):
        if t["mi_any"] >= t["mi"] - 1:
            return "same"
        na = t["node_any"]
        return (f"{t['mi_any']:.0f} mi — {H.escape(na['name'])} "
                f"({H.escape(na['city'] or '')}, {H.escape(na['state'] or '')})")
    trs = "".join(
        f"<tr><td>{i}</td><td>{H.escape(t['name'])}, {t['state']}</td><td>{t['pop']:,}</td>"
        f"<td><b>{t['mi']:.0f} mi</b></td><td>{H.escape(t['node']['name'])} "
        f"({H.escape(t['node']['city'] or '')}, {H.escape(t['node']['state'] or '')})</td>"
        f"<td>{anycell(t)}</td></tr>"
        for i, t in enumerate(gaps, 1))
    strs = "".join(
        f"<tr><td>{r['state']}</td><td>{r['median']:.0f} mi</td>"
        f"<td>{H.escape(r['worst_town'])} — {r['worst_mi']:.0f} mi</td>"
        f"<td>{r['pct_pop_over_100']:.0f}%</td></tr>" for r in rows)
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>The Desert Index — GSN</title>
<style>body{{background:#efefea;color:#111;font:16px/1.5 "Times New Roman",Times,serif;max-width:860px;margin:0 auto;padding:16px}}
a{{color:#0000EE}}a:visited{{color:#551A8B}}h1,h2{{text-align:center}}hr{{border:0;border-top:3px double #c8102e}}
table{{border-collapse:collapse;width:100%;background:#fff;border:2px outset #999;font-size:14px;margin:10px 0}}
th{{background:#c8102e;color:#fff;font:11px Verdana,sans-serif;text-transform:uppercase;padding:5px 7px;text-align:left}}
td{{border-top:1px solid #ccc;padding:5px 8px;vertical-align:top}}.note{{font-size:13px;color:#444;text-align:center}}
div.scroll{{overflow-x:auto}}</style></head><body>
<h1>The <span style="color:#c8102e">Desert</span> Index</h1>
<p class="note">How far is America from a Guzzi wrench? Distance from every US town (5,000+ people)
to the nearest <i>active, full-service</i> GSN node. Straight-line miles — roads are longer.<br>
Computed {TODAY} from {len(fs)} full-service nodes. A neutral finding, not a review.
<br><a href="index.html">&larr; back to the map</a></p><hr>
<h2>The ten worst gaps in the lower 48</h2>
<div class="scroll"><table><tr><th>#</th><th>town</th><th>pop.</th><th>gap</th><th>nearest full-service</th><th>nearest service point (any grade)</th></tr>{trs}</table></div>
<h2>By state</h2>
<div class="scroll"><table><tr><th>state</th><th>median</th><th>worst town</th><th>% of town pop &gt;100 mi</th></tr>{strs}</table></div>
<hr><p class="note">A desert in our data is a desert in reality <i>or</i> a hole in our coverage —
<a href="https://github.com/nathanolla/gsn">corrections via PR</a> welcome either way.<br>
Data ODbL 1.0 · towns © <a href="https://www.geonames.org/">GeoNames</a>, CC-BY 4.0 · generated {TODAY}</p>
</body></html>"""
    (ROOT / "site" / "desert.html").write_text(page)
    print("wrote site/desert.html")


if __name__ == "__main__":
    main()
