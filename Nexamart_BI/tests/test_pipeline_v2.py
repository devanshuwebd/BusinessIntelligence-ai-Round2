from pathlib import Path
import pandas as pd
from Nexamart_BI.src.kpi_engine.pipeline_v2 import (
    build_daily_kpis,
    confidence_gate,
    decompose_revenue_change,
    detect_contradictions,
    detect_material_movements,
)

RAW = Path(__file__).parents[1] / "bronze_layer" / "raw"

def test_no_fact_multiplication():
    kpi, _ = build_daily_kpis(RAW)
    sales = pd.read_csv(RAW / "sales.csv")
    assert int(kpi.total_orders.sum()) == sales.order_id.nunique()
    assert round(float(kpi.total_revenue.sum()), 2) == round(float(sales.revenue.sum()), 2)

def test_decomposition_reconciles():
    sales = pd.read_csv(RAW / "sales.csv", parse_dates=["date"])
    drivers = decompose_revenue_change(sales, sales.date.max())
    current = sales[sales.date > sales.date.max() - pd.Timedelta(days=7)].revenue.sum()
    previous = sales[(sales.date > sales.date.max() - pd.Timedelta(days=14)) & (sales.date <= sales.date.max() - pd.Timedelta(days=7))].revenue.sum()
    assert round(sum(d["effect"] for d in drivers), 2) == round(current - previous, 2)

def test_sparse_history_abstains():
    gate = confidence_gate(15, {"sales": {"status": "fresh"}}, [], 4)
    assert gate["status"] == "abstain"
    assert "sparse_history_less_than_28_days" in gate["reasons"]

def test_stale_contradictory_evidence_abstains():
    gate = confidence_gate(90, {"sales": {"status": "stale"}}, ["revenue_down_demand_up:P001"], 4)
    assert gate["status"] == "abstain"
    assert "contradictory_evidence" in gate["reasons"]


def test_demand_stockout_co_movement_is_not_contradiction():
    sales = pd.DataFrame([
        {"date": pd.Timestamp("2026-01-01"), "product_id": "P001", "order_id": "o1", "quantity": 2, "revenue": 200},
        {"date": pd.Timestamp("2026-01-08"), "product_id": "P001", "order_id": "o2", "quantity": 3, "revenue": 300},
    ])
    assert detect_contradictions(sales, pd.DataFrame(), pd.Timestamp("2026-01-08"), days=7) == []


def test_materiality_is_explicitly_scored():
    values = [1000000, 1010000, 990000, 1005000, 995000, 1008000, 992000, 1400000]
    kpi = pd.DataFrame({"total_revenue": values})
    scored = detect_material_movements(kpi, pct_threshold=0.10, abs_threshold=100000)
    assert bool(scored.iloc[-1]["material"])
    assert scored.iloc[-1]["priority_score"] > 0


def test_revenue_down_demand_up_is_contradiction():
    sales = pd.DataFrame([
        {"date": pd.Timestamp("2026-01-01"), "product_id": "P001", "order_id": "o1", "quantity": 1, "revenue": 100},
        {"date": pd.Timestamp("2026-01-01"), "product_id": "P001", "order_id": "o2", "quantity": 1, "revenue": 100},
        {"date": pd.Timestamp("2026-01-08"), "product_id": "P001", "order_id": "o3", "quantity": 1, "revenue": 34},
        {"date": pd.Timestamp("2026-01-08"), "product_id": "P001", "order_id": "o4", "quantity": 1, "revenue": 33},
        {"date": pd.Timestamp("2026-01-08"), "product_id": "P001", "order_id": "o5", "quantity": 1, "revenue": 33},
    ])
    assert detect_contradictions(sales, pd.DataFrame(), pd.Timestamp("2026-01-08"), days=7) == ["revenue_down_demand_up:P001"]
