import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, fmtDate, money, pct } from "../api";
import DownloadLink from "../components/DownloadLink";
import ForecastResult from "../components/ForecastResult";
import { ErrorBox, PageHeader, SampleBadge, Spinner, TrendBadge, useAsync } from "../components/ui";

export function PredictionHistory() {
  const [page, setPage] = useState(1);
  const { data, error, loading } = useAsync(() => api.predictions({ page, page_size: 15 }), [page]);
  const pages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;
  return (
    <>
      <PageHeader title="My forecasts" sub="Only you can see these." actions={<Link className="btn btn-primary" to="/predict">New forecast</Link>} />
      <ErrorBox error={error} />
      {loading ? <Spinner /> : data && (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead><tr>{["Date", "Device", "Price then", "Estimate at end of period", "Trend", "Files"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
            <tbody>
              {data.items.map((p) => {
                const last = p.results[p.results.length - 1];
                return (
                  <tr key={p.id}>
                    <td className="td">{fmtDate(p.created_at)}</td>
                    <td className="td"><Link className="font-medium text-accent hover:underline" to={`/predictions/${p.id}`}>{p.device_name}</Link> {p.is_sample && <SampleBadge />}<div className="text-xs text-muted">{p.brand} · {p.category}</div></td>
                    <td className="td">{money(p.current_price, p.currency)}</td>
                    <td className="td">{last ? <>{money(last.predicted_price, p.currency)} <span className="text-muted">({last.label}, {pct(last.pct_change)})</span></> : "—"}</td>
                    <td className="td">{p.overall_trend && <TrendBadge trend={p.overall_trend} />}</td>
                    <td className="td whitespace-nowrap"><DownloadLink className="text-accent hover:underline" path={`/api/predictions/${p.id}/csv`}>CSV</DownloadLink> · <DownloadLink className="text-accent hover:underline" path={`/api/predictions/${p.id}/pdf`}>PDF</DownloadLink></td>
                  </tr>
                );
              })}
              {data.items.length === 0 && <tr><td className="td text-muted" colSpan={6}>No forecasts yet. <Link className="text-accent underline" to="/predict">Create your first one</Link>.</td></tr>}
            </tbody>
          </table>
          <div className="flex items-center justify-between p-3 text-sm">
            <span className="text-muted">{data.total} forecast{data.total === 1 ? "" : "s"}</span>
            <span className="flex items-center gap-2"><button className="btn" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>Page {page} of {pages}<button className="btn" disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button></span>
          </div>
        </div>
      )}
    </>
  );
}

export function PredictionView() {
  const { id = "" } = useParams();
  const { data, error, loading } = useAsync(() => api.prediction(id), [id]);
  return (
    <>
      <PageHeader title="Saved forecast" sub={data && `Created ${fmtDate(data.created_at)}`} actions={<Link className="btn" to="/predictions">Back to my forecasts</Link>} />
      {loading ? <Spinner /> : error || !data ? <ErrorBox error={error} /> : <ForecastResult p={data} />}
    </>
  );
}
