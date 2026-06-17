"""Descarga, caché y segmentación de los datos del estudio.

Los datos se descargan **una sola vez** desde Yahoo Finance (vía ``yfinance``)
con ``auto_adjust=True`` (precios de cierre ajustados) y se cachean en CSV
locales en ``data/raw/``. A partir de ahí el dashboard funciona sin depender de
internet. Si la descarga falla (sin red, rate-limit), se lanza un ``RuntimeError``
con instrucciones de reintento.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import config

RAW_DIR = Path(__file__).resolve().parent / "raw"

# Mínimo de muestras por época para que el análisis (y especialmente la coherencia
# de Welch, que necesita varios segmentos) tenga sentido.
MIN_SAMPLES_PER_EPOCH: int = 200


def _safe_name(ticker: str) -> str:
    """Nombre de archivo seguro para un ticker.

    Los tickers internacionales incluyen caracteres como ``^`` (índices) o ``.``
    (sufijo de bolsa, p. ej. ``2330.TW``). Se reemplaza cualquier carácter no
    alfanumérico por ``_``. Los tickers de EE.UU. (``SPY``/``AAL``/``NFLX``) son
    alfanuméricos, por lo que su caché existente no cambia.
    """
    return re.sub(r"[^0-9A-Za-z]", "_", ticker)


def _csv_path(ticker: str) -> Path:
    return RAW_DIR / f"{_safe_name(ticker)}.csv"


def download_all(force: bool = False) -> dict[str, Path]:
    """Descarga el rango completo de cada activo y lo cachea en CSV.

    Parameters
    ----------
    force:
        Si ``True``, vuelve a descargar aunque exista el caché.

    Returns
    -------
    dict que mapea ticker -> ruta del CSV cacheado.
    """
    import yfinance as yf

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    for ticker in config.asset_keys():
        path = _csv_path(ticker)
        if path.exists() and not force:
            paths[ticker] = path
            continue

        try:
            df = yf.download(
                ticker,
                start=config.FULL_START,
                end=config.FULL_END,
                auto_adjust=True,
                progress=False,
            )
        except Exception as exc:  # noqa: BLE001 - se re-lanza con contexto
            raise RuntimeError(
                f"No se pudo descargar '{ticker}' desde Yahoo Finance: {exc}. "
                "Verifica tu conexión a internet y reintenta "
                "(p. ej. `python -m data.loader`)."
            ) from exc

        if df is None or df.empty:
            raise RuntimeError(
                f"Yahoo Finance devolvió datos vacíos para '{ticker}'. "
                "Puede ser un rate-limit temporal; reintenta en unos minutos."
            )

        # yfinance puede devolver columnas MultiIndex (Price, Ticker); las aplanamos.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df.to_csv(path, index=False)
        paths[ticker] = path

    return paths


def load_series(ticker: str) -> pd.DataFrame:
    """Carga el OHLCV diario cacheado de un ticker (descarga si no existe).

    Devuelve un ``DataFrame`` indexado por fecha con al menos la columna
    ``Close`` (precio ajustado, porque se descargó con ``auto_adjust=True``).
    """
    if ticker not in config.ASSETS:
        raise KeyError(f"Ticker desconocido: {ticker}. Válidos: {config.asset_keys()}")

    path = _csv_path(ticker)
    if not path.exists():
        download_all()

    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.set_index("Date").sort_index()
    return df


def segment(df: pd.DataFrame, epoch: str) -> pd.DataFrame:
    """Recorta un ``DataFrame`` indexado por fecha al rango de la época dada."""
    if epoch not in config.EPOCHS:
        raise KeyError(f"Época desconocida: {epoch}. Válidas: {config.epoch_keys()}")
    ep = config.EPOCHS[epoch]
    mask = (df.index >= pd.Timestamp(ep.start)) & (df.index <= pd.Timestamp(ep.end))
    return df.loc[mask]


def get_prices(ticker: str, epoch: str) -> pd.Series:
    """Serie de precios de cierre ajustados para un (activo, época)."""
    df = segment(load_series(ticker), epoch)
    return df["Close"].astype(float)


def get_returns(ticker: str, epoch: str) -> tuple[pd.DatetimeIndex, np.ndarray]:
    """Retornos logarítmicos diarios de un (activo, época).

    Returns
    -------
    (dates, returns) donde ``dates`` son las fechas de los retornos (una menos
    que los precios, por la diferencia) y ``returns`` el array NumPy de
    ``r[n] = ln(P[n]/P[n-1])``.
    """
    prices = get_prices(ticker, epoch)
    log_p = np.log(prices.to_numpy())
    returns = np.diff(log_p)
    dates = prices.index[1:]
    return dates, returns


def validate_coverage() -> dict[str, dict[str, int]]:
    """Verifica que cada (ticker, época) supera ``MIN_SAMPLES_PER_EPOCH``.

    Devuelve un dict ticker -> {época: nº de muestras}. Lanza ``RuntimeError`` si
    algún par queda por debajo del mínimo (hueco de datos que invalidaría el
    análisis).
    """
    report: dict[str, dict[str, int]] = {}
    problems: list[str] = []
    for ticker in config.asset_keys():
        df = load_series(ticker)
        counts: dict[str, int] = {}
        for epoch in config.epoch_keys():
            n = len(segment(df, epoch))
            counts[epoch] = n
            if n < MIN_SAMPLES_PER_EPOCH:
                problems.append(f"{ticker}/{epoch}: {n} < {MIN_SAMPLES_PER_EPOCH}")
        report[ticker] = counts
    if problems:
        raise RuntimeError(
            "Cobertura insuficiente de datos en: " + "; ".join(problems)
        )
    return report


if __name__ == "__main__":  # pragma: no cover - utilidad de línea de comandos
    print("Descargando datos de Yahoo Finance (una sola vez)...")
    for ticker, path in download_all().items():
        df = pd.read_csv(path)
        print(f"  {ticker}: {len(df)} filas -> {path}")
    print("Validando cobertura por época...")
    report = validate_coverage()
    for ticker, counts in report.items():
        c = " ".join(f"{e}={n}" for e, n in counts.items())
        print(f"  {ticker}: {c}")
    print("Listo.")
