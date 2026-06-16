# SPECTRA

**Análisis espectral académico de activos financieros** — proyecto final de
*Sistemas Lineales y Señales*. Implementa la teoría de **Oppenheim & Schafer**
con un motor DSP propio (solo NumPy) y la expone en un dashboard científico
React + Plotly servido por una API FastAPI.

> Estudio **retrospectivo y descriptivo**: muestra los patrones espectrales de
> SPY, AAL y NFLX antes / durante / después de la pandemia. **No** es asesoría
> financiera, predicción ni señal de trading.

## Qué hace

- Descarga (una sola vez) y cachea precios ajustados de **SPY, AAL, NFLX**
  (2018–2023) y los segmenta en tres épocas.
- Sobre los retornos logarítmicos calcula —**todo a mano sobre NumPy**— PSD de
  Welch, entropía espectral y régimen, autocorrelación (Wiener-Khinchin),
  coherencia con el mercado, espectrograma STFT, filtrado FIR e IFFT, ciclo
  dominante y fase.
- Dashboard de 4 paneles coordinados + vistas comparativas.

La matemática y el mapeo a los capítulos de Oppenheim están en
[`docs/TECHNICAL.md`](docs/TECHNICAL.md).

> **Única dependencia externa de DSP en producción:** `numpy.fft`. `scipy.signal`
> se usa **solo** en los tests como oráculo de validación.

---

## Requisitos

- **Python 3.12+** (probado en 3.14).
- **Node 18+** (probado en Node 26).
- Conexión a internet **la primera vez** (para descargar los datos de Yahoo
  Finance). Después funciona offline con el caché CSV.

---

## Ejecución rápida (lanzador automático)

Con Python y Node instalados, desde la raíz del proyecto:

```bash
python main.py
```

Verifica prerrequisitos, prepara el entorno (venv, dependencias, datos) si hace
falta, levanta backend + frontend y abre el dashboard en el navegador. `Ctrl+C`
para detener. Si prefieres el control manual, sigue los pasos de abajo.

---

## Ejecución local (manual, paso a paso)

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt

# Descarga y cachea los datos (una sola vez):
python -m data.loader

# Tests del motor DSP + API (incluye validación contra scipy):
pytest

# Servidor de la API en http://localhost:8000  (docs en /docs):
uvicorn api.main:app --reload --port 8000
```

### 2. Frontend (en otra terminal)

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

El frontend en desarrollo proxea `/api` → `http://localhost:8000`, así que con
ambos procesos arriba el dashboard funciona directamente.

Para un build de producción: `npm run build` (genera `frontend/dist/`).

---

## Ejecución con Docker

> Entregable incluido; requiere Docker Desktop. Levanta backend (8000) y
> frontend servido por nginx (8080).

```bash
docker compose up --build
# Frontend: http://localhost:8080
# API:      http://localhost:8000/docs
```

La primera vez, el backend descarga los datos al iniciar. Para volver a
descargarlos: borra `backend/data/raw/*.csv` y reinicia (o ejecuta
`python -m data.loader` dentro del contenedor backend).

---

## Estructura

```
backend/
  spectra_dsp/   motor DSP propio (núcleo académico, solo NumPy)
  data/          descarga/caché yfinance + segmentación por época
  api/            FastAPI (endpoints, orquestación, interpretación)
  tests/          pytest (oráculos scipy, Parseval, Wiener-Khinchin, FIR, API)
frontend/         React 18 + TypeScript + Vite + Plotly
docs/TECHNICAL.md documentación matemática + mapeo a Oppenheim
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/assets` | Tickers y su rol en el estudio |
| GET | `/epochs` | Épocas y sus fechas |
| POST | `/analyze` | Análisis completo de un (activo, época) |
| POST | `/compare` | Métricas resumidas: 1 activo × 3 épocas, o 3 activos × 1 época |

## Regenerar el caché de datos

```bash
cd backend
python -m data.loader        # usa el caché si existe
# forzar nueva descarga:
python -c "from data.loader import download_all; download_all(force=True)"
```
