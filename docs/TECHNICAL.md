# SPECTRA — Documentación técnica

Proyecto final de **Sistemas Lineales y Señales**. Análisis espectral
retrospectivo de tres activos (SPY, AAL, NFLX) en tres épocas (antes, durante y
después de la pandemia), implementando la teoría de **Oppenheim & Schafer,
*Discrete-Time Signal Processing*** con código propio.

> **Regla del proyecto.** La única primitiva externa de DSP usada en producción
> es `numpy.fft.fft` / `numpy.fft.ifft` (FFT de Cooley-Tukey). Todo lo demás
> —ventanas, Welch, entropía, autocorrelación, coherencia, STFT, FIR, filtrado
> por IFFT, fase— está implementado a mano sobre NumPy. `scipy.signal` aparece
> **solo en los tests** como oráculo de validación.

---

## 1. La FFT como primitiva (lo que sí asumimos)

`numpy.fft.fft` calcula la DFT
`X[k] = Σ_{n=0}^{N-1} x[n] · e^{-j2πkn/N}` mediante el algoritmo de
Cooley-Tukey (complejidad `O(N log N)` en vez de `O(N²)`). Se apoya en la
descomposición *butterfly* y el reordenamiento *bit-reversal*. Para señales
**reales** el espectro es hermítico (`X[N-k] = conj(X[k])`), por lo que basta
con la mitad positiva del espectro (un solo lado) — propiedad que se explota en
todos los estimadores de un lado de este proyecto. *(Oppenheim, cap. 9.)*

---

## 2. Operadores DSP implementados

Convención: frecuencia de muestreo `Fs = 1` muestra/día de trading; frecuencias
en ciclos/día; periodo `T = 1/f` en días.

### 2.1 Preprocesamiento — `spectra_dsp/preprocessing.py` *(cap. 10)*
- **Retorno logarítmico**: `r[n] = ln(P[n]/P[n-1])`. El precio es no estacionario
  (tiene tendencia); el retorno log es aproximadamente estacionario en sentido
  amplio, requisito del análisis espectral.
- **Eliminación de DC**: `x[n] − x̄`, para que la media no nula no inyecte energía
  espuria en `f = 0`.

### 2.2 Ventanas — `spectra_dsp/windows.py` *(cap. 7.2 / 10.2)*
- Hanning: `w[m] = 0.5(1 − cos(2πm/(M−1)))`.
- Hamming: `w[m] = 0.54 − 0.46 cos(2πm/(M−1))`.
- Blackman: `w[m] = 0.42 − 0.5 cos(2πm/(M−1)) + 0.08 cos(4πm/(M−1))`.
- El ventaneo reduce las fugas espectrales (leakage) a costa de ensanchar el
  lóbulo principal.

### 2.3 Estimador de Welch — `spectra_dsp/welch.py` *(cap. 10.3)*
Periodograma modificado por segmento y promedio:

```
U     = (1/M) Σ w²[m]                      (corrección de energía de la ventana)
P_i[k] = 1/(Fs·M·U) · |FFT(x_i·w)[k]|²
P[k]  = (1/K) Σ_i P_i[k]
```

Segmentos solapados al 50 %, ventana por segmento, *detrend* constante por
segmento. Para el espectro de un lado se duplica la potencia de `f > 0` (salvo
DC y Nyquist). Esta normalización coincide con `scaling='density'` de
`scipy.signal.welch`. **Validado**: MSE < 1e-6 contra scipy (`test_welch.py`).

### 2.4 Entropía espectral y régimen — `spectra_dsp/entropy.py`
```
p[k]    = P[k] / Σ P[j]
SE      = − Σ p[k] log₂ p[k]
SE_norm = SE / log₂(N)        ∈ [0, 1]
```
Régimen descriptivo (umbrales por defecto 0.45 / 0.65): `SE_norm < 0.45` →
**Tendencial**; `[0.45, 0.65]` → **Reversivo**; `> 0.65` → **Ruidoso**.
*Describe el pasado; no recomienda operar.*

### 2.5 Autocorrelación y Wiener-Khinchin — `spectra_dsp/autocorr.py` *(cap. 2 / 10.3)*
- Lineal sesgada (panel): `R_xx[m] = (1/N) Σ_n x[n] x[n+m]`.
- **Wiener-Khinchin**: la DFT de la autocorrelación **circular** es exactamente
  el periodograma `(1/N)|X[k]|²`. **Validado** con `atol = 1e-10`
  (`test_wiener_khinchin.py`). La autocorrelación lineal es una aproximación con
  sesgo en retardos grandes; la circular es la que satisface la identidad exacta
  de la DFT.

### 2.6 Densidad espectral cruzada y coherencia — `spectra_dsp/cross_spectrum.py` *(cap. 10.5)*
```
S_AB[k]  = (1/K) Σ_i conj(X_i[k]) Y_i[k]
Coh_AB[k] = |S_AB[k]|² / (P_A[k] · P_B[k])   ∈ [0, 1]
```
**El promediado entre segmentos es esencial**: con un único segmento la
coherencia es idénticamente 1. **Validado**: error relativo < 0.1 % contra
`scipy.signal.coherence` (`test_coherence.py`).

### 2.7 STFT / espectrograma — `spectra_dsp/stft.py` *(cap. 10.3)*
Ventana deslizante con solape, `|FFT(seg·w)|²` por posición → matriz
tiempo-frecuencia. Revela la no estacionariedad dentro de una época.

### 2.8 Filtros FIR windowed-sinc — `spectra_dsp/fir.py` *(cap. 7.5)*
`h_ideal[n] = 2 fc · sinc(2 fc (n − M/2))`, truncada y multiplicada por la
ventana; pasa-banda = `lp(fc_high) − lp(fc_low)`. Aplicación por **convolución
lineal** a mano: `y[n] = Σ_k h[k] x[n−k]`. Respuesta en frecuencia
`|H(e^{jω})|` vía FFT de `h`. **Validado**: ganancia DC unitaria, atenuación de
banda de rechazo y equivalencia con `numpy.convolve` (`test_fir.py`).

### 2.9 Filtrado por bandas vía IFFT — `spectra_dsp/ifft_filter.py` *(cap. 8)*
Máscara ideal hermítica `H[k] = 1` en `[k_low, k_high] ∪ [N−k_high, N−k_low]`,
`x_filt = Re(IFFT(FFT(x)·H))`. Equivale a una **convolución circular** (asume
periodicidad), frente a la convolución **lineal** del FIR.

### 2.10 Ciclo dominante y fase — `spectra_dsp/cycle_phase.py` *(cap. 8)*
`k_peak = argmax P[k]` (k ≠ 0); `T_dom = 1/f_dom`; fase
`φ = atan2(Im X[k], Re X[k])`, `φ% = (φ+π)/(2π)·100`; confianza
`E_dom/E_total`.

### 2.11 Parseval — `spectra_dsp/metrics.py` *(cap. 8.7)*
`Σ|x[n]|² = (1/N) Σ|X[k]|²`. **Validado** con residual < 1e-12
(`test_parseval.py`).

---

## 3. Concepto de la asignatura → dónde vive en el código

| Concepto (Oppenheim) | Capítulo | Módulo |
|---|---|---|
| DFT / FFT | 8, 9 | `numpy.fft` (primitiva) |
| Ventanas (Hanning/Hamming/Blackman) | 7.2, 10.2 | `windows.py` |
| Estimación espectral no paramétrica (Welch) | 10.3 | `welch.py` |
| Autocorrelación / Wiener-Khinchin | 2, 10.3 | `autocorr.py` |
| Espectro cruzado y coherencia | 10.5 | `cross_spectrum.py` |
| Análisis tiempo-frecuencia (STFT) | 10.3 | `stft.py` |
| Diseño FIR por ventaneo + convolución | 7.5, 2 | `fir.py` |
| Filtrado por máscara espectral (conv. circular) | 8 | `ifft_filter.py` |
| Magnitud y fase de la DFT | 8 | `cycle_phase.py` |
| Teorema de Parseval | 8.7 | `metrics.py` |
| Entropía de Shannon sobre la PSD | — | `entropy.py` |

---

## 4. Resultados y observaciones (datos reales, N = 1024, Hanning)

| Activo / época | Régimen | Ciclo dom. | Confianza | Coherencia vs SPY | Volatilidad |
|---|---|---|---|---|---|
| SPY / antes | Ruidoso | ~2 d | 1.7 % | (benchmark) | **0.0093** |
| AAL / antes | Ruidoso | ~53 d | 2.6 % | 0.65 | 0.0242 |
| AAL / durante | Ruidoso | ~5 d | 2.3 % | **0.12** | **0.0508** |
| NFLX / durante | Ruidoso | ~2 d | 3.8 % | 0.42 | 0.0252 |
| NFLX / después | Ruidoso | ~2 d | 2.2 % | **0.82** | 0.0373 |

Lecturas:
- **Espectro casi plano (régimen "Ruidoso") en todos los casos.** Es el resultado
  esperado y honesto: los retornos diarios de activos líquidos se aproximan a
  ruido blanco (hipótesis de mercado eficiente). Ningún ciclo concentra energía
  significativa (confianza siempre baja), por lo que el "ciclo dominante" debe
  leerse con cautela.
- **La historia la cuentan la volatilidad y la coherencia**, no un ciclo:
  - **AAL durante la pandemia**: volatilidad máxima (0.0508) y coherencia mínima
    con el mercado (0.12) → el sector aerolíneas se **desacopló** y entró en alta
    turbulencia.
  - **NFLX después**: coherencia alta (0.82) → tras su auge, se mueve **muy
    sincronizado** con el mercado amplio.
  - **SPY**: la menor volatilidad (0.0093), como corresponde al índice agregado.
- El **espectrograma STFT** dentro de "durante" hace visible el shock de
  volatilidad de marzo 2020 como una banda de energía concentrada en el tiempo.

---

## 5. Limitaciones

- **El mercado no es un sistema LTI puro.** El análisis espectral asume
  estacionariedad y linealidad que solo se cumplen de forma aproximada; por eso
  se segmenta por épocas y se usa la STFT.
- **Coherencia ≠ causalidad.** Una coherencia alta indica relación lineal en
  frecuencia, no que un activo cause el movimiento del otro.
- **El "ciclo dominante" es frágil** cuando el espectro es plano: `argmax` sobre
  ruido devuelve un bin esencialmente aleatorio. La métrica de **confianza**
  (`E_dom/E_total`) explicita esa fragilidad.
- **Umbrales heurísticos.** Las fronteras de régimen (0.45 / 0.65) son
  convenciones ajustables desde la UI, no constantes físicas.
- **Sin predicción.** El proyecto es estrictamente **retrospectivo y descriptivo**:
  no contiene señales de trading, backtesting de rentabilidad ni recomendaciones.
