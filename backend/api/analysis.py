"""Orquestación del análisis: une la capa de datos con el motor DSP.

Para cada (activo, época) ejecuta el pipeline completo de SPECTRA y arma la
respuesta de la API. Los resultados se cachean en memoria por combinación de
parámetros para que el dashboard sea fluido.
"""

from __future__ import annotations

import numpy as np

from data import config, loader
from spectra_dsp import (
    autocorr,
    cross_spectrum,
    cycle_phase,
    entropy,
    fir,
    ifft_filter,
    preprocessing,
    stft,
    welch,
)

from . import interpret, schemas

_CACHE: dict[tuple, schemas.AnalyzeResponse] = {}


def _aligned_returns(
    asset: str, epoch: str, benchmark: str
) -> tuple[np.ndarray, np.ndarray]:
    """Retornos de ``asset`` y del ``benchmark`` alineados por fecha común."""
    da, ra = loader.get_returns(asset, epoch)
    db, rb = loader.get_returns(benchmark, epoch)
    common = da.intersection(db)
    ia = da.isin(common)
    ib = db.isin(common)
    return ra[ia], rb[ib]


def _dominant_component_ifft(r: np.ndarray, f_dom: float) -> np.ndarray:
    n = r.size
    k = int(round(f_dom * n))
    k = min(max(k, 1), n // 2)
    half_width = max(1, int(round(0.25 * k)))
    return ifft_filter.bandpass_ifft(r, max(1, k - half_width), min(n // 2, k + half_width))


def _dominant_component_fir(r: np.ndarray, f_dom: float) -> np.ndarray:
    n = r.size
    num_taps = min(101, (n // 4) | 1)  # impar
    if num_taps < 9:
        num_taps = 9
    fc_low = max(1e-3, f_dom * 0.6)
    fc_high = min(0.49, f_dom * 1.4)
    if fc_low >= fc_high:
        fc_low = max(1e-3, fc_high * 0.5)
    h = fir.fir_bandpass(num_taps, fc_low, fc_high, window="blackman")
    return fir.convolve(r, h, mode="same")


def analyze(req: schemas.AnalyzeRequest) -> schemas.AnalyzeResponse:
    key = (req.asset, req.epoch, req.N, req.window, req.eps_low, req.eps_high)
    if key in _CACHE:
        return _CACHE[key]

    if req.asset not in config.ASSETS:
        raise KeyError(f"Activo desconocido: {req.asset}")
    if req.epoch not in config.EPOCHS:
        raise KeyError(f"Época desconocida: {req.epoch}")

    benchmark = config.benchmark_for(req.asset)

    prices = loader.get_prices(req.asset, req.epoch)
    dates, returns = loader.get_returns(req.asset, req.epoch)
    r = preprocessing.remove_dc(returns)
    n = r.size
    nperseg = min(req.N, n)

    # --- PSD de Welch + ciclo dominante ---
    freqs, psd = welch.welch_psd(r, fs=config.FS, nperseg=nperseg, window=req.window)
    dom = cycle_phase.dominant_cycle(freqs, psd)
    phase = cycle_phase.phase_at_frequency(r, dom["f_dom"], fs=config.FS)

    # --- Entropía / régimen ---
    se, se_norm = entropy.spectral_entropy(psd)
    regime = entropy.regime_label(se_norm, req.eps_low, req.eps_high)

    # --- Componente del ciclo dominante reconstruida ---
    comp_ifft = _dominant_component_ifft(r, dom["f_dom"])
    comp_fir = _dominant_component_fir(r, dom["f_dom"])

    # --- Espectrograma STFT ---
    seg = min(64, max(8, n // 6))
    st_times, st_freqs, st_mat = stft.stft_spectrogram(
        r, fs=config.FS, nperseg=seg, window=req.window
    )

    # --- Autocorrelación ---
    max_lag = min(120, n - 1)
    acf = autocorr.autocorrelation(r, max_lag=max_lag)

    # --- Coherencia vs el benchmark del mercado ---
    if req.asset == benchmark:
        coh_freqs = freqs
        coh = np.ones_like(freqs)
        coh_at_dom = 1.0
    else:
        ra, rb = _aligned_returns(req.asset, req.epoch, benchmark)
        ra = preprocessing.remove_dc(ra)
        rb = preprocessing.remove_dc(rb)
        # La coherencia EXIGE promediar varios segmentos: con un único segmento
        # sería idénticamente 1. Se elige nperseg ~ N/4 de la serie para obtener
        # del orden de 6-8 segmentos solapados al 50%.
        nps_coh = max(32, min(req.N, ra.size // 4))
        coh_freqs, coh = cross_spectrum.coherence(
            ra, rb, fs=config.FS, nperseg=nps_coh, window=req.window
        )
        kdom = int(np.argmin(np.abs(coh_freqs - dom["f_dom"])))
        coh_at_dom = float(coh[kdom])

    volatility = preprocessing.volatility(returns)

    interpretation = interpret.build_interpretation(
        asset=req.asset,
        epoch=req.epoch,
        benchmark=benchmark,
        regime=regime,
        period_days=dom["period_days"],
        confidence=dom["energy_ratio"],
        volatility=volatility,
        coherence_at_dom=coh_at_dom,
        se_norm=se_norm,
    )

    resp = schemas.AnalyzeResponse(
        asset=req.asset,
        epoch=req.epoch,
        window=req.window,
        time=schemas.TimeSeries(
            dates=[d.strftime("%Y-%m-%d") for d in prices.index],
            price=prices.to_numpy().tolist(),
            returns=r.tolist(),
            returns_dates=[d.strftime("%Y-%m-%d") for d in dates],
            dominant_component_ifft=comp_ifft.tolist(),
            dominant_component_fir=comp_fir.tolist(),
        ),
        spectral=schemas.Spectral(
            freqs=freqs.tolist(),
            psd=psd.tolist(),
            se=se,
            se_norm=se_norm,
            regime=regime,
            stft_times=st_times.tolist(),
            stft_freqs=st_freqs.tolist(),
            stft_matrix=st_mat.tolist(),
        ),
        relation=schemas.Relation(
            coh_freqs=coh_freqs.tolist(),
            coherence=coh.tolist(),
            coherence_at_dom=coh_at_dom,
            autocorr_lags=list(range(len(acf))),
            autocorr=acf.tolist(),
        ),
        summary=schemas.Summary(
            regime=regime,
            period_days=dom["period_days"],
            f_dom=dom["f_dom"],
            phase_pct=phase["phase_pct"],
            phase_rad=phase["phase_rad"],
            confidence=dom["energy_ratio"],
            volatility=volatility,
            coherence_at_dom=coh_at_dom,
            n_samples=n,
            nperseg=nperseg,
            benchmark=benchmark,
            interpretation=interpretation,
        ),
    )
    _CACHE[key] = resp
    return resp


def compare(req: schemas.CompareRequest) -> schemas.CompareResponse:
    rows: list[schemas.CompareRow] = []
    if req.mode == "asset_epochs":
        if req.asset not in config.ASSETS:
            raise KeyError("Se requiere 'asset' válido para mode='asset_epochs'.")
        combos = [(req.asset, ep) for ep in config.epoch_keys()]
    elif req.mode == "epoch_assets":
        if req.epoch not in config.EPOCHS:
            raise KeyError("Se requiere 'epoch' válida para mode='epoch_assets'.")
        if req.market not in config.MARKETS:
            raise KeyError("Se requiere 'market' válido para mode='epoch_assets'.")
        combos = [(a.ticker, req.epoch) for a in config.assets_of_market(req.market)]
    else:
        raise ValueError("mode debe ser 'asset_epochs' o 'epoch_assets'.")

    for asset, epoch in combos:
        a = analyze(
            schemas.AnalyzeRequest(
                asset=asset,
                epoch=epoch,
                N=req.N,
                window=req.window,
                eps_low=req.eps_low,
                eps_high=req.eps_high,
            )
        )
        rows.append(
            schemas.CompareRow(
                asset=asset,
                epoch=epoch,
                regime=a.summary.regime,
                period_days=a.summary.period_days,
                confidence=a.summary.confidence,
                volatility=a.summary.volatility,
                coherence_at_dom=a.summary.coherence_at_dom,
                se_norm=a.spectral.se_norm,
            )
        )
    return schemas.CompareResponse(mode=req.mode, rows=rows)
