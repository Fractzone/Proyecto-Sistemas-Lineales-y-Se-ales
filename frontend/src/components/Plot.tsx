import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "plotly.js-dist-min";
import { baseLayout, plotConfig } from "../theme";

const RawPlot = createPlotlyComponent(Plotly);

interface PlotProps {
  data: unknown[];
  layout?: Record<string, unknown>;
  height?: number;
  onClick?: (e: unknown) => void;
}

export default function Plot({ data, layout = {}, height = 260, onClick }: PlotProps) {
  return (
    <RawPlot
      data={data}
      layout={baseLayout({ height, ...layout })}
      config={plotConfig}
      useResizeHandler
      onClick={onClick}
      style={{ width: "100%", height }}
    />
  );
}
