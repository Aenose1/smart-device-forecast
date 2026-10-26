import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, fmtDate, money, pct, type Mover, type Prediction } from "../api";
import { Icon, type IconName } from "../components/Icon";
import PriceChart from "../components/PriceChart";
import ProductImage from "../components/ProductImage";
import { EmptyState, ErrorBox, SampleBadge, Spinner, Stat, TrendBadge, useAsync } from "../components/ui";
import { deviceImage } from "../lib/catalog";

function Thumb({ d }: { d: { name: string; brand: string; category: string } }) {
  const img = deviceImage(d);
  return <ProductImage src={img.src} fallback={img.fallback} alt="" category={d.category} ratio="1 / 1" className="h-10 w-10 shrink-0 rounded-lg bg-slate-100" />;
}

function Movers({ title, rows, tone }: { title: string; rows: Mover[]; tone: "down" | "up" }) {
  const data = rows.map((r) => ({ name: r.name.length > 24 ? r.name.slice(0, 23) + "…" : r.name, pct: r.pct_change }));
  return (
    <div className="card p-5">
      <h2 className="mb-3 flex items-center gap-2 font-semibold">
        <Icon name={tone === "down" ? "TrendingDown" : "TrendingUp"} className={`h-4 w-4 ${tone === "down" ? "text-teal-700" : "text-amber-600"}`} />{title}
      </h2>
      {rows.length === 0 ? <p className="text-sm text-muted">No devices in this group yet.</p> : (
        <>
          <div style={{ height: 30 + rows.length * 34 }} role="img" aria-label={title}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
                <CartesianGrid horizontal={false} stroke="#e3e8ea" />
                <XAxis type="number" tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12 }} />
                <YAxis type="category" dataKey="name" width={150} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v: any) => `${Number(v).toFixed(1)}%`} />
                <Bar dataKey="pct" fill={tone === "down" ? "#0e7490" : "#d97706"} radius={[0, 6, 6, 0]} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <ul className="mt-2 divide-y divide-line/70">
            {rows.map((r) => (
              <li key={r.id} className="flex items-center gap-3 py-2.5">
                <Thumb d={r} />
                <div className="min-w-0 flex-1">
                  <Link className="block truncate text-sm font-medium hover:text-indigo-700" to={`/devices/${r.id}`}>{r.name}</Link>
                  <div className="text-xs text-muted">{r.brand} · {money(r.first_price, r.currency)} → {money(r.latest_price, r.currency)}</div>
                </div>
                <span className="text-sm font-semibold">{pct(r.pct_change)}</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

function LatestForecast({ id }: { id: number }) {
  const { data: p, error, loading } = useAsync<Prediction>(() => api.prediction(id), [id]);
  return (
    <div className="card p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 font-semibold"><Icon name="ChartLine" className="h-4 w-4 text-indigo-600" />Your latest forecast</h2>
        {p && <Link className="btn !py-1 text-xs" to={`/predictions/${p.id}`}>Open full result<Icon name="ArrowRight" className="h-3.5 w-3.5" /></Link>}
      </div>
      {loading ? <Spinner /> : error || !p ? <ErrorBox error={error} /> : (
        <>
          <div className="mb-3 flex flex-wrap items-center gap-2 text-sm"><b>{p.device_name}</b>{p.is_sample && <SampleBadge />}{p.overall_trend && <TrendBadge trend={p.overall_trend} />}</div>
          {p.history && <PriceChart history={p.history} path={p.path} currency={p.currency} height={260} />}
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <div className="rounded-xl bg-slate-50 p-3"><div className="text-xs text-muted">Current</div><div className="font-semibold">{money(p.current_price, p.currency)}</div></div>
            {p.results.slice(0, 3).map((r) => (
              <div key={r.horizon_months} className="rounded-xl bg-amber-50/70 p-3"><div className="text-xs text-muted">After {r.label}</div><div className="font-semibold">{money(r.predicted_price, p.currency)}</div><div className="text-xs text-muted">{pct(r.pct_change)}</div></div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

const QUICK: { to: string; icon: IconName; title: string; text: string }[] = [
  { to: "/predict", icon: "Brain", title: "AI price prediction", text: "Estimate a device's future price" },
  { to: "/compare", icon: "GitCompare", title: "Compare devices", text: "Specs and price history side by side" },
  { to: "/smartphones", icon: "Smartphone", title: "Smartphones", text: "Browse phones by brand and price" },
  { to: "/laptops", icon: "Laptop", title: "Laptops", text: "Gaming, student, business, general" },
];

export default function Dashboard() {
  const { data, error, loading } = useAsync(() => api.dashboard(), []);
  if (loading) return <Spinner />;
  if (error || !data) return <ErrorBox error={error} />;
  const total = Math.max(1, data.laptops + data.smartphones);
  const latest = data.recent_predictions[0];
  return (
    <>
      <div className="hero-gradient relative mb-6 overflow-hidden rounded-3xl text-white">
        <div className="bg-tech-circuit absolute inset-0 opacity-30" aria-hidden="true" />
        <div className="relative grid items-center gap-4 p-6 md:grid-cols-[1fr_auto] md:p-8">
          <div>
            <p className="text-sm text-indigo-200">Price analytics</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight md:text-3xl">Dashboard</h1>
            <p className="mt-2 max-w-xl text-sm text-slate-300">Catalogue overview, price movements and your recent forecasts. Forecasts are estimates, not guaranteed prices.</p>
            <div className="mt-5 flex flex-wrap gap-2"><Link className="btn btn-primary" to="/predict"><Icon name="Sparkles" className="h-4 w-4" />New forecast</Link><Link className="btn btn-ghost-light" to="/smartphones">Browse devices</Link></div>
          </div>
          <img src="/images/art/devices.svg" alt="" width={320} height={200} className="hidden w-64 rounded-2xl md:block" />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <Stat icon="Layers" label="Total devices" value={data.total_devices} />
        <Stat icon="Smartphone" tone="teal" label="Smartphones" value={data.smartphones} />
        <Stat icon="Laptop" tone="amber" label="Laptops" value={data.laptops} />
        <Stat icon="Database" tone="rose" label="Historical records" value={data.history_records.toLocaleString()} />
        <Stat icon="Activity" label="Avg. price change" value={pct(data.average_price_change)} hint="first vs latest recorded price" />
      </div>

      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-3">
        <div className="lg:col-span-2">
          {latest ? <LatestForecast id={latest.id} /> : (
            <EmptyState icon="Sparkles" title="Run your first forecast" image="/images/art/forecast.svg"
              action={<Link className="btn btn-primary" to="/predict">Start a forecast</Link>}>
              Pick a smartphone or laptop and see its estimated price after one, two and three years.
            </EmptyState>
          )}
        </div>
        <div className="space-y-5">
          <div className="card p-5">
            <h2 className="mb-3 font-semibold">Catalogue mix</h2>
            <div className="flex h-3 overflow-hidden rounded-full bg-slate-100" role="img" aria-label={`${data.smartphones} smartphones and ${data.laptops} laptops`}>
              <div className="bg-teal-600" style={{ width: `${(data.smartphones / total) * 100}%` }} /><div className="bg-amber-500" style={{ width: `${(data.laptops / total) * 100}%` }} />
            </div>
            <div className="mt-2 flex justify-between text-xs text-muted"><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-teal-600" />Smartphones {data.smartphones}</span><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-amber-500" />Laptops {data.laptops}</span></div>
            <p className="mt-3 text-sm text-muted">You have run <b className="text-ink">{data.my_predictions}</b> forecast{data.my_predictions === 1 ? "" : "s"}.</p>
          </div>
          <div className="card p-3">
            <h2 className="px-2 pt-2 pb-1 font-semibold">Quick actions</h2>
            <ul>{QUICK.map((q) => (
              <li key={q.to}><Link to={q.to} className="flex items-center gap-3 rounded-xl px-2 py-2 transition hover:bg-slate-50">
                <span className="icon-tile !h-9 !w-9"><Icon name={q.icon} className="h-4 w-4" /></span>
                <span className="min-w-0 flex-1"><span className="block text-sm font-medium">{q.title}</span><span className="block truncate text-xs text-muted">{q.text}</span></span>
                <Icon name="ChevronRight" className="h-4 w-4 text-slate-400" /></Link></li>
            ))}</ul>
          </div>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Movers title="Largest price decreases" rows={data.top_decreases} tone="down" />
        <Movers title="Largest price increases" rows={data.top_increases} tone="up" />
      </div>
      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div className="card p-5">
          <h2 className="mb-3 flex items-center gap-2 font-semibold"><Icon name="ChartColumn" className="h-4 w-4 text-indigo-600" />Price records by month</h2>
          {data.records_by_month.length === 0 ? <p className="text-sm text-muted">No price history has been uploaded yet.</p> : (
            <div style={{ height: 240 }} role="img" aria-label="Records by month">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.records_by_month}><CartesianGrid vertical={false} stroke="#e3e8ea" />
                  <XAxis dataKey="month" tick={{ fontSize: 11 }} minTickGap={24} /><YAxis tick={{ fontSize: 12 }} width={36} allowDecimals={false} />
                  <Tooltip /><Bar dataKey="records" fill="#4f46e5" radius={[4, 4, 0, 0]} isAnimationActive={false} /></BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
        <div className="card p-5">
          <h2 className="mb-3 flex items-center gap-2 font-semibold"><Icon name="History" className="h-4 w-4 text-indigo-600" />Your recent forecasts</h2>
          {data.recent_predictions.length === 0 ? <p className="text-sm text-muted">You haven't run a forecast yet. <Link className="text-indigo-600 underline" to="/predict">Start one</Link>.</p> : (
            <ul className="divide-y divide-line/70">
              {data.recent_predictions.map((p) => (
                <li key={p.id} className="flex items-center gap-3 py-2.5">
                  <Thumb d={{ name: p.device_name, brand: p.brand, category: p.category }} />
                  <div className="min-w-0 flex-1"><Link className="block truncate text-sm font-medium hover:text-indigo-700" to={`/predictions/${p.id}`}>{p.device_name}</Link><div className="text-xs text-muted">{fmtDate(p.created_at)}</div></div>
                  {p.overall_trend && <TrendBadge trend={p.overall_trend} />}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  );
}
