"""Esquemas Pydantic de las respuestas de la API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AssetInfo(BaseModel):
    ticker: str
    name: str
    role: str


class EpochInfo(BaseModel):
    key: str
    label: str
    start: str
    end: str


class AnalyzeRequest(BaseModel):
    asset: str = Field(..., description="Ticker: SPY | AAL | NFLX")
    epoch: str = Field(..., description="Época: antes | durante | despues")
    N: int = Field(1024, ge=64, le=4096, description="Resolución espectral (nperseg)")
    window: str = Field("hanning", description="hanning | hamming | blackman")
    eps_low: float = Field(0.45, ge=0.0, le=1.0)
    eps_high: float = Field(0.65, ge=0.0, le=1.0)


class TimeSeries(BaseModel):
    dates: list[str]
    price: list[float]
    returns: list[float]
    returns_dates: list[str]
    dominant_component_ifft: list[float]
    dominant_component_fir: list[float]


class Spectral(BaseModel):
    freqs: list[float]
    psd: list[float]
    se: float
    se_norm: float
    regime: str
    # Espectrograma STFT
    stft_times: list[float]
    stft_freqs: list[float]
    stft_matrix: list[list[float]]


class Relation(BaseModel):
    coh_freqs: list[float]
    coherence: list[float]
    coherence_at_dom: float
    autocorr_lags: list[int]
    autocorr: list[float]


class Summary(BaseModel):
    regime: str
    period_days: float
    f_dom: float
    phase_pct: float
    phase_rad: float
    confidence: float
    volatility: float
    coherence_at_dom: float
    n_samples: int
    nperseg: int
    interpretation: str


class AnalyzeResponse(BaseModel):
    asset: str
    epoch: str
    window: str
    time: TimeSeries
    spectral: Spectral
    relation: Relation
    summary: Summary


class CompareRequest(BaseModel):
    mode: str = Field(..., description="'asset_epochs' o 'epoch_assets'")
    asset: str | None = None
    epoch: str | None = None
    N: int = Field(1024, ge=64, le=4096)
    window: str = "hanning"
    eps_low: float = 0.45
    eps_high: float = 0.65


class CompareRow(BaseModel):
    asset: str
    epoch: str
    regime: str
    period_days: float
    confidence: float
    volatility: float
    coherence_at_dom: float
    se_norm: float


class CompareResponse(BaseModel):
    mode: str
    rows: list[CompareRow]
