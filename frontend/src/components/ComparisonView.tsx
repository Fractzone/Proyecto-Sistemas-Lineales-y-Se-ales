import { useEffect, useState } from "react";
import Plot from "./Plot";
import { theme } from "../theme";
import { api } from "../api/client";
import type { CompareMode, CompareResponse } from "../types";

interface Props {
  mode: CompareMode;
  asset: string;
  epoch: string;
  market: string;
  N: number;
  window: string;
  epsLow: number;
  epsHigh: number;
}

export default function ComparisonView(p: Props) {
  const [data, setData] = useState<CompareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    api
      .compare({
        mode: p.mode,
        asset: p.mode === "asset_epochs" ? p.asset : undefined,
        epoch: p.mode === "epoch_assets" ? p.epoch : undefined,
        market: p.mode === "epoch_assets" ? p.market : undefined,
        N: p.N,
        window: p.window,
        eps_low: p.epsLow,
        eps_high: p.epsHigh,
      })
      .then((res) => !cancelled && setData(res))
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [p.mode, p.asset, p.epoch, p.market, p.N, p.window, p.epsLow, p.epsHigh]);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="loading-inline">Calculando comparación…</div>;

  const labels = data.rows.map((r) =>
    p.mode === "asset_epochs" ? r.epoch : r.asset
  );

  return (
    <div className="comparison">
      <div className="comparison-charts">
        <section className="panel">
          <h2>Volatilidad</h2>
          <Plot
            height={220}
            data={[
              {
                x: labels,
                y: data.rows.map((r) => r.volatility),
                type: "bar",
                marker: { color: theme.bad },
              },
            ]}
            layout={{ yaxis: { title: "σ retornos" } }}
          />
        </section>
        <section className="panel">
          <h2>Coherencia con el mercado (f_dom)</h2>
          <Plot
            height={220}
            data={[
              {
                x: labels,
                y: data.rows.map((r) => r.coherence_at_dom),
                type: "bar",
                marker: { color: theme.accent2 },
              },
            ]}
            layout={{ yaxis: { title: "coherencia", range: [0, 1] } }}
          />
        </section>
        <section className="panel">
          <h2>Entropía espectral</h2>
          <Plot
            height={220}
            data={[
              {
                x: labels,
                y: data.rows.map((r) => r.se_norm),
                type: "bar",
                marker: { color: theme.warn },
              },
            ]}
            layout={{ yaxis: { title: "SE_norm", range: [0, 1] } }}
          />
        </section>
      </div>

      <section className="panel">
        <h2>
          Tabla comparativa ·{" "}
          {p.mode === "asset_epochs" ? `${p.asset} en las 3 épocas` : `3 activos en «${p.epoch}»`}
        </h2>
        <table className="compare-table">
          <thead>
            <tr>
              <th>{p.mode === "asset_epochs" ? "Época" : "Activo"}</th>
              <th>Régimen</th>
              <th>Ciclo (días)</th>
              <th>Confianza</th>
              <th>Volatilidad</th>
              <th>Coh. f_dom</th>
              <th>SE_norm</th>
            </tr>
          </thead>
          <tbody>
            {data.rows.map((r, i) => (
              <tr key={i}>
                <td>{labels[i]}</td>
                <td>{r.regime}</td>
                <td>{r.period_days.toFixed(1)}</td>
                <td>{(r.confidence * 100).toFixed(1)}%</td>
                <td>{r.volatility.toFixed(4)}</td>
                <td>{r.coherence_at_dom.toFixed(2)}</td>
                <td>{r.se_norm.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
