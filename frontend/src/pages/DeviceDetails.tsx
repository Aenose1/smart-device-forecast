import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError, fmtDate, money, pct, type Prediction } from "../api";
import DownloadLink from "../components/DownloadLink";
import ForecastResult from "../components/ForecastResult";
import { Icon } from "../components/Icon";
import PriceChart from "../components/PriceChart";
import ProductImage from "../components/ProductImage";
import { ErrorBox, Notice, SampleBadge, Spinner, Stat, useAsync } from "../components/ui";
import { deviceImage, keySpecs, releaseYear } from "../lib/catalog";

export default function DeviceDetails() {
  const { id = "" } = useParams();
  const dev = useAsync(() => api.device(id), [id]);
  const hist = useAsync(() => api.history(id), [id]);
  const [pred, setPred] = useState<Prediction | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<unknown>(null);

  const run = async () => {
    setBusy(true); setErr(null);
    try { setPred(await api.forecast(id, 3)); } catch (e) { setErr(e); } finally { setBusy(false); }
  };

  if (dev.loading) return <Spinner />;
  if (dev.error || !dev.data) return <ErrorBox error={dev.error} />;
  const d = dev.data, s = hist.data?.stats;
  const cur = d.currency;
  const img = deviceImage(d);
  const move = (m: { amount: number; pct: number; from_date: string; to_date: string } | null) => m ? `${money(Math.abs(m.amount), cur)} (${pct(m.pct)}) · ${fmtDate(m.from_date)} → ${fmtDate(m.to_date)}` : "None recorded";
  const insufficient = err instanceof ApiError && (err.code === "insufficient_history" || err.code === "no_price_history");

  return (
    <>
      <nav aria-label="Breadcrumb" className="mb-3 text-sm text-muted">
        <Link className="hover:text-indigo-700" to={d.category === "Laptop" ? "/laptops" : "/smartphones"}>{d.category === "Laptop" ? "Laptops" : "Smartphones"}</Link>
        <span className="mx-1.5">/</span><Link className="hover:text-indigo-700" to={`${d.category === "Laptop" ? "/laptops" : "/smartphones"}?brand=${encodeURIComponent(d.brand)}`}>{d.brand}</Link>
      </nav>
      <section className="card mb-5 grid overflow-hidden md:grid-cols-[22rem_1fr]">
        <div className="bg-slate-50"><ProductImage src={img.src} fallback={img.fallback} alt={img.alt} category={d.category} priority /></div>
        <div className="flex flex-col p-5 md:p-7">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="font-semibold uppercase tracking-wide text-indigo-600">{d.brand}</span>
            <span className="chip">{d.category}</span>{d.specs["Laptop type"] && <span className="chip">{d.specs["Laptop type"]}</span>}
            {releaseYear(d) && <span className="chip">Released {releaseYear(d)}</span>}<span className="chip">{d.status}</span>
            {hist.data?.has_sample_data && <SampleBadge />}
          </div>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight md:text-3xl">{d.name}</h1>
          <dl className="mt-4 grid gap-x-6 gap-y-1.5 text-sm sm:grid-cols-2">
            {keySpecs(d).map((k) => <div key={k.label} className="flex justify-between gap-3 border-b border-line/70 py-1"><dt className="text-muted">{k.label}</dt><dd className="text-right font-medium">{k.value}</dd></div>)}
          </dl>
          <div className="mt-auto flex flex-wrap items-end justify-between gap-3 pt-5">
            <div><div className="text-xs uppercase tracking-wide text-muted">Reference price</div><div className="text-2xl font-semibold">{money(s?.current_price ?? d.latest_price, cur)}</div></div>
            <div className="flex flex-wrap gap-2">
              <Link className="btn" to={`/compare?ids=${encodeURIComponent(d.id)}`}><Icon name="GitCompare" className="h-4 w-4" />Compare</Link>
              <DownloadLink className="btn" path={`/api/devices/${d.id}/history?format=csv`}><Icon name="FileDown" className="h-4 w-4" />History CSV</DownloadLink>
              <a className="btn btn-primary" href="#forecast"><Icon name="Sparkles" className="h-4 w-4" />Forecast</a>
            </div>
          </div>
        </div>
      </section>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat icon="Tag" label="Latest known price" value={money(s?.current_price ?? d.latest_price, cur)} hint={s ? fmtDate(s.last_date) : "no history yet"} />
        <Stat icon="Calendar" tone="teal" label="Launch price" value={money(d.launch_price, cur)} hint={d.release_date ? `released ${fmtDate(d.release_date)}` : undefined} />
        <Stat icon="TrendingUp" tone="amber" label="Change since first record" value={pct(s?.pct_change)} hint={s ? `${money(s.abs_change, cur)}` : undefined} />
        <Stat icon="Database" tone="rose" label="Historical records" value={s?.records ?? 0} />
      </div>

      <div className="mt-5 grid grid-cols-1 gap-5 lg:grid-cols-3">
        <div className="card p-4 lg:col-span-2">
          <h2 className="mb-2 font-semibold">Price history</h2>
          {hist.loading ? <Spinner /> : hist.data && hist.data.history.length > 0 ? (
            <PriceChart currency={cur} history={hist.data.history.map((h) => [h.date, h.price])} />
          ) : <p className="py-8 text-center text-sm text-muted">No historical prices have been uploaded for this device yet.</p>}
        </div>
        <div className="card p-4">
          <h2 className="mb-2 font-semibold">Specifications</h2>
          {Object.keys(d.specs).length === 0 ? <p className="text-sm text-muted">No specifications recorded.</p> : (
            <dl className="text-sm">{Object.entries(d.specs).map(([k, v]) => (
              <div key={k} className="flex justify-between gap-3 border-b border-line/70 py-1.5"><dt className="text-muted">{k}</dt><dd className="text-right">{v}</dd></div>))}</dl>
          )}
        </div>
      </div>

      {s && (
        <div className="card mt-5 p-4">
          <h2 className="mb-2 font-semibold">Historical summary</h2>
          <dl className="grid gap-x-8 gap-y-2 text-sm sm:grid-cols-2">
            <div><dt className="inline text-muted">Minimum: </dt><dd className="inline">{money(s.min_price, cur)} ({fmtDate(s.min_date)})</dd></div>
            <div><dt className="inline text-muted">Maximum: </dt><dd className="inline">{money(s.max_price, cur)} ({fmtDate(s.max_date)})</dd></div>
            <div><dt className="inline text-muted">Average: </dt><dd className="inline">{money(s.avg_price, cur)}</dd></div>
            <div><dt className="inline text-muted">Period: </dt><dd className="inline">{fmtDate(s.first_date)} – {fmtDate(s.last_date)}</dd></div>
            <div><dt className="inline text-muted">Highest drop: </dt><dd className="inline">{move(s.highest_drop)}</dd></div>
            <div><dt className="inline text-muted">Highest increase: </dt><dd className="inline">{move(s.highest_increase)}</dd></div>
          </dl>
        </div>
      )}

      <section className="mt-6" id="forecast">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 className="flex items-center gap-2 text-lg font-semibold"><Icon name="ChartLine" className="h-5 w-5 text-indigo-600" />3-year price forecast</h2>
          <button className="btn btn-primary" onClick={run} disabled={busy}><Icon name="Sparkles" className="h-4 w-4" />{busy ? "Forecasting…" : pred ? "Run again" : "Generate forecast"}</button>
        </div>
        <ErrorBox error={err} />
        {insufficient && <p className="mt-2 text-sm text-muted">A forecast needs enough recorded prices. An administrator can upload more history under Datasets.</p>}
        {pred ? <ForecastResult p={pred} /> : !err && <Notice tone="info">Generate a forecast to see the estimated price after 1, 2 and 3 years, with downloadable CSV and PDF.</Notice>}
      </section>
    </>
  );
}
