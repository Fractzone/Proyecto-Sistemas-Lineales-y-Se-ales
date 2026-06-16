"""Tests del ciclo dominante y la fase."""

import numpy as np

from spectra_dsp import cycle_phase, welch


def test_dominant_cycle_period():
    t = np.arange(4096)
    period = 20.0  # días
    x = np.sin(2 * np.pi * t / period)
    f, p = welch.welch_psd(x, fs=1.0, nperseg=1024, window="hamming")
    dom = cycle_phase.dominant_cycle(f, p)
    assert abs(dom["period_days"] - period) < 1.0
    assert dom["energy_ratio"] > 0.1


def test_phase_of_sine_vs_cosine():
    n = 1024
    t = np.arange(n)
    f0 = 8 / n  # bin exacto 8
    sine = np.sin(2 * np.pi * f0 * t)
    cosine = np.cos(2 * np.pi * f0 * t)
    ph_sin = cycle_phase.phase_at_frequency(sine, f0, fs=1.0)["phase_rad"]
    ph_cos = cycle_phase.phase_at_frequency(cosine, f0, fs=1.0)["phase_rad"]
    # cos tiene fase ~0; sin tiene fase ~ -pi/2 (X[k] = -i*N/2 para seno).
    assert abs(ph_cos) < 0.05
    assert abs(ph_sin + np.pi / 2) < 0.05


def test_phase_pct_range():
    n = 512
    t = np.arange(n)
    x = np.cos(2 * np.pi * 5 * t / n)
    out = cycle_phase.phase_at_frequency(x, 5 / n)
    assert 0.0 <= out["phase_pct"] <= 100.0
