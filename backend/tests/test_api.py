"""Tests de los endpoints de la API (FastAPI TestClient)."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_assets():
    r = client.get("/assets")
    assert r.status_code == 200
    tickers = {a["ticker"] for a in r.json()}
    assert tickers == {"SPY", "AAL", "NFLX"}


def test_epochs():
    r = client.get("/epochs")
    assert r.status_code == 200
    keys = {e["key"] for e in r.json()}
    assert keys == {"antes", "durante", "despues"}


def test_analyze_basic():
    r = client.post(
        "/analyze",
        json={"asset": "AAL", "epoch": "durante", "N": 512, "window": "hanning"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["asset"] == "AAL"
    assert len(data["spectral"]["freqs"]) == len(data["spectral"]["psd"])
    assert data["summary"]["period_days"] > 0
    assert 0.0 <= data["summary"]["coherence_at_dom"] <= 1.0
    assert "retrospectiva" in data["summary"]["interpretation"].lower()
    # El espectrograma es una matriz freqs x times.
    mat = data["spectral"]["stft_matrix"]
    assert len(mat) == len(data["spectral"]["stft_freqs"])


def test_analyze_benchmark_self_coherence():
    r = client.post("/analyze", json={"asset": "SPY", "epoch": "antes", "N": 512})
    assert r.status_code == 200
    assert r.json()["summary"]["coherence_at_dom"] == 1.0


def test_analyze_invalid_asset():
    r = client.post("/analyze", json={"asset": "TSLA", "epoch": "antes"})
    assert r.status_code == 400


def test_compare_epoch_assets():
    r = client.post("/compare", json={"mode": "epoch_assets", "epoch": "durante"})
    assert r.status_code == 200
    rows = r.json()["rows"]
    assert {row["asset"] for row in rows} == {"SPY", "AAL", "NFLX"}


def test_compare_asset_epochs():
    r = client.post("/compare", json={"mode": "asset_epochs", "asset": "NFLX"})
    assert r.status_code == 200
    rows = r.json()["rows"]
    assert {row["epoch"] for row in rows} == {"antes", "durante", "despues"}
