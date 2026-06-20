interface LiveControlsProps {
  N: number;
  window: string;
  epsLow: number;
  epsHigh: number;
  onN: (v: number) => void;
  onWindow: (v: string) => void;
  onEpsLow: (v: number) => void;
  onEpsHigh: (v: number) => void;
}

const WINDOWS = ["hanning", "hamming", "blackman"];

/**
 * Controles del modo en vivo: subconjunto de ``Controls`` (sin época ni modo
 * comparación, que no aplican). La acción se elige en ``StockSelectorPanel``.
 */
export default function LiveControls(p: LiveControlsProps) {
  return (
    <div className="controls">
      <div className="control-group">
        <label>Resolución N = {p.N}</label>
        <input
          type="range"
          min={256}
          max={4096}
          step={256}
          value={p.N}
          onChange={(e) => p.onN(Number(e.target.value))}
        />
      </div>

      <div className="control-group">
        <label>Ventana</label>
        <select value={p.window} onChange={(e) => p.onWindow(e.target.value)}>
          {WINDOWS.map((w) => (
            <option key={w} value={w}>
              {w}
            </option>
          ))}
        </select>
      </div>

      <div className="control-group">
        <label>
          ε_low = {p.epsLow.toFixed(2)} · ε_high = {p.epsHigh.toFixed(2)}
        </label>
        <div className="dual-slider">
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={p.epsLow}
            onChange={(e) => p.onEpsLow(Math.min(Number(e.target.value), p.epsHigh - 0.01))}
          />
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={p.epsHigh}
            onChange={(e) => p.onEpsHigh(Math.max(Number(e.target.value), p.epsLow + 0.01))}
          />
        </div>
      </div>
    </div>
  );
}
