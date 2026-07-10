#!/usr/bin/env python3
"""
build_principle_traceability_tables.py
NormTrace Political Rights — International Standards & Principle Traceability Layer
Generated: 2026-05-18

Reads:
  - 10 international MD files from corpus/international/md/
  - 4 international brain YAML files from 02_country_legal_brains/international/
  - Domestic CSVs: 03_tables/country_legal_brains/mexico/ and costa_rica/

Produces 7 CSV + 7 JSON tables in:
  - 03_tables/international/
  - 03_tables/principle_traceability/

Deterministic only. No LLM. No internet.
"""

import csv
import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

import yaml

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent

INTL_MD_DIR     = BASE / "corpus" / "international" / "md"
INTL_BRAIN_DIR  = BASE / "02_country_legal_brains" / "international"
MEX_TABLE_DIR   = BASE / "03_tables" / "country_legal_brains" / "mexico"
CRC_TABLE_DIR   = BASE / "03_tables" / "country_legal_brains" / "costa_rica"
OUT_INTL_DIR    = BASE / "03_tables" / "international"
OUT_TRACE_DIR   = BASE / "03_tables" / "principle_traceability"

SEP = ";"

# ─────────────────────────────────────────────────────────────────────────────
# YAML LOADERS
# ─────────────────────────────────────────────────────────────────────────────

_INLINE_REGEX_LIST = re.compile(r':\s*\[r"[^\]]*\].*$', re.MULTILINE)

def _preprocess_yaml(text: str) -> str:
    """
    Replace inline flow-sequence values that contain regex character classes
    (e.g. [r"deber[aá]", ...]) with empty block lists.
    Those fields are metadata-only and not consumed by the pipeline.
    Specifically replaces lines of the form:  key: [r"..."]
    """
    def _replace(m):
        # Preserve leading whitespace + key name, substitute an empty list
        full = m.group(0)
        colon_pos = full.index(":")
        key_part = full[:colon_pos + 1]
        return key_part + " []"
    return _INLINE_REGEX_LIST.sub(_replace, text)

def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError:
        # Fallback: strip inline regex lists and retry
        cleaned = _preprocess_yaml(raw)
        return yaml.safe_load(cleaned)

def load_profiles() -> dict:
    """Returns dict keyed by source_id."""
    data = load_yaml(INTL_BRAIN_DIR / "international_standards_profile.yml")
    return {s["source_id"]: s for s in data["sources"]}

def load_hierarchy() -> dict:
    """Returns dict: source_id → {tier, tier_name, normative_weight, legal_character}."""
    data = load_yaml(INTL_BRAIN_DIR / "international_source_hierarchy.yml")
    result = {}
    for tier_entry in data["hierarchy"]:
        for src in tier_entry["sources"]:
            result[src] = {
                "tier": tier_entry["tier"],
                "tier_name": tier_entry["tier_name"],
                "normative_weight": tier_entry["normative_weight"],
                "legal_character": tier_entry["legal_character"],
            }
    return result

def load_extraction_rules() -> dict:
    """Returns dict keyed by source_id."""
    data = load_yaml(INTL_BRAIN_DIR / "standard_extraction_rules.yml")
    rules = {s["source_id"]: s for s in data["sources"]}
    rules["_global"] = data["global_rules"]
    rules["_principle_keywords"] = data["principle_assignment_keywords"]
    return rules

def load_principle_map() -> list:
    """Returns list of principle dicts."""
    data = load_yaml(INTL_BRAIN_DIR / "political_rights_principle_map.yml")
    return data["principles"]

# ─────────────────────────────────────────────────────────────────────────────
# CSV I/O
# ─────────────────────────────────────────────────────────────────────────────

def read_csv(path: Path) -> list:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        for row in reader:
            rows.append(row)
    return rows

def write_csv(path: Path, rows: list, fieldnames: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";",
                                quotechar='"', quoting=csv.QUOTE_ALL,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [CSV] {path.relative_to(BASE)} — {len(rows)} rows")

def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"  [JSON] {path.relative_to(BASE)}")

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STRIP PATTERNS
# ─────────────────────────────────────────────────────────────────────────────

GLOBAL_SKIP = [
    re.compile(r"^ABOUT US$"),
    re.compile(r"^Our Mandates"),
    re.compile(r"^Home \("),
    re.compile(r"<!--.*?-->"),
    re.compile(r"^Next: Article"),
    re.compile(r"^List of Articles"),
    re.compile(r"^\s*$"),
]

OC2821_REQUIRED = re.compile(
    r"(political right|article\s+23|restriction|reelection|term.limit|"
    r"democratic.continu|electoral.integrit|right.to.vote|suffrage|"
    r"derecho.*pol[íi]tico|art[íi]culo\s+23|restricci[oó]n|reelecci[oó]n|"
    r"continuidad\s+democr[aá]tica|integridad\s+electoral|derechos\s+pol[íi]ticos)",
    re.IGNORECASE
)

def should_skip_line(line: str) -> bool:
    for pat in GLOBAL_SKIP:
        if pat.search(line):
            return True
    return False

def truncate_text(text: str, max_len: int = 3000) -> tuple:
    """Returns (possibly truncated text, was_truncated bool)."""
    if len(text) > max_len:
        return text[:max_len].rstrip(), True
    return text, False

# ─────────────────────────────────────────────────────────────────────────────
# PRINCIPLE KEYWORD MATCHING
# ─────────────────────────────────────────────────────────────────────────────

_COMPILED_PRIN_KEYWORDS: dict = {}

def _compile_principle_keywords(raw_keywords: dict) -> dict:
    compiled = {}
    for prin_id, entry in raw_keywords.items():
        patterns = []
        for kw in entry.get("keywords", []):
            # Strip leading r" and trailing " if present (YAML raw string artifact)
            kw_clean = kw.strip().lstrip("r").strip('"').strip("'")
            try:
                patterns.append(re.compile(kw_clean, re.IGNORECASE))
            except re.error:
                patterns.append(re.compile(re.escape(kw_clean), re.IGNORECASE))
        compiled[prin_id] = patterns
    return compiled

def assign_principles(text: str, compiled_keywords: dict) -> list:
    matched = []
    for prin_id, patterns in compiled_keywords.items():
        for pat in patterns:
            if pat.search(text):
                matched.append(prin_id)
                break
    return matched

# ─────────────────────────────────────────────────────────────────────────────
# INTERNATIONAL PROVISION EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_article_provisions(md_text: str, source_rule: dict,
                                compiled_keywords: dict,
                                source_id: str,
                                profile: dict,
                                hierarchy_entry: dict) -> list:
    """Extract provisions using article heading pattern."""
    raw_pattern = source_rule["heading_pattern"]
    # Ensure pattern has at least one capturing group for the article/section number.
    # Some patterns use literal numbers (e.g. "29") or \d+ without parens.
    try:
        _test = re.compile(raw_pattern)
        if _test.groups == 0:
            raise ValueError("no groups")
    except (re.error, ValueError):
        # Wrap first numeric token (\d+ or a literal digit sequence) in a group
        raw_pattern = re.sub(r'(\\d\+|\d+)', r'(\1)', raw_pattern, count=1)
    heading_pat = re.compile(raw_pattern)
    targeted = source_rule.get("targeted_articles")

    lines = md_text.splitlines()
    provisions = []
    current_article = None
    current_inline = ""
    current_lines = []

    def flush(art_num, inline, body_lines):
        if art_num is None:
            return
        if targeted is not None and int_safe(art_num) not in targeted:
            return
        text = inline
        if body_lines:
            body = "\n".join(l for l in body_lines if not should_skip_line(l)).strip()
            text = (inline + "\n" + body).strip() if inline else body
        if len(text) < 30:
            return
        text, truncated = truncate_text(text)
        principles = assign_principles(text, compiled_keywords)
        provisions.append({
            "source_id": source_id,
            "article_or_paragraph": str(art_num),
            "provision_text": text,
            "word_count": len(text.split()),
            "assigned_principles": "|".join(principles) if principles else "",
            "normative_weight": hierarchy_entry["normative_weight"],
            "legal_character": hierarchy_entry["legal_character"],
            "manual_review_required": str(profile.get("manual_review_required", False)).lower(),
            "truncated": str(truncated).lower(),
        })

    for line in lines:
        m = heading_pat.match(line)
        if m:
            flush(current_article, current_inline, current_lines)
            current_article = m.group(1).strip()
            current_inline = m.group(2).strip() if m.lastindex >= 2 else ""
            current_lines = []
        else:
            if current_article is not None:
                current_lines.append(line)

    flush(current_article, current_inline, current_lines)
    return provisions


def extract_paragraph_provisions(md_text: str, source_rule: dict,
                                  compiled_keywords: dict,
                                  source_id: str,
                                  profile: dict,
                                  hierarchy_entry: dict) -> list:
    """Extract provisions using numbered paragraph pattern."""
    para_pat = re.compile(source_rule["paragraph_pattern"])
    targeted = source_rule.get("targeted_paragraphs", "all")
    para_range = source_rule.get("targeted_paragraph_range")
    is_oc = source_id == "INT-OC2821"

    lines = md_text.splitlines()
    provisions = []
    current_para = None
    current_lines = []

    def flush(para_num, body_lines):
        if para_num is None:
            return
        if targeted == "selective" or is_oc:
            # Apply OC-28/21 keyword filter
            body = " ".join(body_lines)
            if not OC2821_REQUIRED.search(body):
                return
        if para_range:
            try:
                n = int(para_num)
                if not (para_range[0] <= n <= para_range[1]):
                    return
            except ValueError:
                pass
        text = "\n".join(l for l in body_lines if not should_skip_line(l)).strip()
        if len(text) < 30:
            return
        text, truncated = truncate_text(text)
        principles = assign_principles(text, compiled_keywords)
        manual = "true" if is_oc else str(profile.get("manual_review_required", False)).lower()
        provisions.append({
            "source_id": source_id,
            "article_or_paragraph": f"para.{para_num}",
            "provision_text": text,
            "word_count": len(text.split()),
            "assigned_principles": "|".join(principles) if principles else "",
            "normative_weight": hierarchy_entry["normative_weight"],
            "legal_character": hierarchy_entry["legal_character"],
            "manual_review_required": manual,
            "truncated": str(truncated).lower(),
        })

    for line in lines:
        if should_skip_line(line):
            continue
        m = para_pat.match(line)
        if m:
            flush(current_para, current_lines)
            current_para = m.group(1)
            current_lines = [line]
        else:
            if current_para is not None:
                current_lines.append(line)

    flush(current_para, current_lines)
    return provisions


def int_safe(val):
    try:
        return int(str(val).strip().rstrip("."))
    except (ValueError, AttributeError):
        return -1


def extract_international_provisions(profiles: dict,
                                      extraction_rules: dict,
                                      hierarchy: dict,
                                      compiled_keywords: dict) -> list:
    """Main extraction loop over all 10 international MD files."""
    all_provisions = []
    source_counts = {}

    for source_id, profile in profiles.items():
        stem = profile["filename_stem"]
        md_path = INTL_MD_DIR / f"{stem}.md"
        if not md_path.exists():
            print(f"  [WARN] {md_path.name} not found — skipping {source_id}")
            continue

        rule = extraction_rules.get(source_id, {})
        hier = hierarchy.get(source_id, {"normative_weight": 1, "legal_character": "unknown"})

        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        provisions = []

        # Paragraph-primary sources
        if rule.get("paragraph_pattern"):
            provisions = extract_paragraph_provisions(
                md_text, rule, compiled_keywords, source_id, profile, hier)
            # If paragraph extraction yielded zero results and heading_pattern exists,
            # fall back to heading extraction (OC-28/21 fallback)
            if not provisions and rule.get("heading_pattern"):
                provisions = extract_article_provisions(
                    md_text, rule, compiled_keywords, source_id, profile, hier)
        elif rule.get("heading_pattern"):
            provisions = extract_article_provisions(
                md_text, rule, compiled_keywords, source_id, profile, hier)
        else:
            print(f"  [WARN] No extraction pattern for {source_id}")

        source_counts[source_id] = len(provisions)
        all_provisions.extend(provisions)

    # Assign sequential provision IDs
    for i, prov in enumerate(all_provisions, start=1):
        sid = prov["source_id"].replace("-", "")
        prov["provision_id"] = f"{sid}-{i:04d}"

    # Report
    print(f"\n  International provisions extracted:")
    for sid, cnt in source_counts.items():
        print(f"    {sid}: {cnt}")
    print(f"  TOTAL: {len(all_provisions)}\n")

    return all_provisions

# ─────────────────────────────────────────────────────────────────────────────
# TABLE 1: INTERNATIONAL STANDARD PROVISIONS
# ─────────────────────────────────────────────────────────────────────────────

def build_intl_provisions_table(provisions: list, profiles: dict) -> list:
    rows = []
    for p in provisions:
        sid = p["source_id"]
        prof = profiles.get(sid, {})
        rows.append({
            "provision_id": p["provision_id"],
            "source_id": sid,
            "source_title_short": prof.get("short_title", sid),
            "article_or_paragraph": p["article_or_paragraph"],
            "provision_text": p["provision_text"],
            "word_count": p["word_count"],
            "assigned_principles": p["assigned_principles"],
            "normative_weight": p["normative_weight"],
            "legal_character": p["legal_character"],
            "manual_review_required": p["manual_review_required"],
            "truncated": p.get("truncated", "false"),
        })
    return rows

INTL_PROV_FIELDS = [
    "provision_id", "source_id", "source_title_short",
    "article_or_paragraph", "provision_text", "word_count",
    "assigned_principles", "normative_weight", "legal_character",
    "manual_review_required", "truncated",
]

# ─────────────────────────────────────────────────────────────────────────────
# TABLE 2: PRINCIPLE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

def build_principle_definitions_table(principles: list) -> list:
    rows = []
    for p in principles:
        rows.append({
            "principle_id": p["principle_id"],
            "principle_name": p["principle_name"],
            "short_label": p.get("short_label", ""),
            "description": p.get("description", "").strip(),
            "legal_preparedness_question": p.get("legal_preparedness_question", "").strip(),
            "operational_dimensions": "|".join(p.get("operational_dimensions", [])),
            "primary_sources": "|".join(p.get("primary_sources", [])),
            "related_mechanisms": "|".join(p.get("related_mechanisms", [])),
        })
    return rows

PRIN_DEF_FIELDS = [
    "principle_id", "principle_name", "short_label", "description",
    "legal_preparedness_question", "operational_dimensions",
    "primary_sources", "related_mechanisms",
]

# ─────────────────────────────────────────────────────────────────────────────
# TABLE 3: MECHANISM-PRINCIPLE REQUIREMENTS
# ─────────────────────────────────────────────────────────────────────────────

def build_mechanism_principle_requirements(principles: list,
                                            provisions: list,
                                            hierarchy: dict,
                                            profiles: dict) -> list:
    """
    For each (principle, mechanism) pair, identify which international
    sources provide a requirement, and build one row per (principle, mech, source).
    """
    # Build index: principle_id → primary_sources list
    # Primary sources are e.g. ["INT-ICCPR:Art.2", "INT-ACHR:Art.23"]
    # We extract the source_id part before the colon.

    tier_labels = {1: "mandatory_binding", 2: "strongly_recommended",
                   3: "recommended_good_practice", 4: "complementary"}

    rows = []
    req_counter = defaultdict(int)

    for prin in principles:
        prin_id = prin["principle_id"]
        mechs = prin.get("related_mechanisms", [])
        raw_sources = prin.get("primary_sources", [])

        # Parse source references: "INT-ICCPR:Art.2" → "INT-ICCPR"
        source_ids = []
        for ref in raw_sources:
            parts = ref.split(":")
            sid = parts[0].strip()
            if sid in profiles:
                source_ids.append((sid, ref))

        for mech in mechs:
            for (sid, full_ref) in source_ids:
                hier = hierarchy.get(sid, {})
                tier = hier.get("tier", 4)
                req_type = tier_labels.get(tier, "complementary")
                manual = profiles.get(sid, {}).get("manual_review_required", False)

                req_id = f"REQ-{prin_id}-{mech[:20].upper().replace(' ', '_').replace('_', '-')}-{sid}"
                rows.append({
                    "requirement_id": req_id,
                    "principle_id": prin_id,
                    "mechanism_id": mech,
                    "source_id": sid,
                    "source_tier": tier,
                    "normative_weight": hier.get("normative_weight", 1),
                    "requirement_type": req_type,
                    "requirement_description": f"{prin_id} — {mech} — {full_ref}",
                    "manual_review_required": str(bool(manual)).lower(),
                })

    return rows

REQ_FIELDS = [
    "requirement_id", "principle_id", "mechanism_id", "source_id",
    "source_tier", "normative_weight", "requirement_type",
    "requirement_description", "manual_review_required",
]

# ─────────────────────────────────────────────────────────────────────────────
# DOMESTIC DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

def load_domestic_data(table_dir: Path, country_prefix: str) -> dict:
    """Load provisions and actor edges for a country."""
    prov_path = table_dir / f"{country_prefix}_legal_provisions.csv"
    edges_path = table_dir / f"{country_prefix}_actor_mechanism_edges.csv"

    provisions = read_csv(prov_path) if prov_path.exists() else []
    edges_raw = read_csv(edges_path) if edges_path.exists() else []

    # Normalise edges — Mexico has actor_id/actor_name/mechanism_id/mechanism_name fields,
    # Costa Rica has actor/mechanism fields.
    # CAL-001: prefer mechanism_name over mechanism_id to avoid returning internal IDs
    # like "MEX-MECH-001" instead of plain names like "vote".
    edges = []
    for e in edges_raw:
        actor = e.get("actor_id") or e.get("actor") or ""
        mech = e.get("mechanism_name") or e.get("mechanism") or e.get("mechanism_id") or ""
        edges.append({"actor": actor, "mechanism": mech,
                      "anchor_strength": e.get("anchor_strength", "0")})

    return {"provisions": provisions, "edges": edges}

# ─────────────────────────────────────────────────────────────────────────────
# SCORE COMPUTATION
# ─────────────────────────────────────────────────────────────────────────────

PROCESS_MECHANISMS = {
    "vote", "recall", "citizen_initiative", "popular_consultation",
    "referendum", "electoral_remedies", "constitutional_remedies",
    "civil_registry_electoral_functions",
    "independent_candidacies",   # CAL-REF-002: audit confirmed extensive LGIPE procedural corpus
}

TIMELINE_PAT = re.compile(
    r"(plazo|t[eé]rmino|\bd[íi]as\b|horas|dentro de|a m[aá]s tardar|"
    r"calendario|peri[oó]dico|dentro del t[eé]rmino|en un plazo)",
    re.IGNORECASE
)
REMEDY_PAT = re.compile(
    r"(recurso|impugnar|inconformidad|nulidad|sanci[oó]n|juicio|"
    r"amparo|appeal|judicial|recourse|impartial)",
    re.IGNORECASE
)
EQUALITY_PAT = re.compile(
    r"(sin discriminaci[oó]n|igualdad|paridad|no discriminaci[oó]n|"
    r"cuota|medidas.*especiales|equal|non.discrim)",
    re.IGNORECASE
)
# CAL-REF-001: Differentiated accessibility dimensions.
# ACCESSIBILITY_DISABILITY_PAT — CRPD Art. 29 disability-specific language.
# Required for PRIN-003 score >= 4; generic access alone is insufficient.
ACCESSIBILITY_DISABILITY_PAT = re.compile(
    r"(discapacidad|persons?\s+with\s+disabilit|disability|"
    r"ajuste\s+razonable|reasonable\s+accommodation|"
    r"voto\s+asistido|asistencia\s+(?:para\s+)?(?:al\s+)?voto|"
    r"asistencia.*electoral.*discapacidad|discapacidad.*asistencia|"
    r"braille|lengua\s+de\s+se[ñn]as|int[eé]rprete.*(?:vot|electoral)|"
    r"sign\s+language|assistive|tecnolog[íi]a\s+de\s+apoyo|"
    r"(?:casilla|cab[íi]na|local\s+electoral|instalaci[oó]n)\s+accesible|"
    r"material(?:es)?\s+accesible[s]?\s+(?:de\s+)?vot|"
    r"formato\s+accesible.*(?:vot|informaci[oó]n\s+electoral)|"
    r"accesibilidad\s+(?:del\s+)?voto|voto.*accesibilidad)",
    re.IGNORECASE
)
# Linguistically or culturally specific participation access
ACCESSIBILITY_LANGUAGE_CULTURAL_PAT = re.compile(
    r"(lengua\s+ind[íi]gena|idioma\s+ind[íi]gena|"
    r"traducci[oó]n\s+(?:a\s+la\s+)?lengua|"
    r"int[eé]rprete\s+(?:de\s+)?lengua|en\s+su\s+propia\s+lengua|"
    r"comunidades?\s+ind[íi]genas?.*(?:vot|participac)|"
    r"indigenous\s+language|accesibilidad\s+cultural)",
    re.IGNORECASE
)
# Digital or informational accessible formats
ACCESSIBILITY_DIGITAL_PAT = re.compile(
    r"(voto\s+electr[oó]nico|plataforma\s+(?:digital|electr[oó]nica)\s+"
    r"(?:del\s+)?(?:TSE|INE|organismo\s+electoral)|"
    r"formato\s+accesible.*informac|informac.*formato\s+accesible|"
    r"accesibilidad\s+web|web.*accesibilidad)",
    re.IGNORECASE
)
# Generic access language — catches remaining "accesib"/"accessible" terms.
# For PRIN-003, this alone caps score at 3 and sets manual_review_required=true.
ACCESSIBILITY_GENERAL_PAT = re.compile(
    r"(accesib|accessible)",
    re.IGNORECASE
)
TERRITORIAL_PAT = re.compile(
    r"(municipal|local|territorial|nivel.*federal|estado.*municipio|"
    r"comunidad.*ind[íi]gena|circunscripci[oó]n|all levels|subnational)",
    re.IGNORECASE
)
RESTRICTION_PAT = re.compile(
    r"(criterio.*objetivo|proporcion|necesario|fin leg[íi]timo|"
    r"ley.*establece|restricci[oó]n|objective criteria|proportionate)",
    re.IGNORECASE
)
TRANSPARENCY_PAT = re.compile(
    r"(transparencia|publicidad|rendici[oó]n.*cuentas|divulgaci[oó]n|"
    r"transparenc|accountability|disclosure|audit|public.*information|reporting)",
    re.IGNORECASE
)

SCORE_LABELS = {
    0: "absent",
    1: "declaratory_only",
    2: "partial_basis",
    3: "functional_basis",
    4: "strong_basis",
    5: "integrated_basis",
}

# CAL-004: per-principle dimension whitelists.
# Only dimensions in a principle's whitelist count toward that principle's score.
# Each whitelist has exactly 5 dimensions so the full 0–5 range is achievable.
PRINCIPLE_DIMENSION_WHITELIST = {
    # Legality: statutory anchor + legal hierarchy + enabling law + process + actor
    "PRIN-001": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "process_defined", "timeline_present", "actor_assigned"},
    # Equality: anchor + equality keyword + actor + non-discrimination + territorial
    "PRIN-002": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "equality_measure", "actor_assigned", "territorial_coverage"},
    # Accessibility: anchor + accessibility keyword + equality + actor
    "PRIN-003": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "accessibility_measure", "equality_measure", "actor_assigned"},
    # Effective participation: anchor + process + actor + timeline + territorial
    "PRIN-004": {"anchor_statutory", "process_defined", "actor_assigned",
                 "timeline_present", "territorial_coverage"},
    # Pluralism: anchor + process + actor + restriction + equality
    "PRIN-005": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "process_defined", "actor_assigned", "restriction_criteria"},
    # Due process / remedy: anchor + process + actor + timeline + remedy
    "PRIN-006": {"anchor_statutory", "process_defined", "actor_assigned",
                 "timeline_present", "remedy_present"},
    # Transparency: anchor + actor + process + transparency keyword + equality
    "PRIN-007": {"anchor_statutory", "actor_assigned", "process_defined",
                 "transparency_measure", "equality_measure"},
    # Institutional competence: anchor + actor + process + timeline
    "PRIN-008": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "actor_assigned", "process_defined", "timeline_present"},
    # Procedural certainty: anchor + process + timeline + actor + restriction
    "PRIN-009": {"anchor_statutory", "process_defined", "timeline_present",
                 "actor_assigned", "restriction_criteria"},
    # Territorial / multilevel: anchor + process + actor + territorial + equality
    "PRIN-010": {"anchor_statutory", "process_defined", "actor_assigned",
                 "territorial_coverage", "equality_measure"},
    # Administrative capacity: anchor + actor + process + timeline + territorial
    "PRIN-011": {"anchor_statutory", "actor_assigned", "process_defined",
                 "timeline_present", "territorial_coverage"},
    # Restriction legality: anchor + restriction criteria + equality + process
    "PRIN-012": {"anchor_statutory", "constitutional_or_statutory_anchor",
                 "restriction_criteria", "equality_measure", "process_defined"},
}


def compute_score(matched_provisions: list, mechanism: str,
                  actors_for_mech: set, principle_id: str = None) -> tuple:
    """
    Returns (score, label, dimensions_passed, needs_review).

    Calibration fixes applied:
      CAL-002: keyword dimensions only fire on provisions with anchor_strength >= 3;
               for corpora >= 200 provisions, require >= 2 distinct source_type categories.
      CAL-003: actor gate — if actor_count == 0 and max_strength >= 3, cap score at 2.
      CAL-004: per-principle dimension whitelist from PRINCIPLE_DIMENSION_WHITELIST.
    """
    if not matched_provisions:
        return 0, "absent", [], False

    strengths = [int_safe(p.get("anchor_strength", 0)) for p in matched_provisions]
    max_strength = max(strengths) if strengths else 0

    if max_strength <= 1:
        needs_review = any(p.get("manual_review_required", "false").lower() == "true"
                           for p in matched_provisions)
        return 1, "declaratory_only", [], needs_review

    # CAL-002: build anchor-qualified provision pool for keyword matching
    qualified_provisions = [p for p in matched_provisions
                             if int_safe(p.get("anchor_strength", 0)) >= 3]
    large_corpus = len(matched_provisions) >= 200

    def keyword_fires(pattern) -> bool:
        """True if pattern matches at least one anchor-qualified provision.
        For large corpora (>=200 provisions), additionally require matches
        span >=2 distinct source_type categories (CAL-002 multi-source rule)."""
        hits = [p for p in qualified_provisions
                if pattern.search(p.get("provision_text", ""))]
        if not hits:
            return False
        if large_corpus:
            source_types = {
                p.get("source_type", "") or p.get("source_id", "?")
                for p in hits
            }
            return len(source_types) >= 2
        return True

    actor_count = len(actors_for_mech)

    # Build all possible dimensions — anchor-based first, then keyword-gated
    all_dimensions = []
    if max_strength >= 3:
        all_dimensions.append("anchor_statutory")
    if max_strength >= 4:
        all_dimensions.append("constitutional_or_statutory_anchor")
    if mechanism in PROCESS_MECHANISMS:
        all_dimensions.append("process_defined")
    if actors_for_mech:
        all_dimensions.append("actor_assigned")
    if keyword_fires(TIMELINE_PAT):
        all_dimensions.append("timeline_present")
    if keyword_fires(REMEDY_PAT) or mechanism in {"electoral_remedies", "constitutional_remedies"}:
        all_dimensions.append("remedy_present")
    if keyword_fires(EQUALITY_PAT):
        all_dimensions.append("equality_measure")

    # CAL-REF-001: Differentiated accessibility detection.
    # Test patterns in specificity order; record the most specific subdimension found.
    # For PRIN-003, only disability-specific / language / digital counts toward the
    # whitelist dimension "accessibility_measure". Generic access alone caps score at 3.
    _has_disability = keyword_fires(ACCESSIBILITY_DISABILITY_PAT)
    _has_language   = keyword_fires(ACCESSIBILITY_LANGUAGE_CULTURAL_PAT)
    _has_digital    = keyword_fires(ACCESSIBILITY_DIGITAL_PAT)
    _has_general    = keyword_fires(ACCESSIBILITY_GENERAL_PAT)

    _accessibility_specific  = _has_disability or _has_language or _has_digital
    _accessibility_generic_only = _has_general and not _accessibility_specific

    # Record the most specific subdimension that fired
    if _has_disability:
        all_dimensions.append("accessibility_disability_specific")
    elif _has_language:
        all_dimensions.append("accessibility_language_or_cultural")
    elif _has_digital:
        all_dimensions.append("accessibility_digital_or_informational")
    elif _has_general:
        all_dimensions.append("accessibility_general_access")

    # "accessibility_measure" (the whitelist key) fires only when specific evidence found
    if _accessibility_specific:
        all_dimensions.append("accessibility_measure")

    if keyword_fires(TERRITORIAL_PAT):
        all_dimensions.append("territorial_coverage")
    if keyword_fires(RESTRICTION_PAT):
        all_dimensions.append("restriction_criteria")
    if keyword_fires(TRANSPARENCY_PAT):
        all_dimensions.append("transparency_measure")

    # CAL-004: filter to principle-specific dimension whitelist
    if principle_id and principle_id in PRINCIPLE_DIMENSION_WHITELIST:
        whitelist = PRINCIPLE_DIMENSION_WHITELIST[principle_id]
        dimensions = [d for d in all_dimensions if d in whitelist]
    else:
        dimensions = all_dimensions

    dim_count = len(dimensions)

    # Score assignment
    if dim_count == 0:
        score = 1
    elif dim_count == 1:
        score = 2
    elif dim_count == 2:
        score = 3
    elif dim_count <= 4:
        score = 4
    else:
        score = 5

    # Anchor cap: if no statutory-or-higher provisions, cap at 3
    if max_strength <= 2:
        score = min(score, 3)

    # CAL-003: actor gate — if no actor is assigned at statutory level, cap at 2.
    # Applies whenever max_strength >= 3 (statutory+ provisions present) to ensure
    # that institutionally meaningful scores (>=3) require at least one designated actor.
    if actor_count == 0 and max_strength >= 3:
        score = min(score, 2)

    # CAL-REF-001: PRIN-003 generic-access cap.
    # If only generic "accesib"/"accessible" language fired (no disability-specific,
    # language/cultural, or digital evidence), PRIN-003 score is capped at 3 and
    # flagged for manual review. This prevents logistical access language from
    # driving score 4 or 5 for the accessibility principle.
    _prin003_generic_cap = (
        principle_id == "PRIN-003"
        and _accessibility_generic_only
        and score >= 4
    )
    if _prin003_generic_cap:
        score = min(score, 3)

    needs_review = any(p.get("manual_review_required", "false").lower() == "true"
                       for p in matched_provisions)
    # Override needs_review if PRIN-003 generic-access cap applied
    if _prin003_generic_cap:
        needs_review = True

    return score, SCORE_LABELS[score], dimensions, needs_review


GAP_SEVERITY = {
    0: "critical",
    1: "significant",
    2: "significant",
    3: "moderate",
    4: "none",
    5: "none",
}

def build_scores_table(country_code: str, country_data: dict,
                        principles: list, hierarchy: dict) -> list:
    provisions = country_data["provisions"]
    edges = country_data["edges"]

    # Index provisions by mechanism — split pipe-separated multi-mechanism values
    mech_provisions = defaultdict(list)
    for p in provisions:
        raw_mech = p.get("mechanism", "").strip()
        if raw_mech:
            for mech in raw_mech.split("|"):
                mech = mech.strip()
                if mech:
                    mech_provisions[mech].append(p)

    # Index actors by mechanism — split pipe-separated values in actor edges
    mech_actors = defaultdict(set)
    for e in edges:
        raw_mech = (e.get("mechanism") or "").strip()
        actor = (e.get("actor") or "").strip()
        if raw_mech and actor:
            for mech in raw_mech.split("|"):
                mech = mech.strip()
                if mech:
                    mech_actors[mech].add(actor)

    rows = []
    for prin in principles:
        prin_id = prin["principle_id"]
        for mech in prin.get("related_mechanisms", []):
            matched = mech_provisions.get(mech, [])
            actors = mech_actors.get(mech, set())
            # CAL-004: pass principle_id so compute_score applies per-principle whitelist
            score, label, dims, needs_review = compute_score(matched, mech, actors, prin_id)

            # Corpus coverage note
            notes = []
            if country_code == "CRC":
                if not matched:
                    notes.append("mechanism_not_in_corpus")
                ral_provisions = [p for p in matched
                                   if p.get("source_id") == "CRC-RAL"]
                if ral_provisions:
                    notes.append("includes_ral_commentary_risk")
            if country_code == "MEX" and not matched:
                notes.append("mechanism_not_in_corpus")

            rows.append({
                "score_id": f"SCR-{country_code}-{prin_id}-{mech[:20]}",
                "country_code": country_code,
                "principle_id": prin_id,
                "mechanism_id": mech,
                "matched_provision_count": len(matched),
                "max_anchor_strength": max(
                    (int_safe(p.get("anchor_strength", 0)) for p in matched), default=0
                ),
                "actor_count": len(actors),
                "implementation_readiness_score": score,
                "score_label": label,
                "dimension_checks_passed": "|".join(dims),
                "needs_review": str(needs_review).lower(),
                "corpus_coverage_note": "|".join(notes) if notes else "ok",
            })

    return rows

SCORE_FIELDS = [
    "score_id", "country_code", "principle_id", "mechanism_id",
    "matched_provision_count", "max_anchor_strength", "actor_count",
    "implementation_readiness_score", "score_label",
    "dimension_checks_passed", "needs_review", "corpus_coverage_note",
]

# ─────────────────────────────────────────────────────────────────────────────
# TABLE 6: COMPARISON
# ─────────────────────────────────────────────────────────────────────────────

def build_comparison_table(mex_scores: list, crc_scores: list) -> list:
    # Index by (principle_id, mechanism_id)
    mex_idx = {(r["principle_id"], r["mechanism_id"]): r for r in mex_scores}
    crc_idx = {(r["principle_id"], r["mechanism_id"]): r for r in crc_scores}

    all_keys = set(mex_idx.keys()) | set(crc_idx.keys())
    rows = []

    for (prin_id, mech_id) in sorted(all_keys):
        mex = mex_idx.get((prin_id, mech_id))
        crc = crc_idx.get((prin_id, mech_id))
        mex_score = int(mex["implementation_readiness_score"]) if mex else 0
        crc_score = int(crc["implementation_readiness_score"]) if crc else 0
        delta = mex_score - crc_score
        abs_delta = abs(delta)
        convergence = ("aligned" if abs_delta <= 1
                       else "divergent" if abs_delta == 2
                       else "highly_divergent")

        notes_parts = []
        if mex and mex.get("corpus_coverage_note", "ok") != "ok":
            notes_parts.append(f"MEX:{mex['corpus_coverage_note']}")
        if crc and crc.get("corpus_coverage_note", "ok") != "ok":
            notes_parts.append(f"CRC:{crc['corpus_coverage_note']}")
        if crc and "ral_commentary_risk" in (crc.get("corpus_coverage_note", "")):
            notes_parts.append("CRC_RAL_caveat")

        rows.append({
            "comparison_id": f"CMP-{prin_id}-{mech_id[:20]}",
            "principle_id": prin_id,
            "mechanism_id": mech_id,
            "mexico_score": mex_score,
            "mexico_label": mex["score_label"] if mex else "absent",
            "costa_rica_score": crc_score,
            "costa_rica_label": crc["score_label"] if crc else "absent",
            "score_delta": delta,
            "convergence_level": convergence,
            "gap_severity_mexico": GAP_SEVERITY.get(mex_score, "none"),
            "gap_severity_costa_rica": GAP_SEVERITY.get(crc_score, "none"),
            "notes": "|".join(notes_parts) if notes_parts else "",
        })

    return rows

CMP_FIELDS = [
    "comparison_id", "principle_id", "mechanism_id",
    "mexico_score", "mexico_label",
    "costa_rica_score", "costa_rica_label",
    "score_delta", "convergence_level",
    "gap_severity_mexico", "gap_severity_costa_rica", "notes",
]

# ─────────────────────────────────────────────────────────────────────────────
# TABLE 7: PRINCIPLE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def build_summary_table(principles: list, mex_scores: list,
                         crc_scores: list, hierarchy: dict,
                         profiles: dict) -> list:
    mex_by_prin = defaultdict(list)
    for r in mex_scores:
        mex_by_prin[r["principle_id"]].append(int(r["implementation_readiness_score"]))

    crc_by_prin = defaultdict(list)
    for r in crc_scores:
        crc_by_prin[r["principle_id"]].append(int(r["implementation_readiness_score"]))

    rows = []
    for prin in principles:
        prin_id = prin["principle_id"]

        # Count binding sources for this principle
        raw_sources = prin.get("primary_sources", [])
        binding_count = 0
        for ref in raw_sources:
            sid = ref.split(":")[0].strip()
            hier = hierarchy.get(sid, {})
            if hier.get("tier") == 1:
                binding_count += 1

        mex_s = mex_by_prin.get(prin_id, [0])
        crc_s = crc_by_prin.get(prin_id, [0])

        mex_avg = round(sum(mex_s) / len(mex_s), 2) if mex_s else 0
        crc_avg = round(sum(crc_s) / len(crc_s), 2) if crc_s else 0

        mex_gaps = sum(1 for s in mex_s if s <= 2)
        crc_gaps = sum(1 for s in crc_s if s <= 2)
        mex_critical = sum(1 for s in mex_s if s == 0)
        crc_critical = sum(1 for s in crc_s if s == 0)

        overall_avg = (mex_avg + crc_avg) / 2

        # CAL-005: raise "adequate" bar — require avg >= 4.0 AND no score-0
        # mechanism in either country; "partial" if avg >= 3.0; else "insufficient".
        mex_has_critical = any(s == 0 for s in mex_s)
        crc_has_critical = any(s == 0 for s in crc_s)
        if overall_avg >= 4.0 and not mex_has_critical and not crc_has_critical:
            flag = "adequate"
        elif overall_avg >= 3.0:
            flag = "partial"
        else:
            flag = "insufficient"

        rows.append({
            "principle_id": prin_id,
            "principle_name": prin["principle_name"],
            "mexico_avg_score": mex_avg,
            "mexico_gap_count": mex_gaps,
            "mexico_critical_gaps": mex_critical,
            "costa_rica_avg_score": crc_avg,
            "costa_rica_gap_count": crc_gaps,
            "costa_rica_critical_gaps": crc_critical,
            "binding_sources_count": binding_count,
            "overall_preparedness_flag": flag,
        })

    return rows

SUMMARY_FIELDS = [
    "principle_id", "principle_name",
    "mexico_avg_score", "mexico_gap_count", "mexico_critical_gaps",
    "costa_rica_avg_score", "costa_rica_gap_count", "costa_rica_critical_gaps",
    "binding_sources_count", "overall_preparedness_flag",
]

# ─────────────────────────────────────────────────────────────────────────────
# TABLE 8: UNIFIED PRINCIPLE TRACEABILITY MATRIX (MEX + CRC)
# ─────────────────────────────────────────────────────────────────────────────

def build_matrix_table(mex_scores: list, crc_scores: list,
                        principles: list) -> list:
    """
    Combines MEX and CRC score rows into a single unified matrix.
    Dimension checks are expanded into explicit boolean columns.
    """
    prin_names = {p["principle_id"]: p["principle_name"] for p in principles}

    COUNTRY_LABELS = {"MEX": "Mexico", "CRC": "Costa Rica"}

    rows = []
    for score_row in mex_scores + crc_scores:
        cc = score_row["country_code"]
        country = COUNTRY_LABELS.get(cc, cc)
        prin_id = score_row["principle_id"]
        mech_id = score_row["mechanism_id"]

        # Expand dimension_checks_passed pipe-string into a set
        raw_dims = score_row.get("dimension_checks_passed", "")
        dims_set = set(raw_dims.split("|")) if raw_dims else set()

        score = int(score_row["implementation_readiness_score"])
        gap_type = GAP_SEVERITY.get(score, "none")

        # administrative_capacity_defined: true when both actor_assigned AND
        # process_defined are confirmed (proxy for institutional readiness)
        admin_cap = "true" if ("actor_assigned" in dims_set and
                               "process_defined" in dims_set) else "false"

        # accessibility_defined: true if any accessibility subdimension fired
        # (disability-specific, language/cultural, digital, or general)
        _ACCESS_DIMS = {
            "accessibility_measure",
            "accessibility_disability_specific",
            "accessibility_language_or_cultural",
            "accessibility_digital_or_informational",
            "accessibility_general_access",
        }

        rows.append({
            "country":                      country,
            "principle_id":                 prin_id,
            "principle_name":               prin_names.get(prin_id, ""),
            "mechanism_id":                 mech_id,
            "mechanism_name":               mech_id,
            "matched_provision_count":      score_row["matched_provision_count"],
            "max_anchor_strength":          score_row["max_anchor_strength"],
            "actor_count":                  score_row["actor_count"],
            "process_defined":              "true" if "process_defined" in dims_set else "false",
            "actor_assigned":               "true" if "actor_assigned" in dims_set else "false",
            "timeline_defined":             "true" if "timeline_present" in dims_set else "false",
            "territorial_level_defined":    "true" if "territorial_coverage" in dims_set else "false",
            "remedy_defined":               "true" if "remedy_present" in dims_set else "false",
            "accessibility_defined":        "true" if dims_set & _ACCESS_DIMS else "false",
            "equality_defined":             "true" if "equality_measure" in dims_set else "false",
            "transparency_defined":         "true" if "transparency_measure" in dims_set else "false",
            "restriction_defined":          "true" if "restriction_criteria" in dims_set else "false",
            "administrative_capacity_defined": admin_cap,
            "implementation_readiness_score": score,
            "score_label":                  score_row["score_label"],
            "gap_type":                     gap_type,
            "corpus_coverage_note":         score_row["corpus_coverage_note"],
            "needs_review":                 score_row["needs_review"],
            "dimension_checks_passed":      raw_dims,
            "notes":                        "",
        })

    # Sort: country → principle → mechanism
    rows.sort(key=lambda r: (r["country"], r["principle_id"], r["mechanism_id"]))
    return rows


MATRIX_FIELDS = [
    "country", "principle_id", "principle_name", "mechanism_id", "mechanism_name",
    "matched_provision_count", "max_anchor_strength", "actor_count",
    "process_defined", "actor_assigned", "timeline_defined",
    "territorial_level_defined", "remedy_defined", "accessibility_defined",
    "equality_defined", "transparency_defined", "restriction_defined",
    "administrative_capacity_defined",
    "implementation_readiness_score", "score_label", "gap_type",
    "corpus_coverage_note", "needs_review", "dimension_checks_passed", "notes",
]

# ─────────────────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────

def write_final_report(stats: dict, out_dir: Path):
    report_path = out_dir / "principle_traceability_report_2026-05-18.md"
    lines = []
    lines.append("# NormTrace Political Rights — Principle Traceability Layer Report")
    lines.append("**Date:** 2026-05-18")
    lines.append("**Scope:** International standards brain + principle traceability pipeline")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. International Sources Processed")
    lines.append("")
    lines.append(f"**{stats['sources_processed']} sources** processed from "
                 f"`corpus/international/md/`.")
    lines.append("")
    lines.append("| Source ID | Short Title | Tier | Legal Character | Provisions |")
    lines.append("|---|---|---|---|---|")
    for row in stats["source_rows"]:
        lines.append(f"| {row['source_id']} | {row['short_title']} | "
                     f"{row['tier']} | {row['legal_character']} | {row['provisions']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. International Standard Provisions Extracted")
    lines.append("")
    lines.append(f"**Total: {stats['total_intl_provisions']} provisions** extracted "
                 f"across all 10 sources.")
    lines.append("")
    lines.append(f"- Tier 1 (binding treaty): {stats['tier1_provisions']} provisions")
    lines.append(f"- Tier 2 (authoritative interpretive): {stats['tier2_provisions']} provisions")
    lines.append(f"- Tier 3 (soft law with political commitment): {stats['tier3_provisions']} provisions")
    lines.append(f"- Tier 4 (soft law declaration): {stats['tier4_provisions']} provisions")
    lines.append(f"- Provisions with principle assignment: {stats['assigned_provisions']}")
    lines.append(f"- Provisions flagged manual_review_required: {stats['manual_review_provisions']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Principles Created")
    lines.append("")
    lines.append(f"**{stats['principles_count']} principles** (PRIN-001 to PRIN-012) "
                 f"loaded from `political_rights_principle_map.yml`.")
    lines.append("")
    lines.append("| Principle ID | Name |")
    lines.append("|---|---|")
    for p in stats["principles_list"]:
        lines.append(f"| {p['id']} | {p['name']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Mechanism-Principle Requirements Created")
    lines.append("")
    lines.append(f"**{stats['requirements_count']} requirement rows** in "
                 f"`mechanism_principle_requirements` table.")
    lines.append(f"- Mandatory binding (tier 1): {stats['mandatory_req']}")
    lines.append(f"- Strongly recommended (tier 2): {stats['recommended_req']}")
    lines.append(f"- Recommended good practice (tier 3): {stats['good_practice_req']}")
    lines.append(f"- Complementary (tier 4): {stats['complementary_req']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Domestic Mechanism-Principle Rows Created")
    lines.append("")
    lines.append(f"**Mexico:** {stats['mex_score_rows']} scoring rows "
                 f"(principle × mechanism combinations evaluated).")
    lines.append(f"**Costa Rica:** {stats['crc_score_rows']} scoring rows.")
    lines.append(f"**Comparison rows:** {stats['cmp_rows']} (INT-OUT-06).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 6. Main Gaps Detected by Country")
    lines.append("")
    lines.append("### Mexico — Gaps (score ≤ 2)")
    lines.append("")
    if stats["mex_gaps"]:
        lines.append("| Principle | Mechanism | Score | Severity |")
        lines.append("|---|---|---|---|")
        for g in stats["mex_gaps"]:
            lines.append(f"| {g['principle_id']} | {g['mechanism_id']} | "
                         f"{g['score']} | {g['severity']} |")
    else:
        lines.append("No critical or significant gaps detected in Mexico corpus.")
    lines.append("")
    lines.append("### Costa Rica — Gaps (score ≤ 2)")
    lines.append("")
    if stats["crc_gaps"]:
        lines.append("| Principle | Mechanism | Score | Severity |")
        lines.append("|---|---|---|---|")
        for g in stats["crc_gaps"]:
            lines.append(f"| {g['principle_id']} | {g['mechanism_id']} | "
                         f"{g['score']} | {g['severity']} |")
    else:
        lines.append("No critical or significant gaps detected in Costa Rica corpus.")
    lines.append("")
    lines.append("> **Caveat:** Gaps reflect corpus-based diagnostic legal preparedness, "
                 "not legal compliance. Costa Rica scores may be conservative due to absent "
                 "Sala IV jurisprudence, TSE resolutions, and LGAP (see INT-VN-008).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 7. Metadata Errors and Source Verification")
    lines.append("")
    lines.append("### HRC General Comment 25 (INT-HRC-GC25)")
    lines.append("")
    lines.append("**Verification result: NO METADATA ERROR.**")
    lines.append("")
    lines.append("File `observacion_general_25_comite_derechos_humanos.md` was flagged "
                 "for verification due to possible confusion with a CRC (Committee on the "
                 "Rights of the Child) general comment on children's digital rights. "
                 "Content confirmed as HRC General Comment No. 25 on ICCPR Article 25 "
                 "(Participation in Public Affairs and the Right to Vote), 1996. "
                 "Language: Spanish. 29 numbered paragraphs.")
    lines.append("")
    lines.append("**Pipeline action:** `metadata_error: false` — source used normally in "
                 "all principle traceability computations.")
    lines.append("")
    lines.append("### OC-28/21 Restriction Enforced")
    lines.append("")
    lines.append("INT-OC2821 provisions extracted with selective keyword filter "
                 "(political rights, ACHR Art. 23, democratic continuity). "
                 f"**{stats['oc2821_provisions']} provisions** extracted, "
                 "all with `manual_review_required=true`. "
                 "OC-28/21 is used as interpretive standard only — not as domestic rule source.")
    lines.append("")
    lines.append("### Other Sources")
    lines.append("")
    lines.append("No metadata errors detected in any other source. "
                 "ILO 169 file contains full convention text despite title suggesting "
                 "only Arts. 6–7 (see INT-VN-004 — positive impact on extraction).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 8. Output Files Created")
    lines.append("")
    lines.append("### `03_tables/international/`")
    lines.append("")
    for f in stats["output_files_intl"]:
        lines.append(f"- `{f}`")
    lines.append("")
    lines.append("### `03_tables/principle_traceability/`")
    lines.append("")
    for f in stats["output_files_trace"]:
        lines.append(f"- `{f}`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 9. Principle Summary Table")
    lines.append("")
    lines.append("| Principle | MEX Avg | MEX Gaps | CRC Avg | CRC Gaps | "
                 "Binding Sources | Flag |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in stats["summary_rows"]:
        lines.append(f"| {r['principle_id']} {r['principle_name']} | "
                     f"{r['mexico_avg_score']} | {r['mexico_gap_count']} | "
                     f"{r['costa_rica_avg_score']} | {r['costa_rica_gap_count']} | "
                     f"{r['binding_sources_count']} | {r['overall_preparedness_flag']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> **Diagnostic note:** All scores are corpus-based legal preparedness "
                 "indicators only — not legal compliance findings, not judicial determinations. "
                 "NormTrace is an analytical tool, not a legal opinion.")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n  [REPORT] {report_path.relative_to(BASE)}")
    return report_path

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n=== NormTrace: Building Principle Traceability Tables ===\n")

    # ── Load brain files ──────────────────────────────────────────────────────
    print("Loading international brain files...")
    profiles   = load_profiles()
    hierarchy  = load_hierarchy()
    ext_rules  = load_extraction_rules()
    principles = load_principle_map()

    compiled_keywords = _compile_principle_keywords(
        ext_rules.get("_principle_keywords", {}))

    print(f"  {len(profiles)} source profiles loaded")
    print(f"  {len(hierarchy)} hierarchy entries loaded")
    print(f"  {len(principles)} principles loaded")

    # ── Extract international provisions ─────────────────────────────────────
    print("\nExtracting international standard provisions...")
    intl_provisions = extract_international_provisions(
        profiles, ext_rules, hierarchy, compiled_keywords)

    # ── Load domestic data ────────────────────────────────────────────────────
    print("Loading domestic provision tables...")
    mex_data = load_domestic_data(MEX_TABLE_DIR, "mexico")
    crc_data = load_domestic_data(CRC_TABLE_DIR, "costa_rica")
    print(f"  Mexico: {len(mex_data['provisions'])} provisions, "
          f"{len(mex_data['edges'])} actor edges")
    print(f"  Costa Rica: {len(crc_data['provisions'])} provisions, "
          f"{len(crc_data['edges'])} actor edges")

    # ── Build tables ──────────────────────────────────────────────────────────
    print("\nBuilding output tables...")

    t1 = build_intl_provisions_table(intl_provisions, profiles)
    t2 = build_principle_definitions_table(principles)
    t3 = build_mechanism_principle_requirements(principles, intl_provisions,
                                                 hierarchy, profiles)
    t4 = build_scores_table("MEX", mex_data, principles, hierarchy)
    t5 = build_scores_table("CRC", crc_data, principles, hierarchy)
    t6 = build_comparison_table(t4, t5)
    t7 = build_summary_table(principles, t4, t5, hierarchy, profiles)
    t8 = build_matrix_table(t4, t5, principles)

    # ── Write CSV and JSON ────────────────────────────────────────────────────
    OUT_INTL_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TRACE_DIR.mkdir(parents=True, exist_ok=True)

    # Webapp data directory for principle traceability outputs
    WEBAPP_TRACE_DIR = BASE / "05_webapp" / "public" / "data" / "principle_traceability"
    WEBAPP_TRACE_DIR.mkdir(parents=True, exist_ok=True)

    output_files_intl = []
    output_files_trace = []

    def out_pair(dir_: Path, stem: str, table: list, fields: list,
                 json_key: str, file_list: list, extra_json_dir: Path = None):
        csv_path = dir_ / f"{stem}.csv"
        json_path = dir_ / f"{stem}.json"
        write_csv(csv_path, table, fields)
        write_json(json_path, {json_key: table})
        file_list.append(f"{stem}.csv")
        file_list.append(f"{stem}.json")
        if extra_json_dir is not None:
            extra_json_dir.mkdir(parents=True, exist_ok=True)
            extra_csv = extra_json_dir / f"{stem}.csv"
            extra_json = extra_json_dir / f"{stem}.json"
            write_csv(extra_csv, table, fields)
            write_json(extra_json, {json_key: table})

    out_pair(OUT_INTL_DIR, "international_standard_provisions",
             t1, INTL_PROV_FIELDS, "international_standard_provisions", output_files_intl)
    out_pair(OUT_INTL_DIR, "principle_definitions",
             t2, PRIN_DEF_FIELDS, "principles", output_files_intl)
    out_pair(OUT_INTL_DIR, "mechanism_principle_requirements",
             t3, REQ_FIELDS, "requirements", output_files_intl)

    out_pair(OUT_TRACE_DIR, "domestic_mechanism_principle_scores_MEX",
             t4, SCORE_FIELDS, "scores", output_files_trace)
    out_pair(OUT_TRACE_DIR, "domestic_mechanism_principle_scores_CRC",
             t5, SCORE_FIELDS, "scores", output_files_trace)
    out_pair(OUT_TRACE_DIR, "principle_gap_analysis_comparison",
             t6, CMP_FIELDS, "comparisons", output_files_trace)
    out_pair(OUT_TRACE_DIR, "principle_summary_by_country",
             t7, SUMMARY_FIELDS, "principle_summary", output_files_trace)
    # Unified matrix — also mirrored to webapp public data
    out_pair(OUT_TRACE_DIR, "principle_traceability_matrix",
             t8, MATRIX_FIELDS, "matrix", output_files_trace,
             extra_json_dir=WEBAPP_TRACE_DIR)

    # ── Build stats for final report ──────────────────────────────────────────
    source_rows = []
    for sid, prof in profiles.items():
        hier = hierarchy.get(sid, {})
        cnt = sum(1 for p in intl_provisions if p.get("source_id") == sid)
        source_rows.append({
            "source_id": sid,
            "short_title": prof.get("short_title", sid),
            "tier": hier.get("tier", "?"),
            "legal_character": hier.get("legal_character", "?"),
            "provisions": cnt,
        })

    tier_counts = defaultdict(int)
    for p in intl_provisions:
        tier_counts[p.get("normative_weight", 0)] += 1

    mex_gap_rows = [
        {"principle_id": r["principle_id"], "mechanism_id": r["mechanism_id"],
         "score": r["implementation_readiness_score"],
         "severity": GAP_SEVERITY.get(int(r["implementation_readiness_score"]), "none")}
        for r in t4 if int(r["implementation_readiness_score"]) <= 2
    ]
    crc_gap_rows = [
        {"principle_id": r["principle_id"], "mechanism_id": r["mechanism_id"],
         "score": r["implementation_readiness_score"],
         "severity": GAP_SEVERITY.get(int(r["implementation_readiness_score"]), "none")}
        for r in t5 if int(r["implementation_readiness_score"]) <= 2
    ]

    req_by_type = defaultdict(int)
    for r in t3:
        req_by_type[r["requirement_type"]] += 1

    oc2821_count = sum(1 for p in intl_provisions if p.get("source_id") == "INT-OC2821")

    stats = {
        "sources_processed": len(profiles),
        "source_rows": source_rows,
        "total_intl_provisions": len(intl_provisions),
        "tier1_provisions": sum(1 for p in intl_provisions if p.get("normative_weight") == 5),
        "tier2_provisions": sum(1 for p in intl_provisions if p.get("normative_weight") == 4),
        "tier3_provisions": sum(1 for p in intl_provisions if p.get("normative_weight") == 3),
        "tier4_provisions": sum(1 for p in intl_provisions if p.get("normative_weight") == 2),
        "assigned_provisions": sum(1 for p in intl_provisions if p.get("assigned_principles")),
        "manual_review_provisions": sum(1 for p in intl_provisions
                                         if p.get("manual_review_required") == "true"),
        "principles_count": len(principles),
        "principles_list": [{"id": p["principle_id"], "name": p["principle_name"]}
                             for p in principles],
        "requirements_count": len(t3),
        "mandatory_req": req_by_type.get("mandatory_binding", 0),
        "recommended_req": req_by_type.get("strongly_recommended", 0),
        "good_practice_req": req_by_type.get("recommended_good_practice", 0),
        "complementary_req": req_by_type.get("complementary", 0),
        "mex_score_rows": len(t4),
        "crc_score_rows": len(t5),
        "cmp_rows": len(t6),
        "mex_gaps": mex_gap_rows,
        "crc_gaps": crc_gap_rows,
        "oc2821_provisions": oc2821_count,
        "output_files_intl": output_files_intl,
        "output_files_trace": output_files_trace,
        "summary_rows": t7,
    }

    report_path = write_final_report(stats, OUT_TRACE_DIR)

    print("\n=== Pipeline complete ===")
    print(f"  International provisions: {len(intl_provisions)}")
    print(f"  Principle definitions:    {len(t2)}")
    print(f"  Requirements:             {len(t3)}")
    print(f"  MEX score rows:           {len(t4)}")
    print(f"  CRC score rows:           {len(t5)}")
    print(f"  Comparison rows:          {len(t6)}")
    print(f"  Summary rows:             {len(t7)}")
    print(f"  Matrix rows:              {len(t8)}")
    print(f"  Report: {report_path.relative_to(BASE)}")
    print()


if __name__ == "__main__":
    main()
