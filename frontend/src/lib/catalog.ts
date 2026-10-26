import type { Device } from "../api";

/** Parse the free-text spec strings the catalogue stores ("16 GB", "1 TB", "6.7 inch"). Returns null when absent. */
const num = (s?: string) => { const m = s?.replace(/,/g, "").match(/(\d+(?:\.\d+)?)/); return m ? parseFloat(m[1]) : null; };
export const ramGB = (d: Pick<Device, "specs">) => num(d.specs["RAM"]);
export const storageGB = (d: Pick<Device, "specs">) => {
  const v = num(d.specs["Storage"]);
  return v === null ? null : /tb/i.test(d.specs["Storage"]) ? v * 1000 : v;
};
export const laptopType = (d: Pick<Device, "specs">) => d.specs["Laptop type"] ?? null;
export const hasDedicatedGpu = (d: Pick<Device, "specs">) => {
  const g = d.specs["GPU"];
  return g ? !/integrated|shared|uhd|iris/i.test(g) : null;
};
export const releaseYear = (d: Pick<Device, "release_date">) => (d.release_date ? new Date(d.release_date).getFullYear() : null);

/** The few specifications shown on a card. */
export function keySpecs(d: Pick<Device, "category" | "specs">): { label: string; value: string }[] {
  const s = d.specs;
  const pick = (label: string, key: string, fmt?: (v: string) => string) => (s[key] ? [{ label, value: fmt ? fmt(s[key]) : s[key] }] : []);
  if (d.category === "Smartphone") {
    return [...pick("Chip", "Processor"), ...(s["RAM"] && s["Storage"] ? [{ label: "Memory", value: `${s["RAM"]} / ${s["Storage"]}` }] : []),
      ...pick("Display", "Display"), ...pick("Battery", "Battery")];
  }
  return [...pick("CPU", "Processor"), ...(s["RAM"] && s["Storage"] ? [{ label: "Memory", value: `${s["RAM"]} / ${s["Storage"]}` }] : []),
    ...pick("GPU", "GPU"), ...pick("Display", "Display", (v) => (s["Refresh rate"] ? `${v}, ${s["Refresh rate"]}` : v))];
}

// ------------------------------------------------------------------ artwork selection
const COLORWAYS = ["indigo", "teal", "rose", "amber"] as const;
const hash = (t: string) => { let h = 0; for (let i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) >>> 0; return h; };

export interface DeviceLike { id?: string; name: string; brand: string; category: string; launch_price?: number; specs?: Record<string, string> }

/** Same brand -> same colourway, so a brand looks consistent across the catalogue. */
export function artKey(d: DeviceLike): string {
  const cw = COLORWAYS[hash(d.brand.toLowerCase()) % COLORWAYS.length];
  if (d.category === "Smartphone") {
    const b = d.brand.toLowerCase();
    const shape = b === "apple" ? "flagship" : b === "google" ? "bar" : b === "nothing" ? "dual"
      : (d.launch_price ?? 0) >= 60000 ? "flagship" : hash(d.name) % 2 ? "round" : "dual";
    return `phone-${shape}-${cw}`;
  }
  const n = d.name.toLowerCase(), t = (d.specs?.["Laptop type"] ?? "").toLowerCase();
  let kind = "student";
  if (/predator|alienware|raider|stealth|aorus|rog strix/.test(n)) kind = "gaming-pro";
  else if (t === "gaming") kind = "gaming";
  else if (t === "business") kind = "business";
  else if (t === "general") kind = /swift|zenbook|macbook air|xps|surface|book4 pro|envy|aero|slim 5|pavilion aero/.test(n) ? "ultrabook" : "student";
  return `laptop-${kind}-${cw}`;
}

export const artSrc = (key: string) => `/images/fallback/${key}.svg`;

/** Primary image: an optional licensed product photo set by an admin as the spec "Image URL" (a local /images/... path
 *  or an https URL). Otherwise the bundled illustration. The illustration is also the fallback if the photo fails. */
export function deviceImage(d: DeviceLike): { src: string; fallback: string; alt: string } {
  const fallback = artSrc(artKey(d));
  const custom = d.specs?.["Image URL"]?.trim();
  const ok = custom && (/^\/images\/[\w./-]+$/.test(custom) || /^https:\/\/[^\s"'<>]+$/.test(custom));
  return { src: ok ? custom! : fallback, fallback, alt: `${d.brand} ${d.name.replace(new RegExp(`^${d.brand}\\s+`, "i"), "")} (${d.category.toLowerCase()} illustration)` };
}
