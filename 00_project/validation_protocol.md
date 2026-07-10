# Validation Protocol — NormTrace-Political Rights

**Version:** 0.1.0-pilot
**Date:** 2026-05-18
**Status:** Current

---

## 1. Purpose

This protocol defines the validation checks that must be run on all tables in NormTrace-Political Rights before outputs are used in analysis or reporting. It also defines the structure of validation reports and the categories of issues.

Validation is performed at two levels:

- **Automated validation:** Checks run by Python scripts in `06_scripts/validation/` against the CSV tables. Catches structural errors, missing fields, broken references, and formatting problems.
- **Human legal review:** Checks that require expert judgment. Cannot be automated. Must be performed by a qualified legal professional before any output is considered validated.

---

## 2. Automated validation checks

### 2.1 Structural integrity checks

| Check | Description | Severity |
|---|---|---|
| Missing primary key | Any row where the primary key field is null or empty | Critical |
| Duplicate primary key | Any two rows sharing the same primary key value in the same table | Critical |
| Broken foreign key | Any foreign key value that does not match an existing primary key in the referenced table | Critical |
| Empty required field | Any required field that is null or empty (see field definitions in data dictionary) | Critical |
| Invalid controlled vocabulary | Any field using a controlled vocabulary value that is not in the approved list | Medium |
| Inconsistent country code | Any row where the `country` field uses a value not in the approved list (`mexico`, `costa_rica`, `international`, `comparative_soft_law`) | Medium |
| Semicolon within field value | Any field value that contains an unescaped semicolon (which would corrupt the CSV delimiter) | Critical |
| Line break within field value | Any field value that contains an unescaped line break | Critical |
| Whitespace padding | Any field value that begins or ends with leading or trailing whitespace | Minor |

### 2.2 Source traceability checks

| Check | Description | Severity |
|---|---|---|
| Missing source reference | Any analytical row (in provisions, mechanisms, mapping, barriers) that does not have a `source_id` or `provision_id` FK | Critical |
| Source ID not in corpus index | Any `source_id` referenced in an analytical table that does not appear in `political_rights_corpus_index.csv` | Critical |
| Unverified source | Any analytical row referencing a source with `verification_status: pending_verification` | Medium |
| Missing article reference | Any provision row that does not include an `article_ref` value | Medium |
| Missing paragraph reference for jurisprudence | Any jurisprudence standard row that does not include a paragraph number | Medium |

### 2.3 Date and vigency checks

| Check | Description | Severity |
|---|---|---|
| Unverified date | Any corpus index row where `last_amendment_date` is null and no explanation is in `notes` | Medium |
| Vigency unverified | Any corpus index row with `vigency_status: unverified` that is referenced in an analytical table | Medium |
| Version date older than last amendment | Any row where `version_date` predates `last_amendment_date` by more than 12 months | Medium |
| Missing date_added | Any corpus index row without a `date_added` value | Minor |

### 2.4 Mechanism and mapping consistency checks

| Check | Description | Severity |
|---|---|---|
| Mechanism without provisions | Any mechanism row in `political_rights_mechanisms.csv` that has no corresponding rows in `political_rights_domestic_provisions.csv` | Medium |
| Mechanism without activation requirements | Any mechanism row in `political_rights_mechanisms.csv` that has no corresponding rows in `political_rights_activation_requirements.csv` | Medium |
| Mapping without domestic anchor | Any row in `political_rights_mapping.csv` where `provision_id` is null and `notes` does not contain a no-match explanation | Critical |
| Mapping without standard | Any row in `political_rights_mapping.csv` where `standard_id` is null | Medium |
| Barrier without provision | Any row in `political_rights_barrier_typology.csv` where `provision_id` is null and the barrier type is not `formal_recognition_only` | Medium |
| Barrier without legal text excerpt | Any barrier row where `legal_text_excerpt` is null | Medium |
| Actor edge without provision | Any row in `political_rights_actor_mechanism_edges.csv` where `provision_id` is null | Medium |

### 2.5 Activation scale checks

| Check | Description | Severity |
|---|---|---|
| Activation level out of range | Any row where `activation_level` is not an integer between 0 and 5 | Critical |
| Missing activation evidence | Any row where `activation_level` is 3, 4, or 5 and `activation_evidence` is null | Medium |
| High confidence with no evidence | Any row where `activation_confidence: high` and `activation_evidence` is null | Medium |
| Formal recognition only coded as high activation | Any row where the only identified provision is a constitutional declaration and `activation_level` is 4 or 5 | Critical — requires human review |
| Implementation gap coded as high activation | Any row where a barrier of type `implementation_gap` or `formal_recognition_only` is present and `activation_level` is 4 or 5 | Critical — requires human review |

### 2.6 Review status checks

| Check | Description | Severity |
|---|---|---|
| Missing review status | Any analytical row without a `review_status` value | Medium |
| Validated without reviewer ID | Any row with `review_status: validated` and no `reviewer` value | Critical |
| Validated without review date | Any row with `review_status: validated` and no `review_date` value | Critical |

---

## 3. Human legal review requirements

The following checks cannot be automated. They require review by a qualified legal professional:

| Check | Description |
|---|---|
| Activation level correctness | Verify that each activation level assigned is supported by the specific provisions cited, applying the methodology note criteria |
| Formal recognition vs activation | Confirm that no mechanism with missing procedural architecture is coded at level 3 or above |
| Barrier type appropriateness | Confirm that each barrier type correctly characterises the legal gap or restriction in the specific provision |
| Threshold proportionality | Review whether thresholds classified as potentially disproportionate are correctly assessed against IACtHR/HRC standards |
| Jurisprudence holdings | Verify that extracted holdings, criteria, and operative paragraphs are accurately reproduced and correctly attributed |
| Cross-table consistency | Confirm that the same mechanism is described consistently in the mechanisms table, activation requirements table, barrier table, and mapping table |
| Comparative consistency | Confirm that equivalent mechanisms in Mexico and Costa Rica are classified using the same criteria |
| International standard mapping | Confirm that the correspondence type assigned (meets_standard / partial / divergence / silence) is supported by the specific standard cited |

---

## 4. Validation report structure

Validation runs produce a report saved to `04_outputs/validation_reports/` with the following structure:

```
validation_report_{date}.md
```

**Report sections:**

### Summary
- Date and time of run
- Total rows checked per table
- Total critical issues found
- Total medium issues found
- Total minor issues found
- Human review rows flagged

### Critical issues
One row per critical issue:
- Table name
- Row ID (primary key value)
- Field name
- Issue description
- Recommended action

### Medium issues
Same format as critical issues.

### Minor issues
Same format, grouped by issue type.

### Rows requiring human legal review
List of row IDs flagged for human review, with the reason for the flag.

### Validation status summary per table
Table-level summary: number of rows, number of issues by severity, percentage validated.

---

## 5. Issue severity definitions

| Severity | Definition | Action required |
|---|---|---|
| **Critical** | The issue makes the data unreliable or causes broken references. The row cannot be used in analysis until resolved. | Must be resolved before the row is included in any output |
| **Medium** | The issue indicates missing information, unverified data, or a possible error. The row can be used with caution but must be reviewed. | Flag with `review_status: under_review`; resolve before final validation |
| **Minor** | The issue is a formatting or consistency problem that does not affect data reliability. | Resolve in next data cleaning pass |

---

## 6. Validation frequency

- **Before any major analytical step:** Run automated validation before extracting provisions, before mapping, and before generating outputs.
- **After any bulk import or conversion:** Run automated validation after any batch addition of sources or rows.
- **Before any output export:** Run automated validation before generating country snapshots, comparative briefs, or exported tables.
- **Human review:** Schedule human legal review at least once per phase milestone.

---

## 7. Validation scripts

Automated validation scripts are stored in `06_scripts/validation/`. Scripts use Python. Required libraries: `pandas`, `csv`. Scripts produce the validation report in the format defined in section 4.

Scripts to be developed:

| Script | Function |
|---|---|
| `validate_structure.py` | Primary key, duplicate, required field, and controlled vocabulary checks across all tables |
| `validate_foreign_keys.py` | Cross-table foreign key integrity checks |
| `validate_dates.py` | Date format, vigency, and version currency checks |
| `validate_activation.py` | Activation scale range, evidence, and consistency checks |
| `validate_csv_format.py` | Semicolon-in-field and line-break-in-field checks |
| `generate_validation_report.py` | Compiles all check outputs into the standard validation report |

---

## 8. Traceability of validation

Each validation report is saved with a timestamp. Git commit history records when validation runs were performed. Rows that are corrected following validation are noted in commit messages referencing the validation report filename and issue ID.
