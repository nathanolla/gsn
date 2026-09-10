# System Specification: GuzziOracle (AquilaDoc) Technical Engine
**Document Version:** 1.0.0  
**Target Platform:** Progressive Web Application (PWA) & Headless API  
**Ecosystem Alignment:** Guzzi Support Network (`guzzisupport.network`)  
**Core Principle:** Deterministic Technical Accuracy over Generative Fluency  

---

## 1. System Mission & Architectural Directives

`GuzziOracle` is an offline-capable, citation-grounded technical intelligence system designed for owners, mechanics, and restorers of Moto Guzzi motorcycles. 

### 1.1 Non-Negotiable Directives
1. **Zero Hallucination Tolerance:** Generative extrapolation on mechanical clearances, torque values, wiring pinouts, and fluid ratings is classified as a critical system fault. If a spec is not indexed in the ground-truth store, the system must emit an explicit negative assertion (`STATUS: UNVERIFIED_SPEC`).
2. **Era & Architecture Segregation:** Transverse air-cooled V-twins span distinct engineering lineages across 60+ years. The system must never cross-pollinate small-block, big-block (loop, Tonti, spine, CARC), and liquid-cooled (V100/Stelvio) specifications.
3. **Local-First / Edge Survivability:** Primary triage algorithms, emergency wiring bypasses, and common service metrics must operate fully offline without external cloud dependencies via local browser storage (IndexedDB/OPFS).
4. **Strict Citation Contract:** Every returned torque spec, fluid capacity, and valve lash value must include exact page/section reference to the primary workshop manual or factory technical bulletin.

---

## 2. Platform Architecture

The platform uses a split-plane design: a client-side offline core running inside a zero-tracking Progressive Web App, paired with a high-fidelity cloud/hybrid Retrieval-Augmented Generation (RAG) pipeline for complex queries.

```
┌─────────────────────────────────────────────────────────────┐
│                   Client Layer (PWA / Edge)                 │
│  - Offline Cache (IndexedDB / CacheStorage)                 │
│  - Glove-Compatible Mobile UI (Tailwind + Svelte/React)     │
│  - Client-side SQLite/WASM Spec Lookup                      │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / WebSockets
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 GuzziOracle Ingestion & RAG                 │
├──────────────────────────────┬──────────────────────────────┤
│    Document Parsing & OCR    │     Retrieval Engine         │
│  - LlamaParse / Table-Aware  │  - Hybrid Vector + BM25      │
│  - Electrical Schematic CAD  │  - Metadata Hard-Filtering   │
│  - Microfiche Parts Cross-Ref│  - Re-ranking (Cohere/BGE)   │
└──────────────────────────────┴──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Primary Knowledge Store                     │
│  - Factory Workshop Manuals (OEM Piaggio/Guzzi)             │
│  - Gregory Bender Technical Archive (This Old Tractor)       │
│  - GuzziTech / WildGuzzi Curated Registry                   │
│  - GuzziDiag & PADS Diagnostic Code Mapping                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Knowledge Taxonomy & Engine Lineages

All queries and retrieval spaces must be filtered by mechanical family before semantic retrieval executes.

| Engine Family | Representative Models | Displacement / Valvetrain | Primary Failure / Quirk Footprint |
| :--- | :--- | :--- | :--- |
| **Loop Frame** | V700, V750 Ambassador, Eldorado | 703cc – 844cc (2V OHV) | Chrome bore flaking, 4-speed gearbox shimming, generator belt tension. |
| **Tonti Big Block** | V7 Sport, 850 Le Mans, California II/III, 1000S | 844cc – 1064cc (2V OHV) | Timing chain tensioners, U-joint spline lube, points vs early electronic ignitions. |
| **Spine Frame** | Daytona, 1100 Sport, V11 Sport/Le Mans | 1064cc (2V & 4V Hi-Cam) | 5-speed vs 6-speed transmission pawl springs, relay voltage drop, tank suck. |
| **Small Block (Classic)** | V35, V50, V65, V75, Nevada | 349cc – 744cc (2V Heron Head) | Universal joint failure, oil capacity sensitivity, clutch pushrod seals. |
| **CARC Big Block** | Breva 1100/1200, Griso, Norge, 1200 Sport | 1064cc – 1151cc (2V & 4V) | Flat tappet vs roller tappet conversion (8V motors), CARC torque arm bushings, starter relay wiring ("Startus Interruptus"). |
| **Modern Small Block** | V7 I/II/III, V7 850, V9 Bobber/Roamer | 744cc – 853cc (2V Hemi/Heron) | Single throttle body calibration, dry single-plate clutch adjustment, valve lash settling. |
| **Air/Oil-Cooled E4/E5** | V85 TT (Strada / Travel / Adventure) | 853cc (Titanium intake valves) | Pushrod lash stability, de-cat exhaust remapping thresholds, rear shock preload. |
| **Compact Block (Liquid)** | V100 Mandello, Stelvio 1200 (modern) | 1042cc (DOHC 4V Liquid) | Ride-by-wire calibration, quickshifter microswitch alignment, coolant circuit venting. |

---

## 4. Ingestion & Document Pipeline Specification

### 4.1 Document Processing
1. **Table Integrity:** Scanned service manuals frequently store fluid viscosity, tightening torques, and valve clearances in tabular format. The ingestion layer must extract tables using structured layout recognition (Markdown tables or JSON schema) rather than raw text streaming to preserve column-row association.
2. **Diagram Extraction:** Exploded microfiches and schematics must be chunked with high-resolution image bounding boxes, indexed by component group (e.g., `GROUP_03_TRANSMISSION`, `GROUP_12_FINAL_DRIVE`).

### 4.2 Metadata Schema
Every chunk injected into the vector/lexical index must include:
```json
{
  "chunk_id": "v85tt_wsm_2021_sec02_p048_01",
  "document_title": "Moto Guzzi V85 TT E4/E5 Workshop Manual",
  "source_type": "OEM_WORKSHOP_MANUAL",
  "publication_date": "2021-03",
  "engine_family": "AIR_COOLED_853",
  "chassis_codes": ["KW", "KY"],
  "models_supported": ["V85 TT", "V85 TT Travel"],
  "system": "POWERTRAIN",
  "subsystem": "CYLINDER_HEAD",
  "page_reference": 48,
  "torque_specs": [
    {
      "fastener": "Cylinder head fixing nut M10x1.5",
      "torque_nm": 42.0,
      "sequence_required": true,
      "lubrication_condition": "Light engine oil on threads"
    }
  ],
  "clearances": [
    {
      "component": "Intake valve tappet",
      "metric_value": "0.10 mm",
      "condition": "Cold engine (T <= 25C)"
    },
    {
      "component": "Exhaust valve tappet",
      "metric_value": "0.15 mm",
      "condition": "Cold engine (T <= 25C)"
    }
  ]
}
```

---

## 5. Core Operational Engines

### 5.1 The Triage & Diagnostic State Machine
The system handles roadside queries via symptom isolation trees before touching generative generation:

1. **State 1: Machine Confirmation**
   * Prompt user for year, exact displacement, and lineage if not stored in local garage profile.
2. **State 2: Fault Categorization**
   * Classify: `NO_CRANK`, `CRANK_NO_START`, `POOR_IDLE_SURGE`, `CHARGING_FAULT`, `DRIVELINE_NOISE`.
3. **State 3: Deterministic Known-Fault Interception**
   * *Trigger:* California / Breva / Griso + "Dash turns on, starter clicks or silent".
   * *Direct Path:* Emit "Startus Interruptus" protocol (relay #3 coil trigger feed voltage drop analysis) before generic battery diagnostics.
   * *Trigger:* 2008–2012 1200 4V (Griso, Stelvio, Norge) + "Top end ticking / loss of power".
   * *Direct Path:* Immediate check for A5 engine code and flat vs. roller tappet wear status.

### 5.2 Parts Cross-Reference & Alternative Sourcing
Provides verified alternative automotive/industrial component matches for out-of-production or high-cost OEM parts:
* **Sensors:** Weber-Marelli IAW throttle position sensors (e.g., PF09 cross-compatibility).
* **Fuel Delivery:** Bosch / Walbro in-tank pump drop-ins vs OEM complete assembly replacements.
* **Bearings & Seals:** SKF / FAG industrial standard part numbers for swingarm bearings, bevel box needle bearings, and fork seals.
* **Filters:** Industrial and automotive oil filter equivalents (Mann, Mahle, UFI, Wix).

---

## 6. System Prompt & Guardrail Directives

When interacting with the retrieval layer, the inference model operates under the following strict system prompt:

```markdown
You are GuzziOracle, an authoritative Moto Guzzi mechanical and technical specialist.

RULES OF ENGAGEMENT:
1. SPECIFICATION SAFETY: You will NOT state torque specifications, bearing tolerances, or valve clearances from memory or inference. Every specification must cite the specific OEM manual, edition, and page number provided in the context.
2. DRY VS WET THREADS: If a torque value is retrieved, you must state whether the manual requires clean dry threads or lightly oiled threads. If unspecified, append: "Warning: Verify thread condition in manual."
3. ERA ISOLATION: Never assume small block specs apply to big blocks. Do not suggest CARC torque values for Tonti swingarms.
4. ROAD-SIDE PRIORITY: For non-garage emergency queries, prioritize immediate mechanical safety, temporary bypass options (e.g., relay jumping), and minimal tool requirements.
5. NEGATIVE RESPONSES: If the provided reference documents do not contain the exact model specification, explicitly state: "Data not found in indexed manuals for [Model Year]. Do not guess."
```

---

## 7. Offline PWA & Data Storage Architecture

* **Framework:** SvelteKit or lightweight React compiled to static progressive assets.
* **Styling:** Low-contrast industrial palette (amber/carbon/monochrome), high legibility in direct sunlight, minimum 48px touch targets for gloved operation.
* **Storage Engines:**
  * `IndexedDB` via `idb-keyval` for storing user garage profiles (VIN, engine code, modifications, installed tire sizes, service records).
  * `Origin Private File System (OPFS)`: Stores model-specific offline bundles (~15MB compressed JSON + WebP schematic pack).
* **Network Independence:**
  * Pre-caches complete emergency wiring schematics and quick-service matrices (valve lash, fluid grades, spark plug gaps, torque charts) for up to 3 selected bikes.

---

## 8. Deployment & Phased Rollout

1. **Phase 1: Static Specs & Emergency Matrix (Local-First)**
   * Deploy curated tables for modern (V85 TT, V7 III/850, V100) and iconic classic (V11, California 1100, Le Mans) bikes directly to `guzzisupport.network/oracle`.
2. **Phase 2: RAG Pipeline Integration**
   * Ingest factory manuals and ThisOldTractor technical articles into hybrid Vector + Lexical search.
   * Enable natural language question answering with manual citations.
3. **Phase 3: Community Verification & Pull Requests**
   * Allow verified mechanics and network nodes to submit errata and field-tested solutions via GitHub PRs against the static schema.

---

## Triage note (Claude, 2026-09-10 — banked during the GSN nine-item round)

Nathan's spec, filed under ideas; his follow-up decision: **inference = Mistral,
ideally EU-hosted** (credibility + privacy; coherent with GSN's
privacy-by-architecture posture and the European skew of the audience).

Flags to resolve before any build starts:
1. **§2/Knowledge Store lists GuzziTech — a banned source in GSN**, enforced by a
   CI sweep. Excise it from the spec, or the ban gets consciously revisited first.
   It does not enter an index as a side effect.
2. **Rights posture needed before Phase 2**: OEM workshop manuals are copyrighted;
   the Gregory Bender / ThisOldTractor archive has its own permission terms.
   Phase 1 (curated static spec matrices, community-verifiable via PR) has no such
   dependency and is the honest place to start.
3. **Era taxonomy**: the spec's 8 lineages map cleanly onto the 7 `eras` values
   shipped in GSN this round (spec splits modern small-block vs V85; GSN folds
   them — reconcile when Phase 1 tables are authored).
4. Sequencing: after the current GSN round per sprint discipline.
