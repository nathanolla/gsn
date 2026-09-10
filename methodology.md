# Methodology

Rubric 1.1.0. Nodes are graded from dated observations, not opinion.

## Observations
An observation is a dated fact with a method. Methods, strongest first:

- `official-locator` — appears on the manufacturer's dealer locator
- `called` / `visited` / `bought` — first-party check
- `community-endorsement` — dated, sourced forum or owners-group recommendation; must name the venue and date; supports capability evidence only, not franchise status; does not outrank a first-party check
- `website` — weakest; alone, caps status at `unverified`

## Categories
Derived from observations, not stored as opinion:

- `full-service` — locator listing or franchise statement, books Guzzi service, service depth evidenced
- `satellite` — franchise or service without depth evidence
- `depot` — mail-order parts at scale
- `performance` — tuning or dyno
- `heritage` — vintage/classic specialization
- `knowledge` — book, software, or club (no coordinates)

Multi-role nodes list several.

## Eras
`eras` (see doctrine) is derived the same way: an era is listed only when an observation
evidences work on that platform family — a website statement of vintage/classic Guzzi
service, a dated community report naming the model worked on, or a first-party check.
Absence of the field is "unknown", never "none". Rubric 1.2.0 adds this section.

## Status
- `active` — recent observations support operation
- `unverified` — website-only, or `last_verified` over 24 months
- `defunct` — evidence of closure; kept, rendered faded

## Bot-walls
An HTTP 403/bot-challenge on re-verification is **not evidence of closure** — the server
is alive and refusing robots. If a standing `official-locator` observation less than 24
months old exists, the node stays `active` and the 403 is recorded as an observation.
Website-only nodes behind a bot-wall degrade to `unverified` (nothing can be confirmed).
A first-party check (`called`/`visited`) beats the wall entirely.

## Corrections
Submit a newer or better observation; the category recomputes. Any listed business may request correction or removal.

## Reviews
Node cards may link to a business's public review page. This dataset does not import, cache, render, or summarize ratings.
