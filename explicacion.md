# Guía de conceptos de SPECTRA

Explicación completa de cada concepto, gráfica y métrica del dashboard,
con nivel simple y nivel técnico-académico (Sistemas Lineales y Señales).

---

## 1. La señal que se analiza: retornos logarítmicos

### Explicación simple
En vez de analizar el precio directamente (que sube con el tiempo y no es comparable
entre activos), SPECTRA trabaja con **cuánto cambia el precio cada día en
porcentaje**. Concretamente, usa el logaritmo de ese cambio:

```
retorno_hoy = ln(precio_hoy / precio_ayer)
```

Un retorno positivo = el precio subió. Uno negativo = bajó. La magnitud indica cuánto.

### Explicación técnica (materia)
La serie de **retornos logarítmicos** es la señal discreta `r[n] = ln(P[n]/P[n−1])`.
Se prefiere a los retornos simples porque:
- Es **estacionaria en sentido amplio (WSS)** en condiciones de mercado normales
  (media y varianza constantes en el tiempo), requisito para que la PSD tenga
  interpretación válida (cap. 10.1 de Oppenheim & Schafer).
- Tiene propiedades aditivas en el tiempo: `r_1to3 = r_1 + r_2 + r_3`.

Antes del análisis espectral se **elimina la componente DC** (media de la señal),
que de otro modo dominaría el bin `k=0` y distorsionaría la estimación.

**Código:** `spectra_dsp/preprocessing.py` → `log_returns`, `remove_dc`.

---

## 2. Frecuencia y periodo

### Explicación simple
La frecuencia mide **qué tan rápido oscila algo**. En este proyecto la unidad es
**ciclos por día de trading**: frecuencia 0.1 significa un ciclo completo cada 10 días.
El **periodo** es lo inverso: `T = 1 / frecuencia`. Si f = 0.1 → T = 10 días.

Frecuencia 0 (DC) = la tendencia promedio constante (no oscilatoria).
Frecuencia 0.5 = Nyquist = la más rápida posible con datos diarios (ciclo cada 2 días).

### Explicación técnica (materia)
Con frecuencia de muestreo `Fs = 1.0` muestra/día, la **frecuencia digital**
`ω = 2πf/Fs` va de `0` a `π` (ciclos/muestra normalizados, o equivalentemente
`f` va de `0` a `0.5` ciclos/muestra). El **teorema de muestreo de Nyquist-Shannon**
(Oppenheim cap. 4) establece que solo podemos representar componentes hasta `Fs/2 = 0.5`
ciclos/día; cualquier ciclo más rápido sería aliasing.

Dado que los datos son diarios de trading (~252 días/año):
- `f = 0.004` → ciclo anual (~252 días)
- `f = 0.02`  → ciclo mensual (~50 días)
- `f = 0.1`   → ciclo de ~10 días

---

## 3. Ventanas espectrales (Hanning, Hamming, Blackman, Rectangular)

### Explicación simple
Imagina que tomas una foto de solo un pedazo de la señal (un segmento). En los bordes
del segmento la señal se "corta" abruptamente, como si pusieran una pared. Eso
crea ruido artificial en el espectro (fuga espectral). Las ventanas **suavizan los
bordes** multiplicando la señal por una curva que vale 0 en los extremos y 1 en
el centro, para que el corte sea gradual.

Cada ventana tiene sus ventajas:
- **Rectangular (sin ventana):** máxima resolución pero mucha fuga. Útil como referencia.
- **Hanning:** buen balance general. La más usada en análisis espectral.
- **Hamming:** lóbulo lateral un poco menor que Hanning; aún más limpia.
- **Blackman:** la más "limpia" (lóbulos laterales muy bajos) pero la más ancha en
  resolución. Ideal cuando importa separar frecuencias con niveles de energía muy distintos.

### Explicación técnica (materia)
La **fuga espectral (spectral leakage)** ocurre porque la DFT asume periodicidad
implícita en el bloque analizado. Si la señal no es periódica exactamente en `M`
muestras, los extremos crean una discontinuidad que "filtra" energía de una
frecuencia hacia los bins vecinos (Oppenheim cap. 10.2).

Las ventanas se aplican **antes de la FFT**: `x_ventaneado[m] = x[m] · w[m]`.

Fórmulas implementadas a mano (`spectra_dsp/windows.py`):

| Ventana | Fórmula w[m], m = 0..M-1 | Lóbulo lateral (aprox.) |
|---|---|---|
| **Hanning** | `0.5·(1 − cos(2πm/(M−1)))` | −31 dB |
| **Hamming** | `0.54 − 0.46·cos(2πm/(M−1))` | −41 dB |
| **Blackman** | `0.42 − 0.5·cos(2πm/(M−1)) + 0.08·cos(4πm/(M−1))` | −57 dB |
| **Rectangular** | `1` | −13 dB |

> **Restricción académica del proyecto:** estas ventanas se implementan desde la
> fórmula matemática. **No se usa** `numpy.hanning`, `numpy.hamming` ni ningún
> equivalente de librería. Referencia: cap. 7.2 / 10.2-10.3.

---

## 4. PSD de Welch (gráfica principal del espectro)

### Explicación simple
La **Densidad Espectral de Potencia (PSD)** dice **cuánta energía hay en cada
frecuencia**. Es la "fotografía" del contenido frecuencial de la señal.

El método de Welch divide la señal en pedazos solapados (por ejemplo, 50% de
solapamiento), calcula el espectro de cada pedazo, y **promedia** todos. Ese
promedio hace que el resultado sea más estable (menos ruidoso) que calcular
el espectro de la señal completa de una sola vez.

En la gráfica del dashboard (eje Y logarítmico):
- Un pico alto = hay mucha energía en esa frecuencia (hay un ciclo claro).
- Un espectro plano = energía igual en todas las frecuencias = ruido blanco.

### Explicación técnica (materia)
El **periodograma de Welch** (Oppenheim cap. 10.3) es un estimador no paramétrico
consistente de la PSD. Para cada segmento ventaneado `x_i`:

```
P_i[k] = (1 / (Fs · U)) · |FFT(x_i · w)[k]|²   donde  U = Σ w²[m]
```

La PSD final es el promedio sobre `K` segmentos:

```
P_Welch[k] = (1/K) · Σ_i P_i[k]
```

El factor `U = Σ w²[m]` es el **factor de corrección de energía de la ventana**,
que garantiza que la potencia total estimada sea consistente independientemente
de la ventana elegida. Sin él, ventanas con poca área (como Blackman) subestimarían
sistemáticamente la potencia.

El **tradeoff sesgo-varianza** está en `K`: más segmentos → menor varianza (más suave)
pero segmentos más cortos → peor resolución en frecuencia. Con `nperseg = N` y
`overlap = 50%`, la resolución frecuencial es `Fs/N` ciclos/día.

**Código:** `spectra_dsp/welch.py` → `welch_psd`.
**Test:** `tests/test_welch.py` valida contra `scipy.signal.welch` con MSE < 1e−6.

---

## 5. Entropía espectral y régimen (Tendencial / Reversivo / Ruidoso)

### Explicación simple
La **entropía espectral** mide **qué tan "ordenado" o "caótico" es el espectro**.

Imagina que la PSD es un histograma de energía. Si toda la energía está concentrada
en una sola frecuencia (una onda pura), el histograma tiene un único pico alto → poco
desorden → entropía baja. Si la energía está perfectamente repartida en todas las
frecuencias (ruido puro), el histograma es completamente plano → máximo desorden →
entropía máxima.

Los tres regímenes del dashboard:
- **Tendencial (SE < 45%):** la señal tiene una o pocas frecuencias dominantes,
  como una onda clara. El mercado se movía en una dirección definida.
- **Reversivo (45% ≤ SE < 65%):** energía parcialmente estructurada. Hay
  cierta organización pero también ruido. El mercado oscilaba sin tendencia clara.
- **Ruidoso (SE ≥ 65%):** la energía está casi uniformemente repartida en todo el
  espectro. Se comporta como ruido blanco. No hay ciclo dominante identificable.

### Explicación técnica (materia)
Se aplica la **entropía de Shannon** (teoría de la información) a la PSD normalizada
tratada como distribución de probabilidad sobre las frecuencias:

```
p[k]    = P[k] / Σ_j P[j]          (normalizar la PSD para que sume 1)
SE      = −Σ_k p[k] · log2(p[k])   (entropía en bits)
SE_norm = SE / log2(N_bins)         (normalizar a [0,1])
```

- `SE_norm = 0` → toda la energía en un solo bin (señal monocromática perfecta).
- `SE_norm = 1` → energía idénticamente distribuida en todos los bins (ruido blanco).

Los umbrales (0.45 / 0.65) son **heurísticos y configurables** en el dashboard.
No tienen respaldo teórico universal; son parámetros del modelo descriptivo.

**Código:** `spectra_dsp/entropy.py` → `spectral_entropy`, `regime_label`.

---

## 6. Autocorrelación y el teorema de Wiener-Khinchin

### Explicación simple
La **autocorrelación** responde a: "¿si el retorno de hoy fue positivo, el de
dentro de X días tiende también a ser positivo o negativo?" Mide la memoria de
la señal consigo misma en distintos retardos (lags).

- Barra alta en lag 1 → hay correlación de un día para el otro (tendencia).
- Barra alta en lag 20 → hay un ciclo mensual.
- Barras todas cerca de cero → la señal no tiene "memoria" (ruido blanco).

### Explicación técnica (materia)
La **función de autocorrelación (ACF)** es:

```
R[m] = (1/N) · Σ_n x[n] · x[n+m]
```

El **teorema de Wiener-Khinchin** (Oppenheim cap. 2.9 / 10.3) establece que la PSD
es la **DFT de la ACF**:

```
P[k] = DFT{R[m]}
```

Esto conecta el dominio del tiempo (autocorrelación) con el de frecuencia (PSD) de
forma exacta para señales WSS. En SPECTRA se implementa como la DFT de la ACF
circular, validada numéricamente en `tests/test_wiener_khinchin.py` contra la PSD
de Welch.

**Código:** `spectra_dsp/autocorr.py` → `autocorrelation`, `wiener_khinchin_psd`.

---

## 7. Coherencia con el mercado (vs SPY)

### Explicación simple
La coherencia mide **cuánto se mueven dos señales "al mismo ritmo"** en cada
frecuencia, de 0 a 1:

- **Coherencia = 1** en una frecuencia → esa oscilación de AAL/NFLX está perfectamente
  sincronizada con la del mercado (SPY) a ese ritmo.
- **Coherencia = 0** → en esa frecuencia las dos señales son completamente independientes.
- **Coherencia promedio baja** → el activo se desacopló del mercado (ejemplo: AAL
  durante la pandemia, que colapsó por razones propias de la aviación).

La línea vertical en la gráfica marca la frecuencia del ciclo dominante detectado;
el número mostrado es la coherencia exactamente en ese punto.

### Explicación técnica (materia)
La **coherencia cuadrática** (Oppenheim cap. 10.5) es:

```
C_xy[k] = |S_xy[k]|² / (P_x[k] · P_y[k])     ∈ [0, 1]
```

donde `S_xy[k]` es la **densidad espectral cruzada**:

```
S_xy[k] = (1/K) · Σ_i conj(X_i[k]) · Y_i[k]
```

La coherencia REQUIERE promediar sobre múltiples segmentos. Con un único segmento,
`|S_xy|² = P_x · P_y` siempre, dando coherencia trivialmente 1 en todo el espectro
(Oppenheim nota al pie, cap. 10.5). Por eso en el código se usa `nperseg ≈ N/4`
(~6-8 segmentos), no `nperseg = N`.

> **Bug histórico corregido:** en la primera versión usábamos `nperseg = N` → coherencia
> = 1.00 para todos los casos. Corregido en `api/analysis.py`.

**Código:** `spectra_dsp/cross_spectrum.py` → `cross_spectral_density`, `coherence`.
**Test:** `tests/test_coherence.py` valida contra `scipy.signal.coherence` con error < 0.1%.

---

## 8. Espectrograma STFT (heatmap tiempo-frecuencia)

### Explicación simple
Mientras la PSD de Welch muestra el **promedio total** del contenido frecuencial de
toda la época, el **espectrograma** muestra cómo ese contenido **cambió en el tiempo**.

Es como un video de espectros. El eje horizontal es el tiempo; el vertical,
la frecuencia; el color, la intensidad (cuánta energía). Si aparece una banda
de color brillante que dura solo unos meses, eso significa que hubo una oscilación
temporal en esa frecuencia, que luego desapareció.

### Explicación técnica (materia)
La **Transformada de Fourier de Corto Plazo (STFT)** (Oppenheim cap. 10.3) desliza
una ventana de longitud `M` a pasos de `hop` muestras y calcula la FFT de cada
bloque:

```
X[m, k] = Σ_{n=0}^{M-1} x[m·hop + n] · w[n] · e^{−j2πkn/M}
```

El resultado es la **densidad espectral de potencia en función del tiempo**
(espectrograma). El número de muestras del espectrograma en tiempo es
`n_frames = (N − M) // hop + 1`.

El tradeoff clave de la STFT es entre **resolución temporal** y **resolución
frecuencial**: ventanas cortas dan buena resolución temporal pero mala frecuencial,
y viceversa (principio de incertidumbre de Heisenberg en DSP).

**Código:** `spectra_dsp/stft.py` → `stft_spectrogram`.

---

## 9. Ciclo dominante y confianza

### Explicación simple
El **ciclo dominante** es la frecuencia con más energía en el espectro. Si hay una
oscilación que se repite más que cualquier otra, esta es la que detectamos.

La **confianza** (energy_ratio) dice qué fracción de la energía total corresponde
a ese ciclo: si es 0.02 (2%) significa que el ciclo "ganador" tiene una diferencia
mínima sobre el resto → no hay un ciclo claro, el espectro es casi plano. Si fuera
0.50, ese ciclo concentraría la mitad de toda la energía → muy nítido.

En mercados eficientes, la confianza suele ser < 5%. Es correcto; no es un error.

### Explicación técnica (materia)
El ciclo dominante se obtiene como `argmax(PSD[1:])` (excluyendo DC, bin `k=0`).
Su frecuencia es `f_dom = k_peak · Fs / M` y su periodo `T = 1/f_dom` días.

La **confianza** es la energía relativa:

```
energy_ratio = PSD[k_peak] / Σ_k PSD[k]
```

La **fase** en `f_dom` es el ángulo de la DFT compleja:

```
φ = atan2(Im X[k], Re X[k])     (Oppenheim cap. 8)
φ_pct = (φ + π) / (2π) · 100   (% del ciclo completado)
```

**Código:** `spectra_dsp/cycle_phase.py` → `dominant_cycle`, `phase_at_frequency`.

---

## 10. Filtrado FIR (filtro digital diseñado a mano)

### Explicación simple
Un **filtro pasa-banda FIR** deja pasar solo las oscilaciones dentro de un rango de
frecuencias y bloquea el resto. En el dashboard, se usa para **extraer y mostrar** la
componente del ciclo dominante superpuesta sobre los retornos (línea de color en
el Panel 1).

Por ejemplo: si el ciclo dominante tiene un periodo de 30 días (f ≈ 0.033), el
filtro pasa-banda deja pasar solo las frecuencias entre ~0.024 y ~0.046, bloqueando
todo lo demás.

El resultado es una onda suavizada que muestra si ese ciclo estaba presente en la señal.
Su amplitud muy pequeña confirma que, aunque existe, concentra poca energía.

### Explicación técnica (materia)
Se usa el método **windowed-sinc** (Oppenheim cap. 7.5):

1. La respuesta al impulso ideal de un pasa-bajos con corte `fc` es:
   ```
   h_ideal[n] = 2·fc · sinc(2·fc·(n − M/2))
   ```
2. Se trunca a `num_taps` coeficientes y se **multiplica por una ventana** (Blackman)
   para reducir el rizado de Gibbs en la transición.
3. El **pasa-banda** se obtiene por diferencia de dos pasa-bajos:
   ```
   h_bp = h_lp(fc_high) − h_lp(fc_low)
   ```
4. Se aplica por **convolución lineal** `y[n] = Σ_k h[k]·x[n−k]`,
   implementada a mano sin `numpy.convolve` (bucle explícito sobre coeficientes).

La convolución lineal en el dominio del tiempo equivale a multiplicación en el
dominio de la frecuencia: `Y[k] = H[k] · X[k]`.

**Código:** `spectra_dsp/fir.py` → `sinc_lowpass`, `fir_bandpass`, `convolve`.

---

## 11. Filtrado por IFFT (máscara hermítica en frecuencia)

### Explicación simple
En lugar de diseñar un filtro y convolucionarlo, este método hace lo mismo pero
directamente en el dominio de la frecuencia:

1. Calcula la FFT de la señal.
2. Pone a cero todos los coeficientes fuera de la banda de interés.
3. Calcula la IFFT → recupera solo la parte de la señal en esa banda.

El resultado es muy similar al FIR pero computacionalmente más directo. También
se muestra superpuesto en el Panel 1 (segunda línea de color).

### Explicación técnica (materia)
El **filtrado espectral por máscara hermítica** explota que la DFT de una señal
real tiene simetría conjugada (Oppenheim cap. 8.6):
```
X[N−k] = conj(X[k])
```
La máscara pone `H[k] = 1` para `k ∈ [k_low, k_high] ∪ [N−k_high, N−k_low]`
y `H[k] = 0` en el resto. Aplicarla en frecuencia equivale a **convolución circular**
(no lineal) con la respuesta al impulso de la máscara.

```
x_filtered = real(IFFT(FFT(x) · H))
```

Diferencia con FIR: el FIR es convolución **lineal** (causal, sín artefactos
de periodicidad); la IFFT es convolución **circular** (implica periodicidad en los
extremos). Para señales largas la diferencia es mínima.

**Código:** `spectra_dsp/ifft_filter.py` → `bandpass_ifft`.

---

## 12. Parseval y energía total

### Explicación simple
El **teorema de Parseval** dice que la energía total de una señal en el tiempo es
igual a la energía calculada desde su espectro. Es una prueba de consistencia:
si los dos cálculos coinciden, el análisis espectral fue correcto.

### Explicación técnica (materia)
Parseval (Oppenheim cap. 8.7):

```
Σ |x[n]|²   =   (1/N) · Σ |X[k]|²
```

Se verifica numéricamente en `tests/test_parseval.py` con error relativo < 1e−12,
confirmando que no se pierde ni se inventa energía en ninguna parte del pipeline.

---

## 13. Qué muestra cada panel del dashboard

### Panel 1 — Serie temporal
- **Precio de cierre ajustado:** la curva superior, en USD. Muestra la tendencia
  macro del activo en la época.
- **Retornos logarítmicos:** la señal principal de análisis (oscila alrededor de 0).
  Su dispersión visual corresponde a la volatilidad.
- **Componente dominante IFFT / FIR:** las líneas de color superpuestas sobre los
  retornos. Son la parte de la señal que corresponde al ciclo de mayor energía,
  reconstruida mediante los dos métodos de filtrado. Normalmente tienen amplitud
  muy pequeña (< 10% de la señal), lo que confirma visualmente que el ciclo no es dominante.

### Panel 2 — Espectro
- **PSD de Welch (log-log):** el espectro completo. Un espectro plano (línea horizontal)
  = ruido blanco. La línea vertical indica el ciclo dominante detectado. El rótulo
  muestra la frecuencia y el periodo en días.
- **Espectrograma STFT (heatmap):** evolución del espectro a lo largo del tiempo de
  la época. Colores cálidos = alta energía; fríos = poca. Si el espectrograma es
  uniforme y sin patrones, confirma la naturaleza ruidosa de la señal.
- **Gauge de entropía / régimen:** barra que va de 0 (señal pura) a 1 (ruido total),
  con la etiqueta de régimen coloreada.

### Panel 3 — Relación con el mercado
- **Coherencia vs SPY:** gráfica de coherencia en función de la frecuencia. La
  línea vertical marca el ciclo dominante; el número es la coherencia ahí.
  Coherencia alta = ese ciclo está sincronizado con el mercado.
- **Autocorrelación:** barras de correlación de la señal consigo misma en cada lag
  (retardo en días). Barras pequeñas en todos los lags → la señal es casi white noise
  (cada día es casi independiente del anterior).

### Panel 4 — Resumen
Tarjeta con todas las métricas clave:
- **Régimen:** etiqueta descriptiva.
- **Ciclo dominante:** periodo en días de trading y frecuencia.
- **Fase:** posición actual en el ciclo (0–100%).
- **Confianza:** fracción de energía del ciclo dominante; mide cuán pronunciado es el pico.
- **Volatilidad:** desviación estándar de los retornos diarios.
- **Coherencia en f_dom:** sincronización con el mercado justo en la frecuencia del ciclo.
- **Interpretación:** párrafo auto-generado que cruza todas las métricas con el contexto
  de la época (pandemia, crisis, etc.). Siempre termina recordando que es descriptivo-retrospectivo.

### Tabla comparativa (modo comparación)
Permite ver las métricas de los 9 pares (activo × época) de un vistazo, facilitando
la comparación: por ejemplo, verificar que AAL tiene la volatilidad más alta
durante la pandemia, o que NFLX aumenta su coherencia con el mercado después de ella.

---

## 14. Por qué todos los análisis muestran "Ruidoso"

Esta pregunta tiene una respuesta clara que combina finanzas y teoría de señales.

### La respuesta directa

Los **retornos logarítmicos diarios de acciones son, esencialmente, ruido blanco**.
Esto no es un error del análisis; es el resultado correcto y el que predice la teoría.

### Explicación con analogía

Imagina que grabas el sonido de una multitud en un estadio. Hay miles de personas
hablando al mismo tiempo, cada una a su propio ritmo, sin coordinarse. El resultado
es ruido. No hay una frecuencia dominante. Si intentas encontrar "la melodía" de la
multitud, no la encontrarás porque no existe.

El mercado de valores funciona similar: hay millones de participantes comprando
y vendiendo simultáneamente, reaccionando a noticias distintas, con horizontes
de tiempo distintos. El resultado agregado en retornos diarios se aproxima mucho
a ruido blanco.

### La razón teórica: Hipótesis del Mercado Eficiente (EMH)

La **EMH (Efficient Market Hypothesis, Fama 1970)** afirma que los precios ya
incorporan toda la información disponible. Consecuencia directa: los retornos
son impredecibles → no hay estructura frecuencial explotable → **la PSD debe ser
aproximadamente plana** (ruido blanco).

Un espectro plano → entropía espectral máxima → SE_norm ≈ 0.90–0.99 en datos reales.
El umbral de "Ruidoso" es SE_norm ≥ 0.65. Todos los casos reales caen bien por encima.

### Por qué los filtros NO cambian el régimen

Aquí está la confusión más común:

> "¿No usamos filtros para limpiar la señal? ¿No debería el resultado filtrado ser Tendencial?"

**No, por dos razones:**

**1. El régimen se calcula sobre la señal ORIGINAL, no sobre la filtrada.**
El régimen describe la naturaleza de la señal cruda de retornos. Aplicar un filtro
para extraer el ciclo dominante y luego clasificar esa señal filtrada es circular:
le preguntarías a una señal de banda estrecha (casi pura por definición) si es
"Tendencial", y por supuesto que lo sería. Pero eso no describe el activo, sino
el resultado del filtro.

**2. Los filtros en SPECTRA son para VISUALIZACIÓN, no para clasificación.**
El filtro FIR y el filtro IFFT se usan para **reconstruir y mostrar** la componente
del ciclo dominante superpuesta sobre los retornos (Panel 1). Su propósito es
responder "¿cómo se vería la señal si solo existiera ese ciclo?". No modifican
el análisis espectral ni la clasificación de régimen.

### La confianza (energy_ratio) lo confirma

La confianza del ciclo dominante (fracción de energía que concentra) en datos
financieros diarios suele ser **1–5%**. Eso significa que el ciclo "ganador"
tiene una mínima ventaja sobre el resto. No hay una frecuencia que domine;
el espectro es casi completamente plano.

### ¿Qué señal sí daría "Tendencial"?
- El **precio** (no el retorno): los precios tienen tendencia secular y sus PSD
  caen como `1/f²` (proceso integrado), concentrando energía en frecuencias bajas.
  Pero el precio no es estacionario y analizar su espectro no tiene interpretación
  limpia en teoría de señales.
- Un **activo sintético** con una sinusoide pura: trivialmente Tendencial.
- Una señal con **estacionalidad muy fuerte**: por ejemplo, ventas de chocolates
  con pico todos los diciembres. Los mercados financieros líquidos no tienen ese patrón.

### ¿Dónde está entonces la información útil?

Que todos sean "Ruidoso" es el titular correcto, pero la historia interesante está
en las diferencias **entre los casos** en las otras métricas:

| Métrica | Qué diferencia a los casos |
|---|---|
| **Volatilidad** | AAL/durante tiene 5× más volatilidad que SPY/antes. La crisis sí deja huella. |
| **Coherencia** | AAL se desacopla del mercado durante la pandemia (0.12). NFLX se re-acopla después (0.82). |
| **Confianza del ciclo** | Varía aunque sea pequeña: AAL muestra ciclos de muy corto plazo durante la crisis. |
| **Espectrograma** | Episodios de alta energía concentrada (flash crashes, anuncios) aparecen como manchas en el heatmap. |

> El proyecto demuestra correctamente la teoría de Oppenheim: los mercados
> eficientes producen señales de alta entropía espectral. La información no está
> en el régimen (siempre Ruidoso) sino en la **magnitud de la volatilidad** y en
> la **coherencia cruzada entre activos**.

---

## Resumen de módulos del código y su correspondencia con la materia

| Módulo | Concepto | Capítulo Oppenheim |
|---|---|---|
| `preprocessing.py` | Estacionariedad, señales WSS | Cap. 10.1 |
| `windows.py` | Ventanas espectrales, fuga | Cap. 7.2, 10.2 |
| `welch.py` | Estimación espectral, Welch PSD | Cap. 10.3 |
| `entropy.py` | Entropía de Shannon en PSD | Aplicación de teoría de información |
| `autocorr.py` | ACF, Wiener-Khinchin | Cap. 2.9, 10.3 |
| `cross_spectrum.py` | PSD cruzada, coherencia | Cap. 10.5 |
| `stft.py` | STFT, análisis tiempo-frecuencia | Cap. 10.3 |
| `fir.py` | Filtros FIR, windowed-sinc, convolución lineal | Cap. 7.5 |
| `ifft_filter.py` | Filtrado por máscara, simetría hermítica | Cap. 8.6 |
| `cycle_phase.py` | Magnitud y fase de la DFT | Cap. 8 |
| `metrics.py` | Parseval, energía | Cap. 8.7 |
