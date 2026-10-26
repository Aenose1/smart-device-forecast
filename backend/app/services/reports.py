"""CSV and PDF exports for stored predictions."""
from __future__ import annotations

import csv
import io
from datetime import date
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

from ..models import Device, Prediction
from ..schemas import specs_to_dict
from .forecast_service import DISCLAIMER

CSV_COLUMNS = ["Device", "Category", "Current Price", "Forecast Date", "Forecast Year",
               "Predicted Price", "Percentage Change", "Trend"]


def _safe(text: str) -> str:
    """Neutralise spreadsheet formula injection in exported text cells."""
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


def csv_filename(p: Prediction) -> str:
    years = round(max(p.horizons) / 12) if p.horizons else 3
    return f"device_{years}_year_forecast.csv"


def prediction_csv(p: Prediction) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(CSV_COLUMNS)
    for r in p.results:
        w.writerow([_safe(p.device_name), p.category, f"{p.current_price:.2f}", r["forecast_date"], r["label"],
                    f"{r['predicted_price']:.2f}", f"{r['pct_change']:.2f}", r["trend"]])
    return buf.getvalue().encode("utf-8-sig")


def history_csv(device: Device, rows) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["device_id", "device_name", "category", "date", "price", "source", "currency"])
    for r in rows:
        w.writerow([r.device_id, _safe(device.name), device.category, r.date.isoformat(), f"{r.price:.2f}",
                    _safe(r.source), r.currency])
    return buf.getvalue().encode("utf-8")


def _money(v: float, cur: str) -> str:
    return f"{cur} {v:,.0f}"


def _chart(p: Prediction, forecast: bool) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(7.2, 3.1), dpi=150)
    hx = [date.fromisoformat(d) for d, _ in p.history]
    hy = [v for _, v in p.history]
    ax.plot(hx, hy, color="#1d4e89", lw=1.8, label="Historical price")
    if forecast and p.path:
        fx = [hx[-1]] + [date.fromisoformat(r["date"]) for r in p.path]
        fy = [hy[-1]] + [r["predicted"] for r in p.path]
        ax.plot(fx, fy, color="#c4572a", lw=1.8, ls="--", label="Estimated future price")
        ax.fill_between(fx[1:], [r["lower"] for r in p.path], [r["upper"] for r in p.path], color="#c4572a", alpha=0.15,
                        label="Approx. 95% range")
    ax.set_ylabel(p.currency)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, loc="best")
    ax.tick_params(labelsize=7)
    fig.autofmt_xdate()
    fig.tight_layout()
    out = io.BytesIO()
    fig.savefig(out, format="png")
    plt.close(fig)
    out.seek(0)
    return out


def prediction_pdf(p: Prediction, device: Device | None) -> bytes:
    ss = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9, leading=12)
    small = ParagraphStyle("s", parent=body, fontSize=8, textColor=colors.HexColor("#555555"))
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm,
                            bottomMargin=14 * mm, title=f"Price forecast - {p.device_name}", author="Smart Device Price Forecasting")
    P = lambda t, st=body: Paragraph(escape(str(t)), st)  # noqa: E731

    def table(data, widths=None, header=True):
        t = Table([[P(c) if not isinstance(c, Paragraph) else c for c in row] for row in data], colWidths=widths, repeatRows=1 if header else 0)
        style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c8ccd2")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                 ("FONTSIZE", (0, 0), (-1, -1), 9)]
        if header:
            style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8ecf1")))
        t.setStyle(TableStyle(style))
        return t

    cur, st, mi = p.currency, p.stats or {}, p.model_info or {}
    el = [P("Estimated Future Price Report", ss["Title"]), P(f"{p.device_name} ({p.brand})", ss["Heading3"])]
    el.append(P("PREDICTION / ESTIMATE ONLY. " + DISCLAIMER, ParagraphStyle("w", parent=body, textColor=colors.HexColor("#8a2d0b"))))
    if p.is_sample:
        el.append(P("This device's price history includes SAMPLE/DEMO data and is not real market data.",
                    ParagraphStyle("w2", parent=body, textColor=colors.HexColor("#8a2d0b"))))
    el.append(P("Device information", h2))
    info = [["Name", p.device_name], ["Brand", p.brand], ["Category", p.category]]
    if device:
        info += [["Release date", str(device.release_date or "n/a")], ["Launch price", _money(device.launch_price, cur)],
                 ["Status", device.status]]
    info += [["Latest known price", f"{_money(p.current_price, cur)} (as of {p.as_of})"]]
    el.append(table(info, [45 * mm, 125 * mm], header=False))
    specs = specs_to_dict(device) if device else {}
    if specs:
        el += [P("Specifications", h2), table([[k, v] for k, v in specs.items()], [45 * mm, 125 * mm], header=False)]
    if st:
        el.append(P("Historical price summary", h2))
        rows = [["Records", st["records"]], ["Period", f"{st['first_date']} to {st['last_date']}"],
                ["Minimum", f"{_money(st['min_price'], cur)} ({st['min_date']})"], ["Maximum", f"{_money(st['max_price'], cur)} ({st['max_date']})"],
                ["Average", _money(st["avg_price"], cur)], ["Change over period", f"{st['pct_change']}%"]]
        if st.get("highest_drop"):
            rows.append(["Highest drop", f"{_money(abs(st['highest_drop']['amount']), cur)} ({st['highest_drop']['pct']}%)"])
        if st.get("highest_increase"):
            rows.append(["Highest increase", f"{_money(st['highest_increase']['amount'], cur)} (+{st['highest_increase']['pct']}%)"])
        el.append(table(rows, [45 * mm, 125 * mm], header=False))
    el += [P("Historical price graph", h2), Image(_chart(p, False), width=170 * mm, height=73 * mm)]
    el.append(P("Estimated future prices", h2))
    data = [["Horizon", "Forecast date", "Estimated price", "Approx. 95% range", "Change", "Trend"]]
    for r in p.results:
        data.append([r["label"], r["forecast_date"], _money(r["predicted_price"], cur),
                     f"{_money(r['lower'], cur)} - {_money(r['upper'], cur)}", f"{r['pct_change']:+.1f}%", r["trend"]])
    el += [table(data, [22 * mm, 26 * mm, 32 * mm, 52 * mm, 16 * mm, 24 * mm]), Spacer(1, 4),
           Image(_chart(p, True), width=170 * mm, height=73 * mm)]
    m = mi.get("metrics", {})
    fmt = lambda v: "n/a" if v is None else f"{v:,.2f}"  # noqa: E731
    el.append(P("Model", h2))
    el.append(table([["Model used", mi.get("model_type", "n/a")], ["Trained", str(mi.get("trained_at", "n/a"))[:19]],
                     ["Dataset version", mi.get("dataset_version", "n/a")], ["Observations", mi.get("n_observations", "n/a")],
                     ["Validation", m.get("validation", "n/a")],
                     ["MAE / RMSE", f"{fmt(m.get('mae'))} / {fmt(m.get('rmse'))}"],
                     ["MAPE / R2", f"{fmt(m.get('mape'))}% / {fmt(m.get('r2'))}"],
                     ["Features", ", ".join(mi.get("feature_set", {}).get("model_features", []))]], [45 * mm, 125 * mm], header=False))
    el += [Spacer(1, 6), P(f"Prediction date: {p.created_at:%Y-%m-%d %H:%M} UTC", small), P(DISCLAIMER, small)]
    doc.build(el)
    return buf.getvalue()
