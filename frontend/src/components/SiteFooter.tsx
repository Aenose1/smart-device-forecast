import { Link } from "react-router-dom";
import { Logo } from "./SiteNav";

export default function SiteFooter() {
  return (
    <footer className="mt-16 bg-navy text-slate-300">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 md:grid-cols-4 md:px-6">
        <div className="md:col-span-2">
          <Logo light />
          <p className="mt-3 max-w-md text-sm text-slate-400">
            Browse smartphones and laptops, see their recorded price history, and get an estimated price one to five years ahead,
            with the uncertainty shown.
          </p>
        </div>
        <div>
          <h2 className="text-sm font-semibold text-white">Explore</h2>
          <ul className="mt-3 space-y-2 text-sm">
            <li><Link className="hover:text-white" to="/smartphones">Smartphones</Link></li>
            <li><Link className="hover:text-white" to="/laptops">Laptops</Link></li>
            <li><Link className="hover:text-white" to="/compare">Compare devices</Link></li>
            <li><Link className="hover:text-white" to="/predict">Price forecast</Link></li>
            <li><Link className="hover:text-white" to="/about">About</Link></li>
          </ul>
        </div>
        <div>
          <h2 className="text-sm font-semibold text-white">Data &amp; method</h2>
          <p className="mt-3 text-sm text-slate-400">
            Specifications and launch prices are approximate reference values. Price histories shipped with the project are
            <b className="font-medium text-slate-200"> synthetic demonstration data</b>; load real prices from the Admin area.
          </p>
        </div>
      </div>
      <div className="border-t border-white/10">
        <p className="mx-auto max-w-7xl px-4 py-4 text-xs text-slate-400 md:px-6">
          Forecasts are estimates based on historical price patterns. They are not guaranteed prices and may differ from actual market prices.
          Brand and product names belong to their respective owners; no affiliation or endorsement is implied. Device images are original illustrations, not product photographs.
        </p>
      </div>
    </footer>
  );
}
