"""Constantes del modo *en vivo* de SPECTRA: catálogo de acciones de EE.UU.,
parámetros de descarga intradía y etiquetas de unidad.

El modo en vivo analiza, en casi-tiempo-real, una acción de la bolsa de EE.UU.
sobre barras intradía de 1 minuto de los últimos días (vía ``yfinance``). A
diferencia del estudio estático (diario, por épocas de pandemia), aquí la
frecuencia de muestreo es 1 muestra por *barra de 1 minuto*; internamente se
sigue tratando como ``FS = 1.0`` (ciclos/muestra) para no alterar el motor DSP, y
solo cambian las *etiquetas* (ciclos/min, minutos).

El benchmark de coherencia es SPY (S&P 500 ETF), igual que en el estudio estático
de EE.UU.
"""

from __future__ import annotations

from .config import Asset, KIND_CONTRAST, KIND_GENERAL

# Parámetros de descarga intradía (yfinance). 1m está limitado a ~7 días de
# historia por Yahoo Finance; da del orden de ~2000 barras de mercado regular,
# suficiente para Welch/coherencia (que exigen varios segmentos).
LIVE_INTERVAL: str = "1m"
LIVE_PERIOD: str = "7d"

# Frecuencia de muestreo interna: 1 muestra por barra. Las fórmulas DSP trabajan
# en ciclos/muestra; las etiquetas (LIVE_UNITS) lo traducen a ciclos/min.
LIVE_FS: float = 1.0

# Benchmark de coherencia (referencia del mercado US).
LIVE_BENCHMARK: str = "SPY"

# Etiquetas de unidad para la respuesta en vivo (ver schemas.Units).
LIVE_UNITS: dict[str, str] = {
    "freq": "ciclos/min",
    "period": "min",
    "time": "minutos",
}

# Catálogo curado de acciones US líquidas (buen intradía en yfinance). SPY actúa
# como benchmark; el resto son acciones a analizar. Se reutiliza la dataclass
# ``Asset`` del estudio estático (ticker, name, role, kind).
LIVE_ASSETS: dict[str, Asset] = {
    a.ticker: a
    for a in (
        Asset("SPY", "S&P 500 ETF", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
        Asset("AAPL", "Apple", "Tecnológica de mega-capitalización", KIND_CONTRAST),
        Asset("MSFT", "Microsoft", "Software y nube de mega-capitalización", KIND_CONTRAST),
        Asset("NVDA", "NVIDIA", "Semiconductores / IA, alta volatilidad", KIND_CONTRAST),
        Asset("AMZN", "Amazon", "Comercio electrónico y nube", KIND_CONTRAST),
        Asset("GOOGL", "Alphabet (Google)", "Publicidad y tecnología", KIND_CONTRAST),
        Asset("META", "Meta Platforms", "Redes sociales y publicidad", KIND_CONTRAST),
        Asset("TSLA", "Tesla", "Vehículos eléctricos, alta volatilidad", KIND_CONTRAST),
        Asset("AMD", "Advanced Micro Devices", "Semiconductores", KIND_CONTRAST),
        Asset("JPM", "JPMorgan Chase", "Banca / sector financiero", KIND_CONTRAST),
        Asset("AAL", "American Airlines", "Aerolíneas, sensible al ciclo", KIND_CONTRAST),
        Asset("NFLX", "Netflix", "Streaming y entretenimiento", KIND_CONTRAST),
    )
}


def live_asset_keys() -> list[str]:
    return list(LIVE_ASSETS.keys())
