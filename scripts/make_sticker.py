#!/usr/bin/env python3
"""The counter sticker: QR to the site, offered free to every full-service node.

Output is a print-ready vector (site/sticker.svg, 100x75mm + 2mm bleed) in the
site's own 1999 face — double red rule, Times, the red GUZZI. Deliberately no
eagle, no Piaggio trademark imagery: the wordmark use is nominative and the
non-affiliation line is printed on the sticker itself.

Requires: python3-qrcode. Run after changing the design; commit the output.
"""
import pathlib

import qrcode

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://guzzisupport.network/"

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
qr.add_data(URL)
qr.make(fit=True)
m = qr.get_matrix()
n = len(m)

# Geometry (mm). Canvas 104x79 = 100x75 sticker + 2mm bleed all round.
# Title runs full width; below it the text column owns x<59 and the QR
# (with 3mm quiet zone) owns x>=60 — the two never overlap.
W, H, BLEED = 104.0, 79.0, 2.0
QR_SIZE = 34.0
QR_X, QR_Y = W - BLEED - 5.0 - QR_SIZE, 26.0
cell = QR_SIZE / n
path = []
for y, row in enumerate(m):
    for x, v in enumerate(row):
        if v:
            path.append(f"M{QR_X + x * cell:.3f} {QR_Y + y * cell:.3f}"
                        f"h{cell:.3f}v{cell:.3f}h-{cell:.3f}z")
qr_path = "".join(path)

TXT_X = BLEED + 7.0
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm"
     viewBox="0 0 {W} {H}">
  <title>Guzzi Support Network — counter sticker</title>
  <!-- bleed background -->
  <rect x="0" y="0" width="{W}" height="{H}" fill="#efefea"/>
  <!-- trim line (100x75mm): printers cut here; keep for proof, harmless if printed -->
  <rect x="{BLEED}" y="{BLEED}" width="{W - 2 * BLEED}" height="{H - 2 * BLEED}"
        fill="none" stroke="#bbb" stroke-width="0.1" stroke-dasharray="1 1.5"/>
  <!-- the double red rule, top and bottom -->
  <g stroke="#c8102e" stroke-width="0.8">
    <line x1="{BLEED + 4}" y1="{BLEED + 6}" x2="{W - BLEED - 4}" y2="{BLEED + 6}"/>
    <line x1="{BLEED + 4}" y1="{BLEED + 7.6}" x2="{W - BLEED - 4}" y2="{BLEED + 7.6}"/>
    <line x1="{BLEED + 4}" y1="{H - BLEED - 7.6}" x2="{W - BLEED - 4}" y2="{H - BLEED - 7.6}"/>
    <line x1="{BLEED + 4}" y1="{H - BLEED - 6}" x2="{W - BLEED - 4}" y2="{H - BLEED - 6}"/>
  </g>
  <g font-family="'Times New Roman',Times,serif" fill="#111">
    <text x="{TXT_X}" y="{BLEED + 15}" font-size="6.0" font-weight="bold">The
      <tspan fill="#c8102e">GUZZI</tspan> Support Network</text>
    <text x="{TXT_X}" y="{BLEED + 22.5}" font-size="4.2" font-style="italic">&#8220;Where&#8230;?&#8221; &#8212; answered.</text>
    <text x="{TXT_X}" y="{BLEED + 29}" font-size="3.2">Every shop, wrench, parts depot</text>
    <text x="{TXT_X}" y="{BLEED + 33.4}" font-size="3.2">and club that keeps a Moto Guzzi</text>
    <text x="{TXT_X}" y="{BLEED + 37.8}" font-size="3.2">running &#8212; one community-kept,</text>
    <text x="{TXT_X}" y="{BLEED + 42.2}" font-size="3.2">freshness-dated map.</text>
    <text x="{TXT_X}" y="{BLEED + 49}" font-size="3.5" font-weight="bold">Scan it. Save the nodes. Ride.</text>
    <text x="{TXT_X}" y="{BLEED + 56}" font-size="3.8" font-family="'Courier New',monospace">guzzisupport.network</text>
    <text x="{TXT_X}" y="{H - BLEED - 11.6}" font-size="2.4" fill="#555">free to listed shops &#183; no ads, no tracking, no accounts &#183; ODbL data</text>
    <text x="{TXT_X}" y="{H - BLEED - 8.4}" font-size="2.4" fill="#555">not affiliated with, endorsed or sponsored by Piaggio Group or Moto Guzzi</text>
  </g>
  <!-- QR: quiet zone then modules -->
  <rect x="{QR_X - 3}" y="{QR_Y - 3}" width="{QR_SIZE + 6}" height="{QR_SIZE + 6}" fill="#fff"/>
  <path d="{qr_path}" fill="#111"/>
</svg>
"""
out = ROOT / "site" / "sticker.svg"
out.write_text(svg)
print(f"wrote {out.relative_to(ROOT)} ({n}x{n} QR modules, 100x75mm + bleed)")
