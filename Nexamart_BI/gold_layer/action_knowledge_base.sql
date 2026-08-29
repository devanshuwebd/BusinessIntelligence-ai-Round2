CREATE OR REPLACE TABLE nexamart.gold.action_knowledge_base (
  driver_type STRING, trigger_rule STRING, controllable_lever STRING,
  recommended_action STRING, owner STRING, decision_right STRING,
  expected_impact STRING, impact_method STRING, monitoring_plan STRING
);

INSERT INTO nexamart.gold.action_knowledge_base VALUES
('stockout_hours','stockout_hours > 4.0 OR stock_available < 10','regional_inventory_transfer','Reroute stock from an adjacent regional hub before spot-market purchasing','Operations Team','Supply Chain Lead',NULL,'Not estimated','Monitor stockout hours and fill rate for 48 hours'),
('marketing_efficiency','click_to_conversion_rate declines > 15%','campaign_review','Review campaigns and throttle sustained low-efficiency campaigns','Growth Team','Growth Team Lead',NULL,'Not estimated','Monitor click-to-conversion rate for 7 days'),
('lead_time','lead_time > 7 days at reorder point','precleared_purchase_order','Pre-clear replenishment or reroute through an alternative hub','Operations Team','Supply Chain Lead',NULL,'Not estimated','Monitor lead time and inventory coverage daily');
