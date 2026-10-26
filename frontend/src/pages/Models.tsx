import { useState } from "react";
import { api, fmtDate, fmtNum, modelLabel } from "../api";
import { ErrorBox, Notice, PageHeader, Spinner, useAsync } from "../components/ui";

export default function Models() {
  const models = useAsync(() => api.admin.models(), []);
  const [logStatus, setLogStatus] = useState("");
  const logs = useAsync(() => api.admin.logs(logStatus || undefined), [logStatus]);
  const [scope, setScope] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<unknown>(null);
  const [result, setResult] = useState<Awaited<ReturnType<typeof api.admin.train>> | null>(null);
  const [open, setOpen] = useState<number | null>(null);

  const train = async () => {
    setBusy(true); setErr(null); setResult(null);
    try {
      setResult(await api.admin.train(scope === "" ? {} : scope === "Laptop" || scope === "Smartphone" ? { category: scope } : { device_id: scope }));
      models.reload(); logs.reload();
    } catch (e) { setErr(e); } finally { setBusy(false); }
  };

  return (
    <>
      <PageHeader title="Models and logs" sub="Each device gets its own model, chosen from several candidates on held-out recent prices." />
      <div className="card mb-5 flex flex-wrap items-end gap-3 p-4">
        <div><label className="label" htmlFor="sc">Train</label>
          <select id="sc" className="input" value={scope} onChange={(e) => setScope(e.target.value)}>
            <option value="">All devices with price history</option><option value="Laptop">All laptops</option><option value="Smartphone">All smartphones</option>
          </select></div>
        <div><label className="label" htmlFor="sd">or one device ID</label><input id="sd" className="input" placeholder="LP001" onChange={(e) => setScope(e.target.value.trim() || "")} /></div>
        <button className="btn btn-primary" onClick={train} disabled={busy}>{busy ? "Training…" : "Train models"}</button>
        <p className="w-full text-xs text-muted">Training runs now and may take a while for large catalogues. Models also retrain automatically when a device's price data changes.</p>
        <div className="w-full"><ErrorBox error={err} /></div>
        {result && (<div className="w-full space-y-2 text-sm">
          <Notice tone="info">Trained {result.trained.length} device(s).</Notice>
          {result.failed.length > 0 && <Notice>{result.failed.length} skipped: {result.failed.map((f) => `${f.device_name} (${f.reason})`).join("; ")}</Notice>}
        </div>)}
      </div>

      <h2 className="mb-2 font-semibold">Model versions</h2>
      {models.loading ? <Spinner /> : (
        <div className="card overflow-x-auto"><table className="w-full">
          <thead><tr>{["Device", "Category", "Model", "Trained", "Data version", "Obs.", "MAE", "RMSE", "MAPE %", "R²", "Active"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
          <tbody>
            {models.data?.items.map((m) => (<>
              <tr key={m.id} className="cursor-pointer hover:bg-paper" onClick={() => setOpen(open === m.id ? null : m.id)}>
                <td className="td">{m.device_name}</td><td className="td">{m.category}</td><td className="td">{modelLabel(m.model_type)}</td><td className="td">{fmtDate(m.trained_at)}</td>
                <td className="td">{m.dataset_version}</td><td className="td">{m.n_observations}</td><td className="td">{fmtNum(m.metrics.mae)}</td><td className="td">{fmtNum(m.metrics.rmse)}</td>
                <td className="td">{fmtNum(m.metrics.mape)}</td><td className="td">{fmtNum(m.metrics.r2)}</td><td className="td">{m.is_active ? "yes" : "no"}</td></tr>
              {open === m.id && <tr key={`${m.id}-d`}><td className="td bg-paper" colSpan={11}>
                {m.candidates.map((c) => <div key={c.name} className="text-sm">{c.selected ? "● " : "○ "}{modelLabel(c.name)}: {c.status === "ok" ? `RMSE ${fmtNum(c.rmse)}, MAE ${fmtNum(c.mae)}, R² ${fmtNum(c.r2)}` : c.status}</div>)}
              </td></tr>}
            </>))}
            {models.data?.items.length === 0 && <tr><td className="td text-muted" colSpan={11}>No models trained yet.</td></tr>}
          </tbody></table></div>
      )}

      <div className="mb-2 mt-6 flex items-center justify-between"><h2 className="font-semibold">Prediction and training logs</h2>
        <select aria-label="Filter logs" className="input w-auto" value={logStatus} onChange={(e) => setLogStatus(e.target.value)}><option value="">All</option><option value="ok">Successful</option><option value="error">Errors</option></select></div>
      {logs.loading ? <Spinner /> : (
        <div className="card overflow-x-auto"><table className="w-full">
          <thead><tr>{["Time", "Event", "Status", "Device", "User", "Message", "ms"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
          <tbody>{logs.data?.items.map((l) => (
            <tr key={l.id}><td className="td whitespace-nowrap">{new Date(l.created_at).toLocaleString()}</td><td className="td">{l.event}</td>
              <td className={`td ${l.status === "error" ? "font-medium text-red-700" : ""}`}>{l.status}</td><td className="td">{l.device_id ?? "—"}</td><td className="td">{l.user ?? "—"}</td>
              <td className="td">{l.message}</td><td className="td">{l.duration_ms}</td></tr>))}
            {logs.data?.items.length === 0 && <tr><td className="td text-muted" colSpan={7}>No log entries.</td></tr>}</tbody></table></div>
      )}
    </>
  );
}
