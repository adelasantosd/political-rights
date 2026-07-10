# NormTrace Political Rights — Principle Traceability Scoring Calibration Audit
**Date:** 2026-05-19  
**Scope:** `domestic_mechanism_principle_scores_MEX.csv` and `domestic_mechanism_principle_scores_CRC.csv`  
**Method:** Statistical analysis of score distributions, dimension coverage, provision pools, and actor edge lookups  
**Status:** AUDIT ONLY — no output files modified

---

## 1. Executive Finding

The current scoring model is **over-permissive**. Every mechanism present in either corpus receives a score of 5 ("integrated_basis"), while absent mechanisms receive 0. This bimodal distribution renders the intermediate score levels (1–4) unused and the "adequate" preparedness flag meaningless. The root cause is not a single bug but a combination of four structural problems, one of which is an outright code defect (actor lookup for Mexico).

---

## 2. Score Distribution

| Score | Label | Mexico count | Costa Rica count |
|---|---|---|---|
| 0 | absent | 13 | 12 |
| 1 | declaratory_only | 0 | 0 |
| 2 | partial_basis | 0 | 0 |
| 3 | functional_basis | 0 | 0 |
| 4 | strong_basis | 0 | 0 |
| 5 | integrated_basis | 51 | 52 |
| **Total** | | **64** | **64** |

Every present mechanism in both countries scores 5. Intermediate scores 1–4 are never assigned. This is a strong diagnostic indicator of over-permissive calibration.

---

## 3. Problems Identified

### Problem 1 — Code Defect: Mexico Actor Edge Lookup (HIGH SEVERITY)

**What the code does:**  
`load_domestic_data()` reads actor-mechanism edges using:
```python
actor = e.get("actor_id") or e.get("actor") or ""
mech  = e.get("mechanism_id") or e.get("mechanism") or ""
```

**What goes wrong:**  
Mexico's actor edge CSV has columns `actor_id`, `mechanism_id`, `mechanism_name`. The expression `e.get("mechanism_id")` returns the internal ID string (e.g., `"MEX-MECH-001"`), **not the mechanism name**. The `mech_actors` dictionary is then indexed by `"MEX-MECH-001"` rather than `"vote"`. When `build_scores_table` looks up `mech_actors.get("vote", set())`, it finds nothing, yielding `actor_count = 0` for every Mexico row.

**Evidence:**  
All 51 non-zero Mexico score rows have `actor_count = 0` and `actor_assigned` is absent from their `dimension_checks_passed`. Yet the Mexico actor edge table has confirmed data for 13 distinct mechanism names, with vote=78 edges, political_parties=80, electoral_remedies=67, etc.

**Impact:**  
Mexico scores reach 5 without actor confirmation. The `actor_assigned` dimension silently fails for all Mexico entries. Scores are technically inflated because actor confirmation is supposed to be required for score ≥ 3 (per the scoring algorithm specification in `principle_traceability_rules.yml`).

**Proposed fix:**  
Change the edge reader to prefer `mechanism_name` over `mechanism_id`:
```python
mech = e.get("mechanism_name") or e.get("mechanism") or e.get("mechanism_id") or ""
```
This aligns Mexico to the same actor-confirmed scoring path as Costa Rica.

---

### Problem 2 — Pooled-Text Keyword Matching is a Weak Signal at Large Corpus Size (HIGH SEVERITY)

**What the code does:**  
All provisions for a given mechanism are concatenated into a single text pool. Dimension checks (timeline, equality, accessibility, territorial, etc.) fire if **any single provision** in the pool matches the keyword pattern.

**Evidence:**

| Mechanism | Provisions (MEX) | Accessibility keyword hits | Percentage |
|---|---|---|---|
| vote | 1,041 | 15 | 1.4% |
| political_parties | 702 | ~11 | ~1.6% |
| electoral_remedies | 206 | ~6 | ~2.9% |

For `vote` in Mexico: 15 out of 1,041 provisions mention accessibility keywords. Yet the `accessibility_measure` dimension passes, contributing to score 5. The 15 matching provisions include 4 from `electoral_administrative` sources (anchor_strength 2 — INE internal procedures), 5 from `parliamentary_regulation` (Reglamento del Senado — not directly electoral), and only 3 from `constitution` or statutory sources with anchor_strength ≥ 4.

**Impact:**  
A mechanism with 1,000 provisions will statistically guarantee that every keyword dimension fires, even when only 1–2% of provisions are relevant to that dimension. This inflates scores by 1–2 levels across all high-volume mechanisms. Every principle that includes a large mechanism (vote, political_parties, electoral_remedies) inherits inflated cross-cutting dimension scores.

**Additional evidence — principle-agnostic scoring:**  
The same 1,041 vote provisions score identically for PRIN-001 (legality), PRIN-002 (equality), PRIN-003 (accessibility), PRIN-004 (participation), PRIN-007 (transparency), PRIN-009 (timing), PRIN-010 (territorial), and PRIN-012 (restrictions). There is no principle-specific evidence filter. A provision about electoral campaign timelines counts as "timeline evidence" for both PRIN-009 (procedural certainty) and PRIN-001 (legal basis). This is not analytically sound.

**Proposed fix:**  
Require that keyword-dimension evidence passes a source-quality threshold: the matching provision must have `anchor_strength ≥ 3` (statutory or higher) for a dimension to be credited. Administrative-only keyword matches (anchor_strength ≤ 2) should not be counted.

Additionally, for mechanisms with ≥200 provisions, require that each dimension fires in ≥2 distinct `source_type` categories with `anchor_strength ≥ 3` (not just a single provision in the pooled text).

---

### Problem 3 — Actor Confirmation Not Gated for Score ≥ 4 (HIGH SEVERITY)

**What the code does:**  
`actor_assigned` is one of nine dimensions contributing to a raw dimension count. The score 5 threshold is `dim_count ≥ 5`. No dimension is required; all are optional contributions to the count.

**Impact:**  
Mexico scores 5 across 51 entries without actor confirmation (due to Problem 1, but also by design). Even after fixing Problem 1, the algorithm would allow score 5 with actor_count = 0 if other 5+ dimensions pass. This is inconsistent with the principle traceability specification in `principle_traceability_rules.yml` which states:

> *"step_4_dimension_scoring: CORE dimensions: actor_check: any provision has an actor_id in actor_mechanism_edges"*
> *"contributes_to_score: [3, 4, 5]"*

The specification intends actor assignment to be required at score ≥ 3, but the implementation does not enforce it as a gate — it treats it as one optional dimension among many.

**Proposed fix:**  
Introduce a CORE dimension gate: if `actor_assigned` fails AND `actor_count == 0`, cap score at 2 for mechanisms where actors are expected (i.e., all mechanisms except soft declaratory rights). This aligns implementation with the specification and ensures scores ≥ 3 require at least one institutionally designated actor.

---

### Problem 4 — No Principle-Specific Dimension Filtering (MEDIUM SEVERITY)

**What the code does:**  
All nine dimension checks are applied uniformly to every (principle, mechanism) combination. PRIN-003 (accessibility) and PRIN-007 (transparency) get the same nine dimension checks against the same provision pool.

**Evidence:**  
PRIN-003/vote (accessibility) scores 5 in both Mexico and Costa Rica. The `accessibility_measure` dimension fires, but also `equality_measure`, `remedy_present`, `restriction_criteria`, and `territorial_coverage` — dimensions that are not specifically relevant to PRIN-003's operational question (whether persons with disabilities can access voting procedures). The score reflects that the vote corpus is large and diverse, not that accessibility is specifically well-addressed.

**Impact:**  
Principles that have different analytical focus (e.g., PRIN-003 accessibility vs PRIN-007 transparency) receive identical scores for the same mechanism because they draw from the same provision pool and the same dimension checks. The principle-specific `operational_dimensions` field in `political_rights_principle_map.yml` is not used to filter which dimensions are counted for each principle.

**Proposed fix:**  
Map each principle's `operational_dimensions` to the corresponding dimension checks in `compute_score`. Only count dimensions relevant to the specific principle. For example:
- PRIN-003: count only `anchor_statutory`, `actor_assigned`, `accessibility_measure` (core); `equality_measure` (secondary)
- PRIN-007: count only `anchor_statutory`, `actor_assigned`, `process_defined`; then transparency-specific keywords

This would require extending `compute_score` to accept a per-principle dimension whitelist.

---

### Problem 5 — "Adequate" Flag Threshold Too Low (MEDIUM SEVERITY)

**What the code does:**  
`overall_preparedness_flag` is set to "adequate" when average score ≥ 3.5, "partial" when ≥ 2.0, "insufficient" when < 2.0.

**Evidence:**  
All 12 principles receive "adequate" for both countries. With 51/64 Mexico scores at 5 and only 13 at 0, the average for any principle is approximately (51/n × 5 + 13/n × 0), which always exceeds 3.5 for principles with few gaps.

**Impact:**  
The "adequate" flag does not differentiate between a framework with deep, specific, multi-source legal preparation and one where keywords happen to fire across a large corpus. The flag provides no useful analytical signal.

**Proposed fix:**  
After recalibrating the scoring model (fixes above), raise the "adequate" threshold to average score ≥ 4.0, "partial" for ≥ 3.0. Alternatively, require that **all** mechanisms for a principle (not just the average) reach score ≥ 3 for "adequate" — one absent mechanism (score 0) for a binding treaty obligation should not be averaged away.

---

## 4. Summary of Proposed Calibration Changes

| ID | Problem | Severity | Proposed Change | File to Modify |
|---|---|---|---|---|
| CAL-001 | Mexico actor edge lookup uses mechanism_id instead of mechanism_name | HIGH — Code defect | Change `e.get("mechanism_id")` to `e.get("mechanism_name") or e.get("mechanism")` | `build_principle_traceability_tables.py` → `load_domestic_data()` |
| CAL-002 | Pooled-text keyword matching fires on any single provision regardless of anchor strength | HIGH | Require matching provision has anchor_strength ≥ 3; for corpora ≥200 provisions require ≥2 distinct source_types | `build_principle_traceability_tables.py` → `compute_score()` |
| CAL-003 | Actor_assigned not gated; mechanism can reach score 5 with zero actors | HIGH | Gate scores ≥ 3 on actor_assigned passing (where actors are expected); cap at 2 if actor_count = 0 | `build_principle_traceability_tables.py` → `compute_score()` |
| CAL-004 | Same nine dimensions counted for all principles regardless of principle-specific relevance | MEDIUM | Use per-principle dimension whitelist from `political_rights_principle_map.yml` operational_dimensions | `build_principle_traceability_tables.py` → `compute_score()` |
| CAL-005 | "Adequate" flag average threshold too low (3.5) given bimodal distribution | MEDIUM | Raise to ≥ 4.0 average, or add condition that no mandatory mechanism scores 0 | `build_principle_traceability_tables.py` → `build_summary_table()` |

---

## 5. Expected Score Distribution After Recalibration

With CAL-001 through CAL-003 applied, the expected approximate distribution is:

| Score | Label | Expected (post-calibration) |
|---|---|---|
| 0 | absent | ~15–18 per country (mechanisms genuinely absent) |
| 1 | declaratory_only | ~2–5 (constitutional-only, no implementing law) |
| 2 | partial_basis | ~5–8 (statutory basis, no actor confirmation OR low anchor keywords only) |
| 3 | functional_basis | ~10–15 (actor + process, missing timeline or remedy evidence from high-anchor sources) |
| 4 | strong_basis | ~15–20 (actor + process + at least 2 cross-cutting dimensions from anchor ≥ 3 sources) |
| 5 | integrated_basis | ~5–10 (full evidence from constitutional/statutory sources with actor, process, timeline, remedy, and equality/accessibility) |

This distribution would make the scoring scale meaningful and would allow the "adequate" flag to differentiate across principles.

---

## 6. Jurisprudence Layer Implication

The jurisprudence calibration audit reinforces the decision to set `affects_scoring=false` for all jurisprudence entries. If the current scoring model is over-permissive, adding jurisprudence as a scoring input would only compound the inflation. Once the scoring model is recalibrated (CAL-001 to CAL-005), a carefully scoped jurisprudence scoring contribution could be considered — but only for:

- Interpretive test refinement of gap descriptions (not score increases)  
- Severity reclassification of identified gaps (e.g., promoting a score-2 gap to "critical" when binding IACtHR case law establishes an unambiguous obligation)  
- Never for increasing domestic anchor_strength or converting a corpus gap into legal preparedness

---

## 7. Files Reviewed (No Modifications Made)

- `03_tables/principle_traceability/domestic_mechanism_principle_scores_MEX.csv` — read-only
- `03_tables/principle_traceability/domestic_mechanism_principle_scores_CRC.csv` — read-only
- `03_tables/principle_traceability/principle_summary_by_country.csv` — read-only
- `03_tables/country_legal_brains/mexico/mexico_actor_mechanism_edges.csv` — read-only
- `03_tables/country_legal_brains/mexico/mexico_legal_provisions.csv` — sampled
- `scripts/build_principle_traceability_tables.py` — logic reviewed

**No output tables were modified.** This report documents findings and proposed changes for human review and approval before any recalibration run.

---

> **Diagnostic note:** Proposed calibration changes are not corrections to data errors. They are refinements to the scoring model design to better reflect the analytical intent of the principle traceability layer: diagnosing operational legal preparedness, not merely detecting corpus presence.
