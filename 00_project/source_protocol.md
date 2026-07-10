# Source Protocol — NormTrace-Political Rights

**Version:** 0.1.0-pilot
**Date:** 2026-05-18
**Status:** Current

---

## 1. Purpose

This protocol governs the identification, verification, acquisition, conversion, and metadata assignment of all legal sources added to the NormTrace-Political Rights corpus. It applies to all sources in `01_sources/` regardless of country, source type, or phase.

Every source added to the corpus must satisfy the conditions in this protocol before it is used in any analytical table.

---

## 2. Source hierarchy

Sources are ranked by reliability and preferred in the following order:

1. **Official current consolidated text** published by the issuing authority (constitutional body, legislature, electoral authority, court) or official publication organ (Diario Oficial de la Federación for Mexico; La Gaceta for Costa Rica; official OAS or UN repositories for international instruments).
2. **Official consolidated text from the official legislative database** (e.g. Cámara de Diputados portal for Mexico; Sistema Costarricense de Información Jurídica (SCIJ) or TSE normativa portal for Costa Rica; OAS treaty collection for inter-American instruments).
3. **Official jurisprudence database** of the issuing court or body (TEPJF database; SCJN SJF; TSE jurisprudence portal; CorteIDH official case database; OHCHR for UN treaty body documents).
4. **Secondary repository with attribution** — only when no official source is accessible, and only if the source is explicitly identified as a consolidated text with a specific amendment date.

Sources from categories 3 and 4 carry elevated `metadata_risk` and `vigency_risk` and must be flagged accordingly in the corpus index.

---

## 3. Source types and treatment

| Source type | Treatment |
|---|---|
| `constitutional_text` | Always use the current consolidated official version. Verify last amendment date against the official gazette. |
| `statute` | Use the current consolidated official text. Do not use individual reform decrees as the primary source for a statute. |
| `internal_regulation` | Use the current version from the issuing institution. Verify publication date in official gazette. |
| `administrative_regulation` | Use the current version from the issuing institution. Verify currency. Mark `vigency_risk: medium` or higher. |
| `decree` | Use as a supporting source only, not as the primary text of a consolidated instrument. Mark as `partial_reform_source`. |
| `international_treaty` | Use the official text from the treaty depositary (OAS or UN). Record ratification dates for Mexico and Costa Rica. |
| `judgment` | Use the official text from the court's database. Record case number, date, and operative paragraphs. |
| `advisory_opinion` | Use the official text. Clearly distinguish from binding judgments. |
| `general_comment` | Use the official UN or OAS text. Record adoption date. |
| `soft_law_standard` | Mark `legal_force: soft_law`. Do not treat as binding. Use as comparative context only. |
| `thematic_report` | Mark as IACHR or equivalent report. Extract relevant standards only; do not convert full report. |
| `jurisprudence_compilation` | Record the date range covered. Note that compilations may not include the most recent decisions. |

---

## 4. Version and vigency rules

- **Do not use draft texts.** Texts marked as drafts, proposals, or anteproyectos are not eligible for the corpus.
- **Do not use unofficial versions.** Texts downloaded from news sites, NGO publications, secondary repositories, or unofficial platforms are not eligible as primary sources unless they reproduce the official text with attribution and a specific amendment date.
- **Multiple versions of the same instrument:** If multiple versions exist (e.g. original 2009 text and a 2023 consolidated version), use only the consolidated current version as the primary corpus entry. Historical versions may be archived in `99_archive/` with clear labelling.
- **Reform decrees only:** If only a reform decree is available (not a consolidated text), record it as a `partial_reform_source` in the source discovery table and recommend locating the consolidated version before conversion. Do not treat a reform decree as the complete instrument.
- **Vigency uncertainty:** If the vigency status cannot be confirmed from the official source, record `vigency_status: unverified` in the corpus index and flag the source for verification before use.

---

## 5. Source verification checklist

Before adding any source to the corpus, confirm the following:

- [ ] Is the source official? (published by the issuing authority or official gazette)
- [ ] Is the version current? (reflects last known amendment)
- [ ] Is the date of last amendment or update available?
- [ ] Is the issuing authority identified?
- [ ] Is the legal force clear? (binding / soft law / interpretive)
- [ ] Is the source downloadable from an official URL?
- [ ] Is OCR needed? (scanned image PDF)
- [ ] Does it contain articles, paragraphs, holdings, guidelines, or annexes relevant to political participation rights?
- [ ] Is the correct target folder identified?
- [ ] Is the proposed Markdown filename stable and descriptive?
- [ ] Is the source national-level, subnational, municipal, international, or jurisprudential?
- [ ] Should it be included in phase 1 or deferred to phase 2?
- [ ] Is there already a file for the same instrument in the corpus? (avoid duplicates)

---

## 6. Folder and filename conventions

**Folder assignments:**

| Source category | Target folder |
|---|---|
| Mexican constitutional, statutory, electoral, regulatory and jurisprudential sources | `01_sources/mexico/md/` |
| Costa Rican constitutional, statutory, electoral, regulatory and jurisprudential sources | `01_sources/costa_rica/md/` |
| International and inter-American instruments, jurisprudence, and soft law | `01_sources/international_standards/md/` |
| Venice Commission, IDEA International, and other comparative references | `01_sources/comparative_soft_law/md/` |
| Municipal or subnational sources (phase 2 only) | `01_sources/{country}/municipal/md/` |

**Filename rules:**
- Lowercase only
- Underscores (no spaces, hyphens, accents, parentheses, or special characters)
- Format: `{country_or_system}_{issuing_authority_or_instrument}_{short_title}_{year}.md`
- Year refers to the year of the current consolidated version or the version date used
- Examples:
  - `mexico_constitucion_politica_cpeum_2026.md`
  - `mexico_ley_general_instituciones_procedimientos_electorales_lgipe_2024.md`
  - `mexico_tepjf_jurisprudencia_derechos_politico_electorales.md`
  - `costa_rica_constitucion_politica_1949.md`
  - `costa_rica_codigo_electoral_ley_8765_2009.md`
  - `costa_rica_tse_reglamento_referendum.md`
  - `interamerican_convencion_americana_derechos_humanos_cadh_1969.md`
  - `corteidh_jurisprudencia_derechos_politicos_art23_cadh.md`
  - `un_ccpr_observacion_general_25_art25_pidcp_1996.md`
  - `oas_carta_democratica_interamericana_2001.md`

- Do not duplicate filenames. If a source already exists, update its metadata instead of creating a new file.

---

## 7. Markdown conversion requirements

All converted Markdown files must:

- Begin with a YAML metadata block (see section 8)
- Preserve article numbers exactly as they appear in the source
- Preserve section titles, chapter headings, and structural labels
- Preserve transitory provisions
- Preserve annexes where relevant
- Preserve tables where present in the source
- For jurisprudence: preserve holdings, criteria, theses, rulings, and operative paragraphs verbatim
- For administrative guidelines: preserve formats, thresholds, procedural requirements, and timelines
- Not summarise legal content during conversion
- Not conduct substantive legal analysis during conversion

**OCR note:** If a PDF is image-only (scanned), apply OCR before conversion. Record `ocr_required: true` in the metadata. Flag the output for quality review, as OCR introduces error risk in legal text.

---

## 8. YAML metadata block

Every Markdown source file must begin with the following metadata block:

```yaml
---
source_id:
source_title:
country_or_system:
jurisdiction_level: national / subnational / international
source_type:
issuing_authority:
official_source_url:
download_url:
publication_date:
last_amendment_date:
version_date:
legal_force:
language:
download_format:
conversion_method: pdf_to_md / html_to_md / manual_transcription / ocr_then_md
ocr_required:
vigency_status:
verification_status:
phase: phase_1 / phase_2
date_added:
notes:
---
```

All fields must be populated. Where information is not available, record `null` and note why in the `notes` field.

---

## 9. Jurisprudence-specific rules

Jurisprudential sources require additional metadata and structural treatment:

- Record `case_number` or `thesis_number` in the notes or a separate metadata field
- Identify whether the source is: `jurisprudencia` (binding), `tesis relevante` (persuasive), `sentencia` (judgment), `opinion consultiva` (advisory opinion), `resolución` (resolution), `criterio` (criterion), or `general_comment`
- For IACtHR judgments: identify the paragraph numbers of the operative paragraphs (puntos resolutivos) and key holdings
- Distinguish majority holdings from concurring or dissenting opinions where analytically relevant
- Record the State Party against which the judgment was issued
- For TEPJF: record the expediente number and whether the source is jurisprudencia or tesis relevante
- For TSE Costa Rica: record the resolution number and date
- For UN HRC general comments: record the general comment number and year of adoption

---

## 10. Municipal and subnational sources

Municipal and subnational sources are phase 2 unless one of the following conditions is met:

- The municipal or subnational source is directly required to understand a national-level mechanism (e.g. a national law explicitly delegates to municipal authority with binding procedural rules)
- The source is essential to the comparative analysis for one country and cannot be replaced by a national-level source

If a municipal source is included in phase 1 under an exception, record the justification in the `notes` field of the corpus index and place the file in `01_sources/{country}/municipal/md/`.

---

## 11. No-duplicate rule

Before converting or adding any source, search the corpus index for existing entries with the same `source_id` or the same `official_source_url`. If a file for the same instrument already exists:

- Update the metadata if the version has changed
- Do not create a duplicate Markdown file
- Record the update in the Git commit message and in the source discovery table

---

## 12. Date accessed

Record the date on which the official source was accessed in the `notes` field of the corpus metadata. This is the date on which vigency was last verified from the official source. Official source URLs and access dates provide the basis for version traceability.
