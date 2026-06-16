"""Densidad espectral cruzada (CSD) y coherencia espectral.

Referencia: Oppenheim & Schafer, cap. 10.5 (espectro cruzado entre dos señales).

Densidad espectral cruzada por promediado de Welch (segmentos solapados,
misma ventana que la PSD):

    S_AB[k] = (1/K) · Σ_i conj(X_i[k]) · Y_i[k]   (con la misma normalización que la PSD)

Coherencia (magnitud cuadrática), en [0, 1]:

    Coh_AB[k] = |S_AB[k]|² / (P_A[k] · P_B[k])

La coherencia mide cuán linealmente relacionadas están dos señales a cada
frecuencia: ~1 indica fuerte acoplamiento (sincronización con el mercado), ~0
indica desacople. El promediado entre segmentos es esencial: con un solo
segmento la coherencia es trivialmente 1.
"""

from __future__ import annotations

import numpy as np

from .welch import _segment_ffts, _step_from_overlap, _to_onesided, onesided_freqs
from .windows import get_window


def _common_setup(x, y, fs, nperseg, window, overlap, detrend):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size != y.size:
        raise ValueError("Las dos señales deben tener la misma longitud.")
    M = min(int(nperseg), x.size)
    if M < 2:
        raise ValueError("nperseg efectivo debe ser >= 2.")
    w = get_window(window, M)
    U = float(np.sum(w * w))
    step = _step_from_overlap(M, overlap)
    fx = _segment_ffts(x, w, step, detrend)
    fy = _segment_ffts(y, w, step, detrend)
    return M, U, fs, fx, fy


def cross_spectral_density(
    x: np.ndarray,
    y: np.ndarray,
    fs: float = 1.0,
    nperseg: int = 256,
    window: str = "hanning",
    overlap: float = 0.5,
    detrend: bool = True,
    onesided: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """CSD compleja ``S_AB[k]`` por promediado de Welch."""
    M, U, fs, fx, fy = _common_setup(x, y, fs, nperseg, window, overlap, detrend)
    sxy = (np.conj(fx) * fy).mean(axis=0) / (fs * U)
    if onesided:
        sxy = _to_onesided(sxy, M)
        freqs = onesided_freqs(M, fs)
    else:
        freqs = np.fft.fftfreq(M, d=1.0 / fs)
    return freqs, sxy


def coherence(
    x: np.ndarray,
    y: np.ndarray,
    fs: float = 1.0,
    nperseg: int = 256,
    window: str = "hanning",
    overlap: float = 0.5,
    detrend: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    r"""Coherencia espectral :math:`|S_{AB}|^2/(P_A P_B)` en [0, 1].

    Los factores de escala (fs, energía de la ventana, duplicado de un lado) se
    cancelan en el cociente, por lo que el resultado coincide con
    ``scipy.signal.coherence`` (oráculo en los tests) cuando se usa la misma
    ventana y segmentación.
    """
    M, U, fs, fx, fy = _common_setup(x, y, fs, nperseg, window, overlap, detrend)
    sxx = (np.abs(fx) ** 2).mean(axis=0)
    syy = (np.abs(fy) ** 2).mean(axis=0)
    sxy = (np.conj(fx) * fy).mean(axis=0)

    n_out = M // 2 + 1
    sxx = sxx[:n_out]
    syy = syy[:n_out]
    sxy = sxy[:n_out]

    denom = sxx * syy
    coh = np.zeros(n_out)
    nz = denom > 0
    coh[nz] = (np.abs(sxy[nz]) ** 2) / denom[nz]
    freqs = onesided_freqs(M, fs)
    return freqs, np.clip(coh, 0.0, 1.0)
