# AI Use Disclosure — NormTrace-Political Rights

**Version:** 0.1.0-pilot
**Date:** 2026-05-18
**Status:** Current

---

## 1. Scope of this disclosure

This document describes how AI assistance is used in the NormTrace-Political Rights project, what AI does not do, and what human review requirements apply to all AI-assisted outputs.

---

## 2. What AI assistance is used for

AI assistance is used in this project for the following tasks:

**Document processing:**
- Converting PDF and HTML legal sources to structured Markdown
- Generating YAML metadata blocks for each source file
- Identifying structural elements (articles, paragraphs, fractions, transitories)

**Preliminary extraction:**
- Extracting domestic legal provisions relevant to political participation rights and mechanisms
- Extracting activation requirements (thresholds, procedures, timelines, admissibility conditions)
- Extracting actor roles and competence assignments from legal text
- Extracting holdings, criteria, and operative paragraphs from jurisprudential sources

**Preliminary classification:**
- Assigning preliminary activation scale scores (0–5) with supporting evidence notes
- Identifying preliminary barrier types from the project typology
- Tagging provisions by mechanism type and actor role

**Consistency checking:**
- Cross-checking foreign key references across tables
- Flagging fields that appear incomplete, inconsistent, or uncertain
- Identifying possible duplicate provisions or source entries

**Drafting:**
- Drafting project documentation, analytical notes, and methodology text subject to human review
- Generating validation summaries and review flags

---

## 3. What AI does not do

- AI does not provide final legal interpretation of any provision, holding, or standard.
- AI does not assess whether Mexico or Costa Rica complies with any international obligation.
- AI does not determine the binding or non-binding force of any instrument.
- AI does not resolve ambiguities in legal text; it flags them for human review.
- AI does not provide legal advice.
- AI does not replace expert review by qualified legal professionals.
- AI does not verify that sources are current, official, or complete; source verification is a human responsibility.

---

## 4. Traceability requirement

Every row in every analytical table must be traceable to one of the following:

- A specific article and paragraph of a domestic legal instrument (identified by source ID, article number, and paragraph)
- A specific holding, criterion, or operative paragraph of an international or inter-American judicial or quasi-judicial body (identified by source ID and paragraph number)
- A specific standard in a treaty, general comment, or authoritative interpretive document (identified by source ID and article/paragraph)
- An explicit uncertainty note explaining why no provision could be identified and what sources were searched

Rows without source traceability are not considered complete. The `review_status` field must remain `preliminary` until source traceability is confirmed and human review is recorded.

---

## 5. Human review requirements

All AI-assisted outputs are preliminary. The following human review steps are required before any output may be considered validated:

| Output type | Required review |
|---|---|
| Provision extraction | Verification by a qualified legal professional that the extracted text matches the source and that the classification is accurate |
| Activation scale scores | Review by a qualified electoral or constitutional law specialist for the relevant jurisdiction |
| Barrier classifications | Review by a qualified legal professional with knowledge of the applicable international standards |
| Jurisprudence holdings | Review by a qualified international human rights lawyer or electoral law specialist |
| Actor and competence mapping | Review by a qualified professional with knowledge of the institutional structure of the relevant jurisdiction |
| Comparative analysis | Review by a comparative constitutional or electoral law specialist |

---

## 6. Labelling of AI-assisted outputs

All AI-assisted outputs carry the field `review_status: preliminary` until human review is completed and recorded. The `reviewer` and `review_date` fields in the mapping table record who validated each row and when.

Outputs with `review_status: preliminary` must not be cited, relied upon in policy documents, used in litigation, or presented as established legal findings without disclosure of their preliminary status.

---

## 7. No legal advice

Nothing in this repository constitutes legal advice. The outputs are academic research infrastructure. They are designed to support research, comparative analysis, and legislative reform work by qualified professionals who will apply their own legal judgment. No output in this repository should be relied upon as legal advice in any specific legal matter.

---

## 8. Model and tool disclosure

| Tool | Purpose | Notes |
|---|---|---|
| Claude (Anthropic) | Document processing, extraction, drafting, preliminary classification | Used via Cowork mode and Agent SDK |
| Python scripts | Validation, consistency checks, network analysis, CSV processing | See `06_scripts/` |

Specific model versions are not recorded at the row level but may be noted in commit messages where material to the output.
