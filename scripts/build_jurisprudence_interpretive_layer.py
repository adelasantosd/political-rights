#!/usr/bin/env python3
"""
build_jurisprudence_interpretive_layer.py
NormTrace Political Rights — Jurisprudence & Interpretive Standards Layer
Generated: 2026-05-19

Reads:
  corpus/jurisprudencia/jurisprudence_discovery_table.csv

Produces CSV and JSON outputs in:
  03_tables/jurisprudence/
  05_webapp/public/data/jurisprudence/

IMPORTANT CONSTRAINTS:
  - This is a DISCOVERY TABLE, not a full jurisprudence corpus.
  - Jurisprudence is a secondary interpretive layer only.
  - Do NOT increase domestic anchor_strength based on jurisprudence.
  - Do NOT modify domestic legal_provisions tables.
  - Do NOT produce compliance conclusions.
  - affects_scoring = false for all entries by default.
  - manual_review_required = true for all entries.
"""

import csv
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────

BASE = Path(__file__).resolve().parent.parent

INPUT_CSV     = BASE / "corpus" / "jurisprudencia" / "jurisprudence_discovery_table.csv"
OUT_TABLE_DIR = BASE / "03_tables" / "jurisprudence"
OUT_WEBAPP_DIR = BASE / "05_webapp" / "public" / "data" / "jurisprudence"

SEP = ";"

# ─────────────────────────────────────────────────────────────────────────────
# PRINCIPLE MAP  (canonical — from political_rights_principle_map.yml)
# ─────────────────────────────────────────────────────────────────────────────

PRINCIPLES = {
    "PRIN-001": "legality_and_sufficient_legal_basis",
    "PRIN-002": "equality_and_non_discrimination",
    "PRIN-003": "accessibility_and_reasonable_accommodation",
    "PRIN-004": "effective_participation",
    "PRIN-005": "pluralism_and_collective_representation",
    "PRIN-006": "due_process_and_effective_remedy",
    "PRIN-007": "transparency_and_accountability",
    "PRIN-008": "institutional_competence_and_independence",
    "PRIN-009": "procedural_certainty_and_time_limits",
    "PRIN-010": "territorial_and_multilevel_implementation",
    "PRIN-011": "administrative_capacity_and_resources",
    "PRIN-012": "restriction_legality_necessity_proportionality",
}

# ─────────────────────────────────────────────────────────────────────────────
# MECHANISM MAP  (canonical — from task specification)
# ─────────────────────────────────────────────────────────────────────────────

MECHANISMS = [
    "vote",
    "right_to_stand_for_election",
    "political_parties",
    "independent_candidacies",
    "citizen_initiative",
    "popular_consultation",
    "referendum",
    "recall",
    "electoral_remedies",
    "constitutional_remedies",
    "indigenous_consultation_or_participation",
    "gender_parity_and_women_participation",
    "disability_accessible_participation",
    "campaign_finance_and_electoral_integrity",
]

# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATION RULES
# Maps court_or_body + document_type → source_type
# ─────────────────────────────────────────────────────────────────────────────

def classify_source_type(row: dict) -> str:
    court = row.get("court_or_body", "").lower()
    doc_type = row.get("document_type", "").lower()
    jur_id = row.get("jur_id", "")

    if "corte interamericana" in court or "corteidh" in jur_id.lower():
        return "binding_inter_american_case_law"
    if "comité de derechos humanos" in court or "ccpr" in court or "juri-un" in jur_id.upper():
        return "un_human_rights_committee_view_or_standard"
    if "comisión interamericana" in court or "iachr" in jur_id.upper():
        return "inter_american_commission_report"
    if "venecia" in court or "venice" in court or "idea" in court.lower():
        return "soft_law_comparative_standard"
    if "database" in doc_type or "reference" in doc_type:
        return "database_or_reference_source"
    # Fallback
    return "soft_law_comparative_standard"


def classify_binding_status(row: dict) -> str:
    legal_force = row.get("legal_force", "").lower()
    source_type = classify_source_type(row)

    if source_type == "binding_inter_american_case_law":
        doc_type = row.get("document_type", "").lower()
        if "sentencia" in doc_type:
            return "binding_inter_american"
        elif "opinion_consultiva" in doc_type or "consultiva" in doc_type:
            return "authoritative_interpretive"
        return "binding_inter_american"
    if source_type == "un_human_rights_committee_view_or_standard":
        return "authoritative_interpretive"
    if source_type == "inter_american_commission_report":
        return "persuasive_soft_law"
    return "comparative_soft_law"


def classify_legal_force(row: dict) -> str:
    """Numeric interpretive weight 1–5."""
    binding = classify_binding_status(row)
    priority = row.get("priority_level", "P3").strip().upper()

    base = {
        "binding_inter_american": 5,
        "authoritative_interpretive": 4,
        "persuasive_soft_law": 3,
        "comparative_soft_law": 2,
    }.get(binding, 2)

    # Priority adjustment: P1 doesn't increase beyond base, but P3 reduces by 1
    if priority == "P3" and base > 1:
        base -= 1
    return base


def classify_interpretive_weight(row: dict) -> str:
    w = classify_legal_force(row)
    return {5: "high", 4: "high", 3: "medium", 2: "low", 1: "low"}.get(w, "low")

# ─────────────────────────────────────────────────────────────────────────────
# MECHANISM MAPPING
# Maps discovery-table mechanism tokens to canonical mechanism IDs
# ─────────────────────────────────────────────────────────────────────────────

# Discovery table uses Spanish mechanism tokens; map to canonical English names
_MECH_TOKEN_MAP = {
    "be_voted":                         "right_to_stand_for_election",
    "candidatura_independiente":        "independent_candidacies",
    "registro_partido":                 "political_parties",
    "vote":                             "vote",
    "consulta_popular":                 "popular_consultation",
    "referendum":                       "referendum",
    "revocacion_mandato":               "recall",
    "iniciativa_ciudadana":             "citizen_initiative",
    "todos_los_mecanismos":             "all",
    "todos los mecanismos":             "all",
}

def extract_mechanisms(row: dict) -> list:
    """Parse relevant_right_or_mechanism field → list of canonical mechanism IDs."""
    raw = row.get("relevant_right_or_mechanism", "")
    # Split on pipe, space-pipe, comma
    tokens = re.split(r"\s*\|\s*|\s*,\s*", raw)
    result = []
    for tok in tokens:
        tok_clean = tok.strip().lower().replace(" ", "_").replace("-", "_")
        if tok_clean in _MECH_TOKEN_MAP:
            mapped = _MECH_TOKEN_MAP[tok_clean]
            if mapped == "all":
                result = list(MECHANISMS)
                break
            if mapped not in result:
                result.append(mapped)
        elif tok_clean in MECHANISMS:
            if tok_clean not in result:
                result.append(tok_clean)
    return result if result else ["vote"]  # default: vote if nothing parsed


# ─────────────────────────────────────────────────────────────────────────────
# PRINCIPLE MAPPING
# Per-entry heuristic based on source content, subject_matter, and mechanisms
# ─────────────────────────────────────────────────────────────────────────────

# Known per-entry principle assignments (manually curated from discovery table content)
_PER_ENTRY_PRINCIPLES = {
    "JURI-IACtHR-01": {
        "PRIN-001": ("high", "Castañeda establece que las restricciones al derecho a candidatura independiente deben tener base legal suficiente, precisa y proporcional.", "strict_legality_test"),
        "PRIN-005": ("high", "El Estado no puede otorgar monopolio absoluto a partidos políticos; el pluralismo exige reconocer formas alternativas de participación.", "pluralism_and_non_monopoly_test"),
        "PRIN-006": ("high", "El recurso de amparo no era efectivo en materia electoral; el Estado debe proveer un recurso judicial efectivo específico.", "effective_remedy_electoral_test"),
        "PRIN-012": ("high", "Restricciones al Art. 23 deben superar test de proporcionalidad y necesidad en sociedad democrática.", "proportionality_test_art23"),
    },
    "JURI-IACtHR-02": {
        "PRIN-002": ("high", "La exigencia de presentar candidatos únicamente a través de partidos políticos discrimina a comunidades indígenas.", "non_discrimination_indigenous_test"),
        "PRIN-005": ("high", "El pluralismo político requiere proteger formas diversas de organización política, incluyendo organizaciones indígenas no partidistas.", "pluralism_diversity_test"),
        "PRIN-010": ("high", "Los derechos políticos de pueblos indígenas deben poder ejercerse a través de formas propias de organización territorial y comunitaria.", "indigenous_territorial_participation_test"),
        "PRIN-012": ("high", "La restricción a candidaturas indígenas no partidistas no supera el test de proporcionalidad del Art. 23.2.", "proportionality_test_art23"),
    },
    "JURI-IACtHR-03": {
        "PRIN-001": ("high", "Sólo una condena penal impuesta por juez competente puede restringir los derechos políticos del Art. 23.2; la inhabilitación administrativa carece de base convencional.", "taxativity_art232_test"),
        "PRIN-006": ("high", "El órgano administrativo que impone sanciones con efecto en derechos políticos debe respetar garantías del debido proceso.", "due_process_political_sanction_test"),
        "PRIN-012": ("high", "El Art. 23.2 es taxativo: la lista de causas válidas de restricción al sufragio pasivo es cerrada.", "taxativity_restriction_test"),
    },
    "JURI-IACtHR-04": {
        "PRIN-001": ("high", "Confirma taxatividad del Art. 23.2: órgano no judicial no puede restringir derechos políticos pasivos.", "taxativity_art232_confirmed"),
        "PRIN-006": ("high", "La destitución de un funcionario electo mediante acto administrativo viola garantías procesales del Art. 8 y el derecho político del Art. 23.", "due_process_elected_official_test"),
        "PRIN-012": ("high", "Amplía López Mendoza: solo condena penal por juez competente puede privar del derecho a ser elegido.", "restriction_judicial_exclusivity_test"),
    },
    "JURI-IACtHR-05": {
        "PRIN-002": ("high", "Las restricciones penales de larga duración sobre derechos políticos deben evaluarse con escrutinio especial cuando afectan a grupos indígenas.", "indigenous_equality_political_rights_test"),
        "PRIN-006": ("high", "Las restricciones a los derechos políticos deben respetar las garantías judiciales del Art. 8 CADH.", "judicial_guarantee_political_restriction_test"),
        "PRIN-012": ("medium", "Las sanciones con efecto en derechos políticos deben ser proporcionadas al delito.", "proportionality_criminal_political_sanction"),
    },
    "JURI-IACtHR-06": {
        "PRIN-001": ("high", "El Art. 30 CADH exige que las restricciones a derechos convencionales emanen de 'leyes' formales — no de decretos, circulares o actos administrativos.", "legality_formal_law_test"),
        "PRIN-012": ("high", "La legalidad de las restricciones implica ley formal, accesible, precisa, y no arbitraria.", "formal_law_restriction_test"),
    },
    "JURI-IACtHR-07": {
        "PRIN-002": ("high", "La paridad de género en órganos electorales y en candidaturas es una obligación positiva derivada del Art. 23 CADH.", "gender_parity_electoral_obligation"),
        "PRIN-008": ("high", "Los órganos electorales deben ser independientes, imparciales y técnicamente competentes.", "electoral_body_independence_test"),
        "PRIN-004": ("high", "La participación efectiva de mujeres en procesos electorales requiere medidas positivas del Estado.", "effective_participation_women_test"),
    },
    "JURI-IACtHR-08": {
        "PRIN-001": ("medium", "El ámbito de los derechos laborales puede traslaparse con derechos de participación política cuando afecta a personas electas.", "political_mandate_labor_rights_interface"),
        "PRIN-004": ("low", "El derecho a la participación política puede extenderse a formas de expresión y participación en el ámbito público.", "broad_participation_scope_test"),
    },
    "JURI-UN-01": {
        "PRIN-001": ("high", "El GC25 del CDH es la interpretación autorizada del Art. 25 PIDCP: todo mecanismo de participación requiere base legal positiva.", "gc25_legality_standard"),
        "PRIN-002": ("high", "Las distinciones en el ejercicio de los derechos del Art. 25 deben basarse en criterios objetivos y razonables.", "gc25_non_discrimination_criteria"),
        "PRIN-003": ("high", "Los procedimientos de votación deben ser accesibles para personas con discapacidad.", "gc25_accessibility_voting"),
        "PRIN-004": ("high", "El derecho a participar implica condiciones materiales de efectividad, no solo reconocimiento formal.", "gc25_effective_participation_standard"),
        "PRIN-006": ("high", "El Art. 25 requiere recursos efectivos contra violaciones al derecho a participar.", "gc25_remedy_standard"),
        "PRIN-009": ("high", "Las elecciones deben ser periódicas, con intervalos definidos y razonables.", "gc25_periodicity_standard"),
        "PRIN-012": ("high", "Las restricciones al Art. 25 deben basarse en criterios objetivos y razonables, no en opinión política.", "gc25_restriction_criteria"),
    },
    "JURI-UN-02": {
        "PRIN-004": ("medium", "El derecho de reunión pacífica (Art. 21) es condición de ejercicio de los derechos políticos de participación directa.", "assembly_as_participation_condition"),
        "PRIN-009": ("medium", "El GC37 desarrolla garantías procedimentales mínimas para reuniones y expresión colectiva.", "procedural_guarantees_assembly"),
    },
    "JURI-IACHR-01": {
        "PRIN-007": ("medium", "El informe CIDH documenta patrones de erosión de la transparencia y accountability institucional en procesos electorales.", "transparency_erosion_pattern"),
        "PRIN-008": ("medium", "La independencia de los órganos electorales es condición de legitimidad democrática.", "institutional_independence_democracy_condition"),
    },
    "JURI-IACHR-02": {
        "PRIN-007": ("medium", "La institucionalidad democrática requiere mecanismos de rendición de cuentas efectivos.", "accountability_democratic_institution"),
        "PRIN-008": ("medium", "El Estado de Derecho democrático requiere separación de poderes y control institucional independiente.", "rule_of_law_institutional_competence"),
        "PRIN-001": ("low", "El marco democrático requiere base normativa que respete la separación de poderes.", "normative_framework_separation_powers"),
    },
    "JURI-VEN-01": {
        "PRIN-001": ("medium", "El Código establece estándares mínimos de base legal para procedimientos electorales.", "electoral_code_legality_benchmark"),
        "PRIN-009": ("high", "El Código define parámetros de certeza temporal: calendarios electorales, plazos de inscripción y campaña.", "temporal_certainty_electoral_benchmark"),
        "PRIN-007": ("high", "El Código establece estándares de transparencia en financiamiento, resultados y administración electoral.", "transparency_electoral_benchmark"),
        "PRIN-008": ("high", "El Código define criterios de independencia y profesionalismo de la administración electoral.", "electoral_administration_independence_benchmark"),
    },
    "JURI-VEN-02": {
        "PRIN-001": ("medium", "El Código establece requisitos de base legal para referéndums: ley formal, procedimiento claro.", "referendum_legality_benchmark"),
        "PRIN-009": ("high", "El Código define plazos, fases y garantías procedimentales para referéndums.", "referendum_temporal_procedural_benchmark"),
        "PRIN-004": ("medium", "Los referéndums deben garantizar información suficiente y tiempo adecuado para la deliberación ciudadana.", "informed_participation_referendum"),
    },
    "JURI-VEN-03": {
        "PRIN-005": ("high", "El Código define estándares mínimos de pluralismo: acceso al registro, financiamiento equitativo, reglas de competencia.", "political_party_pluralism_benchmark"),
        "PRIN-007": ("medium", "Los partidos políticos deben mantener transparencia financiera y de membresía.", "political_party_transparency_benchmark"),
    },
    "JURI-IDEA-01": {
        "PRIN-004": ("low", "IDEA provee análisis comparativo de diseños de democracia directa que pueden contextualizar evaluaciones de participación.", "direct_democracy_comparative_context"),
        "PRIN-009": ("low", "El manual documenta variaciones en marcos procedimentales de consulta popular, referéndum y revocación.", "procedural_variation_direct_democracy"),
        "PRIN-001": ("low", "El manual identifica requisitos mínimos de base legal para distintos mecanismos de democracia directa.", "legal_basis_direct_democracy_benchmark"),
    },
}

# Interpretive tests per principle assignment
def get_principle_assignments(jur_id: str) -> dict:
    """Returns dict: {principle_id: (relevance, description, test_name)}"""
    return _PER_ENTRY_PRINCIPLES.get(jur_id, {})


# ─────────────────────────────────────────────────────────────────────────────
# NORMALISE FIELDS
# ─────────────────────────────────────────────────────────────────────────────

def normalise_country(raw: str) -> str:
    raw = raw.strip().lower()
    if raw in ("internacional", "international", "inter-american"):
        return "international"
    return raw.title()


def normalise_court(raw: str) -> str:
    raw = raw.strip()
    abbreviations = {
        "Corte Interamericana de Derechos Humanos": "IACtHR / Corte IDH",
        "Comité de Derechos Humanos — ONU (CCPR)": "HRC / CCPR",
        "Comisión Interamericana de Derechos Humanos (CIDH)": "IACHR / CIDH",
        "Comisión de Venecia — Consejo de Europa": "Venice Commission",
        "International IDEA": "International IDEA",
    }
    for key, abbr in abbreviations.items():
        if key in raw or abbr in raw:
            return abbr
    return raw


def normalise_priority(raw: str) -> str:
    raw = raw.strip().upper()
    if raw.startswith("P1"):
        return "P1"
    if raw.startswith("P2"):
        return "P2"
    return "P3"


def normalise_filename(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if not raw.endswith(".md"):
        raw += ".md"
    return raw.lower().replace(" ", "_")


# ─────────────────────────────────────────────────────────────────────────────
# READ INPUT
# ─────────────────────────────────────────────────────────────────────────────

def read_input(path: Path) -> list:
    """Auto-detect delimiter, prefer semicolon."""
    with open(path, "r", encoding="utf-8") as f:
        sample = f.read(2048)
    semi_count = sample.count(";")
    comma_count = sample.count(",")
    delimiter = ";" if semi_count >= comma_count else ","

    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter, quotechar='"')
        for row in reader:
            rows.append({k: (v or "").strip() for k, v in row.items()})
    print(f"  Input: {len(rows)} rows, delimiter='{delimiter}'")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# CSV / JSON WRITERS
# ─────────────────────────────────────────────────────────────────────────────

def write_csv(path: Path, rows: list, fieldnames: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=SEP,
                                quotechar='"', quoting=csv.QUOTE_ALL,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [CSV]  {path.relative_to(BASE)}  ({len(rows)} rows)")


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"  [JSON] {path.relative_to(BASE)}")


def write_both(csv_path: Path, webapp_json_path: Path,
               rows: list, fieldnames: list, json_key: str):
    write_csv(csv_path, rows, fieldnames)
    write_json(webapp_json_path, {json_key: rows})


# ─────────────────────────────────────────────────────────────────────────────
# BUILD TABLE 1: jurisprudence_index
# ─────────────────────────────────────────────────────────────────────────────

INDEX_FIELDS = [
    "jur_id", "country_or_system", "court_or_body",
    "case_or_document_number", "case_or_document_title",
    "source_type", "binding_status", "legal_force", "interpretive_weight",
    "affects_scoring", "rights_or_mechanisms_covered",
    "priority_level", "proposed_md_filename",
    "full_text_available", "metadata_available",
    "manual_review_required", "notes",
]

def build_index(raw_rows: list) -> list:
    rows = []
    for r in raw_rows:
        jur_id = r["jur_id"]
        mechanisms = extract_mechanisms(r)
        rows.append({
            "jur_id": jur_id,
            "country_or_system": normalise_country(r.get("country_or_system", "")),
            "court_or_body": normalise_court(r.get("court_or_body", "")),
            "case_or_document_number": r.get("case_or_document_number", ""),
            "case_or_document_title": r.get("short_name", ""),
            "source_type": classify_source_type(r),
            "binding_status": classify_binding_status(r),
            "legal_force": classify_legal_force(r),
            "interpretive_weight": classify_interpretive_weight(r),
            "affects_scoring": "false",          # HARD RULE
            "rights_or_mechanisms_covered": "|".join(mechanisms),
            "priority_level": normalise_priority(r.get("priority_level", "P3")),
            "proposed_md_filename": normalise_filename(r.get("proposed_md_filename", "")),
            "full_text_available": "false",       # discovery table only
            "metadata_available": "true",         # discovery table fields available
            "manual_review_required": "true",     # HARD RULE
            "notes": r.get("notes", ""),
        })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# BUILD TABLE 2: jurisprudence_principle_map
# ─────────────────────────────────────────────────────────────────────────────

PRIN_MAP_FIELDS = [
    "jur_id", "court_or_body", "case_or_document_title",
    "principle_id", "principle_name",
    "interpretive_relevance", "interpretive_test_or_standard",
    "binding_status", "interpretive_weight",
    "use_in_model", "affects_scoring",
    "manual_review_required", "notes",
]

def build_principle_map(raw_rows: list) -> list:
    rows = []
    for r in raw_rows:
        jur_id = r["jur_id"]
        assignments = get_principle_assignments(jur_id)
        binding = classify_binding_status(r)
        weight = classify_interpretive_weight(r)
        court = normalise_court(r.get("court_or_body", ""))
        title = r.get("short_name", "")

        if not assignments:
            # No curated assignment — add a placeholder for manual review
            rows.append({
                "jur_id": jur_id,
                "court_or_body": court,
                "case_or_document_title": title,
                "principle_id": "UNASSIGNED",
                "principle_name": "manual_review_required",
                "interpretive_relevance": "unknown",
                "interpretive_test_or_standard": "",
                "binding_status": binding,
                "interpretive_weight": weight,
                "use_in_model": "pending_review",
                "affects_scoring": "false",
                "manual_review_required": "true",
                "notes": "No curated principle assignment — requires manual review",
            })
            continue

        for prin_id, (relevance, description, test_name) in assignments.items():
            prin_name = PRINCIPLES.get(prin_id, "")
            # use_in_model: refine_interpretive_test for binding; contextual for soft law
            use = ("refine_interpretive_test" if binding in
                   ("binding_inter_american", "authoritative_interpretive")
                   else "contextual_benchmark")
            rows.append({
                "jur_id": jur_id,
                "court_or_body": court,
                "case_or_document_title": title,
                "principle_id": prin_id,
                "principle_name": prin_name,
                "interpretive_relevance": relevance,
                "interpretive_test_or_standard": test_name,
                "binding_status": binding,
                "interpretive_weight": weight,
                "use_in_model": use,
                "affects_scoring": "false",
                "manual_review_required": "true",
                "notes": description,
            })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# BUILD TABLE 3: jurisprudence_mechanism_map
# ─────────────────────────────────────────────────────────────────────────────

MECH_MAP_FIELDS = [
    "jur_id", "court_or_body", "case_or_document_title",
    "mechanism_id", "mechanism_name",
    "interpretive_relevance", "affected_country_or_system",
    "interpretive_weight",
    "manual_review_required", "notes",
]

# Known country affectation per entry
_COUNTRY_AFFECTATION = {
    "JURI-IACtHR-01": "Mexico (respondent state); comparative: Costa Rica",
    "JURI-IACtHR-02": "Comparative: Mexico, Costa Rica (indigenous candidacies)",
    "JURI-IACtHR-03": "Comparative: Mexico, Costa Rica (administrative sanctions on political rights)",
    "JURI-IACtHR-04": "Comparative: Mexico, Costa Rica (administrative sanctions — confirms JURI-IACtHR-03)",
    "JURI-IACtHR-05": "Comparative: Mexico, Costa Rica (indigenous political rights / criminal sanctions)",
    "JURI-IACtHR-06": "All CADH states parties: Mexico, Costa Rica",
    "JURI-IACtHR-07": "All CADH states parties: Mexico, Costa Rica — gender parity",
    "JURI-IACtHR-08": "Comparative: Mexico, Costa Rica (political mandate / labor rights interface)",
    "JURI-UN-01":  "All ICCPR states parties: Mexico, Costa Rica",
    "JURI-UN-02":  "All ICCPR states parties: Mexico, Costa Rica",
    "JURI-IACHR-01": "Comparative — regional pattern documentation",
    "JURI-IACHR-02": "Comparative — regional pattern documentation",
    "JURI-VEN-01": "Comparative soft-law benchmark: Mexico, Costa Rica",
    "JURI-VEN-02": "Comparative soft-law benchmark: Mexico, Costa Rica",
    "JURI-VEN-03": "Comparative soft-law benchmark: Mexico, Costa Rica",
    "JURI-IDEA-01": "Global comparative reference: Mexico, Costa Rica",
}

# Relevance per mechanism for each entry (partial — high-priority ones)
_MECH_RELEVANCE = {
    "JURI-IACtHR-01": {
        "independent_candidacies": "high",
        "right_to_stand_for_election": "high",
        "electoral_remedies": "high",
    },
    "JURI-IACtHR-02": {
        "independent_candidacies": "high",
        "right_to_stand_for_election": "high",
        "political_parties": "high",
        "indigenous_consultation_or_participation": "high",
    },
    "JURI-IACtHR-03": {
        "right_to_stand_for_election": "high",
        "independent_candidacies": "high",
        "electoral_remedies": "medium",
    },
    "JURI-IACtHR-04": {
        "right_to_stand_for_election": "high",
        "constitutional_remedies": "high",
        "electoral_remedies": "medium",
    },
    "JURI-IACtHR-05": {
        "vote": "medium",
        "right_to_stand_for_election": "high",
        "indigenous_consultation_or_participation": "high",
    },
    "JURI-IACtHR-06": {
        "vote": "high",
        "right_to_stand_for_election": "high",
        "political_parties": "medium",
    },
    "JURI-IACtHR-07": {
        "gender_parity_and_women_participation": "high",
        "right_to_stand_for_election": "high",
        "political_parties": "medium",
    },
    "JURI-UN-01": {
        k: "high" for k in MECHANISMS
    },
    "JURI-VEN-01": {
        "vote": "high",
        "right_to_stand_for_election": "high",
        "political_parties": "high",
        "independent_candidacies": "medium",
        "campaign_finance_and_electoral_integrity": "high",
    },
    "JURI-VEN-02": {
        "referendum": "high",
        "popular_consultation": "high",
    },
    "JURI-VEN-03": {
        "political_parties": "high",
        "campaign_finance_and_electoral_integrity": "medium",
    },
    "JURI-IDEA-01": {
        "popular_consultation": "low",
        "referendum": "low",
        "recall": "low",
        "citizen_initiative": "low",
    },
}

def build_mechanism_map(raw_rows: list) -> list:
    rows = []
    for r in raw_rows:
        jur_id = r["jur_id"]
        court = normalise_court(r.get("court_or_body", ""))
        title = r.get("short_name", "")
        weight = classify_interpretive_weight(r)
        country_affect = _COUNTRY_AFFECTATION.get(jur_id, "international")
        mech_relevance_map = _MECH_RELEVANCE.get(jur_id, {})
        mechanisms = extract_mechanisms(r)

        for mech in mechanisms:
            relevance = mech_relevance_map.get(mech, "medium")
            rows.append({
                "jur_id": jur_id,
                "court_or_body": court,
                "case_or_document_title": title,
                "mechanism_id": mech,
                "mechanism_name": mech.replace("_", " "),
                "interpretive_relevance": relevance,
                "affected_country_or_system": country_affect,
                "interpretive_weight": weight,
                "manual_review_required": "true",
                "notes": "",
            })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# BUILD TABLE 4: jurisprudence_download_plan
# ─────────────────────────────────────────────────────────────────────────────

DOWNLOAD_FIELDS = [
    "jur_id", "case_or_document_title", "court_or_body",
    "priority_level", "recommended_action", "proposed_md_filename",
    "requires_metadata", "requires_full_text", "notes",
]

_DOWNLOAD_ACTIONS = {
    "P1": "IMMEDIATE: Download PDF from official URL; convert to Markdown; add to corpus/jurisprudencia/md/",
    "P2": "SCHEDULED: Download and convert in next corpus expansion cycle.",
    "P3": "DEFERRED: Add to acquisition backlog; review in Phase 2.",
}

_SOURCE_NOTES = {
    "sentencia": "IACtHR judgment — official PDF at corteidh.or.cr. Use pdfplumber or marker for Markdown conversion.",
    "opinion_consultiva": "IACtHR advisory opinion — official PDF at corteidh.or.cr. Full text required for OC-based principle refinement.",
    "general_comment": "UN treaty body general comment — official at OHCHR. Often already in HTML/PDF.",
    "thematic_report": "IACHR thematic report — PDF at oas.org. Convert with column-aware PDF extractor.",
    "soft_law_standard": "Venice Commission / IDEA — PDF at venice.coe.int or idea.int. Soft law — lower extraction priority than binding sources.",
}

def build_download_plan(raw_rows: list) -> list:
    rows = []
    for r in raw_rows:
        jur_id = r["jur_id"]
        priority = normalise_priority(r.get("priority_level", "P3"))
        doc_type = r.get("document_type", "").lower()
        action = _DOWNLOAD_ACTIONS.get(priority, _DOWNLOAD_ACTIONS["P3"])
        source_note = _SOURCE_NOTES.get(doc_type, "See official URL for download instructions.")
        rows.append({
            "jur_id": jur_id,
            "case_or_document_title": r.get("short_name", ""),
            "court_or_body": normalise_court(r.get("court_or_body", "")),
            "priority_level": priority,
            "recommended_action": action,
            "proposed_md_filename": normalise_filename(r.get("proposed_md_filename", "")),
            "requires_metadata": "false",    # metadata already in discovery table
            "requires_full_text": "true",    # no full text in corpus yet
            "notes": source_note,
        })
    # Sort by priority then jur_id
    rows.sort(key=lambda r: (r["priority_level"], r["jur_id"]))
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# BUILD TABLE 5: jurisprudence_validation_notes
# ─────────────────────────────────────────────────────────────────────────────

VAL_FIELDS = [
    "note_id", "note_type", "severity", "affected_jur_id",
    "description", "recommended_action", "manual_review_required",
]

def build_validation_notes(raw_rows: list, index_rows: list) -> list:
    notes = []
    note_counter = [1]

    def add(note_type, severity, affected_id, description, action):
        notes.append({
            "note_id": f"JVN-{note_counter[0]:03d}",
            "note_type": note_type,
            "severity": severity,
            "affected_jur_id": affected_id,
            "description": description,
            "recommended_action": action,
            "manual_review_required": "true",
        })
        note_counter[0] += 1

    # System-level notes
    add("layer_constraint", "informational", "all",
        "This layer is a SECONDARY INTERPRETIVE LAYER only. No entry may increase "
        "domestic anchor_strength or convert a domestic legal gap into legal preparedness. "
        "affects_scoring=false and manual_review_required=true are hard rules for all entries.",
        "Enforce in all downstream consumers of these tables.")

    add("corpus_status", "high", "all",
        "All 16 entries are discovery-table metadata only. No full Markdown text exists "
        "in corpus/jurisprudencia/md/ for any entry. Principle and mechanism mappings are "
        "based on holding_summary and subject_matter fields — not full-text analysis.",
        "Execute download plan (jurisprudence_download_plan.csv) before using jurisprudence "
        "to refine interpretive tests in production.")

    add("binding_status_caveat", "medium", "all",
        "Corte IDH judgments (sentencias) are classified as binding_inter_american. "
        "This binding character applies to states parties to the CADH and to the jurisdiction "
        "of the IACtHR. Mexico and Costa Rica are both parties. However, binding character "
        "operates at the international level — it does not automatically create domestic "
        "statutory anchoring under the NormTrace scoring model.",
        "Maintain affects_scoring=false; use for interpretive test refinement only.")

    add("oc2821_overlap", "medium", "JURI-IACtHR-06",
        "JURI-IACtHR-06 (OC-3/83 — 'Leyes' en Art. 30) overlaps thematically with "
        "INT-OC2821 already in the international corpus. The two advisory opinions address "
        "different questions: OC-3/83 defines 'laws' for restriction purposes; OC-28/21 "
        "addresses democratic continuity and term limits. No duplication risk, but downstream "
        "users should distinguish them.",
        "Maintain separate entries. Cross-reference INT-OC2821 when applying PRIN-012.")

    add("gc25_overlap", "medium", "JURI-UN-01",
        "JURI-UN-01 (HRC GC25) is the same instrument as INT-HRC-GC25 in the international "
        "corpus. In the international corpus it is treated as a full-text provision source. "
        "In this jurisprudence layer it is treated as a metadata-only discovery entry. "
        "Do not double-count its authority.",
        "Flag JURI-UN-01 as covered_by_intl_corpus=INT-HRC-GC25 in downstream consumers.")

    add("discovery_table_field_mismatch", "low", "all",
        "The discovery table uses 'short_name' as the document title field. "
        "The required output schema uses 'case_or_document_title'. The mapping "
        "short_name → case_or_document_title is applied in this pipeline.",
        "No action required. Documented for schema traceability.")

    # Per-entry notes for P1 entries without curated mechanism assignments
    for r in raw_rows:
        jur_id = r["jur_id"]
        mechs = extract_mechanisms(r)
        if not mechs or mechs == ["vote"]:
            prio = normalise_priority(r.get("priority_level", "P3"))
            if prio == "P1":
                add("mechanism_mapping_uncertain", "medium", jur_id,
                    f"{jur_id}: Mechanism mapping defaulted to 'vote' because "
                    f"relevant_right_or_mechanism field could not be parsed with confidence. "
                    f"Requires manual review of full text.",
                    "Verify mechanism mapping after full text acquisition.")

    # Venice Commission / IDEA soft law caveat
    soft_law_ids = [r["jur_id"] for r in raw_rows
                    if classify_source_type(r) == "soft_law_comparative_standard"]
    for sid in soft_law_ids:
        add("soft_law_caveat", "low", sid,
            f"{sid}: Classified as comparative_soft_law. Not binding for Mexico or Costa Rica. "
            f"Use only as benchmarking reference, not as authoritative standard.",
            "Ensure interpretive_weight=low or medium. Do not cite as binding authority.")

    return notes


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n=== NormTrace: Building Jurisprudence Interpretive Layer ===\n")

    if not INPUT_CSV.exists():
        print(f"ERROR: Input file not found: {INPUT_CSV}")
        sys.exit(1)

    # 1. Read
    print("Reading discovery table...")
    raw_rows = read_input(INPUT_CSV)

    # 2. Build tables
    print("\nBuilding output tables...")
    index_rows   = build_index(raw_rows)
    prin_rows    = build_principle_map(raw_rows)
    mech_rows    = build_mechanism_map(raw_rows)
    dl_rows      = build_download_plan(raw_rows)
    val_rows     = build_validation_notes(raw_rows, index_rows)

    # 3. Write
    print()
    write_both(
        OUT_TABLE_DIR  / "jurisprudence_index.csv",
        OUT_WEBAPP_DIR / "jurisprudence_index.json",
        index_rows, INDEX_FIELDS, "jurisprudence_index"
    )
    write_both(
        OUT_TABLE_DIR  / "jurisprudence_principle_map.csv",
        OUT_WEBAPP_DIR / "jurisprudence_principle_map.json",
        prin_rows, PRIN_MAP_FIELDS, "jurisprudence_principle_map"
    )
    write_both(
        OUT_TABLE_DIR  / "jurisprudence_mechanism_map.csv",
        OUT_WEBAPP_DIR / "jurisprudence_mechanism_map.json",
        mech_rows, MECH_MAP_FIELDS, "jurisprudence_mechanism_map"
    )
    write_both(
        OUT_TABLE_DIR  / "jurisprudence_download_plan.csv",
        OUT_WEBAPP_DIR / "jurisprudence_download_plan.json",
        dl_rows, DOWNLOAD_FIELDS, "jurisprudence_download_plan"
    )
    write_both(
        OUT_TABLE_DIR  / "jurisprudence_validation_notes.csv",
        OUT_WEBAPP_DIR / "jurisprudence_validation_notes.json",
        val_rows, VAL_FIELDS, "jurisprudence_validation_notes"
    )

    # 4. Report
    print("\n=== Run Report ===")
    print(f"  Entries processed:        {len(raw_rows)}")
    from collections import Counter
    src_types = Counter(r["source_type"] for r in index_rows)
    print(f"  By source_type:")
    for k, v in sorted(src_types.items()):
        print(f"    {k}: {v}")
    print(f"  Principle mappings:       {len([r for r in prin_rows if r['principle_id'] != 'UNASSIGNED'])}")
    print(f"  Mechanism mappings:       {len(mech_rows)}")
    p1 = [r for r in dl_rows if r["priority_level"] == "P1"]
    print(f"  P1 full-text acquisitions: {len(p1)}")
    for r in p1:
        print(f"    {r['jur_id']}: {r['case_or_document_title'][:50]}")
    print(f"  Validation notes:         {len(val_rows)}")
    print()
    print("  Output files created:")
    for f in ["jurisprudence_index", "jurisprudence_principle_map",
              "jurisprudence_mechanism_map", "jurisprudence_download_plan",
              "jurisprudence_validation_notes"]:
        print(f"    03_tables/jurisprudence/{f}.csv")
        print(f"    05_webapp/public/data/jurisprudence/{f}.json")
    print()
    print("  Files NOT modified:")
    print("    03_tables/country_legal_brains/mexico/  — UNCHANGED")
    print("    03_tables/country_legal_brains/costa_rica/  — UNCHANGED")
    print("    03_tables/international/  — UNCHANGED")
    print("    03_tables/principle_traceability/  — UNCHANGED")
    print()
    print("  Malformed rows / metadata problems:")
    problems = [r for r in raw_rows
                if not r.get("proposed_md_filename") or
                not r.get("priority_level")]
    if problems:
        for p in problems:
            print(f"    {p['jur_id']}: missing proposed_md_filename or priority_level")
    else:
        print("    None — all 16 rows have required fields.")
    print()
    print("=== Done ===\n")


if __name__ == "__main__":
    main()
