import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "plotly.js-dist-min";
import { baseLayout, plotConfig } from "../theme";

const RawPlot = createPlotlyComponent(Plotly);

interface PlotProps {
  data: unknown[];
  layout?: Record<string, unknown>;
  height?: number;
}

export default function Plot({ data, layout = {}, height = 260 }: PlotProps) {
  return (
    <RawPlot
      data={data}
      layout={baseLayout({ height, ...layout })}
      config={plotConfig}
      useResizeHandler
      style={{ width: "100%", height }}
    />
  );
}
