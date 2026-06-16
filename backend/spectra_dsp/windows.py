"""Ventanas de análisis espectral (implementadas a mano).

Referencia: Oppenheim & Schafer, cap. 7.2 (diseño de FIR por ventaneo) y
cap. 10.2-10.3 (efecto de la ventana en la estimación espectral).

El ventaneo reduce las fugas espectrales (leakage) suavizando los extremos del
segmento antes de la DFT, a costa de ensanchar el lóbulo principal. Se
implementan las formas **simétricas** clásicas (denominador ``M-1``), que son
las que se usan tanto para el diseño de filtros FIR como para la segmentación de
Welch en este proyecto. No se usa ``numpy.hanning`` ni equivalentes.
"""

from __future__ import annotations

import numpy as np

WINDOW_NAMES = ("hanning", "hamming", "blackman", "rect")


def hanning(M: int) -> np.ndarray:
    r""":math:`w[m] = 0.5\,(1 - \cos(2\pi m/(M-1)))`, m = 0..M-1."""
    if M < 1:
        raise ValueError("M debe ser >= 1.")
    if M == 1:
        return np.ones(1)
    m = np.arange(M)
    return 0.5 * (1.0 - np.cos(2.0 * np.pi * m / (M - 1)))


def hamming(M: int) -> np.ndarray:
    r""":math:`w[m] = 0.54 - 0.46\,\cos(2\pi m/(M-1))`."""
    if M < 1:
        raise ValueError("M debe ser >= 1.")
    if M == 1:
        return np.ones(1)
    m = np.arange(M)
    return 0.54 - 0.46 * np.cos(2.0 * np.pi * m / (M - 1))


def blackman(M: int) -> np.ndarray:
    r""":math:`w[m] = 0.42 - 0.5\cos(2\pi m/(M-1)) + 0.08\cos(4\pi m/(M-1))`."""
    if M < 1:
        raise ValueError("M debe ser >= 1.")
    if M == 1:
        return np.ones(1)
    m = np.arange(M)
    return (
        0.42
        - 0.5 * np.cos(2.0 * np.pi * m / (M - 1))
        + 0.08 * np.cos(4.0 * np.pi * m / (M - 1))
    )


def rect(M: int) -> np.ndarray:
    """Ventana rectangular (sin ventaneo); útil como referencia."""
    if M < 1:
        raise ValueError("M debe ser >= 1.")
    return np.ones(M)


_DISPATCH = {
    "hanning": hanning,
    "hann": hanning,
    "hamming": hamming,
    "blackman": blackman,
    "rect": rect,
    "rectangular": rect,
    "boxcar": rect,
}


def get_window(name: str, M: int) -> np.ndarray:
    """Devuelve la ventana ``name`` de longitud ``M`` (dispatcher por nombre)."""
    key = name.lower()
    if key not in _DISPATCH:
        raise ValueError(f"Ventana desconocida: {name!r}. Válidas: {WINDOW_NAMES}")
    return _DISPATCH[key](M)
