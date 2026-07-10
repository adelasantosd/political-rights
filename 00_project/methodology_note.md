# Methodology Note — NormTrace-Political Rights

**Version:** 0.1.0-pilot
**Date:** 2026-05-18
**Status:** Draft — subject to revision

---

## 1. Methodological problem

Legal recognition of political participation rights is widespread. Constitutional provisions affirm the right to vote, to stand for election, to participate in referendums, to submit citizen legislative initiatives, and to trigger other direct democracy mechanisms. Electoral codes and implementing regulations exist in most Latin American legal systems. Inter-American and international human rights standards reinforce these rights.

The analytical problem is that recognition does not equal activation. A legal text can formally establish a right or mechanism while leaving unresolved the question of how, before whom, under what conditions, and with what legal effect that right or mechanism can be exercised. When the procedure is absent or unclear, when no authority is identified, when activation thresholds are prohibitively high, when the legal effect is non-binding, or when no remedy exists if an institution refuses to act, the mechanism exists in law but is not legally activable in practice.

This methodological gap — between formal recognition and legal activation — is the central object of analysis. It has not been sufficiently treated in comparative electoral law scholarship, which often catalogues mechanisms without assessing the completeness of their activation architecture.

NormTrace-Political Rights applies a structured, reproducible methodology to identify and map this gap for Mexico and Costa Rica across a defined range of political participation rights and mechanisms.

---

## 2. Conceptual distinctions

**Formal recognition.** A right or mechanism is formally recognised when it appears in constitutional, statutory, or equivalent legal text as an entitlement or procedural option available to citizens. Formal recognition establishes the right's existence in the legal system. It does not establish its activability.

**Legal activation.** A right or mechanism is legally activated when the domestic legal system provides all of the following conditions: (a) an identified responsible authority with a defined competence; (b) a procedure specifying how the right or mechanism is invoked; (c) threshold conditions (signature, geographic, temporal, or other) that are defined and not unreasonably burdensome; (d) admissibility rules with defined criteria and limited discretion; (e) a timeline for processing; (f) a review or remedy mechanism in case of refusal, error or inaction; (g) a legal effect binding on the relevant authority; (h) accessibility conditions that do not make activation disproportionately difficult for ordinary citizens; (i) an implementation duty that obligates the authority to act once activation conditions are met.

The absence of any one of these conditions does not necessarily make a mechanism entirely inert, but it produces a legal-institutional barrier that the project records and classifies.

**Activation burden.** The aggregate of legal-institutional conditions that a citizen or group must satisfy to invoke a mechanism. High activation burden is not automatically a legal deficiency but may indicate a disproportionate restriction on political rights under international standards.

**Legal-institutional barrier.** A specific identifiable condition in the legal text — or a specific absence from it — that impedes or complicates the activation of a political participation mechanism. Barriers are classified using the typology in section 5.

**Reviewability.** The availability of a formal legal mechanism to challenge, before a competent body, a decision refusing or obstructing the activation of a political participation right or mechanism. Reviewability is treated as a necessary condition for full legal activation under Article 25 ICCPR and Articles 23 and 25 ACHR.

**Binding effect.** The legal consequence of successful activation. A mechanism has binding effect when its outcome creates a legally enforceable obligation on the relevant authority (e.g. to hold a vote, to process a legislative initiative, to organise a revocation process). Non-binding effect — where the outcome can be disregarded — is recorded as a barrier.

**Accessibility condition.** A condition in the legal text — or its absence — that affects whether ordinary citizens, including those with limited resources, digital access, or knowledge of formal procedures, can practically invoke a mechanism. Accessibility conditions include: free or low-cost procedures; availability in official languages; digital and in-person options; geographic distribution of collection points; and non-discriminatory standing requirements.

---

## 3. Analytical workflow

The project follows a fourteen-stage analytical workflow:

**Stage 1: Source identification and vigency verification.** Identify official, current, consolidated legal texts. Verify last amendment date, issuing authority, and legal force. Exclude draft texts, historical versions, and unofficial repositories as primary sources.

**Stage 2: Markdown conversion and metadata.** Convert verified PDF sources to Markdown, preserving article numbers, section headings, transitory provisions, and annexes. Assign YAML metadata block to each file. Record source ID, title, jurisdiction, source type, issuing authority, official URL, publication date, last amendment date, legal force, and version date.

**Stage 3: Domestic corpus index.** Build the `political_rights_corpus_index.csv` listing all sources in the corpus with identifiers, metadata keys, and status fields.

**Stage 4: Legal structure detection.** Identify the structural architecture of each source: title/book/chapter/article/paragraph/fraction structure. Detect numbering conventions. Record in `political_rights_document_structure.csv`.

**Stage 5: Domestic provision extraction.** Extract provisions relevant to political participation rights and mechanisms. Record verbatim or closely paraphrased text with article, paragraph, and fraction references. Tag by mechanism, right, and actor. Record in `political_rights_domestic_provisions.csv`.

**Stage 6: Mechanism extraction.** Identify each distinct participation mechanism in the legal text. Classify by type (vote, candidacy, referendum, initiative, consultation, revocation, remedy, other). Record in `political_rights_mechanisms.csv`.

**Stage 7: Activation requirements extraction.** For each mechanism, extract each activation requirement identified in the legal text. Classify by component (threshold, procedure, timeline, admissibility, authority, legal effect, review, accessibility). Record in `political_rights_activation_requirements.csv`.

**Stage 8: Actor and competence mapping.** Identify all institutions and actors with a role in each mechanism: who initiates, receives, verifies, admits, organises, reviews, and implements. Record competence type (exclusive, shared, concurrent, delegated, undefined). Record in `political_rights_actors.csv` and `political_rights_actor_mechanism_edges.csv`.

**Stage 9: International and inter-American standards extraction.** Extract relevant standards from ACHR Article 23, ICCPR Article 25, General Comment 25, IACtHR judgments, IACHR reports, and other instruments in scope. Record verbatim holdings, operative paragraphs, and criteria with source reference. Record in `political_rights_international_standards.csv`.

**Stage 10: Standard-to-mechanism mapping.** Map each international or inter-American standard to the relevant domestic mechanism or provision. Identify correspondence, partial correspondence, or absence. Record in `political_rights_activation_standards.csv` and `political_rights_mapping.csv`.

**Stage 11: Activation scale coding.** Apply the activation scale (0–5) to each mechanism in each country. Record the score, the evidence supporting it, and the confidence level. Flag for human review. Record in `political_rights_mapping.csv`.

**Stage 12: Barrier typology coding.** Identify and classify each legal-institutional barrier associated with each mechanism. Record the barrier type, the specific provision or absence that generates the barrier, and the legal text reference. Record in `political_rights_barrier_typology.csv`.

**Stage 13: Comparative Mexico–Costa Rica analysis.** Compare activation levels and barrier profiles across the two countries for equivalent or analogous mechanisms. Identify structural design differences, common barriers, and divergent activation pathways. Record in `political_rights_comparative_mechanism_matrix.csv`.

**Stage 14: Validation and expert review.** Run automated validation checks (see `00_project/validation_protocol.md`). Flag rows for human legal review. Record review status and reviewer notes. No row is considered validated until human review is recorded.

---

## 4. Activation scale

The activation scale measures the degree to which a political participation mechanism is legally activable from the text of domestic law. Scores run from 0 to 5.

| Score | Label | Description |
|---|---|---|
| **0** | No identifiable domestic recognition | No provision in the corpus addresses this right or mechanism, even indirectly. |
| **1** | Formal recognition only | The right or mechanism appears in the constitutional or legal text as an entitlement or option, but no procedure, authority, threshold, or legal effect is defined. Constitutional declaration without implementing law. |
| **2** | Recognition with incomplete or unclear procedure | Some procedural elements exist (e.g. a threshold or a designated authority) but the activation architecture is incomplete: one or more critical conditions (procedure, review, legal effect, or admissibility) are absent or ambiguous. |
| **3** | Procedurally available but high activation burden | The activation architecture is substantially present but one or more conditions impose a disproportionate burden: e.g. threshold is set at a level the IACtHR or HRC has characterised as unreasonable; no independent review exists; legal effect is conditional on a secondary decision; or accessibility conditions exclude significant population groups. |
| **4** | Legally actionable with defined authority, procedure, review and reasonable access | All critical activation conditions are present and defined in law: authority, procedure, threshold, admissibility criteria, timeline, review mechanism, and legal effect. The burden is identifiable and not obviously disproportionate. Accessible in law, though not necessarily in practice. |
| **5** | Fully activated with clear procedure, institutional support, safeguards, review, transparency and effective implementation route | All conditions for level 4, plus: explicit institutional support or facilitation duties; transparency or public information obligations; accessibility safeguards (language, digital/in-person options, geographic reach); effective review mechanism with defined timelines; binding legal effect with enforcement mechanism; and no identifiable legal-textual barrier. |

**Coding rules:**

- Score the mechanism as reflected in the legal text, not in practice or in political reality.
- Score conservatively: when in doubt between two scores, assign the lower one and flag for review.
- Record the specific evidence for the score in the `activation_evidence` field.
- A mechanism may be scored differently in Mexico and Costa Rica even if the formal constitutional text is similar, because the activation architecture in implementing law differs.
- Do not treat the existence of a constitutional provision as evidence of level 4 or 5. Constitutional recognition without implementing law is level 1.
- Do not treat the existence of an implementing law as evidence of level 4 or 5 unless all activation conditions are verifiably present in the text.

---

## 5. Barrier typology

The following barrier types are used in the project. A single mechanism may exhibit more than one barrier type. Each barrier must be traceable to a specific provision or to a specific absence in the legal text.

| Barrier type | Description |
|---|---|
| `formal_recognition_only` | Right or mechanism recognised but no implementing procedure exists in law. |
| `missing_procedure` | The mechanism is recognised and partially regulated, but the procedure for invocation is absent or insufficiently defined. |
| `unclear_responsible_authority` | No authority is designated, or the designation is ambiguous or contested between institutions. |
| `high_signature_threshold` | Signature or support threshold is set at a level that imposes disproportionate burden given population or electoral roll size. |
| `high_geographic_threshold` | Geographic distribution requirement (e.g. minimum support across states or regions) is set at a disproportionate level. |
| `restrictive_time_limit` | Time allowed for activation is too short to permit reasonable citizen organisation, or no time limit is set (creating procedural uncertainty). |
| `broad_admissibility_discretion` | Admissibility rules give an institution broad or unguided discretion to reject a petition, without defined criteria or review. |
| `subject_matter_exclusion` | The mechanism explicitly excludes certain subject matters from its scope in ways that may conflict with international standards. |
| `weak_review_remedy` | No review or remedy mechanism is available when activation is refused, or the available remedy is inadequate (e.g. no suspensive effect, very short deadline, no standing for initiators). |
| `non_binding_effect` | The outcome of the mechanism does not create a legally binding obligation on the relevant authority. |
| `implementation_gap` | The law requires a secondary regulation or institutional act to make the mechanism operational, but that secondary act has not been adopted or is incomplete. |
| `transparency_gap` | The law does not require public disclosure of decisions on admissibility, verification, or organisation; or information about procedures is not publicly accessible. |
| `accessibility_gap` | The procedure imposes conditions (economic, geographic, linguistic, literacy-based, or bureaucratic) that effectively exclude population groups not related to a legitimate regulatory objective. |
| `digital_access_gap` | Signature collection or submission is limited to digital platforms without adequate alternative in-person options, or digital platforms impose technical barriers. |
| `territorial_federal_gap` | In federal systems: the mechanism requires action at multiple governmental levels, but coordination obligations are absent or unenforceable, creating implementation uncertainty. |
| `institutional_support_gap` | The law does not assign facilitation, information, or support duties to any institution to assist citizens in invoking the mechanism. |
| `fragmentation_across_legal_instruments` | Activation conditions are distributed across multiple legal instruments with no consolidating norm, creating risk of inconsistency and uncertainty. |
| `dependency_on_secondary_regulation` | The mechanism depends on a secondary regulation or administrative act that has not been issued or is subject to executive or institutional discretion. |
| `obsolete_or_outdated_procedure` | The procedure was designed for conditions (e.g. paper signature collection, in-person registration) that may be inconsistent with current legal or technological reality, creating practical barriers. |
| `no_barrier_identified_in_text` | The legal text does not present an identifiable barrier for this mechanism on this component. Does not imply the mechanism is barrier-free in practice. |
| `uncertain` | A potential barrier may exist but cannot be confirmed or excluded from the legal text alone; human legal review required. |

---

## 6. Actor and mechanism mapping

The project maps the institutional roles in each participation mechanism across both countries. For each mechanism, the following actor roles are identified:

- **Initiator:** The citizen, group, or institution with legal standing to invoke the mechanism.
- **Receiver:** The institution that receives the petition, signature collection, or application.
- **Verifier:** The institution responsible for verifying thresholds, identities, or compliance with formal requirements.
- **Admitting authority:** The institution that rules on admissibility or formally convenes the mechanism.
- **Organiser:** The institution responsible for the operational organisation of the mechanism (ballot design, logistics, voter registry).
- **Reviewer:** The institution with jurisdiction to review refusals, errors, or complaints.
- **Implementer:** The institution with the duty to give effect to the outcome.

Actor mapping uses the `political_rights_actors.csv` table (actor registry with competence type) and the `political_rights_actor_mechanism_edges.csv` table (each actor–role–mechanism link with legal basis).

Competence types recorded: `exclusive`, `shared`, `concurrent`, `delegated`, `undefined`.

---

## 7. International and inter-American standards

International and inter-American standards are used in two ways in this project.

**As reference standards for activation assessment:** The standards of ACHR Article 23, ICCPR Article 25, and General Comment 25 define what a legally activated political right requires. They specify that restrictions on political rights must be lawful, necessary, proportionate, and not discriminatory. They inform the criteria applied when assigning activation scores and barrier types.

**As a mapping layer in the comparative analysis:** Each domestic mechanism is mapped against the applicable international standard to identify: correspondence (domestic law meets or exceeds the standard); partial correspondence (domestic law addresses the standard but incompletely); divergence (domestic law departs from or is inconsistent with the standard); or silence (domestic law does not address the area covered by the standard).

**IACtHR jurisprudence** is treated as binding interpretive authority for Mexico and Costa Rica, both of which have accepted the contentious jurisdiction of the Court. IACtHR judgments involving other States Parties are treated as persuasive but not directly binding. Key judgments are extracted for holdings and operative paragraphs relevant to the activation conditions under review.

**General Comment 25** is treated as authoritative interpretive guidance on ICCPR Article 25. It establishes that states must take positive steps to ensure citizens can exercise participation rights in practice, not merely in form.

**IACHR thematic reports** are treated as soft-law interpretive materials.

**Venice Commission and IDEA International** standards are used as comparative context only in phase 2, and do not carry the legal force of binding treaty obligations.

---

## 8. Comparative logic

Mexico and Costa Rica are compared to identify: structural differences in the design of activation conditions; different legal pathways for equivalent mechanisms; and different barrier profiles for equivalent rights.

The comparison is not a ranking. Neither country is assessed as more or less democratic. The comparison identifies which activation conditions are present in both systems, which are present in one and absent in the other, and what the legal-institutional consequences of those differences are.

Where a mechanism exists in one country but not the other (e.g. revocation of mandate exists in Mexico but is structured differently or absent in Costa Rica at the national level), the comparison notes the structural difference and its implications for the applicable international standard.

The comparative output is recorded in `political_rights_comparative_mechanism_matrix.csv`.

---

## 9. Role of AI, Python and human review

**AI assistance** is used for: document conversion; YAML metadata generation; preliminary extraction of provisions, mechanisms, activation requirements, and actor roles; preliminary classification on the activation scale and barrier typology; consistency checking across tables; and drafting of analytical text subject to human review.

AI outputs are preliminary. AI does not make final legal determinations. AI does not assess compliance. AI does not produce legal advice. AI text generation may introduce errors in legal interpretation, misidentify provisions, or misclassify barriers. All AI-assisted outputs carry `review_status: preliminary` until human legal review is recorded.

**Python scripts** are used for: validation of table structure and consistency; cross-table foreign key checks; network analysis of institutional relationships; and export of structured data. Scripts are stored in `06_scripts/`.

**Human legal review** is necessary and irreplaceable for: confirming provision identification; validating activation scale scores; validating barrier classifications; reviewing jurisprudence holdings; and approving outputs for use. No output is considered validated without recorded human review.

---

## 10. Limitations

- **Corpus dependence:** Analysis is limited to sources in the corpus. Sources not yet added to the corpus will not be reflected in outputs. Corpus completeness is tracked in the source discovery table.
- **Legal text does not prove practice:** A mechanism that is legally activable at level 4 or 5 in the text may still be practically inaccessible due to institutional capacity, social barriers, economic costs, or political pressure. The project maps legal-textual conditions, not empirical access.
- **Activation scoring is conservative and preliminary:** Scores may change following expert review or the addition of new sources (e.g. implementing regulations, jurisprudence).
- **Municipal and subnational mechanisms are phase 2:** This version does not analyse state-level electoral laws in Mexico or local participation mechanisms in Costa Rica.
- **Jurisprudence is selective:** Phase 1 includes key IACtHR judgments and thematic compilations from TEPJF and TSE. It is not a complete jurisprudence survey.
- **No empirical data:** The project does not measure actual use rates, citizen awareness, institutional compliance rates, or political obstacles to mechanism use.
- **AI-assisted outputs are preliminary:** All classifications, extractions, and scale codings require expert legal validation before they can be relied upon.
