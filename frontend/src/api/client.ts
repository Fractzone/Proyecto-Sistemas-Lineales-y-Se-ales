import type {
  AnalyzeRequest,
  AnalyzeResponse,
  AssetInfo,
  CompareResponse,
  EpochInfo,
} from "../types";

export interface CompareRequest {
  mode: string;
  asset?: string;
  epoch?: string;
  N: number;
  window: string;
  eps_low: number;
  eps_high: number;
}

// En desarrollo Vite proxea /api -> backend:8000. En producción se puede fijar
// VITE_API_BASE (p. ej. "http://localhost:8000").
const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getAssets: () => request<AssetInfo[]>("/assets"),
  getEpochs: () => request<EpochInfo[]>("/epochs"),
  analyze: (req: AnalyzeRequest) =>
    request<AnalyzeResponse>("/analyze", { method: "POST", body: JSON.stringify(req) }),
  compare: (req: CompareRequest) =>
    request<CompareResponse>("/compare", { method: "POST", body: JSON.stringify(req) }),
};
