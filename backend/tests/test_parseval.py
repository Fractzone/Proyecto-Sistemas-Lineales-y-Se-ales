"""Teorema de Parseval: conservación de energía tiempo <-> frecuencia."""

import numpy as np

from spectra_dsp import metrics


def test_parseval_random(rng):
    x = rng.standard_normal(1000)
    assert metrics.parseval_residual(x) < 1e-12


def test_parseval_signal():
    t = np.arange(2048)
    x = np.sin(2 * np.pi * 0.07 * t) + 0.3 * np.cos(2 * np.pi * 0.23 * t)
    e_t = metrics.energy(x)
    e_f = metrics.spectral_energy(x)
    assert abs(e_t - e_f) / e_t < 1e-12
