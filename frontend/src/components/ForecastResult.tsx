import { fmtDate, fmtNum, modelLabel, money, pct, type Prediction } from "../api";
import DownloadLink from "./DownloadLink";
import PriceChart from "./PriceChart";
import { Icon } from "./Icon";
import { Disclaimer, Notice, SampleBadge, TrendBadge } from "./ui";

export default function ForecastResult({ p }: { p: Prediction }) {
  const mi = p.model_info;
  const last = p.results[p.results.length - 1];
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <h2 className="text-lg font-semibold">Estimated future price: {p.device_name}</h2>
        {p.is_sample && <SampleBadge />}
      </div>
      {p.warnings?.map((w, i) => <Notice key={i}>{w}</Notice>)}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card p-4">
          <div className="text-sm text-muted">Current price</div>
          <div className="mt-1 text-2xl font-semibold">{money(p.current_price, p.currency)}</div>
          <div className="mt-1 text-xs text-muted">latest known, {fmtDate(p.as_of)}</div>
        </div>
        {p.results.map((r) => (
          <div key={r.horizon_months} className="card border-amber-200 bg-gradient-to-br from-white to-amber-50/60 p-4">
            <div className="text-sm text-muted">Estimated after {r.label}</div>
            <div className="mt-1 text-2xl font-semibold">{money(r.predicted_price, p.currency)}</div>
            <div className="mt-1 text-xs text-muted">
              {pct(r.pct_change)} ({money(r.abs_change, p.currency)}) · range {money(r.lower, p.currency)}–{money(r.upper, p.currency)}
            </div>
          </div>
        ))}
      </div>

      {last && (
        <div className="flex items-center gap-2 text-sm">
          Price trend: <TrendBadge trend={last.trend} />
          <span className="text-muted">over {last.label}</span>
        </div>
      )}

      <div className="card p-4">
        <h3 className="mb-2 text-sm font-semibold">Historical and estimated price</h3>
        {p.history && <PriceChart history={p.history} path={p.path} currency={p.currency} />}
        <p className="mt-2 text-xs text-muted">Solid line: recorded prices. Dashed line and shaded band: estimate and approximate 95% range ({mi?.interval.method}).</p>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead><tr>{["Horizon", "Forecast date", "Estimated price", "Absolute change", "Change", "Trend"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
          <tbody>
            {p.results.map((r) => (
              <tr key={r.horizon_months}>
                <td className="td font-medium">{r.label}</td><td className="td">{fmtDate(r.forecast_date)}</td>
                <td className="td">{money(r.predicted_price, p.currency)}</td><td className="td">{money(r.abs_change, p.currency)}</td>
                <td className="td">{pct(r.pct_change)}</td><td className="td"><TrendBadge trend={r.trend} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap gap-2">
        <DownloadLink className="btn btn-primary" path={`/api/predictions/${p.id}/csv`}><Icon name="Download" className="h-4 w-4" />Download CSV</DownloadLink>
        <DownloadLink className="btn" path={`/api/predictions/${p.id}/pdf`}><Icon name="FileDown" className="h-4 w-4" />Download PDF report</DownloadLink>
      </div>

      {mi && (
        <details className="card p-4 text-sm">
          <summary className="cursor-pointer font-semibold">Model details</summary>
          <dl className="mt-3 grid gap-x-6 gap-y-1 sm:grid-cols-2">
            <div><dt className="inline text-muted">Model used: </dt><dd className="inline font-medium">{modelLabel(mi.model_type)}</dd></div>
            <div><dt className="inline text-muted">Category pipeline: </dt><dd className="inline">{mi.category}</dd></div>
            <div><dt className="inline text-muted">Trained: </dt><dd className="inline">{fmtDate(mi.trained_at)}</dd></div>
            <div><dt className="inline text-muted">Dataset version: </dt><dd className="inline">{mi.dataset_version}</dd></div>
            <div><dt className="inline text-muted">Observations: </dt><dd className="inline">{mi.n_observations}</dd></div>
            <div><dt className="inline text-muted">Validation: </dt><dd className="inline">{mi.metrics.validation}</dd></div>
            <div><dt className="inline text-muted">MAE / RMSE: </dt><dd className="inline">{fmtNum(mi.metrics.mae)} / {fmtNum(mi.metrics.rmse)}</dd></div>
            <div><dt className="inline text-muted">MAPE / R²: </dt><dd className="inline">{fmtNum(mi.metrics.mape)}% / {fmtNum(mi.metrics.r2)}</dd></div>
          </dl>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full">
              <thead><tr>{["Candidate model", "MAE", "RMSE", "MAPE %", "R²", ""].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
              <tbody>
                {mi.candidates.map((c) => (
                  <tr key={c.name} className={c.selected ? "bg-indigo-50" : ""}>
                    <td className="td">{modelLabel(c.name)}</td>
                    {c.status === "ok" ? (<><td className="td">{fmtNum(c.mae)}</td><td className="td">{fmtNum(c.rmse)}</td><td className="td">{fmtNum(c.mape)}</td><td className="td">{fmtNum(c.r2)}</td><td className="td">{c.selected && "selected"}</td></>)
                      : <td className="td text-muted" colSpan={5}>{c.status}</td>}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-muted">Models are compared on the most recent observations, which are held back from training (no shuffling). With few observations, metrics are noisy.</p>
        </details>
      )}
      <Disclaimer />
    </div>
  );
}
