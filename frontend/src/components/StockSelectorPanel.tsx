import type { AssetInfo } from "../types";

interface Props {
  assets: AssetInfo[];
  selected: string;
  onSelect: (ticker: string) => void;
  lastUpdated: Date | null;
  refreshing: boolean;
  onRefresh: () => void;
}

/**
 * Sustituye al globo terráqueo en el modo en vivo: cuadrícula de acciones US
 * para seleccionar la que se analiza, más el estado de actualización.
 */
export default function StockSelectorPanel(p: Props) {
  return (
    <section className="panel stock-selector">
      <h2>Acciones · Bolsa de EE.UU.</h2>
      <p className="stock-hint">
        Selecciona una acción para analizar sus barras de 1 min en vivo. La
        coherencia se mide contra el benchmark del mercado (SPY).
      </p>
      <div className="stock-grid">
        {p.assets.map((a) => (
          <button
            key={a.ticker}
            className={`stock-chip ${p.selected === a.ticker ? "active" : ""}`}
            onClick={() => p.onSelect(a.ticker)}
            title={a.role}
          >
            <span className="stock-ticker">{a.ticker}</span>
            <span className="stock-name">{a.name}</span>
          </button>
        ))}
      </div>
      <div className="live-status">
        <span className="live-status-text">
          {p.lastUpdated
            ? `Última actualización: ${p.lastUpdated.toLocaleTimeString()}`
            : "Esperando datos…"}
          {p.refreshing && " · actualizando…"}
        </span>
        <button className="refresh-btn" onClick={p.onRefresh} disabled={p.refreshing}>
          ↻ Actualizar
        </button>
      </div>
    </section>
  );
}
