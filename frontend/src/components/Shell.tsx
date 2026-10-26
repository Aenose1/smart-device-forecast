import { Outlet } from "react-router-dom";
import SiteFooter from "./SiteFooter";
import SiteNav from "./SiteNav";

/** Navigation bar + page + footer. */
export default function Shell({ wide }: { wide?: boolean }) {
  return (
    <div className="flex min-h-screen flex-col">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded-lg focus:bg-white focus:px-3 focus:py-2">Skip to content</a>
      <SiteNav />
      <main id="main" className={wide ? "flex-1" : "mx-auto w-full max-w-7xl flex-1 px-4 py-6 md:px-6 md:py-8"}><Outlet /></main>
      <SiteFooter />
    </div>
  );
}
