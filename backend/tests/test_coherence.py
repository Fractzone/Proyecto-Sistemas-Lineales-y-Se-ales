"""Valida la coherencia propia contra scipy.signal.coherence (ORÁCULO)."""

import numpy as np
import scipy.signal as ss

from spectra_dsp import cross_spectrum
from spectra_dsp.windows import get_window


def test_coherence_matches_scipy(coupled_pair):
    x, y = coupled_pair
    M = 512
    w = get_window("hanning", M)

    f_mine, c_mine = cross_spectrum.coherence(
        x, y, fs=1.0, nperseg=M, window="hanning", overlap=0.5, detrend=True
    )
    f_sp, c_sp = ss.coherence(
        x, y, fs=1.0, window=w, nperseg=M, noverlap=M // 2, detrend="constant"
    )

    assert np.allclose(f_mine, f_sp)
    rel = float(np.max(np.abs(c_mine - c_sp)) / np.max(c_sp))
    assert rel < 1e-3, f"Error relativo coherencia vs scipy = {rel}"


def test_coherence_bounded(coupled_pair):
    x, y = coupled_pair
    _, c = cross_spectrum.coherence(x, y, nperseg=256)
    assert np.all(c >= 0.0) and np.all(c <= 1.0)


def test_high_coherence_at_common_tone(coupled_pair):
    x, y = coupled_pair
    f, c = cross_spectrum.coherence(x, y, nperseg=512)
    k = int(np.argmin(np.abs(f - 0.05)))
    assert c[k] > 0.8  # fuerte acoplamiento en el tono común
