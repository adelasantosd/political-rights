# Data Dictionary — NormTrace-Political Rights

**Version:** 0.1.0-pilot
**Date:** 2026-05-18
**Status:** Draft — fields subject to revision as datasets are built

---

## Overview

This data dictionary describes the structure and field definitions for all tables used in NormTrace-Political Rights. All tables are stored as CSV files with semicolon delimiters. Tables in `03_tables/` are the core analytical outputs. Tables in `02_data/` hold raw and processed source data.

Field names use snake_case. Controlled vocabulary values are listed where applicable. Foreign key relationships are noted.

---

## Table 1: `political_rights_corpus_index.csv`

**Location:** `03_tables/source_discovery/political_rights_corpus_index.csv`
**Purpose:** Master registry of all sources added to the NormTrace-Political Rights corpus. Every Markdown source file must have a corresponding row in this table.
**Primary key:** `source_id`

| Field | Type | Description |
|---|---|---|
| `source_id` | string | Unique source identifier (e.g. `MX_CPEUM_2026`, `CR_CE_8765`, `INT_CADH_1969`) |
| `country_or_system` | string | `mexico` / `costa_rica` / `international` / `comparative_soft_law` |
| `source_title` | string | Official title of the legal instrument |
| `source_type` | string | See controlled vocabulary below |
| `issuing_authority` | string | Authority that issued or published the source |
| `official_source_url` | string | URL of the official source |
| `publication_date` | date | YYYY-MM-DD or YYYY |
| `last_amendment_date` | date | YYYY-MM-DD or YYYY; null if not applicable |
| `version_date` | date | Date of the version used in the corpus |
| `legal_force` | string | See controlled vocabulary below |
| `language` | string | `es` / `en` / `fr` |
| `download_format` | string | `pdf` / `html` / `xml` / `other` |
| `ocr_required` | boolean | Whether OCR was applied during conversion |
| `md_file_path` | string | Relative path to the Markdown file in `01_sources/` |
| `metadata_file_path` | string | Relative path to the YAML metadata file |
| `vigency_status` | string | `vigente` / `partially_amended` / `superseded` / `historical` / `unverified` |
| `verification_status` | string | `verified` / `pending_verification` / `flagged` |
| `phase` | string | `phase_1` / `phase_2` |
| `date_added` | date | YYYY-MM-DD |
| `notes` | string | Free text notes, flags, or uncertainty markers |

**Controlled vocabulary — source_type:** `constitutional_text` / `statute` / `internal_regulation` / `administrative_regulation` / `decree` / `international_treaty` / `advisory_opinion` / `judgment` / `resolution` / `general_comment` / `soft_law_standard` / `thematic_report` / `jurisprudence_compilation` / `unidentified`

**Controlled vocabulary — legal_force:** `binding_constitutional` / `binding_statutory` / `binding_regulatory` / `binding_treaty` / `binding_judgment` / `advisory_opinion` / `treaty_body_interpretation` / `soft_law` / `comparative_reference` / `unverified`

---

## Table 2: `political_rights_document_structure.csv`

**Location:** `03_tables/domestic_corpus/political_rights_document_structure.csv`
**Purpose:** Records the structural architecture of each legal source (titles, books, chapters, articles, transitory provisions, annexes). Used to navigate legal texts and confirm extraction completeness.
**Primary key:** `structure_id`
**Foreign keys:** `source_id` → `political_rights_corpus_index.source_id`

| Field | Type | Description |
|---|---|---|
| `structure_id` | string | Unique identifier for the structural element (e.g. `MX_CPEUM_T1_C1`) |
| `source_id` | string | FK → corpus index |
| `structural_level` | string | `titulo` / `libro` / `capitulo` / `seccion` / `articulo` / `parrafo` / `fraccion` / `inciso` / `transitory` / `annex` |
| `element_number` | string | Number or label of the element (e.g. `35`, `VIII`, `Primero Transitorio`) |
| `element_title` | string | Title of the element if present |
| `parent_element_id` | string | ID of the parent structural element (for hierarchy) |
| `page_reference` | string | Page range in source PDF for traceability |
| `notes` | string | Notes on numbering anomalies or editorial conventions |

---

## Table 3: `political_rights_domestic_provisions.csv`

**Location:** `03_tables/domestic_corpus/political_rights_domestic_provisions.csv`
**Purpose:** Verbatim or closely paraphrased extraction of domestic legal provisions relevant to political participation rights and mechanisms. Each row is one provision.
**Primary key:** `provision_id`
**Foreign keys:** `source_id` → corpus index; `mechanism_id` → mechanisms table; `actor_id` → actors table

| Field | Type | Description |
|---|---|---|
| `provision_id` | string | Unique identifier (e.g. `MX_CPEUM_A35_VIII`) |
| `source_id` | string | FK → corpus index |
| `country` | string | `mexico` / `costa_rica` |
| `article_ref` | string | Article and paragraph reference (e.g. `Art. 35, fracc. VIII`) |
| `provision_text_es` | string | Verbatim or closely paraphrased text in Spanish |
| `provision_type` | string | `right` / `mechanism` / `procedure` / `threshold` / `authority` / `remedy` / `exclusion` / `sanction` / `transitional` / `other` |
| `mechanism_id` | string | FK → mechanisms table (if provision belongs to a mechanism) |
| `actor_id` | string | FK → actors table (if provision assigns competence) |
| `last_reform_ref` | string | Reform decree reference for this provision |
| `extraction_method` | string | `ai_assisted` / `manual` |
| `review_status` | string | `preliminary` / `under_review` / `validated` |
| `notes` | string | Uncertainty flags, cross-references, editorial notes |

---

## Table 4: `political_rights_mechanisms.csv`

**Location:** `03_tables/mechanisms/political_rights_mechanisms.csv`
**Purpose:** Registry of all political participation mechanisms identified in the corpus for each country. One row per mechanism per country.
**Primary key:** `mechanism_id`
**Foreign keys:** `source_id` → corpus index

| Field | Type | Description |
|---|---|---|
| `mechanism_id` | string | Unique identifier (e.g. `MX_CONSULTA_POPULAR`, `CR_REFERENDUM`) |
| `country` | string | `mexico` / `costa_rica` |
| `mechanism_name_es` | string | Official or established name in Spanish |
| `mechanism_type` | string | See controlled vocabulary below |
| `constitutional_basis` | string | Constitutional article(s) establishing the mechanism |
| `statutory_basis` | string | Primary statute(s) governing the mechanism |
| `regulatory_basis` | string | Key implementing regulation(s) |
| `subject_matter_scope` | string | What matters can be decided or requested through the mechanism |
| `subject_matter_exclusions` | string | Explicit exclusions from scope |
| `legal_effect_type` | string | `binding` / `advisory` / `archivable_without_decision` / `conditional` / `undefined` |
| `activation_level` | integer | 0–5 (see methodology note) |
| `activation_confidence` | string | `high` / `medium` / `low` / `uncertain` |
| `activation_evidence` | string | Summary of evidence supporting the activation score |
| `review_status` | string | `preliminary` / `under_review` / `validated` |
| `notes` | string | Notes, flags, cross-country comparison pointers |

**Controlled vocabulary — mechanism_type:** `suffrage` / `candidacy_right` / `independent_candidacy` / `political_party_participation` / `referendum` / `popular_consultation` / `plebiscite` / `citizen_legislative_initiative` / `revocation_of_mandate` / `petition` / `public_hearing` / `electoral_remedy` / `constitutional_review` / `indigenous_participation` / `other`

---

## Table 5: `political_rights_activation_requirements.csv`

**Location:** `03_tables/mechanisms/political_rights_activation_requirements.csv`
**Purpose:** Each activation requirement for each mechanism, extracted from the legal text. One row per requirement per mechanism.
**Primary key:** `requirement_id`
**Foreign keys:** `mechanism_id` → mechanisms table; `provision_id` → provisions table

| Field | Type | Description |
|---|---|---|
| `requirement_id` | string | Unique identifier |
| `mechanism_id` | string | FK → mechanisms table |
| `country` | string | `mexico` / `costa_rica` |
| `requirement_component` | string | See controlled vocabulary below |
| `requirement_text` | string | Verbatim or closely paraphrased legal requirement |
| `provision_id` | string | FK → provisions table |
| `quantitative_threshold` | string | Numeric value if applicable (e.g. `2% of electoral roll`) |
| `is_defined_in_law` | boolean | Whether this component is explicitly defined in a legal text |
| `is_proportionate_per_standard` | string | `yes` / `no` / `uncertain` / `not_assessed` — whether IACtHR/HRC standards suggest the threshold is proportionate |
| `barrier_type` | string | FK → barrier typology (if this requirement generates a barrier) |
| `review_status` | string | `preliminary` / `under_review` / `validated` |
| `notes` | string | Notes and flags |

**Controlled vocabulary — requirement_component:** `eligible_initiators` / `signature_threshold` / `geographic_threshold` / `support_collection_method` / `digital_platform` / `verification_procedure` / `admissibility_criteria` / `admitting_authority` / `timeline_for_processing` / `review_or_remedy` / `legal_effect` / `implementation_duty` / `accessibility_condition` / `other`

---

## Table 6: `political_rights_actors.csv`

**Location:** `03_tables/actors/political_rights_actors.csv`
**Purpose:** Registry of all institutions and actors identified in the corpus as having roles in political participation mechanisms.
**Primary key:** `actor_id`

| Field | Type | Description |
|---|---|---|
| `actor_id` | string | Unique identifier (e.g. `MX_INE`, `CR_TSE`, `MX_TEPJF`) |
| `country` | string | `mexico` / `costa_rica` / `international` |
| `actor_name_es` | string | Official name in Spanish |
| `actor_name_en` | string | Name in English |
| `actor_type` | string | `electoral_authority` / `legislative_body` / `judicial_body` / `executive_body` / `constitutional_court` / `international_court` / `commission` / `civil_society` / `citizen_group` / `other` |
| `legal_basis` | string | Legal instrument establishing the actor |
| `constitutional_autonomy` | boolean | Whether the institution has constitutional autonomy |
| `notes` | string | Notes on institutional history, reforms, or competence scope |

---

## Table 7: `political_rights_actor_mechanism_edges.csv`

**Location:** `03_tables/actors/political_rights_actor_mechanism_edges.csv`
**Purpose:** Each actor–role–mechanism link. Records which actors play which roles in which mechanisms, with legal basis for each link.
**Primary key:** `edge_id`
**Foreign keys:** `actor_id` → actors table; `mechanism_id` → mechanisms table; `provision_id` → provisions table

| Field | Type | Description |
|---|---|---|
| `edge_id` | string | Unique identifier |
| `actor_id` | string | FK → actors table |
| `mechanism_id` | string | FK → mechanisms table |
| `country` | string | `mexico` / `costa_rica` |
| `actor_role` | string | See controlled vocabulary below |
| `competence_type` | string | `exclusive` / `shared` / `concurrent` / `delegated` / `undefined` |
| `provision_id` | string | FK → provisions table (legal basis for this role) |
| `notes` | string | Notes on role ambiguity, contested competence, or reform history |

**Controlled vocabulary — actor_role:** `initiator` / `receiver` / `verifier` / `admitting_authority` / `organiser` / `reviewer` / `implementer` / `oversight` / `support_provider` / `other`

---

## Table 8: `political_rights_international_standards.csv`

**Location:** `03_tables/international_standards/political_rights_international_standards.csv`
**Purpose:** Verbatim holdings, criteria, operative paragraphs, and interpretive standards extracted from international and inter-American instruments and jurisprudence. Each row is one standard or holding.
**Primary key:** `standard_id`
**Foreign keys:** `source_id` → corpus index

| Field | Type | Description |
|---|---|---|
| `standard_id` | string | Unique identifier (e.g. `INT_CADH_A23_P1`, `IAC_CASTANEDA_H1`) |
| `source_id` | string | FK → corpus index |
| `instrument_or_case` | string | Name of treaty, case, or document |
| `court_or_body` | string | IACtHR / HRC / IACHR / OAS / other |
| `article_or_paragraph_ref` | string | Article, paragraph, or case paragraph reference |
| `standard_text` | string | Verbatim holding, criterion, or standard |
| `participation_issue` | string | See controlled vocabulary below |
| `legal_force` | string | From corpus index controlled vocabulary |
| `country_involved` | string | Country against which judgment was issued (if applicable) |
| `date` | string | Date of instrument, judgment, or general comment |
| `notes` | string | Notes on interpretation, scope, or inter-case relationships |

**Controlled vocabulary — participation_issue:** `right_to_vote` / `right_to_be_elected` / `access_to_public_office` / `political_party_access` / `independent_candidacy` / `restriction_permissibility` / `proportionality_of_restriction` / `effective_remedy` / `non_discrimination` / `indigenous_participation` / `parity` / `direct_democracy` / `referendum_right` / `disqualification_or_suspension` / `other`

---

## Table 9: `political_rights_activation_standards.csv`

**Location:** `03_tables/activation_mapping/political_rights_activation_standards.csv`
**Purpose:** Maps each international or inter-American standard to the relevant domestic mechanism and activation requirement, recording correspondence, partial correspondence, or divergence.
**Primary key:** `activation_standard_id`
**Foreign keys:** `standard_id` → international standards table; `mechanism_id` → mechanisms table; `requirement_id` → activation requirements table

| Field | Type | Description |
|---|---|---|
| `activation_standard_id` | string | Unique identifier |
| `standard_id` | string | FK → international standards table |
| `country` | string | `mexico` / `costa_rica` |
| `mechanism_id` | string | FK → mechanisms table |
| `requirement_id` | string | FK → activation requirements table (if specific requirement is mapped) |
| `correspondence_type` | string | `meets_standard` / `partial_correspondence` / `divergence` / `silence` / `uncertain` |
| `correspondence_notes` | string | Description of how domestic law corresponds or diverges from the standard |
| `review_status` | string | `preliminary` / `under_review` / `validated` |

---

## Table 10: `political_rights_mapping.csv`

**Location:** `03_tables/activation_mapping/political_rights_mapping.csv`
**Purpose:** The core analytical mapping table. Each row links an international standard to a domestic mechanism, activation score, and barrier profile for one country. This is the primary output of the activation analysis.
**Primary key:** `mapping_id`
**Foreign keys:** `standard_id` → international standards table; `mechanism_id` → mechanisms table; `provision_id` → provisions table; `actor_id` → actors table

| Field | Type | Description |
|---|---|---|
| `mapping_id` | string | Unique identifier |
| `standard_id` | string | FK → international standards table |
| `country` | string | `mexico` / `costa_rica` |
| `mechanism_id` | string | FK → mechanisms table |
| `provision_id` | string | FK → provisions table (primary domestic anchor) |
| `actor_id` | string | FK → actors table (primary responsible actor) |
| `activation_level` | integer | 0–5 |
| `activation_confidence` | string | `high` / `medium` / `low` / `uncertain` |
| `activation_evidence` | string | Summary of evidence supporting the score |
| `barrier_ids` | string | Pipe-separated list of barrier IDs from barrier typology table |
| `correspondence_type` | string | From activation_standards controlled vocabulary |
| `analyst` | string | Initials or ID of analyst |
| `date_analysed` | date | YYYY-MM-DD |
| `review_status` | string | `preliminary` / `under_review` / `validated` |
| `reviewer` | string | Initials or ID of reviewer |
| `review_date` | date | YYYY-MM-DD |
| `notes` | string | Analytical notes, uncertainty flags, cross-references |

---

## Table 11: `political_rights_barrier_typology.csv`

**Location:** `03_tables/barriers/political_rights_barrier_typology.csv`
**Purpose:** Detailed record of each legal-institutional barrier identified for each mechanism and activation requirement. Each row is one barrier instance.
**Primary key:** `barrier_id`
**Foreign keys:** `mechanism_id` → mechanisms table; `requirement_id` → activation requirements table; `provision_id` → provisions table

| Field | Type | Description |
|---|---|---|
| `barrier_id` | string | Unique identifier |
| `country` | string | `mexico` / `costa_rica` |
| `mechanism_id` | string | FK → mechanisms table |
| `requirement_id` | string | FK → activation requirements table |
| `barrier_type` | string | From methodology note barrier typology controlled vocabulary |
| `barrier_description` | string | Description of the specific barrier in this mechanism |
| `provision_id` | string | FK → provisions table (provision generating or failing to address the barrier) |
| `legal_text_excerpt` | string | Verbatim or paraphrased text creating or evidencing the barrier |
| `international_standard_reference` | string | Standard against which this constitutes a barrier (if applicable) |
| `severity_assessment` | string | `critical` / `moderate` / `minor` / `uncertain` — preliminary assessment |
| `review_status` | string | `preliminary` / `under_review` / `validated` |
| `notes` | string | Notes and flags |

---

## Table 12: `political_rights_comparative_mechanism_matrix.csv`

**Location:** `03_tables/comparative/political_rights_comparative_mechanism_matrix.csv`
**Purpose:** Side-by-side comparison of equivalent or analogous mechanisms in Mexico and Costa Rica, with activation levels, barrier profiles, and structural design differences.
**Primary key:** `comparison_id`
**Foreign keys:** `mechanism_id_mexico` → mechanisms table; `mechanism_id_costa_rica` → mechanisms table

| Field | Type | Description |
|---|---|---|
| `comparison_id` | string | Unique identifier |
| `mechanism_type` | string | From mechanism type controlled vocabulary |
| `mechanism_id_mexico` | string | FK → mechanisms table (Mexico) or `absent` |
| `mechanism_id_costa_rica` | string | FK → mechanisms table (Costa Rica) or `absent` |
| `activation_level_mexico` | integer | 0–5 or null if absent |
| `activation_level_costa_rica` | integer | 0–5 or null if absent |
| `constitutional_basis_mx` | string | Constitutional provision in Mexico |
| `constitutional_basis_cr` | string | Constitutional provision in Costa Rica |
| `threshold_mx` | string | Activation threshold in Mexico |
| `threshold_cr` | string | Activation threshold in Costa Rica |
| `legal_effect_mx` | string | Legal effect type in Mexico |
| `legal_effect_cr` | string | Legal effect type in Costa Rica |
| `key_design_differences` | string | Summary of structural design differences |
| `common_barriers` | string | Pipe-separated list of barrier types present in both countries |
| `divergent_barriers` | string | Pipe-separated list of barrier types present in one country only |
| `applicable_standard` | string | Primary applicable international standard |
| `review_status` | string | `preliminary` / `under_review` / `validated` |
| `notes` | string | Analytical notes |

---

## Table 13: `political_rights_network_nodes.csv`

**Location:** `03_tables/network_analysis/political_rights_network_nodes.csv`
**Purpose:** Node registry for network analysis of institutional relationships in political participation mechanisms. Nodes are actors, mechanisms, standards, and provisions.
**Primary key:** `node_id`

| Field | Type | Description |
|---|---|---|
| `node_id` | string | Unique node identifier |
| `node_type` | string | `actor` / `mechanism` / `standard` / `provision` / `barrier` |
| `node_label` | string | Display label |
| `country` | string | `mexico` / `costa_rica` / `international` |
| `source_table` | string | Table from which the node originates |
| `source_row_id` | string | Primary key value from the source table |
| `notes` | string | Notes |

---

## Table 14: `political_rights_network_edges.csv`

**Location:** `03_tables/network_analysis/political_rights_network_edges.csv`
**Purpose:** Edge registry for network analysis. Edges represent relationships between nodes.
**Primary key:** `edge_id`
**Foreign keys:** `source_node_id`, `target_node_id` → network nodes table

| Field | Type | Description |
|---|---|---|
| `edge_id` | string | Unique edge identifier |
| `source_node_id` | string | FK → network nodes table |
| `target_node_id` | string | FK → network nodes table |
| `edge_type` | string | `actor_role` / `standard_maps_to_mechanism` / `provision_anchors_requirement` / `barrier_blocks_requirement` / `mechanism_has_remedy` / `other` |
| `weight` | float | Optional weight for network analysis |
| `notes` | string | Notes |

---

## Table 15: `source_discovery_table.csv`

**Location:** `03_tables/source_discovery/source_discovery_table.csv`
**Purpose:** Tracks the corpus acquisition process. Records all sources identified for potential inclusion, their acquisition status, and recommended actions. Feeds the corpus index as sources are verified and added.
**Primary key:** `priority_id`

| Field | Type | Description |
|---|---|---|
| `priority_id` | string | Unique identifier (e.g. `MX-01`, `CR-01`, `INT-01`) |
| `country_or_system` | string | `mexico` / `costa_rica` / `international` / `comparative_soft_law` |
| `source_id` | string | Anticipated corpus source ID |
| `source_title` | string | Title of the source |
| `source_type` | string | From corpus index controlled vocabulary |
| `official_source_url` | string | Official URL |
| `priority_level` | string | `P1` / `P2` / `P3` |
| `reason_for_priority` | string | Why this source is needed for the corpus |
| `mechanisms_or_rights_covered` | string | Pipe-separated list of mechanisms |
| `expected_tables_to_feed` | string | Pipe-separated list of target tables |
| `download_format` | string | `pdf` / `html` / `xml` / `other` |
| `conversion_complexity` | string | `low` / `medium` / `high` / `very_high` |
| `metadata_risk` | string | `low` / `medium` / `high` |
| `vigency_risk` | string | `low` / `medium` / `high` |
| `recommended_next_action` | string | Specific action required |
| `target_folder` | string | Target folder in repository |
| `proposed_md_filename` | string | Proposed Markdown filename |
| `acquisition_status` | string | `pending` / `downloaded` / `converted` / `verified` / `added_to_corpus` / `deferred` |
| `notes` | string | Notes and flags |

---

## Table 16: `jurisprudence_discovery_table.csv`

**Location:** `03_tables/source_discovery/jurisprudence_discovery_table.csv`
**Purpose:** Tracks jurisprudential sources identified for the inter-American, domestic electoral, and constitutional court layers. Separate from the general source discovery table to allow jurisprudence-specific fields.
**Primary key:** `jurisprudence_source_id`

| Field | Type | Description |
|---|---|---|
| `jurisprudence_source_id` | string | Unique identifier (e.g. `IAC_CASTANEDA_2008`) |
| `system` | string | `inter_american` / `mexico_tepjf` / `mexico_scjn` / `costa_rica_tse` / `costa_rica_sala_iv` / `un_hrc` / `other` |
| `case_or_document_title` | string | Full case name or document title |
| `court_or_body` | string | Court or body that issued the decision |
| `country_involved` | string | Country against which the decision was issued |
| `date` | string | Date of decision or adoption |
| `instrument_interpreted` | string | Treaty, constitutional provision, or legal instrument interpreted |
| `article_or_right` | string | Specific article or right addressed |
| `standard_short` | string | Short statement of the key standard or holding |
| `participation_issue` | string | From international standards controlled vocabulary |
| `legal_force` | string | From corpus index controlled vocabulary |
| `official_url` | string | URL of the official source |
| `paragraphs_to_review` | string | Key paragraph numbers for extraction |
| `relevance_for_normtrace` | string | Summary of relevance for the analytical tables |
| `relevance_for_mexico` | string | Specific relevance for Mexico analysis |
| `relevance_for_costa_rica` | string | Specific relevance for Costa Rica analysis |
| `requires_full_text_download` | boolean | Whether full text is needed |
| `requires_manual_legal_review` | boolean | Whether human expert review is required for this source |
| `acquisition_status` | string | `pending` / `downloaded` / `converted` / `verified` / `added_to_corpus` / `deferred` |
| `notes` | string | Notes |

---

## Controlled vocabulary cross-reference

The following controlled vocabulary items are shared across multiple tables and must be applied consistently:

**`review_status`:** `preliminary` / `under_review` / `validated`

**`country`:** `mexico` / `costa_rica` / `international` / `comparative_soft_law`

**`source_type`:** `constitutional_text` / `statute` / `internal_regulation` / `administrative_regulation` / `decree` / `international_treaty` / `advisory_opinion` / `judgment` / `resolution` / `general_comment` / `soft_law_standard` / `thematic_report` / `jurisprudence_compilation` / `unidentified`

**`legal_force`:** `binding_constitutional` / `binding_statutory` / `binding_regulatory` / `binding_treaty` / `binding_judgment` / `advisory_opinion` / `treaty_body_interpretation` / `soft_law` / `comparative_reference` / `unverified`

**`activation_level`:** integer 0–5

**`activation_confidence`:** `high` / `medium` / `low` / `uncertain`

**`phase`:** `phase_1` / `phase_2`
