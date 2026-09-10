#!/usr/bin/env python3
"""The global desert heat layer (Nathan, 2026-09-10: "green=good red=bad grey=desert").

For every town on earth (GeoNames cities5000, CC-BY 4.0), color by distance to
the nearest active full-service node, painted as translucent blobs into one
Web-Mercator PNG the map shows as an L.imageOverlay. Towns, not a land grid:
oceans stay empty for free, and the layer honestly shows where people are.

Honesty rule, stated everywhere the layer is: outside the countries we have
actually scraped, grey measures OUR coverage at least as much as the world's.

Usage: python3 scripts/desert_overlay.py [path/to/cities5000.txt]
Writes site/desert-overlay.png (bounds: lat 72 .. -56, lon -180 .. 180 —
keep in sync with the JS overlay bounds in site/index.html).
"""
import json
import math
import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAT_N, LAT_S = 72.0, -56.0
W = 2048

# distance (mi) -> color ramp: site green -> yellow -> orange -> brand red,
# then fading to grey = desert
STOPS = [(0, (0x1e, 0x8a, 0x5f)), (75, (0x6f, 0xa8, 0x3a)), (150, (0xd4, 0xc4, 0x37)),
         (250, (0xd9, 0x8d, 0x2b)), (400, (0xc8, 0x10, 0x2e)), (550, (0x7a, 0x7a, 0x7a))]


def ramp(d):
    if d >= STOPS[-1][0]:
        return STOPS[-1][1]
    for (d0, c0), (d1, c1) in zip(STOPS, STOPS[1:]):
        if d <= d1:
            t = (d - d0) / (d1 - d0)
            return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def main():
    gaz = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "cities5000.txt"
    if not gaz.exists():
        sys.exit(f"gazetteer not found: {gaz} (see scripts/desert_index.py docstring)")
    g = json.loads((ROOT / "site" / "nodes.geojson").read_text())
    nodes = []
    for f in g["features"]:
        p = f["properties"]
        if f["geometry"] and p["status"] == "active" and "full-service" in p["capability"]:
            lon, lat = f["geometry"]["coordinates"]
            nodes.append((lat, lon, math.cos(math.radians(lat))))
    towns = []
    for line in open(gaz, encoding="utf-8"):
        c = line.split("\t")
        lat, lon = float(c[4]), float(c[5])
        if not (LAT_S <= lat <= LAT_N):
            continue
        # equirectangular approx is fine for *choosing* the nearest at map scale
        best = min((abs(lat - nl) ** 2 + ((lon - no + 180) % 360 - 180) ** 2 * cl ** 2)
                   for nl, no, cl in nodes)
        towns.append((lat, lon, 69.09 * math.sqrt(best)))

    y_n, y_s = merc_y(LAT_N), merc_y(LAT_S)
    H = round(W * (y_n - y_s) / (2 * math.pi))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    # worst first so good coverage wins the pixel where towns overlap
    for lat, lon, d in sorted(towns, key=lambda t: -t[2]):
        x = (lon + 180.0) / 360.0 * W
        y = (y_n - merc_y(lat)) / (y_n - y_s) * H
        r = 6.0 if d >= 400 else 4.5
        dr.ellipse([x - r, y - r, x + r, y + r], fill=ramp(d) + (120,))
    out = ROOT / "site" / "desert-overlay.png"
    img.save(out, optimize=True)
    n_desert = sum(1 for t in towns if t[2] >= 550)
    print(f"wrote {out.relative_to(ROOT)} ({W}x{H}): {len(towns):,} towns, "
          f"{len(nodes)} FS nodes, {n_desert:,} towns in grey desert (>=550 mi)")


if __name__ == "__main__":
    main()
