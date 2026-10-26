import { Area, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { money } from "../api";

interface Props {
  history: [string, number][];
  path?: { date: string; predicted: number; lower: number; upper: number }[];
  currency: string;
  height?: number;
}

export default function PriceChart({ history, path, currency, height = 340 }: Props) {
  const t = (s: string) => new Date(s).getTime();
  const rows: Record<number, any> = {};
  history.forEach(([d, p]) => (rows[t(d)] = { t: t(d), hist: p }));
  if (path?.length && history.length) {
    const last = history[history.length - 1];
    rows[t(last[0])] = { ...rows[t(last[0])], fcst: last[1], band: [last[1], last[1]] };
    path.forEach((r) => (rows[t(r.date)] = { t: t(r.date), fcst: r.predicted, band: [r.lower, r.upper] }));
  }
  const data = Object.values(rows).sort((a, b) => a.t - b.t);
  const fmtT = (v: number) => new Date(v).toLocaleDateString("en-GB", { month: "short", year: "2-digit" });
  const compact = (v: number) => new Intl.NumberFormat("en-IN", { notation: "compact", maximumFractionDigits: 1 }).format(v);

  return (
    <div role="img" aria-label="Line chart of historical prices and estimated future prices" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
          <CartesianGrid stroke="#e3e8ea" vertical={false} />
          <XAxis dataKey="t" type="number" scale="time" domain={["dataMin", "dataMax"]} tickFormatter={fmtT} tick={{ fontSize: 12 }} minTickGap={40} />
          <YAxis tickFormatter={compact} tick={{ fontSize: 12 }} width={56} domain={["auto", "auto"]} />
          <Tooltip
            labelFormatter={(v) => new Date(Number(v)).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
            formatter={(v: any, name: string) => [Array.isArray(v) ? `${money(v[0], currency)} – ${money(v[1], currency)}` : money(Number(v), currency), name]}
          />
          <Legend verticalAlign="top" height={28} />
          {path && <Area dataKey="band" name="Approx. 95% range" stroke="none" fill="#d97706" fillOpacity={0.14} isAnimationActive={false} />}
          <Line dataKey="hist" name="Historical price" stroke="#0e7490" strokeWidth={2.2} dot={history.length < 40} connectNulls isAnimationActive={false} />
          {path && <Line dataKey="fcst" name="Estimated future price" stroke="#d97706" strokeWidth={2.2} strokeDasharray="6 4" dot={false} isAnimationActive={false} />}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
