from pathlib import Path
import json
import os

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="NexaMart KPI Intelligence", page_icon="📊", layout="wide")
ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "gold_layer"
API_URL = os.getenv("NEXAMART_API_URL", "http://127.0.0.1:8000/api")
API_TOKEN = os.getenv("NEXAMART_API_TOKEN", "")
try:
    ROLE_TOKENS = json.loads(os.getenv("NEXAMART_ROLE_TOKENS", "{}"))
except json.JSONDecodeError:
    ROLE_TOKENS = {}
ROLE_REGIONS = {"Executive", "Analyst"}

st.title("NexaMart KPI Intelligence-to-Action Engine")
st.caption("Deterministic KPI calculations and server-loaded evidence come before optional LLM narration.")
role = st.sidebar.selectbox("Prototype persona / entitlement", list(ROLE_REGIONS))
st.sidebar.warning("Demo authorization only unless NEXAMART_ROLE_TOKENS is configured for server-side role verification.")
summary_path = GOLD / "kpi_daily_summary_output.csv"
context_path = GOLD / "insight_context.json"
freshness_path = GOLD / "source_freshness.json"
region_path = GOLD / "kpi_region_daily_output.csv"
if not summary_path.exists() or not context_path.exists():
    st.error("Gold outputs are missing. Run `python run_pipeline.py` first.")
    st.stop()

summary = pd.read_csv(summary_path, parse_dates=["date"])
context = json.loads(context_path.read_text(encoding="utf-8"))
freshness = json.loads(freshness_path.read_text(encoding="utf-8")) if freshness_path.exists() else {}
if len(summary) < 2:
    st.error("At least two daily records are required for comparison.")
    st.stop()
latest, prior = summary.iloc[-1], summary.iloc[-2]


def pct(current, previous):
    return 0 if previous == 0 else (current - previous) / previous * 100


st.info(f"Latest available source date: {latest.date.date()}. Freshness is measured against the configured pipeline as-of date.")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", f"₹{latest.total_revenue:,.0f}", f"{pct(latest.total_revenue, prior.total_revenue):+.2f}%")
c2.metric("Orders", f"{latest.total_orders:,.0f}", f"{pct(latest.total_orders, prior.total_orders):+.2f}%")
c3.metric("AOV", f"₹{latest.aov:,.2f}", f"{pct(latest.aov, prior.aov):+.2f}%")
c4.metric("Stockout hours", f"{latest.total_stockout_hours:,.2f}", f"{pct(latest.total_stockout_hours, prior.total_stockout_hours):+.2f}%")

left, right = st.columns(2)
with left:
    st.subheader("KPI trend")
    st.line_chart(summary.set_index("date")[["total_revenue", "total_orders", "aov"]])
with right:
    st.subheader("Driver evidence")
    evidence = context.get("drivers", []) + context.get("supporting_signals", []) + context.get("policy_evidence", [])
    st.dataframe(pd.DataFrame(evidence), use_container_width=True, hide_index=True)

if region_path.exists():
    st.subheader(f"Visible regional KPI data — {role}")
    token = ROLE_TOKENS.get(role, API_TOKEN)
    try:
        regional = requests.get(f"{API_URL}/regional-snapshot", params={"persona": role, "insight_id": context["insight_id"]}, headers={"X-Nexamart-Token": token}, timeout=10)
        regional.raise_for_status()
        regional_data = regional.json()
        st.caption(f"Authorization mode: {regional_data.get('authorization_mode', 'unknown')}")
        st.dataframe(pd.DataFrame(regional_data.get("rows", [])), use_container_width=True, hide_index=True)
    except requests.RequestException as exc:
        st.warning(f"Regional entitlement service unavailable: {exc}")

st.subheader("Source freshness")
st.dataframe(pd.DataFrame(freshness).T, use_container_width=True)
confidence = context.get("confidence", {})
st.metric("Confidence gate", f"{confidence.get('score', 0):.0f}/100", confidence.get("status", "unknown"))
if confidence.get("status") != "proceed":
    st.warning("Abstention reasons: " + ", ".join(confidence.get("reasons", [])))

with st.expander("Required low-confidence demonstrations"):
    scenarios = context.get("scenarios", {})
    st.write("Sparse history", scenarios.get("sparse_history", {}))
    st.write("Contradictory evidence", scenarios.get("contradictory_evidence", {}))

st.subheader("Policy-constrained action")
action_gate = context.get("action_gate", {})
if action_gate.get("material") and action_gate.get("confidence_status") == "proceed" and context.get("actions"):
    st.dataframe(pd.DataFrame(context["actions"]), use_container_width=True, hide_index=True)
else:
    st.info("No action is available: the movement is not material, evidence did not pass the confidence gate, or no policy match was retrieved.")

if st.button("Generate evidence-grounded narrative"):
    payload = {"persona": role, "insight_id": context["insight_id"]}
    token = ROLE_TOKENS.get(role, API_TOKEN)
    try:
        res = requests.post(f"{API_URL}/generate-insight", headers={"X-Nexamart-Token": token}, json=payload, timeout=35)
        res.raise_for_status()
        result = res.json()
        if result.get("status") == "abstained":
            st.warning(result.get("narrative", "No insight generated"))
        elif result.get("status") in {"ok", "demo_ok"}:
            st.success(result.get("narrative", "No insight generated"))
            if result.get("status") == "demo_ok":
                st.caption("Deterministic demo narration; configure NEXAMART_LLM_URL for live LLM narration.")
        else:
            st.error(result.get("narrative", "No insight generated"))
        st.json(result.get("telemetry", {}))
    except requests.RequestException as exc:
        st.error(f"No explanation generated: {exc}")

st.subheader("Human feedback")
with st.form("feedback"):
    corrected = st.text_input("Corrected driver", context.get("drivers", [{}])[0].get("driver", ""))
    rating = st.selectbox("Recommendation rating", ["Correct / Accurate", "Incorrect / Flawed", "Needs review"])
    notes = st.text_area("Notes")
    if st.form_submit_button("Persist feedback"):
        body = {
            "insight_id": context["insight_id"],
            "user_id": f"demo-{role.lower()}",
            "persona": role,
            "predicted_driver": context.get("drivers", [{}])[0].get("driver", ""),
            "corrected_driver": corrected,
            "recommendation_rating": rating,
            "free_text": notes,
            "evidence_version": "pipeline_v2",
        }
        token = ROLE_TOKENS.get(role, API_TOKEN)
        try:
            response = requests.post(f"{API_URL}/log-feedback", headers={"X-Nexamart-Token": token}, json=body, timeout=10)
            response.raise_for_status()
            st.success("Feedback persisted.")
        except requests.RequestException as exc:
            st.error(f"Feedback was not persisted: {exc}")
