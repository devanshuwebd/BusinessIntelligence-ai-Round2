from pathlib import Path
import json
import os
import pandas as pd
from src.kpi_engine.pipeline_v2 import (
    build_daily_kpis,
    confidence_gate,
    decompose_revenue_change,
    detect_contradictions,
    detect_material_movements,
    filter_to_as_of,
    history_days_by_product,
    read_and_validate,
)
from src.llm.rag_retriever import retrieve_policy_context
from src.recommendations.lineage import generate_evidence_lineage

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "bronze_layer" / "raw"
DOCS = ROOT / "docs"
SILVER = ROOT / "silver_layer"
GOLD = ROOT / "gold_layer"
SILVER.mkdir(exist_ok=True)
GOLD.mkdir(exist_ok=True)

# Set NEXAMART_DATA_AS_OF to a historical snapshot when replaying the demo.
as_of_override = os.getenv("NEXAMART_DATA_AS_OF")
sales = filter_to_as_of(read_and_validate(RAW / "sales.csv", "sales"), as_of_override)
inventory = filter_to_as_of(read_and_validate(RAW / "inventory.csv", "inventory"), as_of_override)
marketing = filter_to_as_of(read_and_validate(RAW / "marketing.csv", "marketing"), as_of_override)
for name, frame in [("sales", sales), ("inventory", inventory), ("marketing", marketing)]:
    try:
        frame.to_parquet(SILVER / f"{name}_clean.parquet", index=False)
    except ImportError:
        frame.to_csv(SILVER / f"{name}_clean.csv", index=False)

kpi, freshness = build_daily_kpis(RAW, as_of_date=as_of_override)
movement = detect_material_movements(kpi)
latest_date = kpi["date"].max()
latest_movement = movement.iloc[-1].to_dict()
drivers = decompose_revenue_change(sales, latest_date)
latest, prior = kpi[kpi["date"] <= latest_date].iloc[-1], kpi[kpi["date"] <= latest_date].iloc[-2]
supporting = [
    {"evidence_id": "marketing_daily_delta", "signal": "marketing_spend", "value": float(latest.marketing_spend - prior.marketing_spend), "causal": False},
    {"evidence_id": "marketing_efficiency", "signal": "click_to_conversion_rate", "value": float(latest.click_to_conversion_rate - prior.click_to_conversion_rate), "causal": False},
    {"evidence_id": "inventory_daily_delta", "signal": "total_stockout_hours", "value": float(latest.total_stockout_hours - prior.total_stockout_hours), "causal": False},
]
history = history_days_by_product(sales)
global_history_days = int((sales.date.max() - sales.date.min()).days) + 1
contradictions = detect_contradictions(sales, inventory, latest_date)
confidence = confidence_gate(global_history_days, freshness, contradictions, len(drivers) + len(supporting))

# The contradiction scenario is a controlled fixture, explicitly labelled as simulated.
conflict_as_of = pd.Timestamp("2026-07-31")
scenario_sales = pd.DataFrame([
    {"date": conflict_as_of - pd.Timedelta(days=13), "product_id": "SCENARIO_P001", "order_id": "scenario-previous-1", "quantity": 1, "revenue": 100.0},
    {"date": conflict_as_of - pd.Timedelta(days=13), "product_id": "SCENARIO_P001", "order_id": "scenario-previous-2", "quantity": 1, "revenue": 100.0},
    {"date": conflict_as_of - pd.Timedelta(days=2), "product_id": "SCENARIO_P001", "order_id": "scenario-current-1", "quantity": 1, "revenue": 34.0},
    {"date": conflict_as_of - pd.Timedelta(days=2), "product_id": "SCENARIO_P001", "order_id": "scenario-current-2", "quantity": 1, "revenue": 33.0},
    {"date": conflict_as_of - pd.Timedelta(days=2), "product_id": "SCENARIO_P001", "order_id": "scenario-current-3", "quantity": 1, "revenue": 33.0},
])
conflict_ids = detect_contradictions(scenario_sales, pd.DataFrame(), conflict_as_of)
scenario_freshness = {name: {**value, "status": "fresh"} for name, value in freshness.items()}
conflict_confidence = confidence_gate(global_history_days, scenario_freshness, conflict_ids, len(drivers) + len(supporting))
p999_rows = history.loc[history.product_id.eq("P999"), "history_days"]
p999_history = int(p999_rows.iloc[0]) if not p999_rows.empty else 0
sparse_confidence = confidence_gate(p999_history, scenario_freshness, [], len(drivers))

region_daily = sales.groupby(["date", "region"], as_index=False).agg(
    total_revenue=("revenue", "sum"), total_orders=("order_id", "nunique"), total_quantity=("quantity", "sum")
)
region_daily["aov"] = region_daily["total_revenue"].div(region_daily["total_orders"].replace(0, pd.NA))
regional_snapshot = region_daily[region_daily.date.eq(latest_date)].copy()
regional_snapshot["date"] = regional_snapshot["date"].dt.date.astype(str)
source_metadata = {name: {"max_event_date": value["max_event_date"], "as_of_date": value["as_of_date"], "lag_days": value["lag_days"], "row_count": value["row_count"]} for name, value in freshness.items()}
lineage = generate_evidence_lineage(
    "Total Revenue",
    source_metadata,
    [item["evidence_id"] for item in drivers + supporting],
    "deterministic daily aggregation plus price-volume-mix decomposition; supporting signals are non-causal",
)

# Actions require all three gates: material movement, proceed confidence, and retrievable policy context.
policy_context = {
    "volume": retrieve_policy_context("stockout_hours", DOCS),
    "price_mix": retrieve_policy_context("price_mix", DOCS),
    "interaction": retrieve_policy_context("price_mix", DOCS),
}
action_rules = {
    "volume": {"lever": "inventory_and_demand_review", "action": "Review availability and demand signals before changing spend", "owner": "Operations Team", "decision_right": "Operations Lead", "monitoring_plan": "Monitor orders, quantity, and stockout hours for 48 hours", "policy_document": "inventory_policy.pdf"},
    "price_mix": {"lever": "pricing_review", "action": "Review price and product mix changes against approved pricing policy", "owner": "Commercial Team", "decision_right": "Commercial Lead", "monitoring_plan": "Monitor realised price, AOV, and margin daily", "policy_document": "pricing_policy.pdf"},
    "interaction": {"lever": "cross_functional_review", "action": "Review the interaction between volume and realised price", "owner": "Commercial Team", "decision_right": "Commercial Lead", "monitoring_plan": "Monitor revenue decomposition on the next refresh", "policy_document": "pricing_policy.pdf"},
}
def policy_was_retrieved(text):
    return bool(text) and not text.startswith("No policy document") and not text.startswith("Policy retrieval unavailable:")


policy_evidence = [
    {"driver": driver, "evidence_id": f"policy_{driver}", "signal": "retrieved_policy", "document": rule["policy_document"], "available": policy_was_retrieved(policy_context[driver]), "causal": False}
    for driver, rule in action_rules.items()
]
actions = []
policy_by_driver = {item["driver"]: item for item in policy_evidence}
if bool(latest_movement.get("material")) and confidence["status"] == "proceed":
    for driver in sorted((item for item in drivers if item["effect"] < 0), key=lambda item: abs(item["effect"]), reverse=True):
        rule = action_rules.get(driver["driver"])
        policy = policy_by_driver.get(driver["driver"])
        if rule and policy and policy["available"]:
            actions.append({"driver": driver["driver"], "evidence_id": driver["evidence_id"], **rule, "policy_evidence_id": policy["evidence_id"], "expected_impact": None, "impact_method": "Not estimated without experiment or validated model"})

kpi.to_csv(GOLD / "kpi_daily_summary_output.csv", index=False)
region_daily.to_csv(GOLD / "kpi_region_daily_output.csv", index=False)
movement.to_csv(GOLD / "kpi_movement_output.csv", index=False)
pd.DataFrame(drivers + supporting).to_csv(GOLD / "kpi_driver_analysis_output.csv", index=False)
(GOLD / "source_freshness.json").write_text(json.dumps(freshness, indent=2), encoding="utf-8")
context = {
    "insight_id": f"revenue-{latest_date.date().isoformat()}",
    "as_of_date": latest_date.date().isoformat(),
    "snapshot": latest.to_dict(),
    "regional_snapshot": regional_snapshot.to_dict("records"),
    "movement": latest_movement,
    "drivers": drivers,
    "supporting_signals": supporting,
    "policy_evidence": policy_evidence,
    "confidence": confidence,
    "lineage": lineage,
    "actions": actions,
    "action_gate": {"material": bool(latest_movement.get("material")), "confidence_status": confidence["status"], "policy_retrieval_required": True},
    "method_boundary": "LLM narrates server-loaded evidence only; it cannot calculate or claim causality.",
    "scenarios": {
        "sparse_history": {"entity": "P999", "history_days": p999_history, "history_definition": "calendar span from first to last observed sale", "confidence": sparse_confidence},
        "contradictory_evidence": {"scenario_type": "controlled_fixture", "as_of_date": conflict_as_of.date().isoformat(), "evidence_ids": conflict_ids, "confidence": conflict_confidence},
    },
}
(GOLD / "insight_context.json").write_text(json.dumps(context, indent=2, default=str), encoding="utf-8")
print(f"Validated rows: sales={len(sales):,}, inventory={len(inventory):,}, marketing={len(marketing):,}")
print(f"Latest available source date: {latest_date.date()} | confidence: {confidence['status']} | material: {bool(latest_movement.get('material'))}")
print(f"Scenario gates: P999={sparse_confidence['status']} | contradiction={conflict_confidence['status']}")
