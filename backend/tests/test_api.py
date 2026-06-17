"""Tests de los endpoints de la API (FastAPI TestClient)."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_assets():
    r = client.get("/assets")
    assert r.status_code == 200
    tickers = {a["ticker"] for a in r.json()}
    # Los activos de EE.UU. siguen presentes dentro del registro global.
    assert {"SPY", "AAL", "NFLX"} <= tickers


def test_markets():
    r = client.get("/markets")
    assert r.status_code == 200
    markets = r.json()
    codes = {m["code"] for m in markets}
    assert {"US", "GB", "TW"} <= codes
    us = next(m for m in markets if m["code"] == "US")
    assert us["benchmark"] == "SPY"
    assert len(us["assets"]) == 3
    # Cada mercado tiene exactamente un activo general.
    for m in markets:
        generals = [a for a in m["assets"] if a["kind"] == "general"]
        assert len(generals) == 1
        assert generals[0]["ticker"] == m["benchmark"]


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


def test_analyze_non_us_market():
    # Activo de contraste del Reino Unido: la coherencia se calcula contra ^FTSE.
    r = client.post(
        "/analyze",
        json={"asset": "IAG.L", "epoch": "durante", "N": 512, "window": "hanning"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["asset"] == "IAG.L"
    assert data["summary"]["benchmark"] == "^FTSE"
    # Al no ser el benchmark, la coherencia no es trivialmente 1.
    assert data["summary"]["coherence_at_dom"] != 1.0
    assert 0.0 <= data["summary"]["coherence_at_dom"] <= 1.0


def test_analyze_non_us_benchmark_self_coherence():
    r = client.post("/analyze", json={"asset": "^FTSE", "epoch": "antes", "N": 512})
    assert r.status_code == 200
    assert r.json()["summary"]["coherence_at_dom"] == 1.0
    assert r.json()["summary"]["benchmark"] == "^FTSE"


def test_compare_epoch_assets():
    r = client.post(
        "/compare", json={"mode": "epoch_assets", "epoch": "durante", "market": "US"}
    )
    assert r.status_code == 200
    rows = r.json()["rows"]
    assert {row["asset"] for row in rows} == {"SPY", "AAL", "NFLX"}


def test_compare_epoch_assets_non_us():
    r = client.post(
        "/compare", json={"mode": "epoch_assets", "epoch": "durante", "market": "GB"}
    )
    assert r.status_code == 200
    rows = r.json()["rows"]
    assert {row["asset"] for row in rows} == {"^FTSE", "IAG.L", "OCDO.L"}


def test_compare_epoch_assets_requires_market():
    r = client.post("/compare", json={"mode": "epoch_assets", "epoch": "durante"})
    assert r.status_code == 400


def test_compare_asset_epochs():
    r = client.post("/compare", json={"mode": "asset_epochs", "asset": "NFLX"})
    assert r.status_code == 200
    rows = r.json()["rows"]
    assert {row["epoch"] for row in rows} == {"antes", "durante", "despues"}
