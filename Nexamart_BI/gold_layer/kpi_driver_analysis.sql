CREATE OR REPLACE VIEW nexamart.gold.kpi_driver_analysis AS
WITH periods AS (
  SELECT *, CASE
    WHEN date > date_sub((SELECT MAX(date) FROM nexamart.gold.kpi_daily_summary), 7) THEN 'current'
    WHEN date > date_sub((SELECT MAX(date) FROM nexamart.gold.kpi_daily_summary), 14) THEN 'previous'
  END AS period
  FROM nexamart.gold.kpi_daily_summary
), agg AS (
  SELECT period, SUM(total_revenue) AS revenue, SUM(total_quantity) AS quantity,
         SUM(total_revenue) / NULLIF(SUM(total_quantity), 0) AS realised_price
  FROM periods WHERE period IS NOT NULL GROUP BY period
), p AS (
  SELECT MAX(CASE WHEN period='current' THEN revenue END) AS rev_current,
    MAX(CASE WHEN period='previous' THEN revenue END) AS rev_previous,
    MAX(CASE WHEN period='current' THEN quantity END) AS qty_current,
    MAX(CASE WHEN period='previous' THEN quantity END) AS qty_previous,
    MAX(CASE WHEN period='current' THEN realised_price END) AS price_current,
    MAX(CASE WHEN period='previous' THEN realised_price END) AS price_previous FROM agg
)
SELECT rev_current - rev_previous AS revenue_change,
  (qty_current - qty_previous) * price_previous AS volume_effect,
  (price_current - price_previous) * qty_previous AS price_mix_effect,
  (qty_current - qty_previous) * (price_current - price_previous) AS interaction_effect,
  'price_volume_decomposition; non_causal; seven_day_windows' AS method FROM p;
