#!/usr/bin/env python3
"""
build_principle_traceability_explainer.py
NormTrace Political Rights — Principle Traceability Explainer Generator

Reads principle_traceability_matrix.csv and produces:
  - 03_tables/principle_traceability/principle_traceability_explainer.csv
  - 05_webapp/public/data/principle_traceability/principle_traceability_explainer.json

Schema:
  country;principle_id;principle_name;mechanism_id;mechanism_name;
  implementation_readiness_score;score_label;plain_language_interpretation;
  why_not_higher;review_priority;manual_review_required;notes

Rules:
  - Do not change scores.
  - Do not claim legal compliance.
  - Explain scores as diagnostic legal preparedness.
  - For score 0: distinguish mechanism absence, vocabulary mismatch, and corpus gap.
  - For score 4: name which single dimension prevents score 5 and why it did not fire.
  - For score 5: note integrated corpus evidence, not legal compliance.
  - PRIN-003 accessibility: distinguish disability-specific, language/cultural, digital,
    and generic access subdimensions. Apply CRPD Art. 29 caveat where relevant.
"""

import csv
import json
import sys
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent
MATRIX_PATH    = BASE / "03_tables" / "principle_traceability" / "principle_traceability_matrix.csv"
OUT_CSV        = BASE / "03_tables" / "principle_traceability" / "principle_traceability_explainer.csv"
OUT_JSON       = BASE / "05_webapp" / "public" / "data" / "principle_traceability" / "principle_traceability_explainer.json"

EXPLAINER_FIELDS = [
    "country", "principle_id", "principle_name", "mechanism_id", "mechanism_name",
    "implementation_readiness_score", "score_label",
    "plain_language_interpretation", "why_not_higher",
    "review_priority", "manual_review_required", "notes",
]

# ─── Label helpers ────────────────────────────────────────────────────────────

PRIN_SHORT = {
    "PRIN-001": "legality and legal basis",
    "PRIN-002": "equality and non-discrimination",
    "PRIN-003": "accessibility and disability accommodation",
    "PRIN-004": "effective participation",
    "PRIN-005": "pluralism and collective representation",
    "PRIN-006": "due process and effective remedy",
    "PRIN-007": "transparency and accountability",
    "PRIN-008": "institutional competence and independence",
    "PRIN-009": "procedural certainty and time limits",
    "PRIN-010": "territorial and multilevel implementation",
    "PRIN-011": "administrative capacity and resources",
    "PRIN-012": "restriction legality and proportionality",
}

MECH_LABEL = {
    "vote":                               "the right to vote",
    "right_to_stand_for_election":        "the right to stand for election (candidacy)",
    "political_parties":                  "political party regulation",
    "independent_candidacies":            "independent candidacies",
    "electoral_remedies":                 "electoral remedies and appeals",
    "constitutional_remedies":            "constitutional remedies (amparo/habeas corpus)",
    "electoral_authority_internal_governance": "electoral authority internal governance (INE/TSE)",
    "transparency_and_accountability":    "electoral transparency and accountability",
    "civil_registry_electoral_functions": "civil registry and electoral roll functions",
    "citizen_initiative":                 "citizen legislative initiative",
    "popular_consultation":               "popular consultation (referéndum/consulta)",
    "recall":                             "recall of elected officials",
    "referendum":                         "referendum mechanism",
    "electoral_crimes":                   "electoral crimes and sanctions",
    "civic_education_voter_information":  "civic education and voter information",
    "campaign_finance":                   "campaign finance regulation",
}

# Mechanisms where absence is more likely corpus gap than genuine absence
CORPUS_GAP_RISK = {"constitutional_remedies", "civic_education_voter_information"}

# Mechanisms where vocabulary mismatch between corpus and mechanism label is plausible
VOCAB_MISMATCH_RISK = {"referendum", "recall", "campaign_finance"}

# All accessibility subdimension names (post-REF-001 differentiation)
ACCESSIBILITY_DIMS = {
    "accessibility_measure",
    "accessibility_disability_specific",
    "accessibility_language_or_cultural",
    "accessibility_digital_or_informational",
    "accessibility_general_access",
}

# Principle dimension whitelists (must match build_principle_traceability_tables.py)
WHITELIST = {
    "PRIN-001": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "process_defined", "timeline_present", "actor_assigned"},
    "PRIN-002": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "equality_measure", "actor_assigned", "territorial_coverage"},
    "PRIN-003": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "accessibility_measure", "equality_measure", "actor_assigned"},
    "PRIN-004": {"anchor_statutory", "process_defined", "actor_assigned",
                 "timeline_present", "territorial_coverage"},
    "PRIN-005": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "process_defined", "actor_assigned", "restriction_criteria"},
    "PRIN-006": {"anchor_statutory", "process_defined", "actor_assigned",
                 "timeline_present", "remedy_present"},
    "PRIN-007": {"anchor_statutory", "actor_assigned", "process_defined",
                 "transparency_measure", "equality_measure"},
    "PRIN-008": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "actor_assigned", "process_defined", "timeline_present"},
    "PRIN-009": {"anchor_statutory", "process_defined", "timeline_present",
                 "actor_assigned", "restriction_criteria"},
    "PRIN-010": {"anchor_statutory", "process_defined", "actor_assigned",
                 "territorial_coverage", "equality_measure"},
    "PRIN-011": {"anchor_statutory", "actor_assigned", "process_defined",
                 "timeline_present", "territorial_coverage"},
    "PRIN-012": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "restriction_criteria", "equality_measure", "process_defined"},
}

MISSING_DIM_EXPLANATION = {
    "process_defined": (
        "The mechanism is not currently classified as a citizen-facing participatory procedure "
        "in the pipeline model. Substantive procedural provisions may exist in the corpus but the "
        "process dimension was not awarded by the mechanism classification rule."
    ),
    "actor_assigned": (
        "No institutionally designated actor was confirmed in the actor-mechanism edge table "
        "for this mechanism. Scores ≥ 3 require at least one confirmed actor (CAL-003 gate)."
    ),
    "timeline_present": (
        "No calendar, deadline, or time-limit provisions at anchor-strength ≥ 3 were confirmed "
        "in this mechanism's corpus for this principle (CAL-002: multi-source required for large corpora)."
    ),
    "territorial_coverage": (
        "No provisions confirming subnational, multilevel, or territorial implementation were "
        "found at anchor-strength ≥ 3."
    ),
    "remedy_present": (
        "No remedy, appeal, or accountability provisions were confirmed at anchor-strength ≥ 3 "
        "from the required source diversity."
    ),
    "equality_measure": (
        "No non-discrimination, parity, or special-measures provisions were found at "
        "anchor-strength ≥ 3 in this mechanism's corpus for this principle."
    ),
    "accessibility_measure": (
        "No disability-specific, language/cultural, or digital accessibility provisions were "
        "confirmed at anchor-strength ≥ 3. Generic 'accessible' language alone does not satisfy "
        "PRIN-003 requirements (CAL-REF-001: CRPD Art. 29 specificity rule)."
    ),
    "transparency_measure": (
        "No disclosure, audit, or public-information provisions were confirmed at "
        "anchor-strength ≥ 3 from the required source types."
    ),
    "restriction_criteria": (
        "No objective criteria governing permissible limitations were confirmed at "
        "anchor-strength ≥ 3."
    ),
    "constitutional_or_statutory_anchor": (
        "No provisions from constitution or organic/framework statute (anchor-strength ≥ 4) "
        "were found for this mechanism. The corpus contains only regulatory-level sources."
    ),
    "anchor_statutory": (
        "Provisions found are below anchor-strength 3 (administrative or reglamentary sources only), "
        "which is insufficient to confirm a statutory legal basis."
    ),
}

# CRPD Art. 29 caveat — appended to all PRIN-003 rows at score >= 3
PRIN003_CRPD_CAVEAT = (
    " Note: accessibility scores reflect keyword detection in anchor-qualified provisions and "
    "are a diagnostic indicator of corpus-based legal preparedness only. Full conformity with "
    "CRPD Article 29 (participation in political and public life) requires specific disability "
    "accommodation evidence beyond corpus presence and is subject to dedicated legal audit."
)

# Generic-access-only caveat for PRIN-003 score == 3 with cap applied
PRIN003_GENERIC_CAP_NOTE = (
    "Score capped at 3 (functional_basis): only generic 'accessible'/'accesib' language was "
    "detected at anchor-strength ≥ 3. Disability-specific, language/cultural, or digital "
    "accessibility evidence is required for score ≥ 4 under CAL-REF-001. "
    "Manual review required to determine whether substantive CRPD Art. 29 provisions exist "
    "under different vocabulary."
)


def _get_dims(row: dict) -> set:
    raw = row.get("dimension_checks_passed", "")
    return set(raw.split("|")) if raw else set()


def _get_missing(row: dict) -> list:
    prin_id = row["principle_id"]
    dims = _get_dims(row)
    whitelist = WHITELIST.get(prin_id, set())
    return [d for d in whitelist if d not in dims]


def _has_accessibility_specific(dims: set) -> bool:
    """True if any specific (non-generic) accessibility subdimension fired."""
    return bool(dims & {
        "accessibility_measure",
        "accessibility_disability_specific",
        "accessibility_language_or_cultural",
        "accessibility_digital_or_informational",
    })


def _has_accessibility_generic_only(dims: set) -> bool:
    """True if only generic access language fired, no specific subdimension."""
    has_specific = _has_accessibility_specific(dims)
    has_any = bool(dims & ACCESSIBILITY_DIMS)
    return has_any and not has_specific


def _accessibility_subdim_label(dims: set) -> str:
    """Return a human-readable label for which accessibility subdimension fired."""
    if "accessibility_disability_specific" in dims or "accessibility_measure" in dims:
        return "disability-specific or reasonable accommodation evidence"
    if "accessibility_language_or_cultural" in dims:
        return "indigenous-language or cultural accessibility evidence"
    if "accessibility_digital_or_informational" in dims:
        return "digital or informational accessible format evidence"
    if "accessibility_general_access" in dims:
        return "generic accessibility language (not disability-specific)"
    return "no accessibility evidence"


def build_plain_language(row: dict) -> dict:
    """Build the explainer fields for a single matrix row."""
    score      = int(row["implementation_readiness_score"])
    prin_id    = row["principle_id"]
    mech_id    = row["mechanism_id"]
    country    = row["country"]
    prov_count = int(row["matched_provision_count"])
    actor_count = int(row["actor_count"])
    anchor     = int(row["max_anchor_strength"])
    prin_short = PRIN_SHORT.get(prin_id, prin_id)
    mech_label = MECH_LABEL.get(mech_id, mech_id.replace("_", " "))
    dims       = _get_dims(row)
    missing    = _get_missing(row)

    interp = why = ""
    priority = "low"
    manual   = "false"
    notes    = ""

    # ── Score 0 ──────────────────────────────────────────────────────────────
    if score == 0:
        if prov_count == 0:
            if mech_id in CORPUS_GAP_RISK:
                interp = (
                    f"No provisions matching '{mech_label}' were found in the {country} corpus "
                    f"for {prin_short}. This likely reflects a corpus gap — the relevant legislation "
                    f"may use different terminology or may not yet be included in the provision table — "
                    f"rather than an actual absence of legal regulation."
                )
                why = (
                    "Score cannot rise above 0 without at least one matched provision. "
                    "Recommend verifying whether relevant legislation exists under a different "
                    "mechanism label or vocabulary in the domestic corpus."
                )
                priority = "medium"
            elif mech_id in VOCAB_MISMATCH_RISK:
                interp = (
                    f"No provisions tagged to '{mech_label}' were found in the {country} corpus "
                    f"for {prin_short}. This may reflect mechanism absence, a vocabulary mismatch "
                    f"in the domestic corpus tagging, or that this mechanism is not formally "
                    f"established in {country}'s current electoral legal framework."
                )
                why = (
                    "Score cannot rise above 0 without matched provisions. "
                    "Verify whether this mechanism is regulated under a different label in domestic law."
                )
                priority = "medium"
            else:
                interp = (
                    f"No provisions matching '{mech_label}' were found in the {country} corpus "
                    f"for {prin_short}. The mechanism appears absent from the corpus: it may not be "
                    f"legally formalised in {country}, may be regulated under a different label, or "
                    f"may not yet be included in the current provision table."
                )
                why = (
                    "Score cannot rise above 0 without at least one matched provision. "
                    "If the mechanism exists in domestic law under a different label, update corpus tagging."
                )
                priority = "low"
        else:
            interp = (
                f"Provisions matching '{mech_label}' were found ({prov_count} total) but none "
                f"reached the required anchor-strength level (≥ 3) for {prin_short}. The corpus "
                f"contains only administrative or reglamentary references to this mechanism, which "
                f"are insufficient to confirm a legal basis at the statutory or constitutional level."
            )
            why = (
                "Requires at least one provision at anchor-strength ≥ 3 (statutory or higher). "
                "Matched provisions are administrative sources only (anchor ≤ 2)."
            )
            priority = "high"
        manual = "true"
        notes  = "Score 0: mechanism absent or below anchor threshold. Diagnostic — not a legal finding."
        return _row(row, interp, why, priority, manual, notes)

    # ── Score 1 ──────────────────────────────────────────────────────────────
    if score == 1:
        interp = (
            f"The {country} corpus contains references to '{mech_label}' in the context of "
            f"{prin_short}, but all provisions are below the statutory anchor level "
            f"(anchor-strength ≤ 1: administrative or reglamentary sources only). The right exists "
            f"in declaratory form in the corpus but is not grounded in statute, organic law, or "
            f"constitution. This does not constitute an implementable legal basis."
        )
        why = (
            "Requires at least one provision from a statutory or higher source "
            "(anchor-strength ≥ 3) to advance beyond score 1."
        )
        priority = "high"
        manual   = "true"
        notes    = "Score 1: declaratory corpus presence only; no statutory or constitutional anchor confirmed."
        return _row(row, interp, why, priority, manual, notes)

    # ── Score 2 ──────────────────────────────────────────────────────────────
    if score == 2:
        actor_note = ""
        if actor_count == 0:
            actor_note = (
                " No institutionally designated actor was confirmed for this mechanism "
                "(CAL-003 actor gate: scores ≥ 3 require at least one confirmed actor)."
            )
        interp = (
            f"The {country} corpus contains statutory-level provisions ({prov_count} matched, "
            f"max anchor-strength={anchor}) establishing a partial legal basis for {prin_short} "
            f"in the context of {mech_label}.{actor_note} "
            f"The legal framework is present at the statutory level but lacks the dimensional "
            f"coverage needed to confirm a functional operational basis."
        )
        confirmed = ", ".join(sorted(dims)) if dims else "none confirmed"
        why = (
            f"Requires at least 2 of 5 whitelist dimensions to advance to score 3. "
            f"Confirmed: {confirmed}. "
            f"Missing: {', '.join(missing) or 'none'}."
        )
        priority = "high"
        manual   = "true"
        notes    = (
            f"Score 2: partial statutory basis; actor_count={actor_count}. "
            "Diagnostic legal preparedness indicator — not a compliance finding."
        )
        return _row(row, interp, why, priority, manual, notes)

    # ── Score 3 ──────────────────────────────────────────────────────────────
    if score == 3:
        # Special case: PRIN-003 with generic-access-only cap
        generic_capped = (
            prin_id == "PRIN-003"
            and _has_accessibility_generic_only(dims)
            and not _has_accessibility_specific(dims)
        )
        if generic_capped:
            interp = (
                f"The {country} corpus contains statutory-level provisions ({prov_count} matched, "
                f"max anchor-strength={anchor}) for '{mech_label}' that include generic accessibility "
                f"language ('accesib'/'accessible'). However, no disability-specific, language/cultural, "
                f"or digital accessibility evidence was confirmed at anchor-strength ≥ 3 under the "
                f"CRPD Art. 29 specificity requirement (CAL-REF-001). "
                f"The score is capped at 3 (functional_basis) pending human review to determine "
                f"whether substantive disability accommodation provisions exist in the corpus under "
                f"different vocabulary.{PRIN003_CRPD_CAVEAT}"
            )
            why = (
                "Score capped at 3 under CAL-REF-001: disability-specific, language/cultural, or "
                "digital accessibility evidence required for PRIN-003 score ≥ 4. Generic 'accessible' "
                "language alone does not satisfy the CRPD Art. 29 specificity standard."
            )
            priority = "medium"
            manual   = "true"
            notes    = PRIN003_GENERIC_CAP_NOTE
        else:
            missing_text = "; ".join(
                MISSING_DIM_EXPLANATION.get(d, d) for d in missing[:2]
            )
            interp = (
                f"The {country} corpus establishes a functional legal basis for {prin_short} "
                f"in the context of {mech_label}. The framework is grounded in statutory or higher "
                f"sources ({prov_count} matched provisions, max anchor={anchor}) and confirms "
                f"{len(dims)} of 5 required dimensions. The legal architecture is operable but "
                f"not yet fully developed across all relevant dimensions."
            )
            why = (
                f"Requires at least 4 of 5 whitelist dimensions for score 4. "
                f"Missing: {', '.join(missing)}. {missing_text}"
            )
            priority = "medium"
            manual   = "false"
            notes    = (
                f"Score 3: functional basis; {len(dims)}/5 whitelist dimensions confirmed. "
                "Diagnostic legal preparedness — not a compliance finding."
            )
        return _row(row, interp, why, priority, manual, notes)

    # ── Score 4 ──────────────────────────────────────────────────────────────
    if score == 4:
        confirmed_count = len(dims & WHITELIST.get(prin_id, set()))
        missing_dim = missing[0] if missing else "unknown"
        missing_expl = MISSING_DIM_EXPLANATION.get(missing_dim, f"Dimension '{missing_dim}' not confirmed.")

        # PRIN-003 accessibility subdimension label
        prin003_note = ""
        if prin_id == "PRIN-003":
            access_label = _accessibility_subdim_label(dims)
            prin003_note = (
                f" Accessibility evidence type detected: {access_label}."
                + PRIN003_CRPD_CAVEAT
            )

        interp = (
            f"The {country} corpus establishes a strong legal basis for {prin_short} in the "
            f"context of {mech_label}. The framework is grounded in "
            f"{'constitutional and statutory ' if anchor >= 5 else 'statutory '}"
            f"sources ({prov_count} matched provisions, max anchor-strength={anchor}) and confirms "
            f"{confirmed_count} of 5 principle-specific dimensions: "
            f"{', '.join(sorted(dims & WHITELIST.get(prin_id, set())))}. "
            f"This indicates a well-developed legal architecture with one operational gap in the "
            f"current corpus.{prin003_note}"
        )
        why = (
            f"Score 5 requires all 5 whitelist dimensions. "
            f"Missing dimension: '{missing_dim}'. {missing_expl}"
        )

        if prin_id == "PRIN-003":
            priority = "medium"
            manual   = "true"
        elif missing_dim == "process_defined":
            # Structural model boundary — not a corpus gap
            priority = "low"
            manual   = "false"
        else:
            priority = "low"
            manual   = "false"

        notes = (
            f"Score 4: strong basis; {confirmed_count}/5 whitelist dimensions confirmed; "
            f"missing: {missing_dim}. "
            "Diagnostic legal preparedness — not a compliance finding."
        )
        return _row(row, interp, why, priority, manual, notes)

    # ── Score 5 ──────────────────────────────────────────────────────────────
    if score == 5:
        confirmed_count = len(dims & WHITELIST.get(prin_id, set()))

        # Small provision pool flag (fewer than 20 anchor-qualified provisions)
        small_pool_note = ""
        if prov_count < 20:
            small_pool_note = (
                f" Caution: score 5 is based on a small provision pool ({prov_count} total "
                f"matched provisions). All 5 dimensions are confirmed but 'integrated_basis' "
                f"reflects dimensional coverage rather than deep operational corpus depth."
            )

        # PRIN-003 subdimension label + CRPD caveat
        prin003_note = ""
        if prin_id == "PRIN-003":
            access_label = _accessibility_subdim_label(dims)
            prin003_note = (
                f" Accessibility evidence type: {access_label}."
                + PRIN003_CRPD_CAVEAT
            )

        interp = (
            f"The {country} corpus establishes an integrated legal basis for {prin_short} "
            f"in the context of {mech_label}. All 5 principle-specific dimensions are confirmed "
            f"from {'constitutional, statutory, ' if anchor >= 5 else 'statutory '}"
            f"and implementing sources ({prov_count} matched provisions, max anchor={anchor}): "
            f"{', '.join(sorted(dims & WHITELIST.get(prin_id, set())))}. "
            f"Score 5 indicates comprehensive dimensional coverage in the current corpus. "
            f"It does not constitute a finding of legal compliance with international "
            f"obligations.{small_pool_note}{prin003_note}"
        )
        why = (
            "Score 5 is the maximum. All 5 whitelist dimensions are confirmed. "
            "Further improvement requires enhanced operational implementation, "
            "not additional legal text."
        )

        if prin_id == "PRIN-003":
            priority = "medium"
            manual   = "true"
        elif prov_count < 20:
            priority = "medium"
            manual   = "true"
        else:
            priority = "low"
            manual   = "false"

        notes = (
            f"Score 5: all {confirmed_count}/5 whitelist dimensions confirmed. "
            "Integrated corpus evidence — not legal compliance. "
            + ("Small provision pool: interpret with care. " if prov_count < 20 else "")
            + ("CRPD Art. 29 accessibility caveat applies. " if prin_id == "PRIN-003" else "")
        )
        return _row(row, interp, why, priority, manual, notes)

    # Fallback
    return _row(row, "Unknown score.", "", "low", "false", "")


def _row(source: dict, interp: str, why: str, priority: str,
         manual: str, notes: str) -> dict:
    return {
        "country":                        source["country"],
        "principle_id":                   source["principle_id"],
        "principle_name":                 source["principle_name"],
        "mechanism_id":                   source["mechanism_id"],
        "mechanism_name":                 source["mechanism_name"],
        "implementation_readiness_score": source["implementation_readiness_score"],
        "score_label":                    source["score_label"],
        "plain_language_interpretation":  interp,
        "why_not_higher":                 why,
        "review_priority":                priority,
        "manual_review_required":         manual,
        "notes":                          notes,
    }


# ─── I/O helpers ──────────────────────────────────────────────────────────────

def _read_csv(path: Path) -> list:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _write_csv(path: Path, rows: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EXPLAINER_FIELDS, delimiter=";")
        w.writeheader()
        w.writerows(rows)
    print(f"  [CSV] {path.relative_to(BASE)} — {len(rows)} rows")


def _write_json(path: Path, rows: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"explainer": rows}, f, ensure_ascii=False, indent=2)
    print(f"  [JSON] {path.relative_to(BASE)}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n=== NormTrace: Building Principle Traceability Explainer ===\n")

    if not MATRIX_PATH.exists():
        print(f"ERROR: matrix file not found: {MATRIX_PATH}", file=sys.stderr)
        sys.exit(1)

    matrix = _read_csv(MATRIX_PATH)
    print(f"Loaded {len(matrix)} rows from {MATRIX_PATH.relative_to(BASE)}")

    explainer_rows = [build_plain_language(row) for row in matrix]

    _write_csv(OUT_CSV, explainer_rows)
    _write_json(OUT_JSON, explainer_rows)

    # Summary
    from collections import Counter
    score_dist  = Counter(r["implementation_readiness_score"] for r in explainer_rows)
    prio_dist   = Counter(r["review_priority"] for r in explainer_rows)
    manual_dist = Counter(r["manual_review_required"] for r in explainer_rows)

    print(f"\nScore distribution: {dict(sorted(score_dist.items()))}")
    print(f"Review priority:    {dict(sorted(prio_dist.items()))}")
    print(f"Manual review:      {dict(manual_dist.items())}")
    print(f"\n=== Explainer complete — {len(explainer_rows)} rows ===\n")


if __name__ == "__main__":
    main()
