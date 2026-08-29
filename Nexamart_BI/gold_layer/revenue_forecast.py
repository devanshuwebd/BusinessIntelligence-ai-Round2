import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

summary = spark.table("nexamart.gold.sales_daily").select("date", "total_revenue").toPandas()
summary["date"] = pd.to_datetime(summary["date"])
summary = summary.sort_values("date").reset_index(drop=True)
summary["day_index"] = np.arange(len(summary))

model = LinearRegression().fit(summary[["day_index"]], summary["total_revenue"])
summary["expected_revenue"] = model.predict(summary[["day_index"]])
forecast = spark.createDataFrame(summary[["date", "total_revenue", "expected_revenue"]])
forecast.write.format("delta").mode("overwrite").saveAsTable("nexamart.gold.revenue_forecast")
print("Revenue forecast baseline generated from gold.sales_daily")
