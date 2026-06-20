import { useEffect, useMemo, useState } from "react";
import LiveControls from "./LiveControls";
import StockSelectorPanel from "./StockSelectorPanel";
import Panel1Time from "./Panel1Time";
import Panel2Spectral from "./Panel2Spectral";
import Panel3Coherence from "./Panel3Coherence";
import Panel4Summary from "./Panel4Summary";
import LoadingOverlay from "./LoadingOverlay";
import ErrorBanner from "./ErrorBanner";
import { api } from "../api/client";
import { useLiveAnalysis } from "../hooks/useLiveAnalysis";
import type { AssetInfo } from "../types";

/**
 * Vista del modo en vivo: análisis intradía de una acción de EE.UU. en
 * casi-tiempo-real. Reutiliza los mismos paneles que el modo estático; el globo
 * terráqueo se sustituye por ``StockSelectorPanel``. El polling (60 s) y el botón
 * de actualizar viven en ``useLiveAnalysis``.
 */
export default function LiveView() {
  const [assets, setAssets] = useState<AssetInfo[]>([]);
  const [assetsError, setAssetsError] = useState<string | null>(null);
  const [asset, setAsset] = useState("AAPL");
  const [N, setN] = useState(1024);
  const [windowName, setWindowName] = useState("hanning");
  const [epsLow, setEpsLow] = useState(0.45);
  const [epsHigh, setEpsHigh] = useState(0.65);

  useEffect(() => {
    api
      .getLiveAssets()
      .then((a) => {
        setAssets(a);
        // Si AAPL no estuviera en el catálogo, cae a la primera acción no-benchmark.
        if (!a.some((x) => x.ticker === "AAPL")) {
          const first = a.find((x) => x.kind !== "general") ?? a[0];
          if (first) setAsset(first.ticker);
        }
      })
      .catch((e: Error) => setAssetsError(e.message));
  }, []);

  const params = useMemo(
    () => ({ asset, N, window: windowName, eps_low: epsLow, eps_high: epsHigh }),
    [asset, N, windowName, epsLow, epsHigh]
  );
  const { data, loading, refreshing, error, lastUpdated, refresh } = useLiveAnalysis(
    params,
    true
  );

  return (
    <>
      {assetsError && <ErrorBanner message={assetsError} />}
      <LiveControls
        N={N}
        window={windowName}
        epsLow={epsLow}
        epsHigh={epsHigh}
        onN={setN}
        onWindow={setWindowName}
        onEpsLow={setEpsLow}
        onEpsHigh={setEpsHigh}
      />
      <main className="dashboard">
        {error && <ErrorBanner message={error} />}
        {loading && <LoadingOverlay />}
        <div className="grid">
          {data && <Panel1Time data={data} />}
          {data && <Panel2Spectral data={data} epsLow={epsLow} epsHigh={epsHigh} />}
          {data && <Panel3Coherence data={data} />}
          <StockSelectorPanel
            assets={assets}
            selected={asset}
            onSelect={setAsset}
            lastUpdated={lastUpdated}
            refreshing={refreshing}
            onRefresh={refresh}
          />
          {data && <Panel4Summary data={data} />}
        </div>
      </main>
    </>
  );
}
