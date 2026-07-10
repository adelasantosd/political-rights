#!/usr/bin/env python3
"""
build_mexico_legal_brain_tables.py
NormTrace Political Rights — Mexico Offline Legal Brain Pipeline

Reads Markdown legal sources and metadata from corpus/mexico/,
extracts provisions using deterministic rules (no LLM), detects
mechanisms/actors/rights/obligations, assigns anchoring classifications,
and exports precomputed CSV and JSON tables for the webapp.

Usage:
    python3 scripts/build_mexico_legal_brain_tables.py

Outputs:
    03_tables/country_legal_brains/mexico/  (CSV files)
    05_webapp/public/data/legal_brains/mexico/  (JSON files)
"""

import os
import re
import csv
import json
import yaml
import sys
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_MD_DIR    = REPO_ROOT / "corpus" / "mexico" / "md"
CORPUS_META_DIR  = REPO_ROOT / "corpus" / "mexico" / "metadata"
BRAIN_DIR        = REPO_ROOT / "02_country_legal_brains" / "mexico"
OUT_CSV_DIR      = REPO_ROOT / "03_tables" / "country_legal_brains" / "mexico"
OUT_JSON_DIR     = REPO_ROOT / "05_webapp" / "public" / "data" / "legal_brains" / "mexico"

CSV_SEP = ";"

COUNTRY = "Mexico"

# Files to skip (non-legal sources)
SKIP_FILES = {"conversion_log.md"}

# ---------------------------------------------------------------------------
# SOURCE REGISTRY — maps filename stems to metadata-level classifications
# ---------------------------------------------------------------------------

SOURCE_REGISTRY = {
    "mexico_constitution_cpeum_latest_reform_2026_04_23": {
        "source_id": "MEX-CPEUM",
        "source_type": "constitution",
        "normative_rank": 1,
        "legal_anchor_type": "constitutional",
        "base_anchor_strength": 5,
    },
    "ley_general_instituciones_procedimientos_electorales": {
        "source_id": "MEX-LGIPE",
        "source_type": "general_law",
        "normative_rank": 3,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
    },
    "ley_general_partidos_politicos": {
        "source_id": "MEX-LGPP",
        "source_type": "general_law",
        "normative_rank": 3,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
    },
    "ley_general_medios_impugnacion_electoral": {
        "source_id": "MEX-LGSMIME",
        "source_type": "general_law",
        "normative_rank": 3,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
    },
    "ley_general_delitos_electorales": {
        "source_id": "MEX-LGDE",
        "source_type": "general_law",
        "normative_rank": 3,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
    },
    "ley_federal_consulta_popular": {
        "source_id": "MEX-LFCP",
        "source_type": "federal_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
    },
    "ley_federal_revocacion_mandato": {
        "source_id": "MEX-LFRM",
        "source_type": "federal_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
    },
    "ley_general_responsabilidades_administrativas": {
        "source_id": "MEX-LGRA",
        "source_type": "general_law",
        "normative_rank": 3,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
    },
    "mexico_general_transparency_access_information_law_lgtaip_2025": {
        "source_id": "MEX-LGTAIP",
        "source_type": "general_law",
        "normative_rank": 3,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
    },
    "reglamento_camara_diputados": {
        "source_id": "MEX-REGCD",
        "source_type": "parliamentary_regulation",
        "normative_rank": 5,
        "legal_anchor_type": "regulatory_or_parliamentary_procedural",
        "base_anchor_strength": 3,
    },
    "reglamento_senado_republica": {
        "source_id": "MEX-REGSN",
        "source_type": "parliamentary_regulation",
        "normative_rank": 5,
        "legal_anchor_type": "regulatory_or_parliamentary_procedural",
        "base_anchor_strength": 3,
    },
    "reglamento_gobierno_interior_congreso_general": {
        "source_id": "MEX-REGCONG",
        "source_type": "parliamentary_regulation",
        "normative_rank": 5,
        "legal_anchor_type": "regulatory_or_parliamentary_procedural",
        "base_anchor_strength": 3,
    },
    "reglamento_interior_ine_2025": {
        "source_id": "MEX-REGINE",
        "source_type": "electoral_administrative",
        "normative_rank": 6,
        "legal_anchor_type": "electoral_administrative",
        "base_anchor_strength": 2,
    },
    "ine_consulta_popular_2021": {
        "source_id": "MEX-INECP",
        "source_type": "electoral_administrative",
        "normative_rank": 6,
        "legal_anchor_type": "electoral_administrative",
        "base_anchor_strength": 2,
    },
    "ine_revocacion_mandato_2022": {
        "source_id": "MEX-INERM",
        "source_type": "electoral_administrative",
        "normative_rank": 6,
        "legal_anchor_type": "electoral_administrative",
        "base_anchor_strength": 2,
    },
    "mexico_federal_administrative_procedure_law_lfpa_2025": {
        "source_id": "MEX-LFPA",
        "source_type": "federal_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 3,
    },
    "mexico_organic_law_federal_public_administration_loapf_2025": {
        "source_id": "MEX-LOAPF",
        "source_type": "federal_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 3,
    },
    "mexico_federal_budget_and_fiscal_responsibility_law_lfprh_2026": {
        "source_id": "MEX-LFPRH",
        "source_type": "federal_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 2,
    },
    "mexico_planning_law_lplan_2026": {
        "source_id": "MEX-LPLAN",
        "source_type": "federal_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 2,
    },
}

# ---------------------------------------------------------------------------
# MECHANISM DEFINITIONS
# ---------------------------------------------------------------------------

MECHANISMS = {
    "vote": {
        "mechanism_id": "MEX-MECH-001",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"sufragio", r"votar\b", r"votaci[oó]n", r"\bvoto\b", r"lista nominal",
            r"padr[oó]n electoral", r"elecciones libres", r"sufragio universal",
            r"sufragio secreto", r"urna\b", r"casilla\b", r"jornada electoral",
            r"boleta electoral", r"escrutinio",
        ],
    },
    "right_to_stand_for_election": {
        "mechanism_id": "MEX-MECH-002",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"poder ser votad", r"\bcandidat[ao]\b", r"candidatura",
            r"registro de candidat", r"paridad", r"candidatura independiente",
            r"postulaci[oó]n", r"aspirante\b", r"elegibilidad",
        ],
    },
    "political_parties": {
        "mechanism_id": "MEX-MECH-003",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"partido pol[ií]tico", r"partidos pol[ií]ticos", r"registro de partido",
            r"financiamiento de partido", r"prerrogativas", r"militantes\b",
            r"democracia interna", r"coalici[oó]n\b", r"fiscalizaci[oó]n de partido",
            r"documentos b[aá]sicos",
        ],
    },
    "independent_candidacies": {
        "mechanism_id": "MEX-MECH-004",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "medium",
        "keywords": [
            r"candidatura independiente", r"candidatos independientes",
            r"candidato independiente", r"registro independiente",
            r"firmas de apoyo ciudadano", r"apoyo ciudadano para candidatura",
        ],
    },
    "citizen_initiative": {
        "mechanism_id": "MEX-MECH-005",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 4,
        "operational_dependence": "medium",
        "keywords": [
            r"iniciativa ciudadana", r"iniciativa de ley", r"iniciativa de los ciudadanos",
            r"derecho de iniciar leyes", r"iniciativa popular",
            r"firmas de ciudadanos para iniciativa",
        ],
    },
    "popular_consultation": {
        "mechanism_id": "MEX-MECH-006",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "medium",
        "keywords": [
            r"consulta popular", r"consultas populares", r"consulta de trascendencia",
            r"resultado vinculatorio", r"primer domingo de agosto",
            r"cuarenta por ciento.*inscritos", r"dos por ciento.*inscritos",
            r"trascendencia nacional",
        ],
    },
    "recall": {
        "mechanism_id": "MEX-MECH-007",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "medium",
        "keywords": [
            r"revocaci[oó]n de mandato", r"revocar mandato",
            r"revocaci[oó]n del presidente",
            r"tres por ciento.*lista nominal",
            r"diecisiete entidades",
        ],
    },
    "electoral_remedies": {
        "mechanism_id": "MEX-MECH-008",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"medio de impugnaci[oó]n", r"medios de impugnaci[oó]n",
            r"recurso de apelaci[oó]n", r"juicio de revisi[oó]n constitucional",
            r"\bJRC\b", r"\bJDC\b", r"\bRAP\b", r"\bREC\b",
            r"juicio para la protecci[oó]n de derechos pol[ií]tico-electorales",
            r"impugnaci[oó]n electoral", r"recurso de reconsideraci[oó]n",
            r"Sala Superior", r"Sala Regional",
        ],
    },
    "electoral_crimes": {
        "mechanism_id": "MEX-MECH-009",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"delito electoral", r"delitos electorales", r"compra de voto",
            r"coacci[oó]n electoral", r"fraude electoral",
            r"alteraci[oó]n de resultados",
            r"obstaculizar proceso electoral", r"violencia pol[ií]tica",
            r"sanci[oó]n penal",
        ],
    },
    "legislative_petition_or_participation": {
        "mechanism_id": "MEX-MECH-010",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 3,
        "operational_dependence": "medium",
        "keywords": [
            r"derecho de petici[oó]n", r"petici[oó]n legislativa",
            r"participaci[oó]n ciudadana", r"comisi[oó]n de petici[oó]n",
            r"dictaminaci[oó]n de iniciativa",
        ],
    },
    "transparency_and_accountability": {
        "mechanism_id": "MEX-MECH-011",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 4,
        "operational_dependence": "medium",
        "keywords": [
            r"transparencia\b", r"acceso a la informaci[oó]n",
            r"sujeto obligado", r"informaci[oó]n p[uú]blica",
            r"transparencia proactiva", r"fiscalizaci[oó]n\b",
            r"rendici[oó]n de cuentas", r"auditor[ií]a\b",
        ],
    },
    "administrative_responsibility": {
        "mechanism_id": "MEX-MECH-012",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 4,
        "operational_dependence": "medium",
        "keywords": [
            r"responsabilidad administrativa", r"servidor p[uú]blico",
            r"falta administrativa", r"sanci[oó]n administrativa",
            r"inhabilitaci[oó]n\b", r"destituci[oó]n\b",
            r"[oó]rgano interno de control",
        ],
    },
    "electoral_authority_internal_governance": {
        "mechanism_id": "MEX-MECH-013",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"Consejo General", r"consejero electoral",
            r"Junta General Ejecutiva", r"Secretar[ií]a Ejecutiva INE",
            r"estructura org[aá]nica INE", r"[oó]rganos del INE",
            r"reglamento interior INE", r"Sala Superior TEPJF",
            r"magistrado electoral",
        ],
    },
}

# ---------------------------------------------------------------------------
# ACTOR KEYWORDS
# ---------------------------------------------------------------------------

ACTOR_KEYWORDS = {
    "INE": [r"Instituto Nacional Electoral", r"\bINE\b", r"Consejo General"],
    "TEPJF": [r"Tribunal Electoral", r"\bTEPJF\b", r"Sala Superior", r"Sala Regional"],
    "SCJN": [r"Suprema Corte", r"\bSCJN\b"],
    "Congress": [r"Congreso de la Uni[oó]n", r"C[aá]mara de Diputados", r"Senado de la Rep[uú]blica"],
    "Political_parties": [r"partidos pol[ií]ticos", r"partido pol[ií]tico"],
    "Citizens": [r"ciudadanos\b", r"ciudadanas\b", r"ciudadan[ií]a\b"],
    "FGR": [r"Ministerio P[uú]blico", r"Fiscal[ií]a General", r"\bFGR\b", r"\bFEPADE\b"],
    "SFP": [r"Secretar[ií]a de la Funci[oó]n P[uú]blica", r"\bSFP\b", r"[oó]rganos? internos? de control"],
    "OPLEs": [r"organismos p[uú]blicos locales", r"\bOPLE\b", r"\bOPLEs\b"],
}

# ---------------------------------------------------------------------------
# EDITORIAL ANNOTATION PATTERNS (to strip from provision text)
# ---------------------------------------------------------------------------

EDITORIAL_PATTERNS = [
    re.compile(r'P[aá]rrafo\s+(reformado|adicionado|derogado)\s+DOF\s+[\d\-]+', re.IGNORECASE),
    re.compile(r'Fracci[oó]n\s+(reformada|adicionada|derogada)[^\.]*?DOF\s+[\d\-]+', re.IGNORECASE),
    re.compile(r'Inciso\s+(reformado|adicionado|derogado)[^\.]*?DOF\s+[\d\-]+', re.IGNORECASE),
    re.compile(r'Art[ií]culo\s+reformado\s+DOF\s+[\d\-]+', re.IGNORECASE),
    re.compile(r'Denominaci[oó]n[^\.]*?(reformada|adicionada|suprimida|derogada)[^\.]*?DOF\s+[\d\-]+', re.IGNORECASE),
    re.compile(r'Numeral\s+(reformado|adicionado|derogado)[^\.]*?DOF\s+[\d\-]+', re.IGNORECASE),
    re.compile(r'Fe de erratas[^\.]*?DOF[^\.]*', re.IGNORECASE),
    re.compile(r'Reforma\s+DOF\s+[\d\-]+[^\.]*', re.IGNORECASE),
    re.compile(r'Texto vigente', re.IGNORECASE),
    re.compile(r'recupera su vigencia con el texto que ten[ií]a[^\.]*', re.IGNORECASE),
    re.compile(r'Declarad[ao] inv[aá]lid[ao][^\.]*sentencia[^\.]*SCJN[^\.]*', re.IGNORECASE),
    re.compile(r'declaratoria de invalidez[^\.]*', re.IGNORECASE),
    re.compile(r'por sentencia de la SCJN[^\.]*', re.IGNORECASE),
    re.compile(r'notificada para efectos legales[^\.]*', re.IGNORECASE),
    re.compile(r'publicada DOF[^\.]*', re.IGNORECASE),
    re.compile(r'Ley Abrogada DOF[^\.]*', re.IGNORECASE),
    re.compile(r'<!--\s*Page\s+\d+\s*-->', re.IGNORECASE),
]

SCJN_INVALIDITY_PATTERN = re.compile(
    r'(declarad[ao] inv[aá]lid|recupera su vigencia|ley abrogada)',
    re.IGNORECASE
)

# ---------------------------------------------------------------------------
# RIGHT DIMENSION KEYWORDS
# ---------------------------------------------------------------------------

RIGHT_DIMENSION_MAP = [
    (re.compile(r'votar|sufragio|voto\b', re.I), "active_suffrage"),
    (re.compile(r'ser votad|candidat|postulac', re.I), "passive_suffrage"),
    (re.compile(r'asociarse|asociaci[oó]n pol[ií]tica|partido|militante', re.I), "freedom_of_association"),
    (re.compile(r'petici[oó]n|iniciar leyes|iniciativa', re.I), "petition_and_initiative"),
    (re.compile(r'consulta popular|referéndum', re.I), "direct_democracy"),
    (re.compile(r'revocaci[oó]n de mandato', re.I), "recall"),
    (re.compile(r'impugnar|recurso.*electoral|juicio.*electoral', re.I), "electoral_remedy"),
    (re.compile(r'transparencia|acceso a la informaci[oó]n', re.I), "access_to_information"),
    (re.compile(r'no discriminaci[oó]n|igualdad|paridad', re.I), "equality_non_discrimination"),
]

# ---------------------------------------------------------------------------
# OBLIGATION / FACULTY / RESTRICTION / PROCEDURE / REQUIREMENT / REMEDY / SANCTION
# ---------------------------------------------------------------------------

OBLIGATION_RE    = re.compile(r'\bder[aá]\b|\bdeben\b|\btienen la obligaci[oó]n\b|\bcorresponde\b|\bcompete\b', re.I)
FACULTY_RE       = re.compile(r'\bpodr[aá]\b|\bpueden\b|\btiene la facultad\b|\bfaculta\b|\best[aá] facultado\b', re.I)
RESTRICTION_RE   = re.compile(r'\bno podr[aá]\b|\bno pueden\b|\bqueda prohibido\b|\best[aá] prohibido\b|\bse proh[ií]be\b|\bno procede\b', re.I)
REMEDY_RE        = re.compile(r'\bimpugnar\b|\brecurso\b|\bjuicio\b|\bapelaci[oó]n\b|\breconsideraci[oó]n\b|\breparaci[oó]n\b', re.I)
SANCTION_RE      = re.compile(r'\bsanci[oó]n\b|\bpena\b|\bmulta\b|\binhabilitaci[oó]n\b|\bdestituci[oó]n\b|\bprisi[oó]n\b|\bsuspensi[oó]n de derechos\b', re.I)
PROCEDURE_RE     = re.compile(r'\bplazo\b|\bt[eé]rmino\b|\bprocedimiento\b|\bconvocatoria\b|\bregistro\b|\bsolicitud\b|\bverificaci[oó]n\b|\bc[oó]mputo\b|\bresoluci[oó]n\b', re.I)
REQUIREMENT_RE   = re.compile(r'\brequisito\b|\bcondici[oó]n\b|\bacreditar\b|\bdemostrar\b|\bpor ciento\b|\bumbral\b|\bm[ií]nimo de\b', re.I)

# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------

def strip_editorial_annotations(text: str) -> tuple[str, bool]:
    """Remove editorial annotations from provision text.
    Returns (cleaned_text, has_invalidity_note)."""
    has_invalidity = bool(SCJN_INVALIDITY_PATTERN.search(text))
    for pat in EDITORIAL_PATTERNS:
        text = pat.sub("", text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text, has_invalidity


def detect_mechanisms(text: str, source_id: str) -> list[str]:
    """Return list of mechanism names detected in text."""
    text_lower = text.lower()
    found = []
    for mech_name, mech_info in MECHANISMS.items():
        for kw in mech_info["keywords"]:
            if re.search(kw, text, re.IGNORECASE):
                found.append(mech_name)
                break
    return found


def detect_actors(text: str) -> list[str]:
    """Return list of actor labels detected in text."""
    found = []
    for label, patterns in ACTOR_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                found.append(label)
                break
    return found


def detect_right_dimension(text: str) -> str:
    for pattern, right in RIGHT_DIMENSION_MAP:
        if pattern.search(text):
            return right
    return ""


def detect_obligation_or_faculty(text: str) -> str:
    if OBLIGATION_RE.search(text):
        return "obligation"
    if FACULTY_RE.search(text):
        return "faculty"
    return ""


def detect_flag(text: str, pattern: re.Pattern) -> bool:
    return bool(pattern.search(text))


def make_citation(source_id: str, article: str, subdivision: str) -> str:
    parts = [source_id, article]
    if subdivision:
        parts.append(subdivision)
    return " ".join(p for p in parts if p)


def read_metadata(stem: str) -> dict:
    """Try multiple metadata filename patterns."""
    candidates = [
        CORPUS_META_DIR / f"{stem}.metadata.yml",
        CORPUS_META_DIR / f"{stem}_metadata.yml",
        CORPUS_META_DIR / f"{stem}.metadata.yaml",
    ]
    for path in candidates:
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"  [WARN] Could not parse metadata {path}: {e}", file=sys.stderr)
                return {}
    return {}


def determine_gap_types(
    mechanisms: list[str],
    source_type: str,
    anchor_strength: int,
    has_invalidity: bool,
    text: str,
) -> str:
    gaps = []
    if anchor_strength == 0:
        gaps.append("legal_silence")
    if anchor_strength <= 2 and source_type == "electoral_administrative":
        gaps.append("administrative_overdependence")
    if has_invalidity:
        gaps.append("update_review_needed")
    if "citizen_initiative" in mechanisms:
        gaps.append("corpus_incomplete")
    if source_type in ("parliamentary_regulation", "electoral_administrative") and anchor_strength == 3:
        gaps.append("thin_statutory_anchoring")
    if not gaps:
        gaps.append("none_detected")
    return "|".join(gaps)


def determine_manual_review(
    anchor_strength: int,
    has_invalidity: bool,
    mechanisms: list[str],
    source_type: str,
    metadata_missing: bool,
) -> bool:
    if metadata_missing:
        return True
    if has_invalidity:
        return True
    if anchor_strength <= 1:
        return True
    if "citizen_initiative" in mechanisms:
        return True
    if source_type == "electoral_administrative" and anchor_strength <= 2:
        return True
    return False


# ---------------------------------------------------------------------------
# MARKDOWN PARSER
# ---------------------------------------------------------------------------

def parse_provisions_from_markdown(md_path: Path, source_meta: dict, file_metadata: dict) -> list[dict]:
    """
    Parse a Markdown legal file into a list of provision dicts.
    Returns list of provision records.
    """
    source_id        = source_meta.get("source_id", "UNKNOWN")
    source_type      = source_meta.get("source_type", "unknown")
    normative_rank   = source_meta.get("normative_rank", 9)
    legal_anchor_type = source_meta.get("legal_anchor_type", "no_identifiable_anchor")
    base_anchor_strength = source_meta.get("base_anchor_strength", 0)

    source_title = (
        file_metadata.get("title")
        or file_metadata.get("short_title")
        or md_path.stem
    )
    source_file = md_path.name

    provisions = []
    prov_counter = 0

    try:
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERROR] Could not read {md_path}: {e}", file=sys.stderr)
        return provisions

    # Split into lines
    lines = content.split("\n")

    # State tracking
    current_article = ""
    current_subdivision = ""
    current_article_type = ""  # "operative" | "transitory"
    text_buffer = []
    is_transitory_section = False

    def flush_buffer(article, subdivision, article_type, buffer_lines):
        """Convert buffered lines into a provision record."""
        nonlocal prov_counter
        raw_text = " ".join(line.strip() for line in buffer_lines if line.strip())
        if not raw_text or len(raw_text) < 10:
            return None
        cleaned_text, has_invalidity = strip_editorial_annotations(raw_text)
        if not cleaned_text or len(cleaned_text) < 10:
            return None

        prov_counter += 1
        prov_id = f"{source_id}-{prov_counter:04d}"

        mechs = detect_mechanisms(cleaned_text, source_id)
        actors = detect_actors(cleaned_text)
        right_dim = detect_right_dimension(cleaned_text)
        oblig_fac = detect_obligation_or_faculty(cleaned_text)

        has_restriction = detect_flag(cleaned_text, RESTRICTION_RE)
        has_remedy      = detect_flag(cleaned_text, REMEDY_RE)
        has_sanction    = detect_flag(cleaned_text, SANCTION_RE)
        has_procedure   = detect_flag(cleaned_text, PROCEDURE_RE)
        has_requirement = detect_flag(cleaned_text, REQUIREMENT_RE)

        # Determine anchor strength
        anchor_strength = base_anchor_strength
        # Upgrade to 5 if constitutional + mechanisms have known statutory basis
        if source_type == "constitution" and mechs:
            anchor_strength = 5
        # Downgrade for administrative if no statute found
        if source_type == "electoral_administrative":
            anchor_strength = min(anchor_strength, 2)
        # Downgrade for unknown mechanism
        if not mechs and source_type not in ("constitution",):
            anchor_strength = max(anchor_strength - 1, 0)

        # Operational dependence
        if source_type == "electoral_administrative":
            op_dep = "medium"
        elif source_type == "constitution":
            op_dep = "low"
        elif source_type in ("general_law", "federal_law"):
            op_dep = "low"
        elif source_type == "parliamentary_regulation":
            op_dep = "medium"
        else:
            op_dep = "unknown"

        gap_types = determine_gap_types(mechs, source_type, anchor_strength, has_invalidity, cleaned_text)

        metadata_missing = not bool(file_metadata)
        manual_review = determine_manual_review(
            anchor_strength, has_invalidity, mechs, source_type, metadata_missing
        )

        citation = make_citation(source_id, article, subdivision)
        confidence = "medium" if not manual_review else "low"

        return {
            "provision_id": prov_id,
            "country": COUNTRY,
            "source_id": source_id,
            "source_title": source_title,
            "source_file": source_file,
            "source_type": source_type,
            "normative_rank": normative_rank,
            "article": article,
            "subdivision": subdivision,
            "citation": citation,
            "provision_text": cleaned_text[:2000],  # cap length
            "mechanism": "|".join(mechs) if mechs else "",
            "right_dimension": right_dim,
            "actor": "|".join(actors) if actors else "",
            "authority": "|".join(a for a in actors if a in ("INE", "TEPJF", "SCJN", "Congress", "FGR", "SFP")),
            "obligation_or_faculty": oblig_fac,
            "procedure": "yes" if has_procedure else "",
            "requirement": "yes" if has_requirement else "",
            "restriction": "yes" if has_restriction else "",
            "remedy": "yes" if has_remedy else "",
            "sanction_or_accountability": "yes" if has_sanction else "",
            "legal_anchor_type": legal_anchor_type,
            "anchor_strength": anchor_strength,
            "operational_dependence": op_dep,
            "gap_type": gap_types,
            "confidence": confidence,
            "manual_review_required": "true" if manual_review else "false",
            "notes": "has_invalidity_annotation" if has_invalidity else "",
        }

    # Article detection regexes
    # Pattern A: Markdown-headed articles (### Artículo N)
    article_re = re.compile(
        r'^#{1,5}\s+Art[ií]culo\s+(\d+[°o]?\s*(?:[Bb]is|[Tt]er|[Qq]uater)?\s*\d*\.?)',
        re.IGNORECASE
    )
    # Pattern B: Bare article lines without heading markers (INE documents)
    # "Artículo 1." or "Artículo 1" on its own line (possibly with trailing period or text)
    article_bare_re = re.compile(
        r'^Art[ií]culo\s+(\d+[°o]?\s*(?:[Bb]is|[Tt]er|[Qq]uater)?\s*\d*)\.?\s*(.*)',
        re.IGNORECASE
    )
    article_upper_re = re.compile(
        r'^#{1,5}\s+ART[IÍ]CULO\s+([A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ]+)?)',
        re.IGNORECASE
    )
    transitory_re = re.compile(
        r'transitori|TRANSITORI|ARTÍCULO\s+(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|SÉPTIMO|OCTAVO|NOVENO|DÉCIMO)',
        re.IGNORECASE
    )

    fraccion_re = re.compile(r'^([IVX]+\.?)\s+\S', re.IGNORECASE)
    inciso_re   = re.compile(r'^([a-záéíóúñ]\.)(?:\s|\n)')
    numeral_re  = re.compile(r'^(\d+[°o]?)\.\s+\S')

    for line in lines:
        stripped = line.strip()

        # Check for transitory section marker
        if transitory_re.search(stripped) and re.match(r'^#{1,5}\s*', stripped):
            is_transitory_section = True

        # Check article header (Markdown-headed or bare)
        m = article_re.match(stripped) or article_upper_re.match(stripped)
        m_bare = article_bare_re.match(stripped) if not m else None
        matched = m or m_bare
        if matched:
            # Flush previous buffer
            if text_buffer and current_article:
                rec = flush_buffer(current_article, current_subdivision, current_article_type, text_buffer)
                if rec:
                    provisions.append(rec)
            current_article = matched.group(1).strip().rstrip(".")
            current_subdivision = ""
            current_article_type = "transitory" if is_transitory_section else "operative"
            # Article text: for bare pattern, group(2) may contain inline text
            if m_bare:
                inline_text = matched.group(2).strip() if len(matched.groups()) >= 2 else ""
                text_buffer = [inline_text] if inline_text else []
            else:
                heading_text = re.sub(r'^#{1,5}\s+Art[ií]culo\s+[\d°oBisTerQuater\s\.]+', '', stripped, flags=re.I).strip()
                text_buffer = [heading_text] if heading_text else []
            continue

        # Check subdivision (fracción, inciso, numeral)
        if current_article:
            fm = fraccion_re.match(stripped)
            im = inciso_re.match(stripped)
            nm = numeral_re.match(stripped)
            if fm:
                # New fracción — flush and start new buffer at subdivision level
                if text_buffer:
                    rec = flush_buffer(current_article, current_subdivision, current_article_type, text_buffer)
                    if rec:
                        provisions.append(rec)
                current_subdivision = f"Fr. {fm.group(1)}"
                text_buffer = [stripped]
                continue
            elif im:
                if text_buffer:
                    rec = flush_buffer(current_article, current_subdivision, current_article_type, text_buffer)
                    if rec:
                        provisions.append(rec)
                current_subdivision = f"Inc. {im.group(1)}"
                text_buffer = [stripped]
                continue
            elif nm:
                if text_buffer:
                    rec = flush_buffer(current_article, current_subdivision, current_article_type, text_buffer)
                    if rec:
                        provisions.append(rec)
                current_subdivision = f"Num. {nm.group(1)}"
                text_buffer = [stripped]
                continue
            else:
                text_buffer.append(stripped)
        # else: before first article — skip

    # Flush final buffer
    if text_buffer and current_article:
        rec = flush_buffer(current_article, current_subdivision, current_article_type, text_buffer)
        if rec:
            provisions.append(rec)

    return provisions


# ---------------------------------------------------------------------------
# CSV / JSON WRITERS
# ---------------------------------------------------------------------------

def write_csv(path: Path, fieldnames: list[str], rows: list[dict], sep: str = CSV_SEP):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=sep,
                                extrasaction="ignore", quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# TABLE BUILDERS
# ---------------------------------------------------------------------------

def build_country_profile() -> list[dict]:
    rows = [
        {"country": COUNTRY, "field": "country_name", "value": "Mexico", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "iso3", "value": "MEX", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "legal_family", "value": "Civil law (Romano-Germanic); federal constitutional system", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "constitutional_system", "value": "Federal presidential republic", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "constitution_title", "value": "Constitución Política de los Estados Unidos Mexicanos (CPEUM)", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "constitution_last_reform", "value": "2026-04-23", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "electoral_authority_primary", "value": "Instituto Nacional Electoral (INE)", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "electoral_tribunal_primary", "value": "Tribunal Electoral del Poder Judicial de la Federación (TEPJF)", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "suffrage_type", "value": "Universal, direct, secret, equal, free (Art. 35 Fr. I CPEUM)", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "voting_age", "value": "18", "notes": "Art. 34 CPEUM", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "treaty_reception", "value": "Monist with constitutional supremacy; Art. 1 CPEUM (2011 reform) — pro persona", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "key_constitutional_articles", "value": "34,35,36,38,40,41,54,99,108,116,122", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "corpus_note_international_standards", "value": "ICCPR Art.25, ACHR Art.23, HRC GC25, CEDAW Art.7, CRPD Art.29 not in corpus — conventionality analysis requires manual review", "notes": "", "manual_review_required": "true"},
        {"country": COUNTRY, "field": "corpus_note_state_legislation", "value": "Sub-national (state) electoral legislation not in corpus", "notes": "", "manual_review_required": "true"},
        {"country": COUNTRY, "field": "corpus_note_jurisprudence", "value": "No TEPJF/SCJN jurisprudence text files in corpus", "notes": "", "manual_review_required": "true"},
        {"country": COUNTRY, "field": "corpus_note_scjn_2023", "value": "2023 electoral reform (DOF 02-03-2023) substantially invalidated by SCJN (DOF 24-11-2023) — affected provisions restored to pre-reform text", "notes": "", "manual_review_required": "true"},
        {"country": COUNTRY, "field": "pipeline_run_date", "value": "2026-05-18", "notes": "Offline deterministic pipeline", "manual_review_required": "false"},
    ]
    return rows


def build_source_hierarchy() -> list[dict]:
    rows = [
        {
            "country": COUNTRY,
            "source_type": "constitution",
            "rank": 1,
            "function": "Establishes fundamental political rights and institutional design. Directly enforceable.",
            "legal_preparedness_value": "highest",
            "can_create_core_right_or_mechanism": "true",
            "can_create_restrictions": "true",
            "can_create_remedies": "true",
            "caution": "Check SCJN invalidation annotations in consolidated text.",
        },
        {
            "country": COUNTRY,
            "source_type": "general_law",
            "rank": 2,
            "function": "Leyes generales — binding on federal and state levels. LGIPE, LGPP, LGSMIME, LGDE.",
            "legal_preparedness_value": "high",
            "can_create_core_right_or_mechanism": "true",
            "can_create_restrictions": "true",
            "can_create_remedies": "true",
            "caution": "Check SCJN 2023 invalidation annotations. LGSMIME restored from abrogation.",
        },
        {
            "country": COUNTRY,
            "source_type": "federal_law",
            "rank": 3,
            "function": "Leyes federales — federal scope. LFCP, LFRM, LGRA, LGTAIP, LOAPF, LFPA.",
            "legal_preparedness_value": "high",
            "can_create_core_right_or_mechanism": "true",
            "can_create_restrictions": "true",
            "can_create_remedies": "true",
            "caution": "Federal scope only; state-level equivalents not in corpus.",
        },
        {
            "country": COUNTRY,
            "source_type": "parliamentary_regulation",
            "rank": 4,
            "function": "Internal legislative procedure. Reglamentos of Cámara, Senado, Congreso General.",
            "legal_preparedness_value": "medium",
            "can_create_core_right_or_mechanism": "false",
            "can_create_restrictions": "false",
            "can_create_remedies": "false",
            "caution": "Procedural only. Cannot create substantive political rights or electoral mechanisms.",
        },
        {
            "country": COUNTRY,
            "source_type": "electoral_administrative",
            "rank": 5,
            "function": "INE acuerdos, lineamientos, protocolos. Reglamento Interior INE.",
            "legal_preparedness_value": "operational_only",
            "can_create_core_right_or_mechanism": "false",
            "can_create_restrictions": "false",
            "can_create_remedies": "false",
            "caution": "CRITICAL: Cannot create rights or mechanisms. Max anchor_strength=2. Administrative_overdependence if no statute found.",
        },
        {
            "country": COUNTRY,
            "source_type": "jurisprudential_interpretive",
            "rank": 6,
            "function": "SCJN and TEPJF jurisprudence. Not in current corpus.",
            "legal_preparedness_value": "interpretive_complement",
            "can_create_core_right_or_mechanism": "false",
            "can_create_restrictions": "false",
            "can_create_remedies": "false",
            "caution": "No jurisprudence files in corpus. All references require manual_review_required: true.",
        },
    ]
    return rows


def build_mechanism_map() -> list[dict]:
    rows = []
    for mech_name, minfo in MECHANISMS.items():
        rows.append({
            "mechanism_id": minfo["mechanism_id"],
            "country": COUNTRY,
            "mechanism_name": mech_name,
            "legal_preparedness_relevance": minfo["legal_preparedness_relevance"],
            "constitutional_sources": "",
            "statutory_sources": "",
            "regulatory_or_procedural_sources": "",
            "administrative_sources": "",
            "interpretive_sources": "",
            "core_legal_elements": "",
            "likely_legal_anchor_strength": minfo["likely_anchor_strength"],
            "operational_dependence": minfo["operational_dependence"],
            "manual_review_required": "false",
            "notes": "",
        })
    return rows


def build_actor_map() -> list[dict]:
    actor_data = [
        ("MEX-ACT-001", "Instituto Nacional Electoral (INE)", "autonomous_electoral_authority",
         "CPEUM Art. 41; LGIPE",
         "MEX-CPEUM|MEX-LGIPE|MEX-LGPP|MEX-REGINE",
         "vote|right_to_stand_for_election|political_parties|popular_consultation|recall|electoral_authority_internal_governance",
         "Organizes federal elections; voter registration; party oversight", "primary_electoral_administrator", "false"),
        ("MEX-ACT-002", "Tribunal Electoral del Poder Judicial de la Federación (TEPJF)", "electoral_court",
         "CPEUM Art. 99; LGSMIME",
         "MEX-CPEUM|MEX-LGSMIME",
         "electoral_remedies|popular_consultation|recall",
         "Final resolution of electoral disputes; JRC; JDC", "supreme_electoral_tribunal", "false"),
        ("MEX-ACT-003", "Suprema Corte de Justicia de la Nación (SCJN)", "supreme_court",
         "CPEUM Art. 105 Fr. II; Art. 35 Fr. VIII",
         "MEX-CPEUM|MEX-LGIPE",
         "popular_consultation|electoral_remedies",
         "Constitutionality review of electoral laws; consulta popular subject-matter review", "constitutional_review_court", "false"),
        ("MEX-ACT-004", "Congreso de la Unión — Cámara de Diputados", "legislative_body",
         "CPEUM Art. 50–70; Art. 35 Fr. VII",
         "MEX-CPEUM|MEX-REGCD|MEX-REGCONG",
         "citizen_initiative|legislative_petition_or_participation|popular_consultation",
         "Enacts electoral laws; processes citizen initiatives", "legislature", "false"),
        ("MEX-ACT-005", "Congreso de la Unión — Senado de la República", "legislative_body",
         "CPEUM Art. 50–58",
         "MEX-CPEUM|MEX-REGSN",
         "citizen_initiative|legislative_petition_or_participation|popular_consultation",
         "Enacts electoral laws; processes citizen initiatives", "legislature", "false"),
        ("MEX-ACT-006", "Partidos Políticos Nacionales", "political_organization",
         "CPEUM Art. 41; LGPP",
         "MEX-CPEUM|MEX-LGPP|MEX-LGIPE",
         "political_parties|vote|right_to_stand_for_election",
         "Nominate candidates; administer public financing; internal democracy", "political_actor", "false"),
        ("MEX-ACT-007", "Ciudadanos / Ciudadanas", "rights_holder",
         "CPEUM Art. 34–36",
         "MEX-CPEUM|MEX-LGIPE|MEX-LFCP|MEX-LFRM",
         "vote|right_to_stand_for_election|citizen_initiative|popular_consultation|recall|legislative_petition_or_participation",
         "Exercise active and passive suffrage; submit initiatives; vote in consultations", "primary_rights_holder", "false"),
        ("MEX-ACT-008", "Fiscalía General de la República (FGR)", "prosecutorial_authority",
         "CPEUM Art. 102 A; LGDE",
         "MEX-LGDE",
         "electoral_crimes",
         "Prosecute electoral crimes", "electoral_crimes_prosecutor", "false"),
        ("MEX-ACT-009", "Secretaría de la Función Pública / Órganos Internos de Control", "oversight_body",
         "CPEUM Art. 113; LGRA",
         "MEX-LGRA",
         "administrative_responsibility",
         "Administrative oversight; sanctions of public servants", "administrative_oversight", "false"),
        ("MEX-ACT-010", "Organismos Públicos Locales (OPLEs)", "local_electoral_authority",
         "CPEUM Art. 116 Fr. IV; LGIPE",
         "MEX-LGIPE|MEX-CPEUM",
         "vote|right_to_stand_for_election",
         "Organize local elections; local candidate registration", "local_electoral_administrator", "true"),
    ]
    rows = []
    for (aid, name, atype, basis, sources, mechs, funcs, role, review) in actor_data:
        rows.append({
            "actor_id": aid,
            "country": COUNTRY,
            "actor_name": name,
            "actor_type": atype,
            "constitutional_or_statutory_basis": basis,
            "relevant_sources": sources,
            "mechanisms": mechs,
            "functions": funcs,
            "legal_preparedness_role": role,
            "manual_review_required": review,
            "notes": "",
        })
    return rows


def build_mechanism_sources(all_provisions: list[dict]) -> list[dict]:
    """Build mechanism_sources table from extracted provisions."""
    seen = set()
    rows = []
    for prov in all_provisions:
        mechs = prov["mechanism"].split("|") if prov["mechanism"] else []
        for mech in mechs:
            mech = mech.strip()
            if not mech:
                continue
            key = (prov["source_id"], mech)
            if key in seen:
                continue
            seen.add(key)
            minfo = MECHANISMS.get(mech, {})
            rows.append({
                "country": COUNTRY,
                "mechanism_id": minfo.get("mechanism_id", ""),
                "mechanism_name": mech,
                "source_id": prov["source_id"],
                "source_title": prov["source_title"],
                "source_file": prov["source_file"],
                "source_type": prov["source_type"],
                "normative_rank": prov["normative_rank"],
                "role_in_mechanism": "primary" if prov["normative_rank"] <= 3 else "supporting",
                "legal_anchor_type": prov["legal_anchor_type"],
                "is_core_source": "true" if prov["normative_rank"] <= 3 else "false",
                "manual_review_required": prov["manual_review_required"],
                "notes": "",
            })
    return rows


def build_actor_mechanism_edges(all_provisions: list[dict]) -> list[dict]:
    """Build actor-mechanism edges from extracted provisions."""
    seen = set()
    rows = []
    actor_id_map = {
        "INE": "MEX-ACT-001",
        "TEPJF": "MEX-ACT-002",
        "SCJN": "MEX-ACT-003",
        "Congress": "MEX-ACT-004",
        "Political_parties": "MEX-ACT-006",
        "Citizens": "MEX-ACT-007",
        "FGR": "MEX-ACT-008",
        "SFP": "MEX-ACT-009",
        "OPLEs": "MEX-ACT-010",
    }
    for prov in all_provisions:
        mechs = prov["mechanism"].split("|") if prov["mechanism"] else []
        actors = prov["actor"].split("|") if prov["actor"] else []
        for mech in mechs:
            mech = mech.strip()
            if not mech:
                continue
            minfo = MECHANISMS.get(mech, {})
            for actor in actors:
                actor = actor.strip()
                if not actor:
                    continue
                key = (actor, mech, prov["source_id"])
                if key in seen:
                    continue
                seen.add(key)
                rel_type = prov["obligation_or_faculty"] or "reference"
                rows.append({
                    "country": COUNTRY,
                    "actor_id": actor_id_map.get(actor, f"MEX-ACT-{actor}"),
                    "actor_name": actor,
                    "mechanism_id": minfo.get("mechanism_id", ""),
                    "mechanism_name": mech,
                    "relationship_type": rel_type,
                    "source_id": prov["source_id"],
                    "citation": prov["citation"],
                    "legal_anchor_type": prov["legal_anchor_type"],
                    "anchor_strength": prov["anchor_strength"],
                    "manual_review_required": prov["manual_review_required"],
                    "notes": "",
                })
    return rows


def build_validation_notes() -> list[dict]:
    data = [
        ("VN-001", "corpus_gap", "high", "All Mexico corpus", "electoral_remedies|political_parties|vote",
         "No TEPJF/SCJN jurisprudence in corpus. Interpretive anchor incomplete.",
         "Add TEPJF tesis for key mechanisms in future update.", "true"),
        ("VN-002", "corpus_gap", "high", "N/A", "all",
         "ICCPR Art.25, ACHR Art.23, HRC GC25, CEDAW Art.7, CRPD Art.29 not in corpus.",
         "Manual conventionality review required.", "true"),
        ("VN-003", "legal_complexity", "high",
         "ley_general_instituciones_procedimientos_electorales.md|ley_general_medios_impugnacion_electoral.md|ley_general_partidos_politicos.md",
         "vote|right_to_stand_for_election|political_parties|electoral_remedies",
         "2023 electoral reform substantially invalidated by SCJN (DOF 24-11-2023). LGSMIME temporarily abrogated and restored.",
         "Exclude invalidated text. Set manual_review_required for affected provisions.", "true"),
        ("VN-004", "corpus_gap", "medium", "N/A", "vote|right_to_stand_for_election|electoral_authority_internal_governance",
         "Sub-national (state) electoral legislation not in corpus.",
         "Flag federal_or_subnational_implementation_gap for state-level provisions.", "true"),
        ("VN-005", "anchoring_caution", "medium",
         "ine_consulta_popular_2021.md|ine_revocacion_mandato_2022.md|reglamento_interior_ine_2025.md",
         "popular_consultation|recall|electoral_authority_internal_governance",
         "INE lineamientos are process-specific and operational only. Max anchor_strength=2.",
         "Classify as electoral_administrative. Flag administrative_overdependence if no statute.", "false"),
        ("VN-006", "corpus_gap", "medium", "N/A", "citizen_initiative",
         "No dedicated citizen initiative law in corpus. Art. 35 Fr. VII refers to 'Ley del Congreso'.",
         "Verify if Ley de Iniciativa Ciudadana exists outside corpus. Flag corpus_incomplete.", "true"),
        ("VN-007", "scope_note", "low", "mexico_federal_budget_and_fiscal_responsibility_law_lfprh_2026.md|mexico_planning_law_lplan_2026.md",
         "transparency_and_accountability",
         "LFPRH and Ley de Planeación have limited direct political rights relevance.",
         "Extract only INE/TEPJF budget and accountability provisions.", "false"),
        ("VN-008", "scope_note", "low", "conversion_log.md", "all",
         "conversion_log.md is an editorial log file, not a legal source.",
         "Skip entirely in pipeline.", "false"),
        ("VN-009", "accessibility_gap", "medium", "all",
         "vote|right_to_stand_for_election|popular_consultation|recall",
         "CRPD Art. 29 requires accessible voting. No accessibility provisions in corpus.",
         "Flag accessibility_gap. Manual review for CRPD compliance.", "true"),
        ("VN-010", "anchoring_caution", "low", "all", "all",
         "Conservative defaults applied throughout. If classification uncertain, manual_review_required=true.",
         "Expert legal review of all provisions with anchor_strength<=2.", "false"),
    ]
    rows = []
    for i, (nid, ntype, sev, src, mech, desc, rec, review) in enumerate(data, 1):
        rows.append({
            "country": COUNTRY,
            "note_id": nid,
            "note_type": ntype,
            "severity": sev,
            "affected_source": src,
            "affected_mechanism": mech,
            "description": desc,
            "recommended_action": rec,
            "manual_review_required": review,
        })
    return rows


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("NormTrace Political Rights — Mexico Legal Brain Pipeline")
    print("=" * 70)

    # Create output directories
    OUT_CSV_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Step 1: Discover and pair Markdown + metadata files
    # -----------------------------------------------------------------------
    print("\n[1] Discovering corpus files...")

    md_files = sorted([
        f for f in CORPUS_MD_DIR.glob("*.md")
        if f.name not in SKIP_FILES
    ])

    print(f"    Markdown files found: {len(md_files)}")

    meta_files = sorted(CORPUS_META_DIR.glob("*.yml"))
    print(f"    Metadata files found: {len(meta_files)}")

    # Build metadata lookup by stem
    meta_lookup = {}
    for mf in meta_files:
        # Strip .metadata.yml or _metadata.yml suffix to get stem
        stem = mf.name
        for suffix in (".metadata.yml", "_metadata.yml", ".metadata.yaml"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        else:
            stem = mf.stem
        meta_lookup[stem] = mf

    print(f"    Metadata stems indexed: {len(meta_lookup)}")

    # -----------------------------------------------------------------------
    # Step 2: Process each Markdown file
    # -----------------------------------------------------------------------
    print("\n[2] Parsing provisions...")

    all_provisions = []
    md_processed = 0
    meta_matched = 0
    meta_missing_stems = []
    warnings = []

    for md_path in md_files:
        stem = md_path.stem

        # Pair with metadata
        file_metadata = {}
        if stem in meta_lookup:
            file_metadata = read_metadata(stem)
            if file_metadata:
                meta_matched += 1
            else:
                warnings.append(f"Metadata parse failed: {stem}")
        else:
            meta_missing_stems.append(stem)
            warnings.append(f"No metadata file found for: {stem}")

        # Get source registry entry
        source_meta = SOURCE_REGISTRY.get(stem)
        if source_meta is None:
            warnings.append(f"Source not in registry, using defaults: {stem}")
            source_meta = {
                "source_id": f"MEX-{stem[:12].upper()}",
                "source_type": "unknown",
                "normative_rank": 9,
                "legal_anchor_type": "no_identifiable_anchor",
                "base_anchor_strength": 0,
            }

        # Parse provisions
        provs = parse_provisions_from_markdown(md_path, source_meta, file_metadata)
        all_provisions.extend(provs)
        md_processed += 1

        prov_count = len(provs)
        review_count = sum(1 for p in provs if p["manual_review_required"] == "true")
        print(f"    {md_path.name}: {prov_count} provisions ({review_count} flagged for review)")

    print(f"\n    Total provisions extracted: {len(all_provisions)}")
    print(f"    MD files processed: {md_processed}")
    print(f"    Metadata matched: {meta_matched} / {md_processed}")

    if meta_missing_stems:
        print(f"\n    [WARN] Missing metadata for: {', '.join(meta_missing_stems)}")

    # -----------------------------------------------------------------------
    # Step 3: Build derived tables
    # -----------------------------------------------------------------------
    print("\n[3] Building derived tables...")

    country_profile_rows  = build_country_profile()
    source_hierarchy_rows = build_source_hierarchy()
    mechanism_map_rows    = build_mechanism_map()
    actor_map_rows        = build_actor_map()
    mechanism_source_rows = build_mechanism_sources(all_provisions)
    actor_mech_edge_rows  = build_actor_mechanism_edges(all_provisions)
    validation_note_rows  = build_validation_notes()

    print(f"    Country profile rows: {len(country_profile_rows)}")
    print(f"    Source hierarchy rows: {len(source_hierarchy_rows)}")
    print(f"    Mechanism map rows: {len(mechanism_map_rows)}")
    print(f"    Actor map rows: {len(actor_map_rows)}")
    print(f"    Mechanism-source rows: {len(mechanism_source_rows)}")
    print(f"    Actor-mechanism edges: {len(actor_mech_edge_rows)}")
    print(f"    Validation notes: {len(validation_note_rows)}")

    # -----------------------------------------------------------------------
    # Step 4: Export CSV
    # -----------------------------------------------------------------------
    print("\n[4] Writing CSV files...")

    csv_files = {
        "mexico_country_profile.csv": (
            ["country", "field", "value", "notes", "manual_review_required"],
            country_profile_rows,
        ),
        "mexico_source_hierarchy.csv": (
            ["country", "source_type", "rank", "function",
             "legal_preparedness_value", "can_create_core_right_or_mechanism",
             "can_create_restrictions", "can_create_remedies", "caution"],
            source_hierarchy_rows,
        ),
        "mexico_mechanism_map.csv": (
            ["mechanism_id", "country", "mechanism_name", "legal_preparedness_relevance",
             "constitutional_sources", "statutory_sources", "regulatory_or_procedural_sources",
             "administrative_sources", "interpretive_sources", "core_legal_elements",
             "likely_legal_anchor_strength", "operational_dependence", "manual_review_required", "notes"],
            mechanism_map_rows,
        ),
        "mexico_actor_map.csv": (
            ["actor_id", "country", "actor_name", "actor_type",
             "constitutional_or_statutory_basis", "relevant_sources", "mechanisms",
             "functions", "legal_preparedness_role", "manual_review_required", "notes"],
            actor_map_rows,
        ),
        "mexico_legal_provisions.csv": (
            ["provision_id", "country", "source_id", "source_title", "source_file",
             "source_type", "normative_rank", "article", "subdivision", "citation",
             "provision_text", "mechanism", "right_dimension", "actor", "authority",
             "obligation_or_faculty", "procedure", "requirement", "restriction",
             "remedy", "sanction_or_accountability", "legal_anchor_type",
             "anchor_strength", "operational_dependence", "gap_type",
             "confidence", "manual_review_required", "notes"],
            all_provisions,
        ),
        "mexico_mechanism_sources.csv": (
            ["country", "mechanism_id", "mechanism_name", "source_id", "source_title",
             "source_file", "source_type", "normative_rank", "role_in_mechanism",
             "legal_anchor_type", "is_core_source", "manual_review_required", "notes"],
            mechanism_source_rows,
        ),
        "mexico_actor_mechanism_edges.csv": (
            ["country", "actor_id", "actor_name", "mechanism_id", "mechanism_name",
             "relationship_type", "source_id", "citation", "legal_anchor_type",
             "anchor_strength", "manual_review_required", "notes"],
            actor_mech_edge_rows,
        ),
        "mexico_validation_notes.csv": (
            ["country", "note_id", "note_type", "severity", "affected_source",
             "affected_mechanism", "description", "recommended_action", "manual_review_required"],
            validation_note_rows,
        ),
    }

    csv_out_paths = []
    for filename, (fields, rows) in csv_files.items():
        out_path = OUT_CSV_DIR / filename
        write_csv(out_path, fields, rows)
        print(f"    Wrote: {out_path.relative_to(REPO_ROOT)} ({len(rows)} rows)")
        csv_out_paths.append(out_path)

    # -----------------------------------------------------------------------
    # Step 5: Export JSON
    # -----------------------------------------------------------------------
    print("\n[5] Writing JSON files...")

    json_files = {
        "country_profile.json":    country_profile_rows,
        "source_hierarchy.json":   source_hierarchy_rows,
        "mechanism_map.json":      mechanism_map_rows,
        "actor_map.json":          actor_map_rows,
        "legal_provisions.json":   all_provisions,
        "mechanism_sources.json":  mechanism_source_rows,
        "actor_mechanism_edges.json": actor_mech_edge_rows,
        "validation_notes.json":   validation_note_rows,
    }

    json_out_paths = []
    for filename, data in json_files.items():
        out_path = OUT_JSON_DIR / filename
        write_json(out_path, data)
        print(f"    Wrote: {out_path.relative_to(REPO_ROOT)} ({len(data)} records)")
        json_out_paths.append(out_path)

    # -----------------------------------------------------------------------
    # Step 6: Summary report
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY REPORT")
    print("=" * 70)
    print(f"  Status:                    SUCCESS")
    print(f"  MD files processed:        {md_processed}")
    print(f"  Metadata files matched:    {meta_matched}")
    print(f"  Metadata files missing:    {len(meta_missing_stems)}")
    print(f"  Provisions extracted:      {len(all_provisions)}")

    mechs_found = [p["mechanism"] for p in all_provisions if p["mechanism"]]
    mech_set = set()
    for m in mechs_found:
        for part in m.split("|"):
            if part.strip():
                mech_set.add(part.strip())
    print(f"  Mechanisms detected:       {len(mech_set)} ({', '.join(sorted(mech_set))})")
    print(f"  Mechanism-source rows:     {len(mechanism_source_rows)}")
    print(f"  Actor-mechanism edges:     {len(actor_mech_edge_rows)}")

    manual_review_count = sum(1 for p in all_provisions if p["manual_review_required"] == "true")
    print(f"  Provisions requiring manual review: {manual_review_count}")

    admin_overdep = sum(1 for p in all_provisions if "administrative_overdependence" in p.get("gap_type", ""))
    print(f"  Administrative overdependence flags: {admin_overdep}")

    invalidity = sum(1 for p in all_provisions if "has_invalidity_annotation" in p.get("notes", ""))
    print(f"  Provisions with SCJN invalidity annotation: {invalidity}")

    print(f"\n  CSV outputs ({len(csv_out_paths)}):")
    for p in csv_out_paths:
        print(f"    {p.relative_to(REPO_ROOT)}")

    print(f"\n  JSON outputs ({len(json_out_paths)}):")
    for p in json_out_paths:
        print(f"    {p.relative_to(REPO_ROOT)}")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    [WARN] {w}")

    print("\n  VALIDATION FLAGS:")
    print(f"    - No TEPJF/SCJN jurisprudence in corpus — manual_review_required: true")
    print(f"    - No international standards (ICCPR Art.25, ACHR Art.23) in corpus")
    print(f"    - 2023 SCJN electoral reform invalidation affects LGIPE, LGSMIME, LGPP")
    print(f"    - Sub-national (state) legislation not in corpus")
    print(f"    - citizen_initiative: thin_statutory_anchoring / corpus_incomplete flagged")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
