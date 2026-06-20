import type { AnalysisMode } from "../types";

interface Props {
  mode: AnalysisMode;
  onMode: (m: AnalysisMode) => void;
}

export default function ModeToggle({ mode, onMode }: Props) {
  return (
    <div className="mode-toggle segmented">
      <button
        className={mode === "static" ? "active" : ""}
        onClick={() => onMode("static")}
        title="Estudio retrospectivo por épocas de la pandemia (datos diarios)"
      >
        Análisis estático
      </button>
      <button
        className={mode === "live" ? "active" : ""}
        onClick={() => onMode("live")}
        title="Acciones de EE.UU. en casi-tiempo-real (barras de 1 min)"
      >
        Análisis en vivo
      </button>
    </div>
  );
}
