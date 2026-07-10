# Source Verification Checklist — NormTrace-Political Rights

**Version:** 0.1.0-pilot
**Date:** 2026-05-18
**Status:** Current — for use before any source is added to the corpus
**Applies to:** All sources in priority_corpus_list.csv and missing_sources_list.csv

---

## How to use this checklist

For each source, run all 13 checks before adding the source to the corpus. Record the result of each check as:
- `YES` — check passes
- `NO` — check fails (document the issue in the notes column)
- `N/A` — check does not apply to this source type (explain why)
- `?` — check cannot be confirmed yet (flag for follow-up)

A source may be added to the corpus only when all applicable checks pass (YES or N/A). Sources with failing or unresolved checks must be flagged with `vigency_status: unverified` or `verification_status: pending_verification` in the corpus index until resolved.

---

## The 13 checks

| # | Check | Notes |
|---|---|---|
| 1 | **Official source** — Is the source published by the issuing authority or official publication organ? | Official gazette (DOF / La Gaceta), issuing court, treaty depositary (OAS, UN), or official legislative database (Cámara de Diputados, SCIJ, TSE normativa) |
| 2 | **Current version** — Does the source reflect the most recent amendment in force? | Compare against last reform notice in official gazette or official consolidated version header |
| 3 | **Last amendment date available** — Is the date of the last amendment or update recorded? | Must be populated in the YAML metadata block; if unavailable, record `null` with explanation in notes |
| 4 | **Issuing authority identified** — Is the issuing body named and verifiable? | Legislature, constitutional body, electoral authority, court, or treaty depositary |
| 5 | **Legal force clear** — Is the binding status of the source explicit? | Classify as: constitutional, statutory, regulatory, administrative, soft_law, interpretive, advisory |
| 6 | **Downloadable from official URL** — Can the source be downloaded from an official URL listed in the source protocol? | Record the exact official_source_url and download_url; if access requires registration, note this |
| 7 | **OCR required** — Has it been determined whether the PDF is image-only (scanned) or text-based? | Scanned PDFs require OCR before conversion; record `ocr_required: true` in metadata and flag for quality review |
| 8 | **Relevant content confirmed** — Does the source contain articles, paragraphs, holdings, guidelines, or annexes relevant to political participation rights? | Minimum relevance: source must address at least one mechanism or right in scope (vote, be_voted, candidatura_independiente, consulta_popular, revocacion_mandato, iniciativa_ciudadana, referendum, partido_politico_registration) |
| 9 | **Human review required** — Has it been determined whether the source requires substantive legal review before extraction? | All constitutional texts, high-court judgments, and activation-level determinations require human legal review; record in corpus index |
| 10 | **Target folder identified** — Is the correct target folder for the converted Markdown file confirmed? | See source protocol section 6; confirm the folder exists in the repository |
| 11 | **Proposed filename stable and descriptive** — Is the proposed Markdown filename confirmed against the naming convention? | Format: `{country_or_system}_{issuing_authority_or_instrument}_{short_title}_{year}.md`; all lowercase, underscores only, no accents |
| 12 | **Jurisdiction level confirmed** — Has the source been classified as national, subnational, international, or jurisprudential? | Determines folder path and corpus index field; municipal sources are phase 2 unless exception applies |
| 13 | **Phase assignment confirmed** — Has it been determined whether this source is included in phase 1 or deferred to phase 2? | Phase 1: essential for mechanism mapping, activation level coding, and international standard comparison. Phase 2: comparative soft law, secondary jurisprudence, municipal sources |

---

## BLOCK 1 — Mexican constitutional and electoral legislation

### MX-01 — Constitución Política de los Estados Unidos Mexicanos (CPEUM)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | YES | DOF — text in corpus from 23-04-2026 |
| 2 | Current version | ? | Verify DOF 23-04-2026 is latest reform; check for any reform after that date |
| 3 | Last amendment date | YES | 2026-04-23 — present in corpus file header |
| 4 | Issuing authority | YES | Congreso de la Unión / DOF |
| 5 | Legal force | YES | Constitutional |
| 6 | Downloadable from official URL | YES | DOF / Cámara de Diputados |
| 7 | OCR required | ? | Verify existing file — determine if it is text-based or image PDF |
| 8 | Relevant content | YES | Art. 35 (derechos políticos), Art. 41 (partidos, paridad), Art. 99 (TEPJF), Art. 115–116 (federalism) |
| 9 | Human review required | YES | Constitutional text — all activation-level extractions require human legal review |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | ? | Confirm existing filename against naming convention; update if needed |
| 12 | Jurisdiction level | YES | National — constitutional |
| 13 | Phase | YES | Phase 1 |

---

### MX-02 — Ley General de Instituciones y Procedimientos Electorales (LGIPE)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file in corpus — must download from Cámara de Diputados: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf |
| 2 | Current version | ? | Verify post-Plan B version (reform declared unconstitutional by SCJN 2023); check current consolidated version date |
| 3 | Last amendment date | ? | Must confirm from DOF after download |
| 4 | Issuing authority | YES | Congreso de la Unión |
| 5 | Legal force | YES | Statutory — electoral general law |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf |
| 7 | OCR required | ? | Must assess PDF after download |
| 8 | Relevant content | YES | Central electoral law — activation of vote, be_voted, candidatura_independiente, registro_partido |
| 9 | Human review required | YES | Statutory text — extraction of activation requirements requires human verification |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Not yet assigned — proposed: `mexico_ley_general_instituciones_procedimientos_electorales_lgipe_2024.md` (year to confirm after download) |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-03 — Ley Federal de Consulta Popular (LCPo)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file in corpus — must download from Cámara: https://www.diputados.gob.mx/LeyesBiblio/pdf/LCPo.pdf |
| 2 | Current version | ? | Verify current consolidated version |
| 3 | Last amendment date | ? | Must confirm after download |
| 4 | Issuing authority | YES | Congreso de la Unión |
| 5 | Legal force | YES | Statutory |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/LCPo.pdf |
| 7 | OCR required | ? | Must assess PDF after download |
| 8 | Relevant content | YES | Mechanism: consulta_popular — threshold (2% padrón), activation procedure, INE role, SCJN review |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ley_federal_consulta_popular_lcpo_2014.md` (year to confirm) |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-04 — Ley Federal de Revocación de Mandato del Presidente (LFRMPE)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file in corpus — download: https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRMPE.pdf |
| 2 | Current version | ? | Enacted 2021; verify current text |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Congreso de la Unión |
| 5 | Legal force | YES | Statutory |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/LFRMPE.pdf |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Mechanism: revocacion_mandato — threshold (33% padrón), INE role, binding vs consultivo |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ley_federal_revocacion_mandato_presidente_lfrmpe_2021.md` |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-05 — Ley General de Partidos Políticos (LGPP)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGPP.pdf |
| 2 | Current version | ? | Verify post-Plan B version |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Congreso de la Unión |
| 5 | Legal force | YES | Statutory |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/LGPP.pdf |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | registro_partido, financiamiento, paridad, candidatura requirements |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ley_general_partidos_politicos_lgpp_2014.md` (year to confirm) |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-06 — Ley General del Sistema de Medios de Impugnación en Materia Electoral (LGSMIME)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download: https://www.diputados.gob.mx/LeyesBiblio/pdf/LGSMIME.pdf |
| 2 | Current version | ? | Must confirm |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Congreso de la Unión |
| 5 | Legal force | YES | Statutory |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/LGSMIME.pdf |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | JDC (juicio para protección de derechos político-electorales) — primary individual remedy |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ley_general_sistema_medios_impugnacion_materia_electoral_lgsmime_1996.md` (year to confirm) |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-07 — Ley Orgánica del Congreso General (LOCGEUM)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | YES | H_LOCGEUM-8.pdf exists in corpus |
| 2 | Current version | ? | Verify current amendment date against DOF |
| 3 | Last amendment date | ? | Must read metadata from H_LOCGEUM-8.pdf or Cámara de Diputados portal |
| 4 | Issuing authority | YES | Congreso de la Unión |
| 5 | Legal force | YES | Statutory (organic law) |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/LOCGEUM.pdf |
| 7 | OCR required | ? | Assess H_LOCGEUM-8.pdf — may require OCR if scanned |
| 8 | Relevant content | YES | Iniciativa ciudadana procedure in Congress; Art. 130 and related |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ley_organica_congreso_general_estados_unidos_mexicanos_locgeum_2009.md` (year to confirm) |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-08 — Reglamento de la Cámara de Diputados

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | YES | H_Reg_Diputados-4.pdf exists in corpus |
| 2 | Current version | ? | Verify current version against Cámara de Diputados portal |
| 3 | Last amendment date | ? | Must read from PDF or portal |
| 4 | Issuing authority | YES | Cámara de Diputados |
| 5 | Legal force | YES | Internal regulation |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/Reg_Diputados.pdf |
| 7 | OCR required | ? | Assess H_Reg_Diputados-4.pdf |
| 8 | Relevant content | YES | Iniciativa ciudadana — trámite en Cámara de Diputados; comisiones; procedimiento legislativo |
| 9 | Human review required | YES | Regulatory text — review extraction of procedural rules |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_reglamento_camara_diputados_2010.md` (year to confirm) |
| 12 | Jurisdiction level | YES | National — internal regulation |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-09 — Ley de Amparo (LAmp)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | YES | H_LAmp.pdf exists in corpus |
| 2 | Current version | ? | Verify current version — last known major reform 2013 |
| 3 | Last amendment date | ? | Must read from PDF |
| 4 | Issuing authority | YES | Congreso de la Unión |
| 5 | Legal force | YES | Statutory |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/LAmp.pdf |
| 7 | OCR required | ? | Assess H_LAmp.pdf |
| 8 | Relevant content | YES | Amparo as constitutional remedy for political rights violations (limited — courts have historically rejected amparo for electoral matters; JDC is preferred) |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ley_de_amparo_lamp_2013.md` (year to confirm) |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 (scoped) — P1 for remedy mapping only |

---

### MX-10 — H_219.pdf (unidentified)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | UNKNOWN — file exists in corpus but content unidentified |
| 2 | Current version | ? | UNKNOWN |
| 3 | Last amendment date | ? | UNKNOWN |
| 4 | Issuing authority | ? | UNKNOWN — must open file to determine |
| 5 | Legal force | ? | UNKNOWN |
| 6 | Downloadable from official URL | ? | UNKNOWN |
| 7 | OCR required | ? | Must open file to assess |
| 8 | Relevant content | ? | UNKNOWN — must read content to assess relevance |
| 9 | Human review required | YES | Required before any corpus decision |
| 10 | Target folder | ? | Depends on content identification |
| 11 | Proposed filename | NO | Cannot propose until file is identified |
| 12 | Jurisdiction level | ? | UNKNOWN |
| 13 | Phase | ? | UNKNOWN |

**⚠ ACTION REQUIRED:** Open H_219.pdf and read to identify title, date, issuing authority, and content. If it is a reform decree: mark `partial_reform_source`. If it is an irrelevant source: archive to `99_archive/`. Do not convert until all checks pass.

---

## BLOCK 2 — Mexican administrative and regulatory sources

### MX-11 — INE — Lineamientos para la consulta popular (Acuerdo INE/CG572/2021)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — locate in INE repositorio documental: https://repositoriodocumental.ine.mx/ and/or DOF |
| 2 | Current version | ? | 2021 lineamientos — verify no superseding acuerdo exists |
| 3 | Last amendment date | ? | Must check INE repository and DOF |
| 4 | Issuing authority | YES | INE — Consejo General |
| 5 | Legal force | YES | Administrative regulation — secondary to LCPo |
| 6 | Downloadable from official URL | ? | Must locate in INE repository; search for CG572/2021 |
| 7 | OCR required | ? | Must assess after download |
| 8 | Relevant content | YES | Consulta popular — recolección de firmas, verificación, admisibilidad |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ine_acuerdo_cg572_2021_lineamientos_consulta_popular.md` |
| 12 | Jurisdiction level | YES | National — administrative regulation |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-12 — INE — Lineamientos para la revocación de mandato (Acuerdo INE/CG309/2022)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — locate in INE repositorio documental |
| 2 | Current version | ? | 2022 acuerdo — verify |
| 3 | Last amendment date | ? | Must check |
| 4 | Issuing authority | YES | INE — Consejo General |
| 5 | Legal force | YES | Administrative regulation |
| 6 | Downloadable from official URL | ? | Must locate in INE repository; search CG309/2022 |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Revocación de mandato — procedimiento operativo de activación |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ine_acuerdo_cg309_2022_lineamientos_revocacion_mandato.md` |
| 12 | Jurisdiction level | YES | National — administrative regulation |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-13 — INE — Lineamientos para registro de candidaturas independientes (vigentes)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — must locate current acuerdo in INE repository |
| 2 | Current version | ? | Determine whether 2023 or 2024 version is current; check for reform post-2023 |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | INE — Consejo General |
| 5 | Legal force | YES | Administrative regulation — secondary to LGIPE |
| 6 | Downloadable from official URL | ? | Must locate exact acuerdo number in INE repository |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Candidatura independiente — apoyo ciudadano, requisitos de registro |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ine_acuerdo_lineamientos_candidaturas_independientes_2024.md` (year to confirm) |
| 12 | Jurisdiction level | YES | National — administrative regulation |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-14 — INE — Reglamento Interior del INE

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — locate in INE normativa portal or DOF |
| 2 | Current version | ? | Verify current version |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | INE — Consejo General |
| 5 | Legal force | YES | Internal administrative regulation |
| 6 | Downloadable from official URL | ? | INE normativa portal or DOF |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | INE institutional structure — relevant for actor mapping |
| 9 | Human review required | NO | Institutional structure only — low analytical complexity |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ine_reglamento_interior_2016.md` (year to confirm) |
| 12 | Jurisdiction level | YES | National — internal regulation |
| 13 | Phase | YES | Phase 1 (actor mapping) — P2 for detailed analysis |

---

### MX-15 — Ley General en Materia de Delitos Electorales (LGMDE)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from Cámara |
| 2 | Current version | ? | Must confirm |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Congreso de la Unión |
| 5 | Legal force | YES | Statutory |
| 6 | Downloadable from official URL | YES | https://www.diputados.gob.mx/LeyesBiblio/pdf/LGMDE.pdf |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Electoral offences — criminal barriers to political participation |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_ley_general_materia_delitos_electorales_lgmde_2014.md` |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 (barrier mapping) |

---

## BLOCK 3 — Mexican jurisprudence

### MX-16 — TEPJF — Jurisprudencia y tesis sobre derechos político-electorales

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — access via TEPJF database: https://www.te.gob.mx/jurisprudencia/ |
| 2 | Current version | ? | Dynamic database — record access date and scope of query |
| 3 | Last amendment date | N/A | Ongoing database; record date range of compilation |
| 4 | Issuing authority | YES | Tribunal Electoral del Poder Judicial de la Federación (TEPJF) |
| 5 | Legal force | YES | Jurisprudencia: binding. Tesis relevante: persuasive |
| 6 | Downloadable from official URL | YES | TEPJF jurisprudencia portal — must extract by subject (candidaturas independientes, consulta popular, revocación, JDC, paridad) |
| 7 | OCR required | N/A | Database text — digital extraction |
| 8 | Relevant content | YES | Activation standards, proportionality analysis, JDC criteria |
| 9 | Human review required | YES | Holdings must be verified by legal specialist |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_tepjf_jurisprudencia_derechos_politico_electorales.md` |
| 12 | Jurisdiction level | YES | National — federal electoral jurisdiction |
| 13 | Phase | YES | Phase 1 — P1 |

---

### MX-17 — SCJN — Tesis jurisprudenciales sobre Art. 35 CPEUM y derechos político-electorales

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — access via SJF2: https://sjf2.scjn.gob.mx/ |
| 2 | Current version | ? | Dynamic database; record access date and query scope |
| 3 | Last amendment date | N/A | Ongoing; record date range |
| 4 | Issuing authority | YES | Suprema Corte de Justicia de la Nación (SCJN) |
| 5 | Legal force | YES | Jurisprudencia: binding. Tesis relevante: persuasive |
| 6 | Downloadable from official URL | YES | https://sjf2.scjn.gob.mx/ — search Art. 35, Art. 41, paridad de género |
| 7 | OCR required | N/A | Digital text |
| 8 | Relevant content | YES | Constitutional interpretation of political rights — includes post-Plan B decisions |
| 9 | Human review required | YES | Holdings require specialist verification |
| 10 | Target folder | YES | `01_sources/mexico/md/` |
| 11 | Proposed filename | NO | Proposed: `mexico_scjn_jurisprudencia_derechos_politicos_art35_cpeum.md` |
| 12 | Jurisdiction level | YES | National — constitutional jurisdiction |
| 13 | Phase | YES | Phase 1 — P2 (follows TEPJF) |

---

## BLOCK 4 — Costa Rica constitutional and electoral legislation

### CR-01 — Constitución Política de Costa Rica (1949)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from TSE: https://www.tse.go.cr/pdf/normativa/constitucion.pdf |
| 2 | Current version | ? | Verify last reform date — Costa Rica corpus is completely empty |
| 3 | Last amendment date | ? | Must confirm from TSE or La Gaceta |
| 4 | Issuing authority | YES | Asamblea Legislativa / official publication: La Gaceta |
| 5 | Legal force | YES | Constitutional |
| 6 | Downloadable from official URL | YES | https://www.tse.go.cr/pdf/normativa/constitucion.pdf |
| 7 | OCR required | ? | Must assess PDF |
| 8 | Relevant content | YES | Art. 93–98 (sufragio, elecciones), Art. 102 (TSE competencias), Art. 105 (referéndum), Art. 9 (participación directa) |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_constitucion_politica_1949.md` |
| 12 | Jurisdiction level | YES | National — constitutional |
| 13 | Phase | YES | Phase 1 — P1 |

---

### CR-02 — Código Electoral (Ley 8765 — 2009)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from TSE: https://www.tse.go.cr/pdf/normativa/codigoelectoral.pdf |
| 2 | Current version | ? | Must verify current consolidated version; check for post-2009 amendments |
| 3 | Last amendment date | ? | Must confirm from TSE |
| 4 | Issuing authority | YES | Asamblea Legislativa |
| 5 | Legal force | YES | Statutory — central electoral code |
| 6 | Downloadable from official URL | YES | https://www.tse.go.cr/pdf/normativa/codigoelectoral.pdf |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | All electoral mechanisms — vote, candidatura, partidos, paridad |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_codigo_electoral_ley_8765_2009.md` |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### CR-03 — Ley sobre Regulación del Referéndum (Ley 8492 — 2006)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from SCIJ (PGR): http://www.pgrweb.go.cr/scij/ |
| 2 | Current version | ? | Must verify current consolidated version |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Asamblea Legislativa |
| 5 | Legal force | YES | Statutory |
| 6 | Downloadable from official URL | YES | SCIJ — Sistema Costarricense de Información Jurídica |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Referéndum mechanism — activation procedure, thresholds, TSE role |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_ley_regulacion_referendum_8492_2006.md` |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### CR-04 — Ley de Iniciativa Popular (Ley 8491 — 2006)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from SCIJ |
| 2 | Current version | ? | Must verify |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Asamblea Legislativa |
| 5 | Legal force | YES | Statutory |
| 6 | Downloadable from official URL | YES | SCIJ |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Iniciativa popular — activation procedure, threshold (5% of padrón), TSE role |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_ley_iniciativa_popular_8491_2006.md` |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

### CR-05 — Ley Orgánica del TSE (Ley 3504)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from SCIJ |
| 2 | Current version | ? | Must verify consolidated version |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Asamblea Legislativa |
| 5 | Legal force | YES | Statutory (organic law) |
| 6 | Downloadable from official URL | YES | SCIJ |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | TSE institutional structure, competencias, composition — central for actor mapping |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_ley_organica_tse_3504.md` |
| 12 | Jurisdiction level | YES | National — statutory |
| 13 | Phase | YES | Phase 1 — P1 |

---

## BLOCK 5 — Costa Rica administrative and regulatory sources

### CR-06 — TSE — Reglamento del Referéndum

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — locate in TSE normativa: https://www.tse.go.cr/normativa.htm |
| 2 | Current version | ? | Must locate current decree number and verify against La Gaceta |
| 3 | Last amendment date | ? | Must confirm from TSE normativa portal |
| 4 | Issuing authority | YES | TSE — Tribunal Supremo de Elecciones |
| 5 | Legal force | YES | Administrative regulation (decreeto TSE) |
| 6 | Downloadable from official URL | ? | Must locate at TSE normativa portal |
| 7 | OCR required | ? | Must assess after download |
| 8 | Relevant content | YES | Referéndum — procedimiento operativo de activación; recolección de firmas; verificación TSE |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_tse_reglamento_referendum.md` |
| 12 | Jurisdiction level | YES | National — administrative regulation |
| 13 | Phase | YES | Phase 1 — P1 |

---

### CR-07 — TSE — Reglamento sobre Iniciativa Ciudadana en la Formación de la Ley

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — locate in TSE normativa |
| 2 | Current version | ? | Must locate current decree number |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | TSE |
| 5 | Legal force | YES | Administrative regulation |
| 6 | Downloadable from official URL | ? | Must locate at TSE normativa |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Iniciativa popular — verificación de apoyos ciudadanos por el TSE |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_tse_reglamento_iniciativa_ciudadana.md` |
| 12 | Jurisdiction level | YES | National — administrative regulation |
| 13 | Phase | YES | Phase 1 — P1 |

---

### CR-08 — Reglamento de la Asamblea Legislativa

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — locate in Asamblea Legislativa: http://www.asamblea.go.cr/ |
| 2 | Current version | ? | Must verify current version |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Asamblea Legislativa |
| 5 | Legal force | YES | Internal regulation |
| 6 | Downloadable from official URL | YES | Asamblea Legislativa official portal |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Iniciativa popular — tramo legislativo: admisión, comisiones, trámite |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_reglamento_asamblea_legislativa.md` |
| 12 | Jurisdiction level | YES | National — internal regulation |
| 13 | Phase | YES | Phase 1 — P1 |

---

## BLOCK 6 — Costa Rica jurisprudence

### CR-09 — TSE — Jurisprudencia y resoluciones sobre participación directa

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — access via TSE: https://www.tse.go.cr/jurisprudencia.htm |
| 2 | Current version | ? | Dynamic database — record access date and scope of query |
| 3 | Last amendment date | N/A | Ongoing; record date range |
| 4 | Issuing authority | YES | TSE |
| 5 | Legal force | YES | Binding in electoral matters (exclusive constitutional jurisdiction) |
| 6 | Downloadable from official URL | YES | TSE jurisprudencia portal |
| 7 | OCR required | N/A | Digital text |
| 8 | Relevant content | YES | Referéndum, iniciativa popular, derechos de partidos, paridad |
| 9 | Human review required | YES | Holdings must be verified |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_tse_jurisprudencia_participacion_directa.md` |
| 12 | Jurisdiction level | YES | National — electoral jurisdiction |
| 13 | Phase | YES | Phase 1 — P1 |

---

### CR-10 — Sala Constitucional (Sala IV) — Votos clave sobre derechos políticos y referéndum

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — access via Nexus PJ: https://nexuspj.poder-judicial.go.cr/ |
| 2 | Current version | ? | Identify specific votos: 2771-2003, 17555-2014, and others on political rights |
| 3 | Last amendment date | N/A | Individual judgments — record date of each voto |
| 4 | Issuing authority | YES | Sala Constitucional — Corte Suprema de Justicia |
| 5 | Legal force | YES | Binding — Sala IV decisions on constitutionality are final and erga omnes |
| 6 | Downloadable from official URL | YES | Nexus PJ |
| 7 | OCR required | N/A | Digital text |
| 8 | Relevant content | YES | Constitutional review of referéndum restrictions; political rights scope |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/costa_rica/md/` |
| 11 | Proposed filename | NO | Proposed: `costa_rica_sala_iv_jurisprudencia_derechos_politicos_referendum.md` |
| 12 | Jurisdiction level | YES | National — constitutional jurisdiction |
| 13 | Phase | YES | Phase 1 — P1 |

---

## BLOCK 7 — International and inter-American standards

### INT-01 — Convención Americana sobre Derechos Humanos (CADH)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from OEA: https://www.oas.org/dil/esp/tratados_b-32_convencion_americana_sobre_derechos_humanos.htm |
| 2 | Current version | ? | Stable treaty text — verify against OAS official version |
| 3 | Last amendment date | N/A | Treaty text does not change; record adoption date (1969) and entry into force |
| 4 | Issuing authority | YES | OAS — Organización de los Estados Americanos |
| 5 | Legal force | YES | International treaty — binding on ratifying States |
| 6 | Downloadable from official URL | YES | OAS treaty collection |
| 7 | OCR required | ? | Must assess PDF |
| 8 | Relevant content | YES | Art. 23 — derechos políticos — central standard for all project analysis |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/international_standards/md/` |
| 11 | Proposed filename | NO | Proposed: `interamerican_convencion_americana_derechos_humanos_cadh_1969.md` |
| 12 | Jurisdiction level | YES | International — inter-American |
| 13 | Phase | YES | Phase 1 — P1 |

---

### INT-02 — Pacto Internacional de Derechos Civiles y Políticos (PIDCP)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from OHCHR: https://www.ohchr.org/es/ |
| 2 | Current version | ? | Stable treaty text; verify official Spanish version |
| 3 | Last amendment date | N/A | Treaty text does not change; record adoption date (1966) and entry into force |
| 4 | Issuing authority | YES | ONU — Asamblea General |
| 5 | Legal force | YES | International treaty — binding on ratifying States |
| 6 | Downloadable from official URL | YES | OHCHR |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Art. 25 — political rights at universal level |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/international_standards/md/` |
| 11 | Proposed filename | NO | Proposed: `un_pacto_internacional_derechos_civiles_politicos_pidcp_1966.md` |
| 12 | Jurisdiction level | YES | International — universal |
| 13 | Phase | YES | Phase 1 — P1 |

---

### INT-03 — Sentencias de la CorteIDH sobre Art. 23 CADH (Castañeda Gutman, Yatama, López Mendoza, Petro Urrego)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from CorteIDH: https://www.corteidh.or.cr/casos_sentencias.cfm |
| 2 | Current version | YES | Individual judgments — stable; download official Spanish version |
| 3 | Last amendment date | N/A | Individual judgments do not change; record date of each sentencia |
| 4 | Issuing authority | YES | Corte Interamericana de Derechos Humanos |
| 5 | Legal force | YES | Binding on respondent State; persuasive for all States parties |
| 6 | Downloadable from official URL | YES | CorteIDH official case database |
| 7 | OCR required | ? | Must assess each PDF |
| 8 | Relevant content | YES | Art. 23 holdings; candidaturas independientes; proportionality of restrictions; Castañeda Gutman vs México directly relevant |
| 9 | Human review required | YES | Holdings, operative paragraphs require legal specialist verification |
| 10 | Target folder | YES | `01_sources/international_standards/md/` |
| 11 | Proposed filename | NO | Proposed: `corteidh_jurisprudencia_derechos_politicos_art23_cadh.md` (or separate file per case) |
| 12 | Jurisdiction level | YES | International — inter-American |
| 13 | Phase | YES | Phase 1 — P1 |

---

### INT-04 — Observación General No. 25 del Comité de Derechos Humanos ONU (1996)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from OHCHR |
| 2 | Current version | YES | Stable document — adopted 1996; record document number HRI/GEN/1/Rev.9 (Vol. I) |
| 3 | Last amendment date | N/A | General Comments do not change after adoption |
| 4 | Issuing authority | YES | Comité de Derechos Humanos ONU (CCPR) |
| 5 | Legal force | YES | Authoritative interpretation — not binding in same way as treaty, but treated as interpretive authority |
| 6 | Downloadable from official URL | YES | OHCHR — available in Spanish |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Authoritative interpretation of Art. 25 PIDCP — activation standards, thresholds, proportionality |
| 9 | Human review required | YES | |
| 10 | Target folder | YES | `01_sources/international_standards/md/` |
| 11 | Proposed filename | NO | Proposed: `un_ccpr_observacion_general_25_art25_pidcp_1996.md` |
| 12 | Jurisdiction level | YES | International — universal |
| 13 | Phase | YES | Phase 1 — P1 |

---

### INT-05 — Carta Democrática Interamericana (OEA — 2001)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from OEA |
| 2 | Current version | YES | Stable document — adopted 2001 |
| 3 | Last amendment date | N/A | Does not change |
| 4 | Issuing authority | YES | OEA — Asamblea General |
| 5 | Legal force | YES | Soft law — not a binding treaty; persuasive |
| 6 | Downloadable from official URL | YES | OEA official documents |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Democracy and political participation standards — background for Art. 23 CADH analysis |
| 9 | Human review required | YES | Distinguish from binding standards |
| 10 | Target folder | YES | `01_sources/comparative_soft_law/md/` |
| 11 | Proposed filename | NO | Proposed: `oas_carta_democratica_interamericana_2001.md` |
| 12 | Jurisdiction level | YES | International — inter-American soft law |
| 13 | Phase | YES | Phase 1 — P2 |

---

## BLOCK 8 — Comparative soft law

### INT-06 — Comisión de Venecia — Código de Buenas Prácticas en Materia Electoral (2002)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from Council of Europe / Venice Commission |
| 2 | Current version | ? | Verify whether 2002 version with 2018 guidelines update is current |
| 3 | Last amendment date | ? | Check for updates after 2018 |
| 4 | Issuing authority | YES | Comisión de Venecia — Consejo de Europa |
| 5 | Legal force | YES | Soft law — no binding force; used as global comparative benchmark |
| 6 | Downloadable from official URL | YES | Venice Commission portal |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Electoral standards — comparative benchmark for activation analysis |
| 9 | Human review required | YES | Distinguish from binding inter-American standards |
| 10 | Target folder | YES | `01_sources/comparative_soft_law/md/` |
| 11 | Proposed filename | NO | Proposed: `venice_commission_codigo_buenas_practicas_materia_electoral_2002.md` |
| 12 | Jurisdiction level | YES | International — comparative soft law |
| 13 | Phase | YES | Phase 1 — P2 |

---

### INT-07 — IDEA International — Voter Turnout and Direct Democracy (comparative database)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — IDEA International: https://www.idea.int/data-tools/ |
| 2 | Current version | ? | Dynamic database — record access date |
| 3 | Last amendment date | N/A | Ongoing database |
| 4 | Issuing authority | YES | International IDEA |
| 5 | Legal force | YES | Soft law — empirical and comparative reference |
| 6 | Downloadable from official URL | YES | IDEA data tools |
| 7 | OCR required | N/A | Digital data |
| 8 | Relevant content | YES | Comparative data on direct democracy mechanisms — Mexico and Costa Rica context |
| 9 | Human review required | NO | Empirical data — no legal interpretation required |
| 10 | Target folder | YES | `01_sources/comparative_soft_law/md/` |
| 11 | Proposed filename | NO | Proposed: `idea_international_direct_democracy_database_comparative.md` |
| 12 | Jurisdiction level | YES | International — comparative empirical |
| 13 | Phase | YES | Phase 1 — P2 |

---

### INT-08 — IACHR — Informe sobre participación política y derechos políticos en las Américas

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — identify and download from IACHR: https://www.oas.org/es/cidh/ |
| 2 | Current version | ? | Identify most relevant thematic report |
| 3 | Last amendment date | ? | Must confirm publication date of relevant report |
| 4 | Issuing authority | YES | Comisión Interamericana de Derechos Humanos (CIDH) |
| 5 | Legal force | YES | Soft law — persuasive; IACHR reports are not binding judgments |
| 6 | Downloadable from official URL | YES | OAS/IACHR portal |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Regional standards on political participation — IACHR interpretation of Art. 23 CADH |
| 9 | Human review required | YES | Distinguish from CorteIDH binding standards |
| 10 | Target folder | YES | `01_sources/international_standards/md/` |
| 11 | Proposed filename | NO | Proposed: `iachr_informe_participacion_politica_americas.md` (title and year to confirm) |
| 12 | Jurisdiction level | YES | International — inter-American |
| 13 | Phase | YES | Phase 1 — P2 |

---

### INT-09 — Reglamento de la CorteIDH (vigente)

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Official source | ? | No file — download from CorteIDH |
| 2 | Current version | ? | Verify current version (last reform 2009 with subsequent amendments) |
| 3 | Last amendment date | ? | Must confirm |
| 4 | Issuing authority | YES | Corte Interamericana de Derechos Humanos |
| 5 | Legal force | YES | Procedural rules of the Court |
| 6 | Downloadable from official URL | YES | CorteIDH |
| 7 | OCR required | ? | Must assess |
| 8 | Relevant content | YES | Procedural standards for IACtHR litigation — relevant for remedy mapping |
| 9 | Human review required | NO | Procedural document — low analytical complexity |
| 10 | Target folder | YES | `01_sources/international_standards/md/` |
| 11 | Proposed filename | NO | Proposed: `corteidh_reglamento_vigente.md` |
| 12 | Jurisdiction level | YES | International — inter-American |
| 13 | Phase | YES | Phase 1 — P2 |

---

## Summary table — verification status by source

| Source ID | Title (short) | Country | Pass/Fail/Pending | Critical blockers |
|---|---|---|---|---|
| MX-01 | CPEUM | Mexico | Partial — pending | Verify version currency; OCR check; filename check |
| MX-02 | LGIPE | Mexico | Pending — no file | Download required; OCR check; version post-Plan B |
| MX-03 | LCPo | Mexico | Pending — no file | Download required |
| MX-04 | LFRMPE | Mexico | Pending — no file | Download required |
| MX-05 | LGPP | Mexico | Pending — no file | Download required; version post-Plan B |
| MX-06 | LGSMIME | Mexico | Pending — no file | Download required |
| MX-07 | LOCGEUM | Mexico | Partial — PDF exists | OCR check; version verification; Markdown conversion needed |
| MX-08 | Reglamento Cámara | Mexico | Partial — PDF exists | OCR check; version verification; conversion needed |
| MX-09 | Ley de Amparo | Mexico | Partial — PDF exists | OCR check; scope confirmation needed |
| MX-10 | H_219.pdf | Mexico | BLOCKED — unidentified | Must identify content before any corpus decision |
| MX-11 | INE acuerdo CG572/2021 consulta popular | Mexico | Pending — no file | Locate in INE repository; verify no superseding acuerdo |
| MX-12 | INE acuerdo CG309/2022 revocación | Mexico | Pending — no file | Locate in INE repository |
| MX-13 | INE lineamientos candidaturas independientes | Mexico | Pending — no file | Locate current acuerdo; determine if 2023 or 2024 version |
| MX-14 | INE Reglamento Interior | Mexico | Pending — no file | Locate in INE normativa or DOF |
| MX-15 | LGMDE | Mexico | Pending — no file | Download from Cámara |
| MX-16 | TEPJF jurisprudencia | Mexico | Pending — no file | Query TEPJF database by subject |
| MX-17 | SCJN tesis Art. 35 | Mexico | Pending — no file | Query SJF2; post-Plan B decisions |
| CR-01 | Constitución Política CR | Costa Rica | Pending — no file | Download from TSE; all 13 checks pending |
| CR-02 | Código Electoral 8765 | Costa Rica | Pending — no file | Download from TSE |
| CR-03 | Ley Referéndum 8492 | Costa Rica | Pending — no file | Download from SCIJ |
| CR-04 | Ley Iniciativa Popular 8491 | Costa Rica | Pending — no file | Download from SCIJ |
| CR-05 | Ley Orgánica TSE 3504 | Costa Rica | Pending — no file | Download from SCIJ |
| CR-06 | TSE Reglamento Referéndum | Costa Rica | Pending — no file | Locate in TSE normativa; find decree number |
| CR-07 | TSE Reglamento Iniciativa Ciudadana | Costa Rica | Pending — no file | Locate in TSE normativa |
| CR-08 | Reglamento Asamblea Legislativa | Costa Rica | Pending — no file | Locate in Asamblea portal |
| CR-09 | TSE jurisprudencia | Costa Rica | Pending — no file | Query TSE jurisprudencia portal |
| CR-10 | Sala IV votos | Costa Rica | Pending — no file | Access Nexus PJ; identify key votos |
| INT-01 | CADH | International | Pending — no file | Download from OAS |
| INT-02 | PIDCP | International | Pending — no file | Download from OHCHR |
| INT-03 | CorteIDH sentencias Art. 23 | International | Pending — no file | Download 4 key cases from CorteIDH |
| INT-04 | OG 25 CCPR | International | Pending — no file | Download from OHCHR |
| INT-05 | Carta Democrática OEA | International | Pending — no file | Download from OAS |
| INT-06 | Venice Commission Code | International | Pending — no file | Download from Council of Europe |
| INT-07 | IDEA Direct Democracy | International | Pending — no file | Access IDEA data tools |
| INT-08 | IACHR report | International | Pending — no file | Identify and download relevant report |
| INT-09 | CorteIDH Reglamento | International | Pending — no file | Download from CorteIDH |

---

*End of verification checklist. This document should be updated as each source is acquired, converted, and added to the corpus. A source passes verification when all applicable checks show YES or N/A. Record the verification date and responsible person in the corpus index `date_added` and `notes` fields.*
