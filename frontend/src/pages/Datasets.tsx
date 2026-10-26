import { useState } from "react";
import { api, fmtDate, type ValidationReport } from "../api";
import DownloadLink from "../components/DownloadLink";
import { ErrorBox, Notice, PageHeader, SampleBadge, Spinner, useAsync } from "../components/ui";

function Report({ r }: { r: ValidationReport }) {
  return (
    <div className="mt-4 space-y-3 text-sm">
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-3 lg:grid-cols-6">
        {([["Rows read", r.total_rows], ["Valid", r.valid_rows], ["Invalid", r.invalid_rows], ["Duplicates (file)", r.duplicates_in_file], ["Already stored", r.duplicates_existing], ["Missing values", r.missing_values]] as const)
          .map(([k, v]) => <div key={k} className="rounded border border-line p-2"><div className="text-xs text-muted">{k}</div><div className="text-lg font-semibold">{v}</div></div>)}
      </div>
      {r.invalid_device_ids.length > 0 && <Notice>Unknown device IDs: {r.invalid_device_ids.join(", ")}. Add these devices first.</Notice>}
      {r.errors.length > 0 && (
        <div className="max-h-72 overflow-auto rounded border border-line">
          <table className="w-full"><thead><tr>{["Row", "Column", "Problem"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
            <tbody>{r.errors.map((e, i) => <tr key={i}><td className="td">{e.row || "—"}</td><td className="td">{e.column ?? "—"}</td><td className="td">{e.message}</td></tr>)}</tbody></table>
        </div>
      )}
      {r.errors_truncated && <p className="text-xs text-muted">Showing the first {r.errors.length} of {r.error_count} problems.</p>}
    </div>
  );
}

export default function Datasets() {
  const list = useAsync(() => api.admin.datasets(), []);
  const [file, setFile] = useState<File | null>(null);
  const [isSample, setIsSample] = useState(false);
  const [report, setReport] = useState<{ title: string; r: ValidationReport } | null>(null);
  const [err, setErr] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  const act = async (kind: "validate" | "upload") => {
    if (!file) return;
    setBusy(true); setErr(null); setReport(null);
    try {
      if (kind === "validate") setReport({ title: "Validation only. Nothing was stored.", r: await api.admin.validate(file) });
      else { const res = await api.admin.upload(file, isSample); setReport({ title: `Stored ${res.dataset.rows_valid} record(s) from ${res.dataset.filename}.`, r: res.report }); list.reload(); }
    } catch (e) { setErr(e); } finally { setBusy(false); }
  };

  return (
    <>
      <PageHeader title="Datasets" sub="Upload historical price CSVs. Valid rows are stored; problems are reported row by row."
        actions={<DownloadLink className="btn" path="/api/admin/dataset/export">Download processed data (CSV)</DownloadLink>} />
      <div className="card p-4">
        <p className="text-sm text-muted">Required columns: <code>device_id, device_name, category, date, price, source, currency</code>. Dates are YYYY-MM-DD. Device IDs must already exist.</p>
        <div className="mt-3 flex flex-wrap items-end gap-3">
          <div><label className="label" htmlFor="f">CSV file (max 10 MB)</label><input id="f" type="file" accept=".csv,text/csv" className="text-sm" onChange={(e) => setFile(e.target.files?.[0] ?? null)} /></div>
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={isSample} onChange={(e) => setIsSample(e.target.checked)} />This is sample/demo data</label>
          <button className="btn" disabled={!file || busy} onClick={() => act("validate")}>Validate only</button>
          <button className="btn btn-primary" disabled={!file || busy} onClick={() => act("upload")}>{busy ? "Working…" : "Validate and store"}</button>
        </div>
        <div className="mt-3"><ErrorBox error={err} /></div>
        {report && (<><p className="mt-3 font-medium">{report.title}</p><Report r={report.r} /></>)}
      </div>
      <h2 className="mb-2 mt-6 font-semibold">Uploaded datasets</h2>
      {list.loading ? <Spinner /> : (
        <div className="card overflow-x-auto"><table className="w-full">
          <thead><tr>{["#", "File", "Uploaded", "Rows", "Stored", "Invalid", "Duplicates", "Status"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
          <tbody>
            {list.data?.map((d) => (
              <tr key={d.id}><td className="td">{d.id}</td><td className="td">{d.filename} {d.is_sample && <SampleBadge />}</td><td className="td">{fmtDate(d.created_at)}</td>
                <td className="td">{d.rows_total}</td><td className="td">{d.rows_valid}</td><td className="td">{d.rows_invalid}</td><td className="td">{d.rows_duplicate}</td><td className="td">{d.status}</td></tr>
            ))}
            {list.data?.length === 0 && <tr><td className="td text-muted" colSpan={8}>No datasets uploaded yet.</td></tr>}
          </tbody></table></div>
      )}
    </>
  );
}
