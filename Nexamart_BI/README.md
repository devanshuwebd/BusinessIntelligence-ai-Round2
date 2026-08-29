# NexaMart BusinessIntelligence.ai prototype

This prototype demonstrates a governed KPI intelligence-to-action flow.

## Run

```text
python Nexamart_BI/run_pipeline.py
python -m pytest -q Nexamart_BI/tests
python -m compileall Nexamart_BI/backend Nexamart_BI/dashboard Nexamart_BI/src
uvicorn Nexamart_BI.backend.main:app --port 8000
streamlit run Nexamart_BI/dashboard/app.py
```

The pipeline calculates KPI values from the committed sources, aggregates each fact independently, writes freshness and evidence artifacts, and fails closed on invalid data. It never substitutes synthetic business values.

## Configuration

Set `NEXAMART_LLM_URL`, `NEXAMART_LLM_TOKEN`, `NEXAMART_LLM_MODEL`, `NEXAMART_API_TOKEN`, and the optional per-1K-token cost variables through environment variables or a secret manager. Never commit them. For production role authorization, configure `NEXAMART_ROLE_TOKENS` as a JSON object mapping `Executive` and `Analyst` to separate secret tokens. Set `NEXAMART_DATA_AS_OF=2026-08-15` only when replaying this static fixture as a historical demo; leave it unset to measure freshness against the current clock.

The API accepts only a persona and the server-generated `insight_id`. It reloads the persisted gold context, evidence, movement, confidence gate, policy matches, and feedback-calibration data on the server; caller-supplied KPI values are ignored. `/api/regional-snapshot` applies the role-to-region entitlement on the server. Actions are emitted only when the latest movement is material, confidence is `proceed`, and a policy document is available.

For local LLM narration, start the proxy separately with `python Nexamart_BI/llm_integration/nexamart_llm_proxy.py` after configuring a non-empty `NEXAMART_LLM_TOKEN`. In development, when `NEXAMART_LLM_URL` is empty and `NEXAMART_DEMO_MODE=1`, the API returns an explicitly labelled deterministic, evidence-only narrative with different Executive and Analyst wording; it never invents business values. Production defaults demo mode off.

The Executive and Analyst roles are simulated demo entitlements only. Replace them with platform identity and server-side row/column/domain controls before production.

## Scope boundary

Marketing and inventory are supporting signals. They are not labelled causal revenue drivers because the source data has no campaign-to-order attribution. The LLM only narrates deterministic, evidence-linked outputs.

See `docs/round2_demo.md` for the requirement-by-requirement demonstration checklist.
