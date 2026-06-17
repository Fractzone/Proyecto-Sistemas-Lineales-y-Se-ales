import { useEffect, useMemo, useRef } from "react";
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
    const sizes = markets.map((m) => (m.code === selected ? 16 : 11));
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

  // El globo rotable hace que Plotly trate el clic como un arrastre y suprima
  // `plotly_click`, además de cortar la propagación del `mouseup` (por eso los
  // manejadores de React no se enteran). Solución:
  //   1. Rastreamos el país bajo el cursor con el evento `hover` de Plotly.
  //   2. Escuchamos `mousedown`/`mouseup` NATIVOS en FASE DE CAPTURA sobre el
  //      contenedor (la captura se dispara aunque Plotly corte la propagación).
  //   3. Si el ratón apenas se movió entre ambos = clic (no arrastre) → se
  //      selecciona el país que estaba bajo el cursor al pulsar.
  const containerRef = useRef<HTMLDivElement>(null);
  const hoveredCode = useRef<string | null>(null);
  const downPos = useRef<{ x: number; y: number } | null>(null);
  const downHovered = useRef<string | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  function codeFromEvent(e: unknown): string | null {
    const ev = e as { points?: Array<{ pointIndex?: number; pointNumber?: number }> };
    const p = ev.points?.[0];
    const idx = p?.pointIndex ?? p?.pointNumber;
    return idx != null && markets[idx] ? markets[idx].code : null;
  }

  function handleHover(e: unknown) {
    hoveredCode.current = codeFromEvent(e);
  }
  function handleUnhover() {
    hoveredCode.current = null;
  }
  function handleClick(e: unknown) {
    // Camino directo por si Plotly llega a emitir el clic (no siempre lo hace).
    const code = codeFromEvent(e);
    if (code) onSelectRef.current(code);
  }

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onDown = (e: MouseEvent) => {
      downPos.current = { x: e.clientX, y: e.clientY };
      downHovered.current = hoveredCode.current; // país bajo el cursor al pulsar
    };
    const onUp = (e: MouseEvent) => {
      const d = downPos.current;
      downPos.current = null;
      if (!d) return;
      const moved = Math.hypot(e.clientX - d.x, e.clientY - d.y);
      const code = downHovered.current ?? hoveredCode.current;
      if (moved < 8 && code) onSelectRef.current(code);
    };
    el.addEventListener("mousedown", onDown, true);
    el.addEventListener("mouseup", onUp, true);
    return () => {
      el.removeEventListener("mousedown", onDown, true);
      el.removeEventListener("mouseup", onUp, true);
    };
  }, []);

  return (
    <section className="panel">
      <h2>5 · Bolsas del mundo</h2>
      <div ref={containerRef}>
        <Plot
          height={340}
          onClick={handleClick}
          onHover={handleHover}
          onUnhover={handleUnhover}
          config={{
            scrollZoom: true, // rueda del ratón = zoom sobre el globo
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ["toImage", "select2d", "lasso2d"],
          }}
          data={[trace]}
          layout={{
            margin: { l: 0, r: 0, t: 4, b: 4 },
            showlegend: false,
            paper_bgcolor: theme.panel,
            geo: {
              // Proyección ortográfica (globo): arrastrar rota, la rueda hace zoom.
              projection: { type: "orthographic", rotation: { lat: 20, lon: 60, roll: 0 } },
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
      </div>
      <p className="globe-hint">
        {selectedMarket ? `Seleccionado: ${selectedMarket.name}. ` : ""}
        Arrastra para rotar · rueda del ratón o botones +/− para zoom · clic en un
        punto resaltado para analizar esa bolsa.
      </p>
    </section>
  );
}
