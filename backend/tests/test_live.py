"""Tests del modo en vivo (intradía).

La descarga real de yfinance no se prueba aquí (depende de la red y del horario
de mercado). En su lugar se inyectan barras sintéticas directamente en el caché
TTL de ``live_loader``, de modo que ``_fetch`` las sirva sin tocar internet. Esto
ejercita el endpoint completo (``compute_analysis`` + esquema de respuesta).
"""

import time

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import app
from data import live_loader

client = TestClient(app)


def _synthetic_bars(seed: int, n: int = 600) -> pd.DataFrame:
    """DataFrame con índice de 1 min y una columna Close (paseo + ciclo + ruido)."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-02 09:30", periods=n, freq="1min")
    t = np.arange(n)
    cycle = 0.002 * np.sin(2 * np.pi * t / 30.0)  # ciclo de ~30 min
    noise = 0.001 * rng.standard_normal(n)
    log_price = np.cumsum(cycle + noise) + np.log(100.0)
    return pd.DataFrame({"Close": np.exp(log_price)}, index=idx)


@pytest.fixture
def _seed_cache():
    """Inyecta barras sintéticas para SPY (benchmark) y una acción de prueba."""
    now = time.time()
    live_loader._CACHE["SPY"] = (now, _synthetic_bars(1))
    live_loader._CACHE["AAPL"] = (now, _synthetic_bars(2))
    yield
    live_loader._CACHE.clear()


def test_live_assets():
    r = client.get("/live/assets")
    assert r.status_code == 200
    tickers = {a["ticker"] for a in r.json()}
    assert "SPY" in tickers
    assert {"AAPL", "NVDA", "TSLA"} <= tickers


def test_live_analyze_basic(_seed_cache):
    r = client.post("/live/analyze", json={"asset": "AAPL", "N": 256})
    assert r.status_code == 200
    data = r.json()
    assert data["asset"] == "AAPL"
    assert data["epoch"] == "live"
    # Unidades intradía en la respuesta.
    assert data["units"]["freq"] == "ciclos/min"
    assert data["units"]["period"] == "min"
    assert data["last_updated"] is not None
    assert data["summary"]["benchmark"] == "SPY"
    assert 0.0 <= data["summary"]["coherence_at_dom"] <= 1.0
    assert data["summary"]["period_days"] > 0
    assert "minutos" in data["summary"]["interpretation"]


def test_live_analyze_benchmark_self_coherence(_seed_cache):
    r = client.post("/live/analyze", json={"asset": "SPY", "N": 256})
    assert r.status_code == 200
    assert r.json()["summary"]["coherence_at_dom"] == 1.0


def test_live_analyze_invalid_asset(_seed_cache):
    r = client.post("/live/analyze", json={"asset": "NOPE", "N": 256})
    assert r.status_code == 400
