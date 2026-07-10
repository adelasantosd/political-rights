# NormTrace Political Rights — Webapp Data Readiness Report
**Generated:** 2026-05-21  
**Pipeline:** NormTrace Political Rights (offline deterministic; no LLM at runtime)  
**Scope:** Mexico (MEX) + Costa Rica (CRC) + International Standards  

> **Caveat — applies to all outputs:** All datasets described in this report are diagnostic legal preparedness indicators derived from statutory and constitutional text. They describe the structure of legal mandates as encoded in national and international instruments. They do not assert legal compliance, effective exercise of rights, or policy performance. Label all frontend displays accordingly.

---

## Summary Statistics

| Metric | Count |
|---|---|
| Total datasets indexed | 39 |
| Frontend-ready (JSON present in webapp directory) | 32 |
| Not yet mirrored to webapp (JSON exists in 03_tables only) | 7 |
| Datasets with `manual_review_flags_present = true` | 12 |
| Datasets requiring `verify_before_merge` action | 0 (patch edges excluded, not in inventory) |
| Analytical layers covered | 6 |

---

## Verification Checklist

| # | Verification | Status | Notes |
|---|---|---|---|
| 1 | Mexico legal brain JSON files exist | ✓ PASS | 8 files in `05_webapp/public/data/legal_brains/mexico/` |
| 2 | Costa Rica legal brain JSON files exist | ✓ PASS | 8 files in `05_webapp/public/data/legal_brains/costa_rica/` |
| 3 | International standards JSON files exist | ⚠ PARTIAL | JSON files exist in `03_tables/international/` but `05_webapp/public/data/international_standards/` directory does not exist. 3 datasets not mirrored. |
| 4 | Jurisprudence layer JSON files exist | ✓ PASS | 5 files in `05_webapp/public/data/jurisprudence/`. Note: case texts pending ingestion (16 download plan entries). |
| 5 | Principle traceability matrix JSON exists | ✓ PASS | `principle_traceability_matrix.json` present in webapp. |
| 6 | Principle traceability explainer JSON exists | ✓ PASS | `principle_traceability_explainer.json` present in webapp. |
| 7 | Institutional network v2 functional JSON files exist | ✓ PASS | 9 files in `05_webapp/public/data/institutional_network_v2_functional/`. Post-Senate-patch (2026-05-21). |
| 8 | Network v1 exploratory files not required for frontend | ✓ CONFIRMED | `05_webapp/public/data/institutional_network/` (v1) and `05_webapp/public/data/network/` contain exploratory outputs derived by role-hierarchy co-mention. Not required; superseded by v2 functional layer. |
| 9 | Raw Markdown corpus files not required for frontend runtime | ✓ CONFIRMED | Markdown corpus files (01_corpus/) are pipeline inputs only. No Markdown files appear in `05_webapp/public/data/`. Frontend consumes only precomputed JSON/CSV. |
| 10 | All outputs are diagnostic legal preparedness indicators, not compliance findings | ✓ CONFIRMED | Caveat embedded in `data_inventory.json` and all validation note files. Label must appear in all frontend displays. |

---

## Missing Required Datasets

The following 7 datasets have JSON mirrors in `03_tables/` but are **not yet present in `05_webapp/public/data/`**. They are not missing from the pipeline — they are missing only from the webapp serving directory. No pipeline rerun is required.

### International Standards (3 datasets)

The directory `05_webapp/public/data/international_standards/` does not exist.

| Dataset ID | File name | Records | Action required |
|---|---|---|---|
| INV-INT-001 | `principle_definitions` | 12 | Copy `03_tables/international/principle_definitions.json` → `05_webapp/public/data/international_standards/` |
| INV-INT-002 | `mechanism_principle_requirements` | 327 | Copy `03_tables/international/mechanism_principle_requirements.json` → same dir |
| INV-INT-003 | `international_standard_provisions` | 1670 | Copy `03_tables/international/international_standard_provisions.json` → same dir (load on demand — large) |

**Recommended action:** Create `05_webapp/public/data/international_standards/` and copy the 3 JSON files. No data transformation required — files are already in JSON format.

### Principle Traceability Detail Tables (4 datasets)

These files provide more granular breakdowns than the matrix (INV-PT-001) already in the webapp. The matrix alone is sufficient for the primary heatmap; these are needed for drilldown panels.

| Dataset ID | File name | Records | Action required |
|---|---|---|---|
| INV-PT-003 | `domestic_mechanism_principle_scores_MEX` | 64 | Copy `03_tables/principle_traceability/domestic_mechanism_principle_scores_MEX.json` → `05_webapp/public/data/principle_traceability/` |
| INV-PT-004 | `domestic_mechanism_principle_scores_CRC` | 64 | Copy `03_tables/principle_traceability/domestic_mechanism_principle_scores_CRC.json` → same dir |
| INV-PT-005 | `principle_gap_analysis_comparison` | 64 | Copy `03_tables/principle_traceability/principle_gap_analysis_comparison.json` → same dir |
| INV-PT-006 | `principle_summary_by_country` | 12 | Copy `03_tables/principle_traceability/principle_summary_by_country.json` → same dir |

**Recommended action:** Copy 4 JSON files. No data transformation required.

---

## Frontend-Ready Datasets (32)

All datasets below have a JSON file present in `05_webapp/public/data/` and can be consumed directly by the frontend without further action.

### Layer: domestic_legal_brain

| Dataset ID | Country | File | Records | Primary Key | Load strategy |
|---|---|---|---|---|---|
| INV-MEX-001 | Mexico | `actor_map.json` | 10 | actor_id | Eager (small) |
| INV-MEX-002 | Mexico | `actor_mechanism_edges.json` | 625 | source_id+actor_id+mechanism_name | Lazy / on mechanism select |
| INV-MEX-003 | Mexico | `country_profile.json` | 17 | country_code | Eager (small) |
| INV-MEX-004 | Mexico | `legal_provisions.json` | 7502 | provision_id | On-demand only — paginate |
| INV-MEX-005 | Mexico | `mechanism_map.json` | 13 | mechanism_id | Eager (small) |
| INV-MEX-006 | Mexico | `mechanism_sources.json` | 145 | source_id+mechanism_id | Lazy |
| INV-MEX-007 | Mexico | `source_hierarchy.json` | 6 | source_id | Eager (small) |
| INV-CRC-001 | Costa Rica | `costa_rica_actor_map.json` | 9 | actor_id | Eager (small) |
| INV-CRC-002 | Costa Rica | `costa_rica_actor_mechanism_edges.json` | 422 | source_id+actor_id+mechanism_name | Lazy |
| INV-CRC-003 | Costa Rica | `costa_rica_country_profile.json` | 9 | country_code | Eager (small) |
| INV-CRC-004 | Costa Rica | `costa_rica_legal_provisions.json` | 1884 | provision_id | On-demand / paginated |
| INV-CRC-005 | Costa Rica | `costa_rica_mechanism_map.json` | 12 | mechanism_id | Eager (small) |
| INV-CRC-006 | Costa Rica | `costa_rica_mechanism_sources.json` | 83 | source_id+mechanism_id | Lazy |
| INV-CRC-007 | Costa Rica | `costa_rica_source_hierarchy.json` | 12 | source_id | Eager (small) |

### Layer: jurisprudence_interpretive_layer

| Dataset ID | File | Records | Notes |
|---|---|---|---|
| INV-JUR-001 | `jurisprudence_index.json` | 16 cases | Wrapped: `data.jurisprudence_index` |
| INV-JUR-002 | `jurisprudence_mechanism_map.json` | 72 | Wrapped: `data.jurisprudence_mechanism_map` |
| INV-JUR-003 | `jurisprudence_principle_map.json` | 50 | Wrapped: `data.jurisprudence_principle_map` |
| INV-JUR-005 | `jurisprudence_download_plan.json` | 16 | Internal — expose only as pending status count |

### Layer: principle_traceability

| Dataset ID | File | Records | Notes |
|---|---|---|---|
| INV-PT-001 | `principle_traceability_matrix.json` | 128 | Wrapped: `data.matrix`. Primary heatmap dataset. |
| INV-PT-002 | `principle_traceability_explainer.json` | 128 | Wrapped: `data.explainer`. Score drilldown dataset. |

### Layer: institutional_network_v2_functional

| Dataset ID | File | Records | Notes |
|---|---|---|---|
| INV-NET-001 | `institutional_nodes_v2.json` | 19 | Graph nodes. MEX-ACT-005 connected post-patch. |
| INV-NET-002 | `institutional_edges_v2.json` | 1356 | Graph edges. Filter by confidence=high|medium for analytics. |
| INV-NET-003 | `mechanism_network_metrics_v2.json` | 27 | Mechanism overview table. |
| INV-NET-004 | `actor_centrality_metrics_v2.json` | 19 | Centrality rankings. INE bc=0.097 post-patch. |
| INV-NET-005 | `bottleneck_diagnostics_v2.json` | 24 | Bottleneck risk heatmap. |
| INV-NET-006 | `process_stage_coverage_v2.json` | 117 | Stage coverage heatmap. |
| INV-NET-007 | `administrative_dependence_metrics_v2.json` | 27 | Anchor type distribution. |
| INV-NET-009 | `excluded_comention_edges.json` | 920 | Methodology disclosure only — do not render in graph. |

### Layer: validation_and_caveats

| Dataset ID | File | Records | Notes |
|---|---|---|---|
| INV-MEX-008 | `validation_notes.json` (MEX) | 10 | Display in MEX caveat panel |
| INV-CRC-008 | `costa_rica_validation_notes.json` | 12 | Display in CRC caveat panel |
| INV-JUR-004 | `jurisprudence_validation_notes.json` | 10 | Wrapped: `data.jurisprudence_validation_notes` |
| INV-NET-008 | `network_validation_notes_v2.json` | 13 | V2-VAL-0009 cleared post-patch |

---

## Datasets Requiring Manual Review Caveats

The following 12 datasets contain a `manual_review_required` or `needs_review` field with at least one `true` value. The frontend must surface this as a caveat indicator (e.g., a "⚠ Some items pending review" label) on any panel that renders these datasets.

| Dataset ID | File | Layer | Caveat |
|---|---|---|---|
| INV-MEX-001 | actor_map (MEX) | domestic_legal_brain | Some actor roles flagged for manual review |
| INV-MEX-002 | actor_mechanism_edges (MEX) | domestic_legal_brain | Some provision-actor assignments pending review |
| INV-MEX-004 | legal_provisions (MEX) | domestic_legal_brain | Some provisions flagged (authority field encoding) |
| INV-CRC-001 | actor_map (CRC) | domestic_legal_brain | Some actor roles flagged |
| INV-CRC-002 | actor_mechanism_edges (CRC) | domestic_legal_brain | Some assignments pending review |
| INV-CRC-004 | legal_provisions (CRC) | domestic_legal_brain | Some provisions flagged |
| INV-INT-002 | mechanism_principle_requirements | international_standards | Some normative assignments manual |
| INV-INT-003 | international_standard_provisions | international_standards | Some principle assignments manual |
| INV-NET-002 | institutional_edges_v2 | institutional_network_v2_functional | manual_review_required=true on some edges (incl. PATCH-004/005 excluded) |
| INV-NET-001 | institutional_nodes_v2 | institutional_network_v2_functional | Some node fields flagged |
| INV-PT-003 | domestic_mechanism_principle_scores_MEX | principle_traceability | needs_review field present |
| INV-PT-004 | domestic_mechanism_principle_scores_CRC | principle_traceability | needs_review field present |

---

## Recommended Default Frontend Datasets

These are the minimum datasets required to render a functional dashboard without any additional data preparation. All are frontend-ready (JSON present in webapp).

**Country overview panel:**
- INV-MEX-003 (`country_profile.json`) + INV-CRC-003 (`costa_rica_country_profile.json`)
- INV-MEX-005 (`mechanism_map.json`) + INV-CRC-005 (`costa_rica_mechanism_map.json`)

**Principle traceability heatmap (primary view):**
- INV-PT-001 (`principle_traceability_matrix.json`) — 128 rows, scores + labels
- INV-PT-002 (`principle_traceability_explainer.json`) — drilldown on cell click

**Institutional network graph:**
- INV-NET-001 (`institutional_nodes_v2.json`) — graph nodes
- INV-NET-002 (`institutional_edges_v2.json`) — graph edges (filter high+medium)
- INV-NET-003 (`mechanism_network_metrics_v2.json`) — mechanism panel
- INV-NET-005 (`bottleneck_diagnostics_v2.json`) — bottleneck risk column

**Caveat panels (mandatory on all views):**
- INV-MEX-008 (`validation_notes.json`) + INV-CRC-008 (`costa_rica_validation_notes.json`)
- INV-NET-008 (`network_validation_notes_v2.json`)
- Standard caveat string from `data_inventory.json` → `caveat` field

**Load-on-demand (provision drilldown):**
- INV-MEX-004 (`legal_provisions.json`) — 7502 records, paginate
- INV-CRC-004 (`costa_rica_legal_provisions.json`) — 1884 records

---

## Datasets Not Required for Frontend Runtime

| File / directory | Reason excluded |
|---|---|
| `01_corpus/` (Markdown corpus) | Pipeline input only. Not in webapp directory. Raw legal texts are source material, not output. |
| `05_webapp/public/data/institutional_network/` (v1) | Superseded by v2 functional layer. Derived from role-hierarchy co-mention, not explicit legal authority. For exploratory reference only. |
| `05_webapp/public/data/network/` | Summary aggregations from v1. Not required. |
| `03_tables/institutional_network_v2_functional/institutional_edges_v2_pre_senado_patch_backup.csv` | Internal version control backup. Do not expose to frontend. |
| `03_tables/institutional_network_v2_functional/mexico_senado_edges_patch.csv` | Operational patch file. Not for frontend. |
| `03_tables/institutional_network_v2_functional/senado_actor_audit.csv` | Internal audit (298 rows). Not for frontend. |
| `02_country_legal_brains/` (YAML files) | Pipeline configuration. Not for frontend. |
| `scripts/` (Python scripts) | Pipeline code. Not for frontend. |

---

## Notes on JSON Wrapping

Several JSON files use a wrapper object pattern rather than a top-level array. Frontend code must unwrap:

| File | Wrapper key |
|---|---|
| `principle_traceability_matrix.json` | `data.matrix` |
| `principle_traceability_explainer.json` | `data.explainer` |
| `jurisprudence_index.json` | `data.jurisprudence_index` |
| `jurisprudence_mechanism_map.json` | `data.jurisprudence_mechanism_map` |
| `jurisprudence_principle_map.json` | `data.jurisprudence_principle_map` |
| `jurisprudence_validation_notes.json` | `data.jurisprudence_validation_notes` |
| `jurisprudence_download_plan.json` | `data.jurisprudence_download_plan` |

All other JSON files in the webapp directory are top-level arrays and can be consumed directly.

---

## Pending Actions Before Full Frontend Deployment

1. **Create `05_webapp/public/data/international_standards/`** and copy 3 JSON files from `03_tables/international/`.
2. **Copy 4 principle traceability detail JSONs** from `03_tables/principle_traceability/` to `05_webapp/public/data/principle_traceability/`.
3. **Decide on PATCH-004 and PATCH-005** (Senate popular consultation and oath administration edges) — pending manual verification. Run `scripts/build_institutional_network_layer_v2_functional.py` with `--apply-patch PATCH-004 PATCH-005` once disambiguation is resolved.
4. **Decide on jurisprudence full-text ingestion** — 16 cases are indexed (INV-JUR-001) but full texts are not yet downloaded (INV-JUR-005). Surface as "pending enrichment" status in UI.
5. **Add frontend caveat label** to all views: *"Results are diagnostic legal preparedness indicators. They do not assert compliance or effective exercise of any right."*

---

*NormTrace Political Rights — diagnostic institutional legal mapping. Generated 2026-05-21.*
