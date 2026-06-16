"""Teorema de Wiener-Khinchin: PSD = DFT de la autocorrelación."""

import numpy as np

from spectra_dsp import autocorr, welch


def _onesided_periodogram(x, fs=1.0):
    n = x.size
    full = (np.abs(np.fft.fft(x)) ** 2) / (fs * n)
    out = full[: n // 2 + 1].copy()
    if n % 2 == 0:
        out[1:-1] *= 2.0
    else:
        out[1:] *= 2.0
    return out


def test_wiener_khinchin_equals_periodogram(rng):
    x = rng.standard_normal(512)
    _, psd_wk = autocorr.wiener_khinchin_psd(x, fs=1.0)
    psd_ref = _onesided_periodogram(x)
    assert np.allclose(psd_wk, psd_ref, atol=1e-10)


def test_circular_autocorr_zero_lag_is_power(rng):
    x = rng.standard_normal(256)
    rc = autocorr.circular_autocorrelation(x)
    assert abs(rc[0] - np.mean(x ** 2)) < 1e-12


def test_wk_close_to_welch_shape(rng):
    # PSD vía W-K (periodograma) y vía Welch comparten la forma global.
    t = np.arange(4096)
    x = np.sin(2 * np.pi * 0.15 * t) + 0.5 * rng.standard_normal(4096)
    f_w, p_w = welch.welch_psd(x, nperseg=512)
    f_k, p_k = autocorr.wiener_khinchin_psd(x)
    # Ambos deben tener el pico cerca de 0.15.
    assert abs(f_w[np.argmax(p_w[1:]) + 1] - 0.15) < 0.01
    assert abs(f_k[np.argmax(p_k[1:]) + 1] - 0.15) < 0.01
