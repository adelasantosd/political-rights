"""
instruments/electoral_rights.py
NormTrace Political Rights — curated standards registry.

Purpose
-------
This module is a data registry, not an AI prompt. It defines the international
and inter-American standards used for preliminary document-level screening of
political and electoral rights. It does not, by itself, establish system-level
compliance. System-level conclusions require the domestic corpus and applicable
jurisprudence for the country under review.

Design principles
-----------------
- Each standard has a stable ID.
- Each standard includes normative force and interpretive authority.
- Standards are intentionally modular so they can feed tables such as
  international_standards, activation_standards, jurisprudence_standards and
  comparative_mapping.
- Soft-law or interpretive materials are marked as such; they are not treated
  as treaties.
"""

from dataclasses import dataclass, field


@dataclass
class Standard:
    """Atomic standard for NormTrace screening."""
    id: str
    right: str
    instrument: str
    article: str
    source_full: str
    content: str
    normative_force: str = "binding_treaty"  # binding_treaty | authorised_interpretation | soft_law | case_law
    authority_type: str = "treaty"
    binding_status_note: str = ""
    source_url: str | None = None
    gc_reference: str | None = None
    case_law: list[str] = field(default_factory=list)
    applies_to_cr: bool = True
    applies_to_mx: bool = True
    gap_types: list[str] = field(default_factory=list)
    required_elements: list[str] = field(default_factory=list)
    minimum_test: str = ""
    comments: str = ""


ELECTORAL_STANDARDS: list[Standard] = [
    Standard(
        id="ICCPR_25_A",
        right="Participation in public affairs",
        instrument="ICCPR",
        article="Art. 25(a)",
        source_full="International Covenant on Civil and Political Rights, art. 25(a), 16 December 1966, 999 UNTS 171.",
        source_url="https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights",
        content="Every citizen has the right and opportunity to take part in the conduct of public affairs, directly or through freely chosen representatives.",
        gc_reference="Human Rights Committee, General Comment No. 25, CCPR/C/21/Rev.1/Add.7, paras. 5–8.",
        normative_force="binding_treaty",
        authority_type="treaty_plus_authorised_interpretation",
        required_elements=["recognition of participation", "direct or representative participation", "non-discriminatory access", "effective opportunity"],
        minimum_test="The text should recognise participation in public affairs and should not reduce it to periodic voting only.",
        gap_types=["total_absence", "recognition_without_guarantee", "restricted_scope", "indirect_discrimination"],
    ),
    Standard(
        id="ICCPR_25_B",
        right="Right to vote and to be elected",
        instrument="ICCPR",
        article="Art. 25(b)",
        source_full="International Covenant on Civil and Political Rights, art. 25(b).",
        source_url="https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights",
        content="Every citizen has the right and opportunity to vote and to be elected at genuine periodic elections by universal and equal suffrage and secret ballot.",
        gc_reference="Human Rights Committee, General Comment No. 25, paras. 9–23.",
        required_elements=["universal suffrage", "equal suffrage", "secret ballot", "periodic elections", "genuine elections", "free expression of electors"],
        minimum_test="The text should contain operative guarantees for voting, candidacy, secrecy, equality and periodicity.",
        gap_types=["regression", "direct_incompatibility", "indirect_discrimination", "recognition_without_guarantee"],
    ),
    Standard(
        id="ICCPR_25_C",
        right="Equal access to public service",
        instrument="ICCPR",
        article="Art. 25(c)",
        source_full="International Covenant on Civil and Political Rights, art. 25(c).",
        content="Every citizen has the right and opportunity to have access, on general terms of equality, to public service.",
        gc_reference="Human Rights Committee, General Comment No. 25, paras. 23–28.",
        required_elements=["equal access", "public service", "objective criteria", "non-discrimination"],
        minimum_test="The text should avoid arbitrary eligibility barriers to public service and candidacy-related public functions.",
        gap_types=["indirect_discrimination", "recognition_without_guarantee"],
    ),
    Standard(
        id="ICCPR_GC25_RESTRICTIONS",
        right="Objective and reasonable restrictions on political rights",
        instrument="HRC General Comment No. 25",
        article="Paras. 4, 10, 14–15",
        source_full="Human Rights Committee, General Comment No. 25, CCPR/C/21/Rev.1/Add.7 (1996).",
        source_url="https://www.refworld.org/legal/general/hrc/1996/en/28176",
        content="Conditions on political rights must be based on objective and reasonable criteria and must not impose unreasonable barriers to candidacy or participation.",
        normative_force="authorised_interpretation",
        authority_type="un_treaty_body_general_comment",
        binding_status_note="Interpretive guidance for ICCPR art. 25; not a treaty provision in itself.",
        required_elements=["objective criteria", "reasonable criteria", "proportional restrictions", "no excessive candidate requirements"],
        minimum_test="The text should specify restrictions narrowly and should include safeguards against arbitrary or excessive barriers.",
        case_law=["IACtHR, Castañeda Gutman v. Mexico, Judgment of 6 August 2008, Series C No. 184."],
        gap_types=["regression", "direct_incompatibility", "recognition_without_guarantee"],
    ),
    Standard(
        id="ACHR_23_1",
        right="Inter-American political rights",
        instrument="ACHR",
        article="Art. 23(1)",
        source_full="American Convention on Human Rights, art. 23(1), 22 November 1969, OASTS 36.",
        source_url="https://www.oas.org/dil/treaties_b-32_american_convention_on_human_rights.htm",
        content="Every citizen has rights and opportunities to participate in public affairs, vote and be elected in genuine periodic elections, and access public service under general conditions of equality.",
        gc_reference="IACtHR OC-28/21, interpretation of ACHR arts. 1, 23, 24 and 32.",
        required_elements=["participation", "vote", "be elected", "periodic elections", "universal and equal suffrage", "secret ballot", "public service equality"],
        case_law=[
            "IACtHR, Yatama v. Nicaragua, Judgment of 23 June 2005, Series C No. 127.",
            "IACtHR, Castañeda Gutman v. Mexico, Judgment of 6 August 2008, Series C No. 184.",
            "IACtHR, López Mendoza v. Venezuela, Judgment of 1 September 2011, Series C No. 233.",
            "IACtHR, Petro Urrego v. Colombia, Judgment of 8 July 2020, Series C No. 406.",
            "IACtHR, López Lone et al. v. Honduras, Judgment of 5 October 2015, Series C No. 302.",
        ],
        minimum_test="The text should recognise political rights as enforceable rights, not merely as administrative electoral procedures.",
        gap_types=["total_absence", "regression", "direct_incompatibility", "recognition_without_guarantee", "implementation_gap"],
    ),
    Standard(
        id="ACHR_23_2",
        right="Permissible restrictions on political rights",
        instrument="ACHR",
        article="Art. 23(2)",
        source_full="American Convention on Human Rights, art. 23(2).",
        content="The law may regulate political rights only on the basis of age, nationality, residence, language, education, civil and mental capacity, or sentencing by a competent court in criminal proceedings.",
        gc_reference="IACtHR OC-28/21; IACtHR López Mendoza and Petro Urrego on disqualification by competent court.",
        required_elements=["closed grounds", "legal basis", "judicial safeguards", "no administrative disqualification from elected office"],
        minimum_test="The text should not create additional grounds for restriction or administrative disqualification inconsistent with ACHR art. 23(2).",
        case_law=["IACtHR, López Mendoza v. Venezuela (2011).", "IACtHR, Petro Urrego v. Colombia (2020)."],
        gap_types=["direct_incompatibility", "regression"],
    ),
    Standard(
        id="ACHR_8_25_REMEDY",
        right="Due process and effective remedy for political rights",
        instrument="ACHR",
        article="Arts. 8 and 25",
        source_full="American Convention on Human Rights, arts. 8 and 25.",
        content="Political rights must be protected through due process and an effective, accessible remedy before competent authorities.",
        required_elements=["competent authority", "fair hearing", "effective remedy", "timely review", "enforceable decision"],
        minimum_test="The text should identify remedies, competent bodies, deadlines or procedures allowing affected persons to challenge violations of political rights.",
        case_law=["IACtHR, Yatama v. Nicaragua (2005).", "IACtHR, Castañeda Gutman v. Mexico (2008)."],
        gap_types=["total_absence", "recognition_without_guarantee", "implementation_gap"],
    ),
    Standard(
        id="OC28_ELECTORAL_INDEPENDENCE",
        right="Independence of electoral bodies and democratic guarantees",
        instrument="IACtHR Advisory Opinion OC-28/21",
        article="OC-28/21",
        source_full="IACtHR, Advisory Opinion OC-28/21, 7 June 2021.",
        content="Electoral administration and dispute-resolution bodies must preserve institutional conditions for democratic participation and rights protection.",
        normative_force="authorised_interpretation",
        authority_type="inter_american_court_advisory_opinion",
        binding_status_note="Advisory opinion; authoritative inter-American interpretation but not a contentious judgment against a State.",
        required_elements=["institutional independence", "impartial electoral administration", "rights-compatible electoral adjudication", "separation of powers"],
        minimum_test="The text should not structurally subordinate electoral authorities to partisan or executive control and should preserve reviewability for rights violations.",
        case_law=["IACtHR, OC-28/21 (2021)."],
        gap_types=["implementation_gap", "recognition_without_guarantee"],
    ),
    Standard(
        id="CRPD_29",
        right="Participation of persons with disabilities in political and public life",
        instrument="CRPD",
        article="Art. 29",
        source_full="Convention on the Rights of Persons with Disabilities, art. 29, 13 December 2006, 2515 UNTS 3.",
        source_url="https://www.un.org/development/desa/disabilities/convention-on-the-rights-of-persons-with-disabilities/article-29-participation-in-political-and-public-life.html",
        content="States must guarantee persons with disabilities political rights and the opportunity to enjoy them on an equal basis with others, including accessible voting procedures, facilities and materials.",
        gc_reference="CRPD Committee, General Comment No. 1 on equal recognition before the law; General Comment No. 2 on accessibility.",
        required_elements=["accessible procedures", "accessible facilities", "accessible materials", "secret ballot", "assistance by person of choice", "right to stand for election", "participation in NGOs and parties"],
        minimum_test="The text should operationalise accessibility and assistance, and should not restrict voting on the basis of disability or legal capacity status.",
        case_law=["CRPD Committee, Bujdosó et al. v. Hungary, CRPD/C/10/D/4/2011."],
        gap_types=["total_absence", "recognition_without_guarantee", "direct_incompatibility", "implementation_gap"],
    ),
    Standard(
        id="CRPD_12_29_LEGAL_CAPACITY",
        right="Legal capacity and political rights of persons with disabilities",
        instrument="CRPD + CRPD Committee GC No. 1",
        article="Arts. 12 and 29",
        source_full="CRPD arts. 12 and 29; CRPD Committee, General Comment No. 1, CRPD/C/GC/1 (2014).",
        content="Legal capacity restrictions must not be used to deny political rights to persons with disabilities.",
        normative_force="binding_treaty_plus_authorised_interpretation",
        authority_type="treaty_plus_un_treaty_body_general_comment",
        binding_status_note="CRPD arts. 12 and 29 are binding; GC No. 1 is interpretive guidance.",
        required_elements=["no guardianship-based disenfranchisement", "supported decision-making", "equal recognition before the law", "no mental-capacity exclusion"],
        minimum_test="The text should avoid terms such as interdiction, incapacity or guardianship as grounds for suspension of voting or candidacy.",
        case_law=["CRPD Committee, Bujdosó et al. v. Hungary, CRPD/C/10/D/4/2011."],
        gap_types=["direct_incompatibility", "regression", "indirect_discrimination"],
    ),
    Standard(
        id="CEDAW_7_8",
        right="Women’s participation in political and public life",
        instrument="CEDAW",
        article="Arts. 7–8",
        source_full="Convention on the Elimination of All Forms of Discrimination against Women, arts. 7–8, 18 December 1979, 1249 UNTS 13.",
        source_url="https://www.ohchr.org/en/instruments-mechanisms/instruments/convention-elimination-all-forms-discrimination-against-women",
        content="States must eliminate discrimination against women in political and public life, including voting, candidacy, public office, participation in policy formulation and international representation.",
        gc_reference="CEDAW Committee, General Recommendation No. 23 (1997); General Recommendation No. 25 (2004) on temporary special measures.",
        required_elements=["vote", "candidacy", "public office", "participation in policy formulation", "temporary special measures where needed", "international representation"],
        minimum_test="The text should include equality and, where appropriate, parity or temporary special measures across candidacies and decision-making bodies.",
        gap_types=["total_absence", "recognition_without_guarantee", "indirect_discrimination", "implementation_gap"],
    ),
    Standard(
        id="CEDAW_GR25_TSM",
        right="Temporary special measures for substantive equality",
        instrument="CEDAW General Recommendation No. 25",
        article="Art. 4(1) interpretation",
        source_full="CEDAW Committee, General Recommendation No. 25 on temporary special measures, 2004.",
        content="Temporary special measures may be required to accelerate de facto equality of women in political and public life.",
        normative_force="authorised_interpretation",
        authority_type="un_treaty_body_general_recommendation",
        binding_status_note="Interpretive guidance for CEDAW arts. 4, 7 and 8.",
        required_elements=["substantive equality", "temporary special measures", "effective implementation", "monitoring"],
        minimum_test="The text should not treat formal equality as sufficient where structural exclusion requires parity, quotas or equivalent measures.",
        gap_types=["recognition_without_guarantee", "implementation_gap", "indirect_discrimination"],
    ),
    Standard(
        id="ILO169_6_7",
        right="Indigenous consultation and participation",
        instrument="ILO Convention 169",
        article="Arts. 6–7",
        source_full="ILO Convention No. 169 concerning Indigenous and Tribal Peoples, arts. 6–7, 27 June 1989, 1650 UNTS 383. Mexico ratified in 1990; Costa Rica ratified in 1993.",
        source_url="https://www.ilo.org/dyn/normlex/en/f?p=NORMLEXPUB:12100:0::NO::P12100_INSTRUMENT_ID:312314",
        content="States must consult indigenous peoples through appropriate procedures and representative institutions whenever legislative or administrative measures may affect them directly.",
        required_elements=["consultation", "appropriate procedures", "representative institutions", "directly affected measures", "participation in development priorities"],
        minimum_test="The text should identify indigenous participation channels and should not reduce consultation to notification or generic public consultation.",
        case_law=["IACtHR, Yatama v. Nicaragua (2005).", "IACtHR, Saramaka People v. Suriname (2007)."],
        gap_types=["total_absence", "recognition_without_guarantee", "implementation_gap"],
    ),
    Standard(
        id="UNDRIP_18_19",
        right="Indigenous participation and free, prior and informed consent",
        instrument="UNDRIP",
        article="Arts. 18–19",
        source_full="United Nations Declaration on the Rights of Indigenous Peoples, UNGA Res. 61/295, arts. 18–19 (2007).",
        source_url="https://www.un.org/development/desa/indigenouspeoples/declaration-on-the-rights-of-indigenous-peoples.html",
        content="Indigenous peoples have the right to participate in decision-making through representatives chosen by themselves and States shall consult to obtain free, prior and informed consent before adopting measures that may affect them.",
        normative_force="soft_law",
        authority_type="un_declaration",
        binding_status_note="Non-treaty declaration; relevant interpretive and normative standard.",
        required_elements=["self-chosen representatives", "FPIC", "legislative measures", "administrative measures"],
        minimum_test="The text should preserve self-representation and prior consultation for affected indigenous peoples.",
        gap_types=["recognition_without_guarantee", "implementation_gap"],
    ),
    Standard(
        id="IDC_2_6",
        right="Democratic governance and effective citizen participation",
        instrument="Inter-American Democratic Charter",
        article="Arts. 2–6",
        source_full="Inter-American Democratic Charter, OAS General Assembly Resolution AG/RES. 1 (XXVIII-E/01), 11 September 2001.",
        content="Representative democracy requires respect for human rights, periodic free and fair elections, secret ballot, pluralist parties, separation of powers, and citizen participation.",
        normative_force="soft_law",
        authority_type="oas_democratic_instrument",
        binding_status_note="OAS democratic instrument; used as interpretive context in the inter-American system.",
        required_elements=["free and fair elections", "pluralist party system", "separation of powers", "citizen participation", "transparency", "accountability"],
        minimum_test="The text should support democratic participation beyond electoral administration alone.",
        gap_types=["implementation_gap", "recognition_without_guarantee"],
    ),
]


def get_standards_for_country(iso: str) -> list[Standard]:
    """Return applicable standards for a given country ISO code."""
    iso = iso.upper()
    if iso == "CR":
        return [s for s in ELECTORAL_STANDARDS if s.applies_to_cr]
    if iso == "MX":
        return [s for s in ELECTORAL_STANDARDS if s.applies_to_mx]
    return ELECTORAL_STANDARDS


def get_standard(standard_id: str) -> Standard | None:
    return next((s for s in ELECTORAL_STANDARDS if s.id == standard_id), None)


def list_instruments() -> list[dict]:
    """Return a summary of instruments and their methodological status."""
    instruments: dict[str, dict] = {}
    for s in ELECTORAL_STANDARDS:
        if s.instrument not in instruments:
            instruments[s.instrument] = {
                "instrument": s.instrument,
                "standards_count": 0,
                "articles": [],
                "normative_force": set(),
                "authority_type": set(),
            }
        instruments[s.instrument]["standards_count"] += 1
        instruments[s.instrument]["articles"].append(s.article)
        instruments[s.instrument]["normative_force"].add(s.normative_force)
        instruments[s.instrument]["authority_type"].add(s.authority_type)

    out = []
    for item in instruments.values():
        item["normative_force"] = sorted(item["normative_force"])
        item["authority_type"] = sorted(item["authority_type"])
        out.append(item)
    return out
