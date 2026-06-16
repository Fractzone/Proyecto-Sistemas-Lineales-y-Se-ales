"""Ciclo dominante, fase y confianza de la señal.

Referencia: Oppenheim & Schafer, cap. 8 (magnitud y fase de la DFT).

- **Ciclo dominante**: bin de mayor potencia en la PSD (ignorando DC). Su
  frecuencia ``f_dom`` define un periodo ``T_dom = 1/f_dom`` en días de trading.
- **Fase**: ángulo de la DFT en el bin dominante,
  ``φ = atan2(Im X[k], Re X[k])``, normalizado a porcentaje del ciclo.
- **Confianza / limpieza**: energía relativa del bin dominante respecto al total,
  ``E_dom / E_total`` (alto = ciclo nítido; bajo = espectro repartido).
"""

from __future__ import annotations

import numpy as np


def dominant_cycle(freqs: np.ndarray, psd: np.ndarray) -> dict:
    """Localiza el bin de mayor potencia (excluyendo DC) y describe su ciclo.

    Returns
    -------
    dict con ``k_peak`` (índice en el array de un lado), ``f_dom`` (ciclos/día),
    ``period_days`` (1/f_dom) y ``energy_ratio`` (E_dom/E_total).
    """
    freqs = np.asarray(freqs, dtype=float)
    psd = np.asarray(psd, dtype=float)
    if psd.size < 2:
        raise ValueError("PSD demasiado corta.")

    # Excluir DC (k=0) de la búsqueda del pico.
    k_peak = int(np.argmax(psd[1:]) + 1)
    f_dom = float(freqs[k_peak])
    period = float(1.0 / f_dom) if f_dom > 0 else float("inf")
    total = float(psd.sum())
    energy_ratio = float(psd[k_peak] / total) if total > 0 else 0.0
    return {
        "k_peak": k_peak,
        "f_dom": f_dom,
        "period_days": period,
        "energy_ratio": energy_ratio,
    }


def phase_at_frequency(x: np.ndarray, f_dom: float, fs: float = 1.0) -> dict:
    r"""Fase de la señal en la frecuencia ``f_dom`` (ciclos/día).

    Calcula la DFT de longitud completa, localiza el bin más cercano a ``f_dom`` y
    devuelve ``φ = atan2(Im, Re)`` en radianes y como porcentaje del ciclo
    ``φ_pct = (φ + π)/(2π)·100``.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    spectrum = np.fft.fft(x)
    k = int(round(f_dom * n / fs))
    k = min(max(k, 0), n - 1)
    phase = float(np.arctan2(spectrum[k].imag, spectrum[k].real))
    phase_pct = float((phase + np.pi) / (2.0 * np.pi) * 100.0)
    return {"phase_rad": phase, "phase_pct": phase_pct, "bin": k}
