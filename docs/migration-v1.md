# Migration note — v1 private survey → GSN public schema (2026-07-26)

The founder's v1 map stored viewer-relative tier labels (`core-standby-SW`, `edge-E`).
Those mixed intrinsic and relative attributes; GSN splits them (doctrine.md):

| v1 tier | GSN capability | note |
|---|---|---|
| core-primary / core-standby-* | full-service | relative role now computed client-side |
| edge-* ("garnish franchise") | satellite | vocabulary scrub — value-laden labels do not ship |
| depot | depot | |
| performance-W | performance | |
| heritage-* | heritage | |
| book / software | knowledge | |

Commercial-personality notes, negotiation intel, and named private individuals were split
into the founder's private overlay per addendum §1.6/§7 and do not ship in this dataset.
