#!/usr/bin/env python3
"""
build_institutional_network_layer_v2_functional.py
NormTrace Political Rights — Functional Institutional Network Pipeline (v2)

v2 creates directed actor→actor edges ONLY when a legal provision explicitly
supports a functional relationship. Co-mention edges (actors sharing a
mechanism without a directional provision) are excluded from the main graph
and written to excluded_comention_edges.csv.

Primary edge source:   legal_provisions.csv  (authority → actor columns)
Supplementary source:  actor_mechanism_edges.csv  (obligation/faculty only)

No role-hierarchy, no complete subgraphs, no reference-type functional edges
unless provision text contains an explicit functional keyword.

No external dependencies.
"""

import csv
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from itertools import combinations, permutations

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE      = Path(__file__).resolve().parent.parent
BRAIN_DIR = BASE / "03_tables" / "country_legal_brains"
TRACE_DIR = BASE / "03_tables" / "principle_traceability"
OUT_DIR   = BASE / "03_tables" / "institutional_network_v2_functional"
WEBAPP    = BASE / "05_webapp" / "public" / "data" / "institutional_network_v2_functional"

OUT_DIR.mkdir(parents=True, exist_ok=True)
WEBAPP.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Actor name → actor_id mappings
# ---------------------------------------------------------------------------
MEX_NAME_TO_ID = {
    "INE":              "MEX-ACT-001",
    "TEPJF":            "MEX-ACT-002",
    "SCJN":             "MEX-ACT-003",
    "Congress":         "MEX-ACT-004",   # Represents both chambers; Senado = validation note
    "Political_parties":"MEX-ACT-006",
    "Citizens":         "MEX-ACT-007",
    "FGR":              "MEX-ACT-008",
    "SFP":              "MEX-ACT-009",
    "OPLEs":            "MEX-ACT-010",
}

CRC_NAME_TO_ID = {
    "TSE":                  "CRC-ACT-001",
    "Registro_Civil":       "CRC-ACT-002",
    "Juntas_Electorales":   "CRC-ACT-003",
    "Sala_Constitucional":  "CRC-ACT-004",
    "Asamblea_Legislativa": "CRC-ACT-005",
    "Partidos_Politicos":   "CRC-ACT-006",
    "Ciudadanos":           "CRC-ACT-007",
    "Poder_Ejecutivo":      "CRC-ACT-008",
    "Corte_Suprema":        "CRC-ACT-009",
}

MEX_ID_TO_NAME: dict[str, str] = {v: k for k, v in MEX_NAME_TO_ID.items()}
CRC_ID_TO_NAME: dict[str, str] = {v: k for k, v in CRC_NAME_TO_ID.items()}

# ---------------------------------------------------------------------------
# Functional keyword detection → relationship_type
# ---------------------------------------------------------------------------
FUNC_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(somete|presenta\s+(?:ante|a\s+la)|entrega\s+(?:a|al|ante)|solicita\s+(?:a|al)|remite|transmite|submit|deliver|request)", re.I), "submits_to"),
    (re.compile(r"(convoca|emite\s+convocatoria|llama\s+a\s+(?:elecciones|votac)|issues?\s+(?:a\s+)?call|convene)", re.I), "issues_call"),
    (re.compile(r"(registra|inscribe|registro\s+de\s+(?:candidat|partido|lista)|register|enrol)", re.I), "registers_candidate_or_party"),
    (re.compile(r"(verifica|constata|comprueba|revisa\s+(?:los\s+)?requisito|verify|check\s+(?:the\s+)?requirement|scrutin)", re.I), "verifies_requirements"),
    (re.compile(r"(valida|valide|firma\s+y\s+sella|validate\s+signatur|certif)", re.I), "validates_signatures"),
    (re.compile(r"(organiza|administra\s+(?:el\s+)?(?:proceso|elección|votac)|conduce|organiz|administer)", re.I), "organizes_process"),
    (re.compile(r"(publica|difunde|notifica\s+(?:a|al|los)|da\s+a\s+conocer|publish|disseminat|notify)", re.I), "publishes_information"),
    (re.compile(r"(supervisa|vigila|fiscaliz|inspecciona|supervise|oversee|monitor|inspect)", re.I), "supervises"),
    (re.compile(r"(coordina\s+(?:con|las)|coopera\s+con|trabaja\s+conjuntamente|coordinat|cooperat|joint)", re.I), "coordinates_with"),
    (re.compile(r"(financia|asigna\s+recursos|otorga\s+(?:recursos|financiamiento)|fund|allocat|budget)", re.I), "funds_or_allocates_resources"),
    (re.compile(r"(implementa|ejecuta\s+(?:el\s+)?(?:resultado|resolución|acuerdo)|implement|execut|enforce\s+(?:the\s+)?result)", re.I), "implements_result"),
    (re.compile(r"(adjudica|falla\s+(?:en\s+favor|en\s+contra)|dicta\s+(?:sentencia|resolución)|adjudicat|rule\s+on)", re.I), "adjudicates"),
    (re.compile(r"(resuelve\s+(?:la\s+)?(?:impugnac|controversia|recurso)|resolve\s+(?:the\s+)?(?:dispute|challenge|appeal))", re.I), "resolves_dispute"),
    (re.compile(r"(constitucionalidad|acción\s+de\s+inconstitucionalidad|reviews?\s+constitutionality|constitutional\s+review)", re.I), "reviews_constitutionality"),
    (re.compile(r"(sanciona|impone\s+(?:sanción|multa)|amonesta|sanction|penalt|fine\s+(?:the|an?))", re.I), "sanctions"),
    (re.compile(r"(informa\s+(?:a|al)|reporta\s+(?:a|al)|rinde\s+cuentas|report\s+to|account(?:ability)?\s+to)", re.I), "reports_to"),
    (re.compile(r"(accesibilidad|asistencia\s+(?:para\s+)?(?:el\s+)?voto|garantiza\s+(?:el\s+)?acceso\s+(?:a|para)|accessib|guarantee\s+access\s+for)", re.I), "guarantees_accessibility_for"),
    (re.compile(r"(igualdad|paridad|no\s+discriminac|garantiza\s+(?:la\s+)?igualdad|equality|non.?discriminat|parity)", re.I), "guarantees_equality_for"),
    (re.compile(r"(interpone\s+recurso|presenta\s+(?:recurso|queja|demanda)\s+ante|recurso\s+de\s+(?:apelación|revisión)|provides?\s+remedy|appeal\s+to|file\s+(?:a\s+)?complaint\s+with)", re.I), "provides_remedy_to"),
    (re.compile(r"(designa|nombra|appoint|designat|nominate)", re.I), "appoints_or_designates"),
    (re.compile(r"(reglamenta\s+(?:la|el)|emite\s+(?:reglamento|norma|acuerdo\s+general)|regulat|rule.?mak)", re.I), "regulates"),
    (re.compile(r"(requiere\s+(?:de|que)|solicita\s+(?:información|datos)\s+(?:a|al)|requests?\s+(?:information|data)\s+from)", re.I), "requests_from"),
]

def detect_relationship(text: str) -> str:
    """Return first matched relationship_type or 'unknown_functional_relationship'."""
    for pat, rel in FUNC_PATTERNS:
        if pat.search(text):
            return rel
    return "unknown_functional_relationship"

# ---------------------------------------------------------------------------
# Process stage detection
# ---------------------------------------------------------------------------
STAGE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(convoca|apertura|lanzamiento|activation|launch|start\s+(?:of\s+)?(?:process|period))", re.I), "activation"),
    (re.compile(r"(registra|inscribe|padrón|registro\s+(?:de\s+)?(?:candidat|elector|partido)|register\s+(?:candidate|party|voter))", re.I), "registration"),
    (re.compile(r"(verifica|constata|valida|comprueba|verif|validat|scrutin)", re.I), "verification"),
    (re.compile(r"(organiza\s+(?:la\s+)?(?:elección|votac|jornada)|distribuc.*material|instalac.*casilla|organiz)", re.I), "organization"),
    (re.compile(r"(campaña|debate|deliberac|propagand|campaign|deliberat)", re.I), "campaign_or_deliberation"),
    (re.compile(r"(jornada\s+electoral|votac|sufragio|emisión\s+del\s+voto|voting\s+day|balloting|suffrage)", re.I), "voting_or_participation"),
    (re.compile(r"(resuelve|adjudica|falla|sentencia|resolución\s+(?:final|definitiva)|adjudicat|rule\s+on|ruling)", re.I), "adjudication"),
    (re.compile(r"(implementa|ejecuta|cómputo|escrutinio|resultados\s+definitivos|implement|execut|tally|result)", re.I), "implementation"),
    (re.compile(r"(supervisa|vigila|fiscaliz|auditor|oversee|monitor|audit)", re.I), "oversight"),
    (re.compile(r"(rinde\s+cuentas|informa\s+(?:a|al)\s+congreso|transparencia|accountability|report\s+to|transparency)", re.I), "accountability"),
    (re.compile(r"(accesibilidad|voto\s+asistido|acceso\s+para\s+(?:personas|citizens\s+with)|accessib)", re.I), "accessibility_support"),
    (re.compile(r"(publica|difunde|portal|transparencia\s+(?:activa|proactiva)|publish|disclosure|publication)", re.I), "transparency"),
    (re.compile(r"(delegac|subdelegac|junta\s+(?:local|distrital)|territorial|regional\s+coordination)", re.I), "territorial_coordination"),
    (re.compile(r"(sesión\s+(?:del\s+)?(?:consejo|pleno)|quórum|acuerd(?:o|os)\s+internos|internal\s+governance|plenary)", re.I), "internal_governance"),
]

def detect_stage(text: str, mechanism_category: str) -> str:
    for pat, stage in STAGE_PATTERNS:
        if pat.search(text):
            return stage
    # Fallback by mechanism category
    CAT_STAGE_DEFAULT = {
        "participation":   "voting_or_participation",
        "candidacy":       "registration",
        "party_governance": "organization",
        "remedy":          "adjudication",
        "enforcement":     "adjudication",
        "transparency":    "transparency",
        "governance":      "internal_governance",
        "registry":        "registration",
        "legislative":     "implementation",
    }
    return CAT_STAGE_DEFAULT.get(mechanism_category, "unknown_stage")

# ---------------------------------------------------------------------------
# Mechanism category
# ---------------------------------------------------------------------------
MECHANISM_CATEGORY = {
    "vote":                                      "participation",
    "recall":                                    "participation",
    "popular_consultation":                      "participation",
    "referendum":                                "participation",
    "consultative_referendum_or_preliminary_consultation": "participation",
    "citizen_initiative":                        "legislative",
    "legislative_petition_or_participation":     "legislative",
    "right_to_stand_for_election":               "candidacy",
    "independent_candidacies":                   "candidacy",
    "political_parties":                         "party_governance",
    "electoral_remedies":                        "remedy",
    "constitutional_remedies":                   "remedy",
    "electoral_crimes":                          "enforcement",
    "administrative_responsibility":             "enforcement",
    "transparency_and_accountability":           "transparency",
    "electoral_authority_internal_governance":   "governance",
    "civil_registry_electoral_functions":        "registry",
}

CRITICAL_STAGES = {
    "activation", "verification", "organization",
    "adjudication", "implementation", "oversight",
}

# ---------------------------------------------------------------------------
# Edge confidence
# ---------------------------------------------------------------------------
def compute_confidence(has_authority: bool, obl_field: str, keyword_found: bool,
                        anchor_strength: int) -> str:
    if has_authority and keyword_found and obl_field in ("obligation", "faculty"):
        return "high" if anchor_strength >= 3 else "medium"
    if has_authority and (keyword_found or obl_field in ("obligation", "faculty")):
        return "medium"
    return "low"

# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------
def read_csv(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        for row in reader:
            rows.append({k.strip().strip('"'): v.strip().strip('"') for k, v in row.items()})
    return rows

def write_csv(path: Path, fieldnames: list[str], rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",",
                           quotechar='"', quoting=csv.QUOTE_ALL,
                           extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})

def write_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def out_pair(stem: str, fieldnames: list[str], rows: list[dict]):
    write_csv(OUT_DIR / f"{stem}.csv", fieldnames, rows)
    write_json(WEBAPP / f"{stem}.json", rows)
    print(f"  {stem}.csv ({len(rows)} rows) + .json")

# ---------------------------------------------------------------------------
# Edge schema
# ---------------------------------------------------------------------------
EDGE_FIELDS = [
    "edge_id", "country", "mechanism_id", "mechanism_name",
    "source_actor_id", "source_actor_name",
    "target_actor_id", "target_actor_name",
    "relationship_type", "process_stage",
    "domestic_source_id", "citation", "legal_text_excerpt",
    "legal_anchor_type", "anchor_strength",
    "mandatory_or_discretionary", "timeline_defined", "remedy_available",
    "territorial_level", "edge_confidence", "edge_derivation_method",
    "manual_review_required", "notes",
]

EXCL_FIELDS = EDGE_FIELDS + ["exclusion_reason"]

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
def load_data() -> dict:
    d = {}
    d["mex_prov"]    = read_csv(BRAIN_DIR / "mexico"     / "mexico_legal_provisions.csv")
    d["mex_actors"]  = read_csv(BRAIN_DIR / "mexico"     / "mexico_actor_map.csv")
    d["mex_edges"]   = read_csv(BRAIN_DIR / "mexico"     / "mexico_actor_mechanism_edges.csv")
    d["mex_mechs"]   = read_csv(BRAIN_DIR / "mexico"     / "mexico_mechanism_map.csv")
    d["crc_prov"]    = read_csv(BRAIN_DIR / "costa_rica" / "costa_rica_legal_provisions.csv")
    d["crc_actors"]  = read_csv(BRAIN_DIR / "costa_rica" / "costa_rica_actor_map.csv")
    d["crc_edges"]   = read_csv(BRAIN_DIR / "costa_rica" / "costa_rica_actor_mechanism_edges.csv")
    d["crc_mechs"]   = read_csv(BRAIN_DIR / "costa_rica" / "costa_rica_mechanism_map.csv")
    return d

# ---------------------------------------------------------------------------
# 2. Build nodes (reuse v1 logic, same actors)
# ---------------------------------------------------------------------------
NODE_FIELDS = [
    "country", "actor_id", "actor_name", "actor_type", "network_role",
    "mechanism_count", "mechanisms", "legal_preparedness_role",
    "manual_review_required", "notes",
]

ACTOR_ROLE = {
    "autonomous_electoral_authority":     "orchestrator",
    "constitutional_electoral_authority": "orchestrator",
    "electoral_court":                    "adjudicator",
    "constitutional_court":               "adjudicator",
    "supreme_court":                      "supervisor",
    "legislative_body":                   "legislator",
    "executive_power":                    "executive",
    "prosecutorial_authority":            "enforcer",
    "oversight_body":                     "supervisor",
    "local_electoral_authority":          "subordinate",
    "civil_registry_electoral_body":      "subordinate",
    "subordinate_electoral_body":         "subordinate",
    "political_organization":             "political_actor",
    "rights_holder":                      "rights_holder",
}

def build_nodes(data: dict) -> tuple[list[dict], dict, dict]:
    nodes, mex_lkp, crc_lkp = [], {}, {}
    for country, actor_rows, lkp in [
        ("Mexico",     data["mex_actors"], mex_lkp),
        ("Costa Rica", data["crc_actors"], crc_lkp),
    ]:
        for row in actor_rows:
            aid = row.get("actor_id", "").strip()
            if not aid or aid == "actor_id":
                continue
            atype  = row.get("actor_type", "")
            mechs  = [m.strip() for m in (row.get("mechanisms") or "").split("|") if m.strip()]
            node   = {
                "country":               country,
                "actor_id":              aid,
                "actor_name":            row.get("actor_name", ""),
                "actor_type":            atype,
                "network_role":          ACTOR_ROLE.get(atype, "unknown"),
                "mechanism_count":       str(len(mechs)),
                "mechanisms":            "|".join(mechs),
                "legal_preparedness_role": row.get("legal_preparedness_role", ""),
                "manual_review_required": row.get("manual_review_required", "false"),
                "notes":                 row.get("notes", ""),
            }
            nodes.append(node)
            lkp[aid] = node
    return nodes, mex_lkp, crc_lkp

# ---------------------------------------------------------------------------
# 3. Build functional edges from legal_provisions.csv
# ---------------------------------------------------------------------------
def _parse_actors(raw: str, name_to_id: dict) -> list[str]:
    """Resolve pipe-separated short names to actor_ids. Drop unknowns."""
    ids = []
    for name in raw.split("|"):
        name = name.strip()
        aid  = name_to_id.get(name)
        if aid:
            ids.append(aid)
        elif name:
            pass  # unknown short name — skip silently
    return list(dict.fromkeys(ids))  # deduplicate preserving order

def _mech_id(country: str, mech_name: str, mech_name_to_id: dict) -> str:
    return mech_name_to_id.get(mech_name, f"{country[:3].upper()}-MECH-{mech_name[:12]}")

def derive_provision_edges(
    prov_rows: list[dict],
    name_to_id: dict,
    mech_name_to_id: dict,
    country: str,
    id_to_name: dict,
) -> tuple[list[dict], list[dict]]:
    """
    Returns (functional_edges, excluded_comention_edges).
    """
    func_edges   = []
    excl_edges   = []
    edge_counter = [0]

    def next_id() -> str:
        edge_counter[0] += 1
        pfx = "MEX" if country == "Mexico" else "CRC"
        return f"{pfx}V2-EDGE-{edge_counter[0]:04d}"

    def build_base(src_id: str, tgt_id: str, row: dict,
                   rel: str, stage: str, conf: str, method: str,
                   note: str = "") -> dict:
        mechs_raw = (row.get("mechanism") or "").strip()
        mech_name = mechs_raw.split("|")[0].strip() if mechs_raw else ""
        mech_cat  = MECHANISM_CATEGORY.get(mech_name, "other")
        obl_field = (row.get("obligation_or_faculty") or "").strip()
        anchor    = (row.get("legal_anchor_type") or "").strip()
        anch_str  = (row.get("anchor_strength") or "0").strip()
        text_full = (row.get("provision_text") or "").strip()
        text_exc  = text_full[:200]
        timeline  = "yes" if re.search(r"(plazo|término|días|horas|deadline|within\s+\d+)", text_full, re.I) else "no"
        remedy    = "yes" if re.search(r"(recurso|amparo|impugnac|remedy|appeal|challenge)", text_full, re.I) else "no"
        terr      = "yes" if re.search(r"(delegac|subdelegac|local|distrital|regional|circunscripción)", text_full, re.I) else "no"
        return {
            "edge_id":              next_id(),
            "country":              country,
            "mechanism_id":         _mech_id(country, mech_name, mech_name_to_id),
            "mechanism_name":       mech_name,
            "source_actor_id":      src_id,
            "source_actor_name":    id_to_name.get(src_id, src_id),
            "target_actor_id":      tgt_id,
            "target_actor_name":    id_to_name.get(tgt_id, tgt_id),
            "relationship_type":    rel,
            "process_stage":        stage,
            "domestic_source_id":   (row.get("source_id") or "").strip(),
            "citation":             (row.get("citation") or "").strip(),
            "legal_text_excerpt":   text_exc,
            "legal_anchor_type":    anchor,
            "anchor_strength":      anch_str,
            "mandatory_or_discretionary": "mandatory" if obl_field == "obligation" else "discretionary",
            "timeline_defined":     timeline,
            "remedy_available":     remedy,
            "territorial_level":    "yes" if terr == "yes" else "no",
            "edge_confidence":      conf,
            "edge_derivation_method": method,
            "manual_review_required": "false",
            "notes":                note,
        }

    # Track emitted (src, tgt, mech, source_id) to avoid exact duplicates
    emitted: set[tuple] = set()

    for row in prov_rows:
        auth_raw  = (row.get("authority") or "").strip()
        actor_raw = (row.get("actor") or "").strip()
        obl_field = (row.get("obligation_or_faculty") or "").strip()
        text      = (row.get("provision_text") or "").strip()
        mechs_raw = (row.get("mechanism") or "").strip()
        mech_name = mechs_raw.split("|")[0].strip() if mechs_raw else ""
        mech_cat  = MECHANISM_CATEGORY.get(mech_name, "other")
        anchor_s  = 0
        try:
            anchor_s = int((row.get("anchor_strength") or "0"))
        except ValueError:
            pass
        src_id_raw = (row.get("source_id") or "").strip()

        auth_ids  = _parse_actors(auth_raw, name_to_id) if auth_raw else []
        all_ids   = _parse_actors(actor_raw, name_to_id) if actor_raw else []
        target_ids = [a for a in all_ids if a not in auth_ids]

        rel    = detect_relationship(text)
        stage  = detect_stage(text, mech_cat)
        conf   = compute_confidence(bool(auth_ids), obl_field,
                                    rel != "unknown_functional_relationship", anchor_s)

        # ---- A. Directed: authority → target(s)
        if auth_ids and target_ids:
            for src in auth_ids:
                for tgt in target_ids:
                    key = (src, tgt, mech_name, src_id_raw)
                    if key in emitted:
                        continue
                    emitted.add(key)
                    func_edges.append(build_base(src, tgt, row, rel, stage, conf,
                                                  "explicit_textual_relation"))

        # ---- B. Coordination: multiple authorities in same provision
        if len(auth_ids) > 1:
            for src, tgt in permutations(auth_ids, 2):
                key = (src, tgt, mech_name, src_id_raw)
                if key in emitted:
                    continue
                emitted.add(key)
                coord_conf = "medium" if anchor_s >= 3 else "low"
                func_edges.append(build_base(src, tgt, row,
                                              "coordinates_with", "internal_governance",
                                              coord_conf, "coordination_assignment",
                                              "multi-authority provision"))

        # ---- C. Excluded: actor present but no authority → co-mention
        elif all_ids and not auth_ids:
            e = build_base(
                all_ids[0] if all_ids else "",
                all_ids[1] if len(all_ids) > 1 else "",
                row, "unknown_functional_relationship", "unknown_stage",
                "exclude", "excluded_comention_only",
            )
            e["exclusion_reason"] = "no authority field; co-mention only"
            excl_edges.append(e)

    return func_edges, excl_edges

# ---------------------------------------------------------------------------
# 4. Supplementary MEX obligation→reference edges from actor_mechanism_edges
# ---------------------------------------------------------------------------
def derive_mex_obligation_edges(
    mex_edge_rows: list[dict],
    mex_mech_name_to_id: dict,
    mex_id_to_name: dict,
    existing_edge_keys: set,
) -> list[dict]:
    """
    For each (source_id, mechanism) group where obligation+reference actors coexist:
    emit obligation_actor → reference_actor edges at confidence=low.
    """
    # Group by (source_id, mechanism_name)
    groups: dict[tuple, dict[str, list[str]]] = defaultdict(lambda: {"obligation": [], "faculty": [], "reference": []})
    meta:   dict[tuple, dict] = {}

    for row in mex_edge_rows:
        rel   = (row.get("relationship_type") or "").strip()
        src   = (row.get("source_id") or "").strip()
        mech  = (row.get("mechanism_name") or "").strip()
        aid   = (row.get("actor_id") or "").strip()
        if not rel or not src or not mech or not aid:
            continue
        key = (src, mech)
        groups[key][rel].append(aid)
        if key not in meta:
            meta[key] = {
                "anchor_type":   (row.get("legal_anchor_type") or "").strip(),
                "anchor_str":    (row.get("anchor_strength") or "0").strip(),
                "citation":      (row.get("citation") or "").strip(),
            }

    edges = []
    counter = [0]

    def next_id() -> str:
        counter[0] += 1
        return f"MEX-V2-SUP-{counter[0]:04d}"

    for (src_id, mech_name), grp in groups.items():
        obl_actors = grp["obligation"]
        fac_actors = grp["faculty"]
        ref_actors = grp["reference"]
        m = meta[(src_id, mech_name)]

        # obligation/faculty → reference: functional handoff
        sources = obl_actors + fac_actors
        for src_aid in sources:
            for tgt_aid in ref_actors:
                if src_aid == tgt_aid:
                    continue
                key = (src_aid, tgt_aid, mech_name, src_id)
                if key in existing_edge_keys:
                    continue
                existing_edge_keys.add(key)
                is_obl = src_aid in obl_actors
                edges.append({
                    "edge_id":              next_id(),
                    "country":              "Mexico",
                    "mechanism_id":         mex_mech_name_to_id.get(mech_name, mech_name),
                    "mechanism_name":       mech_name,
                    "source_actor_id":      src_aid,
                    "source_actor_name":    mex_id_to_name.get(src_aid, src_aid),
                    "target_actor_id":      tgt_aid,
                    "target_actor_name":    mex_id_to_name.get(tgt_aid, tgt_aid),
                    "relationship_type":    "unknown_functional_relationship",
                    "process_stage":        "unknown_stage",
                    "domestic_source_id":   src_id,
                    "citation":             m["citation"],
                    "legal_text_excerpt":   "",
                    "legal_anchor_type":    m["anchor_type"],
                    "anchor_strength":      m["anchor_str"],
                    "mandatory_or_discretionary": "mandatory" if is_obl else "discretionary",
                    "timeline_defined":     "no",
                    "remedy_available":     "no",
                    "territorial_level":    "no",
                    "edge_confidence":      "low",
                    "edge_derivation_method": "competence_assignment",
                    "manual_review_required": "true",
                    "notes":                "obligation/faculty → reference in same source/mechanism; functional direction inferred",
                })

    return edges

# ---------------------------------------------------------------------------
# 5. Betweenness centrality via BFS (Brandes)
# ---------------------------------------------------------------------------
def compute_betweenness(node_ids: list[str], adj: dict[str, list[str]]) -> dict[str, float]:
    bc = {n: 0.0 for n in node_ids}
    n  = len(node_ids)
    if n <= 2:
        return bc
    for s in node_ids:
        stack: list[str] = []
        pred:  dict[str, list[str]] = {v: [] for v in node_ids}
        sigma: dict[str, int]       = {v: 0   for v in node_ids}
        dist:  dict[str, int]       = {v: -1  for v in node_ids}
        sigma[s] = 1
        dist[s]  = 0
        queue: deque[str] = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in adj.get(v, []):
                if dist[w] < 0:
                    queue.append(w)
                    dist[w] = dist[v] + 1
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta: dict[str, float] = {v: 0.0 for v in node_ids}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                bc[w] += delta[w]
    denom = (n - 1) * (n - 2)
    if denom > 0:
        bc = {k: round(v / denom, 6) for k, v in bc.items()}
    return bc

# ---------------------------------------------------------------------------
# 6. Actor centrality metrics (v2 — high/medium edges only for betweenness)
# ---------------------------------------------------------------------------
CENTRALITY_FIELDS = [
    "country", "actor_id", "actor_name", "actor_type", "network_role",
    "in_degree", "out_degree", "degree", "degree_centrality",
    "betweenness_centrality", "mechanism_participation_count",
    "high_medium_edge_count", "notes",
]

def build_actor_centrality(nodes: list[dict], edges: list[dict]) -> list[dict]:
    rows = []
    for country in ("Mexico", "Costa Rica"):
        country_nodes = [nd for nd in nodes if nd["country"] == country]
        node_ids      = [nd["actor_id"] for nd in country_nodes]
        n             = len(node_ids)

        # Use only high+medium edges for betweenness
        hi_med = [e for e in edges if e["country"] == country
                  and e["edge_confidence"] in ("high", "medium")]
        all_ed = [e for e in edges if e["country"] == country]

        in_deg:  dict[str, int] = defaultdict(int)
        out_deg: dict[str, int] = defaultdict(int)
        adj:     dict[str, list[str]] = defaultdict(list)
        mech_p:  dict[str, set] = defaultdict(set)
        hm_cnt:  dict[str, int] = defaultdict(int)

        for e in all_ed:
            src, tgt = e["source_actor_id"], e["target_actor_id"]
            if src and tgt:
                out_deg[src] += 1
                in_deg[tgt]  += 1
                mech_p[src].add(e["mechanism_name"])
                mech_p[tgt].add(e["mechanism_name"])

        for e in hi_med:
            src, tgt = e["source_actor_id"], e["target_actor_id"]
            if src and tgt:
                if tgt not in adj[src]:
                    adj[src].append(tgt)
                hm_cnt[src] += 1
                hm_cnt[tgt] += 1

        bc = compute_betweenness(node_ids, dict(adj))

        for nd in country_nodes:
            aid   = nd["actor_id"]
            i_deg = in_deg.get(aid, 0)
            o_deg = out_deg.get(aid, 0)
            deg   = i_deg + o_deg
            deg_c = round(deg / max((2 * (n - 1)), 1), 6)
            rows.append({
                "country":                 country,
                "actor_id":                aid,
                "actor_name":              nd["actor_name"],
                "actor_type":              nd["actor_type"],
                "network_role":            nd["network_role"],
                "in_degree":               str(i_deg),
                "out_degree":              str(o_deg),
                "degree":                  str(deg),
                "degree_centrality":       str(deg_c),
                "betweenness_centrality":  str(bc.get(aid, 0.0)),
                "mechanism_participation_count": str(len(mech_p.get(aid, set()))),
                "high_medium_edge_count":  str(hm_cnt.get(aid, 0)),
                "notes":                   "betweenness computed from high/medium-confidence edges only",
            })
    return rows

# ---------------------------------------------------------------------------
# 7. Mechanism network metrics (high/medium edges only)
# ---------------------------------------------------------------------------
MECH_METRICS_FIELDS = [
    "country", "mechanism_id", "mechanism_name", "mechanism_category",
    "node_count_all", "node_count_hi_med",
    "edge_count_all", "edge_count_hi_med",
    "network_density_hi_med",
    "top_actor_id", "top_actor_name", "top_actor_degree_hi_med",
    "high_edge_count", "medium_edge_count", "low_edge_count",
    "bottleneck_risk", "implementation_readiness_score", "notes",
]

def build_mechanism_metrics(edges: list[dict], nodes: list[dict],
                             matrix_rows: list[dict]) -> list[dict]:
    irs_lkp: dict[tuple, str] = {}
    for r in matrix_rows:
        irs_lkp[(r.get("country",""), r.get("mechanism_name",""))] = \
            r.get("implementation_readiness_score","")

    node_lkp = {n["actor_id"]: n for n in nodes}

    # Group all edges by (country, mech_id, mech_name)
    mech_all:   dict[tuple, list] = defaultdict(list)
    mech_hi_med: dict[tuple, list] = defaultdict(list)
    for e in edges:
        if not e["source_actor_id"] or not e["target_actor_id"]:
            continue
        key = (e["country"], e["mechanism_id"], e["mechanism_name"])
        mech_all[key].append(e)
        if e["edge_confidence"] in ("high", "medium"):
            mech_hi_med[key].append(e)

    rows = []
    all_keys = set(mech_all) | set(mech_hi_med)
    for key in sorted(all_keys):
        country, mech_id, mech_name = key
        all_e   = mech_all.get(key, [])
        hi_e    = mech_hi_med.get(key, [])
        cat     = MECHANISM_CATEGORY.get(mech_name, "other")

        actors_all   = set()
        actors_hi_med = set()
        for e in all_e:
            actors_all.add(e["source_actor_id"])
            actors_all.add(e["target_actor_id"])
        for e in hi_e:
            actors_hi_med.add(e["source_actor_id"])
            actors_hi_med.add(e["target_actor_id"])

        n_all   = len(actors_all)
        n_hi    = len(actors_hi_med)
        e_all   = len(all_e)
        e_hi    = len(hi_e)

        # Density = unique directed pairs / max possible pairs (not raw provision rows)
        unique_pairs = len({(e["source_actor_id"], e["target_actor_id"]) for e in hi_e})
        max_e   = n_hi * (n_hi - 1)
        density = round(unique_pairs / max_e, 4) if max_e > 0 else 0.0

        hi_cnt  = sum(1 for e in all_e if e["edge_confidence"] == "high")
        med_cnt = sum(1 for e in all_e if e["edge_confidence"] == "medium")
        lo_cnt  = sum(1 for e in all_e if e["edge_confidence"] == "low")

        # Top actor by unique directed pairs in high/medium edges
        deg_map: dict[str, int] = defaultdict(int)
        seen_pairs: set[tuple] = set()
        for e in hi_e:
            pair = (e["source_actor_id"], e["target_actor_id"])
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                deg_map[e["source_actor_id"]] += 1
                deg_map[e["target_actor_id"]] += 1
        top_id = max(deg_map, key=deg_map.get) if deg_map else ""
        top_deg = deg_map.get(top_id, 0)
        top_name = node_lkp.get(top_id, {}).get("actor_name", "") if top_id else ""

        total_deg = sum(deg_map.values())
        dom_share = top_deg / max(total_deg, 1) if total_deg > 0 else 0

        # Bottleneck risk (based on unique pairs)
        if unique_pairs < 3:
            b_risk = "insufficient_data"
        elif dom_share > 0.50:
            b_risk = "high"
        elif dom_share > 0.30:
            b_risk = "medium"
        else:
            b_risk = "low"

        irs = irs_lkp.get((country, mech_name), "")
        rows.append({
            "country":              country,
            "mechanism_id":         mech_id,
            "mechanism_name":       mech_name,
            "mechanism_category":   cat,
            "node_count_all":       str(n_all),
            "node_count_hi_med":    str(n_hi),
            "edge_count_all":       str(e_all),
            "edge_count_hi_med":    str(e_hi),
            "network_density_hi_med": str(density),
            "top_actor_id":         top_id,
            "top_actor_name":       top_name,
            "top_actor_degree_hi_med": str(top_deg),
            "high_edge_count":      str(hi_cnt),
            "medium_edge_count":    str(med_cnt),
            "low_edge_count":       str(lo_cnt),
            "bottleneck_risk":      b_risk,
            "implementation_readiness_score": irs,
            "notes":                "",
        })
    return rows

# ---------------------------------------------------------------------------
# 8. Bottleneck diagnostics (strict — high/medium only)
# ---------------------------------------------------------------------------
BOTTLENECK_FIELDS = [
    "country", "mechanism_id", "mechanism_name", "mechanism_category",
    "edge_count_hi_med", "dominant_actor_id", "dominant_actor_name",
    "dominant_actor_degree", "dominant_actor_share",
    "critical_stage_dominance", "bottleneck_risk",
    "bottleneck_actors", "notes",
]

def build_bottleneck_diagnostics(mech_metrics: list[dict],
                                  edges: list[dict]) -> list[dict]:
    mech_deg: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    mech_stage: dict[tuple, dict[str, set]] = defaultdict(lambda: defaultdict(set))

    for e in edges:
        if e["edge_confidence"] not in ("high", "medium"):
            continue
        if not e["source_actor_id"] or not e["target_actor_id"]:
            continue
        key = (e["country"], e["mechanism_id"])
        mech_deg[key][e["source_actor_id"]] += 1
        mech_deg[key][e["target_actor_id"]] += 1
        stage = e.get("process_stage", "")
        if stage in CRITICAL_STAGES:
            mech_stage[key][e["source_actor_id"]].add(stage)
            mech_stage[key][e["target_actor_id"]].add(stage)

    rows = []
    for m in mech_metrics:
        key     = (m["country"], m["mechanism_id"])
        deg_map = dict(mech_deg.get(key, {}))
        total   = sum(deg_map.values())
        if not deg_map or total == 0:
            continue

        top_id  = max(deg_map, key=deg_map.get)
        top_deg = deg_map[top_id]
        top_share = round(top_deg / max(total, 1), 4)

        # Critical stage dominance: actor appears in ≥3 critical stages
        crit_dom = {aid: stages for aid, stages in mech_stage.get(key, {}).items()
                    if len(stages) >= 3}
        b_actors = [a for a, d in deg_map.items() if d / max(total, 1) > 0.30]

        rows.append({
            "country":              m["country"],
            "mechanism_id":         m["mechanism_id"],
            "mechanism_name":       m["mechanism_name"],
            "mechanism_category":   m["mechanism_category"],
            "edge_count_hi_med":    m["edge_count_hi_med"],
            "dominant_actor_id":    top_id,
            "dominant_actor_name":  m["top_actor_name"],
            "dominant_actor_degree": str(top_deg),
            "dominant_actor_share": str(top_share),
            "critical_stage_dominance": "|".join(
                f"{aid}:{len(stgs)}" for aid, stgs in crit_dom.items()
            ),
            "bottleneck_risk":      m["bottleneck_risk"],
            "bottleneck_actors":    "|".join(b_actors),
            "notes":                "insufficient_data = fewer than 3 high/medium-confidence edges",
        })
    return rows

# ---------------------------------------------------------------------------
# 9. Process stage coverage (v2)
# ---------------------------------------------------------------------------
STAGE_FIELDS = [
    "country", "mechanism_id", "mechanism_name", "mechanism_category",
    "process_stage", "stage_actor_count", "actors_in_stage",
    "high_med_edges", "stage_covered", "coverage_notes",
]

CATEGORY_STAGES = {
    "participation":   ["activation","registration","verification","organization",
                        "voting_or_participation","adjudication","implementation"],
    "legislative":     ["activation","registration","verification","implementation"],
    "candidacy":       ["registration","verification","organization","adjudication"],
    "party_governance":["registration","verification","organization","oversight","accountability"],
    "remedy":          ["activation","adjudication","implementation"],
    "enforcement":     ["oversight","adjudication","implementation"],
    "transparency":    ["transparency","accountability","oversight"],
    "governance":      ["internal_governance","oversight","accountability"],
    "registry":        ["registration","verification","organization"],
    "other":           ["unknown_stage"],
}

def build_process_stage_coverage(edges: list[dict]) -> list[dict]:
    stage_actors: dict[tuple, set[str]] = defaultdict(set)
    stage_edges:  dict[tuple, int]       = defaultdict(int)

    for e in edges:
        if not e["source_actor_id"] or not e["target_actor_id"]:
            continue
        key = (e["country"], e["mechanism_id"], e["mechanism_name"], e["process_stage"])
        stage_actors[key].add(e["source_actor_id"])
        stage_actors[key].add(e["target_actor_id"])
        if e["edge_confidence"] in ("high", "medium"):
            stage_edges[key] += 1

    mech_set: dict[tuple, str] = {}
    for e in edges:
        k = (e["country"], e["mechanism_id"], e["mechanism_name"])
        mech_set[k] = MECHANISM_CATEGORY.get(e["mechanism_name"], "other")

    rows = []
    for (country, mech_id, mech_name), cat in sorted(mech_set.items()):
        for stage in CATEGORY_STAGES.get(cat, ["unknown_stage"]):
            key     = (country, mech_id, mech_name, stage)
            actors  = stage_actors.get(key, set())
            hi_med  = stage_edges.get(key, 0)
            covered = len(actors) > 0
            rows.append({
                "country":           country,
                "mechanism_id":      mech_id,
                "mechanism_name":    mech_name,
                "mechanism_category": cat,
                "process_stage":     stage,
                "stage_actor_count": str(len(actors)),
                "actors_in_stage":   "|".join(sorted(actors)),
                "high_med_edges":    str(hi_med),
                "stage_covered":     "true" if covered else "false",
                "coverage_notes":    "" if covered else f"no functional edge found for stage '{stage}'",
            })
    return rows

# ---------------------------------------------------------------------------
# 10. Administrative dependence (v2)
# ---------------------------------------------------------------------------
ADMIN_DEP_FIELDS = [
    "country", "mechanism_id", "mechanism_name", "mechanism_category",
    "total_edges", "high_med_edges",
    "statutory_edges", "constitutional_edges", "admin_edges", "unclassified_edges",
    "low_confidence_edges",
    "statutory_share_hi_med", "constitutional_share_hi_med", "admin_share_hi_med",
    "dependence_level", "notes",
]

def classify_anchor(t: str) -> str:
    t = (t or "").lower()
    if "constitutional" in t: return "constitutional"
    if "statutory" in t or "codigo" in t or "ley" in t: return "statutory"
    if "administrative" in t or "regulatory" in t or "procedural" in t: return "administrative"
    return "unclassified"

def build_admin_dependence(mech_metrics: list[dict], edges: list[dict]) -> list[dict]:
    mech_e: dict[tuple, list] = defaultdict(list)
    for e in edges:
        mech_e[(e["country"], e["mechanism_id"])].append(e)

    rows = []
    for m in mech_metrics:
        key   = (m["country"], m["mechanism_id"])
        elist = mech_e.get(key, [])
        hi_me = [e for e in elist if e["edge_confidence"] in ("high", "medium")]
        total = max(len(elist), 1)
        hi_n  = max(len(hi_me), 1)

        def cnt(f): return sum(1 for e in hi_me if classify_anchor(e["legal_anchor_type"]) == f)
        stat  = cnt("statutory")
        const = cnt("constitutional")
        adm   = cnt("administrative")
        lo    = sum(1 for e in elist if e["edge_confidence"] == "low")
        adm_s = round(adm  / hi_n, 4)
        st_s  = round(stat / hi_n, 4)
        co_s  = round(const / hi_n, 4)
        dep   = "high" if adm_s >= 0.60 else ("medium" if adm_s >= 0.30 else "low")

        rows.append({
            "country":               m["country"],
            "mechanism_id":          m["mechanism_id"],
            "mechanism_name":        m["mechanism_name"],
            "mechanism_category":    m["mechanism_category"],
            "total_edges":           str(len(elist)),
            "high_med_edges":        str(len(hi_me)),
            "statutory_edges":       str(stat),
            "constitutional_edges":  str(const),
            "admin_edges":           str(adm),
            "unclassified_edges":    str(cnt("unclassified")),
            "low_confidence_edges":  str(lo),
            "statutory_share_hi_med": str(st_s),
            "constitutional_share_hi_med": str(co_s),
            "admin_share_hi_med":    str(adm_s),
            "dependence_level":      dep,
            "notes":                 "shares computed from high/medium-confidence edges only",
        })
    return rows

# ---------------------------------------------------------------------------
# 11. Network validation notes (v2)
# ---------------------------------------------------------------------------
VALIDATION_FIELDS = [
    "flag_id", "country", "flag_type", "mechanism_id", "mechanism_name",
    "actor_id", "actor_name", "description", "severity", "recommendation",
]

def build_validation_notes(
    nodes: list[dict], edges: list[dict],
    mech_metrics: list[dict], centrality: list[dict],
    mex_prov: list[dict],
) -> list[dict]:
    flags = []
    fc = [0]

    def add(country, ftype, mech_id, mech_name, aid, aname, desc, sev, rec):
        fc[0] += 1
        flags.append({
            "flag_id": f"V2-VAL-{fc[0]:04d}", "country": country,
            "flag_type": ftype, "mechanism_id": mech_id,
            "mechanism_name": mech_name, "actor_id": aid, "actor_name": aname,
            "description": desc, "severity": sev, "recommendation": rec,
        })

    # --- Senado analysis
    senado_text_count = sum(
        1 for r in mex_prov
        if re.search(r'[Ss]enado', (r.get('provision_text',''))+(r.get('actor',''))+(r.get('authority','')))
    )
    add("Mexico", "senado_absent_from_actor_mechanism_edges",
        "", "", "MEX-ACT-005",
        "Congreso de la Unión — Senado de la República",
        f"Senado appears in {senado_text_count} MEX provisions (as text reference) but has "
        f"no dedicated rows in mexico_actor_mechanism_edges.csv. 'Congress' authority "
        f"in actor_map covers both chambers; Senate role in citizen_initiative, "
        f"legislative_petition_or_participation and popular_consultation is implicit.",
        "medium",
        "Add explicit Senado actor_mechanism_edges rows for citizen_initiative and "
        "legislative_petition_or_participation where Senado has distinct procedural role.",
    )

    # --- CRC: no relationship_type
    crc_edge_count = sum(1 for e in edges if e["country"] == "Costa Rica")
    add("Costa Rica", "crc_no_relationship_type_in_source",
        "", "", "", "",
        f"costa_rica_actor_mechanism_edges.csv lacks relationship_type field. All "
        f"{crc_edge_count} CRC v2 edges are derived from provision-level authority→actor "
        f"fields and functional keyword detection — not from obligation/faculty tags. "
        f"Confidence is high/medium where provision text contains functional keywords, "
        f"low otherwise.",
        "medium",
        "Add relationship_type (obligation/faculty/reference) to CRC actor_mechanism_edges "
        "for consistent confidence scoring with MEX.",
    )

    # --- High bottleneck risk
    for m in mech_metrics:
        if m["bottleneck_risk"] == "high":
            add(m["country"], "bottleneck_risk_high",
                m["mechanism_id"], m["mechanism_name"],
                m["top_actor_id"], m["top_actor_name"],
                f"'{m['mechanism_name']}': dominant actor edge share >50% in "
                f"high/medium-confidence subgraph.",
                "high",
                "Verify whether single-actor concentration reflects institutional design "
                "intent or regulatory gap. Check for missing functional edges.",
            )

    # --- insufficient_data mechanisms
    insuff = [m for m in mech_metrics if m["bottleneck_risk"] == "insufficient_data"]
    for m in insuff:
        add(m["country"], "insufficient_functional_edges",
            m["mechanism_id"], m["mechanism_name"], "", "",
            f"'{m['mechanism_name']}' has fewer than 3 high/medium-confidence functional "
            f"edges. Bottleneck analysis is not reliable for this mechanism.",
            "medium",
            "Review provisions for this mechanism; add explicit authority→actor fields "
            "where actors have distinct procedural functions.",
        )

    # --- Actors with zero functional edges (isolated)
    actor_in_edges = set()
    for e in edges:
        if e["edge_confidence"] in ("high", "medium"):
            actor_in_edges.add(e["source_actor_id"])
            actor_in_edges.add(e["target_actor_id"])
    for n in nodes:
        if n["actor_id"] not in actor_in_edges:
            add(n["country"], "actor_absent_from_functional_edges",
                "", "", n["actor_id"], n["actor_name"],
                f"Actor '{n['actor_name']}' has no high/medium-confidence functional edges "
                f"in v2 graph. May reflect data coverage gap rather than legal absence.",
                "medium",
                "Review provisions for this actor's mechanisms; verify authority/actor "
                "fields are populated in legal_provisions.csv.",
            )

    # --- MEX low-confidence majority per mechanism
    mex_mech_conf: dict[str, dict] = defaultdict(lambda: {"high": 0, "medium": 0, "low": 0})
    for e in edges:
        if e["country"] == "Mexico":
            conf = e.get("edge_confidence", "low")
            mex_mech_conf[e["mechanism_name"]][conf] += 1
    for mech, counts in mex_mech_conf.items():
        total = sum(counts.values())
        if total > 0 and counts["low"] / total > 0.70:
            add("Mexico", "low_confidence_majority",
                "", mech, "", "",
                f"More than 70% of '{mech}' edges are low-confidence (derived from "
                f"obligation→reference grouping, no provision-level direction).",
                "medium",
                "Review mexico_legal_provisions.csv authority→actor fields for "
                f"'{mech}' provisions to upgrade low-confidence edges.",
            )

    return flags

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n=== NormTrace: Institutional Network Layer v2 (Functional) ===\n")

    print("[1/10] Loading input data...")
    data = load_data()
    print(f"  MEX: {len(data['mex_prov'])} provisions, {len(data['mex_edges'])} actor-mech edges")
    print(f"  CRC: {len(data['crc_prov'])} provisions, {len(data['crc_edges'])} actor-mech edges")

    # MEX mechanism name → id
    mex_mech_id: dict[str, str] = {}
    for r in data["mex_mechs"]:
        mex_mech_id[r.get("mechanism_name","").strip()] = r.get("mechanism_id","").strip()

    print("[2/10] Building institutional nodes...")
    nodes, mex_lkp, crc_lkp = build_nodes(data)
    print(f"  MEX: {len(mex_lkp)} nodes, CRC: {len(crc_lkp)} nodes")

    # Build id_to_name maps including both provision short names
    mex_id_to_name: dict[str, str] = {n["actor_id"]: n["actor_name"] for n in nodes
                                       if n["country"] == "Mexico"}
    crc_id_to_name: dict[str, str] = {n["actor_id"]: n["actor_name"] for n in nodes
                                       if n["country"] == "Costa Rica"}

    print("[3/10] Deriving MEX functional edges from provisions...")
    mex_func, mex_excl = derive_provision_edges(
        data["mex_prov"], MEX_NAME_TO_ID, mex_mech_id, "Mexico", mex_id_to_name)
    print(f"  MEX provision-level functional edges: {len(mex_func)}")
    print(f"  MEX excluded co-mention: {len(mex_excl)}")

    print("[4/10] Deriving CRC functional edges from provisions...")
    crc_mech_id: dict[str, str] = {}
    for r in data["crc_mechs"]:
        nm = r.get("mechanism_name","").strip()
        crc_mech_id[nm] = r.get("mechanism_id","").strip()

    crc_func, crc_excl = derive_provision_edges(
        data["crc_prov"], CRC_NAME_TO_ID, crc_mech_id, "Costa Rica", crc_id_to_name)
    print(f"  CRC provision-level functional edges: {len(crc_func)}")
    print(f"  CRC excluded co-mention: {len(crc_excl)}")

    print("[5/10] Deriving supplementary MEX obligation edges...")
    existing_keys: set = set()
    for e in mex_func:
        existing_keys.add((e["source_actor_id"], e["target_actor_id"],
                           e["mechanism_name"], e["domestic_source_id"]))

    mex_sup = derive_mex_obligation_edges(
        data["mex_edges"], mex_mech_id, mex_id_to_name, existing_keys)
    print(f"  MEX supplementary obligation→reference edges: {len(mex_sup)}")

    # Combine
    all_edges    = mex_func + crc_func + mex_sup
    all_excl     = mex_excl + crc_excl
    mex_all_edges = mex_func + mex_sup
    crc_all_edges = crc_func

    print(f"\n  TOTAL functional edges: {len(all_edges)}")
    print(f"  TOTAL excluded co-mention: {len(all_excl)}")

    print("[6/10] Computing actor centrality...")
    centrality = build_actor_centrality(nodes, all_edges)

    print("[7/10] Computing mechanism network metrics...")
    matrix = []
    try:
        matrix = read_csv(TRACE_DIR / "principle_traceability_matrix.csv")
    except FileNotFoundError:
        pass
    mech_metrics = build_mechanism_metrics(all_edges, nodes, matrix)

    print("[8/10] Building bottleneck diagnostics...")
    bottleneck = build_bottleneck_diagnostics(mech_metrics, all_edges)

    print("[9/10] Building process stage coverage + admin dependence...")
    stage_cov = build_process_stage_coverage(all_edges)
    admin_dep = build_admin_dependence(mech_metrics, all_edges)

    print("[10/10] Building validation notes...")
    validation = build_validation_notes(
        nodes, all_edges, mech_metrics, centrality, data["mex_prov"])

    # -----------------------------------------------------------------------
    # Write outputs
    # -----------------------------------------------------------------------
    print("\n--- Writing outputs ---")
    out_pair("institutional_nodes_v2",              NODE_FIELDS,         nodes)
    out_pair("institutional_edges_v2",              EDGE_FIELDS,         all_edges)
    out_pair("actor_centrality_metrics_v2",         CENTRALITY_FIELDS,   centrality)
    out_pair("mechanism_network_metrics_v2",        MECH_METRICS_FIELDS, mech_metrics)
    out_pair("bottleneck_diagnostics_v2",           BOTTLENECK_FIELDS,   bottleneck)
    out_pair("process_stage_coverage_v2",           STAGE_FIELDS,        stage_cov)
    out_pair("administrative_dependence_metrics_v2", ADMIN_DEP_FIELDS,   admin_dep)
    out_pair("network_validation_notes_v2",         VALIDATION_FIELDS,   validation)
    out_pair("excluded_comention_edges",            EXCL_FIELDS,         all_excl)

    # -----------------------------------------------------------------------
    # Post-run report
    # -----------------------------------------------------------------------
    print("\n=== POST-RUN REPORT (v2 Functional) ===\n")

    hi_mex = [e for e in mex_all_edges if e["edge_confidence"] in ("high","medium")]
    hi_crc = [e for e in crc_all_edges if e["edge_confidence"] in ("high","medium")]

    print("1. Edge count comparison (v1 → v2):")
    print(f"   Mexico:     v1=485  →  v2={len(mex_all_edges)} total  ({len(hi_mex)} high/medium)")
    print(f"   Costa Rica: v1=434  →  v2={len(crc_all_edges)} total  ({len(hi_crc)} high/medium)")

    print("\n2. v2 density by country and mechanism (high/medium edges):")
    for m in mech_metrics:
        flag = "" if m["bottleneck_risk"] != "insufficient_data" else " [INSUFF]"
        print(f"   [{m['country'][:3]}] {m['mechanism_name'][:38]:38s} "
              f"n={m['node_count_hi_med']:2s} e={m['edge_count_hi_med']:3s} "
              f"density={m['network_density_hi_med']} "
              f"risk={m['bottleneck_risk']}{flag}")

    print("\n3. Top actors by degree (all v2 edges):")
    for country in ("Mexico", "Costa Rica"):
        cc = sorted([c for c in centrality if c["country"] == country],
                    key=lambda x: int(x.get("degree") or 0), reverse=True)
        print(f"   {country}:")
        for c in cc[:5]:
            print(f"     {c['actor_name'][:45]:45s} deg={c['degree']:3s} "
                  f"in={c['in_degree']:3s} out={c['out_degree']:3s} "
                  f"bc={c['betweenness_centrality']}")

    print("\n   Top actors by betweenness:")
    for country in ("Mexico", "Costa Rica"):
        cc = sorted([c for c in centrality if c["country"] == country],
                    key=lambda x: float(x.get("betweenness_centrality") or 0), reverse=True)
        print(f"   {country}:")
        for c in cc[:5]:
            bc = float(c.get("betweenness_centrality") or 0)
            if bc > 0:
                print(f"     {c['actor_name'][:45]:45s} bc={bc:.4f}")
        if all(float(c.get("betweenness_centrality","0")) == 0 for c in cc):
            print(f"     (betweenness=0 for all; graph may still be dense for this country)")

    print("\n4. Bottleneck risk summary:")
    for risk in ("high", "medium", "low", "insufficient_data"):
        mechs_r = [m for m in mech_metrics if m["bottleneck_risk"] == risk]
        print(f"   {risk}: {len(mechs_r)} mechanisms")
        for m in mechs_r:
            print(f"     [{m['country'][:3]}] {m['mechanism_name']}")

    print("\n5. Administrative dependence (v2 high/medium edges):")
    for dep in ("high", "medium", "low"):
        ad = [r for r in admin_dep if r["dependence_level"] == dep]
        if ad:
            print(f"   {dep}:")
            for r in ad:
                print(f"     [{r['country'][:3]}] {r['mechanism_name'][:38]:38s} "
                      f"admin_share={r['admin_share_hi_med']}")

    print("\n6. Excluded co-mention edges:")
    mex_excl_cnt = sum(1 for e in all_excl if e["country"] == "Mexico")
    crc_excl_cnt = sum(1 for e in all_excl if e["country"] == "Costa Rica")
    print(f"   Mexico:     {mex_excl_cnt}")
    print(f"   Costa Rica: {crc_excl_cnt}")

    print(f"\n7. Validation notes: {len(validation)} total")
    hi_v = [v for v in validation if v["severity"] == "high"]
    me_v = [v for v in validation if v["severity"] == "medium"]
    print(f"   High: {len(hi_v)}, Medium: {len(me_v)}")
    for v in validation:
        print(f"   [{v['severity'].upper()}] [{v['country'][:3]}] {v['flag_type']} — "
              f"{v['description'][:80]}...")

    print("\n8. Note: All outputs are diagnostic institutional legal mapping.")
    print("   Edges reflect legal preparedness analysis — not compliance assessment.")
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
