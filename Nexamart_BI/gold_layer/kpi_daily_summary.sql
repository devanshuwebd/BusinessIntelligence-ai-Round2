CREATE OR REPLACE VIEW nexamart.gold.sales_daily AS
SELECT CAST(date AS DATE) AS date, SUM(revenue) AS total_revenue, COUNT(DISTINCT order_id) AS total_orders, SUM(quantity) AS total_quantity, SUM(revenue) / NULLIF(SUM(quantity), 0) AS realised_price, SUM(revenue) / NULLIF(COUNT(DISTINCT order_id), 0) AS aov
FROM nexamart.silver.sales_clean GROUP BY CAST(date AS DATE);

CREATE OR REPLACE VIEW nexamart.gold.marketing_daily AS
SELECT CAST(date AS DATE) AS date, SUM(spend) AS marketing_spend, SUM(impressions) AS impressions, SUM(clicks) AS clicks, SUM(conversions) AS conversions, SUM(conversions) / NULLIF(SUM(clicks), 0) AS click_to_conversion_rate
FROM nexamart.silver.marketing_clean GROUP BY CAST(date AS DATE);

CREATE OR REPLACE VIEW nexamart.gold.inventory_daily AS
SELECT CAST(date AS DATE) AS date, AVG(stock_available) AS avg_stock_available, SUM(stockout_hours) AS total_stockout_hours, AVG(lead_time) AS avg_lead_time
FROM nexamart.silver.inventory_clean GROUP BY CAST(date AS DATE);

CREATE OR REPLACE VIEW nexamart.gold.kpi_daily_summary AS
SELECT COALESCE(s.date, m.date, i.date) AS date, s.total_revenue, s.total_orders, s.total_quantity, s.realised_price, s.aov, m.marketing_spend, m.impressions, m.clicks, m.conversions, m.click_to_conversion_rate, i.avg_stock_available, i.total_stockout_hours, i.avg_lead_time
FROM nexamart.gold.sales_daily s
FULL OUTER JOIN nexamart.gold.marketing_daily m ON s.date = m.date
FULL OUTER JOIN nexamart.gold.inventory_daily i ON COALESCE(s.date, m.date) = i.date;
