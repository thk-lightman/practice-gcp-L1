FROM python:3.11-slim

WORKDIR /app

# Dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Model artifacts (Option A: image-embedded)
COPY model_trace.nc .
COPY model_meta.json .

# Serving code
COPY main.py .

# Cloud Run provides PORT env var
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
