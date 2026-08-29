# BusinessIntelligence.ai

## Project overview

BusinessIntelligence.ai is a governed KPI intelligence-to-action prototype for NexaMart. It converts multiple business data sources into trusted KPI measurements, identifies material movements, ranks measurable drivers, checks evidence quality, retrieves applicable policies, and produces persona-specific explanations and actions.

The system is deliberately designed so that quantitative truth comes from deterministic data processing and analytical rules. The optional narrative service only converts approved evidence into readable language; it does not calculate KPI values, invent evidence, or make unsupported causal claims.

## Round 2 objectives covered

The prototype demonstrates:

- Material KPI movement detection and prioritisation.
- Reconciliation of sales, inventory, and marketing sources with different grains.
- Deterministic driver analysis using price-volume-mix decomposition.
- Executive and Analyst narrative variants.
- Confidence scoring, contradictory-evidence handling, stale-source handling, and abstention.
- Policy-constrained action recommendations.
- Feedback capture and calibration reporting.
- Role and regional entitlement handling.
- Source freshness, evidence IDs, lineage, latency, model-call, token, and cost telemetry.

## Solution architecture

~~~text
Raw CSV sources
    |
    v
Schema, type, null, and key validation
    |
    v
Source-specific clean data at native grain
    |
    v
Independent daily aggregation
    |
    v
Deterministic KPI calculations
    |
    v
Materiality and driver analysis
    |
    v
Freshness, lineage, evidence, and confidence gates
    |
    +--> insufficient or contradictory evidence -> abstain with reasons
    |
    +--> sufficient evidence -> retrieve policy and apply action gates
                                                    |
                                                    v
                                    persona-specific narrative rendering
                                                    |
                                                    v
                                      feedback and runtime telemetry
~~~

### Processing responsibilities

| Layer | Responsibility | Main implementation |
|---|---|---|
| Bronze | Committed source fixtures | bronze_layer/raw |
| Validation | Schema, data types, nulls, and key checks | src/kpi_engine/pipeline_v2.py |
| Silver | Clean source outputs at native grain | silver_layer/Cleaning.py and run_pipeline.py |
| Gold | KPI, movement, driver, contract, and action artifacts | gold_layer and run_pipeline.py |
| Governance | Freshness, confidence, evidence, lineage, entitlements, and policy gates | backend/main.py and pipeline_v2.py |
| Narrative | Optional evidence-bounded text rendering | backend/main.py and src/llm |
| Presentation | Executive/Analyst dashboard | dashboard/app.py |
| Operations | Tests, CI, feedback, and telemetry | tests, .github/workflows/ci.yml, backend/main.py |

## Source data and grains

| Source | Approximate rows | Native grain | Used for |
|---|---:|---|---|
| sales.csv | 154,140 | order/product/date | revenue, orders, quantity, AOV, realised price |
| inventory.csv | 56,825 | date/product/region | stock available, stockout hours, lead time |
| marketing.csv | 9,988 | date/campaign/channel | spend, impressions, clicks, conversions, efficiency |
| products.csv | small dimension | product | product and category validation |

The fixture covers dates through 15 August 2026. Source freshness is therefore important when running the project after that date.

The sources are never joined together at raw fact grain. Each is aggregated independently before being reconciled at daily grain. The customer source is not joined to sales because sales has no customer_id key; joining by customer_segment would multiply facts and produce incorrect KPI totals.

## KPIs and analytical methods

### Sales KPIs

- Total Revenue = sum of completed sales revenue.
- Total Orders = count of distinct order IDs.
- Total Quantity = sum of sold quantity.
- Average Order Value = revenue divided by distinct orders.
- Realised Price = revenue divided by quantity.

### Marketing KPIs

- Marketing Spend.
- Impressions.
- Clicks.
- Conversions.
- Click-to-conversion rate = conversions divided by clicks.

Marketing is treated as a supporting signal. Campaign-to-order attribution is not present in the fixture, so the system does not claim that marketing caused a revenue movement.

### Inventory KPIs

- Average stock available.
- Total stockout hours.
- Average lead time.

### Materiality

A movement is prioritised using percentage movement, absolute business impact, rolling baseline variation, and a z-score signal. A movement must satisfy the configured gates before it can drive an action.

### Price-volume-mix decomposition

Revenue is decomposed as:

~~~text
Revenue = Quantity × Realised Price

Volume effect      = (current quantity - previous quantity) × previous price
Price/mix effect   = (current price - previous price) × previous quantity
Interaction effect = (current quantity - previous quantity) × (current price - previous price)
~~~

The effects reconcile to the observed revenue change. Marketing and inventory remain observational supporting signals unless validated attribution or causal analysis is added.

## KPI contract

The semantic contract in gold_layer/kpi_semantic_layer.sql records the governance metadata needed to interpret each KPI:

- KPI identifier and name.
- Definition and calculation formula.
- Grain and supported dimensions.
- Source tables and columns.
- Refresh cadence, timezone, and currency.
- Owner role.
- Sensitivity classification.
- Entitlement policy.
- Percentage and absolute materiality thresholds.
- Minimum history days.
- Contract version.

The contract is intended to prevent a dashboard, SQL view, or narrative service from using an ambiguous KPI definition.

## Evidence and confidence

Each persisted insight includes an insight ID, source metadata, snapshot, movement, drivers, supporting signals, confidence, lineage, action gate, policy evidence, and low-confidence scenarios.

The engine can abstain for:

- Sparse history below the minimum history threshold.
- Stale source data.
- Contradictory evidence.
- Missing server-side context.
- Failed policy retrieval.
- Missing or untraceable model evidence.

The P999 product is the sparse-history demonstration. A controlled scenario demonstrates revenue decline alongside strong demand growth, which triggers contradictory-evidence abstention.

## Action recommendation model

Actions follow this structure:

~~~text
driver -> controllable lever -> action -> owner -> decision right -> confidence -> monitoring plan
~~~

An action is emitted only when:

1. The KPI movement is material.
2. The confidence gate is proceed.
3. Matching policy evidence was retrieved successfully.

Expected impact is not fabricated. It is left unknown unless an experiment or validated model supports an estimate.

## Narrative service boundary

The optional narrative service receives server-loaded evidence after deterministic processing. It is instructed to:

- Use only supplied values.
- Avoid new calculations.
- Avoid unsupported causality.
- Cite only supplied evidence IDs.
- Use concise decision language for Executive users.
- Include method and uncertainty detail for Analyst users.

When no narrative endpoint is configured in development, demo mode provides deterministic evidence-only wording. In production, demo mode defaults off and an unconfigured service returns an explicit error.

## Dashboard

The Streamlit dashboard provides:

- KPI cards and trend charts.
- Driver and supporting-signal evidence.
- Source freshness.
- Confidence score and abstention reasons.
- Sparse-history and contradiction demonstrations.
- Server-filtered regional data.
- Policy-constrained actions.
- Executive and Analyst narrative variants.
- Feedback submission.
- Runtime telemetry returned by the API.

The Databricks dashboard contains separate Executive View and Analyst View pages for the platform demonstration.

## API

The FastAPI service is implemented in backend/main.py.

| Method and route | Purpose |
|---|---|
| GET /api/health | Service and configuration health |
| POST /api/generate-insight | Evidence-grounded persona narrative |
| GET /api/regional-snapshot | Server-filtered regional snapshot |
| POST /api/log-feedback | Persist user feedback |
| GET /api/feedback/evaluation | Feedback calibration summary |
| GET /api/telemetry/latest | Recent runtime telemetry |

The client sends a persona and server-generated insight_id. KPI values and evidence are reloaded by the server, so the browser cannot replace the quantitative context.

## Dependencies

The project uses Python 3.11 and the dependencies in Nexamart_BI/requirements.txt:

- pandas for tabular processing.
- numpy for numerical operations.
- pyarrow for Parquet output.
- requests for service calls.
- FastAPI and Uvicorn for the API.
- Pydantic for request validation.
- scikit-learn for the forecast utility.
- pypdf for policy PDF text extraction.
- Streamlit for the dashboard.
- pytest and httpx for automated tests.

## Local execution

### Windows PowerShell setup

~~~powershell
git clone https://github.com/devanshuwebd/BusinessIntelligence-ai.git
cd BusinessIntelligence-ai
git checkout main
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\Nexamart_BI\requirements.txt
~~~

If script execution is restricted for the current PowerShell session:

~~~powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
~~~

### Run the pipeline

~~~powershell
python .\Nexamart_BI\run_pipeline.py
~~~

The command validates the inputs and writes generated artifacts to Nexamart_BI/gold_layer and Nexamart_BI/silver_layer.

For the historical material-movement demonstration:

~~~powershell
$env:NEXAMART_DATA_AS_OF="2026-07-15"
python .\Nexamart_BI\run_pipeline.py
~~~

Use the historical as-of date only for the replay. It is not a live-data configuration.

### Run tests and compilation

~~~powershell
python -m pytest -q .\Nexamart_BI\tests
python -m compileall .\Nexamart_BI\backend .\Nexamart_BI\dashboard .\Nexamart_BI\src
~~~

### Start the API

~~~powershell
python -m uvicorn Nexamart_BI.backend.main:app --host 127.0.0.1 --port 8000
~~~

Check the service at:

- http://127.0.0.1:8000/api/health
- http://127.0.0.1:8000/docs

### Start the dashboard

Open a second terminal while the API is running:

~~~powershell
streamlit run .\Nexamart_BI\dashboard\app.py
~~~

Open http://localhost:8501.

### Generate a test narrative

First read the generated insight ID from Nexamart_BI/gold_layer/insight_context.json. Then submit:

~~~powershell
$context = Get-Content .\Nexamart_BI\gold_layer\insight_context.json | ConvertFrom-Json
$body = @{ persona = "Executive"; insight_id = $context.insight_id } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/generate-insight -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 10
~~~

Change Executive to Analyst to compare persona-specific wording.

### Docker execution

~~~powershell
docker build -t nexamart-bi .\Nexamart_BI
docker run --rm -p 8000:8000 -p 8501:8501 nexamart-bi
~~~

Open:

- API health: http://localhost:8000/api/health
- API documentation: http://localhost:8000/docs
- Dashboard: http://localhost:8501

## Verification checklist

A successful Round 2 demonstration should show:

- Five KPI fields derived from the source files.
- Independent aggregation before daily reconciliation.
- No invalid customer-segment join.
- Latest available source date and per-source freshness.
- Deterministic materiality and price-volume-mix decomposition.
- P999 sparse-history abstention.
- Stale or contradictory-evidence abstention.
- Different Executive and Analyst narrative depth.
- Server-side regional entitlement filtering.
- Feedback persistence and calibration output.
- Runtime telemetry for latency, model calls, tokens, cost, and status.
- Actions suppressed when materiality, confidence, or policy gates fail.
- Explicit failure behavior when the optional narrative service is unavailable.

## Project structure

~~~text
.
├── .github/workflows/ci.yml
├── Nexamart_BI/
│   ├── backend/main.py
│   ├── dashboard/app.py
│   ├── bronze_layer/raw/
│   ├── silver_layer/Cleaning.py
│   ├── gold_layer/
│   ├── llm_integration/
│   ├── src/kpi_engine/
│   ├── src/llm/
│   ├── src/recommendations/
│   ├── tests/
│   ├── run_pipeline.py
│   ├── run_full_system.py
│   ├── requirements.txt
│   └── docs/round2_demo.md
└── README.md
~~~

## Security and production limitations

This is a prototype. Before production use:

- Rotate and revoke credentials that appeared in historical commits.
- Replace demo tokens and region maps with an identity provider and server-enforced row, column, and domain controls.
- Replace SQLite with durable shared storage.
- Execute and compare the Databricks SQL artifacts in the actual workspace.
- Add campaign-to-order attribution before causal marketing claims.
- Define a measured feedback retraining or recalibration loop.
- Add rate limiting, model budgets, caching, drift monitoring, deployment controls, and audit retention.

## License and contribution

Add the project’s chosen license and contribution policy before public distribution. Keep source definitions, tests, policy documents, and evidence boundaries synchronized when changing the calculation logic.
