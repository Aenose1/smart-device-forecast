import { Link } from "react-router-dom";
import { api, type PublicOverview } from "../api";
import DeviceCard from "../components/DeviceCard";
import { Icon, type IconName } from "../components/Icon";
import { useAsync } from "../components/ui";
import { artSrc } from "../lib/catalog";

const PHONE_BRANDS = ["OnePlus", "Redmi", "Xiaomi", "Samsung", "Apple", "vivo", "OPPO", "realme", "Google", "Motorola", "POCO", "Nothing"];
const LAPTOP_BRANDS = ["Acer", "ASUS", "Lenovo", "HP", "Dell", "MSI", "Apple", "Samsung", "Microsoft", "Gigabyte"];

const FEATURES: { icon: IconName; title: string; text: string; art: string; to: string }[] = [
  { icon: "Brain", title: "AI Price Prediction", text: "Several models compete on held-out recent prices; the best one is used and its error is shown.", art: "ai", to: "/predict" },
  { icon: "ChartLine", title: "3-Year Forecasting", text: "Estimated price after 1, 2 and 3 years (up to 5) with an approximate 95% range.", art: "forecast", to: "/predict" },
  { icon: "ChartColumn", title: "Price Trends", text: "Recorded price history, highest drops and increases, and category-wide movers.", art: "trends", to: "/dashboard" },
  { icon: "GitCompare", title: "Smart Device Comparison", text: "Put two or three devices side by side: specifications and price history on one chart.", art: "compare", to: "/compare" },
];

function BrandChips({ title, icon, brands, to }: { title: string; icon: IconName; brands: string[]; to: string }) {
  return (
    <div className="card p-5">
      <h3 className="flex items-center gap-2 font-semibold"><span className="icon-tile !h-8 !w-8"><Icon name={icon} className="h-4 w-4" /></span>{title}</h3>
      <ul className="mt-4 flex flex-wrap gap-2">
        {brands.map((b) => (
          <li key={b}><Link className="chip transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700" to={`${to}?brand=${encodeURIComponent(b)}`}>{b}</Link></li>
        ))}
      </ul>
    </div>
  );
}

export default function Landing() {
  const ov = useAsync<PublicOverview | null>(() => api.publicOverview().catch(() => null), []);
  const o = ov.data;
  const phones = o?.brands.Smartphone?.map((b) => b.brand) ?? PHONE_BRANDS;
  const laptops = o?.brands.Laptop?.map((b) => b.brand) ?? LAPTOP_BRANDS;
  const count = (c: string) => o?.brands[c]?.reduce((n, b) => n + b.devices, 0);

  return (
    <>
      {/* ---------------------------------------------------------------- hero */}
      <section className="hero-gradient relative overflow-hidden text-white">
        <div className="bg-tech-circuit absolute inset-0 opacity-40" aria-hidden="true" />
        <div className="relative mx-auto grid max-w-7xl items-center gap-10 px-4 py-14 md:px-6 lg:grid-cols-2 lg:py-20">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-medium text-indigo-100">
              <Icon name="Sparkles" className="h-3.5 w-3.5" />Smartphones &amp; laptops · INR
            </span>
            <h1 className="mt-5 text-4xl font-semibold leading-[1.1] tracking-tight md:text-5xl lg:text-6xl">Predict the Future of Device Prices</h1>
            <p className="mt-5 max-w-xl text-lg text-slate-300">
              See how a smartphone or laptop has been priced so far, then get an estimated price one, two and three years ahead, with the uncertainty shown.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link className="btn btn-primary !px-5 !py-3 text-base" to="/predict"><Icon name="Sparkles" className="h-4 w-4" />Forecast a Device</Link>
              <Link className="btn btn-ghost-light !px-5 !py-3 text-base" to="/smartphones">Explore Devices<Icon name="ArrowRight" className="h-4 w-4" /></Link>
            </div>
            <ul className="mt-8 flex flex-wrap gap-2 text-sm">
              {([["Brain", "AI forecasting"], ["History", "Historical prices"], ["TrendingUp", "3-year predictions"]] as [IconName, string][]).map(([i, t]) => (
                <li key={t} className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-slate-100 backdrop-blur"><Icon name={i} className="h-4 w-4 text-teal-300" />{t}</li>
              ))}
            </ul>
          </div>
          <div className="relative mx-auto w-full max-w-xl">
            <img src="/images/art/hero-devices.svg" alt="A laptop and a smartphone showing abstract price trend lines" width={640} height={480} className="floaty relative w-full drop-shadow-2xl" />
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------------- categories */}
      <section className="mx-auto max-w-7xl px-4 py-14 md:px-6">
        <p className="eyebrow">Browse by category</p>
        <h2 className="section-title mt-1">Smartphones and laptops from popular brands</h2>
        <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-2">
          {([
            ["Smartphones", "/smartphones", "phone-flagship-indigo", "Flagships to everyday phones: price history, specifications and forecasts.", count("Smartphone")],
            ["Laptops", "/laptops", "laptop-gaming-teal", "Gaming, student, business and general-purpose laptops side by side.", count("Laptop")],
          ] as [string, string, string, string, number | undefined][]).map(([t, to, art, text, n]) => (
            <Link key={t} to={to} className="card card-hover group grid grid-cols-5 items-center overflow-hidden">
              <div className="col-span-3 p-6">
                <h3 className="text-xl font-semibold">{t}</h3>
                <p className="mt-2 text-sm text-muted">{text}</p>
                <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-indigo-600">{n ? `${n} devices` : "Browse"}<Icon name="ArrowRight" className="h-4 w-4 transition group-hover:translate-x-1" /></span>
              </div>
              <img src={artSrc(art)} alt="" width={400} height={300} loading="lazy" className="col-span-2 h-full w-full object-cover" />
            </Link>
          ))}
        </div>
        <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2">
          <BrandChips title="Featured smartphone brands" icon="Smartphone" brands={phones} to="/smartphones" />
          <BrandChips title="Featured laptop brands" icon="Laptop" brands={laptops} to="/laptops" />
        </div>
      </section>

      {/* ---------------------------------------------------------------- popular devices (live catalogue; hidden if unavailable) */}
      {o && o.featured.length > 0 && (
        <section className="border-y border-line bg-white">
          <div className="mx-auto max-w-7xl px-4 py-14 md:px-6">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div><p className="eyebrow">Popular devices</p><h2 className="section-title mt-1">From the catalogue</h2></div>
              <Link to="/smartphones" className="btn">View all devices<Icon name="ArrowRight" className="h-4 w-4" /></Link>
            </div>
            <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">{o.featured.map((d) => <DeviceCard key={d.id} d={d} />)}</div>
            <p className="mt-4 text-xs text-muted">Reference prices are the latest price on record. Price histories included with this project are synthetic demonstration data.</p>
          </div>
        </section>
      )}

      {/* ---------------------------------------------------------------- features */}
      <section className="bg-tech-grid">
        <div className="mx-auto max-w-7xl px-4 py-14 md:px-6">
          <p className="eyebrow">What you can do</p>
          <h2 className="section-title mt-1">Price prediction features</h2>
          <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f) => (
              <Link key={f.title} to={f.to} className="card card-hover flex flex-col overflow-hidden">
                <img src={`/images/art/${f.art}.svg`} alt="" width={320} height={200} loading="lazy" className="w-full" />
                <div className="flex flex-1 flex-col p-5">
                  <span className="icon-tile"><Icon name={f.icon} className="h-5 w-5" /></span>
                  <h3 className="mt-3 font-semibold">{f.title}</h3>
                  <p className="mt-1.5 text-sm text-muted">{f.text}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------------- previews */}
      <section className="mx-auto max-w-7xl px-4 pb-6 md:px-6">
        <p className="eyebrow">Preview</p>
        <h2 className="section-title mt-1">From past prices to a three-year estimate</h2>
        <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">
          <div className="card p-5">
            <h3 className="flex items-center gap-2 font-semibold"><Icon name="History" className="h-4 w-4 text-teal-700" />Historical price chart</h3>
            <img src="/images/art/analytics.svg" alt="Illustration of a historical price line chart" width={320} height={200} loading="lazy" className="mt-3 w-full rounded-xl" />
            <p className="mt-3 text-sm text-muted">Every device shows its recorded prices over time, with minimum, maximum, average and the biggest drop and increase.</p>
          </div>
          <div className="card p-5">
            <h3 className="flex items-center gap-2 font-semibold"><Icon name="TrendingUp" className="h-4 w-4 text-amber-600" />Three-year forecast</h3>
            <img src="/images/art/forecast.svg" alt="Illustration: a solid line of recorded prices continuing as a dashed estimate with a widening range" width={320} height={200} loading="lazy" className="mt-3 w-full rounded-xl" />
            <p className="mt-3 text-sm text-muted">Solid line: recorded prices. Dashed line and shaded band: the estimate and its approximate 95% range, which widens over time.</p>
          </div>
        </div>
        <p className="mt-3 text-xs text-muted">Both previews are illustrations of the layout, not real data. Real charts appear in the app.</p>
      </section>

      {/* ---------------------------------------------------------------- CTA */}
      <section className="mx-auto max-w-7xl px-4 pt-10 md:px-6">
        <div className="hero-gradient relative overflow-hidden rounded-3xl px-6 py-10 text-white md:px-12">
          <div className="bg-tech-grid absolute inset-0 opacity-30" aria-hidden="true" />
          <div className="relative flex flex-wrap items-center justify-between gap-6">
            <div className="max-w-xl">
              <h2 className="text-2xl font-semibold md:text-3xl">Ready to see what your next device could cost?</h2>
              <p className="mt-2 text-slate-300">Pick a smartphone or laptop and generate a forecast in a few seconds.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link className="btn btn-primary !px-5 !py-3" to="/predict">New forecast</Link>
              <Link className="btn btn-ghost-light !px-5 !py-3" to="/about">How it works</Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
