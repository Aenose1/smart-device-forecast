"""Generates the ORIGINAL vector artwork in frontend/public/images (stdlib only, no network).

Everything here is drawn from scratch for this project: generic phone / laptop silhouettes in several styles and
colourways, plus hero / feature / background illustrations. They are NOT photographs of real products and carry no
manufacturer logos. Screens show abstract lines only (never numbers), so nothing can be mistaken for real data.

Run:  python -m scripts.generate_images
Real product photos: drop licensed files into frontend/public/images/devices/ and add the spec
`Image URL=/images/devices/<file>` to the device (see README).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "frontend" / "public" / "images"

COLORWAYS = {  # name: (dark, light, glow)
    "indigo": ("#312e81", "#6366f1", "#a5b4fc"),
    "teal": ("#0f4c5c", "#14a3a8", "#7ee0dc"),
    "rose": ("#7f1d3a", "#e0527a", "#fbb6c8"),
    "amber": ("#7a3b0b", "#e08a1e", "#fcd38a"),
}
PHONE_SHAPES = ("flagship", "round", "dual", "bar")
LAPTOP_TYPES = ("gaming", "gaming-pro", "ultrabook", "business", "student")


def write(rel: str, svg: str) -> None:
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(svg.strip() + "\n", encoding="utf-8")


def defs(uid: str, dark: str, light: str, glow: str) -> str:
    return f"""<defs>
<linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f4f7fd"/><stop offset="1" stop-color="#e3eaf6"/></linearGradient>
<linearGradient id="scr{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{dark}"/><stop offset="1" stop-color="{light}"/></linearGradient>
<linearGradient id="body{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2b3445"/><stop offset="1" stop-color="#0f1523"/></linearGradient>
<linearGradient id="metal{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e8edf5"/><stop offset="1" stop-color="#b9c3d4"/></linearGradient>
<radialGradient id="glow{uid}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{glow}" stop-opacity=".55"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>
<filter id="sh{uid}" x="-20%" y="-10%" width="140%" height="140%"><feDropShadow dx="0" dy="10" stdDeviation="9" flood-color="#0f1b2d" flood-opacity=".28"/></filter>
</defs>"""


def screen_art(x, y, w, h, uid, glow, rx=6):
    """Abstract wallpaper + a trend line (no numbers)."""
    px = lambda f: x + w * f
    py = lambda f: y + h * f
    pts = " ".join(f"{px(a):.1f},{py(b):.1f}" for a, b in
                   [(.08, .74), (.22, .64), (.36, .70), (.5, .50), (.64, .56), (.78, .34), (.92, .26)])
    return f"""<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#scr{uid})"/>
<ellipse cx="{px(.78):.1f}" cy="{py(.22):.1f}" rx="{w*.38:.1f}" ry="{h*.3:.1f}" fill="url(#glow{uid})"/>
<polyline points="{pts}" fill="none" stroke="#fff" stroke-opacity=".9" stroke-width="{max(2, w*.018):.1f}" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="{px(.08):.1f}" y="{py(.1):.1f}" width="{w*.3:.1f}" height="{max(3, h*.03):.1f}" rx="2" fill="#fff" fill-opacity=".55"/>
<rect x="{px(.08):.1f}" y="{py(.16):.1f}" width="{w*.18:.1f}" height="{max(3, h*.025):.1f}" rx="2" fill="#fff" fill-opacity=".3"/>"""


def phone_body(shape, uid, c, ox=0, oy=0, scale=1.0, back=False):
    dark, light, glow = c
    w, h = 150 * scale, 300 * scale
    x, y = ox, oy
    g = f'<g filter="url(#sh{uid})">'
    g += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{26*scale}" fill="url(#body{uid})"/>'
    g += f'<rect x="{x+2.5*scale}" y="{y+2.5*scale}" width="{w-5*scale}" height="{h-5*scale}" rx="{23.5*scale}" fill="none" stroke="#fff" stroke-opacity=".12"/>'
    g += f'<rect x="{x+3*scale}" y="{y+78*scale}" width="{3*scale}" height="{36*scale}" rx="1.5" fill="#566179"/>'  # side key
    if not back:
        g += screen_art(x + 8 * scale, y + 8 * scale, w - 16 * scale, h - 16 * scale, uid, glow, rx=19 * scale)
        g += f'<circle cx="{x+w/2}" cy="{y+20*scale}" r="{4.2*scale}" fill="#0b1020"/>'
    return g + "</g>"


def phone_svg(shape: str, cw: str) -> str:
    c = COLORWAYS[cw]
    uid = f"p{shape}{cw}"
    dark, light, glow = c
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img" aria-label="Smartphone illustration">{defs(uid, *c)}'
    s += f'<rect width="400" height="300" fill="url(#bg{uid})"/>'
    s += f'<circle cx="200" cy="150" r="118" fill="url(#glow{uid})"/>'
    # back phone (shows the camera layout), then the front phone slightly overlapping
    bx, by, w, h = 92, 22, 118, 262
    s += f'<g transform="rotate(-8 {bx+w/2} {by+h/2})" filter="url(#sh{uid})">'
    s += f'<rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="22" fill="url(#scr{uid})"/>'
    s += f'<rect x="{bx}" y="{by}" width="{w}" height="{h}" rx="22" fill="#fff" fill-opacity=".08"/>'
    cam = {
        "flagship": f'<rect x="{bx+12}" y="{by+12}" width="62" height="62" rx="16" fill="#0b1020" fill-opacity=".88"/>'
                    + "".join(f'<circle cx="{bx+cx}" cy="{by+cy}" r="11" fill="#1d263b" stroke="#8793ad" stroke-width="2"/><circle cx="{bx+cx}" cy="{by+cy}" r="4.5" fill="#3b4a6b"/>' for cx, cy in ((31, 31), (55, 31), (43, 55))),
        "round": f'<circle cx="{bx+w/2}" cy="{by+44}" r="30" fill="#0b1020" fill-opacity=".88"/>'
                 + "".join(f'<circle cx="{bx+w/2+dx}" cy="{by+44+dy}" r="9" fill="#1d263b" stroke="#8793ad" stroke-width="2"/>' for dx, dy in ((-11, -9), (11, -9), (0, 12))),
        "dual": f'<rect x="{bx+14}" y="{by+14}" width="30" height="62" rx="15" fill="#0b1020" fill-opacity=".88"/>'
                + "".join(f'<circle cx="{bx+29}" cy="{by+cy}" r="9" fill="#1d263b" stroke="#8793ad" stroke-width="2"/>' for cy in (30, 59)),
        "bar": f'<rect x="{bx}" y="{by+34}" width="{w}" height="30" fill="#0b1020" fill-opacity=".88"/>'
               + "".join(f'<circle cx="{bx+cx}" cy="{by+49}" r="9" fill="#1d263b" stroke="#8793ad" stroke-width="2"/>' for cx in (30, 59)),
    }[shape]
    s += cam + "</g>"
    s += phone_body(shape, uid, c, ox=190, oy=24, scale=0.92)
    s += "</svg>"
    return s


def laptop_svg(kind: str, cw: str) -> str:
    c = COLORWAYS[cw]
    uid = f"l{kind.replace('-', '')}{cw}"
    dark, light, glow = c
    gaming = kind.startswith("gaming")
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img" aria-label="Laptop illustration">{defs(uid, *c)}'
    s += f'<rect width="400" height="300" fill="url(#bg{uid})"/><ellipse cx="200" cy="150" rx="150" ry="104" fill="url(#glow{uid})"/>'
    sw, sh = {"gaming": (252, 158), "gaming-pro": (262, 162), "ultrabook": (240, 158), "business": (240, 152), "student": (240, 150)}[kind]
    x = 200 - sw / 2
    y = 56 if kind != "gaming-pro" else 52
    lid = "url(#body%s)" % uid if gaming or kind == "business" else "url(#metal%s)" % uid
    bez = "#0b1020"
    s += '<g filter="url(#sh%s)">' % uid
    s += f'<rect x="{x-6}" y="{y-6}" width="{sw+12}" height="{sh+12}" rx="12" fill="{lid}"/>'
    s += f'<rect x="{x}" y="{y}" width="{sw}" height="{sh}" rx="6" fill="{bez}"/>'
    s += screen_art(x + 5, y + 5, sw - 10, sh - 10, uid, glow, rx=4)
    s += f'<circle cx="{200}" cy="{y-0.5}" r="1.8" fill="#43506b"/>'
    # base (keyboard deck seen from front, trapezoid)
    by = y + sh + 6
    bw = sw + (46 if gaming else 34)
    bx = 200 - bw / 2
    deck = "url(#body%s)" % uid if gaming or kind == "business" else "url(#metal%s)" % uid
    s += f'<path d="M{x-6} {by} H{x+sw+6} L{bx+bw} {by+22} Q{bx+bw} {by+30} {bx+bw-8} {by+30} H{bx+8} Q{bx} {by+30} {bx} {by+22} Z" fill="{deck}"/>'
    s += f'<rect x="{200-34}" y="{by}" width="68" height="6" rx="3" fill="#000" fill-opacity=".22"/>'
    if gaming:
        rgb = ["#ff4d6d", "#ffd23f", "#3ddc97", "#4cc9f0", "#9d4edd"] if kind == "gaming-pro" else [light, glow, light, glow, light]
        for i, col in enumerate(rgb):
            s += f'<rect x="{bx+14+i*((bw-28)/5)}" y="{by+24}" width="{(bw-28)/5-4}" height="3" rx="1.5" fill="{col}" fill-opacity=".95"/>'
        if kind == "gaming-pro":
            s += f'<path d="M{x-6} {y+sh+6} l-12 0 M{x+sw+6} {y+sh+6} l12 0" stroke="#ff4d6d" stroke-width="3" stroke-linecap="round"/>'
    if kind == "business":
        s += f'<rect x="{bx+10}" y="{by+22}" width="14" height="4" rx="2" fill="#d33"/>'
    if kind == "student":
        s += f'<rect x="{bx+10}" y="{by+22}" width="{bw-20}" height="3" rx="1.5" fill="{light}" fill-opacity=".7"/>'
    s += "</g></svg>"
    return s


def hero_svg() -> str:
    c = COLORWAYS["indigo"]
    uid = "hero"
    t = COLORWAYS["teal"]
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-label="A laptop and a smartphone showing abstract price-trend lines">{defs(uid, *c)}'
    s += '<defs><linearGradient id="scr2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f4c5c"/><stop offset="1" stop-color="#14a3a8"/></linearGradient></defs>'
    s += '<ellipse cx="320" cy="250" rx="290" ry="200" fill="url(#glowhero)"/>'
    # laptop
    x, y, sw, sh = 110, 80, 400, 250
    s += f'<g filter="url(#shhero)"><rect x="{x-10}" y="{y-10}" width="{sw+20}" height="{sh+20}" rx="16" fill="url(#bodyhero)"/><rect x="{x}" y="{y}" width="{sw}" height="{sh}" rx="8" fill="#0b1020"/>'
    s += screen_art(x + 6, y + 6, sw - 12, sh - 12, uid, c[2], rx=5)
    # dashboard-like blocks on the laptop screen (abstract)
    for i, hh in enumerate((50, 80, 62, 104, 90, 130)):
        s += f'<rect x="{x+30+i*26}" y="{y+sh-26-hh}" width="16" height="{hh}" rx="3" fill="#fff" fill-opacity=".22"/>'
    by = y + sh + 10
    s += f'<path d="M{x-10} {by} H{x+sw+10} L{x+sw+54} {by+34} Q{x+sw+54} {by+44} {x+sw+44} {by+44} H{x-44} Q{x-54} {by+44} {x-54} {by+34} Z" fill="url(#metalhero)"/><rect x="{320-48}" y="{by}" width="96" height="8" rx="4" fill="#000" fill-opacity=".2"/></g>'
    # phone in front
    px, py, pw, ph = 438, 168, 132, 262
    s += f'<g filter="url(#shhero)"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="24" fill="url(#bodyhero)"/>'
    s += '<rect x="%d" y="%d" width="%d" height="%d" rx="18" fill="url(#scr2)"/>' % (px + 7, py + 7, pw - 14, ph - 14)
    pts = " ".join(f"{px+7+(pw-14)*a:.1f},{py+7+(ph-14)*b:.1f}" for a, b in [(.08, .72), (.28, .6), (.45, .66), (.62, .45), (.8, .36), (.94, .24)])
    s += f'<polyline points="{pts}" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    s += f'<polyline points="{px+7+(pw-14)*.62:.1f},{py+7+(ph-14)*.45:.1f} {px+7+(pw-14)*.8:.1f},{py+7+(ph-14)*.36:.1f} {px+7+(pw-14)*.94:.1f},{py+7+(ph-14)*.24:.1f}" fill="none" stroke="#fcd38a" stroke-width="4" stroke-linecap="round" stroke-dasharray="1 9"/>'
    s += f'<rect x="{px+22}" y="{py+24}" width="60" height="6" rx="3" fill="#fff" fill-opacity=".6"/><circle cx="{px+pw/2}" cy="{py+18}" r="4" fill="#0b1020"/></g>'
    # sparkles
    for cx, cy, r in ((70, 90, 6), (585, 70, 8), (560, 400, 5), (60, 380, 7)):
        s += f'<path d="M{cx} {cy-r*2} L{cx+r*.6} {cy-r*.6} L{cx+r*2} {cy} L{cx+r*.6} {cy+r*.6} L{cx} {cy+r*2} L{cx-r*.6} {cy+r*.6} L{cx-r*2} {cy} L{cx-r*.6} {cy-r*.6} Z" fill="{t[2]}" fill-opacity=".85"/>'
    return s + "</svg>"


def pattern_bg(name: str, color: str, kind: str) -> str:
    if kind == "grid":
        body = f'<pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{color}" stroke-opacity=".10"/></pattern><rect width="100%" height="100%" fill="url(#g)"/>'
    else:  # circuit
        body = (f'<pattern id="c" width="120" height="120" patternUnits="userSpaceOnUse"><g fill="none" stroke="{color}" stroke-opacity=".14" stroke-width="1.5">'
                '<path d="M0 30H40L52 42H120"/><path d="M0 90H30L42 78H80L92 90H120"/><path d="M60 0V20L72 32V60"/><path d="M20 120V100L32 88"/></g>'
                f'<g fill="{color}" fill-opacity=".22"><circle cx="40" cy="30" r="3"/><circle cx="72" cy="60" r="3"/><circle cx="80" cy="78" r="3"/><circle cx="32" cy="88" r="3"/></g></pattern>'
                '<rect width="100%" height="100%" fill="url(#c)"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="480" viewBox="0 0 480 480" aria-hidden="true">{body}</svg>'


def art_card(kind: str) -> str:
    """Small 320x200 illustrations for feature cards and sections (abstract, no numbers)."""
    c = COLORWAYS["indigo"]; t = COLORWAYS["teal"]; a = COLORWAYS["amber"]
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" role="img" aria-label="%s">'
    defs_ = ('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef2ff"/><stop offset="1" stop-color="#e0f2f1"/></linearGradient>'
             '<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#14a3a8"/><stop offset="1" stop-color="#6366f1"/></linearGradient></defs>')
    base = '<rect width="320" height="200" rx="14" fill="url(#bg)"/>'
    if kind == "ai":
        nodes = [(50, 100), (130, 50), (130, 100), (130, 150), (210, 70), (210, 130), (280, 100)]
        edges = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5), (4, 6), (5, 6)]
        body = "".join(f'<line x1="{nodes[i][0]}" y1="{nodes[i][1]}" x2="{nodes[j][0]}" y2="{nodes[j][1]}" stroke="#6366f1" stroke-opacity=".35" stroke-width="2"/>' for i, j in edges)
        body += "".join(f'<circle cx="{x}" cy="{y}" r="11" fill="#fff" stroke="{"#14a3a8" if k in (0, 6) else "#6366f1"}" stroke-width="3"/>' for k, (x, y) in enumerate(nodes))
        label = "Neural network illustration"
    elif kind == "forecast":
        body = '<path d="M24 150 C70 140 100 120 150 112 S200 100 226 92" fill="none" stroke="#14a3a8" stroke-width="5" stroke-linecap="round"/>'
        body += '<path d="M226 92 L296 62 L296 118 Z" fill="#e08a1e" fill-opacity=".18"/><path d="M226 92 C250 84 272 76 296 90" fill="none" stroke="#e08a1e" stroke-width="5" stroke-linecap="round" stroke-dasharray="3 10"/>'
        body += '<line x1="226" y1="30" x2="226" y2="170" stroke="#64748b" stroke-dasharray="3 5"/><circle cx="226" cy="92" r="7" fill="#fff" stroke="#14a3a8" stroke-width="4"/>'
        label = "Forecast line illustration"
    elif kind == "trends":
        body = "".join(f'<rect x="{34+i*38}" y="{170-h}" width="24" height="{h}" rx="5" fill="{"#14a3a8" if i%2==0 else "#6366f1"}" fill-opacity=".85"/>' for i, h in enumerate((40, 74, 58, 100, 84, 124, 108)))
        body += '<path d="M40 120 L80 96 L118 108 L156 66 L194 80 L232 40 L270 52" fill="none" stroke="#e08a1e" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
        label = "Price trend bars illustration"
    elif kind == "compare":
        body = ('<rect x="30" y="40" width="108" height="124" rx="12" fill="#fff" stroke="#c7d2fe" stroke-width="2"/><rect x="182" y="40" width="108" height="124" rx="12" fill="#fff" stroke="#99f6e4" stroke-width="2"/>'
                '<rect x="62" y="56" width="44" height="72" rx="8" fill="#6366f1"/><rect x="198" y="64" width="76" height="52" rx="5" fill="#14a3a8"/><rect x="190" y="118" width="92" height="7" rx="3" fill="#14a3a8" fill-opacity=".5"/>'
                '<rect x="46" y="140" width="76" height="6" rx="3" fill="#94a3b8"/><rect x="198" y="140" width="76" height="6" rx="3" fill="#94a3b8"/>'
                '<circle cx="160" cy="102" r="17" fill="#0f1b2d"/><path d="M152 102h16M164 96l6 6-6 6" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        label = "Device comparison illustration"
    elif kind == "analytics":
        body = ('<rect x="24" y="26" width="272" height="148" rx="12" fill="#fff" stroke="#dbe3ee"/><rect x="38" y="42" width="60" height="8" rx="4" fill="#94a3b8"/>'
                '<path d="M40 150 L84 122 L124 134 L170 88 L214 104 L282 60" fill="none" stroke="url(#ln)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
                '<rect x="40" y="64" width="46" height="18" rx="5" fill="#e0e7ff"/><rect x="92" y="64" width="46" height="18" rx="5" fill="#ccfbf1"/><rect x="144" y="64" width="46" height="18" rx="5" fill="#fef3c7"/>')
        label = "Analytics dashboard illustration"
    elif kind == "devices":
        body = ('<rect x="40" y="46" width="170" height="104" rx="8" fill="#0f1b2d"/><rect x="46" y="52" width="158" height="92" rx="4" fill="#14a3a8"/><path d="M52 132 L84 108 L112 118 L150 78 L196 70" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
                '<path d="M26 150 H224 L212 164 H38 Z" fill="#b9c3d4"/><rect x="226" y="70" width="54" height="104" rx="10" fill="#0f1b2d"/><rect x="231" y="76" width="44" height="92" rx="6" fill="#6366f1"/><path d="M236 150 L250 130 L262 138 L272 108" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
        label = "Laptop and smartphone illustration"
    else:  # shield / data
        body = ('<ellipse cx="160" cy="62" rx="70" ry="20" fill="#6366f1" fill-opacity=".85"/><path d="M90 62v38c0 11 31 20 70 20s70-9 70-20V62" fill="#818cf8"/><ellipse cx="160" cy="100" rx="70" ry="20" fill="#14a3a8" fill-opacity=".8"/>'
                '<path d="M90 100v38c0 11 31 20 70 20s70-9 70-20v-38" fill="#2dd4bf"/><ellipse cx="160" cy="138" rx="70" ry="20" fill="#6366f1" fill-opacity=".85"/>')
        label = "Data layers illustration"
    return (head % label) + defs_ + base + body + "</svg>"


def main() -> None:
    for shape in PHONE_SHAPES:
        for cw in COLORWAYS:
            write(f"fallback/phone-{shape}-{cw}.svg", phone_svg(shape, cw))
    for kind in LAPTOP_TYPES:
        for cw in COLORWAYS:
            write(f"fallback/laptop-{kind}-{cw}.svg", laptop_svg(kind, cw))
    write("art/hero-devices.svg", hero_svg())
    write("art/bg-grid.svg", pattern_bg("grid", "#1e3a8a", "grid"))
    write("art/bg-circuit.svg", pattern_bg("circuit", "#14a3a8", "circuit"))
    for k in ("ai", "forecast", "trends", "compare", "analytics", "devices", "data"):
        write(f"art/{k}.svg", art_card(k))
    print("Wrote artwork to", OUT)


if __name__ == "__main__":
    main()
