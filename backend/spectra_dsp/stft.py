"""Transformada de Fourier de tiempo corto (STFT) / espectrograma.

Referencia: Oppenheim & Schafer, cap. 10.3 (análisis tiempo-frecuencia mediante
DFT de ventana deslizante).

Se desliza una ventana de longitud ``nperseg`` con paso ``hop`` sobre la señal;
para cada posición se calcula ``|FFT(segmento · ventana)|²``. El resultado es una
matriz tiempo-frecuencia que revela la **no estacionariedad** dentro de una época
(por ejemplo el shock de volatilidad de marzo 2020).
"""

from __future__ import annotations

import numpy as np

from .welch import onesided_freqs
from .windows import get_window


def stft_spectrogram(
    x: np.ndarray,
    fs: float = 1.0,
    nperseg: int = 64,
    hop: int | None = None,
    window: str = "hanning",
    detrend: bool = True,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Espectrograma por STFT.

    Parameters
    ----------
    nperseg : longitud de la ventana deslizante.
    hop : avance entre ventanas (por defecto ``nperseg // 2``, 50% de solape).

    Returns
    -------
    (times, freqs, Sxx) donde ``times`` es el centro de cada ventana (en la misma
    unidad que ``1/fs``, es decir días), ``freqs`` el eje de frecuencias de un
    lado, y ``Sxx`` la matriz de potencia con forma ``(len(freqs), len(times))``.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    M = min(int(nperseg), n)
    if M < 2:
        raise ValueError("nperseg efectivo debe ser >= 2.")
    if hop is None:
        hop = max(1, M // 2)

    w = get_window(window, M)
    U = float(np.sum(w * w))
    n_freqs = M // 2 + 1

    starts = list(range(0, n - M + 1, hop))
    if not starts:
        starts = [0]

    sxx = np.empty((n_freqs, len(starts)))
    times = np.empty(len(starts))
    for j, s in enumerate(starts):
        seg = x[s : s + M]
        if detrend:
            seg = seg - seg.mean()
        spec = np.fft.fft(seg * w)
        power = (np.abs(spec[:n_freqs]) ** 2) / (fs * U)
        if M % 2 == 0:
            power[1:-1] *= 2.0
        else:
            power[1:] *= 2.0
        sxx[:, j] = power
        times[j] = (s + M / 2.0) / fs

    freqs = onesided_freqs(M, fs)
    return times, freqs, sxx
