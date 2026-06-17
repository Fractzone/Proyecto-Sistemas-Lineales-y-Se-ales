import Plot from "./Plot";
import { theme } from "../theme";
import type { AnalyzeResponse } from "../types";

export default function Panel3Coherence({ data }: { data: AnalyzeResponse }) {
  const r = data.relation;
  const fDom = data.summary.f_dom;
  const bench = data.summary.benchmark;
  const isBenchmark = data.asset === bench;

  return (
    <section className="panel">
      <h2>3 · Relación con el mercado</h2>
      <Plot
        height={190}
        data={[
          {
            x: r.coh_freqs,
            y: r.coherence,
            type: "scatter",
            mode: "lines",
            name: `Coherencia vs ${bench}`,
            line: { color: theme.accent2, width: 1.4 },
            fill: "tozeroy",
            fillcolor: "rgba(167,139,250,0.12)",
          },
          {
            x: [fDom],
            y: [r.coherence_at_dom],
            type: "scatter",
            mode: "markers",
            name: "en ciclo dom.",
            marker: { color: theme.warn, size: 9, symbol: "diamond" },
          },
        ]}
        layout={{
          title: {
            text: isBenchmark
              ? `Coherencia (${bench} es el benchmark → ≡ 1)`
              : `Coherencia espectral vs ${bench}`,
            font: { size: 12 },
          },
          xaxis: { title: "frecuencia (ciclos/día)" },
          yaxis: { title: "coherencia", range: [0, 1.02] },
        }}
      />
      <Plot
        height={190}
        data={[
          {
            x: r.autocorr_lags,
            y: r.autocorr,
            type: "bar",
            name: "Autocorrelación",
            marker: { color: theme.good },
          },
        ]}
        layout={{
          title: { text: "Autocorrelación R_xx[m]", font: { size: 12 } },
          xaxis: { title: "retardo (días)" },
          yaxis: { title: "R_xx" },
        }}
      />
    </section>
  );
}
