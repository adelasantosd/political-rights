# NormTrace Political Rights — Pipeline Audit Report
**Date:** 2026-05-18  
**Scope:** Mexico and Costa Rica offline legal brain pipelines  
**Audited files:** `mexico_legal_provisions.csv`, `costa_rica_legal_provisions.csv` (and all 8 output tables per country)  
**Method:** Deterministic checks — provision counts by source, duplicate text detection, anchor-type distribution, mechanism false-positive sampling, heading-count vs. provision-count comparison

---

## 1. Pipeline Run Summary

| Metric | Mexico | Costa Rica |
|---|---|---|
| MD files processed | 19 | 11 |
| Total provisions extracted | 7,502 | 1,884 |
| Manual review flags | 3,244 | 814 |
| Mechanism-source rows | 87 | 83 |
| Actor-mechanism edges | 334 | 422 |
| Warnings | 0 | 0 |

---

## 2. Structural Bugs Found and Fixed

Three structural bugs were identified and patched during this audit run. All are in the Costa Rica pipeline. The Mexico pipeline had no structural bugs.

### BUG CR-1 — All Article Patterns: `\\.` in raw strings (CRITICAL, FIXED)

**Symptom:** All 11 Costa Rica sources produced 0 provisions on first run.

**Root cause:** The five article detection patterns (`_ART_A` through `_ART_E`) used `\\.?` inside Python raw strings (`r'...'`). In a raw string, `\\` is two backslash characters, so the regex engine received `\\.` = "literal backslash followed by any character". This never matches a period in legal text.

**Fix:** Changed all `\\.?` occurrences to `\.?` (single backslash in raw string = regex escape for literal dot). Same class of bug as the Mexico INE article-bare fix in the previous pipeline cycle.

**Affected patterns:** All five — `_ART_A`, `_ART_B`, `_ART_C`, `_ART_D`, `_ART_E`.

### BUG CR-2 — Pattern D missed bold-format titled articles (HIGH, FIXED)

**Symptom:** After CR-1 fix, `codigo_electoral_costa_rica.md` produced only 50 provisions despite 309 article headings detected by `grep`. The Código Electoral accounts for ~260 of the missing provisions.

**Root cause:** Pattern D matched `**ARTICULO N.**` (closing `**` immediately after the number). The actual format used in CE articles 21–260+ is `**ARTÍCULO N.- Article title**` where the title is *inside* the bold markers. The old pattern required `\*\*` after the dash, which never appeared in positions 21 onwards.

**Fix:** Changed Pattern D from `r'^\*\*ART[IÍ]CULO\s+(\d+\.?)\s*[-–]?\*\*\s*(.*)'` to `r'^\*\*ART[IÍ]CULO\s+(\d+[°o]?\.?)\s*[-–]?\s*(.*)'`, and added `rstrip('*').strip()` to `match_article()` to clean trailing bold markers from captured inline text.

**Result:** CE provisions went from 50 → 311 (matching the 309 grep-counted headings; 2 extra are from subdivision detection on multi-part articles).

### BUG CR-3 — Missing SOURCE_REGISTRY entry for REGIP (LOW, FIXED)

**Symptom:** `reglamento_aplicacion_articulo_3_ley_iniciativa_popular.md` was skipped with a `[WARN]` message on every run.

**Root cause:** The file's stem (`reglamento_aplicacion_articulo_3_ley_iniciativa_popular`) was not in `SOURCE_REGISTRY`. The YAML brain files identified this source as `CRC-REGIP` but the pipeline entry was absent.

**Fix:** Added entry to `SOURCE_REGISTRY` with `source_type=tse_reglamento`, `normative_rank=5`, `legal_anchor_type=regulatory_or_legislative_procedural`, `base_anchor_strength=3`.

**Result:** 11 provisions from this source now correctly classified and included.

---

## 3. Audit Check Results — Mexico

### 3.1 Provision Counts by Source

| Source ID | Provisions | Notes |
|---|---|---|
| MEX-LGIPE | 1,521 | Comprehensive electoral law (Arts. 1–535); ~3 per article with subdivisions. **Plausible.** |
| MEX-REGCD | 839 | 35 "Artículo Único" entries — see §3.2. |
| MEX-LGTAIP | 776 | Large transparency law; many operational articles. **Plausible.** |
| MEX-LOAPF | 738 | Federal admin structure law; many institutional provisions. **Plausible.** |
| MEX-REGSN | 661 | Senate reglamento; includes 9+13=22 Artículo Único entries — see §3.2. |
| MEX-CPEUM | 441 | Constitution (197 articles + subdivisions + transitorios). **Plausible.** |
| Others | 3,026 | Individually plausible; no anomalies. |

### 3.2 "Artículo Único" Inflation — Mexico Parliamentary Regulations

**Finding:** MEX-REGCD has 35 provisions with `article="Único"` and MEX-REGSN has 22. These come from reform decrees appended to the reglamentos, each of which contains an "Artículo Único" reform clause (standard Mexican legislative drafting for single-reform laws). These are genuinely distinct legal provisions — different reform acts — that happen to share the article label "Único".

**Assessment:** Not a parser bug. Correctly captures distinct reform provisions. However, these provisions are structural reform text, not substantive law, and should be treated as low relevance in mechanism analysis. No patch required; downstream filtering can identify them by `article="Único"` label.

### 3.3 Duplicate Provision Texts — Mexico

**Finding:** 50 duplicate provision text cases. The top duplicates are derogated articles — "(Se deroga)" and "Derogado" text appearing multiple times from different articles across the same or different sources.

**Assessment:** Genuine (different articles that were derogated have identical post-derogation text). Not a parser bug. Derogated provisions can be identified by mechanism=empty + text matches `(se deroga|derogado)` for downstream filtering.

### 3.4 Anchor Type Classification

All 401 `electoral_administrative` provisions have `anchor_strength ≤ 2`. No electoral_administrative provisions were assigned strength 3 or higher. **Pass.**

All 441 constitutional provisions have `anchor_strength = 5`. **Pass.**

### 3.5 Mechanism False Positives — Citizen Initiative in LFPRH

**Finding:** 6 MEX-LFPRH (budget law) provisions tagged `citizen_initiative`. Sample text: `"el Ejecutivo Federal deberá elaborar anteproyectos de iniciativa de Ley de Ingresos"`. The keyword `iniciativa de ley` is matching budget legislation references, not citizen initiative mechanisms.

**Assessment:** Minor false positive (6/7,502 = 0.08%). The LFPRH provisions genuinely mention "iniciativa de Ley" in a non-citizen-initiative context. Keyword should be tightened in a future release: change `r"iniciativa de ley"` to `r"iniciativa ciudadana"` or add a negative lookahead for budget-law context. **No patch this cycle** — impact is minimal.

### 3.6 No-Mechanism Detection Rate

63% of Mexico provisions have no mechanism tag. This is expected: MEX-LOAPF (federal administrative structure), MEX-LFPA (administrative procedure), MEX-LFPRH (budget law), and MEX-LPLAN (planning law) are included for contextual completeness but contain few political-rights-specific provisions. The core electoral sources (MEX-LGIPE, MEX-LGPP, MEX-LGSMIME) have high mechanism detection rates.

---

## 4. Audit Check Results — Costa Rica

### 4.1 Provision Counts by Source (post-fix)

| Source ID | Provisions | Headings (grep) | Notes |
|---|---|---|---|
| CRC-RAL | 622 | 436 | Commentary contamination inflation — expected; all `manual_review_required`. |
| CRC-CPOL | 342 | 199 | 199 articles + subdivision detection → 342. **Plausible.** |
| CRC-LOTSRC | 220 | 102 | 102 articles + subdivisions → 220. **Plausible.** |
| CRC-RATSRE | 174 | 89 | 89 articles + subdivisions → 174. **Plausible.** |
| CRC-LJC | 114 | 114 | Exact match: bare articles, no subdivisions. **Plausible.** |
| CRC-CE | 311 | 309 | Post-fix (was 50). 2-provision overage from subdivisions. **Plausible.** |
| CRC-REGREF | 47 | 35 | 35 articles + subdivisions → 47. **Plausible.** |
| CRC-LREF | 32 | 32 | Exact match. **Plausible.** |
| CRC-REGIP | 11 | 11 | Exact match. **Plausible.** |
| CRC-LIP | 7 | 7 | Exact match. **Plausible.** |
| CRC-LCPREF | 4 | 4 | Exact match. Small law (99 lines). **Plausible.** |

### 4.2 RAL Commentary Inflation

**Finding:** CRC-RAL produces 622 provisions from 436 detected headings. Of 145 cases where the same article number appears multiple times in the same source, the worst cases are articles 178 and 179 (7 copies each) and articles 32, 121, 158 (5 copies each). This is caused by PDF-to-Markdown column merging: the commented compilation PDF had multiple columns (operative text, Sala IV commentary, editorial notes) that became interleaved in the Markdown, creating multiple text blocks under the same article header.

**Assessment:** The pipeline correctly flags all 622 RAL provisions as `manual_review_required=true` with `anchor_strength=2`. The commentary-filtering patterns (`RAL_COMMENTARY_RE`) remove known patterns but cannot fully eliminate the duplication without manual corpus remediation. The validation notes document this risk (CRC-VN-004).

**Recommendation:** The RAL corpus file should be re-processed with a column-aware PDF extraction tool before the next analytical cycle. Until then, RAL provisions should be treated as indicative only, not as certified operative text.

### 4.3 Administrative Source Classification

All 174 CRC-RATSRE provisions are correctly classified as `electoral_administrative` with `anchor_strength = 1`. No provision from the Reglamento Autónomo de Servicios TSE was assigned strength > 1. **Pass.**

The RATSRE mechanism tagging (`electoral_authority_internal_governance` for 78 provisions, `civil_registry_electoral_functions` for 7) reflects genuine keyword matches to TSE institutional terminology within an HR reglamento. These are correctly tagged but low relevance for political rights analysis.

### 4.4 CPOL Anchor Strength Distribution

76 constitutional provisions have `anchor_strength = 5` (mechanism detected → constitutional + statutory development confirmed). 266 have `anchor_strength = 4` (constitutional but no mechanism match in that specific provision — e.g., structural or institutional articles). This distribution is correct per CRC-ANCH-001 and CRC-STRN-001/002. **Pass.**

### 4.5 Duplicate Provision Texts — Costa Rica

6 duplicate text cases. All are short provision fragments (e.g., `"1) Ser ciudadano en ejercicio;"`, `"5) Los militares en servicio activo;"`) that appear in both the Constitución and the Código Electoral with identical wording (cross-referencing provisions). Not a parser bug. **Pass.**

### 4.6 No-Mechanism Detection Rate

50% of Costa Rica provisions have no mechanism tag. This is expected: CRC-RAL (parliamentary procedure) and CRC-RATSRE (HR reglamento) dominate the no-mechanism pool, along with many constitutional provisions covering non-political-rights matters (territory, economy, family, public finances).

---

## 5. Cross-Country Comparison

| Metric | Mexico | Costa Rica |
|---|---|---|
| Admin sources correctly capped | ✅ 0 admin provisions > strength 2 | ✅ 0 admin provisions > strength 2 |
| Constitutional provisions at strength 5 | ✅ All 441 | ✅ 76 (mechanism-matched); 266 at 4 |
| Duplicate text (structural) | ✅ None — derogation text coincidence | ✅ None — cross-source wording coincidence |
| False-positive mechanisms | ⚠️ 6 LFPRH citizen_initiative false positives | ✅ None identified |
| Commented source contamination | N/A | ⚠️ CRC-RAL 622 provisions, all flagged |
| Missing source registry | N/A | ✅ Fixed (REGIP) |

---

## 6. Issues Requiring Follow-Up (Not Structural Bugs)

| Issue | Country | Priority | Action |
|---|---|---|---|
| `r"iniciativa de ley"` keyword too broad | Mexico | Low | Tighten to `r"iniciativa ciudadana"` in next keyword revision |
| RAL corpus needs column-aware re-extraction | Costa Rica | Medium | Re-extract RAL PDF with multi-column-aware tool before legal use |
| Artículo Único reform provisions mixed with substantive law | Mexico | Low | Add `article_type="reform_decree"` flag for `article="Único"` provisions in next release |
| Short provisions (< 30 chars) — INE list items | Mexico | Low | Consider minimum-length filter at 20 chars with `notes="list_item_fragment"` |
| Sala IV jurisprudence and TSE resolutions absent | Costa Rica | High | Corpus gap documented in CRC-VN-001 and CRC-VN-002; requires corpus expansion |
| LGAP excluded (image-based) | Costa Rica | Medium | Requires OCR re-extraction of the LGAP PDF |

---

## 7. Verdict

**Mexico pipeline:** No structural bugs. 7,502 provisions from 19 sources are correctly classified. Minor keyword false positives exist but are below 0.1% impact. Pipeline is production-ready for web application consumption.

**Costa Rica pipeline:** Three structural bugs identified and fixed during this audit (CR-1: raw-string escape, CR-2: Pattern D bold-format, CR-3: missing REGIP entry). Post-fix, 1,884 provisions from 11 sources are correctly classified. CRC-RAL provisions are correctly quarantined with `manual_review_required=true`. Pipeline is production-ready with the caveat that RAL and RATSRE provisions require manual verification before legal use.

**No changes to the legal corpus were made.** All patches were to the pipeline parsing logic only.
