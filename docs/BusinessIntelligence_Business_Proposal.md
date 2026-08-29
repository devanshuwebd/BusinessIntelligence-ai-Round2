# Business Proposal
## BusinessIntelligence.ai — Governed KPI Intelligence-to-Action Platform

**Prepared for:** NexaMart business, analytics, operations, and technology stakeholders  
**Proposal type:** Prototype-to-pilot business proposal  
**Current solution stage:** Round 2 working prototype  
**Decision requested:** Approve a controlled pilot and production-hardening workstream; do not treat the current prototype as production-ready until the stated controls are completed.

---

## 1. Executive summary

NexaMart has business information spread across sales, marketing, inventory, policy documents, and dashboard systems. The problem is not simply a lack of charts. The difficult work begins after a KPI moves: determining whether the movement is material, understanding which evidence supports it, knowing whether the source data is fresh and complete, deciding whether the explanation is causal or only a correlation, and converting the result into an action that the right person is allowed to take.

BusinessIntelligence.ai proposes a governed KPI intelligence-to-action platform that answers four questions:

1. What changed?
2. What evidence supports the movement?
3. How confident should the business be, and when should the system abstain?
4. What action is permitted, who owns it, and how will the outcome be monitored?

The current Round 2 prototype already demonstrates the central workflow using sales, inventory, and marketing sources. It calculates KPI values deterministically, detects material movement, decomposes revenue into volume, price/mix, and interaction effects, records freshness and lineage, handles sparse and contradictory evidence, retrieves policy documents, applies action gates, produces different Executive and Analyst narratives, captures feedback, and records runtime telemetry.

The recommended next step is a controlled pilot with real identity, durable storage, validated Databricks execution, and carefully selected users. The business case should be measured through time saved in investigation, reduction in unsupported explanations, faster decision cycles, user adoption, action follow-through, and cost per insight. No financial return percentage is claimed at this stage because a baseline and pilot measurement period have not yet been approved.

---

## 2. Problem framing

### 2.1 Business problem

Business users regularly see KPI changes without receiving a trustworthy explanation or a clear next step. Investigation is often manual:

- An analyst exports data from several systems.
- Different sources use different dates, grains, hierarchies, and refresh schedules.
- KPI definitions may differ between dashboards or teams.
- Data is joined before aggregation, creating duplicated facts.
- A marketing or inventory signal may be mistaken for a proven cause.
- Stale or missing source data may not be visible to the decision-maker.
- The final narrative may contain numbers that cannot be traced back to a query or source.
- Recommended actions may not respect business policy, ownership, or decision rights.

This creates three business risks:

1. **Slow decisions:** people spend time reconstructing what happened instead of acting.
2. **Low trust:** users cannot tell whether an insight is calculated, inferred, or invented.
3. **Unsafe action:** a plausible explanation can lead to a pricing, inventory, or marketing decision without sufficient evidence or authorization.

### 2.2 Why existing dashboards are not enough

A dashboard is good at displaying a measurement. It is not automatically good at explaining a movement or governing a decision. A reliable intelligence-to-action workflow needs a calculation contract, source metadata, analytical method, confidence gate, policy evidence, and ownership model around the visualization.

### 2.3 Problem statement

NexaMart needs a repeatable way to move from a material KPI movement to an evidence-bounded decision, while preserving the distinction between:

- facts calculated from source data;
- statistical or deterministic analytical signals;
- hypotheses that still require validation;
- policies that constrain action; and
- natural-language explanations generated for different users.

---

## 3. Proposed solution

BusinessIntelligence.ai is a governed decision-support layer placed between business data sources and business users.

### 3.1 Core workflow

~~~text
Sales, inventory, and marketing data
          |
          v
Schema and data-quality validation
          |
          v
Independent source aggregation at native grain
          |
          v
Deterministic KPI calculation
          |
          v
Materiality and driver analysis
          |
          v
Freshness, evidence, lineage, entitlement, and confidence gates
          |
          +--> weak, stale, sparse, or contradictory evidence
          |          -> abstain and show reasons
          |
          +--> sufficient evidence
                     |
                     v
             Retrieve relevant policy
                     |
                     v
              Apply action gate
                     |
                     v
          Persona-specific narrative and action view
                     |
                     v
              Feedback and telemetry
~~~

### 3.2 What the solution does

The solution:

- Calculates trusted KPI values from source data.
- Detects movements that are large enough to matter.
- Ranks measurable contributors using transparent analytical methods.
- Shows source freshness, row counts, lag, lineage, and evidence IDs.
- Abstains when history is sparse or evidence conflicts.
- Retrieves relevant policy documents before recommending actions.
- Gives concise decision summaries to Executives and deeper method/uncertainty detail to Analysts.
- Filters regional views on the server according to the user’s entitlement.
- Records feedback, latency, model calls, token usage, estimated cost, and status.

### 3.3 What the solution does not claim

The solution does not:

- Treat a language model as the source of numerical truth.
- Claim that marketing caused revenue movement without campaign-to-order attribution.
- Estimate financial impact without an experiment or validated model.
- Treat stale fixture data as real-time data.
- Automatically retrain itself merely because feedback was submitted.
- Replace a business owner’s decision authority.

---

## 4. Target users and use cases

### 4.1 Executive user

**Need:** A concise explanation of a material KPI movement and the decisions that require attention.

**Experience:**

- High-level KPI movement.
- Leading evidence-linked driver.
- Confidence status.
- Policy-gated actions.
- Owner and decision right.
- Monitoring plan.

**Example decision:** Decide whether a revenue movement requires a commercial, supply, or cross-functional review.

### 4.2 Analyst user

**Need:** Enough detail to validate the calculation, inspect source freshness, challenge the driver ranking, and investigate uncertainty.

**Experience:**

- KPI definitions and formulas.
- Source grain and freshness.
- Price-volume-mix decomposition.
- Supporting signals.
- Contradictions and abstention reasons.
- Regional and evidence detail.
- Feedback and evaluation controls.

**Example decision:** Determine whether a movement is consistent with volume, realised price, mix, inventory availability, or an unresolved data-quality issue.

### 4.3 Operations and supply-chain user

**Need:** Understand whether demand and availability signals justify an operational review.

**Example decision:** Review stockout hours, lead time, quantity, and order trends before changing replenishment or service actions.

### 4.4 Commercial and growth user

**Need:** Understand revenue, AOV, realised price, and marketing efficiency without confusing campaign correlation with attribution.

**Example decision:** Review pricing or product mix under the approved pricing policy, while treating marketing metrics as supporting evidence until attribution exists.

### 4.5 Governance and technology user

**Need:** Prove how each insight was calculated, which data was used, what policy was applied, who could see the result, and what the service cost.

---

## 5. Business case and expected impact

### 5.1 Value hypothesis

The platform is expected to create value in five areas. These are hypotheses to validate during a pilot, not guaranteed financial outcomes.

| Value area | Expected mechanism | Pilot measurement |
|---|---|---|
| Faster investigation | Automated KPI calculation and driver evidence reduce manual reconstruction | Median time from alert to validated explanation |
| Higher decision trust | Freshness, lineage, evidence IDs, and abstention make uncertainty visible | Unsupported-claim rate; user trust rating; evidence inspection rate |
| Faster action | Recommendations include owner, decision right, and monitoring plan | Time from validated insight to assigned action |
| Safer governance | Policy and entitlement gates prevent unapproved or untraceable recommendations | Policy-gate pass/fail rate; access-control test results |
| Controlled operating cost | Telemetry exposes model calls, tokens, latency, and estimated cost | Cost per insight; p95 latency; error and abstention rates |

### 5.2 Financial case approach

A financial ROI number should be calculated after a baseline is collected. The recommended model is:

~~~text
Annual value
= analyst investigation hours avoided × loaded hourly cost
+ value of faster decisions validated by the business
+ avoided cost of unsupported or unauthorized actions
- platform, storage, identity, model, and operating costs
~~~

The project should not claim a percentage return before the following are known:

- number of investigations per week;
- average current investigation time;
- analyst and decision-maker costs;
- number of material KPI movements;
- percentage of movements requiring manual escalation;
- model and infrastructure costs at expected volume;
- measurable business impact of faster or better decisions.

### 5.3 Adoption value

The solution is designed to improve adoption by showing its reasoning rather than presenting an unexplained answer. Users can see the KPI definition, source freshness, driver method, confidence gate, policy evidence, and monitoring plan in one workflow.

---

## 6. Current prototype implementation

### 6.1 Data sources

The working prototype uses three source domains with different grains:

| Source | Approximate rows | Native grain | Primary measures |
|---|---:|---|---|
| Sales | 154,140 | order/product/date | revenue, orders, quantity, AOV, realised price |
| Inventory | 56,825 | date/product/region | stock available, stockout hours, lead time |
| Marketing | 9,988 | date/campaign/channel | spend, impressions, clicks, conversions |

### 6.2 Deterministic analytics

The prototype calculates values through Python and SQL artifacts rather than hardcoding dashboard numbers.

Revenue driver analysis follows:

~~~text
Revenue = Quantity × Realised Price
~~~

The current implementation separates:

- volume effect;
- price/mix effect; and
- interaction effect.

The effects reconcile to the observed revenue movement. Marketing and inventory are supporting signals because campaign-to-order attribution is not available in the source data.

### 6.3 Governance and uncertainty

The prototype includes:

- a KPI contract with definitions, formulas, grain, sources, cadence, thresholds, history, and entitlement metadata;
- source freshness and lag metadata;
- evidence IDs and lineage;
- materiality scoring;
- stale-source and contradiction handling;
- sparse-history handling for product P999;
- a controlled contradictory-evidence scenario;
- fail-closed policy retrieval; and
- server-side insight context loading.

### 6.4 Actions

The action model follows:

~~~text
driver -> controllable lever -> action -> owner -> decision right -> confidence -> monitoring plan
~~~

Actions are suppressed unless the movement is material, the confidence gate is proceed, and relevant policy evidence has been retrieved successfully.

### 6.5 Personas and access

Executive and Analyst users receive different narrative depth. Regional snapshots are filtered server-side using prototype entitlement rules. These rules are suitable for demonstration, not a final production identity system.

### 6.6 Feedback and telemetry

The prototype persists feedback and reports correction/rating statistics. It also stores model calls, latency, token counts, estimated cost, status, and timestamps. This creates the measurement foundation for future calibration and cost control.

---

## 7. Implementation approach

### Principle 1: Calculate before explaining

All numerical facts, KPI calculations, baselines, movement scores, and decomposition values are produced deterministically before narrative generation.

### Principle 2: Preserve source meaning

Each source is validated and aggregated at its appropriate grain. Facts are not joined at raw grain when doing so would multiply rows.

### Principle 3: Make uncertainty visible

Freshness, missing evidence, sparse history, and contradictions are surfaced to users. The system abstains instead of hiding uncertainty.

### Principle 4: Separate correlation from causality

A supporting signal is not described as a cause unless attribution or causal inference supports that claim.

### Principle 5: Gate action, not just language

A fluent explanation is not enough to authorize a business action. Policy evidence, confidence, materiality, ownership, and decision rights are required.

### Principle 6: Measure the operating economics

Every narrative request should be measurable in latency, model calls, tokens, estimated cost, failure status, and user feedback.

### Principle 7: Improve through controlled feedback

Feedback is captured first, evaluated second, and only then considered for calibration or retraining. No automatic learning claim is made without measured validation.

---

## 8. Dependencies and prerequisites

### 8.1 Current software dependencies

The prototype uses Python 3.11 and the following packages:

- pandas for tabular data processing;
- numpy for numerical operations;
- pyarrow for Parquet output;
- requests for HTTP service calls;
- FastAPI and Uvicorn for the API;
- Pydantic for request validation;
- scikit-learn for the forecast utility;
- pypdf for policy PDF extraction;
- Streamlit for the dashboard; and
- pytest and httpx for tests.

### 8.2 Data prerequisites

A pilot requires:

- a defined owner for every KPI;
- stable source identifiers and source-to-KPI mappings;
- documented refresh schedules;
- valid business keys and grain definitions;
- a shared calendar and timezone convention;
- policy documents with owners and effective dates;
- attribution data if marketing causality is required; and
- data-quality monitoring for missing, delayed, duplicated, or invalid records.

### 8.3 Platform prerequisites

Production deployment requires:

- a supported identity provider;
- server-side row, column, and domain security;
- durable storage for insights, feedback, telemetry, and audit records;
- a managed secrets system;
- a validated Databricks or equivalent execution environment;
- model endpoint governance and budget controls;
- monitoring and alerting; and
- deployment, rollback, and retention procedures.

---

## 9. Execution and demonstration instructions

### 9.1 Local setup

~~~powershell
git clone https://github.com/devanshuwebd/BusinessIntelligence-ai.git
cd BusinessIntelligence-ai
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\Nexamart_BI\requirements.txt
~~~

If PowerShell blocks activation:

~~~powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
~~~

### 9.2 Run the pipeline

~~~powershell
python .\Nexamart_BI\run_pipeline.py
~~~

This validates the sources and writes the Silver and Gold artifacts.

For the historical material-movement demonstration:

~~~powershell
$env:NEXAMART_DATA_AS_OF="2026-07-15"
python .\Nexamart_BI\run_pipeline.py
~~~

### 9.3 Run tests

~~~powershell
python -m pytest -q .\Nexamart_BI\tests
python -m compileall .\Nexamart_BI\backend .\Nexamart_BI\dashboard .\Nexamart_BI\src
~~~

### 9.4 Start the API and dashboard

Terminal 1:

~~~powershell
python -m uvicorn Nexamart_BI.backend.main:app --host 127.0.0.1 --port 8000
~~~

Terminal 2:

~~~powershell
streamlit run .\Nexamart_BI\dashboard\app.py
~~~

Open:

- API health: http://127.0.0.1:8000/api/health
- API documentation: http://127.0.0.1:8000/docs
- Dashboard: http://localhost:8501

### 9.5 Docker

~~~powershell
docker build -t nexamart-bi .\Nexamart_BI
docker run --rm -p 8000:8000 -p 8501:8501 nexamart-bi
~~~

---

## 10. Phased roadmap

The durations below are planning estimates for sequencing, not fixed commitments.

### Phase 0 — Controlled prototype demonstration

**Objective:** Demonstrate the full evidence-to-action flow with the committed fixture.

**Activities:**

- Run the deterministic pipeline.
- Demonstrate material movement and historical replay.
- Show Executive and Analyst experiences.
- Show freshness, lineage, scenarios, policy evidence, feedback, and telemetry.
- Run automated tests and compilation.

**Exit criteria:**

- All Round 2 minimum prototype expectations demonstrated.
- No hardcoded quantitative truth in the runtime path.
- Abstention scenarios behave as documented.

**Outcome:** A reviewable, evidence-bounded prototype suitable for evaluation and stakeholder feedback.

### Phase 1 — Production security and platform foundation

**Objective:** Replace prototype controls with deployable platform controls.

**Activities:**

- Rotate and revoke credentials exposed in historical commits.
- Integrate identity provider and role mapping.
- Implement row-, column-, and domain-level controls.
- Move state from SQLite to durable shared storage.
- Add secret-manager integration.
- Add audit retention and access reviews.

**Exit criteria:**

- Access tests pass for each persona and domain.
- No secrets are stored in source or generated artifacts.
- State survives restart and multi-instance deployment.

**Outcome:** A secure foundation for a limited pilot.

### Phase 2 — Real data and Databricks validation

**Objective:** Validate the platform-native path against governed business data.

**Activities:**

- Execute the SQL artifacts in the real workspace.
- Compare Python and Databricks outputs against the same test fixture.
- Validate KPI contract grain and dimensions.
- Add source freshness and data-quality monitors.
- Establish ownership for KPI contracts and policy documents.

**Exit criteria:**

- KPI outputs reconcile across implementations.
- Data-quality failures are visible and actionable.
- Business owners approve KPI definitions and thresholds.

**Outcome:** A trustworthy pilot data foundation.

### Phase 3 — Controlled business pilot

**Objective:** Measure user value with a small group of Executive, Analyst, Operations, and Commercial users.

**Activities:**

- Select a limited KPI and business domain scope.
- Establish baseline investigation times.
- Track insight acceptance, challenge, abstention, and action follow-through.
- Collect structured user feedback.
- Measure cost and latency under realistic usage.

**Exit criteria:**

- Pilot users can validate evidence without reconstructing the entire analysis.
- Unsupported narrative rate remains within an agreed tolerance.
- Action ownership and monitoring are completed for accepted insights.
- Measured value supports expansion or a redesign decision.

**Outcome:** Evidence for whether the platform creates sufficient business value to scale.

### Phase 4 — Stronger attribution and analytical depth

**Objective:** Expand beyond descriptive contribution analysis where the data supports it.

**Activities:**

- Add campaign-to-order attribution.
- Add forecasting and calibrated anomaly detection.
- Add causal inference or controlled experiments for selected levers.
- Add external-event and competition signals with source provenance.
- Expand product, category, market, and region hierarchies.

**Exit criteria:**

- Causal claims are supported by approved methods.
- Model performance and calibration are monitored.
- New signals have owners, freshness rules, and access policies.

**Outcome:** More powerful explanations without weakening evidence standards.

### Phase 5 — Learning loop and scale

**Objective:** Make the platform improve from validated business feedback and operate economically at scale.

**Activities:**

- Define feedback labels and review queues.
- Calibrate driver rankings using measured feedback.
- Add model and data drift monitoring.
- Add caching, model routing, rate limits, and budget controls.
- Add deployment automation, rollback, and incident procedures.
- Expand delivery channels after access and content review.

**Exit criteria:**

- Feedback changes are measured before release.
- Cost, latency, error, abstention, and drift targets are monitored.
- Production operating procedures are accepted by technology and business owners.

**Outcome:** A scalable governed decision-support capability.

---

## 11. Key risks and mitigations

| Risk | Business impact | Mitigation | Owner |
|---|---|---|---|
| Incorrect KPI definition | Teams act on the wrong number | Versioned KPI contract, named owner, approval workflow, reconciliation tests | Analytics owner |
| Many-to-many or grain errors | Inflated revenue, order, or inventory results | Native-grain aggregation, key validation, no unapproved fact joins | Data engineering |
| Stale or missing source data | False confidence and delayed decisions | Freshness metadata, availability flags, stale-source abstention | Data platform |
| Sparse history for new products | Unstable driver rankings | Minimum-history gate, abstention, separate launch KPI treatment | Analytics owner |
| Contradictory evidence | Wrong explanation or action | Contradiction detection, alternative hypotheses, clarification workflow | Analytics and business owner |
| Unsupported causal claims | Misallocated marketing or supply decisions | Label supporting signals correctly; add attribution before causal claims | Growth/analytics |
| Language-model hallucination | False narratives or reputational harm | Server-loaded context, citation validation, no-calculation prompt, fail-closed errors | Technology owner |
| Exposed credentials or weak entitlements | Data leakage or unauthorized action | Credential rotation, identity provider, server-side row/column/domain controls | Security |
| Policy retrieval failure | Unapproved recommendation | Fail-closed policy gate and policy version/effective-date checks | Governance |
| Low user adoption | Investment does not create value | Persona-specific views, evidence transparency, pilot feedback, user training | Product owner |
| Model cost or latency growth | Poor user experience and unsustainable operating cost | Telemetry, caching, routing, token budgets, p95 monitoring | Platform engineering |
| Feedback bias | System learns from incomplete or unrepresentative corrections | Expert review queue, feedback sampling, measured calibration releases | Analytics governance |
| Databricks/Python mismatch | Inconsistent results across environments | Shared contract, common fixtures, cross-implementation acceptance tests | Data engineering |
| Historical secret exposure | Repository remains unsafe despite code cleanup | Revoke/rotate secrets and review Git history; do not rely only on deleting current files | Security |
| Overreliance on recommendations | Business judgment is replaced by automation | Keep decision rights explicit; require human approval for consequential actions | Business owners |

---

## 12. Operating model and responsibilities

### Business owners

- Approve KPI definitions and materiality thresholds.
- Approve action levers and decision rights.
- Validate policy documents and effective dates.
- Review accepted and rejected insights.

### Analytics and data engineering

- Own source mappings, aggregation logic, quality checks, and analytical methods.
- Maintain the KPI contract and reconciliation tests.
- Investigate drift and data-quality failures.

### Product and operations

- Own user workflows, persona needs, adoption, and action follow-through.
- Define what constitutes a useful insight.
- Monitor whether recommendations lead to completed decisions.

### Technology and security

- Own identity, secrets, network controls, deployment, durable storage, observability, and incident response.
- Enforce server-side entitlements and auditability.
- Maintain model budgets and runtime reliability.

### Governance

- Review causal claims, sensitive data, policy usage, feedback, and release criteria.
- Ensure the system abstains when evidence is not adequate.

---

## 13. Success metrics and pilot scorecard

The pilot should establish a baseline before judging success.

### Efficiency

- Median time from KPI alert to validated explanation.
- Analyst hours spent per investigation.
- Percentage of investigations completed without manual data reconstruction.

### Quality and trust

- KPI reconciliation failure rate.
- Unsupported numerical-claim rate.
- Unsupported causal-claim rate.
- Evidence citation validity rate.
- Abstention precision: whether abstentions occur in genuinely weak cases.
- User rating of explanation usefulness and trustworthiness.

### Actionability

- Percentage of accepted insights with an owner.
- Time from validated insight to assigned action.
- Action completion rate.
- Monitoring-plan completion rate.

### Operations and economics

- p50 and p95 API latency.
- Model calls per insight.
- Tokens per insight.
- Estimated cost per insight.
- Error rate.
- Freshness SLA compliance.
- Access-control test pass rate.

---

## 14. Decision request

Approve the following:

1. Use the current system as a Round 2 demonstration prototype and controlled evaluation artifact.
2. Proceed with Phase 1 security and durable-storage hardening before connecting sensitive production data.
3. Select a small pilot group covering Executive, Analyst, and at least one operational user.
4. Establish baseline measures before making ROI claims.
5. Require explicit approval for causal marketing claims, automated actions, and production deployment.
6. Review pilot results against the success scorecard before scaling.

Do not approve the current prototype for unrestricted production use until identity, secrets, durable storage, Databricks execution, and operational monitoring are completed.

---

## 15. Final recommendation

Proceed with a controlled pilot because the prototype has demonstrated the most important architectural behavior: it calculates before explaining, preserves source context, exposes uncertainty, gates actions with policy, differentiates user personas, and measures runtime behavior.

The recommended investment is not simply an investment in a narrative interface. It is an investment in a governed chain from business data to a decision that can be inspected, challenged, approved, and monitored.

The platform should scale only when it continues to meet this standard:

> Every important explanation must be traceable to evidence, every uncertainty must be visible, and every recommended action must have a valid owner and decision right.
