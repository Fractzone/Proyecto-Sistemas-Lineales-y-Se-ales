import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AnalyzeResponse } from "../types";

export interface AnalysisParams {
  asset: string;
  epoch: string;
  N: number;
  window: string;
  eps_low: number;
  eps_high: number;
}

export function useAnalysis(params: AnalysisParams) {
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .analyze(params)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [params.asset, params.epoch, params.N, params.window, params.eps_low, params.eps_high]);

  return { data, loading, error };
}
