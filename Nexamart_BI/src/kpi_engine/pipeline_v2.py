from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = {
    "sales": {"order_id", "date", "product_id", "region", "customer_segment", "channel", "quantity", "revenue"},
    "inventory": {"date", "product_id", "region", "stock_available", "stockout_hours", "lead_time"},
    "marketing": {"date", "campaign_id", "channel", "spend", "impressions", "clicks", "conversions"},
    "products": {"product_id", "product_name", "category", "price"},
}


def read_and_validate(path, source):
    df = pd.read_csv(path)
    missing = REQUIRED[source] - set(df.columns)
    if missing:
        raise ValueError(f"{source}: missing columns {sorted(missing)}")
    if df.empty:
        raise ValueError(f"{source}: empty source")
    if "date" in df:
        df["date"] = pd.to_datetime(df["date"], errors="raise").dt.normalize()
    numeric = ["quantity", "revenue", "stock_available", "stockout_hours", "lead_time", "spend", "impressions", "clicks", "conversions", "price"]
    for col in numeric:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if df.isna().any().any():
        raise ValueError(f"{source}: nulls remain after type coercion")
    return df


def safe_rate(num, den):
    return num.div(den.replace(0, np.nan)).fillna(0.0)


def _as_of_timestamp(as_of_date=None):
    if as_of_date is None:
        return pd.Timestamp.now(tz="Asia/Kolkata").tz_localize(None).normalize()
    value = pd.Timestamp(as_of_date)
    if value.tzinfo is not None:
        value = value.tz_convert("Asia/Kolkata").tz_localize(None)
    return value.normalize()


def filter_to_as_of(df, as_of_date=None):
    if as_of_date is None:
        return df.copy()
    as_of = _as_of_timestamp(as_of_date)
    filtered = df[df["date"] <= as_of].copy()
    if filtered.empty:
        raise ValueError(f"No {len(df.columns)}-column source records exist on or before {as_of.date()}")
    return filtered


def build_daily_kpis(raw_dir, as_of_date=None):
    raw = Path(raw_dir)
    sales = filter_to_as_of(read_and_validate(raw / "sales.csv", "sales"), as_of_date)
    inventory = filter_to_as_of(read_and_validate(raw / "inventory.csv", "inventory"), as_of_date)
    marketing = filter_to_as_of(read_and_validate(raw / "marketing.csv", "marketing"), as_of_date)
    products = read_and_validate(raw / "products.csv", "products")
    if products["product_id"].duplicated().any():
        raise ValueError("products: product_id must be unique")

    sales = sales.merge(products[["product_id", "category"]], on="product_id", how="left", validate="many_to_one")
    inventory = inventory.merge(products[["product_id", "category"]], on="product_id", how="left", validate="many_to_one")

    sales_day = sales.groupby("date", as_index=False).agg(
        total_revenue=("revenue", "sum"), total_orders=("order_id", "nunique"), total_quantity=("quantity", "sum")
    )
    sales_day["aov"] = safe_rate(sales_day["total_revenue"], sales_day["total_orders"])
    sales_day["realised_price"] = safe_rate(sales_day["total_revenue"], sales_day["total_quantity"])
    sales_day["sales_available"] = True

    marketing_day = marketing.groupby("date", as_index=False).agg(
        marketing_spend=("spend", "sum"), impressions=("impressions", "sum"), clicks=("clicks", "sum"), conversions=("conversions", "sum")
    )
    marketing_day["click_to_conversion_rate"] = safe_rate(marketing_day["conversions"], marketing_day["clicks"])
    marketing_day["marketing_available"] = True

    inventory_day = inventory.groupby("date", as_index=False).agg(
        avg_stock_available=("stock_available", "mean"), total_stockout_hours=("stockout_hours", "sum"), avg_lead_time=("lead_time", "mean")
    )
    inventory_day["inventory_available"] = True

    kpi = sales_day.merge(marketing_day, on="date", how="outer", validate="one_to_one")
    kpi = kpi.merge(inventory_day, on="date", how="outer", validate="one_to_one").sort_values("date").reset_index(drop=True)
    # Never forward-fill facts across source refresh gaps. Availability flags make gaps explicit.

    as_of = _as_of_timestamp(as_of_date)
    freshness = {}
    for name, df in [("sales", sales), ("marketing", marketing), ("inventory", inventory)]:
        max_date = df["date"].max()
        lag_days = int((as_of - max_date).days)
        freshness[name] = {
            "max_event_date": max_date.date().isoformat(),
            "as_of_date": as_of.date().isoformat(),
            "lag_days": lag_days,
            "status": "fresh" if lag_days <= 1 else "stale",
            "row_count": int(len(df)),
        }
    return kpi, freshness


def detect_material_movements(kpi, pct_threshold=0.10, abs_threshold=100000.0):
    out = kpi.copy()
    out["baseline_7d"] = out["total_revenue"].shift(1).rolling(7, min_periods=7).mean()
    out["baseline_std_7d"] = out["total_revenue"].shift(1).rolling(7, min_periods=7).std(ddof=1)
    out["revenue_delta"] = out["total_revenue"] - out["baseline_7d"]
    out["revenue_change_pct"] = out["revenue_delta"].div(out["baseline_7d"].replace(0, np.nan))
    out["z_score"] = out["revenue_delta"].div(out["baseline_std_7d"].replace(0, np.nan))
    out["material"] = (
        out["baseline_7d"].notna()
        & (out["revenue_change_pct"].abs() >= pct_threshold)
        & (out["revenue_delta"].abs() >= abs_threshold)
        & (out["z_score"].abs() >= 2.0)
    )
    out["priority_score"] = out["revenue_change_pct"].abs().fillna(0) * out["revenue_delta"].abs().fillna(0)
    return out


def decompose_revenue_change(sales, latest_date, days=7):
    latest = pd.Timestamp(latest_date).normalize()
    current = sales[(sales.date > latest - pd.Timedelta(days=days)) & (sales.date <= latest)]
    previous = sales[(sales.date > latest - pd.Timedelta(days=2 * days)) & (sales.date <= latest - pd.Timedelta(days=days))]
    q1, q0 = current.quantity.sum(), previous.quantity.sum()
    p1 = current.revenue.sum() / q1 if q1 else np.nan
    p0 = previous.revenue.sum() / q0 if q0 else np.nan
    if not np.isfinite(p0) or not np.isfinite(p1):
        return []
    return [
        {"evidence_id": "volume_decomposition", "driver": "volume", "effect": float((q1 - q0) * p0), "method": "price-volume decomposition", "causal": False},
        {"evidence_id": "price_mix_decomposition", "driver": "price_mix", "effect": float((p1 - p0) * q0), "method": "price-volume decomposition", "causal": False},
        {"evidence_id": "interaction_decomposition", "driver": "interaction", "effect": float((q1 - q0) * (p1 - p0)), "method": "price-volume decomposition", "causal": False},
    ]


def detect_contradictions(sales, inventory, latest_date, days=7):
    """Find metric-direction conflicts, not ordinary demand/stockout co-movement.

    Revenue rising while stockouts rise is a plausible demand/supply interaction. A
    contradiction is reserved for revenue falling while both demand proxies rise,
    which warrants checking attribution, returns, or source quality.
    """
    del inventory  # retained in the public signature for pipeline compatibility
    latest = pd.Timestamp(latest_date).normalize()
    current_start, previous_start = latest - pd.Timedelta(days=days), latest - pd.Timedelta(days=2 * days)
    current = sales[(sales.date > current_start) & (sales.date <= latest)].groupby("product_id").agg(
        revenue=("revenue", "sum"), quantity=("quantity", "sum"), orders=("order_id", "nunique")
    )
    previous = sales[(sales.date > previous_start) & (sales.date <= current_start)].groupby("product_id").agg(
        revenue=("revenue", "sum"), quantity=("quantity", "sum"), orders=("order_id", "nunique")
    )
    joined = current.join(previous, lsuffix="_current", rsuffix="_previous").dropna()
    revenue_change = joined.revenue_current.div(joined.revenue_previous.replace(0, np.nan)) - 1
    quantity_change = joined.quantity_current.div(joined.quantity_previous.replace(0, np.nan)) - 1
    order_change = joined.orders_current.div(joined.orders_previous.replace(0, np.nan)) - 1
    conflicts = joined[
        (revenue_change <= -0.10)
        & (quantity_change >= 0.10)
        & (order_change >= 0.10)
    ]
    return [f"revenue_down_demand_up:{product_id}" for product_id in conflicts.index]


def history_days_by_product(sales):
    history = sales.groupby("product_id")["date"].agg(first_date="min", last_date="max").reset_index()
    history["history_days"] = (history.last_date - history.first_date).dt.days + 1
    return history


def confidence_gate(history_days, freshness, contradictions, evidence_count):
    reasons = []
    if history_days < 28:
        reasons.append("sparse_history_less_than_28_days")
    if any(v["status"] == "stale" for v in freshness.values()):
        reasons.append("one_or_more_sources_stale")
    if contradictions:
        reasons.append("contradictory_evidence")
    if evidence_count < 2:
        reasons.append("insufficient_evidence")
    score = max(0.0, 100.0 - 25.0 * len(reasons))
    return {"score": round(score, 2), "status": "abstain" if reasons or score < 60 else "proceed", "reasons": reasons}
