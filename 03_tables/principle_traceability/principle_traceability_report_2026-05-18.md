# NormTrace Political Rights — Principle Traceability Layer Report
**Date:** 2026-05-18
**Scope:** International standards brain + principle traceability pipeline

---

## 1. International Sources Processed

**10 sources** processed from `corpus/international/md/`.

| Source ID | Short Title | Tier | Legal Character | Provisions |
|---|---|---|---|---|
| INT-ICCPR | ICCPR | 1 | binding | 8 |
| INT-HRC-GC25 | HRC GC25 | 2 | authoritative_interpretive | 27 |
| INT-ACHR | ACHR (Pact of San José) | 1 | binding | 12 |
| INT-IADC | IADC | 3 | soft_law | 9 |
| INT-CEDAW | CEDAW | 1 | binding | 6 |
| INT-CEDAW-GR23 | CEDAW GR23 | 2 | authoritative_interpretive | 228 |
| INT-CRPD-A29 | CRPD Art. 29 | 1 | binding | 10 |
| INT-ILO169 | ILO 169 | 1 | binding | 10 |
| INT-UNDRIP | UNDRIP | 4 | soft_law | 12 |
| INT-OC2821 | IACtHR OC-28/21 | 2 | authoritative_interpretive | 94 |

---

## 2. International Standard Provisions Extracted

**Total: 416 provisions** extracted across all 10 sources.

- Tier 1 (binding treaty): 46 provisions
- Tier 2 (authoritative interpretive): 349 provisions
- Tier 3 (soft law with political commitment): 9 provisions
- Tier 4 (soft law declaration): 12 provisions
- Provisions with principle assignment: 341
- Provisions flagged manual_review_required: 94

---

## 3. Principles Created

**12 principles** (PRIN-001 to PRIN-012) loaded from `political_rights_principle_map.yml`.

| Principle ID | Name |
|---|---|
| PRIN-001 | legality_and_sufficient_legal_basis |
| PRIN-002 | equality_and_non_discrimination |
| PRIN-003 | accessibility_and_reasonable_accommodation |
| PRIN-004 | effective_participation |
| PRIN-005 | pluralism_and_collective_representation |
| PRIN-006 | due_process_and_effective_remedy |
| PRIN-007 | transparency_and_accountability |
| PRIN-008 | institutional_competence_and_independence |
| PRIN-009 | procedural_certainty_and_time_limits |
| PRIN-010 | territorial_and_multilevel_implementation |
| PRIN-011 | administrative_capacity_and_resources |
| PRIN-012 | restriction_legality_necessity_proportionality |

---

## 4. Mechanism-Principle Requirements Created

**327 requirement rows** in `mechanism_principle_requirements` table.
- Mandatory binding (tier 1): 185
- Strongly recommended (tier 2): 85
- Recommended good practice (tier 3): 38
- Complementary (tier 4): 19

---

## 5. Domestic Mechanism-Principle Rows Created

**Mexico:** 64 scoring rows (principle × mechanism combinations evaluated).
**Costa Rica:** 64 scoring rows.
**Comparison rows:** 64 (INT-OUT-06).

---

## 6. Main Gaps Detected by Country

### Mexico — Gaps (score ≤ 2)

| Principle | Mechanism | Score | Severity |
|---|---|---|---|
| PRIN-001 | referendum | 0 | critical |
| PRIN-001 | constitutional_remedies | 0 | critical |
| PRIN-001 | civil_registry_electoral_functions | 0 | critical |
| PRIN-002 | referendum | 0 | critical |
| PRIN-002 | civil_registry_electoral_functions | 0 | critical |
| PRIN-003 | referendum | 0 | critical |
| PRIN-004 | referendum | 0 | critical |
| PRIN-006 | constitutional_remedies | 0 | critical |
| PRIN-008 | civil_registry_electoral_functions | 0 | critical |
| PRIN-009 | referendum | 0 | critical |
| PRIN-010 | civil_registry_electoral_functions | 0 | critical |
| PRIN-011 | civil_registry_electoral_functions | 0 | critical |
| PRIN-012 | referendum | 0 | critical |

### Costa Rica — Gaps (score ≤ 2)

| Principle | Mechanism | Score | Severity |
|---|---|---|---|
| PRIN-001 | independent_candidacies | 0 | critical |
| PRIN-001 | popular_consultation | 0 | critical |
| PRIN-001 | recall | 0 | critical |
| PRIN-002 | popular_consultation | 0 | critical |
| PRIN-003 | popular_consultation | 0 | critical |
| PRIN-004 | popular_consultation | 0 | critical |
| PRIN-005 | independent_candidacies | 0 | critical |
| PRIN-006 | electoral_crimes | 0 | critical |
| PRIN-006 | administrative_responsibility | 0 | critical |
| PRIN-009 | popular_consultation | 0 | critical |
| PRIN-009 | recall | 0 | critical |
| PRIN-012 | recall | 0 | critical |

> **Caveat:** Gaps reflect corpus-based diagnostic legal preparedness, not legal compliance. Costa Rica scores may be conservative due to absent Sala IV jurisprudence, TSE resolutions, and LGAP (see INT-VN-008).

---

## 7. Metadata Errors and Source Verification

### HRC General Comment 25 (INT-HRC-GC25)

**Verification result: NO METADATA ERROR.**

File `observacion_general_25_comite_derechos_humanos.md` was flagged for verification due to possible confusion with a CRC (Committee on the Rights of the Child) general comment on children's digital rights. Content confirmed as HRC General Comment No. 25 on ICCPR Article 25 (Participation in Public Affairs and the Right to Vote), 1996. Language: Spanish. 29 numbered paragraphs.

**Pipeline action:** `metadata_error: false` — source used normally in all principle traceability computations.

### OC-28/21 Restriction Enforced

INT-OC2821 provisions extracted with selective keyword filter (political rights, ACHR Art. 23, democratic continuity). **94 provisions** extracted, all with `manual_review_required=true`. OC-28/21 is used as interpretive standard only — not as domestic rule source.

### Other Sources

No metadata errors detected in any other source. ILO 169 file contains full convention text despite title suggesting only Arts. 6–7 (see INT-VN-004 — positive impact on extraction).

---

## 8. Output Files Created

### `03_tables/international/`

- `international_standard_provisions.csv`
- `international_standard_provisions.json`
- `principle_definitions.csv`
- `principle_definitions.json`
- `mechanism_principle_requirements.csv`
- `mechanism_principle_requirements.json`

### `03_tables/principle_traceability/`

- `domestic_mechanism_principle_scores_MEX.csv`
- `domestic_mechanism_principle_scores_MEX.json`
- `domestic_mechanism_principle_scores_CRC.csv`
- `domestic_mechanism_principle_scores_CRC.json`
- `principle_gap_analysis_comparison.csv`
- `principle_gap_analysis_comparison.json`
- `principle_summary_by_country.csv`
- `principle_summary_by_country.json`
- `principle_traceability_matrix.csv`
- `principle_traceability_matrix.json`

---

## 9. Principle Summary Table

| Principle | MEX Avg | MEX Gaps | CRC Avg | CRC Gaps | Binding Sources | Flag |
|---|---|---|---|---|---|---|
| PRIN-001 legality_and_sufficient_legal_basis | 3.5 | 3 | 3.5 | 3 | 3 | partial |
| PRIN-002 equality_and_non_discrimination | 3.29 | 2 | 4.0 | 1 | 6 | partial |
| PRIN-003 accessibility_and_reasonable_accommodation | 3.2 | 1 | 3.4 | 1 | 4 | partial |
| PRIN-004 effective_participation | 3.83 | 1 | 3.67 | 1 | 2 | partial |
| PRIN-005 pluralism_and_collective_representation | 4.5 | 0 | 3.25 | 1 | 3 | partial |
| PRIN-006 due_process_and_effective_remedy | 3.4 | 1 | 2.8 | 2 | 3 | partial |
| PRIN-007 transparency_and_accountability | 4.0 | 0 | 4.0 | 0 | 1 | adequate |
| PRIN-008 institutional_competence_and_independence | 3.0 | 1 | 4.67 | 0 | 2 | partial |
| PRIN-009 procedural_certainty_and_time_limits | 4.0 | 1 | 3.17 | 2 | 2 | partial |
| PRIN-010 territorial_and_multilevel_implementation | 3.25 | 1 | 4.5 | 0 | 3 | partial |
| PRIN-011 administrative_capacity_and_resources | 2.67 | 1 | 4.33 | 0 | 1 | partial |
| PRIN-012 restriction_legality_necessity_proportionality | 3.67 | 1 | 3.5 | 1 | 2 | partial |

---

> **Diagnostic note:** All scores are corpus-based legal preparedness indicators only — not legal compliance findings, not judicial determinations. NormTrace is an analytical tool, not a legal opinion.