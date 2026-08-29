from pyspark.sql import functions as F

# Load native-grain source facts.
sales = spark.table("nexamart.bronze.sales")
inventory = spark.table("nexamart.bronze.inventory")
marketing = spark.table("nexamart.bronze.marketing")
products = spark.table("nexamart.bronze.products")

products = products.dropDuplicates(["product_id"]).select("product_id", "product_name", "category", "price")

sales_clean = (
    sales.dropDuplicates(["order_id"])
    .withColumn("date", F.to_date("date"))
    .withColumn("region", F.initcap(F.trim("region")))
    .withColumn("customer_segment", F.initcap(F.trim("customer_segment")))
    .withColumn("quantity", F.col("quantity").cast("double"))
    .withColumn("revenue", F.col("revenue").cast("double"))
    .dropna(subset=["order_id", "date", "product_id", "region"])
    .join(products, "product_id", "left")
)

inventory_clean = (
    inventory.dropDuplicates(["date", "product_id", "region"])
    .withColumn("date", F.to_date("date"))
    .withColumn("region", F.initcap(F.trim("region")))
    .fillna({"stock_available": 0, "stockout_hours": 0.0, "lead_time": 0})
    .join(products.select("product_id", "category"), "product_id", "left")
)

marketing_clean = (
    marketing.dropDuplicates(["date", "campaign_id"])
    .withColumn("date", F.to_date("date"))
    .withColumn("channel", F.initcap(F.trim("channel")))
    .fillna({"spend": 0.0, "impressions": 0, "clicks": 0, "conversions": 0})
)

# Preserve each source at its declared grain; Gold SQL aggregates before reconciliation.
sales_clean.write.format("delta").mode("overwrite").saveAsTable("nexamart.silver.sales_clean")
inventory_clean.write.format("delta").mode("overwrite").saveAsTable("nexamart.silver.inventory_clean")
marketing_clean.write.format("delta").mode("overwrite").saveAsTable("nexamart.silver.marketing_clean")
