#!/usr/bin/env python3
"""
build_institutional_network_layer.py
NormTrace Political Rights — Institutional Actor-Network Pipeline

Derives directed actor→actor edges from actor-mechanism associations,
computes network metrics (degree, betweenness via BFS, bottleneck risk),
and writes 8 CSV + 8 JSON output tables.

No external dependencies beyond the Python standard library.
"""

import csv
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from itertools import combinations

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE         = Path(__file__).resolve().parent.parent
BRAIN_DIR    = BASE / "03_tables" / "country_legal_brains"
TRACE_DIR    = BASE / "03_tables" / "principle_traceability"
OUT_DIR      = BASE / "03_tables" / "institutional_network"
WEBAPP_DIR   = BASE / "05_webapp" / "public" / "data" / "institutional_network"

OUT_DIR.mkdir(parents=True, exist_ok=True)
WEBAPP_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Role taxonomy
# ---------------------------------------------------------------------------
ACTOR_ROLE = {
    "autonomous_electoral_authority":  "orchestrator",
    "constitutional_electoral_authority": "orchestrator",
    "electoral_court":                 "adjudicator",
    "constitutional_court":            "adjudicator",
    "supreme_court":                   "supervisor",
    "legislative_body":                "legislator",
    "executive_power":                 "executive",
    "prosecutorial_authority":         "enforcer",
    "oversight_body":                  "supervisor",
    "local_electoral_authority":       "subordinate",
    "civil_registry_electoral_body":   "subordinate",
    "subordinate_electoral_body":      "subordinate",
    "political_organization":          "political_actor",
    "rights_holder":                   "rights_holder",
}

ROLE_RANK = {
    "adjudicator":    5,
    "supervisor":     4,
    "legislator":     4,
    "orchestrator":   3,
    "executive":      3,
    "enforcer":       3,
    "subordinate":    2,
    "political_actor": 1,
    "rights_holder":  0,
}

# (source_role, target_role) → relationship label
EDGE_RELATIONSHIP = {
    ("adjudicator",  "orchestrator"):   "reviews",
    ("adjudicator",  "subordinate"):    "reviews",
    ("adjudicator",  "political_actor"): "reviews",
    ("adjudicator",  "enforcer"):       "reviews",
    ("supervisor",   "orchestrator"):   "oversees",
    ("supervisor",   "subordinate"):    "oversees",
    ("supervisor",   "adjudicator"):    "oversees",
    ("legislator",   "orchestrator"):   "mandates",
    ("legislator",   "subordinate"):    "mandates",
    ("orchestrator", "subordinate"):    "supervises",
    ("orchestrator", "political_actor"): "regulates",
    ("orchestrator", "rights_holder"):  "administers",
    ("orchestrator", "enforcer"):       "refers_to",
    ("executive",    "orchestrator"):   "coordinates_with",
    ("executive",    "subordinate"):    "coordinates_with",
    ("enforcer",     "political_actor"): "investigates",
    ("enforcer",     "rights_holder"):  "investigates",
    ("enforcer",     "orchestrator"):   "reports_to",
}

def get_relationship(source_role: str, target_role: str) -> str:
    return EDGE_RELATIONSHIP.get(
        (source_role, target_role),
        "coordinates_with"
    )

# ---------------------------------------------------------------------------
# Mechanism categories and process stage assignments
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

# Canonical process stages covered by each mechanism category
CATEGORY_STAGES = {
    "participation": [
        "registration",
        "voting_day_administration",
        "vote_counting_and_tabulation",
        "results_certification",
        "electoral_dispute_resolution",
    ],
    "legislative": [
        "citizen_initiative_processing",
        "results_certification",
    ],
    "candidacy": [
        "nomination_or_candidacy",
        "results_certification",
        "electoral_dispute_resolution",
    ],
    "party_governance": [
        "party_registration_and_oversight",
        "campaign",
        "transparency_and_reporting",
    ],
    "remedy": [
        "electoral_dispute_resolution",
        "constitutional_review",
    ],
    "enforcement": [
        "sanctions_and_enforcement",
    ],
    "transparency": [
        "transparency_and_reporting",
    ],
    "governance": [
        "internal_governance",
    ],
    "registry": [
        "civil_registry_functions",
    ],
}

# Which roles cover each process stage
STAGE_ROLES = {
    "registration":                  {"orchestrator", "subordinate"},
    "nomination_or_candidacy":       {"orchestrator", "adjudicator", "political_actor", "rights_holder"},
    "campaign":                      {"political_actor", "orchestrator", "supervisor"},
    "voting_day_administration":     {"orchestrator", "subordinate"},
    "vote_counting_and_tabulation":  {"orchestrator", "subordinate"},
    "results_certification":         {"orchestrator", "adjudicator"},
    "electoral_dispute_resolution":  {"adjudicator", "supervisor"},
    "constitutional_review":         {"adjudicator", "supervisor"},
    "party_registration_and_oversight": {"orchestrator"},
    "citizen_initiative_processing": {"orchestrator", "legislator"},
    "referendum_administration":     {"orchestrator", "legislator"},
    "transparency_and_reporting":    {"orchestrator", "supervisor"},
    "internal_governance":           {"orchestrator"},
    "civil_registry_functions":      {"subordinate", "orchestrator"},
    "sanctions_and_enforcement":     {"enforcer", "adjudicator"},
}

# ---------------------------------------------------------------------------
# CRC short name → actor_id mapping
# ---------------------------------------------------------------------------
CRC_SHORT_TO_ID = {
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

# ---------------------------------------------------------------------------
# Legal anchor → edge category
# ---------------------------------------------------------------------------
def classify_anchor(anchor_type: str) -> str:
    t = (anchor_type or "").lower()
    if "constitutional" in t:
        return "constitutional"
    if "statutory" in t or "electoral_statutory" in t:
        return "statutory"
    if "administrative" in t or "regulatory" in t or "procedural" in t:
        return "administrative"
    return "unclassified"

# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------
def read_csv_semicolon(path: Path) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        for row in reader:
            rows.append({k.strip().strip('"'): v.strip().strip('"') for k, v in row.items()})
    return rows

def write_csv(path: Path, fieldnames: list, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",",
                                quotechar='"', quoting=csv.QUOTE_ALL,
                                extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

def write_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def out_pair(out_dir: Path, webapp_dir: Path, stem: str,
             fieldnames: list, rows: list[dict]):
    csv_path  = out_dir / f"{stem}.csv"
    json_path = webapp_dir / f"{stem}.json"
    write_csv(csv_path, fieldnames, rows)
    write_json(json_path, rows)
    print(f"  wrote {csv_path.name} ({len(rows)} rows)")
    print(f"  wrote {json_path.name}")

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
def load_data() -> dict:
    d = {}
    d["mex_actors"]   = read_csv_semicolon(BRAIN_DIR / "mexico"     / "mexico_actor_map.csv")
    d["mex_edges"]    = read_csv_semicolon(BRAIN_DIR / "mexico"     / "mexico_actor_mechanism_edges.csv")
    d["mex_mechs"]    = read_csv_semicolon(BRAIN_DIR / "mexico"     / "mexico_mechanism_map.csv")
    d["crc_actors"]   = read_csv_semicolon(BRAIN_DIR / "costa_rica" / "costa_rica_actor_map.csv")
    d["crc_edges"]    = read_csv_semicolon(BRAIN_DIR / "costa_rica" / "costa_rica_actor_mechanism_edges.csv")
    d["crc_mechs"]    = read_csv_semicolon(BRAIN_DIR / "costa_rica" / "costa_rica_mechanism_map.csv")
    try:
        d["matrix"] = read_csv_semicolon(TRACE_DIR / "principle_traceability_matrix.csv")
    except FileNotFoundError:
        d["matrix"] = []
        print("  [WARN] principle_traceability_matrix.csv not found — IRS enrichment skipped")
    return d

# ---------------------------------------------------------------------------
# 2. Build actor registry (nodes)
# ---------------------------------------------------------------------------
NODE_FIELDS = [
    "country", "actor_id", "actor_name", "actor_type", "network_role",
    "mechanism_count", "mechanisms", "legal_preparedness_role",
    "manual_review_required", "notes",
]

def build_nodes(data: dict) -> tuple[list[dict], dict, dict]:
    """
    Returns (nodes_rows, actor_lookup_mex, actor_lookup_crc).
    actor_lookup_* maps actor_id → node dict.
    """
    nodes = []
    mex_lookup: dict[str, dict] = {}
    crc_lookup: dict[str, dict] = {}

    for row in data["mex_actors"]:
        actor_id = row.get("actor_id", "")
        if not actor_id or actor_id == "actor_id":
            continue
        actor_type = row.get("actor_type", "")
        mechs_raw  = row.get("mechanisms", "")
        mech_list  = [m.strip() for m in mechs_raw.split("|") if m.strip()]
        node = {
            "country":               "Mexico",
            "actor_id":              actor_id,
            "actor_name":            row.get("actor_name", ""),
            "actor_type":            actor_type,
            "network_role":          ACTOR_ROLE.get(actor_type, "unknown"),
            "mechanism_count":       str(len(mech_list)),
            "mechanisms":            "|".join(mech_list),
            "legal_preparedness_role": row.get("legal_preparedness_role", ""),
            "manual_review_required": row.get("manual_review_required", "false"),
            "notes":                 row.get("notes", ""),
        }
        nodes.append(node)
        mex_lookup[actor_id] = node

    for row in data["crc_actors"]:
        actor_id = row.get("actor_id", "")
        if not actor_id or actor_id == "actor_id":
            continue
        actor_type = row.get("actor_type", "")
        mechs_raw  = row.get("mechanisms", "")
        mech_list  = [m.strip() for m in mechs_raw.split("|") if m.strip()]
        node = {
            "country":               "Costa Rica",
            "actor_id":              actor_id,
            "actor_name":            row.get("actor_name", ""),
            "actor_type":            actor_type,
            "network_role":          ACTOR_ROLE.get(actor_type, "unknown"),
            "mechanism_count":       str(len(mech_list)),
            "mechanisms":            "|".join(mech_list),
            "legal_preparedness_role": row.get("legal_preparedness_role", ""),
            "manual_review_required": row.get("manual_review_required", "false"),
            "notes":                 row.get("notes", ""),
        }
        nodes.append(node)
        crc_lookup[actor_id] = node

    return nodes, mex_lookup, crc_lookup

# ---------------------------------------------------------------------------
# 3. Build directed edges
# ---------------------------------------------------------------------------
EDGE_FIELDS = [
    "edge_id", "country", "source_actor_id", "source_actor_name", "source_role",
    "target_actor_id", "target_actor_name", "target_role",
    "mechanism_id", "mechanism_name", "mechanism_category",
    "relationship_type", "process_stage", "edge_confidence",
    "legal_anchor_type", "anchor_strength", "anchor_category",
    "derivation_method", "manual_review_required", "notes",
]

def _actor_pairs_for_mechanism(actor_edges: list[dict]) -> list[tuple]:
    """Given edges for one mechanism, return all (a, b) ordered pairs with direction."""
    actors = actor_edges  # each dict has actor_id, role, anchor, etc.
    pairs = []
    for i, a in enumerate(actors):
        for j, b in enumerate(actors):
            if i >= j:
                continue
            rank_a = ROLE_RANK.get(a["role"], 0)
            rank_b = ROLE_RANK.get(b["role"], 0)
            if rank_a > rank_b:
                pairs.append((a, b))
            elif rank_b > rank_a:
                pairs.append((b, a))
            else:
                # same rank: bidirectional — add both
                pairs.append((a, b))
                pairs.append((b, a))
    return pairs

def build_edges(data: dict, mex_lookup: dict, crc_lookup: dict) -> list[dict]:
    # ---- MEX: mechanism_id → name
    mex_mech_name = {}
    for r in data["mex_mechs"]:
        mid = r.get("mechanism_id", "")
        mn  = r.get("mechanism_name", "")
        if mid and mid != "mechanism_id":
            mex_mech_name[mid] = mn

    # ---- Group MEX edges by mechanism
    mex_by_mech: dict[str, list[dict]] = defaultdict(list)
    for r in data["mex_edges"]:
        actor_id = r.get("actor_id", "")
        mech_id  = r.get("mechanism_id", "")
        if not actor_id or actor_id == "actor_id":
            continue
        if actor_id not in mex_lookup:
            continue
        node = mex_lookup[actor_id]
        rel_type   = r.get("relationship_type", "reference")
        anchor_str = r.get("anchor_strength", "0")
        anchor_type = r.get("legal_anchor_type", "")
        mex_by_mech[mech_id].append({
            "actor_id":   actor_id,
            "actor_name": node["actor_name"],
            "role":       node["network_role"],
            "rel_type":   rel_type,
            "anchor_str": anchor_str,
            "anchor_type": anchor_type,
        })

    # ---- Group CRC edges by mechanism
    # CRC edges use short actor names; we resolve to actor_id
    crc_by_mech: dict[str, list[dict]] = defaultdict(list)
    for r in data["crc_edges"]:
        short_name = r.get("actor", "")
        mech_name  = r.get("mechanism", "")
        if not short_name or short_name == "actor":
            continue
        actor_id = CRC_SHORT_TO_ID.get(short_name)
        if not actor_id or actor_id not in crc_lookup:
            # fallback: try to find by substring
            actor_id = next(
                (aid for aid, nd in crc_lookup.items()
                 if short_name.lower().replace("_", " ") in nd["actor_name"].lower()),
                None
            )
        if not actor_id:
            print(f"  [WARN] CRC: cannot resolve actor '{short_name}'")
            continue
        node = crc_lookup[actor_id]
        anchor_str  = r.get("anchor_strength", "0")
        anchor_type = r.get("legal_anchor_type", "")
        crc_by_mech[mech_name].append({
            "actor_id":   actor_id,
            "actor_name": node["actor_name"],
            "role":       node["network_role"],
            "rel_type":   None,              # CRC has no relationship_type
            "anchor_str": anchor_str,
            "anchor_type": anchor_type,
        })

    edges = []
    edge_counter = 0

    def _confidence_mex(src: dict, tgt: dict) -> str:
        # Use relationship_type of the higher-authority actor
        dominant_rel = src.get("rel_type") or tgt.get("rel_type") or "reference"
        if dominant_rel == "obligation":
            return "high"
        if dominant_rel == "faculty":
            return "medium"
        return "low"

    def _primary_anchor(actor_list: list[dict]) -> tuple[str, str]:
        best_str = -1
        best_type = ""
        for a in actor_list:
            try:
                s = int(a.get("anchor_str") or 0)
            except ValueError:
                s = 0
            if s > best_str:
                best_str = s
                best_type = a.get("anchor_type", "")
        return best_type, str(max(best_str, 0))

    def _process_stage_for_mech(mech_name: str, src_role: str, tgt_role: str) -> str:
        cat = MECHANISM_CATEGORY.get(mech_name, "other")
        stages = CATEGORY_STAGES.get(cat, [])
        roles_present = {src_role, tgt_role}
        for stage in stages:
            if roles_present & STAGE_ROLES.get(stage, set()):
                return stage
        return stages[0] if stages else "unknown"

    # ---- Emit MEX edges
    for mech_id, actor_list in mex_by_mech.items():
        mech_name = mex_mech_name.get(mech_id, mech_id)
        mech_cat  = MECHANISM_CATEGORY.get(mech_name, "other")
        # Deduplicate actors in this mechanism
        seen_ids: dict[str, dict] = {}
        for a in actor_list:
            aid = a["actor_id"]
            if aid not in seen_ids or (
                ROLE_RANK.get(a["role"], 0) > ROLE_RANK.get(seen_ids[aid]["role"], 0)
            ):
                seen_ids[aid] = a
        unique_actors = list(seen_ids.values())

        for src, tgt in _actor_pairs_for_mechanism(unique_actors):
            anchor_type, anchor_str = _primary_anchor([src, tgt])
            edge_counter += 1
            edges.append({
                "edge_id":           f"MEX-EDGE-{edge_counter:04d}",
                "country":           "Mexico",
                "source_actor_id":   src["actor_id"],
                "source_actor_name": src["actor_name"],
                "source_role":       src["role"],
                "target_actor_id":   tgt["actor_id"],
                "target_actor_name": tgt["actor_name"],
                "target_role":       tgt["role"],
                "mechanism_id":      mech_id,
                "mechanism_name":    mech_name,
                "mechanism_category": mech_cat,
                "relationship_type": get_relationship(src["role"], tgt["role"]),
                "process_stage":     _process_stage_for_mech(mech_name, src["role"], tgt["role"]),
                "edge_confidence":   _confidence_mex(src, tgt),
                "legal_anchor_type": anchor_type,
                "anchor_strength":   anchor_str,
                "anchor_category":   classify_anchor(anchor_type),
                "derivation_method": "role_hierarchy_with_relationship_type_hint",
                "manual_review_required": "false",
                "notes":             "",
            })

    # ---- Emit CRC edges
    for mech_name, actor_list in crc_by_mech.items():
        mech_id  = f"CRC-MECH-{mech_name.upper()[:12]}"
        mech_cat = MECHANISM_CATEGORY.get(mech_name, "other")
        seen_ids: dict[str, dict] = {}
        for a in actor_list:
            aid = a["actor_id"]
            if aid not in seen_ids or (
                ROLE_RANK.get(a["role"], 0) > ROLE_RANK.get(seen_ids[aid]["role"], 0)
            ):
                seen_ids[aid] = a
        unique_actors = list(seen_ids.values())

        for src, tgt in _actor_pairs_for_mechanism(unique_actors):
            anchor_type, anchor_str = _primary_anchor([src, tgt])
            try:
                anc_int = int(anchor_str)
            except ValueError:
                anc_int = 0
            confidence = "medium" if anc_int >= 3 else "low"
            edge_counter += 1
            edges.append({
                "edge_id":           f"CRC-EDGE-{edge_counter:04d}",
                "country":           "Costa Rica",
                "source_actor_id":   src["actor_id"],
                "source_actor_name": src["actor_name"],
                "source_role":       src["role"],
                "target_actor_id":   tgt["actor_id"],
                "target_actor_name": tgt["actor_name"],
                "target_role":       tgt["role"],
                "mechanism_id":      mech_id,
                "mechanism_name":    mech_name,
                "mechanism_category": mech_cat,
                "relationship_type": get_relationship(src["role"], tgt["role"]),
                "process_stage":     _process_stage_for_mech(mech_name, src["role"], tgt["role"]),
                "edge_confidence":   confidence,
                "legal_anchor_type": anchor_type,
                "anchor_strength":   anchor_str,
                "anchor_category":   classify_anchor(anchor_type),
                "derivation_method": "role_hierarchy_only",
                "manual_review_required": "false",
                "notes":             "CRC: no relationship_type in source data; confidence from anchor_strength",
            })

    return edges

# ---------------------------------------------------------------------------
# 4. Betweenness centrality (BFS — no networkx)
# ---------------------------------------------------------------------------
def compute_betweenness(nodes_in_graph: list[str],
                        adj: dict[str, list[str]]) -> dict[str, float]:
    """
    Brandes' algorithm for betweenness centrality (directed graph).
    Returns raw (unnormalised) betweenness scores.
    """
    bc: dict[str, float] = {n: 0.0 for n in nodes_in_graph}
    n = len(nodes_in_graph)
    if n <= 2:
        return bc

    for s in nodes_in_graph:
        # BFS
        stack: list[str] = []
        pred:  dict[str, list[str]] = {n: [] for n in nodes_in_graph}
        sigma: dict[str, int]       = {n: 0   for n in nodes_in_graph}
        dist:  dict[str, int]       = {n: -1  for n in nodes_in_graph}
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
        # Back-propagation
        delta: dict[str, float] = {n: 0.0 for n in nodes_in_graph}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                bc[w] += delta[w]

    # Normalise by (n-1)*(n-2) for directed graph
    denom = (n - 1) * (n - 2)
    if denom > 0:
        bc = {k: round(v / denom, 6) for k, v in bc.items()}
    return bc

# ---------------------------------------------------------------------------
# 5. Actor centrality metrics
# ---------------------------------------------------------------------------
CENTRALITY_FIELDS = [
    "country", "actor_id", "actor_name", "actor_type", "network_role",
    "in_degree", "out_degree", "degree", "degree_centrality",
    "betweenness_centrality", "mechanism_participation_count",
    "high_strength_mechanism_count", "notes",
]

def build_actor_centrality(nodes: list[dict], edges: list[dict]) -> list[dict]:
    rows = []
    for country in ("Mexico", "Costa Rica"):
        country_nodes = [n for n in nodes if n["country"] == country]
        country_edges = [e for e in edges if e["country"] == country]
        node_ids = [n["actor_id"] for n in country_nodes]

        in_deg:  dict[str, int] = defaultdict(int)
        out_deg: dict[str, int] = defaultdict(int)
        adj:     dict[str, list[str]] = defaultdict(list)
        mech_participation: dict[str, set] = defaultdict(set)

        for e in country_edges:
            src, tgt = e["source_actor_id"], e["target_actor_id"]
            out_deg[src] += 1
            in_deg[tgt]  += 1
            if tgt not in adj[src]:
                adj[src].append(tgt)
            mech_participation[src].add(e["mechanism_name"])
            mech_participation[tgt].add(e["mechanism_name"])

        bc = compute_betweenness(node_ids, dict(adj))
        n  = len(node_ids)
        # betweenness = 0 for all is expected when the collapsed actor graph is
        # near-complete (most actors share direct edges via multiple mechanisms),
        # leaving no actor as an exclusive bridge between any pair.
        bc_all_zero = all(v == 0.0 for v in bc.values())

        for node in country_nodes:
            aid   = node["actor_id"]
            i_deg = in_deg.get(aid, 0)
            o_deg = out_deg.get(aid, 0)
            deg   = i_deg + o_deg
            deg_c = round(deg / max((2 * (n - 1)), 1), 6)
            bc_note = (
                "betweenness=0 expected: near-complete graph; use degree_centrality for influence ranking"
                if bc_all_zero else ""
            )
            rows.append({
                "country":                    country,
                "actor_id":                   aid,
                "actor_name":                 node["actor_name"],
                "actor_type":                 node["actor_type"],
                "network_role":               node["network_role"],
                "in_degree":                  str(i_deg),
                "out_degree":                 str(o_deg),
                "degree":                     str(deg),
                "degree_centrality":          str(deg_c),
                "betweenness_centrality":     str(bc.get(aid, 0.0)),
                "mechanism_participation_count": str(len(mech_participation.get(aid, set()))),
                "high_strength_mechanism_count": "",
                "notes":                      bc_note,
            })

    return rows

# ---------------------------------------------------------------------------
# 6. Mechanism network metrics
# ---------------------------------------------------------------------------
MECH_METRICS_FIELDS = [
    "country", "mechanism_id", "mechanism_name", "mechanism_category",
    "node_count", "edge_count", "network_density",
    "top_actor_id", "top_actor_name", "top_actor_degree",
    "orchestrator_count", "adjudicator_count", "subordinate_count",
    "statutory_edge_share", "constitutional_edge_share", "admin_edge_share",
    "high_confidence_edge_share", "low_confidence_edge_share",
    "bottleneck_risk", "implementation_readiness_score", "notes",
]

def build_mechanism_metrics(edges: list[dict], nodes: list[dict],
                             matrix: list[dict]) -> list[dict]:
    # IRS lookup
    irs_lookup: dict[tuple, str] = {}
    for r in matrix:
        key = (r.get("country", ""), r.get("mechanism_name", ""))
        irs_lookup[key] = r.get("implementation_readiness_score", "")

    node_lookup = {n["actor_id"]: n for n in nodes}

    # Group edges by (country, mechanism_id, mechanism_name)
    mech_edges: dict[tuple, list[dict]] = defaultdict(list)
    for e in edges:
        key = (e["country"], e["mechanism_id"], e["mechanism_name"])
        mech_edges[key].append(e)

    rows = []
    for (country, mech_id, mech_name), mech_edge_list in sorted(mech_edges.items()):
        cat = MECHANISM_CATEGORY.get(mech_name, "other")

        # Unique nodes
        actor_ids: set[str] = set()
        for e in mech_edge_list:
            actor_ids.add(e["source_actor_id"])
            actor_ids.add(e["target_actor_id"])
        n_nodes = len(actor_ids)
        n_edges = len(mech_edge_list)
        max_edges = n_nodes * (n_nodes - 1)
        density = round(n_edges / max_edges, 4) if max_edges > 0 else 0.0

        # Role counts
        role_counts: dict[str, int] = defaultdict(int)
        for aid in actor_ids:
            nd = node_lookup.get(aid)
            if nd:
                role_counts[nd["network_role"]] += 1

        # Top actor by degree within this mechanism
        deg_in_mech: dict[str, int] = defaultdict(int)
        for e in mech_edge_list:
            deg_in_mech[e["source_actor_id"]] += 1
            deg_in_mech[e["target_actor_id"]] += 1
        top_actor_id = max(deg_in_mech, key=deg_in_mech.get) if deg_in_mech else ""
        top_actor_name = node_lookup.get(top_actor_id, {}).get("actor_name", "")
        top_actor_deg  = deg_in_mech.get(top_actor_id, 0)

        # Anchor category shares
        stat_cnt  = sum(1 for e in mech_edge_list if e["anchor_category"] == "statutory")
        const_cnt = sum(1 for e in mech_edge_list if e["anchor_category"] == "constitutional")
        adm_cnt   = sum(1 for e in mech_edge_list if e["anchor_category"] == "administrative")
        hi_cnt    = sum(1 for e in mech_edge_list if e["edge_confidence"] == "high")
        lo_cnt    = sum(1 for e in mech_edge_list if e["edge_confidence"] == "low")
        total     = max(n_edges, 1)
        stat_share  = round(stat_cnt  / total, 4)
        const_share = round(const_cnt / total, 4)
        adm_share   = round(adm_cnt   / total, 4)
        hi_share    = round(hi_cnt    / total, 4)
        lo_share    = round(lo_cnt    / total, 4)

        # Bottleneck risk
        if n_nodes > 0:
            conc = top_actor_deg / max((2 * n_edges), 1) if n_edges > 0 else 0
        else:
            conc = 0
        if conc > 0.50:
            b_risk = "high"
        elif conc > 0.30:
            b_risk = "medium"
        else:
            b_risk = "low"

        irs = irs_lookup.get((country, mech_name), "")

        rows.append({
            "country":               country,
            "mechanism_id":          mech_id,
            "mechanism_name":        mech_name,
            "mechanism_category":    cat,
            "node_count":            str(n_nodes),
            "edge_count":            str(n_edges),
            "network_density":       str(density),
            "top_actor_id":          top_actor_id,
            "top_actor_name":        top_actor_name,
            "top_actor_degree":      str(top_actor_deg),
            "orchestrator_count":    str(role_counts.get("orchestrator", 0)),
            "adjudicator_count":     str(role_counts.get("adjudicator", 0)),
            "subordinate_count":     str(role_counts.get("subordinate", 0)),
            "statutory_edge_share":  str(stat_share),
            "constitutional_edge_share": str(const_share),
            "admin_edge_share":      str(adm_share),
            "high_confidence_edge_share": str(hi_share),
            "low_confidence_edge_share":  str(lo_share),
            "bottleneck_risk":       b_risk,
            "implementation_readiness_score": irs,
            "notes":                 "",
        })

    return rows

# ---------------------------------------------------------------------------
# 7. Bottleneck diagnostics
# ---------------------------------------------------------------------------
BOTTLENECK_FIELDS = [
    "country", "mechanism_id", "mechanism_name", "mechanism_category",
    "node_count", "edge_count", "dominant_actor_id", "dominant_actor_name",
    "dominant_actor_degree", "dominant_actor_edge_share",
    "single_actor_concentration", "bottleneck_risk", "bottleneck_actors",
    "notes",
]

def build_bottleneck_diagnostics(mech_metrics: list[dict],
                                  edges: list[dict]) -> list[dict]:
    # Build per-mech actor degree map from edges
    mech_actor_deg: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for e in edges:
        key = (e["country"], e["mechanism_id"])
        mech_actor_deg[key][e["source_actor_id"]] += 1
        mech_actor_deg[key][e["target_actor_id"]] += 1

    rows = []
    for m in mech_metrics:
        key   = (m["country"], m["mechanism_id"])
        degs  = dict(mech_actor_deg.get(key, {}))
        total = sum(degs.values())
        if not degs or total == 0:
            continue

        # Actors above 30% threshold
        bottleneck_actors = [
            aid for aid, d in degs.items()
            if d / total > 0.30
        ]

        dom_id  = m["top_actor_id"]
        dom_deg = int(m.get("top_actor_degree", 0) or 0)
        dom_share = round(dom_deg / max(total, 1), 4)

        rows.append({
            "country":                  m["country"],
            "mechanism_id":             m["mechanism_id"],
            "mechanism_name":           m["mechanism_name"],
            "mechanism_category":       m["mechanism_category"],
            "node_count":               m["node_count"],
            "edge_count":               m["edge_count"],
            "dominant_actor_id":        dom_id,
            "dominant_actor_name":      m["top_actor_name"],
            "dominant_actor_degree":    str(dom_deg),
            "dominant_actor_edge_share": str(dom_share),
            "single_actor_concentration": str(dom_share),
            "bottleneck_risk":          m["bottleneck_risk"],
            "bottleneck_actors":        "|".join(bottleneck_actors),
            "notes": "high risk = >50% edge share; medium = 30-50%",
        })

    return rows

# ---------------------------------------------------------------------------
# 8. Process stage coverage
# ---------------------------------------------------------------------------
STAGE_FIELDS = [
    "country", "mechanism_id", "mechanism_name", "mechanism_category",
    "process_stage", "stage_actor_count", "actors_in_stage",
    "stage_covered", "coverage_notes",
]

def build_process_stage_coverage(edges: list[dict],
                                  nodes: list[dict]) -> list[dict]:
    node_role = {n["actor_id"]: n["network_role"] for n in nodes}

    # Collect actors per (country, mech, stage)
    stage_actors: dict[tuple, set] = defaultdict(set)
    for e in edges:
        key = (e["country"], e["mechanism_id"], e["mechanism_name"], e["process_stage"])
        stage_actors[key].add(e["source_actor_id"])
        stage_actors[key].add(e["target_actor_id"])

    # For each mechanism, enumerate expected stages
    mech_set: dict[tuple, str] = {}
    for e in edges:
        k = (e["country"], e["mechanism_id"], e["mechanism_name"])
        mech_set[k] = e["mechanism_category"]

    rows = []
    for (country, mech_id, mech_name), cat in sorted(mech_set.items()):
        expected_stages = CATEGORY_STAGES.get(cat, [])
        # Stages actually seen in edges
        seen_stages: set[str] = {
            k[3] for k in stage_actors if k[0] == country and k[1] == mech_id
        }
        # Emit one row per expected stage
        for stage in expected_stages:
            actors = stage_actors.get((country, mech_id, mech_name, stage), set())
            # Also check if any actor in the mechanism has a role that covers this stage
            all_mech_actors = {
                a for k, aset in stage_actors.items()
                if k[0] == country and k[1] == mech_id
                for a in aset
            }
            role_covered = any(
                node_role.get(a) in STAGE_ROLES.get(stage, set())
                for a in all_mech_actors
            )
            covered = len(actors) > 0 or role_covered
            rows.append({
                "country":           country,
                "mechanism_id":      mech_id,
                "mechanism_name":    mech_name,
                "mechanism_category": cat,
                "process_stage":     stage,
                "stage_actor_count": str(len(actors)),
                "actors_in_stage":   "|".join(sorted(actors)),
                "stage_covered":     "true" if covered else "false",
                "coverage_notes":    "" if covered else f"no actor covers '{stage}' in this mechanism",
            })

    return rows

# ---------------------------------------------------------------------------
# 9. Administrative dependence metrics
# ---------------------------------------------------------------------------
ADMIN_DEP_FIELDS = [
    "country", "mechanism_id", "mechanism_name", "mechanism_category",
    "total_edge_count", "statutory_edges", "constitutional_edges",
    "admin_edges", "unclassified_edges", "low_confidence_edges",
    "statutory_share", "constitutional_share", "admin_share",
    "low_confidence_share", "dependence_level", "notes",
]

def build_admin_dependence(mech_metrics: list[dict],
                            edges: list[dict]) -> list[dict]:
    # Build counts per mechanism from raw edges
    mech_edge_map: dict[tuple, list[dict]] = defaultdict(list)
    for e in edges:
        key = (e["country"], e["mechanism_id"])
        mech_edge_map[key].append(e)

    rows = []
    for m in mech_metrics:
        key   = (m["country"], m["mechanism_id"])
        melist = mech_edge_map.get(key, [])
        total  = max(len(melist), 1)

        stat  = sum(1 for e in melist if e["anchor_category"] == "statutory")
        const = sum(1 for e in melist if e["anchor_category"] == "constitutional")
        adm   = sum(1 for e in melist if e["anchor_category"] == "administrative")
        uncl  = sum(1 for e in melist if e["anchor_category"] == "unclassified")
        low_c = sum(1 for e in melist if e["edge_confidence"] == "low")

        adm_share   = round(adm  / total, 4)
        const_share = round(const / total, 4)
        stat_share  = round(stat  / total, 4)
        lo_share    = round(low_c / total, 4)

        if adm_share >= 0.60:
            dep_level = "high"
        elif adm_share >= 0.30:
            dep_level = "medium"
        else:
            dep_level = "low"

        rows.append({
            "country":               m["country"],
            "mechanism_id":          m["mechanism_id"],
            "mechanism_name":        m["mechanism_name"],
            "mechanism_category":    m["mechanism_category"],
            "total_edge_count":      str(len(melist)),
            "statutory_edges":       str(stat),
            "constitutional_edges":  str(const),
            "admin_edges":           str(adm),
            "unclassified_edges":    str(uncl),
            "low_confidence_edges":  str(low_c),
            "statutory_share":       str(stat_share),
            "constitutional_share":  str(const_share),
            "admin_share":           str(adm_share),
            "low_confidence_share":  str(lo_share),
            "dependence_level":      dep_level,
            "notes": "high admin dependence = ≥60% edges from admin/regulatory sources",
        })

    return rows

# ---------------------------------------------------------------------------
# 10. Network validation notes
# ---------------------------------------------------------------------------
VALIDATION_FIELDS = [
    "flag_id", "country", "flag_type", "mechanism_id", "mechanism_name",
    "actor_id", "actor_name", "description", "severity", "recommendation",
]

def build_validation_notes(nodes: list[dict], edges: list[dict],
                            mech_metrics: list[dict],
                            centrality: list[dict]) -> list[dict]:
    flags = []
    flag_counter = 0

    def add_flag(country, flag_type, mech_id, mech_name,
                 actor_id, actor_name, desc, severity, rec):
        nonlocal flag_counter
        flag_counter += 1
        flags.append({
            "flag_id":      f"VAL-{flag_counter:04d}",
            "country":      country,
            "flag_type":    flag_type,
            "mechanism_id": mech_id,
            "mechanism_name": mech_name,
            "actor_id":     actor_id,
            "actor_name":   actor_name,
            "description":  desc,
            "severity":     severity,
            "recommendation": rec,
        })

    # Flag 1: isolated actors (no edges)
    actor_in_edges: set[str] = set()
    for e in edges:
        actor_in_edges.add(e["source_actor_id"])
        actor_in_edges.add(e["target_actor_id"])
    for n in nodes:
        if n["actor_id"] not in actor_in_edges:
            add_flag(
                n["country"], "isolated_actor",
                "", "", n["actor_id"], n["actor_name"],
                f"Actor '{n['actor_name']}' has no derived edges — may indicate missing mechanism coverage",
                "medium",
                "Verify actor's mechanism assignments in actor_map and confirm edge data completeness",
            )

    # Flag 2: high bottleneck risk mechanisms
    for m in mech_metrics:
        if m["bottleneck_risk"] == "high":
            add_flag(
                m["country"], "bottleneck_risk_high",
                m["mechanism_id"], m["mechanism_name"],
                m["top_actor_id"], m["top_actor_name"],
                f"Mechanism '{m['mechanism_name']}' has high single-actor concentration "
                f"(top actor: {m['top_actor_name']}, degree share >50%)",
                "high",
                "Verify whether single-actor concentration reflects intended legal design or regulatory gap",
            )

    # Flag 3: low-confidence edges >50%
    for m in mech_metrics:
        lo_share = float(m.get("low_confidence_edge_share") or 0)
        if lo_share > 0.50:
            add_flag(
                m["country"], "low_confidence_majority",
                m["mechanism_id"], m["mechanism_name"],
                "", "",
                f">50% of edges in '{m['mechanism_name']}' are low-confidence "
                f"({round(lo_share*100)}%); relationships may not reflect statutory obligations",
                "medium",
                "Cross-check source provisions; consider adding relationship_type field to CRC edges",
            )

    # Flag 4: mechanisms with no adjudicator
    for m in mech_metrics:
        if int(m.get("adjudicator_count") or 0) == 0:
            cat = m["mechanism_category"]
            if cat in ("participation", "candidacy", "remedy"):
                add_flag(
                    m["country"], "missing_adjudicator",
                    m["mechanism_id"], m["mechanism_name"],
                    "", "",
                    f"Mechanism '{m['mechanism_name']}' (category: {cat}) has no adjudicator actor — "
                    f"dispute resolution pathway unclear",
                    "high",
                    "Verify whether an electoral or constitutional court has jurisdiction over this mechanism",
                )

    # Flag 5: very high betweenness (potential single points of failure)
    for c in centrality:
        bc = float(c.get("betweenness_centrality") or 0)
        if bc > 0.30:
            add_flag(
                c["country"], "high_betweenness_centrality",
                "", "", c["actor_id"], c["actor_name"],
                f"Actor '{c['actor_name']}' has betweenness centrality {bc:.4f} — "
                f"acts as key bridge across multiple mechanisms",
                "medium",
                "Assess whether institutional concentration creates systemic fragility; "
                "verify backup channels exist",
            )

    # Flag 6: CRC mechanisms with role_hierarchy_only derivation
    crc_total = sum(1 for e in edges if e["country"] == "Costa Rica")
    crc_lo_conf = sum(1 for e in edges
                      if e["country"] == "Costa Rica" and e["edge_confidence"] == "low")
    if crc_total > 0:
        add_flag(
            "Costa Rica", "crc_no_relationship_type",
            "", "", "", "",
            f"All {crc_total} Costa Rica edges derived by role hierarchy only "
            f"(source file lacks relationship_type field); {crc_lo_conf} are low-confidence "
            f"(anchor_strength <3), remainder are medium-confidence",
            "medium",
            "Add relationship_type (obligation/faculty/reference) to costa_rica_actor_mechanism_edges.csv "
            "for higher-confidence edge derivation",
        )

    return flags

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("\n=== NormTrace: Institutional Network Layer ===\n")

    print("[1/9] Loading input data...")
    data = load_data()
    print(f"  MEX actors: {len(data['mex_actors'])}, edges: {len(data['mex_edges'])}, mechs: {len(data['mex_mechs'])}")
    print(f"  CRC actors: {len(data['crc_actors'])}, edges: {len(data['crc_edges'])}, mechs: {len(data['crc_mechs'])}")
    print(f"  Matrix rows: {len(data['matrix'])}")

    print("[2/9] Building institutional nodes...")
    nodes, mex_lookup, crc_lookup = build_nodes(data)
    mex_nodes = [n for n in nodes if n["country"] == "Mexico"]
    crc_nodes = [n for n in nodes if n["country"] == "Costa Rica"]
    print(f"  MEX nodes: {len(mex_nodes)}, CRC nodes: {len(crc_nodes)}")

    print("[3/9] Deriving directed edges...")
    edges = build_edges(data, mex_lookup, crc_lookup)
    mex_edges = [e for e in edges if e["country"] == "Mexico"]
    crc_edges = [e for e in edges if e["country"] == "Costa Rica"]
    print(f"  MEX edges: {len(mex_edges)}, CRC edges: {len(crc_edges)}")

    print("[4/9] Computing actor centrality...")
    centrality = build_actor_centrality(nodes, edges)

    print("[5/9] Computing mechanism network metrics...")
    mech_metrics = build_mechanism_metrics(edges, nodes, data["matrix"])

    print("[6/9] Building bottleneck diagnostics...")
    bottleneck = build_bottleneck_diagnostics(mech_metrics, edges)

    print("[7/9] Building process stage coverage...")
    stage_coverage = build_process_stage_coverage(edges, nodes)

    print("[8/9] Building administrative dependence metrics...")
    admin_dep = build_admin_dependence(mech_metrics, edges)

    print("[9/9] Building network validation notes...")
    validation = build_validation_notes(nodes, edges, mech_metrics, centrality)

    # -----------------------------------------------------------------------
    # Write outputs
    # -----------------------------------------------------------------------
    print("\n--- Writing outputs ---")
    out_pair(OUT_DIR, WEBAPP_DIR, "institutional_nodes",    NODE_FIELDS,       nodes)
    out_pair(OUT_DIR, WEBAPP_DIR, "institutional_edges",    EDGE_FIELDS,       edges)
    out_pair(OUT_DIR, WEBAPP_DIR, "actor_centrality_metrics", CENTRALITY_FIELDS, centrality)
    out_pair(OUT_DIR, WEBAPP_DIR, "mechanism_network_metrics", MECH_METRICS_FIELDS, mech_metrics)
    out_pair(OUT_DIR, WEBAPP_DIR, "bottleneck_diagnostics", BOTTLENECK_FIELDS, bottleneck)
    out_pair(OUT_DIR, WEBAPP_DIR, "process_stage_coverage", STAGE_FIELDS,      stage_coverage)
    out_pair(OUT_DIR, WEBAPP_DIR, "administrative_dependence_metrics", ADMIN_DEP_FIELDS, admin_dep)
    out_pair(OUT_DIR, WEBAPP_DIR, "network_validation_notes", VALIDATION_FIELDS, validation)

    # -----------------------------------------------------------------------
    # Post-run report
    # -----------------------------------------------------------------------
    print("\n=== POST-RUN REPORT ===\n")

    # 1. Nodes by country
    print("1. Nodes by country:")
    for country in ("Mexico", "Costa Rica"):
        cn = [n for n in nodes if n["country"] == country]
        print(f"   {country}: {len(cn)} actors")

    # 2. Edges by country
    print("\n2. Edges by country:")
    for country in ("Mexico", "Costa Rica"):
        ce = [e for e in edges if e["country"] == country]
        print(f"   {country}: {len(ce)} directed edges")

    # 3. Mechanisms mapped
    mex_mechs_mapped = set(e["mechanism_name"] for e in mex_edges)
    crc_mechs_mapped = set(e["mechanism_name"] for e in crc_edges)
    print(f"\n3. Mechanisms mapped:")
    print(f"   Mexico ({len(mex_mechs_mapped)}): {', '.join(sorted(mex_mechs_mapped))}")
    print(f"   Costa Rica ({len(crc_mechs_mapped)}): {', '.join(sorted(crc_mechs_mapped))}")

    # 4. Top 5 actors by betweenness per country
    print("\n4. Top 5 actors by betweenness centrality:")
    for country in ("Mexico", "Costa Rica"):
        cc = sorted(
            [c for c in centrality if c["country"] == country],
            key=lambda x: float(x.get("betweenness_centrality") or 0),
            reverse=True
        )[:5]
        print(f"   {country}:")
        for c in cc:
            print(f"     {c['actor_name']}: {c['betweenness_centrality']}")

    # 5. High bottleneck risk mechanisms
    high_bot = [m for m in mech_metrics if m["bottleneck_risk"] == "high"]
    print(f"\n5. Mechanisms with HIGH bottleneck risk ({len(high_bot)}):")
    for m in high_bot:
        print(f"   [{m['country']}] {m['mechanism_name']} — top actor: {m['top_actor_name']}")

    # 6. High administrative dependence
    high_adm = [r for r in admin_dep if r["dependence_level"] == "high"]
    print(f"\n6. Mechanisms with HIGH administrative dependence ({len(high_adm)}):")
    for r in high_adm:
        print(f"   [{r['country']}] {r['mechanism_name']} — admin share: {r['admin_share']}")

    # 7. Process stages with weak coverage
    weak = [s for s in stage_coverage if s["stage_covered"] == "false"]
    print(f"\n7. Process stages with weak coverage ({len(weak)}):")
    for s in weak[:10]:
        print(f"   [{s['country']}] {s['mechanism_name']} / {s['process_stage']}: {s['coverage_notes']}")
    if len(weak) > 10:
        print(f"   ... and {len(weak)-10} more")

    # 8. Output files
    print("\n8. Output files created:")
    for stem in [
        "institutional_nodes", "institutional_edges", "actor_centrality_metrics",
        "mechanism_network_metrics", "bottleneck_diagnostics",
        "process_stage_coverage", "administrative_dependence_metrics",
        "network_validation_notes",
    ]:
        p = OUT_DIR / f"{stem}.csv"
        print(f"   {p}")
        print(f"   {WEBAPP_DIR / (stem + '.json')}")

    # 9. Manual review flags
    high_flags = [v for v in validation if v["severity"] == "high"]
    med_flags  = [v for v in validation if v["severity"] == "medium"]
    print(f"\n9. Manual review flags: {len(validation)} total ({len(high_flags)} high, {len(med_flags)} medium)")
    for v in validation:
        print(f"   [{v['severity'].upper()}] {v['flag_type']} — {v['country']} {v['mechanism_name'] or v['actor_name']}: {v['description'][:80]}...")

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
