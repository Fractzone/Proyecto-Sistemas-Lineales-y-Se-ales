import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "plotly.js-dist-min";
import { baseLayout, plotConfig } from "../theme";

const RawPlot = createPlotlyComponent(Plotly);

interface PlotProps {
  data: unknown[];
  layout?: Record<string, unknown>;
  height?: number;
  onClick?: (e: unknown) => void;
  onHover?: (e: unknown) => void;
  onUnhover?: (e: unknown) => void;
  config?: Record<string, unknown>;
}

export default function Plot({
  data,
  layout = {},
  height = 260,
  onClick,
  onHover,
  onUnhover,
  config,
}: PlotProps) {
  return (
    <RawPlot
      data={data}
      layout={baseLayout({ height, ...layout })}
      config={config ? { ...plotConfig, ...config } : plotConfig}
      useResizeHandler
      onClick={onClick}
      onHover={onHover}
      onUnhover={onUnhover}
      style={{ width: "100%", height }}
    />
  );
}
