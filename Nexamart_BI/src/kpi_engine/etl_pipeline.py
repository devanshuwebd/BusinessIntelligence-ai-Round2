# Databricks entrypoint: execute the governed Silver cleaning transformations.
# The implementation lives in silver_layer/Cleaning.py so the notebook and local
# project documentation refer to the same source-of-truth logic.
from pathlib import Path

exec(open(Path(__file__).resolve().parents[2] / "silver_layer" / "Cleaning.py", encoding="utf-8").read())
