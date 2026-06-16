"""Autocorrelación y teorema de Wiener-Khinchin.

Referencia: Oppenheim & Schafer, cap. 2 (correlación de secuencias) y cap. 10.3
(relación con la densidad espectral de potencia).

Autocorrelación (estimador sesgado, normalizado por N):

    R_xx[m] = (1/N) · Σ_n x[n] · x[n+m]

Teorema de Wiener-Khinchin: la PSD es la transformada de Fourier de la
autocorrelación. En el dominio discreto y finito, la versión **exacta** que
satisface la identidad es la autocorrelación *circular*: su DFT es exactamente el
periodograma ``(1/N)·|X[k]|²``. La autocorrelación *lineal* (la que se grafica en
el panel) es una aproximación con sesgo en los retardos grandes.
"""

from __future__ import annotations

import numpy as np

from .welch import _to_onesided, onesided_freqs


def autocorrelation(x: np.ndarray, max_lag: int | None = None) -> np.ndarray:
    r"""Autocorrelación lineal sesgada para retardos m = 0..max_lag.

    :math:`R_{xx}[m] = (1/N) \sum_{n=0}^{N-1-m} x[n]\,x[n+m]`.

    Si ``max_lag`` es None, se usa ``N-1``.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    if n == 0:
        raise ValueError("Señal vacía.")
    if max_lag is None:
        max_lag = n - 1
    max_lag = min(max_lag, n - 1)
    r = np.empty(max_lag + 1)
    for m in range(max_lag + 1):
        r[m] = np.sum(x[: n - m] * x[m:]) / n
    return r


def circular_autocorrelation(x: np.ndarray) -> np.ndarray:
    r"""Autocorrelación circular: :math:`r_c[m] = (1/N)\sum_n x[n]\,x[(n+m)\bmod N]`.

    Se calcula vía la FFT (``ifft(|X|²)/N``) y es la que satisface de forma exacta
    el teorema de Wiener-Khinchin para la DFT.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    spectrum = np.fft.fft(x)
    rc = np.fft.ifft(np.abs(spectrum) ** 2).real / n
    return rc


def wiener_khinchin_psd(
    x: np.ndarray, fs: float = 1.0, onesided: bool = True
) -> tuple[np.ndarray, np.ndarray]:
    """PSD obtenida vía Wiener-Khinchin (DFT de la autocorrelación circular).

    Por construcción coincide con el periodograma ``(1/(fs·N))·|X[k]|²`` (de un
    lado, con duplicado de las frecuencias positivas), lo que permite verificar
    numéricamente el teorema y compararlo con el estimador de Welch.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    rc = circular_autocorrelation(x)
    # DFT de la autocorrelación circular = |X|²/N. Escalamos por fs como densidad.
    psd_full = np.fft.fft(rc).real / fs
    if onesided:
        psd = _to_onesided(psd_full, n)
        freqs = onesided_freqs(n, fs)
    else:
        psd = psd_full
        freqs = np.fft.fftfreq(n, d=1.0 / fs)
    return freqs, psd
