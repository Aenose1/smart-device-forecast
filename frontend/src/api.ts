export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public details?: any) {
    super(message);
  }
}

export interface Device {
  id: string; name: string; brand: string; category: "Laptop" | "Smartphone"; release_date: string | null;
  launch_price: number; current_price: number | null; latest_price: number; latest_price_date: string | null;
  currency: string; status: string; specs: Record<string, string>;
}
export interface Paged<T> { items: T[]; total: number; page: number; page_size: number }
export interface Stats {
  records: number; first_date: string; last_date: string; current_price: number; min_price: number; min_date: string;
  max_price: number; max_date: string; avg_price: number; abs_change: number; pct_change: number | null;
  highest_drop: Move | null; highest_increase: Move | null;
}
export interface Move { amount: number; pct: number; from_date: string; to_date: string }
export interface HistoryResponse {
  device_id: string; currency: string; has_sample_data: boolean; stats: Stats | null;
  history: { date: string; price: number; source: string; is_sample: boolean }[];
}
export interface ForecastRow {
  horizon_months: number; label: string; forecast_date: string; predicted_price: number; lower: number; upper: number;
  abs_change: number; pct_change: number; trend: string;
}
export interface Candidate { name: string; status: string; mae?: number; rmse?: number; mape?: number | null; r2?: number | null; selected: boolean }
export interface Prediction {
  id: number; kind: string; device_id: string | null; device_name: string; brand: string; category: string; currency: string;
  current_price: number; as_of: string; horizons: number[]; results: ForecastRow[]; overall_trend: string | null;
  overall_pct_change: number | null; model_type: string; is_sample: boolean; created_at: string; disclaimer: string;
  path?: { date: string; predicted: number; lower: number; upper: number }[];
  history?: [string, number][]; stats?: Stats; warnings?: string[];
  model_info?: {
    model_type: string; trained_at: string; dataset_version: string; n_observations: number; category: string;
    metrics: { mae: number; rmse: number; mape: number | null; r2: number | null; n_test: number; validation: string };
    candidates: Candidate[]; feature_set: { model_features: string[]; category_spec_features: string[] };
    interval: { level: number; method: string };
  };
}
export interface Dashboard {
  total_devices: number; laptops: number; smartphones: number; history_records: number; my_predictions: number;
  average_price_change: number | null; top_decreases: Mover[]; top_increases: Mover[];
  records_by_month: { month: string; records: number }[]; recent_predictions: Prediction[];
}
export interface Mover { id: string; name: string; brand: string; category: string; currency: string; first_price: number; latest_price: number; pct_change: number }
export interface DatasetRow {
  id: number; filename: string; is_sample: boolean; status: string; rows_total: number; rows_valid: number; rows_invalid: number;
  rows_duplicate: number; created_at: string;
}
export interface ValidationReport {
  total_rows: number; valid_rows: number; invalid_rows: number; duplicates_in_file: number; duplicates_existing: number;
  missing_values: number; invalid_device_ids: string[]; error_count: number; errors_truncated: boolean;
  errors: { row: number; column: string | null; code: string; message: string }[];
}
export interface ModelRow {
  id: number; device_id: string; device_name: string; category: string; model_type: string; trained_at: string;
  dataset_version: string; n_observations: number; is_active: boolean; metrics: Record<string, any>; candidates: Candidate[];
}
export interface LogRow { id: number; created_at: string; event: string; status: string; message: string; device_id: string | null; user: string | null; duration_ms: number }

/** Human-readable reason for a failed request. A dev-proxy failure (backend not running) comes back as an HTML/empty
 *  500/502/503/504 without JSON, which used to show only "Request failed." */
function explain(status: number, data: any): string {
  const fieldMsg = data?.details?.errors?.map((e: any) => `${e.field}: ${e.message}`).join("; ");
  if (fieldMsg) return fieldMsg;
  if (typeof data?.detail === "string") return data.detail;
  if ([500, 502, 503, 504].includes(status))
    return "The server did not answer correctly. Make sure the backend is running (uvicorn on port 8000) and try again.";
  return `Request failed (HTTP ${status}).`;
}

/** Where the API lives.
 *  - Local development: leave VITE_API_URL unset. Requests go to /api on the Vite dev server, which proxies them to the
 *    FastAPI backend on port 8000 (see vite.config.ts).
 *  - Production (Vercel): set VITE_API_URL=https://smart-device-forcast-1.onrender.com (no trailing slash, no "/api").
 *    The code below already prefixes every path with "/api/...". If it is NOT set, requests go to /api on the Vercel
 *    domain, which frontend/vercel.json forwards to the Render backend as a fallback. */
export const API_BASE: string = ((import.meta as any).env?.VITE_API_URL ?? "").trim().replace(/\/+$/, "");
export const apiUrl = (path: string) => `${API_BASE}${path}`;

/** Anonymous, random id for THIS browser. It is not a login or a credential; it only keeps each browser's forecast
 *  history separate. Stored in localStorage (falls back to memory if storage is blocked). */
let memoryVisitorId = "";
function visitorId(): string {
  try {
    let v = localStorage.getItem("sdf_visitor_id");
    if (!v) { v = (crypto.randomUUID?.() ?? `${Date.now()}${Math.random().toString(36).slice(2)}`).replace(/[^A-Za-z0-9_-]/g, ""); localStorage.setItem("sdf_visitor_id", v); }
    return v;
  } catch {
    return (memoryVisitorId ||= (crypto.randomUUID?.() ?? `${Date.now()}${Math.random().toString(36).slice(2)}`).replace(/[^A-Za-z0-9_-]/g, ""));
  }
}

/** Administrator key (only for the Administration pages). Kept in sessionStorage: cleared when the tab is closed. */
export const adminKey = {
  get: () => { try { return sessionStorage.getItem("sdf_admin_key") ?? ""; } catch { return ""; } },
  set: (k: string) => { try { sessionStorage.setItem("sdf_admin_key", k); } catch { /* ignore */ } },
  clear: () => { try { sessionStorage.removeItem("sdf_admin_key"); } catch { /* ignore */ } },
};

function authHeaders(json: boolean): Record<string, string> {
  const h: Record<string, string> = { "X-Visitor-Id": visitorId() };
  if (json) h["Content-Type"] = "application/json";
  const k = adminKey.get();
  if (k) h["X-Admin-Key"] = k;
  return h;
}

async function request<T>(method: string, url: string, body?: unknown, form?: FormData): Promise<T> {
  let res: Response;
  try {
    res = await fetch(apiUrl(url), {
      method, credentials: "omit",   // no cookies are used anywhere
      headers: authHeaders(body !== undefined),
      body: form ?? (body !== undefined ? JSON.stringify(body) : undefined),
    });
  } catch {
    throw new ApiError(0, "network", "Cannot reach the server. Check your connection and that the backend is running, then try again.");
  }
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => null);
  if (data === null && url.startsWith("/api/")) {
    // The API always answers JSON. A web page or empty body means the request never reached the backend
    // (VITE_API_URL missing or wrong, or the static host answered instead).
    throw new ApiError(res.status, "api_unreachable", `The website could not reach the API (HTTP ${res.status}, not a JSON answer). ` +
      "Check the VITE_API_URL setting (production) or that the backend is running (local).");
  }
  if (!res.ok) throw new ApiError(res.status, data?.code ?? "error", explain(res.status, data), data?.details);
  return data as T;
}

/** Downloads a file through fetch so the visitor / admin headers are sent (a plain <a href> cannot send them). */
export async function downloadFile(path: string, fallbackName = "download"): Promise<void> {
  let res: Response;
  try { res = await fetch(apiUrl(path), { credentials: "omit", headers: authHeaders(false) }); }
  catch { throw new ApiError(0, "network", "Cannot reach the server. Check your connection and try again."); }
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new ApiError(res.status, data?.code ?? "error", explain(res.status, data), data?.details);
  }
  const m = /filename="?([^";]+)"?/i.exec(res.headers.get("content-disposition") ?? "");
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url; a.download = m?.[1] ?? fallbackName; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}

const qs = (p: Record<string, string | number | undefined | null>) => {
  const u = new URLSearchParams();
  Object.entries(p).forEach(([k, v]) => v !== undefined && v !== null && v !== "" && u.set(k, String(v)));
  const s = u.toString();
  return s ? `?${s}` : "";
};

export interface PublicOverview {
  brands: Record<string, { brand: string; devices: number }[]>; featured: Device[]; total_devices: number;
}

export const api = {
  health: () => request<{ status: string }>("GET", "/api/health"),
  publicOverview: () => request<PublicOverview>("GET", "/api/public/overview"),
  dashboard: () => request<Dashboard>("GET", "/api/dashboard"),
  devices: (p: Record<string, any>) => request<Paged<Device>>("GET", `/api/devices/search${qs(p)}`),
  brands: (category?: string) => request<string[]>("GET", `/api/devices/brands${qs({ category })}`),
  device: (id: string) => request<Device>("GET", `/api/devices/${encodeURIComponent(id)}`),
  history: (id: string) => request<HistoryResponse>("GET", `/api/devices/${encodeURIComponent(id)}/history`),
  forecast: (device_id: string, years: number) => request<Prediction>("POST", "/api/forecast", { device_id, years }),
  predict: (device_id: string, months: number) => request<Prediction>("POST", "/api/predict", { device_id, months }),
  predictions: (p: Record<string, any>) => request<Paged<Prediction>>("GET", `/api/predictions${qs(p)}`),
  prediction: (id: number | string) => request<Prediction>("GET", `/api/predictions/${id}`),
  admin: {
    status: () => request<{ mode: "key" | "open" | "disabled"; authorized: boolean }>("GET", "/api/admin/status"),
    overview: () => request<Record<string, number>>("GET", "/api/admin/overview"),
    saveDevice: (b: any, editId?: string) =>
      editId ? request<Device>("PUT", `/api/admin/devices/${encodeURIComponent(editId)}`, b) : request<Device>("POST", "/api/admin/devices", b),
    deleteDevice: (id: string) => request<void>("DELETE", `/api/admin/devices/${encodeURIComponent(id)}`),
    datasets: () => request<DatasetRow[]>("GET", "/api/admin/datasets"),
    upload: (file: File, isSample: boolean) => {
      const f = new FormData(); f.append("file", file); f.append("is_sample", String(isSample));
      return request<{ dataset: DatasetRow; report: ValidationReport }>("POST", "/api/admin/dataset/upload", undefined, f);
    },
    validate: (file: File) => { const f = new FormData(); f.append("file", file); return request<ValidationReport>("POST", "/api/admin/dataset/validate", undefined, f); },
    models: () => request<{ total: number; items: ModelRow[] }>("GET", "/api/admin/models"),
    train: (b: { device_id?: string; category?: string }) =>
      request<{ trained: { device_id: string; device_name: string; model_type: string }[]; failed: { device_id: string; device_name: string; reason: string }[] }>("POST", "/api/admin/models/train", b),
    logs: (status?: string) => request<{ total: number; items: LogRow[] }>("GET", `/api/admin/prediction-logs${qs({ status })}`),
  },
};

export function money(v: number | null | undefined, currency = "INR"): string {
  if (v === null || v === undefined) return "—";
  try {
    return new Intl.NumberFormat(currency === "INR" ? "en-IN" : "en-US", { style: "currency", currency, maximumFractionDigits: 0 }).format(v);
  } catch { return `${currency} ${Math.round(v).toLocaleString()}`; }
}
export const pct = (v: number | null | undefined) => (v === null || v === undefined ? "—" : `${v > 0 ? "+" : ""}${v.toFixed(1)}%`);
export const fmtNum = (v: number | null | undefined, d = 2) => (v === null || v === undefined ? "n/a" : v.toLocaleString(undefined, { maximumFractionDigits: d }));
export const fmtDate = (s: string) => new Date(s).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
export const modelLabel = (n: string) => n.replace(/_/g, " ");
