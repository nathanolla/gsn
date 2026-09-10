# Doctrine — grading

Nodes are graded by function, not existence.

## Principles
- Function over existence; capability over inventory.
- A node is judged by what a rider near it can use it for.
- A node unverified for over two years is rendered faded. Closed nodes are kept and marked `defunct`, not deleted.

## Tier One
The first resource is the rider's own kit: tubeless plug kit, mini compressor, fuses, tape, multi-tool, tire gauge, and the relevant node numbers saved before a trip.

## Capability grades
| grade | meaning |
|---|---|
| `full-service` | Books and performs Guzzi service with wrenching depth |
| `satellite` | Carries the franchise or books service; useful for position and diagnostics |
| `depot` | Parts at scale by mail |
| `performance` | Tuning, dyno, performance work |
| `heritage` | Vintage/classic specialization |
| `knowledge` | Book, software, or club (no coordinates) |

Multi-role nodes list several grades.

## Era competence
"Full-service" says nothing about whether the shop has ever seen a Bing carb. Nodes may
carry `eras` — the Guzzi platform families the shop can actually touch:

| era | means |
|---|---|
| `loop-frame` | V700 / Ambassador / Eldorado loop frames ('67–'74) |
| `tonti` | Tonti-frame big blocks (V7 Sport → 1100, '71–'90s) |
| `small-block` | V35 / V50 / V65 lineage, Breva 750, Nevada |
| `spine-frame` | Daytona / Centauro / V11 spine frames |
| `carc` | CARC bikes (Breva / Griso / Norge / Stelvio, 2004–2016) |
| `v85` | V85 TT platform (2019–) |
| `v100-pads` | V100 compact block, liquid-cooled + PADS electronics (2022–) |

An era claim is graded like everything else: from a dated observation (a vintage-service
statement on the shop's site, a rider's dated report of loop-frame work done), never
inferred from `full-service`. **No `eras` field means "unknown", not "none".**

## Relative roles
Primary, standby, and edge describe a node relative to the viewer's home pin and are computed client-side, not stored. The dataset stores only intrinsic attributes.

## A node entry answers
- What can a rider use it for?
- What was observed, when, and by which method?
