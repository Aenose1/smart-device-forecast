import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, fmtDate, money, pct, type Device, type HistoryResponse } from "../api";
import DeviceCombobox from "../components/DeviceCombobox";
import { Icon } from "../components/Icon";
import ProductImage from "../components/ProductImage";
import { EmptyState, ErrorBox, Notice, PageHeader, SampleBadge, Spinner } from "../components/ui";
import { deviceImage, releaseYear } from "../lib/catalog";

interface Entry { device: Device; hist: HistoryResponse | null }
const COLORS = ["#4f46e5", "#0e7490", "#d97706"];
const MAX = 3;

export default function Compare() {
  const [sp, setSp] = useSearchParams();
  const ids = useMemo(() => (sp.get("ids") ?? "").split(",").map((s) => s.trim()).filter(Boolean).slice(0, MAX), [sp]);
  const [items, setItems] = useState<Entry[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<unknown>(null);
  const key = ids.join(",");

  useEffect(() => {
    let live = true;
    if (ids.length === 0) { setItems([]); return; }
    setBusy(true); setErr(null);
    Promise.all(ids.map(async (id) => ({ device: await api.device(id), hist: await api.history(id).catch(() => null) })))
      .then((r) => live && setItems(r)).catch((e) => live && setErr(e)).finally(() => live && setBusy(false));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const setIds = (next: string[]) => setSp(next.length ? { ids: next.join(",") } : {}, { replace: true });
  const add = (d: Device) => { if (!ids.includes(d.id) && ids.length < MAX) setIds([...ids, d.id]); };
  const remove = (id: string) => setIds(ids.filter((x) => x !== id));

  const rows = useMemo(() => {
    const m = new Map<number, Record<string, number>>();
    items.forEach((e, i) => e.hist?.history.forEach((h) => {
      const t = new Date(h.date).getTime(); const r = m.get(t) ?? { t }; r[`d${i}`] = h.price; m.set(t, r);
    }));
    return [...m.values()].sort((a, b) => a.t - b.t);
  }, [items]);
  const specKeys = useMemo(() => [...new Set(items.flatMap((e) => Object.keys(e.device.specs)))].filter((k) => k !== "Image URL"), [items]);
  const anySample = items.some((e) => e.hist?.has_sample_data);
  const fmtT = (v: number) => new Date(v).toLocaleDateString("en-GB", { month: "short", year: "2-digit" });
  const compact = (v: number) => new Intl.NumberFormat("en-IN", { notation: "compact", maximumFractionDigits: 1 }).format(v);

  return (
    <>
      <PageHeader title="Compare devices" sub={`Put up to ${MAX} smartphones or laptops side by side: reference price, specifications and recorded price history.`} />
      <div className="card mb-5 p-5">
        <label className="label">Add a device {ids.length >= MAX && <span className="font-normal text-muted">(maximum reached)</span>}</label>
        <div className="max-w-xl"><DeviceCombobox key={key} onSelect={add} /></div>
      </div>
      <ErrorBox error={err} />
      {busy && <Spinner label="Loading devices…" />}
      {!busy && ids.length === 0 && (
        <EmptyState icon="GitCompare" title="Choose devices to compare" image="/images/art/compare.svg">
          Search for a model above. You can also open any device and press <b>Compare</b>.
        </EmptyState>
      )}
      {!busy && items.length > 0 && (
        <div className="space-y-5">
          <div className={`grid gap-4 ${items.length === 1 ? "md:grid-cols-1" : items.length === 2 ? "md:grid-cols-2" : "md:grid-cols-3"}`}>
            {items.map((e, i) => {
              const img = deviceImage(e.device), s = e.hist?.stats;
              return (
                <div key={e.device.id} className="card overflow-hidden" style={{ borderTop: `4px solid ${COLORS[i]}` }}>
                  <ProductImage src={img.src} fallback={img.fallback} alt={img.alt} category={e.device.category} ratio="16 / 9" className="bg-slate-50" />
                  <div className="p-4">
                    <div className="flex items-start justify-between gap-2">
                      <div><div className="text-xs font-semibold uppercase tracking-wide text-indigo-600">{e.device.brand}</div>
                        <Link to={`/devices/${e.device.id}`} className="font-semibold hover:text-indigo-700">{e.device.name}</Link></div>
                      <button className="btn !p-1.5" aria-label={`Remove ${e.device.name}`} onClick={() => remove(e.device.id)}><Icon name="X" className="h-4 w-4" /></button>
                    </div>
                    <div className="mt-3 text-xs uppercase tracking-wide text-muted">Reference price</div>
                    <div className="text-xl font-semibold">{money(e.device.latest_price, e.device.currency)}</div>
                    <div className="mt-1 text-xs text-muted">{s ? `${pct(s.pct_change)} since ${fmtDate(s.first_date)}` : "No price history"} · launch {money(e.device.launch_price, e.device.currency)}</div>
                    <Link className="btn btn-primary mt-3 w-full text-xs" to={`/predict?device=${encodeURIComponent(e.device.id)}`}><Icon name="Sparkles" className="h-3.5 w-3.5" />Forecast this device</Link>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="card p-5">
            <div className="mb-2 flex flex-wrap items-center gap-2"><h2 className="font-semibold">Price history</h2>{anySample && <SampleBadge />}</div>
            {rows.length === 0 ? <p className="py-8 text-center text-sm text-muted">None of these devices has recorded prices yet.</p> : (
              <div role="img" aria-label="Price history of the selected devices" style={{ height: 340 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={rows} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
                    <CartesianGrid stroke="#e3e8ea" vertical={false} />
                    <XAxis dataKey="t" type="number" scale="time" domain={["dataMin", "dataMax"]} tickFormatter={fmtT} tick={{ fontSize: 12 }} minTickGap={40} />
                    <YAxis tickFormatter={compact} tick={{ fontSize: 12 }} width={56} domain={["auto", "auto"]} />
                    <Tooltip labelFormatter={(v) => fmtDate(new Date(Number(v)).toISOString())} formatter={(v: any, name: string) => [money(Number(v), items[0].device.currency), name]} />
                    <Legend verticalAlign="top" height={28} />
                    {items.map((e, i) => <Line key={e.device.id} dataKey={`d${i}`} name={e.device.name} stroke={COLORS[i]} strokeWidth={2.2} dot={false} connectNulls isAnimationActive={false} />)}
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            )}
            {new Set(items.map((e) => e.device.currency)).size > 1 && <div className="mt-3"><Notice>These devices use different currencies; the chart axis is not converted.</Notice></div>}
          </div>

          <div className="card overflow-x-auto">
            <table className="w-full">
              <thead><tr><th className="th">Specification</th>{items.map((e, i) => <th key={e.device.id} className="th" style={{ color: COLORS[i] }}>{e.device.name}</th>)}</tr></thead>
              <tbody>
                {[["Brand", (d: Device) => d.brand], ["Category", (d: Device) => d.category], ["Release year", (d: Device) => String(releaseYear(d) ?? "—")],
                  ["Launch price", (d: Device) => money(d.launch_price, d.currency)], ["Reference price", (d: Device) => money(d.latest_price, d.currency)]].map(([label, f]) => (
                  <tr key={label as string}><td className="td font-medium">{label as string}</td>{items.map((e) => <td key={e.device.id} className="td">{(f as (d: Device) => string)(e.device)}</td>)}</tr>
                ))}
                {specKeys.map((k) => <tr key={k}><td className="td font-medium">{k}</td>{items.map((e) => <td key={e.device.id} className="td">{e.device.specs[k] ?? "—"}</td>)}</tr>)}
                <tr><td className="td font-medium">Change since first record</td>{items.map((e) => <td key={e.device.id} className="td">{pct(e.hist?.stats?.pct_change)}</td>)}</tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}
