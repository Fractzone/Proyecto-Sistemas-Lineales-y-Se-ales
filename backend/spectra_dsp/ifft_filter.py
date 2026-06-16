"""Filtrado por bandas en el dominio de la frecuencia (máscara + IFFT).

Referencia: Oppenheim & Schafer, cap. 8 (DFT y convolución circular).

Enfoque complementario al FIR: en vez de convolución lineal en el tiempo, se
multiplica el espectro por una **máscara ideal** ``H[k]`` (1 dentro de la banda,
0 fuera) y se vuelve al tiempo con la IFFT. Para que la señal reconstruida sea
real, la máscara debe ser hermítica: si se conserva el bin ``k`` también se
conserva su simétrico ``N-k``.

    H[k] = 1  para k ∈ [k_low, k_high] ∪ [N-k_high, N-k_low]
    H[k] = 0  en otro caso
    x_filtrado[n] = Re( IFFT( FFT(x) · H ) )

Diferencia conceptual con el FIR: aquí la operación equivale a una convolución
*circular* (asume periodicidad de la señal), mientras que el FIR aplica una
convolución *lineal*. Por eso el FIR introduce transitorios en los bordes y la
máscara IFFT puede introducir efectos de borde por la periodicidad implícita.
"""

from __future__ import annotations

import numpy as np


def bandpass_ifft(x: np.ndarray, k_low: int, k_high: int) -> np.ndarray:
    """Filtra por banda de bins ``[k_low, k_high]`` mediante máscara + IFFT.

    ``k_low``/``k_high`` son índices de bin de la DFT (0 = DC). Se construye la
    máscara hermítica y se devuelve la parte real de la IFFT.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    if not 0 <= k_low <= k_high < n:
        raise ValueError("Se requiere 0 <= k_low <= k_high < N.")

    mask = np.zeros(n)
    mask[k_low : k_high + 1] = 1.0
    # Simetría hermítica: conservar los bins conjugados N-k.
    lo = max(1, n - k_high)  # evita tocar el bin DC con el reflejo
    hi = n - k_low
    if hi >= lo:
        mask[lo : hi + 1] = 1.0

    spectrum = np.fft.fft(x)
    return np.fft.ifft(spectrum * mask).real


def band_from_period(n: int, fs: float, period_low: float, period_high: float) -> tuple[int, int]:
    """Convierte un rango de periodos (en días) a índices de bin ``[k_low, k_high]``.

    Periodo grande -> frecuencia baja -> bin pequeño. ``k = round(f·N/fs)`` con
    ``f = 1/periodo``.
    """
    f_low = fs / period_high  # periodo mayor -> frecuencia menor
    f_high = fs / period_low
    k_low = max(1, int(round(f_low * n / fs)))
    k_high = min(n // 2, int(round(f_high * n / fs)))
    k_high = max(k_high, k_low)
    return k_low, k_high
