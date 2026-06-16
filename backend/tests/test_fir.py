"""Tests del diseño FIR windowed-sinc y la convolución lineal."""

import numpy as np

from spectra_dsp import fir


def test_lowpass_dc_gain_unity():
    h = fir.sinc_lowpass(101, fc=0.1, window="hamming")
    assert abs(np.sum(h) - 1.0) < 1e-12  # ganancia unitaria en DC


def test_lowpass_passband_and_stopband():
    h = fir.sinc_lowpass(101, fc=0.1, window="hamming")
    f, mag = fir.frequency_response(h, n_fft=2048)
    # Banda de paso: |H| ~ 1 cerca de DC.
    passband = mag[f < 0.06]
    assert np.all(np.abs(passband - 1.0) < 0.05)
    # Banda de rechazo: fuerte atenuación lejos del corte.
    stopband = mag[f > 0.18]
    assert np.max(stopband) < 0.05


def test_bandpass_rejects_dc():
    h = fir.fir_bandpass(101, fc_low=0.1, fc_high=0.2, window="hamming")
    assert abs(np.sum(h)) < 1e-3  # ganancia ~0 en DC


def test_convolve_matches_numpy(rng):
    x = rng.standard_normal(200)
    h = fir.sinc_lowpass(31, fc=0.2)
    assert np.allclose(fir.convolve(x, h, mode="full"), np.convolve(x, h, mode="full"))
    assert fir.convolve(x, h, mode="same").size == x.size


def test_bandpass_isolates_tone():
    n = 1024
    t = np.arange(n)
    low = np.sin(2 * np.pi * 0.05 * t)
    mid = np.sin(2 * np.pi * 0.15 * t)
    high = np.sin(2 * np.pi * 0.35 * t)
    x = low + mid + high
    h = fir.fir_bandpass(201, fc_low=0.12, fc_high=0.18, window="blackman")
    y = fir.convolve(x, h, mode="same")
    # La componente media debe sobrevivir mucho más que las otras.
    mid_corr = abs(np.corrcoef(y[100:-100], mid[100:-100])[0, 1])
    assert mid_corr > 0.9
