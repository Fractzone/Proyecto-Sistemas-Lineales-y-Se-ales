# Cómo ejecutar SPECTRA en cualquier computador

Guía paso a paso para poner en marcha el proyecto desde cero. Hay **dos formas**:
ejecución **local** (recomendada, más simple de verificar) y con **Docker**.

---

## 0. Requisitos previos

Instala estas herramientas (una sola vez por computador):

| Herramienta | Versión mínima | Verificar con | Descarga |
|---|---|---|---|
| **Python** | 3.12+ (probado en 3.14) | `python --version` | <https://www.python.org/downloads/> |
| **Node.js** | 18+ (probado en 26) | `node --version` | <https://nodejs.org/> |
| **Git** (opcional) | cualquiera | `git --version` | <https://git-scm.com/> |

- Se necesita **conexión a internet la PRIMERA vez** (para descargar los datos de
  Yahoo Finance). Después funciona sin internet usando el caché en CSV.
- En Windows, si `python` no funciona prueba con `py`.

---

## 1. Obtener el proyecto

Copia la carpeta `spectra/` al computador (o clónala si está en un repositorio).
Todos los comandos siguientes se ejecutan **dentro** de esa carpeta.

---

## ⭐ Forma más fácil: el lanzador automático

Una vez instalados Python y Node (paso 0), ejecuta **un solo comando** desde la
raíz del proyecto:

```bash
cd spectra
python main.py        # en algunos sistemas: py main.py  o  python3 main.py
```

`main.py` se encarga de todo:
1. Verifica que tengas Python 3.12+, Node 18+ y npm. Si falta algo, te dice
   **exactamente qué instalar y dónde**.
2. Crea el entorno virtual, instala las dependencias del backend y del frontend,
   y descarga los datos (todo solo la primera vez).
3. Levanta el backend y el frontend y **abre el dashboard en el navegador**
   automáticamente.

Para detener todo: pulsa `Ctrl + C` en esa terminal.

> Si prefieres hacerlo manualmente o el lanzador falla, usa los pasos detallados
> de las secciones 2 y 3.

---

## 2. Ejecución LOCAL manual (paso a paso)

Necesitas **dos terminales**: una para el backend y otra para el frontend.

### 2.1 Terminal 1 — Backend (API + motor DSP)

```bash
cd spectra/backend

# 1) Crear el entorno virtual de Python
python -m venv .venv

# 2) Activarlo
#    Windows (PowerShell):
.venv\Scripts\Activate.ps1
#    Windows (CMD):
#    .venv\Scripts\activate.bat
#    Linux / macOS:
#    source .venv/bin/activate

# 3) Instalar dependencias
pip install -r requirements.txt

# 4) Descargar y cachear los datos (SOLO la primera vez; requiere internet)
python -m data.loader

# 5) (Opcional pero recomendado) correr los tests: deben pasar 40
pytest

# 6) Levantar la API en http://localhost:8000   (documentación en /docs)
uvicorn api.main:app --reload --port 8000
```

> Deja esta terminal abierta con el servidor corriendo.

### 2.2 Terminal 2 — Frontend (dashboard)

```bash
cd spectra/frontend

# 1) Instalar dependencias
npm install

# 2) Levantar el servidor de desarrollo
npm run dev
```

Abre el navegador en **<http://localhost:5173>**.

El frontend redirige automáticamente las llamadas `/api` al backend
(`http://localhost:8000`), así que con ambos procesos arriba el dashboard
funciona directamente.

### 2.3 Detener
Pulsa `Ctrl + C` en cada terminal.

---

## 3. Ejecución con DOCKER (alternativa)

Requiere **Docker Desktop** instalado y en ejecución
(<https://www.docker.com/products/docker-desktop/>).

```bash
cd spectra

# Construir y levantar backend + frontend
docker compose up --build
```

- **Dashboard**: <http://localhost:8080>
- **API**: <http://localhost:8000/docs>

La primera vez el backend descarga los datos al iniciar (necesita internet). El
caché queda guardado en un volumen Docker (`spectra_data`).

Para detener: `Ctrl + C`, o en otra terminal `docker compose down`.

---

## 4. Build de producción del frontend (sin Docker)

Si quieres generar los archivos estáticos para servirlos con cualquier servidor:

```bash
cd spectra/frontend
npm run build      # genera la carpeta dist/
npm run preview    # (opcional) previsualiza el build en http://localhost:4173
```

> Nota: aparecerá una advertencia de "chunk grande" por la librería Plotly
> (~4.8 MB). Es **normal**, no es un error.

---

## 5. Uso del dashboard

1. Elige una **época** (Antes / Durante / Después).
2. Elige un **activo** (SPY / AAL / NFLX).
3. Ajusta la **resolución N**, la **ventana** y los **umbrales de entropía**.
4. Observa los 4 paneles: tiempo, espectro (PSD + espectrograma + régimen),
   coherencia con el mercado + autocorrelación, y resumen con interpretación.
5. Activa el **modo comparación** para ver un activo en las 3 épocas o los 3
   activos en una época.

---

## 6. Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| `No module named 'data'` al correr un script suelto | Falta el PYTHONPATH | Ejecuta desde `backend/` con `PYTHONPATH=.` (en PowerShell `$env:PYTHONPATH="."`). Con `pytest` no hace falta. |
| Error de descarga / datos vacíos | Sin internet o rate-limit de Yahoo | Reintenta `python -m data.loader` en unos minutos. |
| El dashboard no carga datos | El backend no está corriendo | Verifica que `uvicorn` esté activo en el puerto 8000. |
| `Activate.ps1 ... no se puede cargar` (Windows) | Política de ejecución de PowerShell | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y reintenta. |
| El puerto 8000 o 5173 está ocupado | Otro proceso lo usa | Cambia el puerto: `uvicorn ... --port 8001` y/o ajusta el proxy en `frontend/vite.config.ts`. |
| `npm install` falla con scripts | Política de scripts de npm reciente | Ejecuta `npm install` de nuevo; si pide aprobar scripts, acéptalos (esbuild los necesita). |

---

## 7. Regenerar el caché de datos

```bash
cd spectra/backend
python -m data.loader                                         # usa caché si existe
python -c "from data.loader import download_all; download_all(force=True)"   # forzar
```
