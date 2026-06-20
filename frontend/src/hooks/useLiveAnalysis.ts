import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { AnalyzeResponse } from "../types";

export interface LiveAnalysisParams {
  asset: string;
  N: number;
  window: string;
  eps_low: number;
  eps_high: number;
}

// Intervalo de auto-refresco (polling). El backend cachea ~55 s para no saturar
// yfinance, así que 60 s entrega datos frescos sin re-descargar de más.
const POLL_MS = 60_000;

/**
 * Análisis en vivo con polling. Espejo de ``useAnalysis`` pero:
 *  - vuelve a pedir cada 60 s mientras ``enabled``;
 *  - expone ``refresh()`` para el botón manual;
 *  - mantiene los datos previos visibles durante el refresco (sin parpadeo):
 *    ``loading`` solo en la primera carga / cambio de activo, ``refreshing`` en
 *    los refrescos silenciosos.
 */
export function useLiveAnalysis(params: LiveAnalysisParams, enabled: boolean) {
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Los últimos params, para que el intervalo no quede capturado con valores viejos.
  const paramsRef = useRef(params);
  paramsRef.current = params;

  const fetchOnce = useCallback((isInitial: boolean) => {
    if (isInitial) setLoading(true);
    else setRefreshing(true);
    setError(null);
    return api
      .analyzeLive(paramsRef.current)
      .then((res) => {
        setData(res);
        setLastUpdated(new Date());
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => {
        setLoading(false);
        setRefreshing(false);
      });
  }, []);

  // Carga inicial / al cambiar de activo o parámetros clave (muestra overlay).
  useEffect(() => {
    if (!enabled) return;
    setData(null);
    void fetchOnce(true);
  }, [enabled, params.asset, params.N, params.window, params.eps_low, params.eps_high, fetchOnce]);

  // Polling silencioso cada 60 s mientras el modo en vivo esté activo.
  useEffect(() => {
    if (!enabled) return;
    const id = window.setInterval(() => void fetchOnce(false), POLL_MS);
    return () => window.clearInterval(id);
  }, [enabled, fetchOnce]);

  const refresh = useCallback(() => void fetchOnce(false), [fetchOnce]);

  return { data, loading, refreshing, error, lastUpdated, refresh };
}
