import { useEffect, useState, type ReactNode } from "react";
import { ApiError } from "../api";
import { Icon, type IconName } from "./Icon";

export const Spinner = ({ label = "Loading…" }: { label?: string }) => (
  <div role="status" aria-live="polite" className="flex items-center justify-center gap-3 py-12 text-sm text-muted">
    <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" aria-hidden="true" />{label}
  </div>
);

export function EmptyState({ icon = "Search", title, children, action, image }: { icon?: IconName; title: string; children?: ReactNode; action?: ReactNode; image?: string }) {
  return (
    <div className="card flex flex-col items-center gap-3 px-6 py-10 text-center">
      {image ? <img src={image} alt="" width={240} height={150} loading="lazy" className="w-60 max-w-full rounded-xl" /> : <span className="icon-tile h-12 w-12"><Icon name={icon} className="h-6 w-6" /></span>}
      <h2 className="text-lg font-semibold">{title}</h2>
      {children && <p className="max-w-md text-sm text-muted">{children}</p>}
      {action}
    </div>
  );
}

export function ErrorBox({ error }: { error: unknown }) {
  if (!error) return null;
  const msg = error instanceof ApiError ? error.message : "Something went wrong. Please try again.";
  return (
    <div role="alert" className="flex items-start gap-2 rounded-xl border border-red-300 bg-red-50 px-3 py-2.5 text-sm text-red-800">
      <Icon name="CircleAlert" className="mt-0.5 h-4 w-4 shrink-0" /><span>{msg}</span>
    </div>
  );
}

export const Notice = ({ children, tone = "warn" }: { children: ReactNode; tone?: "warn" | "info" }) => (
  <div className={`flex items-start gap-2 rounded-xl border px-3 py-2.5 text-sm ${tone === "warn" ? "border-amber-300 bg-amber-50 text-amber-900" : "border-indigo-200 bg-indigo-50 text-indigo-900"}`}>
    <Icon name={tone === "warn" ? "TriangleAlert" : "Info"} className="mt-0.5 h-4 w-4 shrink-0" /><div>{children}</div>
  </div>
);

export const Disclaimer = () => (
  <p className="text-xs leading-relaxed text-muted">
    This prediction is based on historical price patterns and may differ from actual market prices. Figures are estimates, not guarantees.
  </p>
);

export function Stat({ label, value, hint, icon, tone = "indigo" }: { label: string; value: ReactNode; hint?: ReactNode; icon?: IconName; tone?: "indigo" | "teal" | "amber" | "rose" }) {
  const tones = { indigo: "bg-indigo-50 text-indigo-600", teal: "bg-teal-50 text-teal-700", amber: "bg-amber-50 text-amber-700", rose: "bg-rose-50 text-rose-600" };
  return (
    <div className="card card-hover p-4">
      <div className="flex items-center justify-between gap-2">
        <div className="text-sm text-muted">{label}</div>
        {icon && <span className={`inline-flex h-8 w-8 items-center justify-center rounded-lg ${tones[tone]}`}><Icon name={icon} className="h-4 w-4" /></span>}
      </div>
      <div className="mt-1 text-2xl font-semibold tracking-tight">{value}</div>
      {hint && <div className="mt-1 text-xs text-muted">{hint}</div>}
    </div>
  );
}

export const PageHeader = ({ title, sub, actions }: { title: string; sub?: ReactNode; actions?: ReactNode }) => (
  <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
    <div>
      <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">{title}</h1>
      {sub && <p className="mt-1 max-w-2xl text-sm text-muted">{sub}</p>}
    </div>
    {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
  </div>
);

export const TrendBadge = ({ trend }: { trend: string }) => {
  const dec = trend.includes("decrease"), inc = trend.includes("increase");
  return (
    <span className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium ${dec ? "bg-teal-100 text-teal-900" : inc ? "bg-amber-100 text-amber-900" : "bg-gray-100 text-gray-700"}`}>
      <Icon name={dec ? "TrendingDown" : inc ? "TrendingUp" : "Activity"} className="h-3 w-3" />{trend}
    </span>
  );
};

export const SampleBadge = () => (
  <span className="rounded-md border border-amber-400 bg-amber-100 px-1.5 py-0.5 text-xs font-medium text-amber-900" title="Prices in this history are synthetic demonstration data, not market data">SAMPLE / DEMO DATA</span>
);

export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [tick, setTick] = useState(0);
  useEffect(() => {
    let live = true;
    setLoading(true); setError(null);
    fn().then((d) => live && setData(d)).catch((e) => live && setError(e)).finally(() => live && setLoading(false));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);
  return { data, error, loading, reload: () => setTick((t) => t + 1) };
}
