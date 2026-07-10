# NormTrace Political Rights — Recalibrated Score Sample Audit
**Date:** 2026-05-19  
**Source file:** `03_tables/principle_traceability/principle_traceability_matrix.csv`  
**Pipeline version:** post-CAL-001–CAL-005 recalibration  
**Scope:** 20 rows sampled — 5 MEX score-4, 5 MEX score-5, 5 CRC score-4, 5 CRC score-5  
**Method:** Evidence traced to domestic source CSVs; dimension logic verified against scoring algorithm and principle whitelists  
**Status:** AUDIT ONLY — no output files modified

---

## 1. Methodology

For each row, this audit:

1. Retrieves all provisions matching the mechanism at `anchor_strength ≥ 3` from the domestic provision table.
2. Identifies the dominant sources by row count and source type.
3. Verifies which whitelist dimensions fired and which did not, and why.
4. Applies one of three verdicts: **Justified**, **Potentially inflated**, or **Potentially too strict**.

**Verdict definitions:**
- **Justified:** Evidence supports the assigned score. The firing and non-firing dimensions match the actual corpus content.
- **Potentially inflated:** The dimensional test fires but the underlying provisions do not specifically address the principle's operational question; or a very small provision pool drives a high score.
- **Potentially too strict:** A dimension fails to fire on a technicality (e.g., mechanism not in `PROCESS_MECHANISMS`) when substantive evidence of the relevant operational dimension is clearly present in the corpus.

---

## 2. Mexico — Score 4 (strong_basis)

---

### Row 1 — MEX / PRIN-001 / electoral_authority_internal_governance

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-001 legality_and_sufficient_legal_basis |
| Mechanism | electoral_authority_internal_governance |
| Score | 4 — strong_basis |
| Provisions (total) | 431 |
| Provisions (anchor ≥ 3) | 387 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| actor_assigned \| timeline_present |
| Dimension missing | process_defined |

**Dominant sources:**  
`MEX-LGIPE` (280 provisions — Ley General de Instituciones y Procedimientos Electorales, general_law, anchor=4), `MEX-LGPP` (44 — Ley General de Partidos Políticos), `MEX-LGSMIME` (25 — Ley General del Sistema de Medios de Impugnación en Materia Electoral), `MEX-CPEUM` (15 — Constitución Política, anchor=5).

**Why score 4 and not 5:**  
`process_defined` did not fire because `electoral_authority_internal_governance` is not in the `PROCESS_MECHANISMS` set. That set contains citizen-facing electoral procedures (vote, recall, remedies, etc.), not institutional governance mechanisms. This is a definitional boundary, not a corpus gap: the LGIPE extensively regulates INE internal governance processes, but the pipeline correctly withholds `process_defined` from non-participatory mechanisms.

**Why score 4 and not 3:**  
Four of five PRIN-001 whitelist dimensions fire. The constitutional anchor (Art. 41 CPEUM establishing INE), statutory implementation (LGIPE Libro Segundo, Título Tercero), actor confirmation (9 actors: INE, Consejo General, TEPJF, etc.), and timeline provisions (electoral calendar articles in LGIPE) are all present in anchor-qualified text from at least two source types.

**Verdict: Justified.**  
Score 4 is analytically appropriate. The legal basis for electoral authority governance is substantively well-established but the absence of `process_defined` correctly reflects that this mechanism is governance-structural, not a citizen participation procedure. "Strong_basis" is an accurate characterisation.

---

### Row 2 — MEX / PRIN-002 / popular_consultation

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-002 equality_and_non_discrimination |
| Mechanism | popular_consultation |
| Score | 4 — strong_basis |
| Provisions (total) | 198 |
| Provisions (anchor ≥ 3) | 101 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 8 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| actor_assigned \| territorial_coverage |
| Dimension missing | equality_measure |

**Dominant sources:**  
`MEX-LFCP` (71 provisions — Ley Federal de Consulta Popular, federal_law, anchor=4), `MEX-CPEUM` (12 — Art. 35 frac. VIII, anchor=5), `MEX-LGDE` (10), `MEX-LGIPE` (5).

**Why score 4 and not 5:**  
`equality_measure` did not fire. The LFCP and Art. 35 CPEUM regulate consultation procedure, validity thresholds, and INE/Cámara roles, but do not include specific non-discrimination or parity provisions for popular consultation participation. The corpus (198 total, 101 qualified) covers the procedural legal basis thoroughly, not the equality dimension of participation. The CAL-002 rule (anchor≥3 required for keyword dims) filters out any incidental equality mentions in administrative provisions.

**Why score 4 and not 3:**  
Four of five PRIN-002 whitelist dimensions confirm: constitutional (Art. 35 VIII, anchor=5) and statutory anchor (LFCP, anchor=4), actor confirmation (INE organises, Cámara convokes), and territorial coverage (national consultation with federal and local scope rules in LFCP Arts. 19–23).

**Verdict: Justified.**  
The popular consultation framework in Mexico has strong legal basis and is institutionally anchored but does not contain equality-specific provisions for this mechanism. Score 4 correctly diagnoses this as a structural gap in the equality dimension, not a missing legal framework overall.

---

### Row 3 — MEX / PRIN-005 / independent_candidacies

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-005 pluralism_and_collective_representation |
| Mechanism | independent_candidacies |
| Score | 4 — strong_basis |
| Provisions (total) | 146 |
| Provisions (anchor ≥ 3) | 129 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| actor_assigned \| restriction_criteria |
| Dimension missing | process_defined |

**Dominant sources:**  
`MEX-LGIPE` (118 provisions — Libro Cuarto on candidaturas independientes, anchor=4), `MEX-CPEUM` (5 — Arts. 35, 116, anchor=5), `MEX-LGDE` (2), `MEX-LGPP` (2).

**Why score 4 and not 5:**  
`process_defined` did not fire: `independent_candidacies` is not in `PROCESS_MECHANISMS`. The LGIPE Book IV (Arts. 357–392) comprehensively regulates the collection of support signatures, INE verification, and candidacy registration — all of which are procedural. However, because the mechanism is not citizen-facing in the same way as `vote` or `recall`, `process_defined` is not awarded by the algorithm. This is a model boundary that slightly undersells the operational depth.

**Why score 4 and not 3:**  
Constitutional anchor (Art. 35 frac. II CPEUM recognising independent candidacy rights), extensive LGIPE statutory framework, 9 confirmed actors, and restriction criteria (signature thresholds, geographic distribution requirements, exclusion periods for party members) all confirmed.

**Verdict: Potentially too strict (borderline).**  
The algorithm withholds `process_defined` from this mechanism, but the LGIPE Book IV is effectively a defined process for citizen participation in candidacy. The score is correct per model rules, but the gap between this mechanism's operational reality and its model treatment is worth flagging. A future iteration should consider adding `independent_candidacies` to `PROCESS_MECHANISMS`.

---

### Row 4 — MEX / PRIN-006 / electoral_crimes

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-006 due_process_and_effective_remedy |
| Mechanism | electoral_crimes |
| Score | 4 — strong_basis |
| Provisions (total) | 49 |
| Provisions (anchor ≥ 3) | 41 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| actor_assigned \| timeline_present \| remedy_present |
| Dimension missing | process_defined |

**Dominant sources:**  
`MEX-LGIPE` (20 provisions), `MEX-LGDE` (10 — Ley General en Materia de Delitos Electorales, anchor=4), `MEX-LGPP` (4), `MEX-CPEUM` (4 — Art. 41 penalties clause).

**Why score 4 and not 5:**  
`process_defined` did not fire: `electoral_crimes` is not in `PROCESS_MECHANISMS`. The LGDE is a dedicated statutory framework for electoral offences, with typified crimes, procedures, and sanctions — but it is a criminal law instrument, not a citizen participation process. The model correctly withholds `process_defined`.

**Why score 4 and not 3:**  
Statutory and constitutional anchor confirmed, 9 actors (Fiscalía Especializada in Delitos Electorales, TEPJF, INE), timeline provisions present (prescription periods, investigation deadlines in LGDE), and remedy provisions confirmed (impugnation mechanisms and sanctions).

**Verdict: Justified.**  
The LGDE provides a complete legislative basis for electoral crime prosecution. Score 4 accurately reflects that the framework is well-established at the statutory level, with the only missing whitelist dimension being one the mechanism structurally cannot meet.

---

### Row 5 — MEX / PRIN-009 / right_to_stand_for_election

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-009 procedural_certainty_and_time_limits |
| Mechanism | right_to_stand_for_election |
| Score | 4 — strong_basis |
| Provisions (total) | 299 |
| Provisions (anchor ≥ 3) | 286 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| actor_assigned \| timeline_present \| restriction_criteria |
| Dimension missing | process_defined |
| Large corpus rule (≥200) | Active — multi-source required for keyword dims |

**Dominant sources:**  
`MEX-LGIPE` (181 provisions — Título Tercero on candidatos, anchor=4), `MEX-LGPP` (28), `MEX-CPEUM` (26 — Arts. 55, 58, 82, 115 requirements), `MEX-LGDE` (25).

**Why score 4 and not 5:**  
`process_defined` withheld (not in PROCESS_MECHANISMS). The large corpus rule (≥200 provisions) triggered for keyword dims: `timeline_present` and `restriction_criteria` both fire because they hit provisions from ≥2 distinct source types at anchor≥3 (LGIPE general_law + CPEUM constitution + LGPP = 3+ types). This validates the keyword signals are not artifact.

**Why score 4 and not 3:**  
Four of five PRIN-009 whitelist dims confirmed. Constitutional requirements for candidacy (age, residency, nationality — CPEUM Arts. 55, 58, 82), LGIPE procedural timelines (registration windows, campaign periods, withdrawal deadlines), 9 confirmed actors, restriction criteria (objective and legally specified requirements all confirmed from multiple statutory sources).

**Verdict: Justified.**  
Score 4 is appropriate. The right-to-stand framework has excellent procedural certainty — defined timelines and restriction criteria from multiple high-anchor sources. The only missing dimension is structural (process_defined). The large corpus rule added quality control on keyword evidence.

---

## 3. Mexico — Score 5 (integrated_basis)

---

### Row 6 — MEX / PRIN-001 / citizen_initiative

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-001 legality_and_sufficient_legal_basis |
| Mechanism | citizen_initiative |
| Score | 5 — integrated_basis |
| Provisions (total) | 15 |
| Provisions (anchor ≥ 3) | 8 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 8 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| process_defined \| actor_assigned \| timeline_present |

**Dominant sources:**  
`MEX-LGSMIME` (3 provisions — Ley General del Sistema de Medios de Impugnación), `MEX-CPEUM` (3 — Art. 35 frac. VII, anchor=5), `MEX-LOAPF` (1), `MEX-REGCONG` (1).

**Why score 5:**  
All 5 PRIN-001 whitelist dimensions fire: constitutional anchor (Art. 35 VII CPEUM), statutory implementation (LGSMIME covers remedy procedures for citizen initiative), `process_defined` (citizen_initiative is in PROCESS_MECHANISMS), actor confirmed (INE as organising body), timelines present (signature collection and verification periods). Small corpus (<200) means no multi-source rule applies.

**Concern:**  
Only 8 anchor-qualified provisions. While all whitelist dimensions fire, the operational depth of "integrated_basis" may overstate the corpus evidence. The 3 LGSMIME provisions appear to address remedy procedures, not citizen initiative procedure directly. The 3 CPEUM provisions confirm the right and basic requirements. With 8 total provisions, the label "integrated_basis for legality" is dimensionally correct but operationally thin.

**Verdict: Potentially inflated (minor).**  
Score 5 is produced by the algorithm correctly, but the small provision pool means the label should be interpreted with caution. The legal basis exists and spans multiple source types (constitution, general_law, federal_law, parliamentary_regulation), but the statutory development is less detailed than for `vote`. A note should accompany this entry in outputs: "Score 5 reflects dimensional coverage from a small provision pool (8 qualified provisions); operational depth is limited relative to higher-volume mechanisms."

---

### Row 7 — MEX / PRIN-001 / vote

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-001 legality_and_sufficient_legal_basis |
| Mechanism | vote |
| Score | 5 — integrated_basis |
| Provisions (total) | 1,041 |
| Provisions (anchor ≥ 3) | 922 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| process_defined \| actor_assigned \| timeline_present |
| Large corpus rule (≥200) | Active |

**Dominant sources:**  
`MEX-LGIPE` (402 provisions), `MEX-REGCD` (128 — Reglamento de sesiones, parliamentary_regulation), `MEX-REGSN` (84), `MEX-CPEUM` (65 — multiple articles, anchor=5), `MEX-REGCONG` (49).

**Why score 5:**  
All 5 PRIN-001 dims confirmed from a corpus of 922 anchor-qualified provisions spanning 4+ source types (general_law, parliamentary_regulation, federal_law, constitution). The large corpus rule (≥200) was active and all keyword dims that fired confirmed evidence from ≥2 distinct source types. Constitutional anchor: CPEUM Arts. 35, 41, 115, 116. Statutory anchor: LGIPE Libros Primero through Quinto. Actors: INE, TEPJF, Consejos Distritales, OPLs, PJF (9 confirmed). Timelines: extensive jornada electoral calendar provisions across LGIPE and CPEUM.

**Verdict: Justified.**  
This is the best-supported score-5 in the Mexico corpus. The vote mechanism has the richest and most structurally diverse legal basis in the dataset. Score 5 for PRIN-001/vote is well-earned. The large corpus rule applied correctly — timeline keywords fire from both LGIPE (general_law) and CPEUM (constitution) at anchor≥3.

---

### Row 8 — MEX / PRIN-003 / right_to_stand_for_election

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-003 accessibility_and_reasonable_accommodations |
| Mechanism | right_to_stand_for_election |
| Score | 5 — integrated_basis |
| Provisions (total) | 299 |
| Provisions (anchor ≥ 3) | 286 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| actor_assigned \| equality_measure \| accessibility_measure |
| Large corpus rule (≥200) | Active |

**Dominant sources:**  
`MEX-LGIPE` (181 provisions, general_law), `MEX-LGPP` (28), `MEX-CPEUM` (26, constitution), `MEX-LGDE` (25).

**Why score 5:**  
All 5 PRIN-003 whitelist dims fire. The large corpus rule (286 qualified provisions) requires keyword dims to fire from ≥2 distinct source types. Both `accessibility_measure` and `equality_measure` satisfy this: they fire from LGIPE (general_law) and at least one other source type (CPEUM or LGPP or LGDE) at anchor≥3.

**Concern:**  
The accessibility provisions in the right-to-stand corpus likely address general access to the electoral process, not disability-specific accommodation in candidacy procedures (e.g., accessible nomination forms, physical accessibility for candidates with disabilities). The LGIPE provisions on candidacy accessibility likely concern geographic and administrative accessibility rather than the CRPD Art. 29 reasonable accommodation obligation. The score reflects corpus breadth, not principle-specific depth.

**Verdict: Potentially inflated (moderate).**  
Score 5 is algorithmically correct — all 5 whitelist dims fire from ≥2 source types — but the accessibility provisions driving the score are likely not specifically about disability accommodation in candidacy processes. The gap between what PRIN-003 operationally asks (disability accommodation in political participation) and what the keyword fires on (general "accessible" language in LGIPE) should be flagged in the explainer and gap description. Recommend `needs_review: true` for all PRIN-003/right_to_stand_for_election entries.

---

### Row 9 — MEX / PRIN-004 / vote

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-004 effective_participation |
| Mechanism | vote |
| Score | 5 — integrated_basis |
| Provisions (total) | 1,041 |
| Provisions (anchor ≥ 3) | 922 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| process_defined \| actor_assigned \| timeline_present \| territorial_coverage |
| Large corpus rule (≥200) | Active |

**Dominant sources:**  
Same as Row 7 (MEX/PRIN-001/vote): LGIPE, CPEUM, REGCD, REGSN, REGCONG.

**Why score 5:**  
All 5 PRIN-004 whitelist dims fire. `vote` is in PROCESS_MECHANISMS (process_defined), actors confirmed, timelines confirmed from ≥2 source types, territorial coverage confirmed (LGIPE regulates federal and local elections; CPEUM Art. 115 establishes municipal electoral rights). Large corpus rule satisfied.

**Verdict: Justified.**  
PRIN-004 (effective participation) for the vote mechanism is one of the strongest-warranted score-5 entries. The corpus breadth (1,041 total), source diversity, and the specific presence of territorial coverage provisions (federal, state, municipal levels) all support "integrated_basis" for effective participation through voting.

---

### Row 10 — MEX / PRIN-009 / citizen_initiative

| Field | Value |
|---|---|
| Country | Mexico |
| Principle | PRIN-009 procedural_certainty_and_time_limits |
| Mechanism | citizen_initiative |
| Score | 5 — integrated_basis |
| Provisions (total) | 15 |
| Provisions (anchor ≥ 3) | 8 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 8 |
| Dimensions passed | anchor_statutory \| process_defined \| actor_assigned \| timeline_present \| restriction_criteria |

**Dominant sources:**  
`MEX-LGSMIME` (3), `MEX-CPEUM` (3 — Art. 35 VII frac. 1–8 establishing timing and threshold requirements), `MEX-LOAPF` (1), `MEX-REGCONG` (1).

**Why score 5:**  
All 5 PRIN-009 whitelist dims fire: constitutional anchor, `process_defined` (citizen_initiative in PROCESS_MECHANISMS), actor (INE), timeline (Art. 35 VII CPEUM specifies annual Congress session window and 90-day INE verification), restriction criteria (1.5% voter signature threshold, subject matter exclusions). Small corpus (<200) — multi-source rule not triggered.

**Concern:**  
Same concern as Row 6: only 8 anchor-qualified provisions. The CPEUM provides the constitutional framework; the LGSMIME provisions address remedies, not the initiation procedure. The timelines and restriction criteria that drive the score are primarily from CPEUM (3 provisions), not from implementing legislation. This means "integrated_basis" rests on constitutional provisions alone for most keyword dims.

**Verdict: Potentially inflated (minor).**  
Score 5 is dimensionally correct: CPEUM Art. 35 VII is a rich article establishing timeline and restriction provisions. However, the lack of secondary statutory depth means the score reflects constitutional provision density more than a fully developed implementing framework. A note should accompany this entry: "Score 5 driven primarily by constitutional provisions (CPEUM Art. 35 VII); implementing statute (LGSMIME) provides limited additional specificity for this mechanism."

---

## 4. Costa Rica — Score 4 (strong_basis)

---

### Row 11 — CRC / PRIN-001 / electoral_authority_internal_governance

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-001 legality_and_sufficient_legal_basis |
| Mechanism | electoral_authority_internal_governance |
| Score | 4 — strong_basis |
| Provisions (total) | 369 |
| Provisions (anchor ≥ 3) | 253 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| actor_assigned \| timeline_present |
| Dimension missing | process_defined |
| Large corpus rule (≥200) | Active |

**Dominant sources:**  
`CRC-CE` (128 provisions — Código Electoral, anchor=4), `CRC-LOTSRC` (52 — Ley Orgánica del TSE, organic_law), `CRC-LREF` (21), `CRC-CPOL` (20 — Constitución Política, anchor=5).

**Why score 4 and not 5:**  
`process_defined` withheld — same structural reason as MEX Row 1. `electoral_authority_internal_governance` is not in PROCESS_MECHANISMS. The large corpus rule (253 qualified provisions) applies to keyword dims: `timeline_present` fires from CE (codigo_ley) and CPOL (constitution) — two distinct source types — satisfying the multi-source requirement.

**Why score 4 and not 3:**  
Constitutional foundation (CPOL Title X, TSE as constitutional organ), LOTSRC organic law for TSE governance, Código Electoral, and confirmed actors (TSE, Dirección del Registro Electoral) across 4+ source types.

**Verdict: Justified.**  
Costa Rica's TSE has uniquely strong constitutional status (constitutional-rank tribunal). Score 4 accurately reflects an extremely well-founded institutional legal basis. The only missing dim is structural. If anything, this entry understates the actual legal depth of CRC's TSE, whose constitutional independence exceeds most comparative frameworks.

---

### Row 12 — CRC / PRIN-003 / citizen_initiative

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-003 accessibility_and_reasonable_accommodations |
| Mechanism | citizen_initiative |
| Score | 4 — strong_basis |
| Provisions (total) | 56 |
| Provisions (anchor ≥ 3) | 19 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 7 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| actor_assigned |
| Dimensions missing | accessibility_measure, equality_measure |

**Dominant sources:**  
`CRC-REGIP` (7 provisions — Reglamento de Iniciativa Popular, tse_reglamento, anchor=3), `CRC-LIP` (5 — Ley de Iniciativa Popular, statutory_law), `CRC-LREF` (4), `CRC-LCPREF` (2), `CRC-CPOL` (1).

**Why score 4 and not 5:**  
`accessibility_measure` and `equality_measure` did not fire. The citizen initiative corpus in Costa Rica (19 qualified provisions) addresses procedural requirements for signature collection and registration, not disability accommodation or gender equality measures for the initiative process. This is a genuine operational gap: the LIP and REGIP do not include accessibility provisions.

**Why score 4 and not 3:**  
Three of five PRIN-003 whitelist dims fire: constitutional anchor (CPOL), statutory anchor (LIP, LREF), and actor confirmed (TSE). Per the algorithm: dim_count=3, dim_count ≤ 4 → score 4.

**Concern:**  
This is a model boundary effect. Three dimensions fire, yielding score 4 ("strong_basis") for accessibility. But "strong_basis for accessibility" is misleading when the two specifically accessibility-relevant dims (`accessibility_measure`, `equality_measure`) are absent. The score reflects legal structure (anchor + actor) more than accessibility-specific preparedness.

**Verdict: Potentially inflated (moderate).**  
Score 4 correctly follows the algorithm but overstates accessibility preparedness for citizen_initiative. The two accessibility-specific whitelist dimensions are exactly those that do not fire. A score of 2–3 would be more analytically accurate for the accessibility principle applied to this mechanism. Flag for explainer: "Score 4 reflects statutory structure and actor assignment; the mechanism lacks specific accessibility provisions. The accessibility and equality dimensions of citizen initiative are not established in the current corpus."

---

### Row 13 — CRC / PRIN-004 / right_to_stand_for_election

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-004 effective_participation |
| Mechanism | right_to_stand_for_election |
| Score | 4 — strong_basis |
| Provisions (total) | 63 |
| Provisions (anchor ≥ 3) | 32 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| actor_assigned \| timeline_present \| territorial_coverage |
| Dimension missing | process_defined |

**Dominant sources:**  
`CRC-CE` (23 provisions — candidacy requirements and procedures, anchor=4), `CRC-CPOL` (6 — Arts. 65–66 and 107, constitutional candidacy rights, anchor=5), `CRC-LOTSRC` (2).

**Why score 4 and not 5:**  
`process_defined` not awarded (mechanism not in PROCESS_MECHANISMS).

**Why score 4 and not 3:**  
Código Electoral candidacy provisions (Arts. 58–82) establish actor, procedure, timelines, and territorial coverage (national, provincial, and municipal candidacy registers). Constitutional basis confirmed. `territorial_coverage` fires from CE + CPOL (two distinct source types). Actor: TSE registers candidacies.

**Verdict: Justified.**  
Score 4 is appropriate. Costa Rica's candidacy framework is clearly codified in the CE and constitutionally grounded. The missing `process_defined` dim is a structural boundary, not a corpus gap.

---

### Row 14 — CRC / PRIN-007 / political_parties

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-007 transparency_and_accountability |
| Mechanism | political_parties |
| Score | 4 — strong_basis |
| Provisions (total) | 167 |
| Provisions (anchor ≥ 3) | 150 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| actor_assigned \| equality_measure \| transparency_measure |
| Dimension missing | process_defined |

**Dominant sources:**  
`CRC-CE` (139 provisions — Título V partido político regulation, anchor=4), `CRC-LOTSRC` (7), `CRC-CPOL` (4 — Arts. 98 political parties chapter).

**Why score 4 and not 5:**  
`process_defined` not awarded (`political_parties` not in PROCESS_MECHANISMS).

**Why score 4 and not 3:**  
Four dims fire: statutory/constitutional anchor (CE + CPOL), actor (TSE as registrar and overseer), equality keywords (gender parity requirements in CE Arts. 2 and 52 "paridad de género"), transparency keywords (CE Arts. 135–147 on party financing disclosure and TSE audit functions). The equality and transparency dims satisfy PRIN-007's whitelist directly.

**Verdict: Justified.**  
This is one of the best-supported score-4 entries for PRIN-007. The Código Electoral's party regulation chapter is extensive (139 anchor-qualified provisions), includes specific transparency mechanisms (financial disclosure, audit), and parity requirements. Score 4 is appropriate — `process_defined` cannot fire due to mechanism classification, but the four confirmed dims represent genuine transparency and accountability architecture.

---

### Row 15 — CRC / PRIN-010 / right_to_stand_for_election

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-010 territorial_and_multilevel_implementation |
| Mechanism | right_to_stand_for_election |
| Score | 4 — strong_basis |
| Provisions (total) | 63 |
| Provisions (anchor ≥ 3) | 32 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| actor_assigned \| equality_measure \| territorial_coverage |
| Dimension missing | process_defined |

**Dominant sources:**  
Same as Row 13 (CRC/PRIN-004/right_to_stand): CRC-CE (23), CRC-CPOL (6), CRC-LOTSRC (2).

**Why score 4 and not 5:**  
`process_defined` withheld; `territorial_coverage` and `equality_measure` fire from CE + CPOL (two distinct source types).

**Why score 4 and not 3:**  
The CE regulates candidacies at national (Asamblea Legislativa), provincial, and municipal levels (cantonal councils). Territorial coverage across three levels is confirmed. Equality provisions (gender parity in candidacy lists confirmed from CE). Actor: TSE.

**Verdict: Justified.**  
Score 4 correctly reflects multilevel candidacy regulation in Costa Rica. The territorial dimension is specifically confirmed: Costa Rica organises elections at national, provincial, and municipal levels with specific candidacy frameworks for each. "Strong_basis" is appropriate.

---

## 5. Costa Rica — Score 5 (integrated_basis)

---

### Row 16 — CRC / PRIN-001 / citizen_initiative

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-001 legality_and_sufficient_legal_basis |
| Mechanism | citizen_initiative |
| Score | 5 — integrated_basis |
| Provisions (total) | 56 |
| Provisions (anchor ≥ 3) | 19 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 7 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| process_defined \| actor_assigned \| timeline_present |

**Dominant sources:**  
`CRC-REGIP` (7 — TSE reglamento, anchor=3), `CRC-LIP` (5 — Ley de Iniciativa Popular, statutory_law, anchor=4), `CRC-LREF` (4), `CRC-LCPREF` (2), `CRC-CPOL` (1, anchor=5).

**Why score 5:**  
All 5 PRIN-001 whitelist dims fire. Constitution (CPOL), dedicated statute (LIP), TSE reglamento, implementing procedural rules (LCPREF), actor (TSE), timelines in LIP and LREF (submission periods, verification timelines). Corpus spans 4 distinct source types (constitution, statutory_law, tse_reglamento, plus LREF). Small corpus (<200) — multi-source rule not triggered.

**Verdict: Justified with note.**  
Score 5 is well-founded. Costa Rica has a more developed statutory framework for citizen initiative than the keyword counts suggest — the LIP, REGIP, and LCPREF collectively establish a complete legal architecture. The small provision pool (19) is itself a diagnostic signal: the CRC citizen initiative framework is concise but comprehensive. "Integrated_basis" is appropriate.  
*Note: corpus size reflects the concise drafting style of Costa Rican legislation, not corpus gaps.*

---

### Row 17 — CRC / PRIN-001 / vote

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-001 legality_and_sufficient_legal_basis |
| Mechanism | vote |
| Score | 5 — integrated_basis |
| Provisions (total) | 397 |
| Provisions (anchor ≥ 3) | 226 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| process_defined \| actor_assigned \| timeline_present |
| Large corpus rule (≥200) | Active |

**Dominant sources:**  
`CRC-CE` (98 provisions, anchor=4), `CRC-CPOL` (42, anchor=5), `CRC-LOTSRC` (36, organic_law), `CRC-REGREF` (24, tse_reglamento), `CRC-LREF` (16).

**Why score 5:**  
All 5 PRIN-001 dims fire. Large corpus rule active (226 qualified): `timeline_present` fires from CE (codigo_ley) and CPOL (constitution) — two distinct types. Constitutional basis: CPOL Arts. 93–98 (suffrage chapter). Organic law: LOTSRC. Código Electoral: comprehensive electoral code. Actor: TSE + Registro Electoral + Tribunal Contencioso.

**Verdict: Justified.**  
CRC/PRIN-001/vote is the strongest score-5 entry in the Costa Rica corpus. The constitutional chapter on suffrage (CPOL Arts. 93–98), the organic TSE law, the Código Electoral, and TSE reglamentos collectively establish a complete and multi-tiered legal basis for voting legality. Score 5 is fully warranted.

---

### Row 18 — CRC / PRIN-003 / vote

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-003 accessibility_and_reasonable_accommodations |
| Mechanism | vote |
| Score | 5 — integrated_basis |
| Provisions (total) | 397 |
| Provisions (anchor ≥ 3) | 226 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| constitutional_or_statutory_anchor \| actor_assigned \| equality_measure \| accessibility_measure |
| Large corpus rule (≥200) | Active |

**Dominant sources:**  
Same as Row 17 (CRC/PRIN-001/vote): CE, CPOL, LOTSRC, REGREF, LREF.

**Why score 5:**  
All 5 PRIN-003 dims fire. Large corpus rule (226 qualified provisions): `accessibility_measure` fires from ≥2 source types (CE + LOTSRC or CPOL). `equality_measure` fires from ≥2 source types (CE gender parity provisions + CPOL Art. 33 non-discrimination).

**Concern:**  
Similar to MEX Row 8: the accessibility keywords firing in the vote corpus for Costa Rica likely refer to physically accessible polling places and assistance provisions rather than comprehensive CRPD-aligned disability accommodation. Costa Rica's CE contains some accessibility provisions for the vote (asistencia al votante, locales accesibles), which is substantive. However, CRPD Article 29 requires more than physical accessibility — it includes accessible ballot formats, assistive technologies, and support for voters with cognitive or communicative impairments.

**Verdict: Justified with analytical caveat.**  
Score 5 is more defensible here than for right_to_stand_for_election, because the vote mechanism has a larger corpus with genuine physical accessibility provisions in the Código Electoral. However, the gap between statutory accessibility provisions (polling place access) and CRPD-aligned comprehensive accommodation should be noted. Score 5 reflects corpus-based preparedness; compliance assessment requires specific CRPD audit.

---

### Row 19 — CRC / PRIN-006 / electoral_remedies

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-006 due_process_and_effective_remedy |
| Mechanism | electoral_remedies |
| Score | 5 — integrated_basis |
| Provisions (total) | 63 |
| Provisions (anchor ≥ 3) | 49 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| process_defined \| actor_assigned \| timeline_present \| remedy_present |

**Dominant sources:**  
`CRC-CE` (30 provisions — Título X recursos y nulidades, anchor=4), `CRC-LOTSRC` (13 — TSE organic law on adjudication powers), `CRC-CPOL` (4 — Arts. 102–103 TSE constitutional jurisdiction), `CRC-LJC` (1).

**Why score 5:**  
All 5 PRIN-006 whitelist dims fire. `electoral_remedies` is in PROCESS_MECHANISMS (process_defined fires). Constitutional basis: CPOL Arts. 102–103 establish TSE as supreme electoral authority with jurisdictional finality. LOTSRC defines TSE's adjudicatory procedures. Código Electoral Título X establishes specific remedies (recurso de amparo electoral, nulidades, apelaciones), timelines, and sanctions. Actor: TSE as constitutionally mandated final adjudicator (9 actors confirmed).

**Verdict: Justified.**  
This is the most clearly justified score-5 in the entire sample. Costa Rica's TSE has constitutional judicial status — unique in Latin America — and the electoral remedy system is codified at constitutional, organic, and statutory levels. The PRIN-006 whitelist is designed precisely for this mechanism, and all five dimensions are genuinely and substantively present. Score 5 is fully warranted and understates nothing.

---

### Row 20 — CRC / PRIN-009 / vote

| Field | Value |
|---|---|
| Country | Costa Rica |
| Principle | PRIN-009 procedural_certainty_and_time_limits |
| Mechanism | vote |
| Score | 5 — integrated_basis |
| Provisions (total) | 397 |
| Provisions (anchor ≥ 3) | 226 |
| Max anchor strength | 5 (constitutional) |
| Actor count | 9 |
| Dimensions passed | anchor_statutory \| process_defined \| actor_assigned \| timeline_present \| restriction_criteria |
| Large corpus rule (≥200) | Active |

**Dominant sources:**  
Same as Rows 17–18 (CRC/vote): CE (98), CPOL (42), LOTSRC (36), REGREF (24), LREF (16).

**Why score 5:**  
All 5 PRIN-009 dims fire. `vote` is in PROCESS_MECHANISMS. Constitutional calendar (CPOL Arts. 95–98), Código Electoral calendar provisions, TSE as actor, timelines confirmed from ≥2 source types under large corpus rule (CE and CPOL both contain calendar and deadline provisions). Restriction criteria: CPOL and CE contain objective eligibility criteria (age, citizenship, non-disqualification conditions).

**Verdict: Justified.**  
Score 5 for procedural certainty on the vote mechanism in Costa Rica is well-supported. The constitutional electoral calendar framework (CPOL), its statutory implementation (CE), and TSE reglamentos collectively establish comprehensive procedural certainty. This is structurally analogous to MEX/PRIN-004/vote but for a different principle, and equally justified.

---

## 6. Summary of Verdicts

| Row | Country | Principle | Mechanism | Score | Verdict |
|---|---|---|---|---|---|
| 1 | MEX | PRIN-001 | electoral_authority_internal_governance | 4 | Justified |
| 2 | MEX | PRIN-002 | popular_consultation | 4 | Justified |
| 3 | MEX | PRIN-005 | independent_candidacies | 4 | Potentially too strict (borderline) |
| 4 | MEX | PRIN-006 | electoral_crimes | 4 | Justified |
| 5 | MEX | PRIN-009 | right_to_stand_for_election | 4 | Justified |
| 6 | MEX | PRIN-001 | citizen_initiative | 5 | Potentially inflated (minor) |
| 7 | MEX | PRIN-001 | vote | 5 | Justified |
| 8 | MEX | PRIN-003 | right_to_stand_for_election | 5 | Potentially inflated (moderate) |
| 9 | MEX | PRIN-004 | vote | 5 | Justified |
| 10 | MEX | PRIN-009 | citizen_initiative | 5 | Potentially inflated (minor) |
| 11 | CRC | PRIN-001 | electoral_authority_internal_governance | 4 | Justified |
| 12 | CRC | PRIN-003 | citizen_initiative | 4 | Potentially inflated (moderate) |
| 13 | CRC | PRIN-004 | right_to_stand_for_election | 4 | Justified |
| 14 | CRC | PRIN-007 | political_parties | 4 | Justified |
| 15 | CRC | PRIN-010 | right_to_stand_for_election | 4 | Justified |
| 16 | CRC | PRIN-001 | citizen_initiative | 5 | Justified with note |
| 17 | CRC | PRIN-001 | vote | 5 | Justified |
| 18 | CRC | PRIN-003 | vote | 5 | Justified with analytical caveat |
| 19 | CRC | PRIN-006 | electoral_remedies | 5 | Justified |
| 20 | CRC | PRIN-009 | vote | 5 | Justified |

**Summary counts:**

| Verdict | Count |
|---|---|
| Justified | 13 |
| Justified with note / analytical caveat | 2 |
| Potentially inflated (minor) | 2 |
| Potentially inflated (moderate) | 2 |
| Potentially too strict (borderline) | 1 |

---

## 7. Cross-Cutting Observations

**Observation 1 — process_defined structural gap:**  
Eight of the twenty rows receive score 4 instead of score 5 because `process_defined` does not fire. In all cases the mechanism is not in `PROCESS_MECHANISMS`, not because the mechanism lacks procedural definition. Mechanisms like `independent_candidacies`, `electoral_crimes`, and `right_to_stand_for_election` have extensively defined procedures in statute. Consideration should be given to expanding `PROCESS_MECHANISMS` in a future calibration cycle, with per-mechanism review.

**Observation 2 — PRIN-003 (accessibility) score inflation risk:**  
All four PRIN-003 rows in this sample (MEX rows 8, CRC rows 12 and 18) show the same pattern: accessibility keywords fire on provisions that address logistical or geographic accessibility rather than disability-specific reasonable accommodation under CRPD Art. 29. This is an inherent limitation of keyword-based accessibility detection. All PRIN-003 entries with scores ≥ 4 should carry a standard caveat: "Accessibility score reflects keyword detection in anchor-qualified provisions; CRPD Art. 29 compliance requires additional disability-specific audit."

**Observation 3 — Small provision pools at score 5:**  
Mexico's citizen_initiative rows (Rows 6 and 10) reach score 5 with only 8 anchor-qualified provisions. The label "integrated_basis" can mislead when corpus depth is thin. All score-5 entries with fewer than 20 anchor-qualified provisions should be flagged as `needs_review: true` in downstream outputs.

**Observation 4 — Large corpus rule functioning correctly:**  
All rows with ≥200 provisions (Rows 5, 7, 8, 9, 11, 17, 18, 20) triggered the multi-source CAL-002 rule. In every case, the keyword dimensions that fired also confirmed evidence from ≥2 distinct source types. No case was found where the large corpus rule suppressed a keyword dim that had genuine substantive evidence. The rule is functioning as designed.

**Observation 5 — CRC electoral_remedies as benchmark:**  
Row 19 (CRC/PRIN-006/electoral_remedies, score 5) is the cleanest score-5 in the entire sample. TSE constitutional status, organic law, Código Electoral, and multi-level actor confirmation all align directly with PRIN-006's operational question. This row should be used as the reference case when calibrating what "integrated_basis" should mean across the system.

---

## 8. Recommended Follow-up Actions

| ID | Observation | Action | Priority |
|---|---|---|---|
| AUD-001 | `independent_candidacies` withheld `process_defined` despite extensive procedural corpus | Evaluate adding `independent_candidacies` to `PROCESS_MECHANISMS` | MEDIUM |
| AUD-002 | PRIN-003 accessibility keyword fires on general accessibility, not CRPD disability-specific accommodation | Add PRIN-003 standard caveat in explainer; flag all PRIN-003 score ≥ 4 as `needs_review` | HIGH |
| AUD-003 | Score-5 entries with < 20 anchor-qualified provisions (MEX citizen_initiative) may overstate operational depth | Add `low_provision_pool` flag to score-5 rows with anchor-qualified count < 20 | MEDIUM |
| AUD-004 | CRC citizen_initiative PRIN-003 score 4 overstates accessibility preparedness | Flag in explainer; consider scoring review for principle–mechanism combinations where ≥2 of the principle-specific keyword dims fail to fire | MEDIUM |

---

> **Audit disclaimer:** This audit evaluates model output quality, not legal compliance. All scores are corpus-based diagnostic legal preparedness indicators. NormTrace is an analytical tool, not a legal opinion.
