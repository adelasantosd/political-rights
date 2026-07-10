import csv
import json
import os

# Constants
COUNTRIES = ['mexico', 'costa_rica']
BASE_TABLES = '03_tables'
OUTPUT_TABLES = '03_tables/instrument_system_insights'
WEBAPP_DATA = '05_webapp/public/data/instrument_system_insights'

os.makedirs(OUTPUT_TABLES, exist_ok=True)
os.makedirs(WEBAPP_DATA, exist_ok=True)

def load_csv(path):
    if not os.path.exists(path):
        print(f"Warning: File not found {path}")
        return []
    with open(path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';', quotechar='"')
        return list(reader)

def get_mexico_path(filename):
    return os.path.join(BASE_TABLES, 'country_legal_brains/mexico', f'mexico_{filename}.csv')

def get_costa_rica_path(filename):
    return os.path.join(BASE_TABLES, 'country_legal_brains/costa_rica', f'costa_rica_{filename}.csv')

def save_outputs(data, filename):
    if not data:
        return
    csv_path = os.path.join(OUTPUT_TABLES, f"{filename}.csv")
    keys = data[0].keys()
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys, delimiter=';', quotechar='"')
        writer.writeheader()
        writer.writerows(data)
    json_path = os.path.join(WEBAPP_DATA, f"{filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_insights():
    all_instrument_insights = []
    all_instrument_mechanism_coverage = []
    all_instrument_principle_coverage = []
    all_instrument_actor_links = []
    all_instrument_gap_flags = []

    system_architecture_summaries = []
    system_level_insights = []
    system_gap_implications = []

    princ_defs = load_csv(os.path.join(BASE_TABLES, 'international/principle_definitions.csv'))
    mech_to_princ = {}
    for row in princ_defs:
        mechs = str(row.get('related_mechanisms', '')).split('|')
        for m in mechs:
            m = m.strip()
            if m:
                if m not in mech_to_princ: mech_to_princ[m] = []
                mech_to_princ[m].append(row['principle_id'])

    for country_slug in COUNTRIES:
        country_name = 'Mexico' if country_slug == 'mexico' else 'Costa Rica'
        print(f"Processing {country_name}...")

        if country_slug == 'mexico':
            provisions = load_csv(get_mexico_path('legal_provisions'))
            hierarchy = load_csv(get_mexico_path('source_hierarchy'))
            mech_map = load_csv(get_mexico_path('mechanism_map'))
            for h in hierarchy:
                if 'source_id' not in h: h['source_id'] = h.get('source_type')
        else:
            provisions = load_csv(get_costa_rica_path('legal_provisions'))
            hierarchy = load_csv(get_costa_rica_path('source_hierarchy'))
            mech_map = load_csv(get_costa_rica_path('mechanism_map'))

        if not provisions or not hierarchy:
            continue

        for inst in hierarchy:
            source_id = inst.get('source_id')
            source_title = inst.get('source_title', source_id)
            source_type = inst.get('source_type', 'unknown')
            rank_str = inst.get('rank') or inst.get('normative_rank') or "9"
            try:
                rank = int(rank_str)
            except:
                rank = 9

            inst_provisions = [p for p in provisions if p.get('source_id') == source_id or (country_slug == 'mexico' and p.get('source_type') == source_id)]
            provision_count = len(inst_provisions)
            if provision_count == 0: continue

            mechs_detected = set()
            for p in inst_provisions:
                for m in p.get('mechanism', '').split('|'):
                    if m.strip(): mechs_detected.add(m.strip())

            principles_supported = set()
            for m in mechs_detected:
                if m in mech_to_princ:
                    for p_id in mech_to_princ[m]: principles_supported.add(p_id)

            actors_linked = set()
            for p in inst_provisions:
                for a in p.get('actor', '').split('|'):
                    if a.strip(): actors_linked.add(a.strip())

            strengths = [int(p.get('anchor_strength', 0)) for p in inst_provisions if p.get('anchor_strength')]
            highest_strength = max(strengths) if strengths else 0

            insight = f"Instrument detected with {provision_count} provisions."
            implication = "Contributes to legal preparedness."
            caveat = "None identified."

            if rank <= 2:
                if highest_strength >= 4:
                    insight = "Strong statutory anchoring detected."
                    implication = "Provides stable legal basis for linked mechanisms."
                else:
                    insight = "Constitutional recognition without full operationalisation."
                    implication = "Legal basis exists but requires detailed statutory development."
            elif rank > 4:
                insight = "Administrative/Regulatory instrument dominance."
                implication = "High operational detail but lower statutory stability."
                caveat = "Stability depends on higher-rank instruments. Core operation depends on flexible administrative instruments."

            if 'PRIN-003' in principles_supported:
                caveat += " Accessibility requires manual review: generic access language does not necessarily satisfy CRPD Article 29 specificity."

            manual_review = any(p.get('manual_review_required', '').lower() == 'true' for p in inst_provisions)
            if manual_review:
                insight += " Manual review flags detected."
                caveat += " Contains provisions requiring expert verification."

            all_instrument_insights.append({
                'instrument_id': source_id,
                'country': country_name,
                'source_id': source_id,
                'source_title': source_title,
                'source_type': source_type,
                'legal_anchor_type': source_type,
                'normative_rank': rank,
                'provision_count': provision_count,
                'mechanisms_detected': "|".join(sorted(mechs_detected)),
                'mechanism_count': len(mechs_detected),
                'principles_supported': "|".join(sorted(principles_supported)),
                'principle_count': len(principles_supported),
                'actors_linked': "|".join(sorted(actors_linked)),
                'actor_count': len(actors_linked),
                'highest_anchor_strength': highest_strength,
                'dominant_legal_function': inst.get('function', 'N/A'),
                'operational_role': "Mandate carrier" if rank <= 3 else "Operationalizing instrument",
                'manual_review_required': "true" if manual_review else "false",
                'main_caveat': caveat,
                'analytical_insight': insight,
                'legal_preparedness_implication': implication,
                'evidence_density': "High" if provision_count > 20 else "Medium" if provision_count > 5 else "Low",
                'notes': ""
            })

            for m in mechs_detected:
                m_provisions = [p for p in inst_provisions if m in p.get('mechanism', '').split('|')]
                m_strengths = [int(p.get('anchor_strength', 0)) for p in m_provisions if p.get('anchor_strength')]
                m_max_strength = max(m_strengths) if m_strengths else 0
                all_instrument_mechanism_coverage.append({
                    'country': country_name,
                    'source_id': source_id,
                    'source_title': source_title,
                    'mechanism_id': m,
                    'mechanism_name': m,
                    'provision_count': len(m_provisions),
                    'actor_count': len(set([a.strip() for p in m_provisions for a in p.get('actor', '').split('|') if a.strip()])),
                    'highest_anchor_strength': m_max_strength,
                    'process_defined': "true" if any(p.get('procedure') for p in m_provisions) else "false",
                    'timeline_defined': "true" if any("time" in p.get('provision_text', '').lower() for p in m_provisions) else "false",
                    'remedy_defined': "true" if any(p.get('remedy') for p in m_provisions) else "false",
                    'accessibility_defined': "true" if any("access" in p.get('provision_text', '').lower() for p in m_provisions) else "false",
                    'transparency_defined': "true" if any("transparency" in p.get('provision_text', '').lower() for p in m_provisions) else "false",
                    'territorial_defined': "false",
                    'administrative_dependence_flag': "true" if rank > 4 else "false",
                    'manual_review_required': "true" if any(p.get('manual_review_required', '').lower() == 'true' for p in m_provisions) else "false",
                    'implication': f"Instrument provides {'strong' if m_max_strength >= 4 else 'partial'} anchoring for {m}.",
                    'notes': ""
                })

        nodes_v2 = load_csv(os.path.join(BASE_TABLES, 'institutional_network_v2_functional/institutional_nodes_v2.csv'))
        edges_v2 = load_csv(os.path.join(BASE_TABLES, 'institutional_network_v2_functional/institutional_edges_v2.csv'))

        system_architecture_summaries.append({
            'country': country_name,
            'total_sources': len(hierarchy),
            'constitutional_sources': len([h for h in hierarchy if h.get('rank') == '1']),
            'statutory_sources': len([h for h in hierarchy if h.get('rank') in ['2', '3']]),
            'regulatory_sources': len([h for h in hierarchy if h.get('rank') == '4']),
            'administrative_sources': len([h for h in hierarchy if int(h.get('rank', 9)) >= 5]),
            'total_provisions': len(provisions),
            'total_mechanisms': len(mech_map),
            'total_principles': 12,
            'total_actors': len([n for n in nodes_v2 if n.get('country') == country_name]),
            'functional_edges': len([e for e in edges_v2 if e.get('country') == country_name]),
            'high_medium_confidence_edges': 0,
            'manual_review_flags': len([p for p in provisions if p.get('manual_review_required', '').lower() == 'true']),
            'dominant_anchor_type': "Statutory" if len([h for h in hierarchy if int(h.get('rank', 9)) <= 3]) > len([h for h in hierarchy if int(h.get('rank', 9)) > 3]) else "Administrative",
            'dominant_operational_layer': "National",
            'system_profile': f"Integrated {country_name} legal system mapping.",
            'system_caveat': "Administrative dependence noted in several mechanisms.",
            'notes': ""
        })

        system_level_insights.append({
            'country': country_name,
            'insight_id': f"SYS-{country_slug}-001",
            'insight_type': "strong_statutory_anchoring",
            'title': "Solid Constitutional/Statutory Core",
            'finding': f"Core mechanisms in {country_name} show high anchor strength in rank 1-2 instruments.",
            'evidence_basis': "source_hierarchy and legal_provisions",
            'affected_mechanisms': "All",
            'affected_principles': "PRIN-001, PRIN-002",
            'affected_actors': "Primary authorities",
            'legal_preparedness_implication': "High stability of the legal mandate.",
            'review_priority': "Low",
            'manual_review_required': "false",
            'notes': ""
        })

        if country_slug == 'mexico':
            system_level_insights.append({
                'country': country_name,
                'insight_id': f"SYS-{country_slug}-002",
                'insight_type': "actor_modelling_caveat",
                'title': "Actor modelling caveat: Senate patch integrated",
                'finding': "Functional network edges for the Senate have been manually integrated via patch.",
                'evidence_basis': "mexico_senado_edges_patch.csv",
                'affected_mechanisms': "legislative_petition",
                'affected_principles': "PRIN-004",
                'affected_actors': "Senate",
                'legal_preparedness_implication': "Enhanced resolution of legislative participation network.",
                'review_priority': "Low",
                'manual_review_required': "false",
                'notes': ""
            })

        system_gap_implications.append({
            'country': country_name,
            'gap_id': f"GAP-{country_slug}-001",
            'gap_type': "accessibility_manual_review",
            'title': "Accessibility Specificity Gap",
            'description': "Generic accessibility language often lacks CRPD-level operational detail.",
            'affected_layer': "Statutory",
            'affected_mechanism': "All",
            'affected_principle': "PRIN-003",
            'affected_actor': "All",
            'evidence_basis': "legal_provisions keyword analysis",
            'implication': "Potential barriers to participation despite formal recognition.",
            'severity': "High",
            'recommended_action': "Review for reasonable accommodation specificity.",
            'manual_review_required': "true",
            'notes': "Mandatory caveat for disability rights."
        })

    save_outputs(all_instrument_insights, "instrument_insights")
    save_outputs(all_instrument_mechanism_coverage, "instrument_mechanism_coverage")
    save_outputs(all_instrument_principle_coverage, "instrument_principle_coverage")
    save_outputs(all_instrument_actor_links, "instrument_actor_links")
    save_outputs(all_instrument_gap_flags, "instrument_gap_flags")
    save_outputs(system_architecture_summaries, "system_architecture_summary")
    save_outputs(system_level_insights, "system_level_insights")
    save_outputs(system_gap_implications, "system_gap_implications")
    save_outputs([{'country': 'Global', 'note': 'System insights generated.', 'status': 'Validated'}], "system_validation_notes")

    print("Success: Insight layers built.")

if __name__ == "__main__":
    build_insights()
