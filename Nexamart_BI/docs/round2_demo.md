# Round 2 demonstration

## Run locally

```text
python Nexamart_BI/run_pipeline.py
python -m pytest -q Nexamart_BI/tests
python -m compileall Nexamart_BI/backend Nexamart_BI/dashboard Nexamart_BI/src
uvicorn Nexamart_BI.backend.main:app --port 8000
streamlit run Nexamart_BI/dashboard/app.py
```

## Evidence to show

- Five KPI fields calculated from sales, marketing, and inventory sources.
- Independent aggregation before joining at day grain.
- No customer segment many-to-many join.
- Latest available source date and per-source freshness.
- Deterministic materiality and price-volume-mix decomposition.
- P999 sparse-history abstention below 28 history days.
- Stale-source and contradictory-evidence abstention.
- Executive and Analyst demo entitlements with different narrative depth; demo mode provides evidence-only persona-specific wording when no LLM endpoint is configured.
- Persistent feedback, `/api/feedback/evaluation` calibration output, and runtime telemetry in the local state store.
- Actions are suppressed when materiality, confidence, or policy gates fail.
- LLM failure returns an explicit error and never fabricates business numbers.

## Required presenter language

Say “latest available source date” when data is stale. Say “supporting signal” rather than “cause” unless validated attribution or causal inference exists. Do not claim model learning until feedback is evaluated and used in a measured update loop.
