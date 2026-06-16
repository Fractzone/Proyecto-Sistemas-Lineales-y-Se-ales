"""Constantes del estudio SPECTRA: activos, épocas y parámetros globales.

El estudio analiza tres activos en tres épocas (antes / durante / después de la
pandemia) sobre la serie de retornos logarítmicos diarios. La frecuencia de
muestreo es 1 muestra por día de trading (``FS = 1.0``), por lo que las
frecuencias se expresan en ciclos/día y los periodos en días de trading.
"""

from __future__ import annotations

from dataclasses import dataclass

# Frecuencia de muestreo: datos diarios de trading -> 1 muestra/día.
FS: float = 1.0

# Rango completo descargado una sola vez y cacheado.
FULL_START: str = "2018-01-01"
FULL_END: str = "2023-12-31"


@dataclass(frozen=True)
class Asset:
    ticker: str
    name: str
    role: str


@dataclass(frozen=True)
class Epoch:
    key: str
    label: str
    start: str
    end: str


# Activos del estudio (precios de cierre ajustados, auto_adjust=True).
ASSETS: dict[str, Asset] = {
    "SPY": Asset("SPY", "S&P 500 ETF", "Mercado general (referencia / benchmark de coherencia)"),
    "AAL": Asset("AAL", "American Airlines", "Contraste: colapso del sector aerolíneas en pandemia"),
    "NFLX": Asset("NFLX", "Netflix", "Contraste: auge del streaming y su corrección posterior"),
}

# Benchmark contra el que se calcula la coherencia espectral.
BENCHMARK: str = "SPY"

# Épocas (segmentos de análisis).
EPOCHS: dict[str, Epoch] = {
    "antes": Epoch("antes", "Antes (pre-pandemia)", "2018-01-01", "2020-02-19"),
    "durante": Epoch("durante", "Durante (pandemia)", "2020-02-20", "2021-12-31"),
    "despues": Epoch("despues", "Después (post-pandemia)", "2022-01-01", "2023-12-31"),
}


def asset_keys() -> list[str]:
    return list(ASSETS.keys())


def epoch_keys() -> list[str]:
    return list(EPOCHS.keys())
