import Plot from "./Plot";
import { theme } from "../theme";
import type { AnalyzeResponse } from "../types";

export default function Panel1Time({ data }: { data: AnalyzeResponse }) {
  const t = data.time;
  return (
    <section className="panel">
      <h2>1 · Dominio del tiempo</h2>
      <Plot
        height={180}
        data={[
          {
            x: t.dates,
            y: t.price,
            type: "scatter",
            mode: "lines",
            name: "Precio ajustado",
            line: { color: theme.accent, width: 1.5 },
          },
        ]}
        layout={{
          title: { text: "Precio histórico", font: { size: 12 } },
          yaxis: { title: "USD" },
        }}
      />
      <Plot
        height={200}
        data={[
          {
            x: t.returns_dates,
            y: t.returns,
            type: "scatter",
            mode: "lines",
            name: "Retornos log",
            line: { color: theme.textMuted, width: 0.8 },
            opacity: 0.6,
          },
          {
            x: t.returns_dates,
            y: t.dominant_component_ifft,
            type: "scatter",
            mode: "lines",
            name: "Ciclo dom. (IFFT)",
            line: { color: theme.warn, width: 1.6 },
          },
          {
            x: t.returns_dates,
            y: t.dominant_component_fir,
            type: "scatter",
            mode: "lines",
            name: "Ciclo dom. (FIR)",
            line: { color: theme.good, width: 1.2, dash: "dot" },
          },
        ]}
        layout={{
          title: { text: "Retornos + componente del ciclo dominante", font: { size: 12 } },
        }}
      />
    </section>
  );
}
