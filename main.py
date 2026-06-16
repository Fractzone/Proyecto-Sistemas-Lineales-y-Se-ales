#!/usr/bin/env python3
"""Lanzador único de SPECTRA.

Ejecuta `python main.py` desde la raíz del proyecto. El script:

  1. Verifica los prerrequisitos (Python 3.12+, Node 18+, npm). Si falta alguno,
     muestra qué instalar y dónde, y se detiene.
  2. Prepara automáticamente lo que falte: entorno virtual, dependencias del
     backend, descarga/caché de datos y dependencias del frontend.
  3. Levanta el backend (FastAPI/uvicorn) y el frontend (Vite), espera a que
     estén listos y abre el dashboard en el navegador.

Pulsa Ctrl+C para detener ambos servidores.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
RAW_DIR = BACKEND / "data" / "raw"

BACKEND_PORT = 8000
FRONTEND_PORT = 5173
BACKEND_URL = f"http://localhost:{BACKEND_PORT}/assets"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

IS_WINDOWS = platform.system() == "Windows"
TICKERS = ("SPY", "AAL", "NFLX")

MIN_PYTHON = (3, 12)
MIN_NODE = 18


# --------------------------------------------------------------------------- #
# Utilidades de salida
# --------------------------------------------------------------------------- #
def _supports_color() -> bool:
    return sys.stdout.isatty() and not IS_WINDOWS or os.environ.get("FORCE_COLOR")


_C = {
    "head": "\033[1;36m",
    "ok": "\033[1;32m",
    "warn": "\033[1;33m",
    "err": "\033[1;31m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}
if not _supports_color():
    _C = {k: "" for k in _C}


def head(msg: str) -> None:
    print(f"\n{_C['head']}=== {msg} ==={_C['reset']}")


def ok(msg: str) -> None:
    print(f"{_C['ok']}[OK]{_C['reset']} {msg}")


def info(msg: str) -> None:
    print(f"{_C['dim']} ->{_C['reset']} {msg}")


def warn(msg: str) -> None:
    print(f"{_C['warn']}[!] {msg}{_C['reset']}")


def fail(msg: str) -> None:
    print(f"{_C['err']}[X] {msg}{_C['reset']}")


def die(msg: str, instructions: str = "") -> None:
    fail(msg)
    if instructions:
        print(instructions)
    sys.exit(1)


# --------------------------------------------------------------------------- #
# Rutas dependientes de la plataforma
# --------------------------------------------------------------------------- #
def venv_python() -> Path:
    if IS_WINDOWS:
        return BACKEND / ".venv" / "Scripts" / "python.exe"
    return BACKEND / ".venv" / "bin" / "python"


def find_npm() -> str | None:
    return shutil.which("npm")


def find_node() -> str | None:
    return shutil.which("node")


def run(cmd: list[str], cwd: Path, what: str) -> None:
    """Ejecuta un comando mostrando su salida; aborta si falla."""
    info(f"{what}…")
    try:
        subprocess.run(cmd, cwd=str(cwd), check=True)
    except subprocess.CalledProcessError:
        die(f"Falló: {what}", f"Comando: {' '.join(cmd)}")


# --------------------------------------------------------------------------- #
# 1. Verificación de prerrequisitos
# --------------------------------------------------------------------------- #
def check_project_layout() -> None:
    head("Verificando estructura del proyecto")
    if not BACKEND.is_dir() or not FRONTEND.is_dir():
        die(
            "No encuentro las carpetas backend/ y frontend/.",
            "Ejecuta este script desde la raíz del proyecto SPECTRA.",
        )
    ok("Carpetas backend/ y frontend/ encontradas.")


def check_python() -> None:
    head("Verificando Python")
    if sys.version_info < MIN_PYTHON:
        die(
            f"Python {sys.version_info.major}.{sys.version_info.minor} detectado; "
            f"se requiere {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+.",
            "Instala una versión reciente desde https://www.python.org/downloads/\n"
            "y vuelve a ejecutar: python main.py",
        )
    ok(f"Python {sys.version_info.major}.{sys.version_info.minor} (suficiente).")


def check_node() -> None:
    head("Verificando Node.js y npm")
    node = find_node()
    npm = find_npm()
    if not node or not npm:
        die(
            "No se encontró Node.js / npm en el PATH.",
            "Instálalos desde https://nodejs.org/ (versión 18 o superior).\n"
            "Después cierra y reabre la terminal y vuelve a ejecutar: python main.py",
        )
    try:
        ver = subprocess.run(
            [node, "--version"], capture_output=True, text=True, check=True
        ).stdout.strip()
        major = int(ver.lstrip("v").split(".")[0])
        if major < MIN_NODE:
            die(
                f"Node {ver} detectado; se requiere v{MIN_NODE}+.",
                "Actualiza desde https://nodejs.org/",
            )
        ok(f"Node {ver} y npm encontrados.")
    except (subprocess.CalledProcessError, ValueError):
        warn("No se pudo leer la versión de Node, pero existe en el PATH. Se continúa.")


# --------------------------------------------------------------------------- #
# 2. Preparación automática del entorno
# --------------------------------------------------------------------------- #
def ensure_backend() -> None:
    head("Preparando el backend")

    # Entorno virtual
    if not venv_python().exists():
        info("No existe el entorno virtual; creándolo…")
        run([sys.executable, "-m", "venv", ".venv"], BACKEND, "Crear venv")
    else:
        ok("Entorno virtual presente.")

    py = str(venv_python())

    # Dependencias
    check = subprocess.run(
        [py, "-c", "import fastapi, uvicorn, numpy, pandas, yfinance"],
        capture_output=True,
    )
    if check.returncode != 0:
        info("Instalando dependencias del backend (puede tardar la primera vez)…")
        run([py, "-m", "pip", "install", "--upgrade", "pip"], BACKEND, "Actualizar pip")
        run([py, "-m", "pip", "install", "-r", "requirements.txt"], BACKEND,
            "Instalar requirements")
    else:
        ok("Dependencias del backend instaladas.")

    # Datos cacheados
    missing = [t for t in TICKERS if not (RAW_DIR / f"{t}.csv").exists()]
    if missing:
        warn(f"Faltan datos cacheados ({', '.join(missing)}). Descargando de Yahoo Finance…")
        info("Esto requiere conexión a internet (solo la primera vez).")
        try:
            subprocess.run([py, "-m", "data.loader"], cwd=str(BACKEND), check=True)
        except subprocess.CalledProcessError:
            die(
                "No se pudieron descargar los datos.",
                "Verifica tu conexión a internet y vuelve a ejecutar: python main.py",
            )
    else:
        ok("Datos cacheados presentes (SPY, AAL, NFLX).")


def ensure_frontend() -> None:
    head("Preparando el frontend")
    if not (FRONTEND / "node_modules").is_dir():
        info("No existe node_modules; instalando dependencias del frontend…")
        npm = find_npm()
        run([npm, "install"], FRONTEND, "npm install")
    else:
        ok("Dependencias del frontend instaladas.")


# --------------------------------------------------------------------------- #
# 3. Arranque de los servidores
# --------------------------------------------------------------------------- #
def _popen(cmd: list[str], cwd: Path) -> subprocess.Popen:
    kwargs: dict = {"cwd": str(cwd)}
    if IS_WINDOWS:
        # Grupo de procesos propio para poder terminar el árbol al cerrar.
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(cmd, **kwargs)


def wait_for(url: str, timeout: float, label: str) -> bool:
    info(f"Esperando a que {label} responda…")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status < 500:
                    return True
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        time.sleep(1)
    return False


def terminate(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        if IS_WINDOWS:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                capture_output=True,
            )
        else:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    except Exception:  # noqa: BLE001
        pass


def launch() -> None:
    head("Arrancando SPECTRA")
    py = str(venv_python())
    npm = find_npm()

    backend_proc: subprocess.Popen | None = None
    frontend_proc: subprocess.Popen | None = None

    try:
        info(f"Backend  → http://localhost:{BACKEND_PORT}  (docs en /docs)")
        backend_proc = _popen(
            [py, "-m", "uvicorn", "api.main:app", "--port", str(BACKEND_PORT)],
            BACKEND,
        )

        if not wait_for(BACKEND_URL, timeout=60, label="el backend"):
            die("El backend no respondió a tiempo.")
        ok("Backend listo.")

        info(f"Frontend → {FRONTEND_URL}")
        frontend_proc = _popen([npm, "run", "dev"], FRONTEND)

        if not wait_for(FRONTEND_URL, timeout=90, label="el frontend"):
            warn("El frontend tardó en responder; intenta abrir manualmente la URL.")
        else:
            ok("Frontend listo.")

        head("SPECTRA en marcha")
        print(f"  Dashboard: {_C['ok']}{FRONTEND_URL}{_C['reset']}")
        print(f"  API docs:  http://localhost:{BACKEND_PORT}/docs")
        print(f"\n{_C['dim']}Abriendo el navegador… (Ctrl+C para detener){_C['reset']}")
        webbrowser.open(FRONTEND_URL)

        # Mantener vivo hasta Ctrl+C o hasta que un proceso muera.
        while True:
            if backend_proc.poll() is not None:
                fail("El backend se detuvo inesperadamente.")
                break
            if frontend_proc.poll() is not None:
                fail("El frontend se detuvo inesperadamente.")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n{_C['dim']}Deteniendo SPECTRA…{_C['reset']}")
    finally:
        terminate(frontend_proc)
        terminate(backend_proc)
        ok("Servidores detenidos. ¡Hasta luego!")


# --------------------------------------------------------------------------- #
# Flujo principal
# --------------------------------------------------------------------------- #
def main() -> None:
    print(f"{_C['head']}")
    print("  ███ SPECTRA — Lanzador automático")
    print(f"  Análisis espectral de activos · Sistemas Lineales y Señales{_C['reset']}")

    check_project_layout()
    check_python()
    check_node()
    ensure_backend()
    ensure_frontend()
    launch()


if __name__ == "__main__":
    main()
