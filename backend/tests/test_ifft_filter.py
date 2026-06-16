"""Tests del filtrado por bandas vía máscara + IFFT."""

import numpy as np

from spectra_dsp import ifft_filter


def test_bandpass_ifft_isolates_bin(two_tone):
    n, k1, k2, comp1, comp2, x = two_tone
    # Conservar solo la banda alrededor de k1 (y su reflejo hermítico).
    filtered = ifft_filter.bandpass_ifft(x, k_low=k1 - 2, k_high=k1 + 2)
    assert np.allclose(filtered, comp1, atol=1e-9)


def test_bandpass_ifft_removes_other_bin(two_tone):
    n, k1, k2, comp1, comp2, x = two_tone
    filtered = ifft_filter.bandpass_ifft(x, k_low=k1 - 2, k_high=k1 + 2)
    # La energía en k2 debe quedar eliminada.
    spec = np.abs(np.fft.fft(filtered))
    assert spec[k2] < 1e-9


def test_output_is_real(two_tone):
    n, k1, k2, comp1, comp2, x = two_tone
    filtered = ifft_filter.bandpass_ifft(x, k_low=k1 - 1, k_high=k1 + 1)
    assert np.isrealobj(filtered)


def test_band_from_period():
    k_low, k_high = ifft_filter.band_from_period(256, fs=1.0, period_low=8, period_high=64)
    # periodo 64 -> f=1/64 -> bin 4 ; periodo 8 -> f=1/8 -> bin 32
    assert k_low == 4 and k_high == 32
