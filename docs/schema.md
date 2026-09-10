# The GSN data endpoint — stable schema, v1

**Endpoint:** `https://guzzisupport.network/nodes.geojson`
**License:** [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) — use it, build on it,
attribute "Guzzi Support Network" with a link, and share-alike any derived database.
**CORS:** served with `Access-Control-Allow-Origin: *` (GitHub Pages) — fetchable from any
browser app, Discord bot, or script without a proxy.

Also served, same license, regenerated on every build:
- `https://guzzisupport.network/gsn-nodes.gpx` — all active geocoded nodes as GPX waypoints
- `https://guzzisupport.network/gsn-poi.gpi` — the same as a Garmin POI file

## The stability promise

Within schema v1:
- **Existing fields never change meaning or type.** Enums only gain values; they never lose
  or repurpose them. New optional properties may appear — ignore what you don't know.
- The FeatureCollection carries `properties.schema_version` (`"1.x"`). A breaking change
  would ship as a **new filename**, never as a silent change to this one.
- `id` is permanent: a node keeps its `id` for life, including after closure (`defunct`).

## Shape

A GeoJSON `FeatureCollection`. Each feature: `geometry` is a `Point` (lon, lat) or `null`
(knowledge nodes may be coordinate-free), and `properties`:

| property | type | semantics |
|---|---|---|
| `id` | string | permanent slug, unique, matches the YAML filename in `/nodes` |
| `name` | string | display name |
| `city`, `state`, `country` | string | `state` is US-style where applicable, else `""`; `country` ISO-3166 alpha-2 |
| `layer` | enum | `franchise` · `independent` · `knowledge` · `event` |
| `capability` | enum[] | `full-service` · `satellite` · `depot` · `performance` · `heritage` · `knowledge` · `event` — graded from observations (see [doctrine](../doctrine.md)) |
| `eras` | enum[]? | platform families evidenced: `loop-frame` · `tonti` · `small-block` · `spine-frame` · `carc` · `v85` · `v100-pads`. **Absent = unknown, never "none"** |
| `brands` | string[] | marques handled; may be empty (unpublished) |
| `functions` | string[] | free-form: what a rider can use it for |
| `url`, `phone`, `address` | string? | as published by the business |
| `status` | enum | `active` · `unverified` · `defunct` (kept, not deleted) |
| `last_verified` | date | newest observation of any method |
| `last_scraped` | date? | newest `website`/`official-locator` observation |
| `last_rider` | date? | newest first-party check (`called`/`visited`/`bought`) |
| `rider_method` | enum? | which first-party method earned `last_rider` |
| `event_start`, `event_end` | date? | event layer only; past events stay listed |
| `observations` | object[] | the evidence: `{date, method, fact}` — the provenance trail |
| `verified_by` | string | who recorded the newest verification |

Dates are `YYYY-MM-DD`. The collection-level `properties` also carry `generated_by` and
`count`.

## Ground rules for consumers

- **Freshness is part of the data.** Render or filter on `last_verified` /
  `last_rider`; presenting a two-year-old scrape as current is on you, not us.
- The observations are the product. If your UI has room for one extra line, show the
  newest observation's method and date.
- Corrections and additions land as PRs on [the repo](https://github.com/nathanolla/gsn) —
  a bot that finds a dead node is a bot that can open an issue.
