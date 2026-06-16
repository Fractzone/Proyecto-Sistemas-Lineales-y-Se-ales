"""Estimador de la densidad espectral de potencia (PSD) por el método de Welch.

Referencia: Oppenheim & Schafer, cap. 10.3 (estimación espectral no paramétrica;
método de promediado de periodogramas modificados de Welch).

Idea: dividir la señal en ``K`` segmentos solapados (solape 50% por defecto),
aplicar una ventana a cada uno, calcular el periodograma modificado de cada
segmento y promediarlos. El promediado reduce la varianza del estimador a costa
de resolución en frecuencia (compromiso sesgo-varianza).

Periodograma modificado del segmento i, con ventana ``w`` de longitud ``M`` y
factor de corrección de energía ``U = (1/M)·Σ w²[m]``:

    P_i[k] = (1 / (fs · M · U)) · |FFT(x_i · w)[k]|²

PSD de Welch (promedio):

    P[k] = (1/K) · Σ_i P_i[k]

Para un espectro de un solo lado (``onesided=True``) se duplica la potencia de
las frecuencias positivas (excepto DC y Nyquist), de modo que la energía total
se conserva. Esta normalización coincide con la convención ``scaling='density'``
de ``scipy.signal.welch`` (usado como oráculo en los tests).

Nota: ``M·U = Σ w²[m]``, por lo que el factor de corrección equivale a dividir
entre la energía de la ventana, ``Σ w²``.
"""

from __future__ import annotations

import numpy as np

from .windows import get_window


def _step_from_overlap(M: int, overlap: float) -> int:
    if not 0.0 <= overlap < 1.0:
        raise ValueError("overlap debe estar en [0, 1).")
    noverlap = int(round(M * overlap))
    return max(1, M - noverlap)


def _segment_ffts(
    x: np.ndarray, window: np.ndarray, step: int, detrend: bool
) -> np.ndarray:
    """FFT (de dos lados) de cada segmento ventaneado. Devuelve matriz (K, M).

    ``detrend`` resta la media de cada segmento (equivale a ``detrend='constant'``
    de scipy), eliminando el sesgo de DC segmento a segmento.
    """
    M = window.size
    n = x.size
    if n < M:
        raise ValueError(f"La señal ({n}) es más corta que el segmento ({M}).")
    K = 1 + (n - M) // step
    ffts = np.empty((K, M), dtype=complex)
    for i in range(K):
        seg = x[i * step : i * step + M]
        if detrend:
            seg = seg - seg.mean()
        ffts[i] = np.fft.fft(seg * window)
    return ffts


def _to_onesided(power_full: np.ndarray, M: int) -> np.ndarray:
    """Convierte una PSD de dos lados a un solo lado, duplicando f>0 (no DC/Nyq)."""
    n_out = M // 2 + 1
    out = power_full[..., :n_out].copy()
    if M % 2 == 0:  # hay bin de Nyquist exacto: no se duplica
        out[..., 1:-1] *= 2.0
    else:
        out[..., 1:] *= 2.0
    return out


def onesided_freqs(M: int, fs: float) -> np.ndarray:
    """Eje de frecuencias (ciclos/unidad de tiempo) para un espectro de un lado."""
    n_out = M // 2 + 1
    return np.arange(n_out) * (fs / M)


def welch_psd(
    x: np.ndarray,
    fs: float = 1.0,
    nperseg: int = 256,
    window: str = "hanning",
    overlap: float = 0.5,
    detrend: bool = True,
    onesided: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """PSD de Welch implementada a mano.

    Parameters
    ----------
    x : señal real 1-D.
    fs : frecuencia de muestreo (en este proyecto, 1.0 muestra/día de trading).
    nperseg : longitud del segmento ``M`` (se recorta a ``len(x)`` si excede).
    window : nombre de la ventana (``hanning``/``hamming``/``blackman``/``rect``).
    overlap : fracción de solape entre segmentos (0.5 = 50%).
    detrend : si True, resta la media de cada segmento.
    onesided : si True, devuelve solo frecuencias >= 0 con potencia duplicada.

    Returns
    -------
    (freqs, psd) : eje de frecuencias en ciclos/día y la PSD estimada.
    El periodo equivalente en días de un bin es ``1/freqs[k]``.
    """
    x = np.asarray(x, dtype=float)
    M = min(int(nperseg), x.size)
    if M < 2:
        raise ValueError("nperseg efectivo debe ser >= 2.")

    w = get_window(window, M)
    U = float(np.sum(w * w))  # = M·U_corr (energía de la ventana)
    step = _step_from_overlap(M, overlap)

    ffts = _segment_ffts(x, w, step, detrend)
    power = (np.abs(ffts) ** 2).mean(axis=0) / (fs * U)

    if onesided:
        psd = _to_onesided(power, M)
        freqs = onesided_freqs(M, fs)
    else:
        psd = power
        freqs = np.fft.fftfreq(M, d=1.0 / fs)
    return freqs, psd
