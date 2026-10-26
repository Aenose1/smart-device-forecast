import { Link } from "react-router-dom";
import { Icon, type IconName } from "../components/Icon";

const POINTS: { icon: IconName; title: string; text: string }[] = [
  { icon: "Layers", title: "Separate models per category", text: "Smartphones and laptops depreciate differently, so each category has its own pipeline and features (RAM, storage, display, battery, camera or GPU). Data is never mixed between categories." },
  { icon: "Brain", title: "Chosen on held-out data", text: "Several candidate models (naive, linear, log-linear, tree-based, damped exponential smoothing and a pooled gradient-boosting model) compete on the most recent prices, which are kept out of training. The best one is used and its error is reported." },
  { icon: "ChartLine", title: "Uncertainty is shown", text: "Every estimate comes with an approximate 95% range that widens with the horizon, plus MAE, RMSE, MAPE and R² for the chosen model." },
  { icon: "ShieldCheck", title: "Honest about data", text: "A device needs at least 8 distinct price dates over 90 days to be forecast. Demo price histories are synthetic and are labelled SAMPLE / DEMO DATA everywhere, including reports." },
];

export default function About() {
  return (
    <>
      <section className="hero-gradient relative overflow-hidden text-white">
        <div className="bg-tech-circuit absolute inset-0 opacity-40" aria-hidden="true" />
        <div className="relative mx-auto grid max-w-7xl items-center gap-8 px-4 py-14 md:px-6 lg:grid-cols-[1.2fr_1fr]">
          <div>
            <p className="eyebrow !text-teal-300">About</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight md:text-5xl">Smart Device Price Prediction &amp; 3-Year Forecasting</h1>
            <p className="mt-4 max-w-2xl text-slate-300">
              A web application that shows the price history of smartphones and laptops and produces estimated future prices from one to five years ahead (three by default),
              using machine-learning models trained on the recorded prices.
            </p>
            <div className="mt-6 flex flex-wrap gap-3"><Link to="/predict" className="btn btn-primary">Try a forecast</Link><Link to="/smartphones" className="btn btn-ghost-light">Browse devices</Link></div>
          </div>
          <img src="/images/art/data.svg" alt="" width={320} height={200} className="mx-auto hidden w-full max-w-sm rounded-2xl lg:block" />
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-4 py-12 md:px-6">
        <p className="eyebrow">How it works</p>
        <h2 className="section-title mt-1">Forecasting you can inspect</h2>
        <div className="mt-8 grid grid-cols-1 gap-5 md:grid-cols-2">
          {POINTS.map((p) => (
            <div key={p.title} className="card card-hover flex gap-4 p-5"><span className="icon-tile shrink-0"><Icon name={p.icon} className="h-5 w-5" /></span>
              <div><h3 className="font-semibold">{p.title}</h3><p className="mt-1 text-sm text-muted">{p.text}</p></div></div>
          ))}
        </div>

        <div className="mt-12 grid grid-cols-1 gap-5 lg:grid-cols-3">
          <div className="card p-5 lg:col-span-2">
            <h2 className="flex items-center gap-2 text-lg font-semibold"><Icon name="Database" className="h-5 w-5 text-indigo-600" />Data sources and limitations</h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-muted">
              <li>Device names, specifications and launch prices are approximate reference values compiled from public launch information (INR). The exact variant or the current street price may differ.</li>
              <li>The price history included with the project is <b className="text-ink">synthetic demonstration data</b>. It is not market data. Administrators can replace it by uploading real price CSVs.</li>
              <li>Forecasts reflect past price patterns only. New launches, tax changes, promotions or supply shocks are not predicted.</li>
              <li>Forecasts are estimates, not guaranteed prices, and may differ from actual market prices.</li>
            </ul>
          </div>
          <div className="card p-5">
            <h2 className="flex items-center gap-2 text-lg font-semibold"><Icon name="Cpu" className="h-5 w-5 text-indigo-600" />Built with</h2>
            <ul className="mt-3 space-y-1.5 text-sm text-muted">
              <li>React, TypeScript, Tailwind CSS, Recharts</li><li>FastAPI, SQLAlchemy (SQLite or PostgreSQL)</li><li>scikit-learn, statsmodels, pandas</li><li>No sign-in: forecast history is kept per browser; administration is protected by a server-side key</li>
            </ul>
            <img src="/images/art/ai.svg" alt="" width={320} height={200} loading="lazy" className="mt-4 w-full rounded-xl" />
          </div>
        </div>
        <p className="mt-8 text-xs text-muted">Brand and product names belong to their respective owners; they are used only to identify devices. Device images are original illustrations, not product photographs. Icons: Lucide (ISC licence).</p>
      </div>
    </>
  );
}
