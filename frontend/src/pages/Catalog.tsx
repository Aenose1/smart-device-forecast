import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, type Device } from "../api";
import DeviceCard from "../components/DeviceCard";
import { Icon } from "../components/Icon";
import { EmptyState, ErrorBox, Spinner } from "../components/ui";
import { hasDedicatedGpu, laptopType, ramGB, storageGB } from "../lib/catalog";

type Cat = "" | "Smartphone" | "Laptop";
const PAGE = 24;
const SORTS: Record<string, [string, (a: Device, b: Device) => number]> = {
  "price-asc": ["Price: low to high", (a, b) => a.latest_price - b.latest_price],
  "price-desc": ["Price: high to low", (a, b) => b.latest_price - a.latest_price],
  brand: ["Brand A-Z", (a, b) => a.brand.localeCompare(b.brand) || a.name.localeCompare(b.name)],
  model: ["Model A-Z", (a, b) => a.name.localeCompare(b.name)],
  newest: ["Newest release", (a, b) => (b.release_date ?? "").localeCompare(a.release_date ?? "")],
};

/** Loads the whole catalogue (100 per request, protected by the API's page cap) so filters and sorting are instant. */
async function loadAll(category: Cat): Promise<Device[]> {
  const out: Device[] = [];
  for (let page = 1; page <= 20; page++) {
    const r = await api.devices({ category: category || undefined, page, page_size: 100 });
    out.push(...r.items);
    if (out.length >= r.total || r.items.length === 0) break;
  }
  return out;
}

export default function Catalog({ category = "" }: { category?: Cat }) {
  const [sp, setSp] = useSearchParams();
  const [all, setAll] = useState<Device[] | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [shown, setShown] = useState(PAGE);
  const [filtersOpen, setFiltersOpen] = useState(false);

  const cat: Cat = category;
  const q = sp.get("q") ?? "";
  const brands = sp.getAll("brand");
  const sort = sp.get("sort") && SORTS[sp.get("sort")!] ? sp.get("sort")! : "price-desc";
  const minP = sp.get("min") ?? "", maxP = sp.get("max") ?? "", ram = sp.get("ram") ?? "", sto = sp.get("storage") ?? "";
  const type = sp.get("type") ?? "", gpu = sp.get("gpu") ?? "";

  useEffect(() => {
    let live = true;
    setAll(null); setError(null);
    loadAll(cat).then((d) => live && setAll(d)).catch((e) => live && setError(e));
    return () => { live = false; };
  }, [cat]);
  useEffect(() => setShown(PAGE), [sp, cat]);

  const set = (k: string, v: string | null) => { const n = new URLSearchParams(sp); if (v) n.set(k, v); else n.delete(k); setSp(n, { replace: true }); };
  const toggleBrand = (b: string) => {
    const n = new URLSearchParams(sp); const cur = n.getAll("brand"); n.delete("brand");
    (cur.includes(b) ? cur.filter((x) => x !== b) : [...cur, b]).forEach((x) => n.append("brand", x)); setSp(n, { replace: true });
  };

  const brandCounts = useMemo(() => {
    const m = new Map<string, number>(); (all ?? []).forEach((d) => m.set(d.brand, (m.get(d.brand) ?? 0) + 1));
    return [...m.entries()].sort((a, b) => a[0].localeCompare(b[0], undefined, { sensitivity: "base" }));
  }, [all]);

  const list = useMemo(() => {
    const t = q.trim().toLowerCase();
    const lo = minP ? Number(minP) : null, hi = maxP ? Number(maxP) : null;
    return (all ?? []).filter((d) => {
      if (t && !`${d.brand} ${d.name} ${d.id}`.toLowerCase().includes(t)) return false;
      if (brands.length && !brands.some((b) => b.toLowerCase() === d.brand.toLowerCase())) return false;
      if (lo !== null && d.latest_price < lo) return false;
      if (hi !== null && d.latest_price > hi) return false;
      if (ram && (ramGB(d) ?? 0) < Number(ram)) return false;
      if (sto && (storageGB(d) ?? 0) < Number(sto)) return false;
      if (type && laptopType(d) !== type) return false;
      if (gpu === "dedicated" && hasDedicatedGpu(d) !== true) return false;
      if (gpu === "integrated" && hasDedicatedGpu(d) !== false) return false;
      return true;
    }).sort(SORTS[sort][1]);
  }, [all, q, brands.join("|"), minP, maxP, ram, sto, type, gpu, sort]);

  const title = cat === "Smartphone" ? "Smartphones" : cat === "Laptop" ? "Laptops" : "All devices";
  const active = [q, minP, maxP, ram, sto, type, gpu].filter(Boolean).length + brands.length;
  const clear = () => setSp(new URLSearchParams(sort !== "price-desc" ? { sort } : {}), { replace: true });

  const filters = (
    <div className="space-y-5 text-sm">
      <div><label className="label" htmlFor="cq">Search model or brand</label>
        <div className="relative"><Icon name="Search" className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted" />
          <input id="cq" className="input pl-9" value={q} onChange={(e) => set("q", e.target.value)} placeholder={cat === "Laptop" ? "e.g. Nitro, ThinkPad" : cat === "Smartphone" ? "e.g. Redmi Note, Pixel" : "e.g. Acer, iPhone"} /></div></div>
      <fieldset><legend className="label">Brand</legend>
        <div className="max-h-56 space-y-1 overflow-auto pr-1">
          {brandCounts.map(([b, n]) => (
            <label key={b} className="flex cursor-pointer items-center justify-between gap-2 rounded-lg px-2 py-1 hover:bg-slate-50">
              <span className="flex items-center gap-2"><input type="checkbox" className="h-4 w-4 accent-indigo-600" checked={brands.some((x) => x.toLowerCase() === b.toLowerCase())} onChange={() => toggleBrand(b)} />{b}</span>
              <span className="text-xs text-muted">{n}</span>
            </label>
          ))}
          {all && brandCounts.length === 0 && <p className="text-muted">No brands yet.</p>}
        </div></fieldset>
      <fieldset><legend className="label">Price range (₹)</legend>
        <div className="grid grid-cols-2 gap-2">
          <input aria-label="Minimum price" className="input" type="number" min={0} placeholder="Min" value={minP} onChange={(e) => set("min", e.target.value)} />
          <input aria-label="Maximum price" className="input" type="number" min={0} placeholder="Max" value={maxP} onChange={(e) => set("max", e.target.value)} />
        </div></fieldset>
      <div className="grid grid-cols-2 gap-2">
        <div><label className="label" htmlFor="cram">RAM</label>
          <select id="cram" className="input" value={ram} onChange={(e) => set("ram", e.target.value)}><option value="">Any</option>{[4, 8, 12, 16, 32].map((v) => <option key={v} value={v}>{v} GB+</option>)}</select></div>
        <div><label className="label" htmlFor="csto">Storage</label>
          <select id="csto" className="input" value={sto} onChange={(e) => set("storage", e.target.value)}><option value="">Any</option>{[128, 256, 512, 1000, 2000].map((v) => <option key={v} value={v}>{v >= 1000 ? `${v / 1000} TB+` : `${v} GB+`}</option>)}</select></div>
      </div>
      {cat === "Laptop" && (
        <div className="grid grid-cols-2 gap-2">
          <div><label className="label" htmlFor="ctype">Laptop type</label>
            <select id="ctype" className="input" value={type} onChange={(e) => set("type", e.target.value)}><option value="">All</option>{["Gaming", "Student", "Business", "General"].map((v) => <option key={v}>{v}</option>)}</select></div>
          <div><label className="label" htmlFor="cgpu">Graphics</label>
            <select id="cgpu" className="input" value={gpu} onChange={(e) => set("gpu", e.target.value)}><option value="">Any</option><option value="dedicated">Dedicated GPU</option><option value="integrated">Integrated</option></select></div>
        </div>
      )}
      {active > 0 && <button className="btn w-full" onClick={clear}>Clear all filters</button>}
    </div>
  );

  return (
    <>
      <div className="card hero-gradient relative mb-6 overflow-hidden border-0 p-6 text-white md:p-8">
        <div className="bg-tech-circuit absolute inset-0 opacity-30" aria-hidden="true" />
        <div className="relative flex flex-wrap items-center justify-between gap-4">
          <div><h1 className="text-2xl font-semibold tracking-tight md:text-3xl">{title}</h1>
            <p className="mt-1 max-w-xl text-sm text-slate-300">
              {cat === "Laptop" ? "Gaming, student, business and general-purpose laptops." : cat === "Smartphone" ? "Popular phones from OnePlus, Redmi, Samsung, Apple and more." : "Smartphones and laptops in one catalogue."} Open a device for its price history and forecast.
            </p></div>
          <img src={cat === "Laptop" ? "/images/fallback/laptop-gaming-pro-indigo.svg" : "/images/fallback/phone-flagship-teal.svg"} alt="" width={200} height={150} className="hidden h-24 w-32 rounded-xl object-cover md:block" />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[17rem_1fr]">
        <aside>
          <button className="btn mb-3 w-full lg:hidden" aria-expanded={filtersOpen} onClick={() => setFiltersOpen(!filtersOpen)}>
            <Icon name="SlidersHorizontal" className="h-4 w-4" />Filters{active ? ` (${active})` : ""}
          </button>
          <div className={`card p-4 ${filtersOpen ? "" : "hidden"} lg:sticky lg:top-20 lg:block`}>{filters}</div>
        </aside>

        <section aria-live="polite">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-muted">{all ? <><b className="text-ink">{list.length}</b> of {all.length} devices</> : "Loading catalogue…"}</p>
            <div className="flex items-center gap-2"><label htmlFor="sort" className="text-sm text-muted"><Icon name="ArrowUpDown" className="mr-1 inline h-4 w-4" />Sort</label>
              <select id="sort" className="input !w-auto" value={sort} onChange={(e) => set("sort", e.target.value)}>
                {Object.entries(SORTS).map(([k, [label]]) => <option key={k} value={k}>{label}</option>)}</select></div>
          </div>
          <ErrorBox error={error} />
          {!all && !error && <Spinner label="Loading devices…" />}
          {all && list.length === 0 && (
            <EmptyState icon="Search" title="No devices match these filters" image="/images/art/devices.svg"
              action={active > 0 ? <button className="btn" onClick={clear}>Clear filters</button> : undefined}>
              {all.length === 0 ? "The catalogue is empty. An administrator can add devices or load the sample catalogue." : "Try removing a filter or searching a different model or brand."}
            </EmptyState>
          )}
          {list.length > 0 && (
            <>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">{list.slice(0, shown).map((d) => <DeviceCard key={d.id} d={d} />)}</div>
              {shown < list.length && <div className="mt-6 text-center"><button className="btn" onClick={() => setShown(shown + PAGE)}>Show more ({list.length - shown} left)</button></div>}
              <p className="mt-6 text-xs text-muted">Specifications and reference prices are approximate. Price histories shipped with the project are synthetic demonstration data.</p>
            </>
          )}
        </section>
      </div>
    </>
  );
}
