# Senate Patch Merge Report — NormTrace Political Rights
## Institutional Network v2 Functional Layer
**Merge date:** 2026-05-21  
**Analyst:** NormTrace automated pipeline + manual review  
**Scope:** Mexico — MEX-ACT-005 (Senado de la República)  
**Label:** Diagnostic institutional legal mapping. Does not assert compliance.

---

## 1. Patch Review Summary

| Item | Count |
|---|---|
| Patch rows reviewed | 5 |
| Rows merged (high confidence) | 3 |
| Rows excluded (verify_before_merge) | 2 |
| Source provisions (LGIPE 2024 reform) | 3 |

**Merged:** PATCH-001, PATCH-002, PATCH-003  
**Excluded:** PATCH-004 (Cámara revisora disambiguation), PATCH-005 (oath administration, relationship_type ambiguity)

### Merged edges

| Patch ID | Edge ID | Source | Target | Relationship | Stage | Provision |
|---|---|---|---|---|---|---|
| PATCH-001 | MEX-V2-SEN-0001 | MEX-ACT-005 | MEX-ACT-001 | issues_call | activation | LGIPE Art. 498 Num. 3 |
| PATCH-002 | MEX-V2-SEN-0002 | MEX-ACT-005 | MEX-ACT-001 | submits_to | registration | LGIPE Art. 501 Num. 1 |
| PATCH-003 | MEX-V2-SEN-0003 | MEX-ACT-005 | MEX-ACT-007 | adjudicates | registration | LGIPE Art. 501 Num. 2 |

All three derive from the 2024 judicial election reform (CPEUM Art. 96; LGIPE Art. 498, 501). All carry `edge_confidence = high`, `edge_derivation_method = explicit_textual_relation`, `legal_anchor_type = statutory`, `anchor_strength = 4`.

### Excluded edges

**PATCH-004** — Senate → SCJN: `submits_to` (popular_consultation, verification)  
Provision LFCP Art. 27 Fr. IV designates the *Cámara revisora* to forward the consultation question to the Supreme Court. Senate's role as revisora is constitutionally conventional, not textually explicit in this provision. Excluded pending chamber-role disambiguation.

**PATCH-005** — Senate → Citizens: `implements_result` (right_to_stand_for_election, implementation)  
Provision LGIPE Art. 535 Num. 1 assigns oath administration to the Senate. The relationship type is ambiguous between `implements_result` and `organizes_process`, and the stage classification (implementation vs. internal_governance) is unresolved. Excluded pending manual review.

---

## 2. Isolation Status: MEX-ACT-005

**Senado de la República is no longer an isolated actor.**

| Metric | Before patch | After patch |
|---|---|---|
| in_degree | 0 | 0 |
| out_degree | 0 | 3 |
| total_degree | 0 | 3 |
| degree_centrality | 0.0 | 0.167 |
| betweenness_centrality | 0.0 | 0.0 |
| mechanism_participation_count | 0 | 1 |
| high_medium_edge_count | 0 | 3 |

MEX-ACT-005 now has out-degree 3 with all edges classified as high confidence. In-degree remains 0: the Senate receives no functional outputs from other actors in the encoded provisions. This correctly reflects its role as an originating authority (convocatoria emitter, list integrator, candidacy adjudicator) rather than a downstream recipient in the right_to_stand_for_election process.

Betweenness remains 0 for MEX-ACT-005 because it has no incoming edges — no shortest paths flow *through* it in the directed graph. This is expected and not a code error.

**Validation flag update:**  
- `V2-VAL-0009` (`actor_absent_from_functional_edges`): reclassified to `senado_patch_merged`, severity `info` — isolation resolved.  
- `V2-VAL-0001` (`senado_absent_from_actor_mechanism_edges`): severity downgraded from `medium` to `low` — the 2024 reform gap is now partially addressed; remaining gap (citizen_initiative, popular_consultation, legislative_petition) is documented for future pipeline runs.

---

## 3. Affected Mechanism: MEX-MECH-002 (right_to_stand_for_election)

### Edge counts

| Metric | Before patch | After patch | Δ |
|---|---|---|---|
| edge_count_all | 77 | 80 | +3 |
| edge_count_hi_med | 22 | 25 | +3 |
| node_count_all | 9 | 10 | +1 |
| node_count_hi_med | 8 | 9 | +1 |

MEX-ACT-005 is now present in the high/medium subgraph of this mechanism.

### Network density

| Metric | Before | After |
|---|---|---|
| network_density_hi_med | 0.2500 | 0.2222 |

Density decreased from 0.25 to 0.22 because adding MEX-ACT-005 as a new node increases the denominator (n × (n−1)) faster than the 3 new edges increase the unique-pair numerator. This is structurally correct: the Senate is a sparse connector — it sends edges but receives none — which lowers overall density while expanding coverage.

### Process stage coverage

The `activation` stage was previously uncovered in MEX-MECH-002. It is now covered:

| Stage | Before | After | New actors |
|---|---|---|---|
| activation | uncovered | **covered** | MEX-ACT-005 (issues_call → INE) |
| registration | covered (5 actors, 6 hi-med) | covered (6 actors, 8 hi-med) | MEX-ACT-005 added |
| adjudication | covered (3 actors, 2 hi-med) | covered — unchanged | — |
| implementation | covered (2 actors, 1 hi-med) | covered — unchanged | — |
| internal_governance | covered (5 actors, 10 hi-med) | covered — unchanged | — |

Gaining activation coverage is analytically significant: the convocatoria emission (PATCH-001) is the stage-triggering act that opens the judicial election cycle. Its absence from the v2 graph was a structural gap, not a modelling choice.

### Administrative dependence

| Metric | Before | After |
|---|---|---|
| statutory_edges (hi-med) | 17 | 20 |
| statutory_share_hi_med | 0.7727 | 0.8000 |
| dependence_level | low | **statutory** |

The 3 new edges (all `legal_anchor_type = statutory`, `anchor_strength = 4`) raise the statutory share from 0.77 to 0.80, crossing the 0.50 threshold that triggers the `statutory` dependence classification. This accurately reflects the 2024 reform's character: the Senate's judicial election roles are entirely creatures of statute (LGIPE), not constitutional convention.

---

## 4. Actor Centrality Changes

### MEX-ACT-001 (INE) — Betweenness emerges

| Metric | Before patch | After patch |
|---|---|---|
| betweenness_centrality | 0.0 | **0.0972** |

Adding MEX-ACT-005 with out-edges exclusively toward INE and Citizens creates directed paths where INE is the sole intermediate node between the Senate and actors that INE connects to downstream. Before the patch, the MEX graph was near-complete and betweenness was 0 for all actors. The Senate's constrained out-degree (3 edges, 2 targets) creates genuine path-dependency through INE that was not present in the collapsed graph.

This is the first non-zero betweenness reading in the MEX functional graph. It confirms INE's role as the primary procedural gateway between the Senate's 2024 reform competences and the broader electoral machinery.

### All other actors

Degree counts and betweenness for MEX-ACT-002 through MEX-ACT-010 (excluding MEX-ACT-005) are unchanged. In-degree of MEX-ACT-001 and MEX-ACT-007 increased by 2 and 1 respectively (reflecting the new inbound edges from MEX-ACT-005).

---

## 5. Bottleneck Risk

| Metric | Before | After |
|---|---|---|
| dominant_actor_id | MEX-ACT-004 | MEX-ACT-004 |
| dominant_actor_degree (hi-med pairs) | 12 | 8 |
| dominant_actor_share | 0.2727 | 0.2500 |
| bottleneck_risk | low | low |

Bottleneck risk remains `low`. MEX-ACT-004 (Congreso — Cámara de Diputados) remains the most-connected actor, but its dominance share fell from 0.27 to 0.25 as the 3 new edges dilute its relative centrality. No new bottleneck is introduced by the Senate patch.

---

## 6. Files Regenerated

The following files were updated (CSV + JSON pairs):

| File stem | Change |
|---|---|
| `institutional_edges_v2` | +3 rows (MEX-V2-SEN-0001/0002/0003) |
| `institutional_edges_v2_pre_senado_patch_backup` | Created (1353 edges — pre-patch snapshot) |
| `actor_centrality_metrics_v2` | MEX-ACT-005 updated; MEX-ACT-001 betweenness updated |
| `mechanism_network_metrics_v2` | MEX-MECH-002 row recomputed |
| `bottleneck_diagnostics_v2` | MEX-MECH-002 row recomputed |
| `process_stage_coverage_v2` | MEX-MECH-002 rows recomputed; activation stage added |
| `administrative_dependence_metrics_v2` | MEX-MECH-002 row recomputed |
| `network_validation_notes_v2` | V2-VAL-0001 downgraded; V2-VAL-0009 cleared |

All CSV files in `03_tables/institutional_network_v2_functional/` and JSON mirrors in `05_webapp/public/data/institutional_network_v2_functional/` are consistent.

---

## 7. Pending Actions

**PATCH-004 — Senate → SCJN (popular_consultation)**  
Requires: confirm which chamber acts as Cámara revisora in the popular consultation legislative sequence (LFCP Art. 27). If Senate is consistently revisora (Chamber of Deputies as cámara de origen), merge at medium confidence.

**PATCH-005 — Senate → Citizens (right_to_stand_for_election, oath)**  
Requires: resolve relationship_type (`implements_result` vs `organizes_process`) and confirm process_stage (`implementation` vs `internal_governance`). Recommend tagging as `internal_governance` given the Senate's institutional character of the protesta act.

Both excluded edges remain documented in `mexico_senado_edges_patch.csv` with `merge_recommendation = verify_before_merge` and `manual_review = true`.

---

*NormTrace Political Rights — diagnostic institutional legal mapping. Results describe legal mandate structure as encoded in statutory text. They do not assert implementation, compliance, or effective exercise of any right.*
