# BusinessIntelligence.ai
## Pitch Presentation & Working Prototype Video Playbook

### Purpose

This guide explains exactly what to open, what to show, and what to say while recording the pitch presentation and working-prototype demonstration.

The presentation should prove two things:

1. The proposal solves a real business decision problem.
2. The prototype demonstrates the core mechanism from data to evidence, confidence, policy, action, and outcome.

### Recommended recording length

- Presentation slides: approximately 3 minutes 30 seconds.
- Working prototype demonstration: approximately 1 minute 30 seconds.
- Closing: approximately 20 seconds.
- Recommended total: 5–6 minutes.

Do not spend the entire video reading slide text. Use the slides as visual support and focus on the decision story.

---

## 1. Files and browser windows to prepare

Before recording, keep these items ready:

1. Final PowerPoint:
   `BusinessIntelligence.ai_Business_Proposal_Final_Readable.pptx`
2. The project repository:
   `C:\Users\devan\BusinessIntelligence-ai`
3. The live Databricks dashboard:
   `NexaMart Executive & Analyst Dashboard`
4. Optional local API page:
   `http://127.0.0.1:8000/docs`
5. Optional local dashboard page:
   `http://localhost:8501`

Use the final readable PowerPoint for recording. Slides 1, 2, 11, and 12 are the protected original slides. Slides 3–10 contain the updated proposal content.

### Recommended window order

- Window 1: PowerPoint in Slide Show mode.
- Window 2: Databricks dashboard for the working-prototype section.
- Window 3: Terminal, prepared but hidden until needed as a fallback.

Close unrelated tabs, notifications, email, passwords, API keys, and personal information before recording.

---

## 2. Before recording: verify the prototype

If you are using the live Databricks dashboard, confirm that it loads before recording.

If you are running locally, open PowerShell in the repository folder and run:

~~~powershell
cd C:\Users\devan\BusinessIntelligence-ai
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\Nexamart_BI\requirements.txt
python .\Nexamart_BI\run_pipeline.py
~~~

For the historical demonstration that produces a material movement:

~~~powershell
$env:NEXAMART_DATA_AS_OF="2026-07-15"
python .\Nexamart_BI\run_pipeline.py
~~~

The pipeline should generate outputs in:

~~~text
Nexamart_BI\gold_layer\
Nexamart_BI\silver_layer\
~~~

Check the API:

~~~powershell
python -m uvicorn Nexamart_BI.backend.main:app --host 127.0.0.1 --port 8000
~~~

Open:

~~~text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/docs
~~~

Start the local dashboard in a second terminal:

~~~powershell
streamlit run .\Nexamart_BI\dashboard\app.py
~~~

Open:

~~~text
http://localhost:8501
~~~

### Expected health response

The API should return a response containing:

~~~json
{
  "status": "ok",
  "server_context": true,
  "demo_mode": true
}
~~~

Do not restart the pipeline repeatedly during recording unless you need to refresh the generated context.

---

## 3. Presentation talk track

### Slide 1 — Title page

**Time:** 0:00–0:08  
**Action:** Keep the original title slide visible.

**Say:**

> “Hello everyone. We are presenting BusinessIntelligence.ai, a governed KPI intelligence-to-action solution for NexaMart. Our focus is moving business intelligence from reporting to reliable decision support.”

Do not change this slide.

---

### Slide 2 — Team details

**Time:** 0:08–0:15  
**Action:** Keep the original team slide visible.

**Say:**

> “I am Devanshu Chotiya, Team Leader from IIT (ISM) Dhanbad, presenting Team VisionCraft.”

Do not change this slide.

---

### Slide 3 — Problem framing

**Time:** 0:15–0:40  
**Action:** Show the three challenge boxes and the decision-layer flow.

**Say:**

> “The business problem is not that organizations lack dashboards. The problem starts when a KPI moves. Teams still have to manually connect revenue, orders, inventory, and marketing signals. They often cannot see whether the evidence is fresh or contradictory, and dashboards rarely identify an approved next action. Our missing layer connects KPI change to evidence, confidence, decision, recommendation, and outcome.”

**Point to:**

- Slow decisions.
- No confidence awareness.
- Limited actionability.
- KPI change to outcome flow.

**Key message:**

> “A movement should not automatically become a confident explanation or an action.”

---

### Slide 4 — Solution design

**Time:** 0:40–1:05  
**Action:** Follow the five-box flow from left to right.

**Say:**

> “BusinessIntelligence.ai first reads business data and calculates deterministic KPIs. It then produces driver evidence and confidence checks, retrieves the relevant policy, and applies an action gate. Only after those controls does it deliver a persona-specific narrative. Executives receive a concise decision summary, while Analysts can inspect the method, evidence, freshness, and uncertainty.”

**Point to:**

1. Business data.
2. Deterministic KPIs.
3. Evidence and confidence.
4. Policy and action gate.
5. Narrative delivery.

**Important sentence:**

> “Calculations and governance happen before narrative generation.”

---

### Slide 5 — Business case and impact

**Time:** 1:05–1:30  
**Action:** Point to the impact cards, then the pilot scorecard.

**Say:**

> “The expected value has five dimensions: faster investigation, better decision quality, explainability, continuous improvement, and controlled operating economics. We are not claiming an invented ROI percentage. Instead, the pilot will measure investigation time, evidence trust, action completion, latency, model usage, and cost per insight.”

**Point to:**

- Faster decisions.
- Better decision quality.
- Explainable and traceable results.
- Feedback and evaluation.
- Telemetry and cost control.

**If asked about ROI:**

> “A financial ROI number requires a baseline from real business usage. The prototype defines the scorecard needed to calculate it honestly.”

---

### Slide 6 — Target users

**Time:** 1:30–1:45  
**Action:** Move across the four role cards.

**Say:**

> “The system supports four groups. Executives need a decision-ready summary. Analysts need detailed evidence and methods. Marketing and Operations need business levers and supporting signals. Data and Analytics teams govern definitions, quality, lineage, feedback, and extension points. The important principle is the same governed evidence with different depth and access.”

**Key message:**

> “Same truth, different depth, governed access, and explicit ownership.”

---

### Slide 7 — How the system works

**Time:** 1:45–2:10  
**Action:** Trace the Bronze, Silver, Gold flow and then the confidence/action flow.

**Say:**

> “The data foundation keeps source meaning intact. Sales, inventory, and marketing are validated at their native grains. They are aggregated independently before being reconciled at daily grain. The Gold layer produces KPI and evidence artifacts. The decision layer then checks evidence, confidence, and policy. If evidence is weak, stale, sparse, or contradictory, the system abstains instead of guessing.”

**Explain the three governance controls:**

- KPI Semantic Contract: defines the metric.
- Data Freshness Registry: shows whether the source is current.
- Role Entitlements: control what each user can see.

---

### Slide 8 — Roadmap

**Time:** 2:10–2:30  
**Action:** Show the four stages from left to right.

**Say:**

> “The prototype stage is complete. The next step is a controlled business pilot with realistic scenarios, a small user cohort, baseline measurements, feedback evaluation, and cost and latency targets. Productionization adds automated ingestion, real identity, durable storage, Databricks validation, monitoring, and audit. Continuous intelligence adds stronger attribution, confidence calibration, measured learning, and outcome-based improvement.”

**Key message:**

> “We scale only after evidence, identity, and operating controls are ready.”

---

### Slide 9 — Risks and mitigations

**Time:** 2:30–2:50  
**Action:** Show the risk/mitigation table.

**Say:**

> “The major risks are addressed inside the pipeline. KPI definition and grain errors are controlled through contracts and reconciliation. Stale, missing, or sparse data triggers freshness and confidence gates. Correlation is not called causation without attribution. Untraceable narratives are blocked by server-loaded context and evidence-ID validation. Access, cost, latency, and adoption are managed through identity, telemetry, budgets, caching, and pilot measurement.”

**Closing line for this slide:**

> “If evidence, policy, or authorization is not sufficient, the system does not recommend an action.”

---

### Slide 10 — Prototype validation

**Time:** 2:50–3:15  
**Action:** Show the source-volume bars and validation checklist.

**Say:**

> “The working prototype processes three source domains: 154,140 sales records, 56,825 inventory records, and 9,988 marketing records. The validation demonstrates reconciliation, price-volume-mix decomposition, sparse-history abstention for P999, contradictory-evidence abstention, policy-gated actions, persona-specific narratives, and automated testing.”

**Point to the five checks:**

1. Revenue and order totals reconcile.
2. Driver effects reconcile to movement.
3. P999 sparse-history case abstains.
4. Contradictory evidence abstains.
5. Policy gates suppress unsupported actions.

**Say:**

> “This proves the core mechanism works as a governed prototype. The remaining production gates are identity, durable storage, attribution, and full platform validation.”

---

## 4. Working prototype demonstration

After Slide 10, switch from PowerPoint to the Databricks dashboard or local dashboard.

### Demo opening sentence

> “I will now show the same flow operating in the prototype: calculated KPI, evidence, confidence, policy, persona, and feedback.”

### Step 1 — Open the Executive View

Show the dashboard’s Executive View first.

Say:

> “The Executive view is designed for fast decision-making. It shows the KPI movement, the leading evidence, confidence status, and the available policy-gated action.”

Point to:

- Revenue movement.
- Orders and AOV.
- Stockout or availability signal.
- Confidence score/status.
- Source freshness or latest available source date.
- Action area, if the action gate passes.

Do not call inventory or marketing a confirmed cause. Say “supporting signal” unless attribution is shown.

### Step 2 — Open the Analyst View

Switch to the Analyst View.

Say:

> “The Analyst view exposes how the result was produced. It shows driver decomposition, source freshness, supporting signals, evidence IDs, confidence reasons, and the lineage needed to challenge the result.”

Point to:

- Volume effect.
- Price/mix effect.
- Interaction effect.
- Source freshness.
- Confidence score and reasons.
- Lineage or evidence section.

Explain the arithmetic briefly:

> “Revenue is calculated as quantity multiplied by realised price. The volume, price/mix, and interaction effects reconcile to the observed movement.”

### Step 3 — Demonstrate abstention

If the dashboard displays the required scenarios, open the low-confidence or scenario section.

Show:

- P999 sparse-history scenario.
- Contradictory-evidence scenario.

Say:

> “This is a key safety behavior. For a product with sparse history, or when strong signals conflict, the system abstains and shows the reason. It does not force a confident explanation.”

If the live dashboard does not expose the scenarios directly, do not invent a click path. Show Slide 10 and say:

> “These cases were executed and verified in the acceptance tests and are included in the generated insight context.”

### Step 4 — Demonstrate persona difference

Generate or show the narrative for Executive first, then Analyst.

Say:

> “The Executive narrative is concise and decision-focused. The Analyst narrative provides more method and uncertainty detail. Both use the same server-loaded evidence; the wording changes, not the underlying quantitative truth.”

### Step 5 — Demonstrate feedback and telemetry, if time allows

Show feedback controls or the telemetry section.

Say:

> “Feedback is persisted against the insight and evidence version for later calibration. Runtime telemetry records latency, model calls, token usage, estimated cost, and status. This prototype captures the learning signal; automatic retraining is a future controlled phase.”

Keep this section short if the recording has a strict time limit.

---

## 5. Local fallback demonstration

If the Databricks dashboard is unavailable during recording, use the local application.

### Start the local dashboard

~~~powershell
cd C:\Users\devan\BusinessIntelligence-ai
.\.venv\Scripts\Activate.ps1
$env:NEXAMART_DATA_AS_OF="2026-07-15"
python .\Nexamart_BI\run_pipeline.py
streamlit run .\Nexamart_BI\dashboard\app.py
~~~

Open:

~~~text
http://localhost:8501
~~~

### Check the API

In a second terminal:

~~~powershell
cd C:\Users\devan\BusinessIntelligence-ai
.\.venv\Scripts\Activate.ps1
python -m uvicorn Nexamart_BI.backend.main:app --host 127.0.0.1 --port 8000
~~~

Open:

~~~text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/docs
~~~

### Test a narrative from PowerShell

~~~powershell
$context = Get-Content .\Nexamart_BI\gold_layer\insight_context.json | ConvertFrom-Json
$body = @{ persona = "Executive"; insight_id = $context.insight_id } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/generate-insight -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 10
~~~

Change Executive to Analyst to compare the two personas.

---

## 6. Closing slides

### Slide 11 — Video

**Time:** 3:15–3:20 or after the live demo  
**Action:** Return to the original Video slide.

**Say:**

> “The working prototype demonstration shows the core mechanism operating end-to-end. The full pitch video and supporting project materials are available through the provided video link.”

Do not change this slide.

### Slide 12 — Thank you

**Time:** Final 10–20 seconds  
**Action:** Show the original Thank You slide.

**Say:**

> “In summary, BusinessIntelligence.ai connects KPI change to evidence, confidence, policy, action, and measurable outcome. It is designed to explain when the business should act and when the system should wait for better evidence. Thank you.”

Do not change this slide.

---

## 7. Complete short script

Use this version if you need one continuous script:

> “BusinessIntelligence.ai is a governed KPI intelligence-to-action solution for NexaMart. Businesses often see that a KPI moved, but still need to manually connect sales, inventory, marketing, and policy information to understand why and what to do. Our solution first validates and aggregates each source independently, calculates KPIs deterministically, detects material movement, and decomposes revenue into volume, price/mix, and interaction effects. It then checks source freshness, evidence strength, contradictions, history, entitlements, and policy before producing an action or narrative. If evidence is weak or contradictory, it abstains instead of guessing. Executives receive a concise decision summary, while Analysts receive method, evidence, freshness, and uncertainty detail. The prototype processes sales, inventory, and marketing data, demonstrates reconciliation, sparse-history abstention, contradictory-evidence abstention, policy-gated actions, feedback capture, and runtime telemetry. Our roadmap moves from this working prototype to a controlled pilot, production identity and durable storage, stronger attribution, and finally measured continuous intelligence. The core principle is simple: deterministic processing calculates the truth, governance decides whether it is reliable, and the narrative layer communicates the result.”

---

## 8. What to say and what not to say

### Use these phrases

- “Latest available source date.”
- “Evidence-linked driver.”
- “Supporting signal.”
- “Policy-gated action.”
- “Confidence gate.”
- “The system abstains when evidence is insufficient.”
- “Prototype entitlement.”
- “Feedback is captured for calibration.”

### Avoid these phrases

- “The model knows the exact cause.”
- “Marketing caused the revenue change.”
- “The system is production-ready.”
- “The system automatically learns from every feedback entry.”
- “The recommendation will increase revenue by a guaranteed percentage.”
- “The data is real-time” when the fixture is stale.
- “The language model calculated the KPI.”

### If asked why the system abstains

> “Because a trustworthy system must know when not to make a claim. Sparse history, stale sources, missing evidence, and contradictions are decision risks, so the engine exposes the reason and waits for better evidence.”

### If asked whether the solution uses a language model

> “Yes, optionally for persona-specific narrative rendering. It receives server-generated evidence after deterministic calculations and governance checks. It cannot replace the KPI values, calculate new business numbers, or cite evidence that was not supplied.”

### If asked whether the system is production-ready

> “It is a working Round 2 prototype. Production hardening still requires real identity, credential rotation, durable storage, validated Databricks execution, attribution, monitoring, and a measured feedback-learning loop.”

### If asked how it learns

> “The prototype captures feedback and calculates calibration signals such as correction rate. Automatic retraining or recalibration is planned only after enough validated feedback is collected and measured.”

### If asked about the stale fixture

> “The fixture’s latest available source date is shown explicitly. If it is stale relative to the current date, the system can abstain rather than presenting old data as real-time. A historical as-of replay is used for the material-movement demonstration.”

---

## 9. Final recording checklist

### Presentation

- [ ] Use `BusinessIntelligence.ai_Business_Proposal_Final_Readable.pptx`.
- [ ] Confirm slides 1, 2, 11, and 12 are unchanged.
- [ ] Start in Slide Show mode.
- [ ] Keep the pointer on the relevant chart, table, or flow.
- [ ] Do not read every bullet word-for-word.
- [ ] Keep the proposal section near 3–4 minutes.

### Prototype

- [ ] Databricks or local dashboard loads before recording.
- [ ] Executive View is shown first.
- [ ] Analyst View is shown second.
- [ ] KPI movement, evidence, freshness, confidence, and action gate are visible.
- [ ] Sparse-history and contradiction behavior is explained.
- [ ] Executive and Analyst narratives are compared.
- [ ] Feedback/telemetry is shown only if time permits.

### Accuracy and safety

- [ ] Do not claim unsupported causality.
- [ ] Do not invent ROI or expected impact.
- [ ] Do not show API keys, tokens, credentials, or personal email.
- [ ] Say “supporting signal” for marketing and inventory unless attribution is proven.
- [ ] Describe the solution as a prototype, not a production system.
- [ ] Keep the original protected slides unchanged.

---

## 10. One-sentence final message

> “BusinessIntelligence.ai does not merely report that a KPI changed; it determines whether the movement is material, shows the evidence and uncertainty, checks what action is permitted, and communicates the result at the right level for each decision-maker.”
