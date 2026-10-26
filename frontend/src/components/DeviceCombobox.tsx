import { useEffect, useRef, useState } from "react";
import { api, money, type Device } from "../api";
import { Icon } from "./Icon";

interface Props { onSelect: (d: Device) => void; selected?: Device | null; category?: string }

export default function DeviceCombobox({ onSelect, selected, category }: Props) {
  const [q, setQ] = useState(selected?.name ?? "");
  const [items, setItems] = useState<Device[]>([]);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const box = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const h = setTimeout(() => {
      setBusy(true);
      api.devices({ q, category, page_size: 100 }).then((r) => setItems(r.items)).catch(() => setItems([])).finally(() => setBusy(false));
    }, 200);
    return () => clearTimeout(h);
  }, [q, category]);
  useEffect(() => {
    const close = (e: MouseEvent) => !box.current?.contains(e.target as Node) && setOpen(false);
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  return (
    <div className="relative" ref={box}>
      <Icon name="Search" className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted" />
      <input className="input pl-9" role="combobox" aria-expanded={open} aria-controls="device-options" placeholder="Search by device name or brand"
        value={q} onChange={(e) => { setQ(e.target.value); setOpen(true); }} onFocus={() => setOpen(true)} />
      {open && (
        <ul id="device-options" role="listbox" className="absolute z-20 mt-1 max-h-72 w-full overflow-auto rounded-xl border border-line bg-white shadow-lift">
          {busy && <li className="px-3 py-2 text-sm text-muted">Searching…</li>}
          {!busy && items.length === 0 && <li className="px-3 py-2 text-sm text-muted">No devices match “{q}”. Ask an administrator to add it.</li>}
          {items.map((d) => (
            <li key={d.id} role="option" aria-selected={selected?.id === d.id}>
              <button type="button" className="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-sm hover:bg-paper"
                onClick={() => { onSelect(d); setQ(d.name); setOpen(false); }}>
                <span><span className="font-medium">{d.name}</span><span className="ml-2 text-muted">{d.brand} · {d.category}</span></span>
                <span className="text-muted">{money(d.latest_price, d.currency)}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
