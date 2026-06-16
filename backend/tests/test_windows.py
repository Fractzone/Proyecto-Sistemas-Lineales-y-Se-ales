"""Tests de las ventanas (propiedades analíticas conocidas)."""

import numpy as np

from spectra_dsp import windows


def test_hanning_endpoints_zero():
    w = windows.hanning(64)
    assert w[0] == 0.0
    assert abs(w[-1]) < 1e-12


def test_hamming_endpoints():
    w = windows.hamming(64)
    assert abs(w[0] - 0.08) < 1e-12
    assert abs(w[-1] - 0.08) < 1e-12


def test_blackman_endpoints_near_zero():
    w = windows.blackman(64)
    assert abs(w[0]) < 1e-12


def test_symmetry():
    for fn in (windows.hanning, windows.hamming, windows.blackman):
        w = fn(101)
        assert np.allclose(w, w[::-1])


def test_hanning_peak_center_odd():
    w = windows.hanning(101)
    assert abs(w[50] - 1.0) < 1e-12


def test_dispatcher_and_unknown():
    assert np.allclose(windows.get_window("hann", 32), windows.hanning(32))
    try:
        windows.get_window("kaiser", 32)
    except ValueError:
        pass
    else:
        raise AssertionError("Debería rechazar ventana desconocida.")
