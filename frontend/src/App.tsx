import { useEffect, useMemo, useState } from "react";
import Controls from "./components/Controls";
import Panel1Time from "./components/Panel1Time";
import Panel2Spectral from "./components/Panel2Spectral";
import Panel3Coherence from "./components/Panel3Coherence";
import Panel4Summary from "./components/Panel4Summary";
import ComparisonView from "./components/ComparisonView";
import WorldGlobe from "./components/WorldGlobe";
import LoadingOverlay from "./components/LoadingOverlay";
import ErrorBanner from "./components/ErrorBanner";
import ModeToggle from "./components/ModeToggle";
import LiveView from "./components/LiveView";
import { api } from "./api/client";
import { useAnalysis } from "./hooks/useAnalysis";
import type { AnalysisMode, CompareMode, EpochInfo, MarketInfo } from "./types";

export default function App() {
  const [mode, setMode] = useState<AnalysisMode>("static");
  const [markets, setMarkets] = useState<MarketInfo[]>([]);
  const [epochs, setEpochs] = useState<EpochInfo[]>([]);
  const [metaError, setMetaError] = useState<string | null>(null);

  const [market, setMarket] = useState("US");
  const [asset, setAsset] = useState("AAL");
  const [epoch, setEpoch] = useState("durante");
  const [N, setN] = useState(1024);
  const [windowName, setWindowName] = useState("hanning");
  const [epsLow, setEpsLow] = useState(0.45);
  const [epsHigh, setEpsHigh] = useState(0.65);
  const [compareMode, setCompareMode] = useState<CompareMode | null>(null);

  useEffect(() => {
    Promise.all([api.getMarkets(), api.getEpochs()])
      .then(([m, e]) => {
        setMarkets(m);
        setEpochs(e);
      })
      .catch((err: Error) => setMetaError(err.message));
  }, []);

  const currentMarket = markets.find((m) => m.code === market);
  const assets = currentMarket?.assets ?? [];

  // Al cambiar de país (clic en el globo): cargar sus activos y seleccionar la
  // primera acción de contraste (narrativa más interesante, como AAL en EE.UU.).
  function selectMarket(code: string) {
    const m = markets.find((mk) => mk.code === code);
    if (!m) return;
    setMarket(code);
    const contrast = m.assets.find((a) => a.kind === "contrast") ?? m.assets[0];
    if (contrast) setAsset(contrast.ticker);
  }

  const params = useMemo(
    () => ({ asset, epoch, N, window: windowName, eps_low: epsLow, eps_high: epsHigh }),
    [asset, epoch, N, windowName, epsLow, epsHigh]
  );
  const { data, loading, error } = useAnalysis(params);

  const activeEpoch = epochs.find((e) => e.key === epoch);
  const activeAsset = assets.find((a) => a.ticker === asset);

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">◣◢</span>
          <div>
            <h1>SPECTRA</h1>
            <p>Análisis espectral de activos · Sistemas Lineales y Señales</p>
          </div>
        </div>
        <ModeToggle mode={mode} onMode={setMode} />
        {mode === "static" ? (
          activeAsset && (
            <div className="context-chip">
              {currentMarket && <strong>{currentMarket.name}</strong>}{" "}
              <strong>{activeAsset.ticker}</strong> · {activeAsset.role}
            </div>
          )
        ) : (
          <div className="context-chip">
            <strong>Bolsa de EE.UU.</strong> · datos intradía (1 min, casi-tiempo-real)
          </div>
        )}
      </header>

      {metaError && <ErrorBanner message={metaError} />}

      {mode === "live" ? (
        <LiveView />
      ) : (
        <>
          <Controls
            assets={assets}
            epochs={epochs}
            asset={asset}
            epoch={epoch}
            N={N}
            window={windowName}
            epsLow={epsLow}
            epsHigh={epsHigh}
            compareMode={compareMode}
            onAsset={setAsset}
            onEpoch={setEpoch}
            onN={setN}
            onWindow={setWindowName}
            onEpsLow={setEpsLow}
            onEpsHigh={setEpsHigh}
            onCompareMode={setCompareMode}
          />

          {compareMode ? (
            <ComparisonView
              mode={compareMode}
              asset={asset}
              epoch={epoch}
              market={market}
              N={N}
              window={windowName}
              epsLow={epsLow}
              epsHigh={epsHigh}
            />
          ) : (
            <main className="dashboard">
              {error && <ErrorBanner message={error} />}
              {loading && <LoadingOverlay />}
              {data && !error && (
                <div className="grid">
                  <Panel1Time data={data} />
                  <Panel2Spectral data={data} epsLow={epsLow} epsHigh={epsHigh} />
                  <Panel3Coherence data={data} />
                  <WorldGlobe markets={markets} selected={market} onSelect={selectMarket} />
                  <Panel4Summary data={data} />
                </div>
              )}
            </main>
          )}
        </>
      )}

      <footer className="app-footer">
        {mode === "static" && activeEpoch && (
          <span>
            Época «{activeEpoch.label}»: {activeEpoch.start} → {activeEpoch.end}
          </span>
        )}
        {mode === "live" && (
          <span>Modo en vivo · bolsa de EE.UU. · barras de 1 min vía yfinance (retardo ~15 min)</span>
        )}
        <span>
          Estudio académico {mode === "static" ? "retrospectivo" : "descriptivo"} — sin
          recomendación de inversión ni predicción.
        </span>
      </footer>
    </div>
  );
}
