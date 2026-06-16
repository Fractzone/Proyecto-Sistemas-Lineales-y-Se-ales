"""Valida el estimador de Welch propio contra scipy.signal.welch (ORÁCULO).

scipy.signal solo se usa aquí, en los tests, como referencia.
"""

import numpy as np
import scipy.signal as ss

from spectra_dsp import welch
from spectra_dsp.windows import get_window


def test_welch_matches_scipy(sine_plus_noise):
    x = sine_plus_noise
    M = 256
    w = get_window("hanning", M)

    f_mine, p_mine = welch.welch_psd(
        x, fs=1.0, nperseg=M, window="hanning", overlap=0.5, detrend=True
    )
    f_sp, p_sp = ss.welch(
        x,
        fs=1.0,
        window=w,
        nperseg=M,
        noverlap=M // 2,
        detrend="constant",
        scaling="density",
        return_onesided=True,
    )

    assert np.allclose(f_mine, f_sp)
    mse = float(np.mean((p_mine - p_sp) ** 2))
    assert mse < 1e-6, f"MSE Welch propio vs scipy = {mse}"


def test_welch_peak_location(sine_plus_noise):
    f, p = welch.welch_psd(sine_plus_noise, fs=1.0, nperseg=512, window="hamming")
    # El pico (ignorando DC) debe caer cerca de 0.1 ciclos/muestra.
    k = int(np.argmax(p[1:]) + 1)
    assert abs(f[k] - 0.1) < 0.01


def test_welch_clamps_long_nperseg():
    x = np.random.default_rng(0).standard_normal(300)
    f, p = welch.welch_psd(x, nperseg=4096)
    assert p.size == 300 // 2 + 1
