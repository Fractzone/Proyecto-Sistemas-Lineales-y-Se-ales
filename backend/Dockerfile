# Backend SPECTRA — API FastAPI + motor DSP
FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema mínimas (curl para healthcheck opcional).
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Descarga los datos si no existen y arranca la API.
CMD ["sh", "-c", "python -m data.loader && uvicorn api.main:app --host 0.0.0.0 --port 8000"]
