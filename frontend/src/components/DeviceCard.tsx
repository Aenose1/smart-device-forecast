import { Link } from "react-router-dom";
import { money, type Device } from "../api";
import { deviceImage, keySpecs, releaseYear } from "../lib/catalog";
import { Icon } from "./Icon";
import ProductImage from "./ProductImage";

export default function DeviceCard({ d }: { d: Device }) {
  const img = deviceImage(d);
  const specs = keySpecs(d).slice(0, 4);
  const year = releaseYear(d);
  const type = d.category === "Laptop" ? d.specs["Laptop type"] : null;
  return (
    <article className="card card-hover flex flex-col overflow-hidden">
      <Link to={`/devices/${d.id}`} className="block bg-slate-50" tabIndex={-1} aria-hidden="true">
        <ProductImage src={img.src} fallback={img.fallback} alt="" category={d.category} />
      </Link>
      <div className="flex flex-1 flex-col p-4">
        <div className="flex items-center justify-between gap-2 text-xs">
          <span className="font-semibold uppercase tracking-wide text-indigo-600">{d.brand}</span>
          <span className="text-muted">{[type, year].filter(Boolean).join(" · ")}</span>
        </div>
        <h3 className="mt-1 font-semibold leading-snug"><Link to={`/devices/${d.id}`} className="hover:text-indigo-700">{d.name}</Link></h3>
        <dl className="mt-3 space-y-1 text-xs">
          {specs.map((s) => (
            <div key={s.label} className="flex justify-between gap-3"><dt className="text-muted">{s.label}</dt><dd className="truncate text-right font-medium" title={s.value}>{s.value}</dd></div>
          ))}
        </dl>
        <div className="mt-auto pt-4">
          <div className="text-[11px] uppercase tracking-wide text-muted">Reference price</div>
          <div className="text-lg font-semibold">{money(d.latest_price, d.currency)}</div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            <Link to={`/devices/${d.id}`} className="btn !px-2 text-xs">Details</Link>
            <Link to={`/predict?device=${encodeURIComponent(d.id)}`} className="btn btn-primary !px-2 text-xs"><Icon name="Sparkles" className="h-3.5 w-3.5" />Forecast</Link>
          </div>
        </div>
      </div>
    </article>
  );
}
