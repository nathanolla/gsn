# Specification Addendum A: Infrastructure, Economics, & Privacy Architecture
**Document Reference:** GuzziOracle-SPEC-ADD-01  
**Parent Document:** `GuzziOracle_System_Specification.md`  
**Status:** Approved for Implementation  
**Primary Engine Selection:** Mistral AI (`mistral-small-latest` / `mistral-large-latest`)  
**Deployment Infrastructure:** Cloudflare Workers + KV + D1 / Vectorize  

---

## 1. Architectural Justification: Mistral AI Stack

To ensure strict operational sovereignty, cost predictability, and lingual accuracy with European technical documentation, the inference layer is standardized on Mistral AI.

### 1.1 Technical & Cultural Alignment
1. **Multilingual Density:** Italian workshop documentation, Mandello factory service notes, and Italian enthusiast archives (*Anima Guzzista*) benefit from Mistral's European training corpus, minimizing semantic drift when translating technical terminology (e.g., *gioco valvole*, *coppia di serraggio*, *frenafiletti*).
2. **Deterministic Tool & JSON Adherence:** Mistral models enforce rigid structural schema outputs without conversational conversational baggage, directly supporting GuzziOracle's zero-extrapolation contract.
3. **Open-Weight Portability:** The option to run identical weights on local infrastructure via `vLLM` or `llama.cpp` ensures that the GSN platform is never vendor-locked to proprietary American hyperscalers.

---

## 2. Economic & Token Budget Modeling

The system is designed to operate on a 100% self-funded model without requiring invasive programmatic ad networks, user subscriptions, or data tracking.

### 2.1 Pricing Foundations (2026 Reference Tiers)
* **Mistral Small 4 / Ministral:** ~$0.15 / 1M input tokens | ~$0.60 / 1M output tokens.
* **Mistral Large 3:** ~$0.50 / 1M input tokens | ~$1.50 / 1M output tokens.

### 2.2 Projected Monthly Operating Ledger (Steady State: 100 Queries / Day)

| Parameter | Metric per Request | Monthly Aggregate (3,000 queries) |
| :--- | :--- | :--- |
| **System Prompt & Rules** | ~450 tokens | 1.35 M tokens |
| **Retrieved Manual Excerpts (RAG)** | ~1,000 tokens | 3.00 M tokens |
| **User Symptom / Question** | ~50 tokens | 0.15 M tokens |
| **Total Input Load** | **1,500 tokens** | **4.50 M tokens** |
| **Structured Output (JSON/Spec)** | **250 tokens** | **0.75 M tokens** |

#### Projected Cost Breakdown:
* **Mistral Small 4 Pipeline:**
  * Input: $4.50 \times \$0.15 = \$0.675$
  * Output: $0.75 \times \$0.60 = \$0.450$
  * **Net Monthly Model Cost:** **~$1.13 USD**
* **Mistral Large 3 Pipeline (High-Reasoning Fallback):**
  * Input: $4.50 \times \$0.50 = \$2.250$
  * Output: $0.75 \times \$1.50 = \$1.125$
  * **Net Monthly Model Cost:** **~$3.38 USD**

*With Edge KV Caching (estimated 50% hit rate for common torque/clearance queries), realized recurring API expenditures drop below **$1.00 - $2.00 USD / month**.*

---

## 3. Threat Modeling & Financial Guardrails

Because the service runs on personal funding, the gateway layer must strictly mitigate distributed scrapers, automated spiders, and denial-of-wallet (DoW) attacks.

### 3.1 Edge Protection Layers (Cloudflare Worker)
```
[ Incoming Request ]
        │
        ├─► [ 1. Rate Limiter ] ──► Exceeds 10 req/min per IP? ──► HTTP 429 (Too Many Requests)
        │
        ├─► [ 2. Hard Token Counter (KV) ] ──► Exceeds $15.00/mo quota? ──► Degrade to Static Lookup
        │
        ├─► [ 3. Exact Query Match (KV) ] ──► Cache Hit? ──► Return Cached JSON (0 API Cost)
        │
        └─► [ 4. Authenticated Request Forward ] ──► Mistral API + Authorization Bearer
```

### 3.2 Guardrail Invariants
1. **Hard Spend Ceiling:** Configured directly in the Mistral Platform console at **$15.00 USD / month**. If breached, all generative endpoints fail closed to static manual links.
2. **Client-Side Exclusion:** API secret keys (`MISTRAL_API_KEY`) must never be exposed via client-side JavaScript or WebAssembly runtimes. All calls are routed through serverless edge functions.
3. **Deterministic Query Interception:** Queries matching exact regex formulas (e.g., `/^v85\s?tt\s+(valve|tappet)\s+(lash|clearance)/i`) never hit the LLM; they return pre-indexed JSON directly from Cloudflare KV.

---

## 4. Privacy & Anti-Surveillance Doctrine

To preserve the zero-tracking ethos of `guzzisupport.network`:

1. **Zero Logging of IP Addresses:** Cloudflare Workers must strip connecting IP headers before routing payloads.
2. **Ephemeral Contexts:** Diagnostic chat sessions are maintained exclusively in client browser memory (`sessionStorage` or `IndexedDB`). No chat transcripts are stored in server-side relational databases.
3. **No Third-Party Analytics:** Prohibit Google Analytics, Meta Pixel, Datadog RUM, or external telemetry SDKs. Monitoring is restricted to raw, aggregated HTTP status counters at the DNS edge.
4. **Voluntary Community Support:** In place of paywalls or tracking ads, a passive, non-modal sponsorship link (*"Buy a tank of gas for the GSN server"*) is placed in the documentation footer.

---

## Triage note (Claude, 2026-09-10)

Banked with the parent spec (guzzioracle-spec-v1.md). Confirms the Mistral
decision with numbers ($1-3/mo at 100 q/day, $15 hard ceiling, fail-closed to
static lookup) and a privacy doctrine consistent with GSN's. Two additions to
the parent triage flags:
1. **"European resources for maximum cred" vs Cloudflare**: Mistral is EU;
   Cloudflare is a US company (EU points of presence notwithstanding). If the
   sovereignty argument is load-bearing for positioning, the edge layer is the
   soft spot — Scaleway/OVH function equivalents exist. Worth one deliberate
   sentence in the spec either way.
2. **Anima Guzzista in the corpus** inherits the same rights-posture item as
   ThisOldTractor: forum authors' content, ask-first.
Also note: deterministic regex interception (§3.2.3) + static Phase 1 tables
means the useful core ships with zero LLM dependency — consistent with the
parent note that Phase 1 is the honest start.
