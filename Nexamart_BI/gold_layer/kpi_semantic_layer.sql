CREATE OR REPLACE TABLE nexamart.gold.kpi_contract (
  kpi_id STRING, kpi_name STRING, definition STRING, formula_sql STRING,
  grain STRING, dimensions ARRAY<STRING>, source_tables ARRAY<STRING>,
  refresh_cadence STRING, timezone STRING, currency STRING, owner_role STRING,
  sensitivity_class STRING, entitlement_policy STRING, materiality_pct DOUBLE,
  materiality_abs DOUBLE, min_history_days INT, contract_version STRING
);

INSERT INTO nexamart.gold.kpi_contract VALUES
('revenue','Total Revenue','Completed sales monetary value','SUM(revenue)','date',array(),array('nexamart.silver.sales_clean'),'daily','Asia/Kolkata','INR','Executive','internal','aggregate_only',0.10,100000,28,'2.1'),
('orders','Total Orders','Unique completed orders','COUNT(DISTINCT order_id)','date',array(),array('nexamart.silver.sales_clean'),'daily','Asia/Kolkata','count','Executive','internal','aggregate_only',0.15,100,28,'2.1'),
('aov','Average Order Value','Revenue divided by unique orders','SUM(revenue)/COUNT(DISTINCT order_id)','date',array(),array('nexamart.silver.sales_clean'),'daily','Asia/Kolkata','INR','Commercial Team','internal','aggregate_only',0.05,50000,28,'2.1'),
('marketing_efficiency','Click-to-Conversion Rate','Conversions divided by clicks','SUM(conversions)/NULLIF(SUM(clicks),0)','date',array(),array('nexamart.silver.marketing_clean'),'daily','Asia/Kolkata','rate','Growth Team','internal','aggregate_only',0.15,0.01,28,'2.1'),
('stockout_hours','Stockout Hours','Observed stockout hours','SUM(stockout_hours)','date',array(),array('nexamart.silver.inventory_clean'),'daily','Asia/Kolkata','hours','Supply Chain Team','internal','aggregate_only',0.10,4,28,'2.1');
