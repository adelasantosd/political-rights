#!/usr/bin/env python3
"""
build_costa_rica_legal_brain_tables.py
NormTrace Political Rights — Costa Rica Offline Legal Brain Pipeline

Reads Markdown legal sources and metadata from corpus/costa_rica/,
extracts provisions using deterministic rules (no LLM at runtime), detects
mechanisms/actors/rights/obligations, assigns anchoring classifications,
and exports precomputed CSV and JSON tables for the webapp.

Usage:
    python3 scripts/build_costa_rica_legal_brain_tables.py

Outputs:
    03_tables/country_legal_brains/costa_rica/  (CSV files)
    05_webapp/public/data/legal_brains/costa_rica/  (JSON files)

CRITICAL INSTITUTIONAL NOTE:
    The Tribunal Supremo de Elecciones (TSE) in Costa Rica has constitutional
    rank equivalent to the three Branches of Government (CPCR Art. 9). Its
    decisions are non-reviewable (Art. 103). It is NOT modeled as an
    administrative body. TSE reglamentos implementing a statutory mandate are
    classified as regulatory_or_legislative_procedural, NOT electoral_administrative.
    Only the Reglamento Autónomo de Servicios TSE (internal HR) is classified
    electoral_administrative.
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
CORPUS_MD_DIR   = REPO_ROOT / "corpus" / "costa_rica" / "md"
CORPUS_META_DIR = REPO_ROOT / "corpus" / "costa_rica" / "metadata"
BRAIN_DIR       = REPO_ROOT / "02_country_legal_brains" / "costa_rica"
OUT_CSV_DIR     = REPO_ROOT / "03_tables" / "country_legal_brains" / "costa_rica"
OUT_JSON_DIR    = REPO_ROOT / "05_webapp" / "public" / "data" / "legal_brains" / "costa_rica"

CSV_SEP = ";"
COUNTRY = "Costa Rica"

# Files to skip entirely (image-based or non-legal)
SKIP_FILES = {
    "ley_general_administracion_publica.md",  # image-based — no extractable text
    "conversion_log.md",
}

# ---------------------------------------------------------------------------
# SOURCE REGISTRY
# Maps filename stems to source-level metadata classifications.
# All CR sources and their normative positions per costa_rica_source_hierarchy.yml
# ---------------------------------------------------------------------------

SOURCE_REGISTRY = {
    # CPCR — Constitución Política de Costa Rica
    "constitucion_politica_costa_rica": {
        "source_id": "CRC-CPOL",
        "source_type": "constitution",
        "normative_rank": 1,
        "legal_anchor_type": "constitutional",
        "base_anchor_strength": 5,
        "manual_review_required_default": False,
    },
    # LOTSRC — Ley Orgánica TSE y Registro Civil
    "ley_organica_tse_registro_civil": {
        "source_id": "CRC-LOTSRC",
        "source_type": "organic_law",
        "normative_rank": 2,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
        "manual_review_required_default": False,
    },
    # CE — Código Electoral
    "codigo_electoral_costa_rica": {
        "source_id": "CRC-CE",
        "source_type": "codigo_ley",
        "normative_rank": 3,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
        "manual_review_required_default": False,
    },
    # LREF — Ley de Regulación del Referéndum
    "ley_regulacion_referendum": {
        "source_id": "CRC-LREF",
        "source_type": "statutory_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
        "manual_review_required_default": False,
    },
    # LIP — Ley de Iniciativa Popular
    "ley_iniciativa_popular": {
        "source_id": "CRC-LIP",
        "source_type": "statutory_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
        "manual_review_required_default": False,
    },
    # LJC — Ley de la Jurisdicción Constitucional
    "ley_jurisdiccion_constitucional": {
        "source_id": "CRC-LJC",
        "source_type": "statutory_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
        "manual_review_required_default": False,
    },
    # LCPREF — Ley Consulta Previa y Facultativa de Constitucionalidad en Referéndum
    "ley_consulta_previa_facultativa_referendum": {
        "source_id": "CRC-LCPREF",
        "source_type": "statutory_law",
        "normative_rank": 4,
        "legal_anchor_type": "statutory",
        "base_anchor_strength": 4,
        "manual_review_required_default": True,  # thin corpus coverage
    },
    # REGREF — Reglamento para los Procesos de Referéndum (TSE)
    "procesos_referendum": {
        "source_id": "CRC-REGREF",
        "source_type": "tse_reglamento",
        "normative_rank": 5,
        "legal_anchor_type": "regulatory_or_legislative_procedural",
        "base_anchor_strength": 3,
        "manual_review_required_default": False,
    },
    # REGIP — Reglamento aplicación art. 3 Ley Iniciativa Popular (TSE)
    "reglamento_aplicacion_articulo_3_ley_iniciativa_popular": {
        "source_id": "CRC-REGIP",
        "source_type": "tse_reglamento",
        "normative_rank": 5,
        "legal_anchor_type": "regulatory_or_legislative_procedural",
        "base_anchor_strength": 3,
        "manual_review_required_default": False,
    },
    "reglamento_autonomo_servicios_tse": {
        "source_id": "CRC-RATSRE",
        "source_type": "administrative_reglamento",
        "normative_rank": 7,
        "legal_anchor_type": "electoral_administrative",
        "base_anchor_strength": 1,
        "manual_review_required_default": False,
    },
    # RAL — Reglamento de la Asamblea Legislativa (commented compilation)
    "reglamento_asamblea_legislativa_comentado": {
        "source_id": "CRC-RAL",
        "source_type": "legislative_reglamento",
        "normative_rank": 6,
        "legal_anchor_type": "regulatory_or_legislative_procedural",
        "base_anchor_strength": 2,
        "manual_review_required_default": True,  # commentary contamination risk
    },
}

# ---------------------------------------------------------------------------
# MECHANISM DEFINITIONS — 12 Costa Rica mechanisms
# Costa Rica-specific; do NOT copy from Mexico.
# ---------------------------------------------------------------------------

MECHANISMS = {
    "vote": {
        "mechanism_id": "CRC-MECH-001",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"sufragio\b", r"votar\b", r"votaci[oó]n\b", r"\bvoto\b",
            r"padr[oó]n electoral", r"lista de electores",
            r"junta[s]?\s+(receptora|electoral)",
            r"c[eé]dula de identidad", r"c[eé]dula.*identidad",
            r"elecciones? populares?", r"sufragio universal",
            r"sufragio secreto", r"sufragio directo",
            r"jornada electoral", r"escrutinio",
            r"registro civil.*elector",
        ],
    },
    "right_to_stand_for_election": {
        "mechanism_id": "CRC-MECH-002",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"candidat[ao]\b", r"candidatura\b", r"ser elegid[ao]\b",
            r"inscri[bp][ci]i[oó]n.*candidat", r"paridad",
            r"alternancia por sexo", r"n[oó]mina.*elecci[oó]n",
            r"requisitos.*diputado", r"elegibilidad",
            r"inelegibilidad", r"no pueden ser elegidos",
        ],
    },
    "political_parties": {
        "mechanism_id": "CRC-MECH-003",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"partido pol[ií]tico", r"partidos pol[ií]ticos",
            r"deuda pol[ií]tica", r"financiamiento.*partido",
            r"contribuci[oó]n.*partido", r"inscripci[oó]n.*partido",
            r"estatutos.*partido", r"democracia interna",
            r"agruparse.*partido", r"cero coma diecinueve",
            r"0[,.]19.*producto interno",
        ],
    },
    "citizen_initiative": {
        "mechanism_id": "CRC-MECH-004",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "medium",
        "keywords": [
            r"iniciativa popular", r"cinco por ciento.*padr[oó]n",
            r"5%.*padr[oó]n", r"iniciativa.*ciudadanos",
            r"firmas.*iniciativa", r"derecho de iniciativa",
            r"ley de iniciativa", r"recolect.*firmas",
        ],
    },
    "referendum": {
        "mechanism_id": "CRC-MECH-005",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "medium",
        "keywords": [
            r"refer[eé]ndum\b", r"referendo\b", r"consulta popular",
            r"consulta.*ciudadana", r"cuarenta por ciento",
            r"40%.*inscritos", r"potestad.*legislar.*pueblo",
            r"delegaci[oó]n.*legislativa", r"convocatoria.*refer[eé]ndum",
        ],
    },
    "consultative_referendum_or_preliminary_consultation": {
        "mechanism_id": "CRC-MECH-006",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 4,
        "operational_dependence": "medium",
        "keywords": [
            r"consulta previa.*constitucionalidad",
            r"consulta facultativa",
            r"sala (constitucional|iv).*refer[eé]ndum",
            r"constitucionalidad.*refer[eé]ndum",
        ],
    },
    "electoral_remedies": {
        "mechanism_id": "CRC-MECH-007",
        "legal_preparedness_relevance": "core",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"resoluciones.*tribunal", r"apelaci[oó]n.*electoral",
            r"recurso.*electoral", r"alzada\b",
            r"impugnaci[oó]n.*electoral", r"prevaricato",
            r"no tienen recurso", r"interpretar.*exclusiva.*obligatoria",
            r"interpretaci[oó]n.*electoral",
        ],
    },
    "constitutional_remedies": {
        "mechanism_id": "CRC-MECH-008",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"amparo\b", r"h[aá]beas corpus",
            r"acci[oó]n de inconstitucionalidad",
            r"sala constitucional", r"jurisdicci[oó]n constitucional",
            r"derechos fundamentales", r"supremac[ií]a constitucional",
        ],
    },
    "legislative_petition_or_participation": {
        "mechanism_id": "CRC-MECH-009",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 4,
        "operational_dependence": "medium",
        "keywords": [
            r"derecho de petici[oó]n", r"iniciativa.*asamblea",
            r"proyecto de ley", r"formaci[oó]n de las leyes",
            r"debate.*plenario", r"comisi[oó]n.*asamblea",
        ],
    },
    "transparency_and_accountability": {
        "mechanism_id": "CRC-MECH-010",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 4,
        "operational_dependence": "medium",
        "keywords": [
            r"transparencia\b", r"fiscalizaci[oó]n\b",
            r"rendici[oó]n de cuentas", r"publicidad.*contribuciones",
            r"gastos.*partido", r"control.*financiero.*partido",
            r"cauci[oó]n.*partido", r"comprobar.*gastos",
        ],
    },
    "electoral_authority_internal_governance": {
        "mechanism_id": "CRC-MECH-011",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"tribunal supremo de elecciones",
            r"\bTSE\b",
            r"magistrados.*elecciones", r"magistrado.*propietario",
            r"magistrado.*suplente", r"composici[oó]n.*tribunal",
            r"independencia.*tribunal", r"cometido.*tribunal",
        ],
    },
    "civil_registry_electoral_functions": {
        "mechanism_id": "CRC-MECH-012",
        "legal_preparedness_relevance": "secondary",
        "likely_anchor_strength": 5,
        "operational_dependence": "low",
        "keywords": [
            r"registro civil", r"estado civil",
            r"listas de electores", r"c[eé]dula.*identidad",
            r"padr[oó]n\b", r"nacionalidad.*registro",
            r"ciudadan[ií]a.*registro",
        ],
    },
}

# ---------------------------------------------------------------------------
# ACTOR KEYWORDS — Costa Rica actors only
# ---------------------------------------------------------------------------

ACTOR_KEYWORDS = {
    "TSE": [
        r"Tribunal Supremo de Elecciones",
        r"\bTSE\b",
        r"magistrado.*elecciones",
    ],
    "Registro_Civil": [
        r"Registro Civil",
        r"padr[oó]n electoral",
    ],
    "Juntas_Electorales": [
        r"Juntas? Electorales?",
        r"Juntas? Receptoras?",
    ],
    "Sala_Constitucional": [
        r"Sala Constitucional",
        r"Sala IV",
        r"jurisdicci[oó]n constitucional",
    ],
    "Asamblea_Legislativa": [
        r"Asamblea Legislativa",
        r"diputados\b",
        r"Congreso.*Costa Rica",
    ],
    "Partidos_Politicos": [
        r"partido pol[ií]tico",
        r"partidos pol[ií]ticos",
    ],
    "Ciudadanos": [
        r"ciudadanos\b", r"ciudadanas\b",
        r"ciudadan[ií]a\b", r"electores\b",
    ],
    "Poder_Ejecutivo": [
        r"Poder Ejecutivo",
        r"Presidente.*Rep[uú]blica",
        r"Gobierno.*Costa Rica",
    ],
    "Corte_Suprema": [
        r"Corte Suprema de Justicia",
        r"Poder Judicial",
    ],
}

# ---------------------------------------------------------------------------
# EDITORIAL ANNOTATION PATTERNS — Costa Rica
# Strips reform annotations and editorial markers from provision text
# ---------------------------------------------------------------------------

EDITORIAL_PATTERNS = [
    # Constitutional reform annotations: (Reforma Constitucional N.° XXXX ...)
    re.compile(r'\(Reforma\s+Constitucional[^)]*\)', re.IGNORECASE),
    re.compile(r'\(Reforma\s+[^)]+\)', re.IGNORECASE),
    re.compile(r'\(Adicionado[^)]+\)', re.IGNORECASE),
    re.compile(r'\(Derogado[^)]+\)', re.IGNORECASE),
    re.compile(r'\(Modificado[^)]+\)', re.IGNORECASE),
    re.compile(r'\(ver art[ií]culo[^)]*\)', re.IGNORECASE),
    # RAL commented source patterns
    re.compile(r'Votos?\s+Sala\s+Constitucional\b[^\n]*', re.IGNORECASE),
    re.compile(r'\b\d{4}-\d{4,5}\b'),  # TSE/Sala IV resolution numbers like 1990-00392
    re.compile(r'Acta\s+de\s+la\s+Sesi[oó]n\s+Plenaria[^\n]*', re.IGNORECASE),
    re.compile(r'RAL\s+20\d{2}\b[^\n]*', re.IGNORECASE),
    re.compile(r'ISBN:[^\n]*', re.IGNORECASE),
    re.compile(r'\bCEDIL\b[^\n]*', re.IGNORECASE),
    # Page markers
    re.compile(r'<!--\s*Page\s+\d+\s*-->', re.IGNORECASE),
    # Extraction notes
    re.compile(r'\[Extraction note[^\]]*\]', re.IGNORECASE),
    # Roman numeral page headers (iv vi xii, etc.)
    re.compile(r'^[ivxlcdmIVXLCDM]+\s+[ivxlcdmIVXLCDM]+\s*$', re.MULTILINE),
]

RAL_COMMENTARY_RE = re.compile(
    r'(Votos?\s+Sala|'
    r'\d{4}-\d{4,5}|'
    r'Acta\s+de\s+la\s+Sesi[oó]n|'
    r'RAL\s+20\d{2}|'
    r'ISBN:|CEDIL)',
    re.IGNORECASE
)

# ---------------------------------------------------------------------------
# RIGHT DIMENSION KEYWORDS
# ---------------------------------------------------------------------------

RIGHT_DIMENSION_MAP = [
    (re.compile(r'sufragio|votar|voto\b', re.I), "active_suffrage"),
    (re.compile(r'candidat|ser elegid|inscripci[oó]n.*candidat', re.I), "passive_suffrage"),
    (re.compile(r'partido|agruparse|pluralismo', re.I), "freedom_of_association"),
    (re.compile(r'iniciativa popular|derecho.*iniciativa', re.I), "petition_and_initiative"),
    (re.compile(r'refer[eé]ndum|consulta popular', re.I), "direct_democracy"),
    (re.compile(r'amparo|h[aá]beas corpus', re.I), "constitutional_remedy"),
    (re.compile(r'petici[oó]n|proyecto de ley', re.I), "petition_and_legislative_participation"),
    (re.compile(r'paridad|igualdad|no discriminaci[oó]n', re.I), "equality_non_discrimination"),
    (re.compile(r'transparencia|publicidad', re.I), "access_to_information"),
]

# ---------------------------------------------------------------------------
# SEMANTIC DETECTION PATTERNS
# ---------------------------------------------------------------------------

OBLIGATION_RE  = re.compile(r'\bder[aá]\b|\bdeben\b|\bcorresponde\b|\bcompete\b|\bobligatorio\b|\bes obligaci[oó]n\b', re.I)
FACULTY_RE     = re.compile(r'\bpodr[aá]\b|\bpueden\b|\btiene la facultad\b|\bpuede\b|\bfaculta\b', re.I)
RESTRICTION_RE = re.compile(r'\bno podr[aá]\b|\bno pueden\b|\bprohibido\b|\bse proh[ií]be\b|\bno procede\b|\bno tendr[aá]\b', re.I)
REMEDY_RE      = re.compile(r'\bamparo\b|\bh[aá]beas corpus\b|\bapelaci[oó]n\b|\brecurso\b|\balzada\b|\brecurrir\b|\bimpugnar\b', re.I)
SANCTION_RE    = re.compile(r'\bsanci[oó]n\b|\bpena\b|\bmulta\b|\bdestituci[oó]n\b|\binhabilit|\bprevaricato\b', re.I)
PROCEDURE_RE   = re.compile(r'\bplazo\b|\bt[eé]rmino\b|\bprocedimiento\b|\bconvocatoria\b|\bregistro\b|\bsolicitud\b|\bverificaci[oó]n\b|\brequisito\b', re.I)
REQUIREMENT_RE = re.compile(r'\brequisito\b|\bporcentaje\b|\b5%\b|\bcinco por ciento\b|\b40%\b|\bcuarenta por ciento\b|\bacreditar\b', re.I)

# ---------------------------------------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------------------------------------

def strip_editorial_annotations(text: str) -> str:
    """Remove editorial annotations from provision text."""
    for pat in EDITORIAL_PATTERNS:
        text = pat.sub("", text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text


def is_ral_commentary_line(line: str) -> bool:
    """Return True if line appears to be RAL commentary, not operative text."""
    return bool(RAL_COMMENTARY_RE.search(line))


def detect_mechanisms(text: str) -> list:
    """Return list of mechanism names detected in text."""
    found = []
    for mech_name, mech_info in MECHANISMS.items():
        for kw in mech_info["keywords"]:
            if re.search(kw, text, re.IGNORECASE):
                found.append(mech_name)
                break
    return found


def detect_actors(text: str) -> list:
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


def determine_anchor_strength(
    source_type: str,
    base_anchor_strength: int,
    mechanisms: list,
    source_id: str,
) -> int:
    """
    Determine final anchor_strength per Costa Rica anchor rules.

    CRITICAL: TSE reglamentos implementing statutory mandates keep base_anchor_strength.
    Reglamento Autónomo Servicios TSE (CRC-RATSRE) capped at 1.
    RAL (CRC-RAL) capped at 2.
    Constitutional provisions anchoring mechanisms with statutory development: 5.
    """
    strength = base_anchor_strength

    if source_type == "constitution":
        # Constitution + known statutory development in corpus → 5
        if mechanisms:
            strength = 5
        else:
            # Constitutional provision but no mechanism match → 4
            strength = 4

    elif source_type == "administrative_reglamento":
        # Reglamento Autónomo Servicios TSE — internal HR only; max 1
        strength = min(strength, 1)

    elif source_type == "legislative_reglamento":
        # RAL commented compilation — max 2
        strength = min(strength, 2)

    elif source_type in ("organic_law", "codigo_ley", "statutory_law"):
        # If mechanism found → keep base (4); else reduce by 1
        if not mechanisms:
            strength = max(strength - 1, 0)

    elif source_type == "tse_reglamento":
        # TSE normative reglamento implementing statute → keep base (3)
        # If no mechanism match → reduce
        if not mechanisms:
            strength = max(strength - 1, 0)

    return strength


def determine_operational_dependence(source_type: str, mechanisms: list) -> str:
    """
    Determine operational_dependence per Costa Rica rules.
    """
    if source_type == "constitution":
        # Self-executing constitutional rights: low
        if any(m in mechanisms for m in [
            "vote", "electoral_remedies", "electoral_authority_internal_governance",
            "constitutional_remedies"
        ]):
            return "low"
        return "low"
    elif source_type in ("organic_law", "codigo_ley", "statutory_law"):
        if any(m in mechanisms for m in ["citizen_initiative", "referendum",
                                          "consultative_referendum_or_preliminary_consultation",
                                          "legislative_petition_or_participation",
                                          "transparency_and_accountability",
                                          "political_parties"]):
            return "medium"
        return "low"
    elif source_type == "tse_reglamento":
        return "high"
    elif source_type == "legislative_reglamento":
        return "medium"
    elif source_type == "administrative_reglamento":
        return "high"
    return "unknown"


def determine_gap_types(
    mechanisms: list,
    source_type: str,
    anchor_strength: int,
    source_id: str,
    manual_review_default: bool,
) -> str:
    gaps = []

    if anchor_strength == 0:
        gaps.append("legal_silence")
    elif anchor_strength == 1 and source_type == "administrative_reglamento":
        gaps.append("administrative_overdependence")

    if source_id == "CRC-RATSRE":
        gaps.append("administrative_overdependence")

    if source_type == "legislative_reglamento":
        gaps.append("update_review_needed")

    if "consultative_referendum_or_preliminary_consultation" in mechanisms:
        gaps.append("thin_statutory_anchoring")

    if source_id == "CRC-LCPREF":
        gaps.append("thin_statutory_anchoring")

    # Known corpus gap: LGAP missing
    if any(m in mechanisms for m in ["transparency_and_accountability",
                                      "legislative_petition_or_participation"]):
        if source_type != "constitution":
            gaps.append("corpus_incomplete")

    if not gaps:
        gaps.append("none_detected")

    return "|".join(dict.fromkeys(gaps))  # deduplicate while preserving order


def determine_manual_review(
    anchor_strength: int,
    source_type: str,
    source_id: str,
    mechanisms: list,
    metadata_missing: bool,
    manual_review_default: bool,
) -> bool:
    if manual_review_default:
        return True
    if metadata_missing:
        return True
    if anchor_strength <= 2:
        return True
    if "consultative_referendum_or_preliminary_consultation" in mechanisms:
        return True
    if source_id in ("CRC-RAL", "CRC-RATSRE"):
        return True
    return False


# ---------------------------------------------------------------------------
# MARKDOWN PARSER — Costa Rica
# ---------------------------------------------------------------------------

# Article detection patterns (5 patterns per costa_rica_extraction_rules.yml)
# NOTE: In raw strings, use r'\.' for optional literal dot (not r'\\.')
#   Pattern A: ### Artículo N.- OR ##### ARTÍCULO N.- (Markdown heading, any case, dash optional)
_ART_A = re.compile(
    r'^#{1,6}\s+ART[IÍ]CULO\s+(\d+[°o]?\.?(?:\s+bis)?)\s*[-–]?\s*(.*)',
    re.IGNORECASE
)
#   Pattern B: ### Artículo N. Title (Markdown heading, no dash, title follows)
_ART_B = re.compile(
    r'^#{1,6}\s+Art[ií]culo\s+(\d+[°o]?\.?(?:\s*bis)?)\s+(.*)',
    re.IGNORECASE
)
#   Pattern C: ## ARTÍCULO N.- (two-hash uppercase — catches sources that don't match A)
_ART_C = re.compile(
    r'^#{1,3}\s+ARTÍCULO\s+(\d+[°o]?)\.?\s*[-–]?\s*(.*)',
    re.IGNORECASE
)
#   Pattern D: **ARTICULO N.- Title** (bold, no heading marker — CE/LJC style)
#   Handles: **ARTÍCULO 31.- Title text**  and **ARTICULO 1.-**
#   Trailing ** stripped from inline text in match_article()
_ART_D = re.compile(
    r'^\*\*ART[IÍ]CULO\s+(\d+[°o]?\.?)\s*[-–]?\s*(.*)',
    re.IGNORECASE
)
#   Pattern E: Bare Artículo N. (no heading marker — fallback)
_ART_E = re.compile(
    r'^Art[ií]culo\s+(\d+[°o]?\.?(?:\s*bis)?)\s*[-–]?\s*(.*)',
    re.IGNORECASE
)

# Transitory pattern
_TRANSITORY = re.compile(
    r'ART[IÍ]CULO\s+(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO)|Transitorio|TRANSITORIO|Disposici[oó]n\s+transitoria',
    re.IGNORECASE
)

# Subdivision patterns — inciso / numeral (CR uses letters and numbers)
_INCISO = re.compile(r'^([a-záéíóúñA-Z])\)\s+\S')
_NUMERAL = re.compile(r'^(\d+)\)\s+\S')
_FRACCION = re.compile(r'^([IVX]+\.?)\s+\S', re.IGNORECASE)


def match_article(line: str):
    """
    Try all 5 article detection patterns. Returns (match, pattern_name) or (None, None).
    Pattern priority: A → B → C → D → E.
    Returns (article_number, inline_text) or None.
    """
    for pat in [_ART_A, _ART_B, _ART_C]:
        m = pat.match(line)
        if m:
            art_num = m.group(1).strip().rstrip(".").strip()
            inline = m.group(2).strip().rstrip("*").strip() if len(m.groups()) >= 2 else ""
            return art_num, inline
    for pat in [_ART_D, _ART_E]:
        m = pat.match(line)
        if m:
            art_num = m.group(1).strip().rstrip(".").strip()
            # Strip trailing bold markers that may appear in bold-format articles
            inline = m.group(2).strip().rstrip("*").strip() if len(m.groups()) >= 2 else ""
            return art_num, inline
    return None


def parse_provisions_from_markdown(
    md_path: Path,
    source_meta: dict,
    file_metadata: dict,
    is_ral: bool = False,
) -> list:
    """
    Parse a Markdown legal file into a list of provision dicts.
    For RAL sources (is_ral=True), applies commentary filtering.
    """
    source_id             = source_meta.get("source_id", "UNKNOWN")
    source_type           = source_meta.get("source_type", "unknown")
    normative_rank        = source_meta.get("normative_rank", 9)
    legal_anchor_type_src = source_meta.get("legal_anchor_type", "no_identifiable_anchor")
    base_anchor_strength  = source_meta.get("base_anchor_strength", 0)
    manual_review_default = source_meta.get("manual_review_required_default", False)

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

    lines = content.split("\n")

    # State
    current_article = ""
    current_subdivision = ""
    is_transitory_section = False
    text_buffer = []

    def flush_buffer(article, subdivision, buffer_lines):
        nonlocal prov_counter

        # For RAL, filter commentary lines from buffer
        if is_ral:
            buffer_lines = [l for l in buffer_lines if not is_ral_commentary_line(l)]

        raw_text = " ".join(line.strip() for line in buffer_lines if line.strip())
        if not raw_text or len(raw_text) < 10:
            return None

        cleaned_text = strip_editorial_annotations(raw_text)
        if not cleaned_text or len(cleaned_text) < 10:
            return None

        prov_counter += 1
        prov_id = f"{source_id}-{prov_counter:04d}"

        mechs   = detect_mechanisms(cleaned_text)
        actors  = detect_actors(cleaned_text)
        right_dim = detect_right_dimension(cleaned_text)
        oblig_fac = detect_obligation_or_faculty(cleaned_text)

        has_restriction = detect_flag(cleaned_text, RESTRICTION_RE)
        has_remedy      = detect_flag(cleaned_text, REMEDY_RE)
        has_sanction    = detect_flag(cleaned_text, SANCTION_RE)
        has_procedure   = detect_flag(cleaned_text, PROCEDURE_RE)
        has_requirement = detect_flag(cleaned_text, REQUIREMENT_RE)

        anchor_strength = determine_anchor_strength(
            source_type, base_anchor_strength, mechs, source_id
        )
        op_dep = determine_operational_dependence(source_type, mechs)
        gap_types = determine_gap_types(
            mechs, source_type, anchor_strength, source_id, manual_review_default
        )
        metadata_missing = not bool(file_metadata)
        manual_review = determine_manual_review(
            anchor_strength, source_type, source_id, mechs,
            metadata_missing, manual_review_default
        )

        citation = make_citation(source_id, article, subdivision)
        confidence = "high" if (anchor_strength >= 4 and not manual_review) else \
                     "medium" if anchor_strength >= 2 else "low"

        # Legal anchor type: for RAL all provisions → no_identifiable_anchor for commentary
        # but regulatory_or_legislative_procedural for operative text
        legal_anchor_type_final = legal_anchor_type_src
        if is_ral and manual_review:
            legal_anchor_type_final = "regulatory_or_legislative_procedural"

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
            "provision_text": cleaned_text[:2000],
            "mechanism": "|".join(mechs) if mechs else "",
            "right_dimension": right_dim,
            "actor": "|".join(actors) if actors else "",
            "authority": "|".join(
                a for a in actors
                if a in ("TSE", "Registro_Civil", "Sala_Constitucional",
                          "Asamblea_Legislativa", "Corte_Suprema")
            ),
            "obligation_or_faculty": oblig_fac,
            "procedure": "yes" if has_procedure else "",
            "requirement": "yes" if has_requirement else "",
            "restriction": "yes" if has_restriction else "",
            "remedy": "yes" if has_remedy else "",
            "sanction_or_accountability": "yes" if has_sanction else "",
            "legal_anchor_type": legal_anchor_type_final,
            "anchor_strength": anchor_strength,
            "operational_dependence": op_dep,
            "gap_type": gap_types,
            "confidence": confidence,
            "manual_review_required": "true" if manual_review else "false",
            "notes": (
                "ral_manual_review_commentary_risk" if is_ral else ""
            ),
        }

    for line in lines:
        stripped = line.strip()

        # Track transitory section
        if _TRANSITORY.search(stripped):
            is_transitory_section = True

        art_match = match_article(stripped)
        if art_match is not None:
            art_num, inline_text = art_match
            # Flush previous buffer
            if text_buffer and current_article:
                rec = flush_buffer(current_article, current_subdivision, text_buffer)
                if rec:
                    provisions.append(rec)
            current_article = art_num
            current_subdivision = ""
            text_buffer = [inline_text] if inline_text else []
            continue

        # Track subdivisions (incisos / numerals / fracciones)
        if current_article:
            fm = _FRACCION.match(stripped)
            im = _INCISO.match(stripped)
            nm = _NUMERAL.match(stripped)
            if fm:
                if text_buffer:
                    rec = flush_buffer(current_article, current_subdivision, text_buffer)
                    if rec:
                        provisions.append(rec)
                current_subdivision = f"Fr. {fm.group(1)}"
                text_buffer = [stripped]
                continue
            elif im:
                if text_buffer:
                    rec = flush_buffer(current_article, current_subdivision, text_buffer)
                    if rec:
                        provisions.append(rec)
                current_subdivision = f"Inc. {im.group(1)}"
                text_buffer = [stripped]
                continue
            elif nm:
                if text_buffer:
                    rec = flush_buffer(current_article, current_subdivision, text_buffer)
                    if rec:
                        provisions.append(rec)
                current_subdivision = f"Num. {nm.group(1)}"
                text_buffer = [stripped]
                continue
            else:
                text_buffer.append(stripped)

    # Final flush
    if text_buffer and current_article:
        rec = flush_buffer(current_article, current_subdivision, text_buffer)
        if rec:
            provisions.append(rec)

    return provisions


# ---------------------------------------------------------------------------
# CSV / JSON WRITERS
# ---------------------------------------------------------------------------

def write_csv(path: Path, fieldnames: list, rows: list, sep: str = CSV_SEP):
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

def build_country_profile() -> list:
    rows = [
        {"country": COUNTRY, "field": "country_name",      "value": "Costa Rica",   "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "legal_family",      "value": "Civil law (Romano-Germanic)", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "electoral_system",  "value": "Proportional representation; unicameral Asamblea Legislativa", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "state_structure",   "value": "Unitary republic", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "treaty_reception",  "value": "Monist (Art. 7 CPCR: treaties superior to ordinary laws; Sala IV bloque de constitucionalidad)", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "tse_status",        "value": "Constitutional rank equal to Branches of Government (Art. 9 CPCR); exclusive jurisdiction (Art. 103)", "notes": "CRITICAL: TSE ≠ INE. Non-reviewable jurisdiction.", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "constitution_year", "value": "1949 (Constitución Política)", "notes": "", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "corpus_sources_total", "value": "12", "notes": "1 excluded (LGAP image-based)", "manual_review_required": "false"},
        {"country": COUNTRY, "field": "pipeline_generated", "value": "2026-05-18", "notes": "Offline deterministic pipeline; no LLM at runtime", "manual_review_required": "false"},
    ]
    return rows


def build_source_hierarchy(all_sources_used: list) -> list:
    rows = []
    for stem, meta in SOURCE_REGISTRY.items():
        rows.append({
            "country": COUNTRY,
            "source_id": meta["source_id"],
            "filename_stem": stem,
            "source_type": meta["source_type"],
            "normative_rank": meta["normative_rank"],
            "legal_anchor_type": meta["legal_anchor_type"],
            "base_anchor_strength": meta["base_anchor_strength"],
            "manual_review_required_default": "true" if meta["manual_review_required_default"] else "false",
            "notes": _source_notes(meta["source_id"]),
        })
    # Add excluded source
    rows.append({
        "country": COUNTRY,
        "source_id": "CRC-LGAP",
        "filename_stem": "ley_general_administracion_publica",
        "source_type": "excluded_image_based",
        "normative_rank": 99,
        "legal_anchor_type": "no_identifiable_anchor",
        "base_anchor_strength": 0,
        "manual_review_required_default": "true",
        "notes": "EXCLUDED: image-based PDF; no extractable text. Corpus gap for LGAP provisions.",
    })
    return rows


def _source_notes(source_id: str) -> str:
    notes_map = {
        "CRC-CPOL": "Constitución Política 1949 with reforms. Reform annotations stripped. Verify current text against SINALEVI.",
        "CRC-LOTSRC": "Ley Orgánica TSE y Registro Civil 1965 with reforms. Vigency: sujeto a verificación.",
        "CRC-CE": "Código Electoral 2009 (N.° 8765). Contains parity (Art. 2) and party financing rules. Vigency: sujeto a verificación.",
        "CRC-LREF": "Ley de Regulación del Referéndum N.° 8492 (2006). Vigency: sujeto a verificación.",
        "CRC-LIP": "Ley de Iniciativa Popular N.° 8491 (2006). Vigency: sujeto a verificación.",
        "CRC-LJC": "Ley de la Jurisdicción Constitucional N.° 7135 (1989). Vigency: sujeto a verificación.",
        "CRC-LCPREF": "Ley Consulta Previa y Facultativa de Constitucionalidad en Referéndum (2021). Thin coverage — 99 lines. manual_review_required.",
        "CRC-REGREF": "Reglamento para Procesos de Referéndum (TSE). Vigency: verificar antes de uso jurídico fino.",
        "CRC-REGIP": "Reglamento aplicación art. 3 Ley Iniciativa Popular N.° 8491 (TSE Decreto N.° 04-2007). Operative rules for signature collection.",
        "CRC-RATSRE": "Reglamento Autónomo Servicios TSE — internal HR only. Max anchor_strength=1. Minimal political rights relevance.",
        "CRC-RAL": "Reglamento Asamblea Legislativa (commented compilation 2014). Commentary contamination risk. All provisions manual_review_required.",
    }
    return notes_map.get(source_id, "")


def build_mechanism_map() -> list:
    rows = []
    for mech_name, mech in MECHANISMS.items():
        rows.append({
            "country": COUNTRY,
            "mechanism_id": mech["mechanism_id"],
            "mechanism_name": mech_name,
            "legal_preparedness_relevance": mech["legal_preparedness_relevance"],
            "likely_anchor_strength": mech["likely_anchor_strength"],
            "operational_dependence": mech["operational_dependence"],
            "notes": _mechanism_notes(mech_name),
        })
    return rows


def _mechanism_notes(mech_name: str) -> str:
    notes_map = {
        "vote": "Universal, direct, secret, obligatory suffrage (Art. 93 CPCR). Strong constitutional + statutory basis.",
        "right_to_stand_for_election": "Gender parity (Art. 2 Código Electoral). Strong constitutional + statutory.",
        "political_parties": "State financing formula: 0.19% PIB (Art. 96 CPCR). Democratic internal structure required (Art. 98).",
        "citizen_initiative": "5% padrón threshold (LIP Art. 1). Dedicated statute — stronger than Mexico corpus.",
        "referendum": "Constitutional basis Art. 105. Dedicated statute (LIP N.° 8492) + TSE reglamento.",
        "consultative_referendum_or_preliminary_consultation": "Thin corpus — 2021 law only. Sala IV + TSE interaction not fully captured.",
        "electoral_remedies": "TSE finality (Art. 103 CPCR). Non-reviewable except prevaricato. Stronger than most electoral tribunals.",
        "constitutional_remedies": "Sala IV jurisdiction. Interface with TSE on electoral matters. Sala IV jurisprudence not in corpus.",
        "legislative_petition_or_participation": "RAL source = manual_review_required. Right of petition (Art. 27 CPCR) is clear.",
        "transparency_and_accountability": "LGAP not extractable — corpus_incomplete flag. Party financing (Art. 96 CPCR + Código Electoral).",
        "electoral_authority_internal_governance": "TSE constitutional rank (Art. 9 CPCR). Magistrados appointed by Corte Suprema (2/3 vote, Art. 100 CPCR).",
        "civil_registry_electoral_functions": "Registro Civil under exclusive TSE dependence (Art. 104 CPCR). Decisions appealable to TSE.",
    }
    return notes_map.get(mech_name, "")


def build_actor_map() -> list:
    actors_data = [
        {
            "actor_id": "CRC-ACT-001", "actor_name": "Tribunal Supremo de Elecciones (TSE)",
            "actor_type": "constitutional_electoral_authority",
            "legal_preparedness_role": "supreme_and_exclusive_electoral_authority",
            "mechanisms": "vote|right_to_stand_for_election|political_parties|citizen_initiative|referendum|consultative_referendum_or_preliminary_consultation|electoral_remedies|electoral_authority_internal_governance|civil_registry_electoral_functions",
            "notes": "CRITICAL: TSE has constitutional rank = Branches of Government (Art. 9). Exclusive, non-reviewable jurisdiction (Art. 103). NOT an administrative body.",
        },
        {
            "actor_id": "CRC-ACT-002", "actor_name": "Registro Civil",
            "actor_type": "civil_registry_electoral_body",
            "legal_preparedness_role": "civil_registry_and_electoral_rolls",
            "mechanisms": "civil_registry_electoral_functions|vote",
            "notes": "Under exclusive TSE dependence (Art. 104 CPCR). Decisions appealable to TSE.",
        },
        {
            "actor_id": "CRC-ACT-003", "actor_name": "Juntas Electorales",
            "actor_type": "subordinate_electoral_body",
            "legal_preparedness_role": "voting_day_administrator",
            "mechanisms": "vote",
            "notes": "Juntas Receptoras de Votos. Decisions appealable to TSE.",
        },
        {
            "actor_id": "CRC-ACT-004", "actor_name": "Sala Constitucional (Sala IV)",
            "actor_type": "constitutional_court",
            "legal_preparedness_role": "constitutional_court",
            "mechanisms": "constitutional_remedies|consultative_referendum_or_preliminary_consultation",
            "notes": "Amparo, habeas corpus, unconstitutionality. Defers to TSE on strictly electoral matters. Sala IV jurisprudence not in corpus.",
        },
        {
            "actor_id": "CRC-ACT-005", "actor_name": "Asamblea Legislativa",
            "actor_type": "legislative_body",
            "legal_preparedness_role": "legislature",
            "mechanisms": "citizen_initiative|referendum|legislative_petition_or_participation|political_parties",
            "notes": "Must consult TSE on electoral legislation (Art. 97 CPCR). 2/3 majority to override TSE opinion.",
        },
        {
            "actor_id": "CRC-ACT-006", "actor_name": "Partidos Políticos",
            "actor_type": "political_organization",
            "legal_preparedness_role": "political_actor",
            "mechanisms": "political_parties|vote|right_to_stand_for_election",
            "notes": "Constitutional recognition (Art. 98). State financing (Art. 96). Must maintain democratic internal structure.",
        },
        {
            "actor_id": "CRC-ACT-007", "actor_name": "Ciudadanos / Ciudadanas",
            "actor_type": "rights_holder",
            "legal_preparedness_role": "primary_rights_holder",
            "mechanisms": "vote|right_to_stand_for_election|citizen_initiative|referendum|legislative_petition_or_participation",
            "notes": "CR citizens 18+. Naturalized citizens: 12 months before first vote (Art. 94 CPCR). Suffrage is obligatory.",
        },
        {
            "actor_id": "CRC-ACT-008", "actor_name": "Poder Ejecutivo",
            "actor_type": "executive_power",
            "legal_preparedness_role": "secondary_political_actor",
            "mechanisms": "referendum",
            "notes": "Can request referendum (Ley Referéndum). Limited electoral role.",
        },
        {
            "actor_id": "CRC-ACT-009", "actor_name": "Corte Suprema de Justicia",
            "actor_type": "supreme_court",
            "legal_preparedness_role": "appointing_body_for_tse",
            "mechanisms": "electoral_authority_internal_governance",
            "notes": "Appoints TSE Magistrados by 2/3 vote (Art. 100 CPCR). Hosts Sala Constitucional.",
        },
    ]
    rows = []
    for a in actors_data:
        rows.append({
            "country": COUNTRY,
            "actor_id": a["actor_id"],
            "actor_name": a["actor_name"],
            "actor_type": a["actor_type"],
            "legal_preparedness_role": a["legal_preparedness_role"],
            "mechanisms": a["mechanisms"],
            "notes": a["notes"],
            "manual_review_required": "false",
        })
    return rows


def build_validation_notes() -> list:
    note_ids = [
        ("CRC-VN-001", "jurisprudence_gap", "medium", "Sala IV jurisprudence not in corpus", "true"),
        ("CRC-VN-002", "tse_resolution_gap", "medium", "TSE resolutions and instructivos not in corpus", "true"),
        ("CRC-VN-003", "excluded_source", "high", "LGAP excluded — image-based PDF; corpus_incomplete for transparency/petition", "true"),
        ("CRC-VN-004", "commented_source_risk", "high", "RAL is commented compilation — commentary contamination risk", "true"),
        ("CRC-VN-005", "vigency_uncertainty", "medium", "Multiple sources carry vigency uncertainty flags", "false"),
        ("CRC-VN-006", "accessibility_gap", "medium", "No corpus provisions on disability or language accessibility for political rights", "true"),
        ("CRC-VN-007", "international_standards_gap", "low", "Treaty texts not in corpus — ICCPR, ACHR, CRPD, CEDAW", "false"),
        ("CRC-VN-008", "tse_reglamento_vigency", "medium", "TSE reglamentos for referendum and citizen initiative — vigency requires verification", "true"),
        ("CRC-VN-009", "parity_and_equality_coverage", "low", "Parity provisions in Código Electoral — corpus coverage confirmed (no gap)", "false"),
        ("CRC-VN-010", "reglamento_autonomo_scope", "low", "Reglamento Autónomo TSE — minimal political rights relevance; anchor_strength capped at 1", "false"),
        ("CRC-VN-011", "constitutionality_consultation_thin_coverage", "medium", "Consulta Previa Constitucionalidad — thin statutory coverage; manual_review", "true"),
        ("CRC-VN-012", "corpus_scope_note", "informational", "CR corpus scope: 11 sources extracted, 1 excluded (LGAP image-based)", "false"),
    ]
    rows = []
    for note_id, category, severity, title, mr in note_ids:
        rows.append({
            "country": COUNTRY,
            "note_id": note_id,
            "category": category,
            "severity": severity,
            "title": title,
            "manual_review_required": mr,
        })
    return rows


def build_mechanism_sources(provisions: list) -> list:
    """Build mechanism-source cross-reference table."""
    seen = set()
    rows = []
    for p in provisions:
        for mech in p["mechanism"].split("|"):
            mech = mech.strip()
            if not mech:
                continue
            key = (mech, p["source_id"])
            if key not in seen:
                seen.add(key)
                mech_id = MECHANISMS.get(mech, {}).get("mechanism_id", "")
                rows.append({
                    "country": COUNTRY,
                    "mechanism": mech,
                    "mechanism_id": mech_id,
                    "source_id": p["source_id"],
                    "source_type": p["source_type"],
                    "legal_anchor_type": p["legal_anchor_type"],
                    "anchor_strength": p["anchor_strength"],
                    "provision_count": 0,  # filled below
                })
    # Count provisions per (mechanism, source)
    count_map = defaultdict(int)
    for p in provisions:
        for mech in p["mechanism"].split("|"):
            mech = mech.strip()
            if mech:
                count_map[(mech, p["source_id"])] += 1
    for row in rows:
        row["provision_count"] = count_map.get((row["mechanism"], row["source_id"]), 0)
    return rows


def build_actor_mechanism_edges(provisions: list) -> list:
    """Build actor-mechanism relationship table."""
    seen = set()
    rows = []
    for p in provisions:
        mechs = [m.strip() for m in p["mechanism"].split("|") if m.strip()]
        actors = [a.strip() for a in p["actor"].split("|") if a.strip()]
        for mech in mechs:
            for actor in actors:
                key = (actor, mech, p["source_id"])
                if key not in seen:
                    seen.add(key)
                    rows.append({
                        "country": COUNTRY,
                        "actor": actor,
                        "mechanism": mech,
                        "source_id": p["source_id"],
                        "legal_anchor_type": p["legal_anchor_type"],
                        "anchor_strength": p["anchor_strength"],
                    })
    return rows


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def main():
    print(f"\n{'='*70}")
    print(f"NormTrace Political Rights — Costa Rica Legal Brain Pipeline")
    print(f"{'='*70}\n")

    # ----------------------------------------------------------------
    # STEP 1: Discover Markdown files
    # ----------------------------------------------------------------
    print("STEP 1: Discovering Markdown files...")
    if not CORPUS_MD_DIR.exists():
        print(f"  [ERROR] Corpus directory not found: {CORPUS_MD_DIR}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted([
        f for f in CORPUS_MD_DIR.glob("*.md")
        if f.name not in SKIP_FILES
    ])
    print(f"  Found {len(md_files)} MD files (excluded: {len(SKIP_FILES)} skip-listed)")

    # ----------------------------------------------------------------
    # STEP 2: Parse provisions from all files
    # ----------------------------------------------------------------
    print("\nSTEP 2: Parsing provisions...")
    all_provisions = []
    sources_used = []
    warn_count = 0

    for md_path in md_files:
        stem = md_path.stem
        source_meta = SOURCE_REGISTRY.get(stem)

        if source_meta is None:
            print(f"  [WARN] {md_path.name} — not in SOURCE_REGISTRY; skipping", file=sys.stderr)
            warn_count += 1
            continue

        file_metadata = read_metadata(stem)
        if not file_metadata:
            print(f"  [WARN] {md_path.name} — no metadata file found", file=sys.stderr)
            warn_count += 1

        is_ral = (source_meta["source_id"] == "CRC-RAL")
        provisions = parse_provisions_from_markdown(md_path, source_meta, file_metadata, is_ral=is_ral)
        source_count = len(provisions)
        print(f"  {md_path.name:60s} → {source_count:4d} provisions  [{source_meta['source_id']}]")

        all_provisions.extend(provisions)
        sources_used.append(source_meta["source_id"])

    print(f"\n  Total provisions extracted: {len(all_provisions)}")
    print(f"  Sources processed:          {len(sources_used)}")
    print(f"  Warnings:                   {warn_count}")

    # ----------------------------------------------------------------
    # STEP 3: Build all tables
    # ----------------------------------------------------------------
    print("\nSTEP 3: Building output tables...")

    country_profile_rows = build_country_profile()
    source_hierarchy_rows = build_source_hierarchy(sources_used)
    mechanism_map_rows = build_mechanism_map()
    actor_map_rows = build_actor_map()
    validation_notes_rows = build_validation_notes()
    mechanism_sources_rows = build_mechanism_sources(all_provisions)
    actor_mechanism_rows = build_actor_mechanism_edges(all_provisions)

    # Mechanism provision count summary
    mech_counts = defaultdict(int)
    for p in all_provisions:
        for m in p["mechanism"].split("|"):
            m = m.strip()
            if m:
                mech_counts[m] += 1

    print("\n  Mechanism provision counts:")
    for mech_name, mech in MECHANISMS.items():
        count = mech_counts.get(mech_name, 0)
        print(f"    {mech_name:55s} {count:5d}")
    unmatched = sum(1 for p in all_provisions if not p["mechanism"])
    print(f"    {'(no mechanism match)':55s} {unmatched:5d}")

    # ----------------------------------------------------------------
    # STEP 4: Write CSV outputs
    # ----------------------------------------------------------------
    print("\nSTEP 4: Writing CSV files...")

    PROVISION_FIELDS = [
        "provision_id", "country", "source_id", "source_title", "source_file",
        "source_type", "normative_rank", "article", "subdivision", "citation",
        "provision_text", "mechanism", "right_dimension", "actor", "authority",
        "obligation_or_faculty", "procedure", "requirement", "restriction",
        "remedy", "sanction_or_accountability", "legal_anchor_type",
        "anchor_strength", "operational_dependence", "gap_type", "confidence",
        "manual_review_required", "notes",
    ]

    outputs = [
        ("costa_rica_country_profile.csv",        ["country","field","value","notes","manual_review_required"],                country_profile_rows),
        ("costa_rica_source_hierarchy.csv",        ["country","source_id","filename_stem","source_type","normative_rank","legal_anchor_type","base_anchor_strength","manual_review_required_default","notes"], source_hierarchy_rows),
        ("costa_rica_mechanism_map.csv",           ["country","mechanism_id","mechanism_name","legal_preparedness_relevance","likely_anchor_strength","operational_dependence","notes"], mechanism_map_rows),
        ("costa_rica_actor_map.csv",               ["country","actor_id","actor_name","actor_type","legal_preparedness_role","mechanisms","notes","manual_review_required"], actor_map_rows),
        ("costa_rica_legal_provisions.csv",        PROVISION_FIELDS, all_provisions),
        ("costa_rica_mechanism_sources.csv",       ["country","mechanism","mechanism_id","source_id","source_type","legal_anchor_type","anchor_strength","provision_count"], mechanism_sources_rows),
        ("costa_rica_actor_mechanism_edges.csv",   ["country","actor","mechanism","source_id","legal_anchor_type","anchor_strength"], actor_mechanism_rows),
        ("costa_rica_validation_notes.csv",        ["country","note_id","category","severity","title","manual_review_required"], validation_notes_rows),
    ]

    for filename, fields, rows in outputs:
        path = OUT_CSV_DIR / filename
        write_csv(path, fields, rows)
        print(f"  Wrote {len(rows):5d} rows → {path}")

    # ----------------------------------------------------------------
    # STEP 5: Write JSON outputs
    # ----------------------------------------------------------------
    print("\nSTEP 5: Writing JSON files...")

    json_outputs = [
        ("costa_rica_country_profile.json",        country_profile_rows),
        ("costa_rica_source_hierarchy.json",        source_hierarchy_rows),
        ("costa_rica_mechanism_map.json",           mechanism_map_rows),
        ("costa_rica_actor_map.json",               actor_map_rows),
        ("costa_rica_legal_provisions.json",        all_provisions),
        ("costa_rica_mechanism_sources.json",       mechanism_sources_rows),
        ("costa_rica_actor_mechanism_edges.json",   actor_mechanism_rows),
        ("costa_rica_validation_notes.json",        validation_notes_rows),
    ]

    for filename, data in json_outputs:
        path = OUT_JSON_DIR / filename
        write_json(path, data)
        print(f"  Wrote → {path}")

    # ----------------------------------------------------------------
    # STEP 6: Summary
    # ----------------------------------------------------------------
    print(f"\n{'='*70}")
    print("PIPELINE COMPLETE — SUMMARY")
    print(f"{'='*70}")
    print(f"  Country:              {COUNTRY}")
    print(f"  MD files processed:   {len(sources_used)}")
    print(f"  Provisions extracted: {len(all_provisions)}")
    print(f"  Manual review flags:  {sum(1 for p in all_provisions if p['manual_review_required'] == 'true')}")
    print(f"  Mechanism-source rows:{len(mechanism_sources_rows)}")
    print(f"  Actor-mechanism edges:{len(actor_mechanism_rows)}")
    print(f"  CSV output dir:       {OUT_CSV_DIR}")
    print(f"  JSON output dir:      {OUT_JSON_DIR}")
    if warn_count:
        print(f"  [WARN] {warn_count} warnings — check stderr")
    print()


if __name__ == "__main__":
    main()
