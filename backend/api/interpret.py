"""Generación del párrafo interpretativo en español (descriptivo, no predictivo).

El texto resume, en lenguaje natural, lo que el análisis espectral reveló sobre
el comportamiento *pasado* del par (activo, época). Deja explícito que NO es una
recomendación de inversión ni una predicción.
"""

from __future__ import annotations

from data import config
from spectra_dsp import entropy

_REGIME_DESC = {
    entropy.REGIME_TREND: (
        "la energía espectral está concentrada en pocas frecuencias, lo que indica "
        "un comportamiento marcadamente estructurado/tendencial en el periodo"
    ),
    entropy.REGIME_REVERT: (
        "la energía se reparte de forma intermedia, compatible con dinámicas de "
        "reversión parcial alrededor de un ciclo"
    ),
    entropy.REGIME_NOISE: (
        "la energía está muy repartida entre frecuencias, cercana a ruido blanco, "
        "sin un ciclo claramente dominante"
    ),
}


def _confidence_word(conf: float) -> str:
    if conf >= 0.15:
        return "nítido"
    if conf >= 0.06:
        return "moderado"
    return "débil"


def build_interpretation(
    asset: str,
    epoch: str,
    benchmark: str,
    regime: str,
    period_days: float,
    confidence: float,
    volatility: float,
    coherence_at_dom: float,
    se_norm: float,
) -> str:
    asset_info = config.ASSETS[asset]
    epoch_info = config.EPOCHS[epoch]
    regime_desc = _REGIME_DESC.get(regime, "")
    conf_word = _confidence_word(confidence)

    coh_txt = (
        f"alta ({coherence_at_dom:.2f})"
        if coherence_at_dom >= 0.6
        else f"moderada ({coherence_at_dom:.2f})"
        if coherence_at_dom >= 0.3
        else f"baja ({coherence_at_dom:.2f})"
    )
    mkt = f"mercado ({benchmark})"
    coh_phrase = (
        f"fuertemente sincronizado con el {mkt}"
        if coherence_at_dom >= 0.6
        else f"parcialmente acoplado al {mkt}"
        if coherence_at_dom >= 0.3
        else f"desacoplado del {mkt}"
    )

    if asset == benchmark:
        coh_sentence = (
            "Como es el activo de referencia, la coherencia consigo mismo no se reporta."
        )
    else:
        coh_sentence = (
            f"En el ciclo dominante su coherencia con el mercado es {coh_txt}, es decir, "
            f"estuvo {coh_phrase}."
        )

    return (
        f"Durante la época «{epoch_info.label}», {asset} ({asset_info.name}) mostró un "
        f"régimen {regime.lower()}: {regime_desc}. El análisis de Welch identifica un "
        f"ciclo dominante de aproximadamente {period_days:.1f} días de trading, con un "
        f"pico espectral {conf_word} (energía relativa {confidence:.1%}) y una "
        f"volatilidad de retornos de {volatility:.4f}. {coh_sentence} "
        f"La entropía espectral normalizada fue {se_norm:.2f}. "
        f"Esta lectura es estrictamente retrospectiva (describe el pasado del segmento) "
        f"y no constituye una predicción ni una recomendación de inversión."
    )
