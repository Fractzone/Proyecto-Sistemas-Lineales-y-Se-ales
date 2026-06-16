"""Diseño de filtros FIR por ventaneo (windowed-sinc) y convolución lineal.

Referencia: Oppenheim & Schafer, cap. 7.5 (diseño de filtros FIR por el método de
ventana / "windowing").

La respuesta al impulso ideal de un pasa-bajos con frecuencia de corte ``fc``
(en ciclos/muestra, 0 < fc < 0.5) es una sinc infinita:

    h_ideal[n] = 2·fc · sinc(2·fc·(n - M/2))

Se trunca a ``num_taps`` coeficientes y se multiplica por una ventana (Hamming o
Blackman) para reducir el rizado de Gibbs. El pasa-banda se obtiene por
diferencia de dos pasa-bajos (equivalente a inversión espectral). El filtro se
aplica por **convolución lineal** ``y[n] = Σ_k h[k]·x[n-k]``, implementada a mano.
"""

from __future__ import annotations

import numpy as np

from .windows import get_window


def _sinc(x: np.ndarray) -> np.ndarray:
    """sinc normalizada: sin(πx)/(πx), con sinc(0)=1 (idéntica a np.sinc)."""
    return np.sinc(x)


def sinc_lowpass(num_taps: int, fc: float, window: str = "hamming") -> np.ndarray:
    r"""Filtro FIR pasa-bajos windowed-sinc.

    ``fc`` es la frecuencia de corte normalizada en ciclos/muestra (0 < fc < 0.5).
    Los coeficientes se normalizan para ganancia unitaria en DC (``Σ h = 1``).
    """
    if num_taps < 1:
        raise ValueError("num_taps debe ser >= 1.")
    if not 0.0 < fc < 0.5:
        raise ValueError("fc debe estar en (0, 0.5) ciclos/muestra.")
    n = np.arange(num_taps)
    center = (num_taps - 1) / 2.0
    h_ideal = 2.0 * fc * _sinc(2.0 * fc * (n - center))
    h = h_ideal * get_window(window, num_taps)
    return h / np.sum(h)


def fir_bandpass(
    num_taps: int, fc_low: float, fc_high: float, window: str = "hamming"
) -> np.ndarray:
    r"""Filtro FIR pasa-banda como diferencia de dos pasa-bajos.

    Banda de paso aproximada ``[fc_low, fc_high]`` (ciclos/muestra). Se construye
    ``h = lp(fc_high) - lp(fc_low)``, de modo que la ganancia en DC es 0.
    """
    if not 0.0 <= fc_low < fc_high < 0.5:
        raise ValueError("Se requiere 0 <= fc_low < fc_high < 0.5.")
    lp_high = sinc_lowpass(num_taps, fc_high, window)
    if fc_low <= 0.0:
        return lp_high
    lp_low = sinc_lowpass(num_taps, fc_low, window)
    return lp_high - lp_low


def convolve(x: np.ndarray, h: np.ndarray, mode: str = "same") -> np.ndarray:
    r"""Convolución lineal :math:`y[n] = \sum_k h[k]\,x[n-k]` (a mano).

    Se acumula desplazando ``x`` por cada coeficiente del filtro (sin usar
    ``numpy.convolve``). ``mode``:

    - ``"full"``: longitud ``len(x)+len(h)-1``.
    - ``"same"``: centrada, misma longitud que ``x`` (útil para superponer la
      componente filtrada sobre el precio).
    """
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    n, m = x.size, h.size
    full = np.zeros(n + m - 1)
    for k in range(m):
        full[k : k + n] += h[k] * x
    if mode == "full":
        return full
    if mode == "same":
        start = (m - 1) // 2
        return full[start : start + n]
    raise ValueError("mode debe ser 'full' o 'same'.")


def frequency_response(
    h: np.ndarray, n_fft: int = 1024, fs: float = 1.0
) -> tuple[np.ndarray, np.ndarray]:
    r"""Respuesta en frecuencia :math:`|H(e^{j\omega})|` vía FFT de ``h``.

    Devuelve ``(freqs, magnitude)`` de un solo lado, con ``freqs`` en ciclos por
    unidad de tiempo (ciclos/muestra si fs=1).
    """
    h = np.asarray(h, dtype=float)
    n_fft = max(n_fft, h.size)
    H = np.fft.fft(h, n_fft)
    n_out = n_fft // 2 + 1
    freqs = np.arange(n_out) * (fs / n_fft)
    return freqs, np.abs(H[:n_out])
