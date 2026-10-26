import { useState } from "react";
import { Link } from "react-router-dom";
import { api, fmtDate, money } from "../api";
import { ErrorBox, PageHeader, Spinner, useAsync } from "../components/ui";

export default function Devices() {
  const [f, setF] = useState({ q: "", category: "", brand: "", min_price: "", max_price: "" });
  const [applied, setApplied] = useState(f);
  const [page, setPage] = useState(1);
  const brands = useAsync(() => api.brands(applied.category || undefined), [applied.category]);
  const list = useAsync(() => api.devices({ ...applied, page, page_size: 15 }), [applied, page]);
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setF({ ...f, [k]: e.target.value });
  const pages = list.data ? Math.max(1, Math.ceil(list.data.total / list.data.page_size)) : 1;

  return (
    <>
      <PageHeader title="Devices" sub="Search the catalogue and open a device for its price history and forecast." />
      <form className="card mb-4 grid gap-3 p-4 md:grid-cols-6" onSubmit={(e) => { e.preventDefault(); setPage(1); setApplied(f); }}>
        <div className="md:col-span-2"><label className="label" htmlFor="q">Name, brand or ID</label><input id="q" className="input" value={f.q} onChange={set("q")} placeholder="e.g. gaming" /></div>
        <div><label className="label" htmlFor="cat">Category</label>
          <select id="cat" className="input" value={f.category} onChange={(e) => setF({ ...f, category: e.target.value, brand: "" })}>
            <option value="">All</option><option>Laptop</option><option>Smartphone</option></select></div>
        <div><label className="label" htmlFor="brand">Brand</label>
          <select id="brand" className="input" value={f.brand} onChange={set("brand")}><option value="">All</option>{brands.data?.map((b) => <option key={b}>{b}</option>)}</select></div>
        <div><label className="label" htmlFor="min">Min price</label><input id="min" className="input" type="number" min={0} value={f.min_price} onChange={set("min_price")} /></div>
        <div><label className="label" htmlFor="max">Max price</label><input id="max" className="input" type="number" min={0} value={f.max_price} onChange={set("max_price")} /></div>
        <div className="flex gap-2 md:col-span-6">
          <button className="btn btn-primary">Search</button>
          <button type="button" className="btn" onClick={() => { const z = { q: "", category: "", brand: "", min_price: "", max_price: "" }; setF(z); setApplied(z); setPage(1); }}>Clear filters</button>
        </div>
      </form>
      <ErrorBox error={list.error} />
      {list.loading ? <Spinner /> : list.data && (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead><tr>{["Device", "Brand", "Category", "Released", "Latest price", "Status"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
            <tbody>
              {list.data.items.map((d) => (
                <tr key={d.id}>
                  <td className="td"><Link className="font-medium text-accent hover:underline" to={`/devices/${d.id}`}>{d.name}</Link><div className="text-xs text-muted">{d.id}</div></td>
                  <td className="td">{d.brand}</td><td className="td">{d.category}</td>
                  <td className="td">{d.release_date ? fmtDate(d.release_date) : "—"}</td>
                  <td className="td">{money(d.latest_price, d.currency)}</td><td className="td">{d.status}</td>
                </tr>
              ))}
              {list.data.items.length === 0 && <tr><td className="td text-muted" colSpan={6}>No devices match these filters. Try clearing some of them.</td></tr>}
            </tbody>
          </table>
          <div className="flex items-center justify-between p-3 text-sm">
            <span className="text-muted">{list.data.total} device{list.data.total === 1 ? "" : "s"}</span>
            <span className="flex items-center gap-2">
              <button className="btn" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
              Page {page} of {pages}
              <button className="btn" disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button>
            </span>
          </div>
        </div>
      )}
    </>
  );
}
