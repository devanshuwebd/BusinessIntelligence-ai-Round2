FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501 8000
CMD ["sh", "-c", "set -e; python run_pipeline.py; uvicorn backend.main:app --host 0.0.0.0 --port 8000 & exec streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0"]
