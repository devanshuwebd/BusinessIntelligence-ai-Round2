CREATE OR REPLACE VIEW nexamart.gold.kpi_anomalies AS
WITH daily_agg AS (
    SELECT
        CAST(date AS DATE) AS date,
        total_revenue AS daily_revenue
    FROM nexamart.gold.kpi_daily_summary
    WHERE total_revenue IS NOT NULL
),
with_baseline AS (
    SELECT
        date,
        daily_revenue,
        AVG(daily_revenue) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS baseline_7d,
        STDDEV_SAMP(daily_revenue) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS baseline_std_7d
    FROM daily_agg
), scored AS (
    SELECT
        date,
        daily_revenue,
        baseline_7d,
        baseline_std_7d,
        daily_revenue - baseline_7d AS absolute_delta,
        (daily_revenue - baseline_7d) / NULLIF(baseline_7d, 0) AS pct_deviation,
        (daily_revenue - baseline_7d) / NULLIF(baseline_std_7d, 0) AS z_score
    FROM with_baseline
)
SELECT
    date,
    daily_revenue,
    baseline_7d,
    baseline_std_7d,
    ROUND(absolute_delta, 2) AS absolute_delta,
    ROUND(pct_deviation * 100, 2) AS pct_deviation,
    ROUND(z_score, 2) AS z_score,
    ABS(COALESCE(pct_deviation, 0)) * ABS(COALESCE(absolute_delta, 0)) AS priority_score,
    CASE
        WHEN ABS(pct_deviation) >= 0.10
         AND ABS(absolute_delta) >= 100000
         AND ABS(z_score) >= 2.0 THEN 'MATERIAL'
        ELSE 'NORMAL'
    END AS anomaly_status
FROM scored;
