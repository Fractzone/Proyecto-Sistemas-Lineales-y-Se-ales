// Tipos que reflejan los esquemas Pydantic del backend.

export interface AssetInfo {
  ticker: string;
  name: string;
  role: string;
  kind: string; // "general" | "contrast"
  market: string;
}

export interface MarketInfo {
  code: string;
  name: string;
  lat: number;
  lon: number;
  benchmark: string;
  assets: AssetInfo[];
}

export interface EpochInfo {
  key: string;
  label: string;
  start: string;
  end: string;
}

export interface TimeSeries {
  dates: string[];
  price: number[];
  returns: number[];
  returns_dates: string[];
  dominant_component_ifft: number[];
  dominant_component_fir: number[];
}

export interface Spectral {
  freqs: number[];
  psd: number[];
  se: number;
  se_norm: number;
  regime: string;
  stft_times: number[];
  stft_freqs: number[];
  stft_matrix: number[][];
}

export interface Relation {
  coh_freqs: number[];
  coherence: number[];
  coherence_at_dom: number;
  autocorr_lags: number[];
  autocorr: number[];
}

export interface Summary {
  regime: string;
  period_days: number;
  f_dom: number;
  phase_pct: number;
  phase_rad: number;
  confidence: number;
  volatility: number;
  coherence_at_dom: number;
  n_samples: number;
  nperseg: number;
  benchmark: string;
  interpretation: string;
}

export interface AnalyzeResponse {
  asset: string;
  epoch: string;
  window: string;
  time: TimeSeries;
  spectral: Spectral;
  relation: Relation;
  summary: Summary;
}

export interface AnalyzeRequest {
  asset: string;
  epoch: string;
  N: number;
  window: string;
  eps_low: number;
  eps_high: number;
}

export interface CompareRow {
  asset: string;
  epoch: string;
  regime: string;
  period_days: number;
  confidence: number;
  volatility: number;
  coherence_at_dom: number;
  se_norm: number;
}

export interface CompareResponse {
  mode: string;
  rows: CompareRow[];
}

export type CompareMode = "asset_epochs" | "epoch_assets";
