"""SPECTRA — motor de procesamiento digital de señales (DSP) propio.

Núcleo académico del proyecto. Todas las operaciones espectrales se implementan
**a mano** sobre arrays de NumPy. La única primitiva externa de DSP permitida es
``numpy.fft.fft`` / ``numpy.fft.ifft`` (FFT de Cooley-Tukey), que se asume y se
documenta pero no se reimplementa.

``scipy.signal`` NO se usa aquí en ningún caso; solo aparece en los tests como
oráculo de validación.

Cada módulo cita el capítulo correspondiente de Oppenheim & Schafer,
*Discrete-Time Signal Processing*.
"""

__version__ = "1.0.0"
