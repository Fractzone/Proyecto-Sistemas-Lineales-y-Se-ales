"""Descarga intradía en vivo para el modo *en vivo* de SPECTRA.

A diferencia de ``loader.py`` (que descarga una sola vez el rango 2018-2023 y lo
cachea en CSV), aquí se descargan las **barras de 1 minuto recientes** de Yahoo
Finance cada vez que el cliente refresca, con un pequeño **caché TTL en memoria**
para no saturar yfinance (rate-limit) cuando varias peticiones llegan juntas.

El motor DSP es agnóstico de la fuente: estas funciones devuelven precios y
retornos logarítmicos en el mismo formato que ``loader.get_prices`` /
``loader.get_returns``, pero indexados por *timestamp* intradía en lugar de fecha.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from . import live_config
from .loader import MIN_SAMPLES_PER_EPOCH

# Caché TTL en memoria: ticker -> (fetched_at_epoch, DataFrame con columna Close).
# El cliente refresca cada 60 s; un TTL de 55 s sirve datos frescos sin volver a
# descargar dentro de la misma ráfaga de peticiones (activo + benchmark).
_TTL_SECONDS: float = 55.0
_CACHE: dict[str, tuple[float, pd.DataFrame]] = {}


def _fetch(ticker: str) -> pd.DataFrame:
    """Descarga (o sirve desde el caché TTL) las barras intradía de un ticker."""
    now = time.time()
    cached = _CACHE.get(ticker)
    if cached is not None and (now - cached[0]) < _TTL_SECONDS:
        return cached[1]

    import yfinance as yf

    try:
        df = yf.Ticker(ticker).history(
            period=live_config.LIVE_PERIOD,
            interval=live_config.LIVE_INTERVAL,
            auto_adjust=True,
        )
    except Exception as exc:  # noqa: BLE001 - se re-lanza con contexto
        raise RuntimeError(
            f"No se pudieron descargar las barras en vivo de '{ticker}' desde "
            f"Yahoo Finance: {exc}. Verifica tu conexión y reintenta."
        ) from exc

    if df is None or df.empty or "Close" not in df.columns:
        raise RuntimeError(
            f"Yahoo Finance no devolvió barras intradía para '{ticker}'. "
            "Puede ser un rate-limit temporal o un ticker sin datos en vivo; "
            "reintenta en unos minutos."
        )

    df = df[["Close"]].dropna()
    if len(df) < MIN_SAMPLES_PER_EPOCH:
        raise RuntimeError(
            f"Muestras intradía insuficientes para '{ticker}': {len(df)} < "
            f"{MIN_SAMPLES_PER_EPOCH}. Prueba con otra acción o más tarde "
            "(fuera del horario de mercado yfinance entrega pocas barras)."
        )

    _CACHE[ticker] = (now, df)
    return df


def get_live_prices(ticker: str) -> pd.Series:
    """Serie de precios de cierre intradía (índice = timestamps de 1 min)."""
    if ticker not in live_config.LIVE_ASSETS:
        raise KeyError(
            f"Acción en vivo desconocida: {ticker}. "
            f"Válidas: {live_config.live_asset_keys()}"
        )
    return _fetch(ticker)["Close"].astype(float)


def get_live_returns(ticker: str) -> tuple[pd.DatetimeIndex, np.ndarray]:
    """Retornos logarítmicos intradía de un ticker.

    Returns
    -------
    (timestamps, returns) con ``r[n] = ln(P[n]/P[n-1])`` y los timestamps de los
    retornos (uno menos que los precios), igual que ``loader.get_returns``.
    """
    prices = get_live_prices(ticker)
    log_p = np.log(prices.to_numpy())
    returns = np.diff(log_p)
    dates = prices.index[1:]
    return dates, returns


def get_aligned_live_returns(
    ticker: str, benchmark: str
) -> tuple[np.ndarray, np.ndarray]:
    """Retornos de ``ticker`` y del ``benchmark`` alineados por timestamp común.

    Espejo intradía de ``analysis._aligned_returns`` (que alinea por fecha): la
    coherencia exige que ambas series compartan exactamente las mismas barras.
    """
    da, ra = get_live_returns(ticker)
    db, rb = get_live_returns(benchmark)
    common = da.intersection(db)
    ia = da.isin(common)
    ib = db.isin(common)
    return ra[ia], rb[ib]
