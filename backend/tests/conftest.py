"""Señales sintéticas reutilizables para los tests del motor DSP."""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def rng():
    return np.random.default_rng(20240614)


@pytest.fixture
def sine_plus_noise(rng):
    """Senoide a 0.1 ciclos/muestra + ruido blanco; longitud 4096."""
    n = 4096
    t = np.arange(n)
    x = np.sin(2 * np.pi * 0.1 * t) + 0.5 * rng.standard_normal(n)
    return x


@pytest.fixture
def coupled_pair(rng):
    """Par de señales con coherencia parcial: y = x filtrada + ruido propio."""
    n = 8192
    t = np.arange(n)
    common = np.sin(2 * np.pi * 0.05 * t) + np.sin(2 * np.pi * 0.2 * t)
    x = common + 0.5 * rng.standard_normal(n)
    y = common + 0.5 * rng.standard_normal(n)
    return x, y


@pytest.fixture
def two_tone():
    """Suma de dos senoides en bins exactos de una DFT de N=256."""
    n = 256
    t = np.arange(n)
    k1, k2 = 8, 40
    comp1 = np.sin(2 * np.pi * k1 * t / n)
    comp2 = 0.7 * np.sin(2 * np.pi * k2 * t / n)
    return n, k1, k2, comp1, comp2, comp1 + comp2
