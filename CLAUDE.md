# CLAUDE.md — Contexto del proyecto SPECTRA

Este archivo resume el estado del proyecto para retomarlo en una sesión futura.

## Qué es

**SPECTRA**: aplicación web académica para el proyecto final de *Sistemas Lineales
y Señales*. Demuestra dominio de la teoría de **Oppenheim & Schafer** implementando
el **análisis espectral a mano** y mostrando, de forma retrospectiva, los patrones
de **SPY, AAL y NFLX** antes / durante / después de la pandemia (2018–2023).

Es un estudio **descriptivo y retrospectivo**: sin predicción, sin señales de
trading, sin recomendaciones de inversión.

## Estado actual: COMPLETO y verificado ✅

Las 5 fases del plan están terminadas:
1. ✅ Andamiaje + capa de datos (descarga real de yfinance cacheada)
2. ✅ Motor DSP propio + tests
3. ✅ API FastAPI
4. ✅ Frontend React + Plotly
5. ✅ Docs + Docker

- **40/40 tests pytest verdes** (incluye oráculos scipy, Parseval, Wiener-Khinchin).
- **`npm run build` del frontend pasa** (typecheck + bundle).
- **Pipeline validado con datos reales** de los 9 pares (activo, época).

El plan aprobado original está en
`C:\Users\diego\.claude\plans\quiero-que-en-el-async-duckling.md`.

## REGLA INVIOLABLE del proyecto

> En **producción** la única primitiva externa de DSP permitida es
> `numpy.fft.fft` / `numpy.fft.ifft`. **Todo lo demás se implementa a mano** sobre
> NumPy. `scipy.signal` aparece **SOLO en los tests** (`backend/tests/`) como
> oráculo de validación; **nunca** en `spectra_dsp/` ni en `api/`.

Si se añade código DSP nuevo: implementarlo a mano, con docstring que incluya la
fórmula y la referencia al capítulo de Oppenheim, y validarlo en un test contra
scipy si aplica.

## Estructura

```
spectra/
  backend/
    spectra_dsp/      # MOTOR DSP propio (núcleo académico, solo NumPy)
      preprocessing.py windows.py welch.py entropy.py autocorr.py
      cross_spectrum.py stft.py fir.py ifft_filter.py cycle_phase.py metrics.py
    data/
      config.py       # tickers, épocas, fechas, FS=1.0
      loader.py       # descarga/caché yfinance -> CSV, segmentación por época
      raw/            # CSV cacheados (generados; .gitignore los ignora)
    api/
      main.py routes.py schemas.py analysis.py interpret.py
    tests/            # pytest (test_welch, test_coherence, test_parseval, ...)
    requirements.txt  pyproject.toml  Dockerfile
    .venv/            # entorno virtual (ya creado)
  frontend/
    src/
      components/ (Controls, Panel1Time, Panel2Spectral, Panel3Coherence,
                   Panel4Summary, ComparisonView, RegimeGauge, Plot, ...)
      api/client.ts  hooks/useAnalysis.ts  types.ts  theme.ts  App.tsx
    package.json  vite.config.ts  Dockerfile  nginx.conf
  docs/TECHNICAL.md   # matemática + mapeo a Oppenheim + resultados + limitaciones
  docker-compose.yml  README.md  ejecutar.md  CLAUDE.md
```

## Convenciones y decisiones

- **Idioma**: UI y documentación en **español**; código e identificadores en **inglés**.
- **Datos**: solo yfinance real (sin fallback sintético). `auto_adjust=True`
  (cierre ajustado). Si falla la descarga, el loader lanza `RuntimeError` con
  instrucción de reintento.
- **Frecuencia**: `FS = 1.0` muestra/día de trading → frecuencias en ciclos/día,
  periodos en días.
- **Análisis** sobre la serie de **retornos logarítmicos** con la media (DC) removida.

## Entorno de la máquina del usuario

- **Python 3.14.4** (no hay 3.12). numpy/pandas/scipy/yfinance/fastapi instalan bien.
- **Node 26 / npm 11.16**. Vite 5.
- **Docker NO está instalado** → `docker-compose.yml` + Dockerfiles son entregable
  **no probado en esta máquina**; la verificación real es local (venv + npm).

## Gotchas / aprendizajes (importante para continuar)

- **El sandbox bloquea el spawn de procesos servidor** (`EPERM: uv_spawn` con
  `Start-Process`, uvicorn en background, etc.). Para verificar la API NO levantes
  uvicorn: usa `fastapi.testclient.TestClient` en proceso (así se validó).
- **PYTHONPATH**: los scripts sueltos necesitan `$env:PYTHONPATH="."` desde
  `backend/`. `pytest` ya lo resuelve vía `pyproject.toml` (`pythonpath=["."]`).
- **Coherencia**: debe calcularse con `nperseg ≈ N/4` de la serie para tener varios
  segmentos; con un solo segmento la coherencia es idénticamente 1 (ya corregido en
  `api/analysis.py`, función `analyze`).
- **Régimen "Ruidoso" en todos los casos es correcto**: los retornos diarios son
  casi ruido blanco (mercado eficiente). La narrativa la cuentan la **volatilidad**
  y la **coherencia**, no un ciclo dominante (cuya confianza es baja a propósito).
- **Bundle grande de Plotly** (~4.8 MB): la advertencia de tamaño en `npm run build`
  es esperada, no es un error.

## Lanzador automático

`main.py` (raíz) es un lanzador multiplataforma: verifica prerrequisitos
(Python 3.12+, Node 18+, npm), prepara automáticamente lo que falte (venv,
dependencias backend/frontend, descarga de datos) y arranca ambos servidores
abriendo el dashboard en el navegador. Uso: `python main.py`. La fase de
verificación/preparación está probada; el arranque de servidores no se puede
probar desde el sandbox de Claude (EPERM), pero usa `subprocess.Popen` estándar.

## Comandos rápidos

```powershell
# Lanzador todo-en-uno (en tu terminal)
python main.py

# Backend: tests
cd backend; .\.venv\Scripts\python.exe -m pytest

# Backend: API (en tu terminal; no funciona desde el sandbox de Claude)
cd backend; .\.venv\Scripts\Activate.ps1; uvicorn api.main:app --reload --port 8000

# Frontend
cd frontend; npm run dev      # http://localhost:5173
cd frontend; npm run build    # genera dist/

# Regenerar datos
cd backend; .\.venv\Scripts\python.exe -m data.loader
```

## Resultados clave (datos reales, N=1024, Hanning)

| Caso | Volatilidad | Coherencia vs SPY | Lectura |
|---|---|---|---|
| AAL / durante | 0.0508 (máx) | 0.12 (desacople) | aerolíneas en crisis |
| NFLX / después | 0.0373 | 0.82 (re-acople) | tras el auge del streaming |
| SPY / antes | 0.0093 (mín) | benchmark | mercado agregado |

## Posibles mejoras futuras (no implementadas)

- Restringir la búsqueda del ciclo dominante a una banda de periodos "razonable"
  (p. ej. 5–250 días) para que `argmax` sobre ruido no caiga cerca de Nyquist.
- Code-splitting del bundle de Plotly para reducir el tamaño.
- Persistir la caché de `_CACHE` (en `api/analysis.py`) a disco entre reinicios.
