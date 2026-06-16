"""Entropía espectral y clasificación descriptiva de régimen.

La entropía espectral aplica la entropía de Shannon a la PSD normalizada tratada
como una distribución de probabilidad sobre las frecuencias. Mide cuán
"repartida" está la energía:

- Energía concentrada en pocas frecuencias  -> entropía baja  -> señal estructurada/tendencial.
- Energía repartida uniformemente (ruido blanco) -> entropía máxima -> señal ruidosa.

Fórmulas:
    p[k]    = P[k] / Σ_j P[j]
    SE      = - Σ_k p[k] · log2(p[k])
    SE_norm = SE / log2(N)        (N = número de bins; SE_norm ∈ [0, 1])

La etiqueta de régimen es **puramente descriptiva del pasado** y NO constituye
una recomendación de inversión ni una predicción.
"""

from __future__ import annotations

import numpy as np

# Etiquetas de régimen (descriptivas).
REGIME_TREND = "Tendencial"
REGIME_REVERT = "Reversivo"
REGIME_NOISE = "Ruidoso"


def spectral_entropy(psd: np.ndarray) -> tuple[float, float]:
    """Entropía espectral (bits) y su versión normalizada en [0, 1].

    Se excluyen bins no positivos al normalizar y se usa la convención
    ``0·log2(0) = 0``.
    """
    p = np.asarray(psd, dtype=float)
    p = p[p > 0]
    total = p.sum()
    if total <= 0 or p.size < 2:
        return 0.0, 0.0
    p = p / total
    se = float(-np.sum(p * np.log2(p)))
    se_norm = se / np.log2(p.size)
    return se, float(np.clip(se_norm, 0.0, 1.0))


def regime_label(se_norm: float, eps_low: float = 0.45, eps_high: float = 0.65) -> str:
    """Etiqueta descriptiva del régimen según la entropía normalizada.

    - ``SE_norm < eps_low``        -> Tendencial (energía concentrada).
    - ``eps_low <= SE_norm < eps_high`` -> Reversivo (estructura parcial).
    - ``SE_norm >= eps_high``      -> Ruidoso (energía repartida).

    Describe el comportamiento histórico del segmento; no recomienda operar.
    """
    if se_norm < eps_low:
        return REGIME_TREND
    if se_norm < eps_high:
        return REGIME_REVERT
    return REGIME_NOISE
