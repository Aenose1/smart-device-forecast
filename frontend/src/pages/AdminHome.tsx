import { useState, type FormEvent } from "react";
import { api, money, type Device } from "../api";
import { ErrorBox, PageHeader, Spinner, Stat, useAsync } from "../components/ui";

const blank = { device_id: "", name: "", brand: "", category: "Laptop", release_date: "", launch_price: "", current_price: "", currency: "INR", status: "Active", specs: "" };
type Form = typeof blank;

const specsToText = (s: Record<string, string>) => Object.entries(s).map(([k, v]) => `${k}=${v}`).join("\n");
const textToSpecs = (t: string) => Object.fromEntries(t.split("\n").map((l) => l.split(/=(.*)/s)).filter((p) => p[0]?.trim() && p[1]?.trim()).map((p) => [p[0].trim(), p[1].trim()]));

export default function AdminHome() {
  const ov = useAsync(() => api.admin.overview(), []);
  const [q, setQ] = useState("");
  const list = useAsync(() => api.devices({ q, page_size: 100 }), [q]);
  const [form, setForm] = useState<Form | null>(null);
  const [editing, setEditing] = useState<string | undefined>();
  const [err, setErr] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  const open = (d?: Device) => {
    setErr(null); setEditing(d?.id);
    setForm(d ? { device_id: d.id, name: d.name, brand: d.brand, category: d.category, release_date: d.release_date ?? "", launch_price: String(d.launch_price),
      current_price: d.current_price ? String(d.current_price) : "", currency: d.currency, status: d.status, specs: specsToText(d.specs) } : { ...blank });
  };
  const save = async (e: FormEvent) => {
    e.preventDefault(); if (!form) return; setBusy(true); setErr(null);
    try {
      await api.admin.saveDevice({ ...form, launch_price: Number(form.launch_price), current_price: form.current_price ? Number(form.current_price) : null,
        release_date: form.release_date || null, specs: textToSpecs(form.specs) }, editing);
      setForm(null); list.reload(); ov.reload();
    } catch (x) { setErr(x); } finally { setBusy(false); }
  };
  const del = async (d: Device) => {
    if (!window.confirm(`Delete ${d.name}? Its price history and models are removed too. Users' saved forecasts are kept.`)) return;
    try { await api.admin.deleteDevice(d.id); list.reload(); ov.reload(); } catch (x) { setErr(x); }
  };
  const set = (k: keyof Form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setForm({ ...form!, [k]: e.target.value });

  return (
    <>
      <PageHeader title="Administration" sub="Manage the device catalogue." actions={<button className="btn btn-primary" onClick={() => open()}>Add device</button>} />
      {ov.data && (
        <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-5">
          <Stat label="Users" value={ov.data.users} /><Stat label="Devices" value={ov.data.devices} hint={`${ov.data.devices_without_history} without history`} />
          <Stat label="Datasets" value={ov.data.datasets} /><Stat label="Price records" value={ov.data.history_records.toLocaleString()} />
          <Stat label="Active models" value={ov.data.active_models} />
        </div>
      )}
      {form && (
        <form onSubmit={save} className="card mb-5 grid gap-3 p-4 md:grid-cols-4">
          <h2 className="font-semibold md:col-span-4">{editing ? `Edit ${editing}` : "Add device"}</h2>
          <div className="md:col-span-4"><ErrorBox error={err} /></div>
          <div><label className="label" htmlFor="did">Device ID</label><input id="did" className="input" required disabled={!!editing} pattern="[A-Za-z0-9_\-]{2,32}" title="2-32 letters, digits, - or _" value={form.device_id} onChange={set("device_id")} placeholder="LP101" /></div>
          <div className="md:col-span-2"><label className="label" htmlFor="dn">Name</label><input id="dn" className="input" required maxLength={160} value={form.name} onChange={set("name")} /></div>
          <div><label className="label" htmlFor="db">Brand</label><input id="db" className="input" required maxLength={80} value={form.brand} onChange={set("brand")} /></div>
          <div><label className="label" htmlFor="dc">Category</label><select id="dc" className="input" value={form.category} onChange={set("category")}><option>Laptop</option><option>Smartphone</option></select></div>
          <div><label className="label" htmlFor="dr">Release date</label><input id="dr" className="input" type="date" value={form.release_date} onChange={set("release_date")} /></div>
          <div><label className="label" htmlFor="lp">Launch price</label><input id="lp" className="input" type="number" min={1} step="any" required value={form.launch_price} onChange={set("launch_price")} /></div>
          <div><label className="label" htmlFor="cp">Current price (optional)</label><input id="cp" className="input" type="number" min={1} step="any" value={form.current_price} onChange={set("current_price")} /></div>
          <div><label className="label" htmlFor="cu">Currency</label><input id="cu" className="input" maxLength={3} required value={form.currency} onChange={set("currency")} /></div>
          <div><label className="label" htmlFor="st">Status</label><select id="st" className="input" value={form.status} onChange={set("status")}><option>Active</option><option>Discontinued</option><option>Upcoming</option></select></div>
          <div className="md:col-span-3"><label className="label" htmlFor="sp">Specifications (one “name=value” per line)</label>
            <textarea id="sp" className="input h-28 font-mono" value={form.specs} onChange={set("specs")} placeholder={"RAM=16 GB\nStorage=512 GB\nDisplay=15.6 inch"} /></div>
          <div className="flex gap-2 md:col-span-4"><button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : "Save device"}</button><button type="button" className="btn" onClick={() => setForm(null)}>Cancel</button></div>
        </form>
      )}
      {!form && <ErrorBox error={err} />}
      <div className="mb-3 max-w-sm"><label className="label" htmlFor="aq">Find a device</label><input id="aq" className="input" value={q} onChange={(e) => setQ(e.target.value)} /></div>
      {list.loading ? <Spinner /> : (
        <div className="card overflow-x-auto"><table className="w-full">
          <thead><tr>{["ID", "Name", "Brand", "Category", "Launch price", "Status", ""].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
          <tbody>
            {list.data?.items.map((d) => (
              <tr key={d.id}><td className="td">{d.id}</td><td className="td font-medium">{d.name}</td><td className="td">{d.brand}</td><td className="td">{d.category}</td>
                <td className="td">{money(d.launch_price, d.currency)}</td><td className="td">{d.status}</td>
                <td className="td whitespace-nowrap text-right"><button className="btn mr-2" onClick={() => open(d)}>Edit</button><button className="btn btn-danger" onClick={() => del(d)}>Delete</button></td></tr>
            ))}
            {list.data?.items.length === 0 && <tr><td className="td text-muted" colSpan={7}>No devices yet. Add one, then upload its price history under Datasets.</td></tr>}
          </tbody></table></div>
      )}
    </>
  );
}
