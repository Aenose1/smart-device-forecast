import { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { Icon } from "./Icon";

export function Logo({ light }: { light?: boolean }) {
  return (
    <Link to="/" className="flex items-center gap-2.5 font-semibold" aria-label="Device Price Forecasting - home">
      <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-teal-500 text-white shadow-sm"><Icon name="ChartLine" className="h-5 w-5" /></span>
      <span className={`leading-tight ${light ? "text-white" : "text-ink"}`}>Device Price<span className="block text-xs font-medium text-muted">Forecasting</span></span>
    </Link>
  );
}

const linkCls = ({ isActive }: { isActive: boolean }) =>
  `rounded-lg px-3 py-2 text-sm font-medium transition ${isActive ? "bg-indigo-50 text-indigo-700" : "text-slate-600 hover:bg-slate-100 hover:text-ink"}`;

export default function SiteNav() {
  const loc = useLocation();
  const [open, setOpen] = useState(false);        // mobile menu
  useEffect(() => { setOpen(false); }, [loc.pathname]);
  useEffect(() => {
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("keydown", esc);
    return () => document.removeEventListener("keydown", esc);
  }, []);

  const links = (
    <>
      <NavLink to="/" end className={linkCls}>Home</NavLink>
      <NavLink to="/dashboard" className={linkCls}>Dashboard</NavLink>
      <NavLink to="/smartphones" className={linkCls}>Smartphones</NavLink>
      <NavLink to="/laptops" className={linkCls}>Laptops</NavLink>
      <NavLink to="/compare" className={linkCls}>Compare</NavLink>
      <NavLink to="/predict" className={linkCls}>Price Forecast</NavLink>
      <NavLink to="/about" className={linkCls}>About</NavLink>
    </>
  );

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-white/85 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-2.5 md:px-6">
        <Logo />
        <nav aria-label="Main" className="hidden items-center gap-1 lg:flex">{links}</nav>
        <div className="flex items-center gap-2">
          <Link className="btn hidden sm:inline-flex" to="/predictions"><Icon name="History" className="h-4 w-4" />My forecasts</Link>
          <Link className="btn !px-2.5" to="/admin" aria-label="Administration" title="Administration"><Icon name="Settings" className="h-4 w-4" /></Link>
          <button className="btn !px-2.5 lg:hidden" aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open} onClick={() => setOpen(!open)}>
            <Icon name={open ? "X" : "Menu"} className="h-5 w-5" />
          </button>
        </div>
      </div>
      {open && (
        <nav aria-label="Mobile" className="grid gap-1 border-t border-line bg-white px-4 py-3 lg:hidden">
          {links}
          <NavLink to="/predictions" className={linkCls}>My forecasts</NavLink>
          <NavLink to="/admin" className={linkCls}>Administration</NavLink>
        </nav>
      )}
    </header>
  );
}
