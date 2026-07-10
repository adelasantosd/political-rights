# NormTrace Political Rights — improved backend files

This package contains improved replacement files for the current Political Rights MVP.

## Main methodological changes

1. The standards registry was expanded from a minimal set into a more auditable registry with `normative_force`, `authority_type`, `source_url`, `required_elements`, `minimum_test` and `binding_status_note`.

2. The analysis result now distinguishes preliminary document-level screening from system-level legal compliance. Absence in an uploaded statute is treated as a document-level signal unless the full domestic corpus confirms system-level absence.

3. The score is relabelled as `preliminary_structural_risk_signal`, not a compliance score.

4. The Mexico profile no longer assumes that INE councillors are elected by popular vote as current valid law. This was replaced with a verification warning.

5. Country profiles now include `corpus_coverage` and methodological warnings.

6. Claude narrative generation is constrained so it cannot convert document-level gaps into definitive system-level findings.

## Files changed

- `instruments/electoral_rights.py`
- `app/data/country_profiles.py`
- `app/services/analysis_service.py`
- `app/services/claude_service.py`
- `app/routers/analysis.py`
- `app/routers/instruments.py`
- `main.py`

## Recommended integration

Copy these files into the corresponding locations in the existing backend. Before deployment, run:

```bash
python -m py_compile instruments/electoral_rights.py app/data/country_profiles.py app/services/analysis_service.py app/services/claude_service.py app/routers/analysis.py app/routers/instruments.py main.py
```

Then run your local API tests against `/api/v1/instruments`, `/api/v1/analysis/text`, and `/api/v1/analysis/compare`.

## Remaining work

These files improve the structure, but the project still needs a real domestic corpus for Mexico and Costa Rica. The next methodological step is to add constitutions, electoral statutes, participation laws, administrative guidelines and jurisprudence as versioned Markdown sources with metadata.
