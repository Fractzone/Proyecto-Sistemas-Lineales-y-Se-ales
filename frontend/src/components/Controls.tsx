import type { AssetInfo, CompareMode, EpochInfo } from "../types";

interface ControlsProps {
  assets: AssetInfo[];
  epochs: EpochInfo[];
  asset: string;
  epoch: string;
  N: number;
  window: string;
  epsLow: number;
  epsHigh: number;
  compareMode: CompareMode | null;
  onAsset: (v: string) => void;
  onEpoch: (v: string) => void;
  onN: (v: number) => void;
  onWindow: (v: string) => void;
  onEpsLow: (v: number) => void;
  onEpsHigh: (v: number) => void;
  onCompareMode: (v: CompareMode | null) => void;
}

const WINDOWS = ["hanning", "hamming", "blackman"];

export default function Controls(p: ControlsProps) {
  return (
    <div className="controls">
      <div className="control-group">
        <label>Época</label>
        <div className="segmented">
          {p.epochs.map((e) => (
            <button
              key={e.key}
              className={p.epoch === e.key ? "active" : ""}
              onClick={() => p.onEpoch(e.key)}
              title={`${e.start} → ${e.end}`}
            >
              {e.label.split(" ")[0]}
            </button>
          ))}
        </div>
      </div>

      <div className="control-group">
        <label>Activo</label>
        <div className="segmented">
          {p.assets.map((a) => (
            <button
              key={a.ticker}
              className={p.asset === a.ticker ? "active" : ""}
              onClick={() => p.onAsset(a.ticker)}
              title={a.role}
            >
              {a.ticker}
            </button>
          ))}
        </div>
      </div>

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

      <div className="control-group">
        <label>Comparación</label>
        <div className="segmented">
          <button
            className={p.compareMode === null ? "active" : ""}
            onClick={() => p.onCompareMode(null)}
          >
            Individual
          </button>
          <button
            className={p.compareMode === "asset_epochs" ? "active" : ""}
            onClick={() => p.onCompareMode("asset_epochs")}
          >
            1 activo · 3 épocas
          </button>
          <button
            className={p.compareMode === "epoch_assets" ? "active" : ""}
            onClick={() => p.onCompareMode("epoch_assets")}
          >
            3 activos · 1 época
          </button>
        </div>
      </div>
    </div>
  );
}
