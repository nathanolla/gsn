# Guzzi Support Network (GSN)

**A community-maintained, geocoded, graded, freshness-dated map of everything that keeps a
Moto Guzzi running.** It answers the community's most common question — *"where…?"* — with a
maintained spatial database instead of decaying forum prose.

Scope at launch: US. Schema: anywhere.

## How it works
- One YAML file per node in [`/nodes`](nodes/) — human-writable, diff-clean.
- CI validates every submission against the schema ([`build/build.py`](build/build.py)):
  required fields, legal enums, coordinates inside the claimed state, URL liveness.
  **A submission that can't state `capability` and `functions` isn't a node — it's a pin,
  and it bounces automatically.**
- Merged nodes compile to `site/nodes.geojson`; the static site renders them with
  client-side home-pin, distance rings, filters, and staleness fading.
- A weekly link check keeps freshness partially automatic; a 404 auto-opens an issue.

## Contributing
Read [`doctrine.md`](doctrine.md) (the grading rubric) and [`methodology.md`](methodology.md)
(observations → categories). Then open a PR using the template. The cheapest valuable
contribution is **adopt-a-node**: confirm the phone still answers and bump `last_verified`.

## Licenses
- **Data** (`/nodes`, generated GeoJSON): [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- **Code** (everything else): MIT — see [LICENSE](LICENSE)

## Disclaimer
Provided as-is, without warranty of any kind, for informational purposes only. Entries are
community observations, not endorsements; verify before you ride. Corrections via PR; any
listed business may request correction or removal, honored within 7 days, no questions asked.

**Not affiliated with, endorsed by, or sponsored by Piaggio Group or Moto Guzzi.
Trademarks are the property of their owners.**
