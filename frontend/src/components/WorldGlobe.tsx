import { useMemo } from "react";
import Plot from "./Plot";
import { theme } from "../theme";
import type { MarketInfo } from "../types";

interface WorldGlobeProps {
  markets: MarketInfo[];
  selected: string;
  onSelect: (code: string) => void;
}

// Globo terráqueo 3D rotable (Plotly scattergeo, proyección ortográfica). Cada
// punto resaltado es un mercado disponible; al hacer clic se selecciona su país.
export default function WorldGlobe({ markets, selected, onSelect }: WorldGlobeProps) {
  const selectedMarket = markets.find((m) => m.code === selected);

  const trace = useMemo(() => {
    const sizes = markets.map((m) => (m.code === selected ? 15 : 9));
    const colors = markets.map((m) => (m.code === selected ? theme.warn : theme.accent));
    return {
      type: "scattergeo",
      mode: "markers+text",
      lat: markets.map((m) => m.lat),
      lon: markets.map((m) => m.lon),
      text: markets.map((m) => m.code),
      textposition: "top center",
      textfont: { size: 9, color: theme.textMuted },
      hovertext: markets.map(
        (m) => `${m.name} · benchmark ${m.benchmark} · ${m.assets.length} activos`
      ),
      hoverinfo: "text",
      marker: {
        size: sizes,
        color: colors,
        opacity: 0.95,
        line: { color: theme.bg, width: 1 },
      },
    };
  }, [markets, selected]);

  function handleClick(e: unknown) {
    const ev = e as { points?: Array<{ pointIndex?: number; pointNumber?: number }> };
    const p = ev.points?.[0];
    const idx = p?.pointIndex ?? p?.pointNumber;
    if (idx != null && markets[idx]) onSelect(markets[idx].code);
  }

  return (
    <section className="panel">
      <h2>5 · Bolsas del mundo</h2>
      <Plot
        height={300}
        onClick={handleClick}
        data={[trace]}
        layout={{
          margin: { l: 0, r: 0, t: 4, b: 4 },
          showlegend: false,
          paper_bgcolor: theme.panel,
          dragmode: "orbit",
          geo: {
            projection: { type: "orthographic", rotation: { lat: 20, lon: 10, roll: 0 } },
            showland: true,
            landcolor: theme.panelAlt,
            showocean: true,
            oceancolor: theme.bg,
            showcountries: true,
            countrycolor: theme.border,
            showcoastlines: true,
            coastlinecolor: theme.border,
            showframe: false,
            bgcolor: "rgba(0,0,0,0)",
            lataxis: { showgrid: true, gridcolor: theme.grid },
            lonaxis: { showgrid: true, gridcolor: theme.grid },
          },
        }}
      />
      <p className="globe-hint">
        {selectedMarket
          ? `Seleccionado: ${selectedMarket.name} — haz clic en otro punto para cambiar de país. Arrastra para rotar el globo.`
          : "Haz clic en un país resaltado para analizar su bolsa."}
      </p>
    </section>
  );
}
