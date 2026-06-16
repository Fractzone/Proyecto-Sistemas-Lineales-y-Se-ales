"""Preprocesamiento de la serie de precios.

Referencia: Oppenheim & Schafer, cap. 10 (análisis de señales aleatorias).

El precio ``P[n]`` es no estacionario (tiene tendencia). El **retorno
logarítmico** ``r[n] = ln(P[n]/P[n-1])`` es aproximadamente estacionario en
media (oscila en torno a ~0) y de varianza más estable, lo que lo hace adecuado
para el análisis espectral, que asume estacionariedad en sentido amplio. Antes
de transformar se elimina la componente continua (DC), pues una media no nula
introduce energía espuria en la frecuencia 0.
"""

from __future__ import annotations

import numpy as np


def log_returns(prices: np.ndarray) -> np.ndarray:
    r"""Retornos logarítmicos: :math:`r[n] = \ln(P[n]/P[n-1])`.

    Equivale a ``diff(ln P)``. Devuelve un array de longitud ``len(prices)-1``.
    """
    p = np.asarray(prices, dtype=float)
    if p.ndim != 1 or p.size < 2:
        raise ValueError("Se requiere un vector de precios con al menos 2 muestras.")
    if np.any(p <= 0):
        raise ValueError("Los precios deben ser positivos para el logaritmo.")
    return np.diff(np.log(p))


def remove_dc(x: np.ndarray) -> np.ndarray:
    r"""Elimina la componente continua: :math:`x[n] - \bar{x}`.

    Quita la energía en la frecuencia 0 (Oppenheim 10.3) para que no domine la
    PSD ni sesgue la entropía espectral.
    """
    x = np.asarray(x, dtype=float)
    return x - x.mean()


def volatility(returns: np.ndarray) -> float:
    """Volatilidad = desviación estándar de los retornos (métrica de resumen)."""
    return float(np.std(np.asarray(returns, dtype=float)))
