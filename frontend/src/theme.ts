// Paleta "terminal financiera científica" (tema oscuro).
export const theme = {
  bg: "#0a0e14",
  panel: "#111722",
  panelAlt: "#0d1320",
  border: "#1f2a3a",
  text: "#c9d6e5",
  textMuted: "#6b7a90",
  grid: "#1a2433",
  accent: "#38bdf8", // cian
  accent2: "#a78bfa", // violeta
  warn: "#fbbf24", // ámbar
  good: "#34d399", // verde
  bad: "#f87171", // rojo
  series: ["#38bdf8", "#fbbf24", "#34d399", "#a78bfa", "#f87171"],
};

// Configuración base de layout para todas las gráficas Plotly.
export function baseLayout(overrides: Record<string, unknown> = {}) {
  return {
    paper_bgcolor: theme.panelAlt,
    plot_bgcolor: theme.panelAlt,
    font: { color: theme.text, family: "ui-monospace, 'Cascadia Code', monospace", size: 11 },
    margin: { l: 56, r: 18, t: 34, b: 42 },
    xaxis: { gridcolor: theme.grid, zerolinecolor: theme.grid, linecolor: theme.border },
    yaxis: { gridcolor: theme.grid, zerolinecolor: theme.grid, linecolor: theme.border },
    legend: { orientation: "h", y: 1.12, font: { size: 10 } },
    hoverlabel: { bgcolor: theme.panel, bordercolor: theme.border },
    ...overrides,
  };
}

export const plotConfig = { displayModeBar: false, responsive: true } as Record<string, unknown>;
