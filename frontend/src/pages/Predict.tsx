import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, money, type Device, type Prediction } from "../api";
import DeviceCombobox from "../components/DeviceCombobox";
import ForecastResult from "../components/ForecastResult";
import { Icon, type IconName } from "../components/Icon";
import ProductImage from "../components/ProductImage";
import { ErrorBox, Notice, PageHeader } from "../components/ui";
import { deviceImage, keySpecs } from "../lib/catalog";

const STEPS: { icon: IconName; title: string; text: string }[] = [
  { icon: "Search", title: "1. Choose a device", text: "Search any smartphone or laptop in the catalogue." },
  { icon: "Database", title: "2. We read its price history", text: "Recorded prices, release date and specifications feed the models." },
  { icon: "Brain", title: "3. Models compete", text: "The model with the lowest error on held-out recent prices is used." },
  { icon: "ChartLine", title: "4. You get an estimate", text: "Price after 1, 2, 3… years with an approximate 95% range and CSV / PDF export." },
];

export default function Predict() {
  const [sp] = useSearchParams();
  const [device, setDevice] = useState<Device | null>(null);
  const [category, setCategory] = useState("");
  const [years, setYears] = useState(3);
  const [pred, setPred] = useState<Prediction | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<unknown>(null);
  const preset = sp.get("device");

  // /predict?device=SP101 (from a device card) pre-selects the device
  useEffect(() => {
    if (!preset) return;
    let live = true;
    api.device(preset).then((d) => { if (live) { setDevice(d); setCategory(d.category); } }).catch((e) => live && setErr(e));
    return () => { live = false; };
  }, [preset]);

  const run = async () => {
    if (!device) return;
    setBusy(true); setErr(null); setPred(null);
    try { setPred(await api.forecast(device.id, years)); } catch (e) { setErr(e); } finally { setBusy(false); }
  };
  const img = device ? deviceImage(device) : null;

  return (
    <>
      <PageHeader title="Price Forecast" sub="Choose a device and a forecast period. The result is saved to your history." />
      <div className="card mb-5 grid gap-4 p-5 md:grid-cols-6">
        <div><label className="label" htmlFor="c">Category</label>
          <select id="c" className="input" value={category} onChange={(e) => { setCategory(e.target.value); setDevice(null); }}>
            <option value="">Laptops and smartphones</option><option>Laptop</option><option>Smartphone</option></select></div>
        <div className="md:col-span-3"><label className="label">Device</label>
          <DeviceCombobox key={`${category}-${device?.id ?? ""}`} category={category || undefined} selected={device} onSelect={setDevice} /></div>
        <div><label className="label" htmlFor="y">Forecast period</label>
          <select id="y" className="input" value={years} onChange={(e) => setYears(Number(e.target.value))}>
            {[1, 2, 3, 4, 5].map((y) => <option key={y} value={y}>{y} year{y > 1 ? "s" : ""}</option>)}</select></div>
        <div className="flex items-end"><button className="btn btn-primary w-full" disabled={!device || busy} onClick={run}><Icon name="Sparkles" className="h-4 w-4" />{busy ? "Working…" : "Estimate prices"}</button></div>
        {device && img && (
          <div className="flex items-center gap-4 rounded-xl bg-slate-50 p-3 md:col-span-6">
            <ProductImage src={img.src} fallback={img.fallback} alt={img.alt} category={device.category} className="w-28 shrink-0 rounded-lg" />
            <div className="min-w-0 text-sm">
              <div className="font-semibold">{device.name} <span className="font-normal text-muted">· {device.brand}, {device.category}</span></div>
              <div className="mt-0.5 text-muted">{keySpecs(device).map((k) => k.value).slice(0, 3).join(" · ")}</div>
              <div className="mt-1">Reference price <b>{money(device.latest_price, device.currency)}</b>. The forecast horizon is {years} year{years > 1 ? "s" : ""}; it does not assume the device is sold that long.</div>
            </div>
          </div>
        )}
      </div>
      <ErrorBox error={err} />
      {busy && <div role="status" className="card flex items-center gap-3 p-5 text-sm text-muted"><span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />Training or loading the model and computing the forecast. The first run for a device can take a few seconds.</div>}
      {!pred && !err && !busy && (
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_20rem]">
          <div className="card p-5">
            <h2 className="font-semibold">How a forecast is made</h2>
            <ol className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">{STEPS.map((s) => (
              <li key={s.title} className="flex gap-3"><span className="icon-tile shrink-0"><Icon name={s.icon} className="h-5 w-5" /></span>
                <div><div className="text-sm font-semibold">{s.title}</div><div className="text-sm text-muted">{s.text}</div></div></li>
            ))}</ol>
            <div className="mt-5"><Notice tone="info">Forecasts are estimates based on historical price patterns. They may differ from actual market prices. Devices with sample data are labelled <b>SAMPLE / DEMO DATA</b>.</Notice></div>
          </div>
          <img src="/images/art/forecast.svg" alt="" width={320} height={200} loading="lazy" className="hidden w-full self-start rounded-2xl border border-line shadow-soft lg:block" />
        </div>
      )}
      {pred && <ForecastResult p={pred} />}
    </>
  );
}
