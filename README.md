# NormTrace-Political Rights

**Legal-institutional activation mapping of political participation rights in Mexico and Costa Rica**

**Version:** 0.1.0-pilot
**Status:** Work in progress — all outputs are preliminary and require expert legal review

---

## Overview

NormTrace-Political Rights is an academic, open-methodology infrastructure for mapping the legal-institutional conditions under which citizens can activate political participation rights in Mexico and Costa Rica.

The project does not ask whether political rights exist in the law. It asks whether, and to what degree, they are legally activable: whether citizens can exercise them through identifiable procedures, before identified authorities, with defined thresholds, within specified timelines, subject to review, and with binding legal effect.

Each right and mechanism is traced from its international or inter-American standard through its domestic constitutional, statutory, regulatory and jurisprudential layers, and assessed against an activation scale and a typology of legal-institutional barriers.

NormTrace-Political Rights is one module within the NormTrace infrastructure. Other modules address different instruments and legal domains. This module is limited to political rights and citizen participation mechanisms.

---

## Why formal recognition is not enough

Many legal systems formally recognise political rights. Constitutions affirm the right to vote, to be elected, to participate in referendums, to submit citizen legislative initiatives, to request popular consultations, or to trigger revocation processes. This formal recognition is legally and politically significant.

It is not, however, sufficient evidence that a right or mechanism is legally activable.

A mechanism is legally activable only when the legal system provides, at minimum:

- an identified responsible authority;
- a defined procedure;
- stated activation thresholds (signature, geographic, temporal);
- admissibility rules with defined criteria;
- a review or remedy mechanism in case of refusal or error;
- a legal effect that follows from successful activation;
- accessibility conditions that do not make activation unreasonably burdensome;
- an implementation duty that obligates the relevant institution to act.

When one or more of these conditions is absent, incomplete, or unreasonably burdensome, a legal-institutional barrier exists. The mechanism may be formally recognised while remaining practically inaccessible. This gap is the core analytical problem of this project.

---

## Pilot scope

**Countries:** Mexico and Costa Rica

Mexico and Costa Rica are selected as pilot cases for the following reasons:

- Both are constitutional democracies with ratified American Convention on Human Rights commitments.
- Both have constitutional provisions on political participation rights and direct democracy mechanisms.
- Both have national electoral courts with substantial jurisprudence on political rights.
- The institutional designs differ significantly: Mexico has a federal structure with a dedicated national electoral authority (INE) and a specialised electoral tribunal (TEPJF); Costa Rica has a unitary structure with a constitutionally autonomous electoral court (TSE) of singular jurisdiction.
- The comparison identifies structural differences in how activation is designed without ranking one system above the other.

**Phase 1** covers national-level constitutional, statutory, electoral, legislative and judicial sources in both countries, alongside international and inter-American standards.

**Phase 2** (planned) covers municipal and subnational mechanisms, empirical use data, and expert validation.

---

## Methodological contribution

NormTrace-Political Rights introduces a structured distinction between formal recognition and legal activation, and applies it systematically to:

- each mechanism identified in domestic law (e.g. referendum, citizen legislative initiative, popular consultation, revocation of mandate, independent candidacy);
- each relevant international or inter-American standard (ACHR Article 23, ICCPR Article 25, General Comment 25, IACtHR jurisprudence);
- each actor identified in the legal-institutional chain (who initiates, receives, verifies, admits, organises, reviews, and implements);
- each activation requirement (threshold, procedure, timeline, admissibility condition);
- each legal effect (binding, advisory, archivable without decision);
- each barrier type identified in the legal text.

The output is not a ranking of democratic quality. It is a structured legal-institutional map of activation conditions and barriers, designed to support comparative research, strategic litigation analysis, and legislative reform work.

---

## Repository structure

```
00_project/           — Scope, methodology, data dictionary, protocols, AI disclosure
01_sources/           — Legal instruments in PDF and Markdown with YAML metadata
  international_standards/  — ACHR, ICCPR, IACtHR jurisprudence, IACHR reports, soft law
  mexico/                   — Mexican constitutional, statutory, electoral, regulatory sources
  costa_rica/               — Costa Rican constitutional, statutory, electoral, regulatory sources
  comparative_soft_law/     — Venice Commission, IDEA International, other comparative references
02_data/              — Raw and processed structured data
03_tables/            — Analytical mapping tables (CSV)
  source_discovery/         — Source inventory and acquisition tracking
  domestic_corpus/          — Document structure and provision index
  international_standards/  — International and inter-American standards tables
  mechanisms/               — Mechanism-level mapping
  actors/                   — Actor registry and competence mapping
  activation_mapping/       — Activation scale coding and barrier coding
  barriers/                 — Barrier typology tables
  comparative/              — Mexico–Costa Rica comparative matrix
  network_analysis/         — Network nodes and edges
  validation/               — Validation reports and review flags
04_outputs/           — Country snapshots, comparative briefs, figures, exports
  country_snapshots/
  comparative_briefs/
  exports/
  figures/
  validation_reports/
06_scripts/           — Conversion, build, validation and export scripts
99_archive/           — Superseded sources and experimental outputs
```

---

## Data workflow

The analytical workflow proceeds in the following stages:

1. Source identification and vigency verification
2. Markdown conversion and YAML metadata assignment
3. Domestic corpus index construction
4. Legal structure detection (articles, sections, transitory provisions)
5. Domestic provision extraction into structured tables
6. Mechanism extraction and classification
7. Activation requirements extraction (threshold, procedure, timeline, admissibility)
8. Actor and competence mapping
9. International and inter-American standards extraction
10. Standard-to-mechanism mapping
11. Activation scale coding (0–5)
12. Barrier typology coding
13. Comparative Mexico–Costa Rica analysis
14. Validation and expert review

Each stage produces or updates one or more CSV tables in `03_tables/`. All tables carry review status fields. No row is considered final until human expert review is recorded.

---

## AI-assisted workflow and human review

AI assistance is used in this project for: document conversion, metadata generation, preliminary extraction of provisions and activation requirements, preliminary classification on the activation scale and barrier typology, and consistency checking across tables.

AI does not determine final legal interpretation. AI does not assess compliance. AI does not produce legal advice.

All AI-assisted outputs are preliminary. Every row in every table requires traceability to a specific source, article, paragraph, case number or explicit uncertainty note. Rows without source traceability are incomplete. All outputs require human expert legal review before use in policy, litigation or legal advice contexts.

See `00_project/ai_use_disclosure.md` for the full AI use policy.

---

## Limitations

- The project analyses legal texts, not their implementation in practice.
- Formal legal activation does not guarantee actual access or use.
- Municipal and subnational mechanisms are phase 2.
- Jurisprudence included in phase 1 is selective and thematic; it does not constitute a complete case law survey.
- Activation scale coding is preliminary and conservative; it requires expert legal validation.
- The project does not assess overall democratic quality, electoral fairness as political practice, or partisan competition dynamics.
- All outputs are work in progress. Version history is maintained through Git.

---

## Citation

Santos Domínguez, A. B. (2026). *NormTrace-Political Rights: Legal-Institutional Activation Mapping of Political Participation Rights in Mexico and Costa Rica* (Version 0.1.2) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21296393 

---

## License

## License and rights

See [LICENSE.md](LICENSE.md) for the licensing and rights conditions applicable to the software, original research materials, official legal sources, and third-party materials included in this repository.
