import type { AnalyzeResponse } from "../types";

function Metric({ label, value, unit }: { label: string; value: string; unit?: string }) {
  return (
    <div className="metric">
      <span className="metric-label">{label}</span>
      <span className="metric-value">
        {value}
        {unit && <span className="metric-unit"> {unit}</span>}
      </span>
    </div>
  );
}

export default function Panel4Summary({ data }: { data: AnalyzeResponse }) {
  const s = data.summary;
  return (
    <section className="panel panel-summary">
      <h2>4 · Resumen e interpretación</h2>
      <div className="metrics-grid">
        <Metric label="Régimen" value={s.regime} />
        <Metric label="Ciclo dominante" value={s.period_days.toFixed(1)} unit="días" />
        <Metric label="Fase" value={s.phase_pct.toFixed(0)} unit="%" />
        <Metric label="Confianza (E_dom/E_tot)" value={(s.confidence * 100).toFixed(1)} unit="%" />
        <Metric label="Volatilidad" value={s.volatility.toFixed(4)} />
        <Metric label="Coherencia en f_dom" value={s.coherence_at_dom.toFixed(2)} />
        <Metric label="Muestras" value={String(s.n_samples)} />
        <Metric label="nperseg" value={String(s.nperseg)} />
      </div>
      <p className="interpretation">{s.interpretation}</p>
    </section>
  );
}
