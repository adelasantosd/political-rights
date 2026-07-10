# Final Download and Conversion Checklist — NormTrace-Political Rights

**Version:** 0.1.0-pilot
**Date:** 2026-05-18
**Status:** Current — to be updated as each source is acquired and converted
**Purpose:** Operational reference for downloading, converting, and registering each source in the corpus

---

## How to use this checklist

For each source entry:
1. Complete the download step — save the PDF or HTML to a staging location
2. Assess OCR need and convert accordingly
3. Apply the YAML metadata block (template in `source_protocol.md` section 8)
4. Save the Markdown file to the target folder with the proposed filename
5. Save the metadata sidecar file to the corresponding `/metadata/` folder
6. Tick each checkbox when the step is complete
7. Record the date accessed in the corpus index notes field

A source is ready for analytical extraction only when all four checkboxes are ticked.

**Manual verification flag** indicates sources that require a human legal specialist to verify the text, vigency, or content before the file can be used in analytical tables.

**Boxes:**
- [ ] DOWNLOAD — file retrieved from official URL
- [ ] CONVERT — Markdown file created with YAML metadata block
- [ ] REGISTER — entry created in `political_rights_corpus_index.csv`
- [ ] VERIFY — human legal review completed (where required)

---

## BLOCK 1 — Mexican constitutional text

### MX-01 — Constitución Política de los Estados Unidos Mexicanos (CPEUM)

**Status in corpus:** File exists — `mexico_constitution_cpeum_latest_reform_2026_04_23.md` (from DOF 2026-04-23). Verify this file is complete and not limited to health chapters. If complete: skip download and convert steps; proceed to register and verify.

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Verify existing file covers full CPEUM including Art. 35–41, 99, 115–116. If incomplete: download from Cámara de Diputados https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf | [ ] |
| CONVERT | Confirm YAML metadata block present in existing file; update if missing. Confirm filename matches convention. Proposed: `mexico_constitucion_politica_cpeum_2026.md` | [ ] |
| REGISTER | Add or update entry in `political_rights_corpus_index.csv` with `source_id: MX-CPEUM-2026`, `vigency_status: vigent`, `version_date: 2026-04-23` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Specialist to confirm that version reflects current text post-reform 2026-04-23; confirm Art. 35 fracc. I–IX text is complete | [ ] |

**Official URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf
**Proposed filename:** `mexico_constitucion_politica_cpeum_2026.md`
**Metadata filename:** `mexico_constitucion_politica_cpeum_2026_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

## BLOCK 2 — Mexican electoral legislation (P1 statutes)

### MX-02 — Ley General de Instituciones y Procedimientos Electorales (LGIPE)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf — Verify this is the post-Plan B version (reform 2022 declared unconstitutional by SCJN 2023). Confirm version date from DOF notice | [ ] |
| CONVERT | Convert PDF to Markdown. Apply YAML metadata block. Note `ocr_required` value. Record version date confirmed | [ ] |
| REGISTER | Add entry in corpus index: `source_id: MX-LGIPE-[year]`, `source_type: statute`, `vigency_status: vigent` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm which articles were invalidated by SCJN (Plan B) and whether current PDF from Cámara reflects those invalidations | [ ] |

**Official URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf
**Proposed filename:** `mexico_ley_general_instituciones_procedimientos_electorales_lgipe_2024.md` *(year to confirm after download)*
**Metadata filename:** `mexico_ley_general_instituciones_procedimientos_electorales_lgipe_2024_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-03 — Ley Federal de Consulta Popular (LCPo)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from: https://www.diputados.gob.mx/LeyesBiblio/pdf/LCPo.pdf — confirm last amendment date from DOF | [ ] |
| CONVERT | Convert PDF to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry in corpus index: `source_id: MX-LCPo-[year]`, `source_type: statute` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm thresholds (2% padrón) | Art. 19 admissibility criteria | Art. 27 INE role | Art. 35 SCJN review | [ ] |

**Official URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LCPo.pdf
**Proposed filename:** `mexico_ley_federal_consulta_popular_lcpo_2014.md` *(year to confirm)*
**Metadata filename:** `mexico_ley_federal_consulta_popular_lcpo_2014_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-04 — Ley Federal de Revocación de Mandato del Presidente (LFRMPE)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from: https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRMPE.pdf — enacted 2021 | [ ] |
| CONVERT | Convert PDF to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: MX-LFRMPE-2021` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm threshold (33% padrón | mínimo 17 entidades) | binding vs consultivo distinction | INE role | [ ] |

**Official URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRMPE.pdf
**Proposed filename:** `mexico_ley_federal_revocacion_mandato_presidente_lfrmpe_2021.md`
**Metadata filename:** `mexico_ley_federal_revocacion_mandato_presidente_lfrmpe_2021_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-05 — Ley General de Partidos Políticos (LGPP)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGPP.pdf — verify post-Plan B version | [ ] |
| CONVERT | Convert PDF to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: MX-LGPP-[year]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm articles about registro de partidos | paridad | financiamiento | candidatura requirements | [ ] |

**Official URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LGPP.pdf
**Proposed filename:** `mexico_ley_general_partidos_politicos_lgpp_2014.md` *(year to confirm)*
**Metadata filename:** `mexico_ley_general_partidos_politicos_lgpp_2014_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-06 — Ley General del Sistema de Medios de Impugnación en Materia Electoral (LGSMIME)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGSMIME.pdf | [ ] |
| CONVERT | Convert PDF to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: MX-LGSMIME-[year]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Map JDC (Arts. 79–93): procedencia | legitimación activa | plazo | efectos | relación con amparo | [ ] |

**Official URL:** https://www.diputados.gob.mx/LeyesBiblio/pdf/LGSMIME.pdf
**Proposed filename:** `mexico_ley_general_sistema_medios_impugnacion_materia_electoral_lgsmime_1996.md` *(year to confirm)*
**Metadata filename:** `mexico_ley_general_sistema_medios_impugnacion_materia_electoral_lgsmime_1996_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

## BLOCK 3 — Mexican statutes — existing PDFs to convert

### MX-07 — Ley Orgánica del Congreso General (LOCGEUM) — PDF: H_LOCGEUM-8.pdf

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | File exists at `01_sources/mexico/pdf/H_LOCGEUM-8.pdf` — skip download | [ ] |
| CONVERT | Assess OCR need. Convert to Markdown. Apply YAML metadata block. Verify Art. 130 bis (iniciativa ciudadana). Confirm version date | [ ] |
| REGISTER | Add entry: `source_id: MX-LOCGEUM-[year]`, `conversion_method: pdf_to_md`, `ocr_required: [confirm]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm Art. 130 bis text | threshold (0.13% padrón) | trámite ante Cámara | plazos | [ ] |

**Source PDF:** `01_sources/mexico/pdf/H_LOCGEUM-8.pdf`
**Official URL (for version verification):** https://www.diputados.gob.mx/LeyesBiblio/pdf/LOCGEUM.pdf
**Proposed filename:** `mexico_ley_organica_congreso_general_estados_unidos_mexicanos_locgeum_2009.md` *(year to confirm)*
**Metadata filename:** `mexico_ley_organica_congreso_general_estados_unidos_mexicanos_locgeum_2009_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-08 — Reglamento de la Cámara de Diputados — PDF: H_Reg_Diputados-4.pdf

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | File exists at `01_sources/mexico/pdf/H_Reg_Diputados-4.pdf` — skip download | [ ] |
| CONVERT | Assess OCR need. Convert to Markdown. Apply YAML metadata block. Focus on articles governing iniciativa ciudadana | [ ] |
| REGISTER | Add entry: `source_id: MX-REG-DIPUTADOS-[year]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Map articles governing iniciativa ciudadana: admisión | comisiones | plazos | archivo | [ ] |

**Source PDF:** `01_sources/mexico/pdf/H_Reg_Diputados-4.pdf`
**Official URL (for version verification):** https://www.diputados.gob.mx/LeyesBiblio/pdf/Reg_Diputados.pdf
**Proposed filename:** `mexico_reglamento_camara_diputados_2010.md` *(year to confirm)*
**Metadata filename:** `mexico_reglamento_camara_diputados_2010_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-09 — Ley de Amparo — PDF: H_LAmp.pdf

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | File exists at `01_sources/mexico/pdf/H_LAmp.pdf` — skip download | [ ] |
| CONVERT | Assess OCR need. Convert to Markdown (scoped to remedy-relevant articles only). Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: MX-LAMP-[year]`, `notes: scoped to remedy mapping — Art. 1, 5, 61 fracc. XIII (improcedencia en materia electoral)` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm Art. 61 fracc. XIII (amparo improcedente en materia electoral) | interaction with JDC | [ ] |

**Source PDF:** `01_sources/mexico/pdf/H_LAmp.pdf`
**Official URL (for version verification):** https://www.diputados.gob.mx/LeyesBiblio/pdf/LAmp.pdf
**Proposed filename:** `mexico_ley_de_amparo_lamp_2013.md` *(year to confirm)*
**Metadata filename:** `mexico_ley_de_amparo_lamp_2013_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-10 — H_219.pdf — UNIDENTIFIED

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | File exists at `01_sources/mexico/pdf/H_219.pdf` — skip download | [ ] |
| CONVERT | ⛔ DO NOT CONVERT until file is identified. Open file and record: title | date | issuing authority | nature of content | [ ] |
| REGISTER | ⛔ DO NOT REGISTER until identification complete. If irrelevant: archive to `99_archive/`. If reform decree: mark `partial_reform_source`. | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Content identification must be performed before any further action | [ ] |

**Source PDF:** `01_sources/mexico/pdf/H_219.pdf`
**Proposed filename:** UNKNOWN — to be determined after identification
**Target folder:** UNKNOWN — depends on content

---

## BLOCK 4 — Mexican administrative sources (INE)

### MX-11 — INE Acuerdo CG572/2021 — Lineamientos Consulta Popular

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access INE repositorio documental: https://repositoriodocumental.ine.mx/ — search "CG572/2021" or "consulta popular 2021". Alternatively search DOF for publication date | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block. Note: mark `vigency_status: partial` if applicable only to 2021 process | [ ] |
| REGISTER | Add entry: `source_id: MX-INE-CG572-2021`, `source_type: administrative_regulation` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm procedural requirements vs LCPo — identify if acuerdo extends or restricts the law | [ ] |

**Access URL:** https://repositoriodocumental.ine.mx/
**Proposed filename:** `mexico_ine_acuerdo_cg572_2021_lineamientos_consulta_popular.md`
**Metadata filename:** `mexico_ine_acuerdo_cg572_2021_lineamientos_consulta_popular_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-12 — INE Acuerdo CG309/2022 — Lineamientos Revocación de Mandato

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access INE repositorio documental — search "CG309/2022" or "revocación de mandato 2022" | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: MX-INE-CG309-2022` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm activation procedure vs LFRMPE — threshold (33% | 17 entidades) | plazos | [ ] |

**Access URL:** https://repositoriodocumental.ine.mx/
**Proposed filename:** `mexico_ine_acuerdo_cg309_2022_lineamientos_revocacion_mandato.md`
**Metadata filename:** `mexico_ine_acuerdo_cg309_2022_lineamientos_revocacion_mandato_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-13 — INE Lineamientos Candidaturas Independientes (vigentes)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access INE repositorio documental — search "candidaturas independientes" | "apoyo ciudadano" | confirm current acuerdo number and year (2023 or 2024) | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block. Record acuerdo number and date confirmed | [ ] |
| REGISTER | Add entry: `source_id: MX-INE-CAND-IND-[year]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm threshold (1% padrón) | plazos | modalidades de recolección | causas de inadmisibilidad | [ ] |

**Access URL:** https://repositoriodocumental.ine.mx/
**Proposed filename:** `mexico_ine_acuerdo_lineamientos_candidaturas_independientes_2024.md` *(year to confirm)*
**Metadata filename:** `mexico_ine_acuerdo_lineamientos_candidaturas_independientes_2024_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

## BLOCK 5 — Mexican jurisprudence

### MX-14 — TEPJF — Jurisprudencia y tesis sobre derechos político-electorales

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access TEPJF jurisprudencia: https://www.te.gob.mx/jurisprudencia/ — query by subject: candidaturas independientes | consulta popular | revocación | JDC | paridad | proporcionalidad. Extract binding jurisprudencia and relevant tesis | [ ] |
| CONVERT | Compile extracted jurisprudencia and tesis into structured Markdown. Apply YAML metadata block. Record date of query and case numbers | [ ] |
| REGISTER | Add entry: `source_id: MX-TEPJF-JUR-[date]`, `source_type: jurisprudence_compilation`, `date_added: [access date]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Specialist to verify holdings, operative paragraphs, and classification as jurisprudencia vs tesis relevante | [ ] |

**Access URL:** https://www.te.gob.mx/jurisprudencia/
**Proposed filename:** `mexico_tepjf_jurisprudencia_derechos_politico_electorales.md`
**Metadata filename:** `mexico_tepjf_jurisprudencia_derechos_politico_electorales_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-15 — SCJN — Tesis y jurisprudencia sobre Art. 35 CPEUM y derechos políticos

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access SJF2: https://sjf2.scjn.gob.mx/ — query by Art. 35 | Art. 41 | paridad de género (contexto electoral) | bloque de constitucionalidad en materia política. Include post-2011 (reforma Art. 1 CPEUM) and post-Plan B (2023) decisions | [ ] |
| CONVERT | Compile relevant tesis and sentencias into structured Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: MX-SCJN-JUR-[date]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Verify holdings; confirm which SCJN decisions are jurisprudencia vs aisladas | [ ] |

**Access URL:** https://sjf2.scjn.gob.mx/
**Proposed filename:** `mexico_scjn_jurisprudencia_derechos_politicos_art35_cpeum.md`
**Metadata filename:** `mexico_scjn_jurisprudencia_derechos_politicos_art35_cpeum_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

### MX-16 — SCJN — Sentencia Plan B (Acción de inconstitucionalidad — reforma electoral 2023)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access SJF2 or SCJN sentencias — search "acción de inconstitucionalidad reforma electoral Plan B 2023" | [ ] |
| CONVERT | Convert to Markdown. Focus on: invalidated articles of LGIPE and LGPP | operative paragraphs | ratio decidendi | [ ] |
| REGISTER | Add entry: `source_id: MX-SCJN-PLAN-B-2023`, `source_type: judgment` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm which articles of LGIPE and LGPP were invalidated and which were upheld | [ ] |

**Access URL:** https://sjf2.scjn.gob.mx/
**Proposed filename:** `mexico_scjn_accion_inconstitucionalidad_reforma_electoral_plan_b_2023.md`
**Metadata filename:** `mexico_scjn_accion_inconstitucionalidad_reforma_electoral_plan_b_2023_metadata.yaml`
**Target folder:** `01_sources/mexico/md/`

---

## BLOCK 6 — Costa Rica constitutional and statutory sources

### CR-01 — Constitución Política de Costa Rica (1949)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from TSE: https://www.tse.go.cr/pdf/normativa/constitucion.pdf | [ ] |
| CONVERT | Convert PDF to Markdown. Apply YAML metadata block. Verify last amendment date from La Gaceta | [ ] |
| REGISTER | Add entry: `source_id: CR-CONST-1949`, `country_or_system: costa_rica`, `source_type: constitutional_text` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Specialist to confirm Art. 93–98, 102, 105, 123 text and current amendment status | [ ] |

**Official URL:** https://www.tse.go.cr/pdf/normativa/constitucion.pdf
**Proposed filename:** `costa_rica_constitucion_politica_1949.md`
**Metadata filename:** `costa_rica_constitucion_politica_1949_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

### CR-02 — Código Electoral (Ley 8765 — 2009)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from TSE: https://www.tse.go.cr/pdf/normativa/codigoelectoral.pdf | [ ] |
| CONVERT | Convert PDF to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: CR-CODIGO-ELECTORAL-2009` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm articles on candidaturas | paridad | registro de partidos | procedimiento electoral | [ ] |

**Official URL:** https://www.tse.go.cr/pdf/normativa/codigoelectoral.pdf
**Proposed filename:** `costa_rica_codigo_electoral_ley_8765_2009.md`
**Metadata filename:** `costa_rica_codigo_electoral_ley_8765_2009_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

### CR-03 — Ley sobre Regulación del Referéndum (Ley 8492 — 2006)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from SCIJ: http://www.pgrweb.go.cr/scij/ — search Ley 8492 | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: CR-LEY-REFERENDUM-8492` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm threshold (5% padrón or Asamblea majority) | materias excluidas | TSE role | Sala IV review | binding vs consultivo | [ ] |

**Official URL:** http://www.pgrweb.go.cr/scij/
**Proposed filename:** `costa_rica_ley_regulacion_referendum_8492_2006.md`
**Metadata filename:** `costa_rica_ley_regulacion_referendum_8492_2006_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

### CR-04 — Ley de Iniciativa Popular (Ley 8491 — 2006)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from SCIJ — search Ley 8491 | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: CR-LEY-INICIATIVA-POPULAR-8491` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm threshold (5% padrón) | TSE verification procedure | Asamblea trámite | plazos | [ ] |

**Official URL:** http://www.pgrweb.go.cr/scij/
**Proposed filename:** `costa_rica_ley_iniciativa_popular_8491_2006.md`
**Metadata filename:** `costa_rica_ley_iniciativa_popular_8491_2006_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

### CR-05 — Ley Orgánica del TSE (Ley 3504)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from SCIJ — search Ley 3504 | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: CR-LEY-ORGANICA-TSE-3504` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm composition (3 magistrados propietarios + 6 suplentes) | competencias exclusivas | relación con Sala IV | [ ] |

**Official URL:** http://www.pgrweb.go.cr/scij/
**Proposed filename:** `costa_rica_ley_organica_tse_3504.md`
**Metadata filename:** `costa_rica_ley_organica_tse_3504_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

## BLOCK 7 — Costa Rica administrative and regulatory sources

### CR-06 — TSE Reglamento del Referéndum

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access TSE normativa: https://www.tse.go.cr/normativa.htm — locate reglamento del referéndum. Identify decree number and La Gaceta publication. If not found as reglamento general: record as gap | [ ] |
| CONVERT | Convert to Markdown if found. Apply YAML metadata block | [ ] |
| REGISTER | Add entry if found. If not found: add entry to `missing_sources_list.csv` with updated status | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm operational procedure vs Ley 8492 | [ ] |

**Official URL:** https://www.tse.go.cr/normativa.htm
**Proposed filename:** `costa_rica_tse_reglamento_referendum.md`
**Metadata filename:** `costa_rica_tse_reglamento_referendum_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`
**⚠ Note:** High uncertainty about existence as a standalone document. May be integrated into Ley 8492 procedural articles.

---

### CR-07 — TSE Reglamento sobre Iniciativa Ciudadana

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access TSE normativa — locate reglamento sobre iniciativa ciudadana. Identify decree number and La Gaceta publication | [ ] |
| CONVERT | Convert to Markdown if found. Apply YAML metadata block | [ ] |
| REGISTER | Add entry if found | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm verification procedure vs Ley 8491 | [ ] |

**Official URL:** https://www.tse.go.cr/normativa.htm
**Proposed filename:** `costa_rica_tse_reglamento_iniciativa_ciudadana.md`
**Metadata filename:** `costa_rica_tse_reglamento_iniciativa_ciudadana_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

### CR-08 — Reglamento de la Asamblea Legislativa

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access Asamblea Legislativa: http://www.asamblea.go.cr/ — locate reglamento de la Asamblea | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: CR-REG-ASAMBLEA-[year]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Map articles governing iniciativa popular trámite | plazos | archivo | [ ] |

**Official URL:** http://www.asamblea.go.cr/
**Proposed filename:** `costa_rica_reglamento_asamblea_legislativa.md`
**Metadata filename:** `costa_rica_reglamento_asamblea_legislativa_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

## BLOCK 8 — Costa Rica jurisprudence

### CR-09 — TSE Jurisprudencia sobre referéndum e iniciativa popular

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access TSE jurisprudencia: https://www.tse.go.cr/jurisprudencia.htm — query by "referéndum" | "iniciativa popular" | "participación ciudadana directa". Extract key resoluciones | [ ] |
| CONVERT | Compile into structured Markdown. Apply YAML metadata block. Record resolution numbers and dates | [ ] |
| REGISTER | Add entry: `source_id: CR-TSE-JUR-[date]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Verify holdings; confirm whether resoluciones are binding or interpretive | [ ] |

**Access URL:** https://www.tse.go.cr/jurisprudencia.htm
**Proposed filename:** `costa_rica_tse_jurisprudencia_referendum_iniciativa_popular.md`
**Metadata filename:** `costa_rica_tse_jurisprudencia_referendum_iniciativa_popular_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

### CR-10 — Sala IV — Votos sobre derechos políticos y referéndum

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access Nexus PJ: https://nexuspj.poder-judicial.go.cr/ — search for key votos: 2771-2003 | 17555-2014 | votos sobre paridad | votos sobre derechos políticos post-2006 | [ ] |
| CONVERT | Compile key votos into structured Markdown. Apply YAML metadata block. Record voto numbers and operative paragraphs | [ ] |
| REGISTER | Add entry: `source_id: CR-SALA4-JUR-[date]` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Verify that holdings are correctly attributed and that each voto is cited by correct number and year | [ ] |

**Access URL:** https://nexuspj.poder-judicial.go.cr/
**Proposed filename:** `costa_rica_sala_iv_jurisprudencia_derechos_politicos_referendum.md`
**Metadata filename:** `costa_rica_sala_iv_jurisprudencia_derechos_politicos_referendum_metadata.yaml`
**Target folder:** `01_sources/costa_rica/md/`

---

## BLOCK 9 — International standards (binding instruments)

### INT-01 — Convención Americana sobre Derechos Humanos (CADH)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from OAS: https://www.oas.org/dil/esp/tratados_b-32_convencion_americana_sobre_derechos_humanos.htm | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block. Record ratification dates for Mexico (1981) and Costa Rica (1970) | [ ] |
| REGISTER | Add entry: `source_id: INT-CADH-1969`, `country_or_system: international`, `source_type: international_treaty` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm Art. 23 text | Art. 32 (restrictions clause) | Art. 30 (scope of restrictions) | [ ] |

**Official URL:** https://www.oas.org/dil/esp/tratados_b-32_convencion_americana_sobre_derechos_humanos.htm
**Proposed filename:** `interamerican_convencion_americana_derechos_humanos_cadh_1969.md`
**Metadata filename:** `interamerican_convencion_americana_derechos_humanos_cadh_1969_metadata.yaml`
**Target folder:** `01_sources/international_standards/md/`

---

### INT-02 — Pacto Internacional de Derechos Civiles y Políticos (PIDCP)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from OHCHR: https://www.ohchr.org/es/ — locate Spanish version of ICCPR | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block. Record ratification dates for Mexico (1981) and Costa Rica (1969) | [ ] |
| REGISTER | Add entry: `source_id: INT-PIDCP-1966` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm Art. 25 text | Art. 19 (freedom of expression) | Art. 22 (freedom of association — relevant for party registration) | [ ] |

**Official URL:** https://www.ohchr.org/es/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights
**Proposed filename:** `un_pacto_internacional_derechos_civiles_politicos_pidcp_1966.md`
**Metadata filename:** `un_pacto_internacional_derechos_civiles_politicos_pidcp_1966_metadata.yaml`
**Target folder:** `01_sources/international_standards/md/`

---

### INT-03 — CorteIDH — Sentencias sobre Art. 23 CADH (Castañeda Gutman | Yatama | López Mendoza | Petro Urrego)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download each sentencia from CorteIDH: https://www.corteidh.or.cr/casos_sentencias.cfm — Castañeda Gutman (Serie C 184) | Yatama (Serie C 127) | López Mendoza (Serie C 233) | Petro Urrego (Serie C 360) | [ ] |
| CONVERT | Convert each to Markdown or compile into thematic Markdown. Apply YAML metadata block per case or per compilation | [ ] |
| REGISTER | Add entries: `source_id: INT-IACtHR-CASTANEDA-2008` | `INT-IACtHR-YATAMA-2005` | `INT-IACtHR-LOPEZ-MENDOZA-2011` | `INT-IACtHR-PETRO-URREGO-2020` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Verify holdings | operative paragraphs | Art. 23.2 taxativity doctrine | proportionality criteria per case | [ ] |

**Official URL:** https://www.corteidh.or.cr/casos_sentencias.cfm
**Proposed filename:** `corteidh_jurisprudencia_derechos_politicos_art23_cadh.md` *(or one file per sentencia)*
**Metadata filename:** `corteidh_jurisprudencia_derechos_politicos_art23_cadh_metadata.yaml`
**Target folder:** `01_sources/international_standards/md/`

---

### INT-04 — OG 25 — Observación General No. 25 del Comité de Derechos Humanos ONU (Art. 25 PIDCP)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from OHCHR — Spanish version. Document reference: CCPR/C/21/Rev.1/Add.7 | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block. Record paragraph numbers of key holdings | [ ] |
| REGISTER | Add entry: `source_id: INT-CCPR-OG25-1996` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Verify paragraph content; confirm §§ on universal suffrage | candidacy restrictions | direct participation | party requirements | [ ] |

**Official URL:** https://www.ohchr.org/en/documents/general-comments-and-recommendations/ccpr-general-comment-no-25-article-25-right-participate
**Proposed filename:** `un_ccpr_observacion_general_25_art25_pidcp_1996.md`
**Metadata filename:** `un_ccpr_observacion_general_25_art25_pidcp_1996_metadata.yaml`
**Target folder:** `01_sources/international_standards/md/`

---

## BLOCK 10 — Comparative soft law

### INT-05 — CorteIDH — OC-28/21 (Funciones órganos electorales | paridad de género)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from CorteIDH: https://www.corteidh.or.cr/docs/opiniones/seriea_28_esp.pdf | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block | [ ] |
| REGISTER | Add entry: `source_id: INT-IACtHR-OC28-2021`, `source_type: advisory_opinion` | [ ] |
| VERIFY | ⚑ MANUAL REVIEW REQUIRED — Confirm §§ on paridad | electoral body obligations | Art. 23 + Art. 1.1 CADH | [ ] |

**Official URL:** https://www.corteidh.or.cr/docs/opiniones/seriea_28_esp.pdf
**Proposed filename:** `corteidh_oc28_21_funciones_organos_electorales_paridad_genero.md`
**Metadata filename:** `corteidh_oc28_21_funciones_organos_electorales_paridad_genero_metadata.yaml`
**Target folder:** `01_sources/international_standards/md/`

---

### INT-06 — Venice Commission — Código de Buenas Prácticas en Materia Electoral (2002)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from Venice Commission: https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD(2002)023rev2-cor-e | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block. Mark `legal_force: soft_law` | [ ] |
| REGISTER | Add entry: `source_id: INT-VENICE-ELECTORAL-CODE-2002`, `country_or_system: comparative_soft_law` | [ ] |
| VERIFY | No specialist verification required — soft law benchmark. Document mark clearly as non-binding | [ ] |

**Official URL:** https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD(2002)023rev2-cor-e
**Proposed filename:** `venice_commission_codigo_buenas_practicas_materia_electoral_2002.md`
**Metadata filename:** `venice_commission_codigo_buenas_practicas_materia_electoral_2002_metadata.yaml`
**Target folder:** `01_sources/comparative_soft_law/md/`

---

### INT-07 — Venice Commission — Código de Buenas Prácticas en Referéndums (2008)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from Venice Commission: https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD(2008)013-e | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block. Mark `legal_force: soft_law` | [ ] |
| REGISTER | Add entry: `source_id: INT-VENICE-REFERENDUM-CODE-2008` | [ ] |
| VERIFY | No specialist verification required | [ ] |

**Official URL:** https://www.venice.coe.int/webforms/documents/?pdf=CDL-AD(2008)013-e
**Proposed filename:** `venice_commission_codigo_buenas_practicas_referendums_2008.md`
**Metadata filename:** `venice_commission_codigo_buenas_practicas_referendums_2008_metadata.yaml`
**Target folder:** `01_sources/comparative_soft_law/md/`

---

### INT-08 — Carta Democrática Interamericana (OEA — 2001)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Download from OAS — Spanish version | [ ] |
| CONVERT | Convert to Markdown. Apply YAML metadata block. Mark `legal_force: soft_law` | [ ] |
| REGISTER | Add entry: `source_id: INT-OAS-CARTA-DEMOCRATICA-2001` | [ ] |
| VERIFY | No specialist verification required | [ ] |

**Official URL:** https://www.oas.org/charter/docs_es/resolucion1_es.htm
**Proposed filename:** `oas_carta_democratica_interamericana_2001.md`
**Metadata filename:** `oas_carta_democratica_interamericana_2001_metadata.yaml`
**Target folder:** `01_sources/comparative_soft_law/md/`

---

### INT-09 — IDEA International — Direct Democracy Handbook (2008)

| Step | Description | Done |
|---|---|---|
| DOWNLOAD | Access IDEA: https://www.idea.int/publications/catalogue/direct-democracy-international-idea-handbook — download or access key chapters | [ ] |
| CONVERT | Convert relevant chapters to Markdown. Apply YAML metadata block. Mark `legal_force: soft_law` | [ ] |
| REGISTER | Add entry: `source_id: INT-IDEA-DD-HANDBOOK-2008` | [ ] |
| VERIFY | No specialist verification required — empirical reference | [ ] |

**Official URL:** https://www.idea.int/publications/catalogue/direct-democracy-international-idea-handbook
**Proposed filename:** `idea_international_direct_democracy_handbook_2008.md`
**Metadata filename:** `idea_international_direct_democracy_handbook_2008_metadata.yaml`
**Target folder:** `01_sources/comparative_soft_law/md/`

---

## Summary progress tracker

| Block | Sources | Downloaded | Converted | Registered | Verified |
|---|---|---|---|---|---|
| Block 1 — CPEUM | 1 | [ ] | [ ] | [ ] | [ ] |
| Block 2 — MX statutes (P1) | 5 | [ ] | [ ] | [ ] | [ ] |
| Block 3 — MX PDFs to convert | 4 | N/A | [ ] | [ ] | [ ] |
| Block 4 — INE admin sources | 3 | [ ] | [ ] | [ ] | [ ] |
| Block 5 — MX jurisprudence | 3 | [ ] | [ ] | [ ] | [ ] |
| Block 6 — CR statutes | 5 | [ ] | [ ] | [ ] | [ ] |
| Block 7 — CR admin sources | 3 | [ ] | [ ] | [ ] | [ ] |
| Block 8 — CR jurisprudence | 2 | [ ] | [ ] | [ ] | [ ] |
| Block 9 — International binding | 4 | [ ] | [ ] | [ ] | [ ] |
| Block 10 — Comparative soft law | 4 | [ ] | [ ] | [ ] | [ ] |
| **TOTAL** | **34** | **0/34** | **0/34** | **0/34** | **0/34** |

---

*This checklist should be updated each time a source is processed. Update the summary table counts and tick the checkboxes in each source entry. Record the date of completion in the corpus index `date_added` field and the access date in the `notes` field.*
