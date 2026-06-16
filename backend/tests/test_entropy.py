"""Tests de la entropía espectral y la clasificación de régimen."""

import numpy as np

from spectra_dsp import entropy


def test_white_noise_high_entropy(rng):
    # PSD ~ plana => entropía normalizada cercana a 1.
    psd = np.abs(rng.standard_normal(512)) ** 2 + 1.0
    _, se_norm = entropy.spectral_entropy(psd)
    assert se_norm > 0.9


def test_single_tone_low_entropy():
    psd = np.full(512, 1e-9)
    psd[37] = 1.0  # toda la energía en un bin
    _, se_norm = entropy.spectral_entropy(psd)
    assert se_norm < 0.1


def test_regime_labels():
    assert entropy.regime_label(0.3) == entropy.REGIME_TREND
    assert entropy.regime_label(0.55) == entropy.REGIME_REVERT
    assert entropy.regime_label(0.8) == entropy.REGIME_NOISE


def test_regime_custom_thresholds():
    assert entropy.regime_label(0.5, eps_low=0.6, eps_high=0.8) == entropy.REGIME_TREND
