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
# Nathan's design brief (2026-09-10): QR code, website URL, and a solid
# abstract image of a transverse V-twin. Nothing else but the legal microtype.
W, H, BLEED = 104.0, 79.0, 2.0
QR_SIZE = 38.0
QR_X, QR_Y = W - BLEED - 7.0, 14.0  # placeholder; set below
QR_X = W - BLEED - 7.0 - QR_SIZE
cell = QR_SIZE / n
path = []
for y, row in enumerate(m):
    for x, v in enumerate(row):
        if v:
            path.append(f"M{QR_X + x * cell:.3f} {QR_Y + y * cell:.3f}"
                        f"h{cell:.3f}v{cell:.3f}h-{cell:.3f}z")
qr_path = "".join(path)


def cylinder():
    """One finned cylinder pointing 'up' in local coords; rotated per side.
    Solid single-fill silhouette: head cap, fin bars, barrel."""
    parts = ['<rect x="-6" y="-33" width="12" height="21" rx="1"/>',      # barrel
             '<rect x="-8" y="-36.5" width="16" height="4" rx="1.2"/>']   # head
    for fy in (-30.5, -26, -21.5, -17):                                    # fins
        parts.append(f'<rect x="-9.5" y="{fy}" width="19" height="2.4" rx="1"/>')
    return "".join(parts)


V2_CX, V2_CY = 28.5, 35.5
v2 = (f'<g transform="translate({V2_CX} {V2_CY}) scale(0.88)" fill="#c8102e">'
      f'<g transform="rotate(-45)">{cylinder()}</g>'
      f'<g transform="rotate(45)">{cylinder()}</g>'
      '<circle cx="0" cy="0" r="11.5"/>'
      '<rect x="-8" y="9" width="16" height="8" rx="2.5"/>'
      '</g>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm"
     viewBox="0 0 {W} {H}">
  <title>Guzzi Support Network — counter sticker</title>
  <rect x="0" y="0" width="{W}" height="{H}" fill="#efefea"/>
  <!-- trim line (100x75mm) -->
  <rect x="{BLEED}" y="{BLEED}" width="{W - 2 * BLEED}" height="{H - 2 * BLEED}"
        fill="none" stroke="#bbb" stroke-width="0.1" stroke-dasharray="1 1.5"/>
  <!-- the mark: solid abstract transverse V-twin -->
  {v2}
  <!-- QR with quiet zone -->
  <rect x="{QR_X - 3}" y="{QR_Y - 3}" width="{QR_SIZE + 6}" height="{QR_SIZE + 6}" fill="#fff"/>
  <path d="{qr_path}" fill="#111"/>
  <text x="{W / 2}" y="66.5" text-anchor="middle" font-size="5.2"
        font-family="'Courier New',monospace" font-weight="bold" fill="#111">guzzisupport.network</text>
  <text x="{W / 2}" y="73.5" text-anchor="middle" font-size="2.0" fill="#666"
        font-family="'Times New Roman',Times,serif">free to listed shops &#183; no tracking &#183; ODbL data &#183; not affiliated with Piaggio Group or Moto Guzzi</text>
</svg>
"""
out = ROOT / "site" / "sticker.svg"
out.write_text(svg)
print(f"wrote {out.relative_to(ROOT)} ({n}x{n} QR modules, 100x75mm + bleed)")
