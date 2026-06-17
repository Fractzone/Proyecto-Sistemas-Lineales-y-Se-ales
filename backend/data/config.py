"""Constantes del estudio SPECTRA: mercados, activos, épocas y parámetros.

El estudio analiza, en cada **mercado** (país), tres activos: un índice/activo
*general* (que actúa como benchmark de coherencia para ese país) y dos acciones
de *contraste* (típicamente la aerolínea de bandera —perdedora en la pandemia— y
un blue-chip/tecnológica —ganadora o resiliente—). El análisis se hace sobre la
serie de retornos logarítmicos diarios en tres épocas (antes / durante / después
de la pandemia). La frecuencia de muestreo es 1 muestra por día de trading
(``FS = 1.0``), por lo que las frecuencias se expresan en ciclos/día y los
periodos en días de trading.
"""

from __future__ import annotations

from dataclasses import dataclass

# Frecuencia de muestreo: datos diarios de trading -> 1 muestra/día.
FS: float = 1.0

# Rango completo descargado una sola vez y cacheado.
FULL_START: str = "2018-01-01"
FULL_END: str = "2023-12-31"

# Roles posibles de un activo dentro de su mercado.
KIND_GENERAL: str = "general"
KIND_CONTRAST: str = "contrast"


@dataclass(frozen=True)
class Asset:
    ticker: str
    name: str
    role: str
    kind: str  # KIND_GENERAL | KIND_CONTRAST


@dataclass(frozen=True)
class Epoch:
    key: str
    label: str
    start: str
    end: str


@dataclass(frozen=True)
class Market:
    code: str  # ISO-ish: "US", "GB", "TW", ...
    name: str
    lat: float
    lon: float
    benchmark: str  # ticker del activo general (referencia de coherencia)
    assets: tuple[Asset, ...]  # (general, contraste1, contraste2)


# Mercados del estudio. El primer activo de cada mercado es el general (benchmark);
# los otros dos son los contrastes (aerolínea de bandera + ganador/blue-chip).
# Coordenadas aproximadas de la plaza financiera del país (para el globo).
MARKETS: dict[str, Market] = {
    "US": Market(
        "US", "Estados Unidos", 40.71, -74.01, "SPY",
        (
            Asset("SPY", "S&P 500 ETF", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("AAL", "American Airlines", "Contraste: colapso del sector aerolíneas en pandemia", KIND_CONTRAST),
            Asset("NFLX", "Netflix", "Contraste: auge del streaming y su corrección posterior", KIND_CONTRAST),
        ),
    ),
    "GB": Market(
        "GB", "Reino Unido", 51.51, -0.13, "^FTSE",
        (
            Asset("^FTSE", "FTSE 100", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("IAG.L", "IAG (British Airways)", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("OCDO.L", "Ocado", "Contraste: comercio electrónico impulsado por la pandemia", KIND_CONTRAST),
        ),
    ),
    "DE": Market(
        "DE", "Alemania", 50.11, 8.68, "^GDAXI",
        (
            Asset("^GDAXI", "DAX 40", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("LHA.DE", "Lufthansa", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("SAP.DE", "SAP", "Contraste: software empresarial resiliente", KIND_CONTRAST),
        ),
    ),
    "FR": Market(
        "FR", "Francia", 48.85, 2.35, "^FCHI",
        (
            Asset("^FCHI", "CAC 40", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("AF.PA", "Air France-KLM", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("MC.PA", "LVMH", "Contraste: lujo y recuperación post-pandemia", KIND_CONTRAST),
        ),
    ),
    "JP": Market(
        "JP", "Japón", 35.68, 139.69, "^N225",
        (
            Asset("^N225", "Nikkei 225", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("9201.T", "Japan Airlines", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("6758.T", "Sony", "Contraste: tecnología y entretenimiento resiliente", KIND_CONTRAST),
        ),
    ),
    "TW": Market(
        "TW", "Taiwán", 25.03, 121.57, "^TWII",
        (
            Asset("^TWII", "TAIEX", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("2610.TW", "China Airlines", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("2330.TW", "TSMC", "Contraste: semiconductores en auge", KIND_CONTRAST),
        ),
    ),
    "HK": Market(
        "HK", "Hong Kong", 22.32, 114.17, "^HSI",
        (
            Asset("^HSI", "Hang Seng", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("0293.HK", "Cathay Pacific", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("0700.HK", "Tencent", "Contraste: tecnología/juegos resiliente", KIND_CONTRAST),
        ),
    ),
    "CA": Market(
        "CA", "Canadá", 43.65, -79.38, "^GSPTSE",
        (
            Asset("^GSPTSE", "S&P/TSX Composite", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("AC.TO", "Air Canada", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("SHOP.TO", "Shopify", "Contraste: e-commerce impulsado por la pandemia", KIND_CONTRAST),
        ),
    ),
    "AU": Market(
        "AU", "Australia", -33.87, 151.21, "^AXJO",
        (
            Asset("^AXJO", "S&P/ASX 200", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("QAN.AX", "Qantas", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("BHP.AX", "BHP Group", "Contraste: minería y materias primas", KIND_CONTRAST),
        ),
    ),
    "KR": Market(
        "KR", "Corea del Sur", 37.57, 126.98, "^KS11",
        (
            Asset("^KS11", "KOSPI", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("003490.KS", "Korean Air", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("005930.KS", "Samsung Electronics", "Contraste: electrónica resiliente", KIND_CONTRAST),
        ),
    ),
    "IN": Market(
        "IN", "India", 19.08, 72.88, "^NSEI",
        (
            Asset("^NSEI", "NIFTY 50", "Mercado general (referencia / benchmark de coherencia)", KIND_GENERAL),
            Asset("INDIGO.NS", "InterGlobe (IndiGo)", "Contraste: aerolínea golpeada por la pandemia", KIND_CONTRAST),
            Asset("TCS.NS", "Tata Consultancy Services", "Contraste: servicios de TI resiliente", KIND_CONTRAST),
        ),
    ),
}

# Mercado por defecto del dashboard.
DEFAULT_MARKET: str = "US"

# Registro plano de todos los activos (ticker -> Asset), derivado de MARKETS.
ASSETS: dict[str, Asset] = {
    asset.ticker: asset for market in MARKETS.values() for asset in market.assets
}

# Mapa ticker -> código de mercado, derivado de MARKETS.
_MARKET_OF_TICKER: dict[str, str] = {
    asset.ticker: market.code for market in MARKETS.values() for asset in market.assets
}

# Benchmark histórico de EE.UU.; se conserva por compatibilidad. La coherencia
# usa el benchmark *del mercado de cada activo* (ver ``benchmark_for``).
BENCHMARK: str = MARKETS[DEFAULT_MARKET].benchmark

# Épocas (segmentos de análisis). Globales: la pandemia afectó a todos los mercados.
EPOCHS: dict[str, Epoch] = {
    "antes": Epoch("antes", "Antes (pre-pandemia)", "2018-01-01", "2020-02-19"),
    "durante": Epoch("durante", "Durante (pandemia)", "2020-02-20", "2021-12-31"),
    "despues": Epoch("despues", "Después (post-pandemia)", "2022-01-01", "2023-12-31"),
}


def asset_keys() -> list[str]:
    return list(ASSETS.keys())


def epoch_keys() -> list[str]:
    return list(EPOCHS.keys())


def market_keys() -> list[str]:
    return list(MARKETS.keys())


def market_of(ticker: str) -> str:
    """Código de mercado al que pertenece un ticker."""
    if ticker not in _MARKET_OF_TICKER:
        raise KeyError(f"Ticker desconocido: {ticker}. Válidos: {asset_keys()}")
    return _MARKET_OF_TICKER[ticker]


def benchmark_for(ticker: str) -> str:
    """Ticker del benchmark (activo general) del mercado de ``ticker``."""
    return MARKETS[market_of(ticker)].benchmark


def assets_of_market(code: str) -> list[Asset]:
    """Lista de activos (general + contrastes) de un mercado."""
    if code not in MARKETS:
        raise KeyError(f"Mercado desconocido: {code}. Válidos: {market_keys()}")
    return list(MARKETS[code].assets)
