"""Métricas de resumen y verificaciones de energía.

Referencia: Oppenheim & Schafer, cap. 8.7 (teorema de Parseval para la DFT).

Teorema de Parseval (conservación de energía tiempo <-> frecuencia):

    Σ_n |x[n]|² = (1/N) · Σ_k |X[k]|²
"""

from __future__ import annotations

import numpy as np


def energy(x: np.ndarray) -> float:
    """Energía de la señal en el tiempo: ``Σ |x[n]|²``."""
    x = np.asarray(x)
    return float(np.sum(np.abs(x) ** 2))


def spectral_energy(x: np.ndarray) -> float:
    """Energía estimada desde la frecuencia: ``(1/N)·Σ |X[k]|²``."""
    x = np.asarray(x)
    spectrum = np.fft.fft(x)
    return float(np.sum(np.abs(spectrum) ** 2) / x.size)


def parseval_residual(x: np.ndarray) -> float:
    """Error relativo entre la energía en tiempo y en frecuencia (debe ser ~0)."""
    e_t = energy(x)
    e_f = spectral_energy(x)
    if e_t == 0:
        return abs(e_f)
    return abs(e_t - e_f) / e_t


def relative_energy(psd: np.ndarray, mask: np.ndarray) -> float:
    """Fracción de la energía espectral contenida en los bins marcados por ``mask``."""
    psd = np.asarray(psd, dtype=float)
    total = psd.sum()
    if total <= 0:
        return 0.0
    return float(psd[mask].sum() / total)
