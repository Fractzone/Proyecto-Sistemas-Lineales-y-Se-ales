import Plot from "./Plot";
import RegimeGauge from "./RegimeGauge";
import { theme } from "../theme";
import type { AnalyzeResponse } from "../types";

interface Props {
  data: AnalyzeResponse;
  epsLow: number;
  epsHigh: number;
}

export default function Panel2Spectral({ data, epsLow, epsHigh }: Props) {
  const s = data.spectral;
  const fDom = data.summary.f_dom;
  const freqUnit = data.units?.freq ?? "ciclos/día";
  const timeUnit = data.units?.time ?? "días";

  // Para log-log se omiten frecuencias/potencias no positivas.
  const fx: number[] = [];
  const py: number[] = [];
  for (let i = 0; i < s.freqs.length; i++) {
    if (s.freqs[i] > 0 && s.psd[i] > 0) {
      fx.push(s.freqs[i]);
      py.push(s.psd[i]);
    }
  }

  return (
    <section className="panel">
      <h2>2 · Análisis espectral</h2>
      <RegimeGauge seNorm={s.se_norm} regime={s.regime} epsLow={epsLow} epsHigh={epsHigh} />
      <Plot
        height={190}
        data={[
          {
            x: fx,
            y: py,
            type: "scatter",
            mode: "lines",
            name: "PSD (Welch)",
            line: { color: theme.accent, width: 1.4 },
          },
          {
            x: [fDom, fDom],
            y: [Math.min(...py), Math.max(...py)],
            type: "scatter",
            mode: "lines",
            name: "Ciclo dominante",
            line: { color: theme.warn, width: 1, dash: "dash" },
          },
        ]}
        layout={{
          title: { text: "Densidad espectral de potencia (log-log)", font: { size: 12 } },
          xaxis: { type: "log", title: `frecuencia (${freqUnit})` },
          yaxis: { type: "log", title: "PSD" },
        }}
      />
      <Plot
        height={190}
        data={[
          {
            z: s.stft_matrix,
            x: s.stft_times,
            y: s.stft_freqs,
            type: "heatmap",
            colorscale: "Viridis",
            colorbar: { thickness: 8, len: 0.9 },
          },
        ]}
        layout={{
          title: { text: "Espectrograma STFT", font: { size: 12 } },
          xaxis: { title: `tiempo (${timeUnit})` },
          yaxis: { title: "frecuencia" },
        }}
      />
    </section>
  );
}
