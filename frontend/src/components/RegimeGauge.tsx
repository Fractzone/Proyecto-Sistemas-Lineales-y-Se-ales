import { theme } from "../theme";

interface RegimeGaugeProps {
  seNorm: number;
  regime: string;
  epsLow: number;
  epsHigh: number;
}

const REGIME_COLOR: Record<string, string> = {
  Tendencial: theme.good,
  Reversivo: theme.warn,
  Ruidoso: theme.bad,
};

export default function RegimeGauge({ seNorm, regime, epsLow, epsHigh }: RegimeGaugeProps) {
  const color = REGIME_COLOR[regime] ?? theme.accent;
  const pct = Math.max(0, Math.min(1, seNorm)) * 100;
  return (
    <div className="gauge">
      <div className="gauge-head">
        <span className="gauge-label">Entropía espectral</span>
        <span className="gauge-regime" style={{ color }}>
          {regime}
        </span>
      </div>
      <div className="gauge-bar">
        <div
          className="gauge-zone"
          style={{ left: 0, width: `${epsLow * 100}%`, background: theme.good }}
        />
        <div
          className="gauge-zone"
          style={{
            left: `${epsLow * 100}%`,
            width: `${(epsHigh - epsLow) * 100}%`,
            background: theme.warn,
          }}
        />
        <div
          className="gauge-zone"
          style={{ left: `${epsHigh * 100}%`, width: `${(1 - epsHigh) * 100}%`, background: theme.bad }}
        />
        <div className="gauge-marker" style={{ left: `${pct}%` }} />
      </div>
      <div className="gauge-value">SE_norm = {seNorm.toFixed(3)}</div>
    </div>
  );
}
