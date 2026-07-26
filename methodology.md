# Methodology — observations in, categories out

**Rubric version 1.0.0 (2026-07-26).**

## Principle
Store **observations**, derive **categories**, never publish **characterizations**.

- An *observation* is a dated, attributed, verifiable fact with a method:
  `2026-07-25 · visited · 3 new Guzzi units on floor` ·
  `2026-07 · called · books Guzzi service appointments: yes` ·
  `listed on official Piaggio dealer locator: yes`.
- Accepted methods, in descending signal quality:
  1. `official-locator` — authoritative and binary (Piaggio's own claim)
  2. `called` / `visited` / `bought` — verifiable by anyone
  3. `website` — weakest; caps a new node's status at `unverified`
- Floor counts are one dated input among several, never the sole basis — allocation and
  season make them noisy.

## Category derivation rules (v1.0.0)
- official-locator listing **or** own-site franchise statement, **and** books Guzzi service,
  **and** service depth evidenced (dedicated techs / multi-line Italian house / ≥3 new units
  observed) → `full-service`
- listing or franchise statement **and** books service, without depth evidence → `satellite`
- mail-order parts at scale → `depot`
- dyno/tuning development as a primary function → `performance`
- vintage specialization as a primary function → `heritage`
- no coordinates (book / software / club) → `knowledge`

A category change is traceable to a data change or a rubric-version change — never to
editorial judgment.

## Status
- `active` — most recent observations support operation
- `unverified` — website-only evidence, or last_verified > 24 months
- `defunct` — evidence of closure; **kept**, rendered ghosted

## Corrections & disputes
Categories are mechanical derivations from dated observations; disputes are resolved by
submitting newer or better observations via PR — the category recomputes.
**The dispute channel is the contribution channel.**

## Delist-on-request
Any listed business may request correction or removal — honored within **7 days**, no
questions asked, logged in repo history.

## Quality opinion is outsourced
Node cards may *link* to a business's public review page; this dataset never imports,
caches, renders, or summarizes ratings, and the rubric never consumes review data.
