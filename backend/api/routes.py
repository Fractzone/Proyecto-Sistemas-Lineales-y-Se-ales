"""Endpoints de la API de SPECTRA."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from data import config, live_config

from . import analysis, schemas

router = APIRouter()


def _asset_info(a: config.Asset) -> schemas.AssetInfo:
    return schemas.AssetInfo(
        ticker=a.ticker,
        name=a.name,
        role=a.role,
        kind=a.kind,
        market=config.market_of(a.ticker),
    )


@router.get("/assets", response_model=list[schemas.AssetInfo])
def get_assets() -> list[schemas.AssetInfo]:
    return [_asset_info(a) for a in config.ASSETS.values()]


@router.get("/markets", response_model=list[schemas.MarketInfo])
def get_markets() -> list[schemas.MarketInfo]:
    return [
        schemas.MarketInfo(
            code=m.code,
            name=m.name,
            lat=m.lat,
            lon=m.lon,
            benchmark=m.benchmark,
            assets=[_asset_info(a) for a in m.assets],
        )
        for m in config.MARKETS.values()
    ]


@router.get("/epochs", response_model=list[schemas.EpochInfo])
def get_epochs() -> list[schemas.EpochInfo]:
    return [
        schemas.EpochInfo(key=e.key, label=e.label, start=e.start, end=e.end)
        for e in config.EPOCHS.values()
    ]


@router.post("/analyze", response_model=schemas.AnalyzeResponse)
def post_analyze(req: schemas.AnalyzeRequest) -> schemas.AnalyzeResponse:
    try:
        return analysis.analyze(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:  # error de datos (descarga)
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/compare", response_model=schemas.CompareResponse)
def post_compare(req: schemas.CompareRequest) -> schemas.CompareResponse:
    try:
        return analysis.compare(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/live/assets", response_model=list[schemas.AssetInfo])
def get_live_assets() -> list[schemas.AssetInfo]:
    """Catálogo curado de acciones US para el modo en vivo (SPY = benchmark)."""
    return [
        schemas.AssetInfo(
            ticker=a.ticker,
            name=a.name,
            role=a.role,
            kind=a.kind,
            market="US",
        )
        for a in live_config.LIVE_ASSETS.values()
    ]


@router.post("/live/analyze", response_model=schemas.AnalyzeResponse)
def post_live_analyze(req: schemas.LiveAnalyzeRequest) -> schemas.AnalyzeResponse:
    try:
        return analysis.analyze_live(req)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:  # error de datos (descarga en vivo)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
