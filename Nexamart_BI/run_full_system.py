from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT / "run_pipeline.py")], check=True)
print("Pipeline complete. Start services with:")
print("  uvicorn Nexamart_BI.backend.main:app --port 8000")
print("  streamlit run Nexamart_BI/dashboard/app.py")
