"""Panel builders. Every function takes a theme dict and returns an SVG string."""
import json, os
from core import svg_open, finish, measure, esc, grid, ROOT

W = 1000

STATS_PATH = os.path.join(ROOT, "stats.json")
DEFAULT_STATS = {"repos": 59, "swift_pct": 84, "years": "3+", "bytes_swift": 5424993}


def stats():
    try:
        return {**DEFAULT_STATS, **json.load(open(STATS_PATH))}
    except Exception:
        return DEFAULT_STATS


# ---------------------------------------------------------------- shared parts
def aurora(w, h, t, blobs):
    out = [f'<g filter="url(#soft)" opacity="{t["auroraOp"]}">']
    for (cx, cy, r, col, dx, dy, dur) in blobs:
        out.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*0.78:.0f}" fill="{col}" opacity=".45">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;{dx} {dy};0 0" dur="{dur}" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".22;.5;.22" dur="{dur}" repeatCount="indefinite"/>'
            f"</ellipse>"
        )
    out.append("</g>")
    return "".join(out)


def typewriter(x, y, phrases, size, color, dur=14.0, weight=700, cls="m", tracking=0.0, uid="tw"):
    n = len(phrases)
    g = 1.0 / n
    widths = [measure(p, "M" if cls == "m" else "D", weight, size, tracking) for p in phrases]
    parts, caret_kt, caret_v = [], [0.0], [x]
    for i, (p, wpx) in enumerate(zip(phrases, widths)):
        s = i * g
        te = s + g * 0.42
        hd = s + g * 0.82
        e = (i + 1) * g
        kts = ";".join(f"{k:.5f}" for k in [0.0, s, te, hd, e, 1.0])
        vs = ";".join(f"{v:.2f}" for v in [0, 0, wpx, wpx, 0, 0])
        parts.append(
            f'<clipPath id="{uid}{i}"><rect x="{x}" y="{y-size}" height="{size*1.5:.0f}" width="0">'
            f'<animate attributeName="width" values="{vs}" keyTimes="{kts}" dur="{dur}s" '
            f'repeatCount="indefinite" calcMode="linear"/></rect></clipPath>'
            f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" letter-spacing="{tracking}" clip-path="url(#{uid}{i})">{esc(p)}</text>'
        )
        caret_kt += [s, te, hd, e]
        caret_v += [x, x + wpx, x + wpx, x]
    kts = ";".join(f"{k:.5f}" for k in caret_kt + [1.0])
    vs = ";".join(f"{v:.2f}" for v in caret_v + [x])
    parts.append(
        f'<rect y="{y-size*0.82:.1f}" width="2" height="{size*0.95:.1f}" rx="1" fill="{color}" x="{x}">'
        f'<animate attributeName="x" values="{vs}" keyTimes="{kts}" dur="{dur}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.45;.5;.95;1" '
        f'dur="1s" repeatCount="indefinite"/></rect>'
    )
    return "".join(parts)


def pill(x, y, label, t, size=11, pad=13, h=26, fill=None, stroke=None, color=None, tracking=0.7,
         weight=700):
    w = measure(label, "M", weight, size, tracking) + pad * 2
    return (
        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2:.0f}" '
        f'fill="{fill or t["panelHi"]}" stroke="{stroke or t["line"]}"/>'
        f'<text class="m" x="{x+pad:.1f}" y="{y+h/2+size*0.36:.1f}" font-size="{size}" '
        f'font-weight="{weight}" letter-spacing="{tracking}" fill="{color or t["muted"]}">'
        f"{esc(label)}</text>"
    ), w


def defs_common(t, w, h, r=18, extra=""):
    return (
        "<defs>"
        f'<clipPath id="clip"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>'
        '<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="46"/></filter>'
        '<filter id="glow" x="-80%" y="-80%" width="260%" height="260%">'
        '<feGaussianBlur stdDeviation="4"/></filter>'
        f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["a1"]}"/><stop offset=".5" stop-color="{t["a2"]}"/>'
        f'<stop offset="1" stop-color="{t["a3"]}"/></linearGradient>'
        f'<linearGradient id="edge" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["grid"]}" stop-opacity=".10"/>'
        f'<stop offset="1" stop-color="{t["grid"]}" stop-opacity="0"/></linearGradient>'
        f"{extra}</defs>"
    )


def frame(t, w, h, r=18):
    return (
        f'<rect width="{w}" height="{h}" rx="{r}" fill="{t["base"]}"/>'
        f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r-0.5}" fill="url(#edge)" '
        f'stroke="{t["line"]}"/>'
    )


def corner_ticks(t, w, h, m=14, L=18):
    c, o = t["a1"], ".45"
    return (
        f'<g stroke="{c}" stroke-opacity="{o}" stroke-width="1.5" fill="none" stroke-linecap="round">'
        f'<path d="M{m} {m+L}V{m}H{m+L}"/><path d="M{w-m-L} {m}H{w-m}V{m+L}"/>'
        f'<path d="M{w-m} {h-m-L}V{h-m}H{w-m-L}"/><path d="M{m+L} {h-m}H{m}V{h-m-L}"/>'
        f'<animate attributeName="stroke-opacity" values=".18;.55;.18" dur="4s" repeatCount="indefinite"/>'
        f"</g>"
    )


# ---------------------------------------------------------------------- 1 HERO
def hero(t):
    w, h = W, 396
    st = stats()
    css = ("@keyframes sh{0%{transform:translateX(-40%)}100%{transform:translateX(150%)}}"
           ".shine{animation:sh 6s cubic-bezier(.45,0,.2,1) infinite}")
    defs = defs_common(t, w, h, extra=(
        '<linearGradient id="nameg" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["text"]}"/><stop offset=".40" stop-color="{t["text"]}"/>'
        f'<stop offset=".50" stop-color="{t["a1"]}"/><stop offset=".56" stop-color="{t["a2"]}"/>'
        f'<stop offset=".66" stop-color="{t["text"]}"/><stop offset="1" stop-color="{t["text"]}"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" '
        'values="-.75 0;.75 0;-.75 0" dur="8s" repeatCount="indefinite"/></linearGradient>'
        '<linearGradient id="shineg" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["grid"]}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{t["grid"]}" stop-opacity=".12"/>'
        f'<stop offset="1" stop-color="{t["grid"]}" stop-opacity="0"/></linearGradient>'
        '<clipPath id="phone"><rect x="778" y="88" width="152" height="248" rx="26"/></clipPath>'
    ))
    s = [svg_open(w, h, t, css, defs), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [
        (110, 30, 200, t["a1"], 60, 40, "17s"),
        (880, 340, 210, t["a2"], -70, -40, "21s"),
        (520, -50, 180, t["a3"], 40, 70, "19s"),
    ]))
    s.append(grid(w, h, t, 34, 1.0, "30s"))
    s.append(corner_ticks(t, w, h))

    s.append(
        f'<circle cx="46" cy="46" r="4" fill="{t["ok"]}">'
        f'<animate attributeName="opacity" values=".35;1;.35" dur="2.2s" repeatCount="indefinite"/></circle>'
        f'<circle cx="46" cy="46" r="4" fill="{t["ok"]}">'
        f'<animate attributeName="r" values="4;13;4" dur="2.2s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".45;0;0" dur="2.2s" repeatCount="indefinite"/></circle>'
        f'<text class="m" x="62" y="50" font-size="11" font-weight="700" letter-spacing="1.8" '
        f'fill="{t["muted"]}">OPEN TO WORK</text>'
        f'<text class="m" x="{w-46}" y="50" font-size="11" font-weight="500" letter-spacing="1.6" '
        f'fill="{t["dim"]}" text-anchor="end">SYDNEY, AUSTRALIA &#183; GMT+11</text>'
    )
    s.append(f'<text x="44" y="162" font-size="70" font-weight="800" letter-spacing="-2.6" '
             f'fill="url(#nameg)">AMISH TUFAIL</text>')
    s.append(f'<text class="m" x="46" y="200" font-size="14" font-weight="700" fill="{t["dim"]}">&#9656;</text>')
    s.append(typewriter(64, 200, [
        "iOS Engineer", "SwiftUI Specialist", "Server-Side Swift", "On-Device AI",
        "Product Craftsman",
    ], 14, t["a1"], dur=17.0, uid="hw"))
    s.append(
        f'<text x="44" y="242" font-size="15.5" font-weight="500" fill="{t["muted"]}">'
        f'Three years deep in Swift &#8212; almost all of it in private repositories.</text>'
        f'<text x="44" y="266" font-size="15.5" font-weight="500" fill="{t["muted"]}">'
        f'So this page shows how I think and what I build with, not a list of links.</text>'
    )
    x = 44
    for label, col in [("SWIFT", t["a4"]), ("SWIFTUI", t["a1"]), ("SWIFTDATA", t["a3"]),
                       ("VAPOR", t["a2"]), ("ON-DEVICE AI", t["muted"])]:
        p, pw = pill(x, 300, label, t, color=col)
        s.append(p); x += pw + 8

    # bottom meta strip
    s.append(f'<path d="M44 348H{w-44}" stroke="{t["line"]}"/>')
    mx = 44
    for k, v in [("REPOS", str(st.get("total_repos", 115))),
                 ("STREAK", f'{st.get("streak_current", 244)} DAYS'),
                 ("PRIMARY", "SWIFT"), ("FOCUS", "NATIVE iOS")]:
        s.append(
            f'<text class="m" x="{mx}" y="374" font-size="10" font-weight="700" letter-spacing="1.4" '
            f'fill="{t["dim"]}">{k}</text>'
            f'<text class="m" x="{mx+62}" y="374" font-size="10" font-weight="700" letter-spacing="1.4" '
            f'fill="{t["text"]}">{v}</text>'
        )
        mx += 168

    # phone
    s.append(
        f'<ellipse cx="854" cy="212" rx="134" ry="134" stroke="{t["line"]}" fill="none"/>'
        f'<g><animateTransform attributeName="transform" type="rotate" from="0 854 212" '
        f'to="360 854 212" dur="24s" repeatCount="indefinite"/>'
        f'<circle cx="854" cy="78" r="4" fill="{t["a1"]}"/>'
        f'<circle cx="988" cy="212" r="2.6" fill="{t["a3"]}"/>'
        f'<circle cx="854" cy="346" r="3" fill="{t["a2"]}"/></g>'
        f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -9;0 0" '
        f'dur="6s" repeatCount="indefinite"/>'
        f'<rect x="778" y="88" width="152" height="248" rx="26" fill="{t["panel"]}" '
        f'stroke="{t["lineHi"]}" stroke-width="1.5"/><g clip-path="url(#phone)">'
        f'<rect x="778" y="88" width="152" height="44" fill="{t["panelHi"]}"/>'
        f'<rect x="832" y="98" width="44" height="13" rx="6.5" fill="{t["base"]}"/>'
        f'<text class="m" x="794" y="154" font-size="8.5" font-weight="700" letter-spacing="1.2" '
        f'fill="{t["dim"]}">TODAY</text>'
    )
    for i in range(3):
        y = 166 + i * 38
        d = i * 0.13
        s.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" '
            f'keyTimes="0;{0.05+d:.3f};{0.16+d:.3f};.84;1" dur="6s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 10;0 10;0 0;0 0" '
            f'keyTimes="0;{0.05+d:.3f};{0.16+d:.3f};1" dur="6s" repeatCount="indefinite"/>'
            f'<rect x="792" y="{y}" width="124" height="30" rx="9" fill="{t["inset"]}" stroke="{t["line"]}"/>'
            f'<circle cx="807" cy="{y+15}" r="5" fill="{[t["a1"],t["a3"],t["a4"]][i]}"/>'
            f'<rect x="819" y="{y+9}" width="{[54,66,44][i]}" height="4.5" rx="2.25" fill="{t["muted"]}" opacity=".55"/>'
            f'<rect x="819" y="{y+18}" width="{[38,30,52][i]}" height="4" rx="2" fill="{t["dim"]}" opacity=".45"/></g>'
        )
    s.append(
        f'<rect x="792" y="286" width="124" height="5" rx="2.5" fill="{t["inset"]}"/>'
        f'<rect x="792" y="286" width="0" height="5" rx="2.5" fill="url(#sweep)">'
        f'<animate attributeName="width" values="0;124;124" keyTimes="0;.75;1" dur="6s" '
        f'repeatCount="indefinite"/></rect>'
        f'<rect x="792" y="304" width="124" height="20" rx="10" fill="{t["a1"]}" opacity=".16"/>'
        f'<text class="m" x="854" y="318" font-size="8.5" font-weight="700" letter-spacing="1" '
        f'fill="{t["a1"]}" text-anchor="middle">BUILD</text>'
        f'<rect class="shine" x="778" y="88" width="46" height="248" fill="url(#shineg)"/></g></g>'
    )
    s.append("</g></svg>")
    return finish("".join(s))


# ------------------------------------------------------------------- 2 DIVIDER
def _divider(t, num, title, sub):
    w, h = W, 74
    s = [svg_open(w, h, t), '<g>']
    s.append(
        f'<text class="m" x="2" y="30" font-size="11" font-weight="700" letter-spacing="2.4" '
        f'fill="{t["a1"]}">{num}</text>'
        f'<text x="2" y="58" font-size="25" font-weight="800" letter-spacing="-.7" '
        f'fill="{t["text"]}">{title}</text>'
    )
    tw = measure(title, "D", 800, 25, -0.7)
    s.append(
        f'<text class="m" x="{tw+22}" y="57" font-size="11.5" font-weight="500" '
        f'fill="{t["dim"]}">{sub}</text>'
    )
    s.append(
        f'<path d="M2 71H{w-2}" stroke="{t["line"]}"/>'
        f'<rect x="2" y="70" width="120" height="2" rx="1" fill="url(#sweep)">'
        f'<animate attributeName="x" values="2;{w-124};2" dur="9s" repeatCount="indefinite"/></rect>'
    )
    s.append("</g></svg>")
    return finish("".join(s).replace("<defs>", "<defs>", 1).replace(
        "<style>", f'<defs><linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
                   f'<stop offset="0" stop-color="{t["a1"]}" stop-opacity="0"/>'
                   f'<stop offset=".5" stop-color="{t["a1"]}"/>'
                   f'<stop offset="1" stop-color="{t["a2"]}" stop-opacity="0"/>'
                   f"</linearGradient></defs><style>", 1))


def div_build(t):      return _divider(t, "01 / METHOD", "How I actually build", "framing to review")
def div_principles(t): return _divider(t, "02 / PRINCIPLES", "What I optimise for", "six opinions")
def div_stack(t):      return _divider(t, "03 / ARCHITECTURE", "What the inside looks like", "layers, not spaghetti")
def div_signal(t):     return _divider(t, "04 / SIGNAL", "The receipts", "pulled live from the GitHub API")
def div_focus(t):      return _divider(t, "05 / FOCUS", "Where the hours go", "self-reported, honestly")
def div_now(t):        return _divider(t, "07 / NOW", "What I am on right now", "updated as it changes")


# ------------------------------------------------------------------ 3 TERMINAL
def terminal(t):
    """Types once on load and freezes. A looping terminal spends half its life
    empty, which is a bad first impression on a page people scroll past."""
    w, h = W, 372
    defs = defs_common(t, w, h, extra=(
        f'<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["panelHi"]}"/><stop offset="1" stop-color="{t["panel"]}"/>'
        "</linearGradient>"))
    s = [svg_open(w, h, t, "", defs), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(140, 400, 170, t["a3"], 60, -40, "23s"),
                              (900, -20, 170, t["a2"], -50, 50, "19s")]))
    s.append(
        f'<rect width="{w}" height="46" fill="url(#tg)"/><path d="M0 46H{w}" stroke="{t["line"]}"/>'
        f'<circle cx="26" cy="23" r="5" fill="#FF5F57" opacity=".9"/>'
        f'<circle cx="44" cy="23" r="5" fill="#FEBC2E" opacity=".9"/>'
        f'<circle cx="62" cy="23" r="5" fill="#28C840" opacity=".9"/>'
        f'<text class="m" x="{w/2}" y="27" font-size="11.5" font-weight="500" fill="{t["dim"]}" '
        f'text-anchor="middle">amish@sydney &#8212; zsh &#8212; 120&#215;40</text>'
    )
    # --- command, typed one character at a time
    cmd = "amish --whoami --verbose"
    steps = [measure(cmd[:i], "M", 500, 13.5) for i in range(len(cmd) + 1)]
    type_dur = 1.9
    vals = ";".join(f"{v:.2f}" for v in steps)
    s.append(
        f'<text class="m" x="30" y="88" font-size="13.5" font-weight="700" fill="{t["a3"]}">&#10095;</text>'
        f'<clipPath id="cmdc"><rect x="48" y="74" height="20" width="0">'
        f'<animate attributeName="width" values="{vals}" dur="{type_dur}s" begin=".35s" '
        f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
        f'<text class="m" x="48" y="88" font-size="13.5" font-weight="500" fill="{t["text"]}" '
        f'clip-path="url(#cmdc)">{esc(cmd)}</text>'
        f'<rect y="76" width="7.5" height="15" fill="{t["a3"]}" x="48" opacity=".9">'
        f'<animate attributeName="x" values="{";".join(f"{48+v:.2f}" for v in steps)}" '
        f'dur="{type_dur}s" begin=".35s" calcMode="discrete" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.45;.5;.95;1" dur=".9s" '
        f'repeatCount="indefinite"/></rect>'
    )
    rows = [
        ("name",       "Amish Tufail", t["text"], t["a1"]),
        ("role",       "iOS Engineer &#183; native product craft", t["text"], None),
        ("location",   "Sydney, Australia", t["muted"], None),
        ("languages",  "Swift (primary) &#183; Python &#183; SQL", t["muted"], None),
        ("frameworks", "SwiftUI &#183; SwiftData &#183; UIKit &#183; Combine &#183; Vapor", t["muted"], None),
        ("patterns",   "clean architecture, DI, versioned schema migrations", t["muted"], None),
        ("testing",    "XCTest and Swift Testing, written as I go", t["muted"], None),
        ("streak",     f'{stats().get("streak_current", 244)} consecutive days of commits', t["a3"], t["a3"]),
        ("visibility", "most repositories are private", t["muted"], None),
        ("principle",  "&#8220;the last ten percent is the product&#8221;", t["a4"], t["a4"]),
    ]
    y0, base = 128, 2.45
    for i, (k, v, col, dot) in enumerate(rows):
        y = y0 + i * 23
        b = base + i * 0.14
        s.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur=".4s" begin="{b:.2f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-10 0" to="0 0" '
            f'dur=".4s" begin="{b:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/>'
            f'<rect x="30" y="{y-10}" width="3" height="13" rx="1.5" fill="{dot or t["line"]}"/>'
            f'<text class="m" x="46" y="{y}" font-size="12.5" font-weight="700" fill="{t["dim"]}">{k}</text>'
            f'<text class="m" x="166" y="{y}" font-size="12.5" font-weight="500" fill="{col}">{v}</text></g>'
        )
    ty = y0 + len(rows) * 23 + 14
    tb = base + len(rows) * 0.14 + 0.2
    s.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".4s" '
        f'begin="{tb:.2f}s" fill="freeze"/>'
        f'<text class="m" x="30" y="{ty}" font-size="13.5" font-weight="700" fill="{t["a3"]}">&#10095;</text>'
        f'<rect x="48" y="{ty-12}" width="7.5" height="15" fill="{t["a3"]}" opacity=".9">'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.45;.5;.95;1" dur=".9s" '
        f'repeatCount="indefinite"/></rect></g>'
    )
    s.append("</g></svg>")
    return finish("".join(s))


# ------------------------------------------------------------------- 4 MARQUEE
ROWS = [
    (["Swift", "SwiftUI", "SwiftData", "UIKit", "Combine", "async / await", "Core Data",
      "MapKit", "AVFoundation", "Vision", "Core ML", "Foundation Models", "WidgetKit"], False, "38s"),
    (["Vapor", "Fluent", "PostgreSQL", "Firebase", "Supabase", "CloudKit", "RevenueCat",
      "Stripe", "REST", "WebSockets", "Alamofire", "Keychain", "OAuth"], True, "44s"),
    (["Clean Architecture", "MVVM", "Dependency Injection", "XCTest", "Swift Testing",
      "Instruments", "GitHub Actions", "TestFlight", "Figma", "Accessibility",
      "Schema Migrations"], False, "50s"),
]


def marquee(t):
    w, h = W, 194
    rows = []
    for items, rtl, dur in ROWS:
        seq, x = [], 0
        for it in items:
            p, pw = pill(x, 0, it, t, size=12, pad=15, h=34, fill=t["panel"], stroke=t["line"],
                         color=t["text"], tracking=0.2, weight=500)
            seq.append(p); x += pw + 10
        body = "".join(seq)
        start, end = ("0", f"-{x}") if not rtl else (f"-{x}", "0")
        rows.append((body, x, start, end, dur))
    # Painted vignettes rather than a luminance mask: masks on a group whose
    # bounding box is three screens wide render inconsistently, overlays never do.
    defs = defs_common(t, w, h, extra=(
        f'<linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["base"]}"/>'
        f'<stop offset=".55" stop-color="{t["base"]}" stop-opacity=".65"/>'
        f'<stop offset="1" stop-color="{t["base"]}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="fadeR" x1="1" y1="0" x2="0" y2="0">'
        f'<stop offset="0" stop-color="{t["base"]}"/>'
        f'<stop offset=".55" stop-color="{t["base"]}" stop-opacity=".65"/>'
        f'<stop offset="1" stop-color="{t["base"]}" stop-opacity="0"/></linearGradient>'))
    s = [svg_open(w, h, t, "", defs), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(500, 97, 280, t["a1"], 90, 0, "25s")]))
    inner = []
    for i, (body, total, start, end, dur) in enumerate(rows):
        y = 26 + i * 56
        inner.append(
            f'<g transform="translate(0 {y})"><g>'
            f'<animateTransform attributeName="transform" type="translate" from="{start} 0" '
            f'to="{end} 0" dur="{dur}" repeatCount="indefinite"/>{body}'
            f'<g transform="translate({total} 0)">{body}</g>'
            f'<g transform="translate({total*2} 0)">{body}</g></g></g>'
        )
    s.append("".join(inner))
    s.append(
        f'<rect x="1" y="1" width="120" height="{h-2}" fill="url(#fadeL)"/>'
        f'<rect x="{w-121}" y="1" width="120" height="{h-2}" fill="url(#fadeR)"/>'
    )
    s.append("</g></svg>")
    return finish("".join(s))


# ---------------------------------------------------------------- 5 METHOD
STEPS = [
    ("FRAME", "Understand the job before the JIRA ticket does.",
     "Who is it for, what breaks today, what does done look like."),
    ("BUILD", "Boring architecture so the features can be interesting.",
     "Layers, injected dependencies, one source of truth for state."),
    ("REFINE", "The demo works. Now make it survive real hands.",
     "Empty states, offline, slow networks, VoiceOver, 60fps."),
    ("REVIEW", "Read it back a week later and delete half of it.",
     "The best change usually removes more than it adds."),
]


def method(t):
    w, h = W, 300
    cw = (w - 2 * 28 - 3 * 12) / 4
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(500, 0, 260, t["a2"], 0, 60, "22s")]))
    s.append(grid(w, h, t, 32, 0.8, "40s"))
    # connector
    s.append(f'<path d="M28 56H{w-28}" stroke="{t["line"]}" stroke-dasharray="4 5"/>')
    s.append(
        f'<circle cx="28" cy="56" r="4" fill="{t["a1"]}" filter="url(#glow)">'
        f'<animate attributeName="cx" values="28;{w-28};{w-28}" keyTimes="0;.8;1" dur="6s" '
        f'repeatCount="indefinite"/></circle>'
        f'<circle cx="28" cy="56" r="3" fill="{t["a1"]}">'
        f'<animate attributeName="cx" values="28;{w-28};{w-28}" keyTimes="0;.8;1" dur="6s" '
        f'repeatCount="indefinite"/></circle>'
    )
    for i, (title, l1, l2) in enumerate(STEPS):
        x = 28 + i * (cw + 12)
        d = i * 0.14
        col = [t["a1"], t["a2"], t["a3"], t["a4"]][i]
        s.append(
            f'<circle cx="{x+9}" cy="56" r="6.5" fill="{t["base"]}" stroke="{t["line"]}"/>'
            f'<circle cx="{x+9}" cy="56" r="3.5" fill="{col}">'
            f'<animate attributeName="opacity" values=".35;1;.35" dur="3s" begin="{i*0.4}s" '
            f'repeatCount="indefinite"/></circle>'
            f'<text class="m" x="{x}" y="30" font-size="10" font-weight="700" letter-spacing="1.6" '
            f'fill="{t["dim"]}">STEP {i+1:02d}</text>'
            f'<text x="{x}" y="106" font-size="21" font-weight="800" letter-spacing="-.5" '
            f'fill="{t["text"]}">{title}</text>'
            f'<rect x="{x}" y="120" width="0" height="2" rx="1" fill="{col}">'
            f'<animate attributeName="width" values="0;34;34" keyTimes="0;.35;1" dur="4s" '
            f'begin="{d*6:.1f}s" repeatCount="indefinite"/></rect>'
        )
        for j, line in enumerate(_wrap(l1, 31)):
            s.append(f'<text x="{x}" y="{150+j*19}" font-size="12.5" font-weight="600" '
                     f'fill="{t["text"]}">{line}</text>')
        for j, line in enumerate(_wrap(l2, 36)):
            s.append(f'<text x="{x}" y="{206+j*18}" font-size="11.5" font-weight="500" '
                     f'fill="{t["dim"]}">{line}</text>')
    s.append("</g></svg>")
    return finish("".join(s))


def _wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > n and cur:
            lines.append(cur); cur = wd
        else:
            cur = (cur + " " + wd).strip()
    if cur:
        lines.append(cur)
    return [esc(l) for l in lines]


# ------------------------------------------------------------- 7 ARCHITECTURE
LAYERS = [
    ("PRESENTATION", "Views, view models, navigation state", "a1",
     ["SwiftUI View", "ViewModel"]),
    ("DOMAIN", "Entities, use cases, repository protocols", "a2",
     ["UseCase", "RepositoryProtocol"]),
    ("DATA", "Repository implementations, DTOs, mapping", "a3",
     ["RepositoryImpl", "DTO + Mapper"]),
    ("PERSISTENCE", "SwiftData schema and versioned migration plans", "a4",
     ["SchemaV1", "MigrationPlan"]),
]


def architecture(t):
    w, h = W, 404
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(760, 40, 220, t["a2"], -40, 60, "20s"),
                              (160, 340, 200, t["a1"], 50, -40, "24s")]))
    s.append(grid(w, h, t, 32, 0.7, "44s"))
    s.append(
        f'<text class="m" x="30" y="36" font-size="10.5" font-weight="700" letter-spacing="2" '
        f'fill="{t["dim"]}">REQUEST FLOWS DOWN &#183; DEPENDENCIES POINT INWARD</text>'
    )
    top = 56
    lh, gap = 68, 8
    for i, (name, desc, key, syms) in enumerate(LAYERS):
        y = top + i * (lh + gap)
        col = t[key]
        s.append(
            f'<rect x="30" y="{y}" width="{w-60}" height="{lh}" rx="12" fill="{t["panel"]}" '
            f'stroke="{t["line"]}"/>'
            f'<rect x="30" y="{y}" width="4" height="{lh}" rx="2" fill="{col}" opacity=".8"/>'
            f'<text class="m" x="52" y="{y+28}" font-size="12" font-weight="700" letter-spacing="1.8" '
            f'fill="{col}">{name}</text>'
            f'<text x="52" y="{y+50}" font-size="12.5" font-weight="500" fill="{t["muted"]}">{desc}</text>'
        )
        x = w - 46
        for sym in reversed(syms):
            pw = measure(sym, "M", 500, 10, 0.2) + 20
            x -= pw
            s.append(
                f'<rect x="{x:.1f}" y="{y+22}" width="{pw:.1f}" height="24" rx="7" fill="{t["inset"]}" '
                f'stroke="{t["line"]}"/>'
                f'<text class="m" x="{x+10:.1f}" y="{y+38}" font-size="10" font-weight="500" '
                f'letter-spacing=".2" fill="{t["dim"]}">{sym}</text>'
            )
            x -= 7
        if i < len(LAYERS) - 1:
            ay = y + lh
            s.append(
                f'<path d="M50 {ay}v{gap}" stroke="{t["line"]}"/>'
                f'<circle cx="50" cy="{ay}" r="2.6" fill="{t["a1"]}">'
                f'<animate attributeName="cy" values="{ay};{ay+gap};{ay+gap}" dur="1.4s" '
                f'begin="{i*0.35}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="1;1;0" dur="1.4s" begin="{i*0.35}s" '
                f'repeatCount="indefinite"/></circle>'
            )
    s.append(
        f'<text class="m" x="30" y="{h-18}" font-size="10.5" font-weight="500" letter-spacing="1.2" '
        f'fill="{t["dim"]}">The UI never touches the database. Dependencies only ever point inward.</text>'
    )
    s.append("</g></svg>")
    return finish("".join(s))


# ---------------------------------------------------------------------- 9 NOW
NOW = [
    ("BUILDING", "a1", "A SwiftData app, currently deep in versioned schema migrations"),
    ("EXPLORING", "a2", "Apple Foundation Models for fully on-device summarisation"),
    ("LEARNING", "a3", "Aspect-based sentiment analysis and OSINT tooling in Python"),
    ("OPEN TO", "a4", "iOS roles in Sydney, remote-friendly teams, contract work"),
]


def now(t):
    w, h = W, 268
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(500, 260, 260, t["a3"], 0, -60, "23s")]))
    s.append(grid(w, h, t, 32, 0.7, "38s"))
    for i, (k, key, v) in enumerate(NOW):
        y = 56 + i * 54
        col = t[key]
        s.append(
            f'<circle cx="40" cy="{y-5}" r="5" fill="{col}">'
            f'<animate attributeName="opacity" values=".35;1;.35" dur="2.6s" begin="{i*0.5}s" '
            f'repeatCount="indefinite"/></circle>'
            f'<circle cx="40" cy="{y-5}" r="5" fill="{col}">'
            f'<animate attributeName="r" values="5;14;5" dur="2.6s" begin="{i*0.5}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".35;0;0" dur="2.6s" begin="{i*0.5}s" '
            f'repeatCount="indefinite"/></circle>'
            f'<text class="m" x="60" y="{y}" font-size="11" font-weight="700" letter-spacing="1.8" '
            f'fill="{col}">{k}</text>'
            f'<text x="196" y="{y}" font-size="14.5" font-weight="500" fill="{t["text"]}">{v}</text>'
        )
        if i < len(NOW) - 1:
            s.append(f'<path d="M40 {y+22}H{w-40}" stroke="{t["line"]}" stroke-opacity=".7"/>')
    s.append("</g></svg>")
    return finish("".join(s))


# ------------------------------------------------------------------- 10 FOOTER
def footer(t):
    w, h = W, 264
    defs = defs_common(t, w, h, extra=(
        '<linearGradient id="fg" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["a1"]}"/><stop offset=".5" stop-color="{t["a2"]}"/>'
        f'<stop offset="1" stop-color="{t["a3"]}"/></linearGradient>'))
    s = [svg_open(w, h, t, "", defs), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(200, 240, 220, t["a1"], 70, -40, "19s"),
                              (800, 20, 220, t["a2"], -60, 50, "23s")]))
    s.append(grid(w, h, t, 34, 0.9, "36s"))
    # wave
    wave = ("M0 176 C 90 146 150 206 250 176 S 410 146 500 176 S 660 206 750 176 S 910 146 1000 176")
    s.append(
        f'<path d="{wave}" stroke="url(#fg)" stroke-width="2" fill="none" opacity=".26"/>'
        f'<path d="{wave}" stroke="url(#fg)" stroke-width="2.5" fill="none" opacity=".95" '
        f'stroke-linecap="round" stroke-dasharray="150 1250" stroke-dashoffset="150">'
        f'<animate attributeName="stroke-dashoffset" values="150;-1250" dur="7s" '
        f'repeatCount="indefinite"/></path>'
        f'<path d="{wave}" stroke="{t["line"]}" stroke-width="1.5" fill="none" opacity=".55" '
        f'transform="translate(0 16)"/>'
        f'<path d="{wave}" stroke="{t["line"]}" stroke-width="1" fill="none" opacity=".3" '
        f'transform="translate(0 32)"/>'
    )
    s.append(
        f'<text x="{w/2}" y="82" font-size="40" font-weight="800" letter-spacing="-1.6" '
        f'fill="{t["text"]}" text-anchor="middle">Let&#8217;s build something native.</text>'
        f'<text x="{w/2}" y="116" font-size="15" font-weight="500" fill="{t["muted"]}" '
        f'text-anchor="middle">Open to iOS roles, contract work and interesting problems.</text>'
    )
    labels = ["amish.tufail2002@gmail.com", "@bisckoot", "github.com/amish-tufail"]
    total = sum(measure(l, "M", 700, 11, 0.7) + 26 for l in labels) + 2 * 10
    x = (w - total) / 2
    for i, l in enumerate(labels):
        p, pw = pill(x, 132, l, t, size=11, pad=13, h=30, fill=t["panel"], stroke=t["line"],
                     color=[t["a1"], t["a2"], t["a3"]][i])
        s.append(p); x += pw + 10
    s.append(
        f'<text class="m" x="{w/2}" y="234" font-size="10.5" font-weight="500" letter-spacing="1.4" '
        f'fill="{t["dim"]}" text-anchor="middle">Rendered as animated SVG &#183; fonts embedded &#183; '
        f'no external services</text>'
    )
    s.append("</g></svg>")
    return finish("".join(s))




# ------------------------------------------------------------------ 6 CONTEXT
def _context_points():
    """Numbers come from stats.json so the weekly job keeps this paragraph true."""
    st = stats()
    return [
        ("a1", "Private does not mean idle.",
         f'{st.get("contrib_private", 0):,} of my {st.get("contrib_total", 0):,} '
         f"contributions this year landed in private repositories."),
        ("a3", "The public tab is the old stuff.",
         "Practice repos, UI studies and experiments from while I was learning."),
        ("a4", "Ask me and I will show you.",
         "I am happy to walk through the architecture of any of it on a call."),
    ]


def context(t):
    w, h = W, 322
    st = stats()
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(180, 20, 220, t["a2"], 60, 50, "20s"),
                              (860, 320, 200, t["a1"], -60, -40, "24s")]))
    s.append(grid(w, h, t, 32, 0.7, "40s"))
    s.append(
        f'<text x="40" y="76" font-size="34" font-weight="800" letter-spacing="-1.2" '
        f'fill="{t["text"]}">Most of what I build is private.</text>'
        f'<text x="40" y="112" font-size="15" font-weight="500" fill="{t["muted"]}">'
        f'Client work, apps still in progress, and code that is not ready for an audience yet.</text>'
        f'<path d="M40 140H{w-40}" stroke="{t["line"]}"/>'
    )
    for i, (key, head, sub) in enumerate(_context_points()):
        y = 176 + i * 46
        col = t[key]
        s.append(
            f'<circle cx="47" cy="{y-5}" r="7" fill="none" stroke="{col}" stroke-opacity=".55"/>'
            f'<path d="M43.5 {y-5}l2.5 2.5 4.5-4.5" stroke="{col}" stroke-width="1.8" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="12" '
            f'stroke-dashoffset="12"><animate attributeName="stroke-dashoffset" from="12" to="0" '
            f'dur=".5s" begin="{0.3+i*0.25:.2f}s" fill="freeze"/></path>'
            f'<text x="70" y="{y}" font-size="15" font-weight="800" fill="{t["text"]}">{head}</text>'
            f'<text x="{70+measure(head,"D",800,15)+12:.0f}" y="{y}" font-size="14" '
            f'font-weight="500" fill="{t["dim"]}">{sub}</text>'
        )
    s.append("</g></svg>")
    return finish("".join(s))


# --------------------------------------------------------------- 7 PRINCIPLES
PRINCIPLES = [
    ("01", "Architecture is a budget", "Every shortcut is borrowed time, and the interest compounds.", "a1"),
    ("02", "State has one home", "One source of truth. Everything else is only a view of it.", "a2"),
    ("03", "The demo is not the product", "Empty states, offline, slow networks, VoiceOver. That is the work.", "a3"),
    ("04", "Delete before you add", "The best change usually removes more than it introduces.", "a4"),
    ("05", "Feel is a feature", "Sixty frames a second, honest loading, motion with a reason.", "a1"),
    ("06", "Boring on purpose", "Predictable code is faster to change than clever code.", "a3"),
]


def principles(t):
    w, h = W, 378
    cw, ch, gx, gy = 302, 148, 15, 16
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(120, 40, 200, t["a1"], 70, 40, "21s"),
                              (880, 340, 210, t["a3"], -60, -50, "25s")]))
    s.append(grid(w, h, t, 30, 0.7, "44s"))
    for i, (num, title, body, key) in enumerate(PRINCIPLES):
        cx = 30 + (i % 3) * (cw + gx)
        cy = 34 + (i // 3) * (ch + gy)
        col = t[key]
        s.append(
            f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="{t["panel"]}" '
            f'stroke="{t["line"]}"/>'
            f'<rect x="{cx}" y="{cy}" width="0" height="2" rx="1" fill="{col}" opacity=".7">'
            f'<animate attributeName="width" from="0" to="{cw}" dur="1.1s" '
            f'begin="{0.2+i*0.12:.2f}s" fill="freeze"/></rect>'
            f'<text class="m" x="{cx+20}" y="{cy+32}" font-size="10.5" font-weight="700" '
            f'letter-spacing="2" fill="{col}">{num}</text>'
        )
        for j, line in enumerate(_wrap(title, 24)):
            s.append(f'<text x="{cx+20}" y="{cy+62+j*22}" font-size="17.5" font-weight="800" '
                     f'letter-spacing="-.4" fill="{t["text"]}">{line}</text>')
        off = 62 + len(_wrap(title, 24)) * 22
        for j, line in enumerate(_wrap(body, 40)):
            s.append(f'<text x="{cx+20}" y="{cy+off+j*17}" font-size="12" font-weight="500" '
                     f'fill="{t["dim"]}">{line}</text>')
    s.append("</g></svg>")
    return finish("".join(s))


# ------------------------------------------------------------------ 8 HEATMAP
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def heatmap(t):
    from datetime import date
    st = stats()
    weeks = st.get("contrib_weeks") or [[0] * 7 for _ in range(53)]
    starts = st.get("week_starts") or []
    peak = max(st.get("peak", 1), 1)
    pitch, cell = 16, 13
    x0, y0 = 56, 74
    w, h = W, y0 + 7 * pitch + 66

    def level(c):
        if c == 0:
            return 0
        r = c / peak
        return 1 if r <= .12 else 2 if r <= .3 else 3 if r <= .6 else 4

    OPS = [None, ".28", ".48", ".72", "1"]
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(140, 20, 200, t["a3"], 70, 40, "22s"),
                              (880, 300, 200, t["a1"], -60, -40, "26s")]))
    s.append(
        f'<text class="m" x="30" y="38" font-size="10.5" font-weight="700" letter-spacing="2" '
        f'fill="{t["dim"]}">CONTRIBUTION CALENDAR &#183; LAST 12 MONTHS</text>'
        f'<text class="m" x="{w-30}" y="38" font-size="12" font-weight="700" fill="{t["text"]}" '
        f'text-anchor="end">{st.get("contrib_total", 0):,} contributions</text>'
    )
    # month labels
    seen = set()
    for i, ds in enumerate(starts):
        try:
            y, m, d = (int(v) for v in ds.split("-"))
        except Exception:
            continue
        if m not in seen and d <= 7:
            seen.add(m)
            s.append(f'<text class="m" x="{x0+i*pitch}" y="{y0-10}" font-size="10" '
                     f'font-weight="500" fill="{t["dim"]}">{MONTHS[m-1]}</text>')
    for i, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        s.append(f'<text class="m" x="{x0-10}" y="{y0+i*pitch+10}" font-size="9.5" '
                 f'font-weight="500" fill="{t["dim"]}" text-anchor="end">{lbl}</text>')
    # cells
    for wi, wk in enumerate(weeks):
        for di, c in enumerate(wk):
            lv = level(c)
            cx, cy = x0 + wi * pitch, y0 + di * pitch
            fill = t["panelHi"] if lv == 0 else t["a3"]
            op = "1" if lv == 0 else OPS[lv]
            s.append(
                f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="3" fill="{fill}" '
                f'fill-opacity="{op}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur=".5s" '
                f'begin="{0.15+wi*0.018+di*0.012:.3f}s" fill="freeze"/></rect>'
            )
    # legend
    ly = y0 + 7 * pitch + 30
    s.append(f'<text class="m" x="30" y="{ly+10}" font-size="10" font-weight="500" '
             f'fill="{t["dim"]}">{st.get("active_days",0)} active days out of '
             f'{st.get("total_days",0)}</text>')
    lx = w - 30 - (5 * 17 + 76)
    s.append(f'<text class="m" x="{lx}" y="{ly+10}" font-size="10" font-weight="500" '
             f'fill="{t["dim"]}">Less</text>')
    for i in range(5):
        s.append(f'<rect x="{lx+36+i*17}" y="{ly}" width="13" height="13" rx="3" '
                 f'fill="{t["panelHi"] if i==0 else t["a3"]}" '
                 f'fill-opacity="{"1" if i==0 else OPS[i]}"/>')
    s.append(f'<text class="m" x="{lx+36+5*17+6}" y="{ly+10}" font-size="10" font-weight="500" '
             f'fill="{t["dim"]}">More</text>')
    s.append("</g></svg>")
    return finish("".join(s))


# ------------------------------------------------------------------- 9 STREAK
def _ring(t, cx, cy, r, pct, col, delay=0.3):
    import math
    circ = 2 * math.pi * r
    off = circ * (1 - min(pct, 1.0))
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["inset"]}" stroke-width="6"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="6" '
        f'stroke-linecap="round" transform="rotate(-90 {cx} {cy})" '
        f'stroke-dasharray="{circ:.2f}" stroke-dashoffset="{circ:.2f}">'
        f'<animate attributeName="stroke-dashoffset" from="{circ:.2f}" to="{off:.2f}" dur="1.4s" '
        f'begin="{delay}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></circle>'
    )


def _fmt_date(ds):
    from datetime import date
    try:
        y, m, d = (int(v) for v in ds.split("-"))
        return f"{d} {MONTHS[m-1]} {y}"
    except Exception:
        return ds


def streak(t):
    w, h = W, 318
    st = stats()
    cur = st.get("streak_current", 0)
    lng = st.get("streak_longest", 0)
    act, tot = st.get("active_days", 0), max(st.get("total_days", 1), 1)
    best, bestd = st.get("best_day_count", 0), st.get("best_day", "")
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(160, 30, 210, t["a4"], 60, 50, "19s"),
                              (840, 320, 210, t["a2"], -60, -40, "23s")]))
    s.append(grid(w, h, t, 30, 0.7, "42s"))
    s.append(
        f'<text class="m" x="30" y="38" font-size="10.5" font-weight="700" letter-spacing="2" '
        f'fill="{t["dim"]}">CONSISTENCY</text>'
        f'<text class="m" x="{w-30}" y="38" font-size="11" font-weight="500" fill="{t["dim"]}" '
        f'text-anchor="end">{st.get("contrib_private",0):,} of '
        f'{st.get("contrib_total",0):,} in private repos</text>'
        f'<path d="M30 54H{w-30}" stroke="{t["line"]}"/>'
    )
    cards = [
        (f"{cur}", "CURRENT STREAK", "days, and counting", 1.0, "a4", True),
        (f"{lng}", "LONGEST STREAK", "personal best", 1.0, "a1", False),
        (f"{act}", "ACTIVE DAYS", f"of {tot} days", act / tot, "a3", False),
        (f"{best}", "BUSIEST DAY", _fmt_date(bestd), 1.0, "a2", False),
    ]
    cwid, gap = 224, 16
    for i, (big, label, sub, pct, key, live) in enumerate(cards):
        cx = 30 + i * (cwid + gap)
        cy = 74
        col = t[key]
        s.append(
            f'<rect x="{cx}" y="{cy}" width="{cwid}" height="196" rx="16" fill="{t["panel"]}" '
            f'stroke="{t["line"]}"/>'
        )
        s.append(_ring(t, cx + 52, cy + 66, 30, pct, col, 0.25 + i * 0.15))
        fs = 22 if len(big) > 3 else 26 if len(big) == 3 else 30
        s.append(
            f'<text x="{cx+52}" y="{cy+66+fs*0.36:.0f}" font-size="{fs}" font-weight="800" '
            f'letter-spacing="-1" fill="{t["text"]}" text-anchor="middle" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur=".6s" '
            f'begin="{0.5+i*0.15:.2f}s" fill="freeze"/>{big}</text>'
            f'<text class="m" x="{cx+20}" y="{cy+148}" font-size="10.5" font-weight="700" '
            f'letter-spacing="1.6" fill="{col}">{label}</text>'
            f'<text class="m" x="{cx+20}" y="{cy+172}" font-size="11" font-weight="500" '
            f'fill="{t["dim"]}">{esc(sub)}</text>'
        )
        if live:
            s.append(
                f'<circle cx="{cx+cwid-26}" cy="{cy+26}" r="4" fill="{t["ok"]}">'
                f'<animate attributeName="opacity" values=".35;1;.35" dur="2s" '
                f'repeatCount="indefinite"/></circle>'
                f'<circle cx="{cx+cwid-26}" cy="{cy+26}" r="4" fill="{t["ok"]}">'
                f'<animate attributeName="r" values="4;12;4" dur="2s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values=".4;0;0" dur="2s" '
                f'repeatCount="indefinite"/></circle>'
            )
    s.append("</g></svg>")
    return finish("".join(s))


# -------------------------------------------------------------------- 10 FOCUS
FOCUS = [
    ("SwiftUI and declarative UI", "Layout, animation, and the state that drives them.", 32, "a1"),
    ("Architecture and persistence", "Layering, dependency injection, SwiftData schemas and migrations.", 26, "a2"),
    ("Swift concurrency", "Actors, structured tasks, and not blocking the main thread.", 16, "a3"),
    ("Server-side Swift", "Vapor and Fluent, because one language for both ends is a gift.", 15, "a4"),
    ("On-device intelligence", "Foundation Models, Vision, and keeping data on the phone.", 11, "a1"),
]


def focus(t):
    w, h = W, 398
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(860, 30, 210, t["a2"], -60, 50, "21s"),
                              (140, 330, 200, t["a3"], 60, -40, "25s")]))
    s.append(grid(w, h, t, 30, 0.7, "46s"))
    s.append(
        f'<text class="m" x="30" y="38" font-size="10.5" font-weight="700" letter-spacing="2" '
        f'fill="{t["dim"]}">ROUGHLY HOW A MONTH SPLITS</text>'
    )
    bx, bw = 560, 348
    for i, (name, desc, pct, key) in enumerate(FOCUS):
        y = 76 + i * 54
        col = t[key]
        s.append(
            f'<text x="30" y="{y}" font-size="15" font-weight="800" letter-spacing="-.3" '
            f'fill="{t["text"]}">{name}</text>'
            f'<text x="30" y="{y+20}" font-size="12" font-weight="500" fill="{t["dim"]}">{desc}</text>'
            f'<rect x="{bx}" y="{y-10}" width="{bw}" height="8" rx="4" fill="{t["inset"]}"/>'
            f'<rect x="{bx}" y="{y-10}" width="0" height="8" rx="4" fill="{col}">'
            f'<animate attributeName="width" from="0" to="{bw*pct/100:.1f}" dur="1.3s" '
            f'begin="{0.25+i*0.12:.2f}s" fill="freeze" calcMode="spline" '
            f'keySplines=".2 .8 .2 1"/></rect>'
            f'<text class="m" x="{w-30}" y="{y-2}" font-size="11.5" font-weight="700" fill="{col}" '
            f'text-anchor="end">{pct}%</text>'
        )
    s.append(
        f'<path d="M30 {h-52}H{w-30}" stroke="{t["line"]}"/>'
        f'<text class="m" x="30" y="{h-24}" font-size="10.5" font-weight="500" letter-spacing=".8" '
        f'fill="{t["dim"]}">Self-reported, not measured. The percentages move with whatever '
        f'I am building.</text>'
    )
    s.append("</g></svg>")
    return finish("".join(s))


# --------------------------------------------------------------------- REGISTRY
PANELS = {
    "hero": hero,
    "terminal": terminal,
    "marquee": marquee,
    "div-build": div_build,
    "method": method,
    "div-principles": div_principles,
    "principles": principles,
    "div-stack": div_stack,
    "architecture": architecture,
    "div-signal": div_signal,
    "heatmap": heatmap,
    "streak": streak,
    "div-focus": div_focus,
    "focus": focus,
    "footer": footer,
}

# ------------------------------------------------------------------- 11 LINKS
BADGES = [
    ("email", "EMAIL", "a1",
     "M3 5.2h14v9.6H3zM3 5.8l7 5 7-5"),
    ("x", "@BISCKOOT", "a2",
     "M4 4.5l12 11M16 4.5L4 15.5"),
    ("repos", "REPOSITORIES", "a3",
     "M4.5 4h9a2 2 0 012 2v10H6.5a2 2 0 01-2-2zM4.5 14a2 2 0 012-2h9"),
]


def _badge(t, key, label, colkey, path):
    col = t[colkey]
    tw = measure(label, "M", 700, 11, 1.6)
    w, h = int(tw + 78), 46
    s = [svg_open(w, h, t), '<defs>'
         f'<linearGradient id="bg{key}" x1="0" y1="0" x2="1" y2="1">'
         f'<stop offset="0" stop-color="{col}" stop-opacity=".16"/>'
         f'<stop offset="1" stop-color="{col}" stop-opacity=".04"/></linearGradient></defs>']
    s.append(
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="{t["panel"]}" '
        f'stroke="{t["line"]}"/>'
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="12" fill="url(#bg{key})"/>'
        f'<g transform="translate(16 13)" stroke="{col}" stroke-width="1.6" fill="none" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{path}" transform="scale(.95)"/></g>'
        f'<text class="m" x="48" y="{h/2+4}" font-size="11" font-weight="700" letter-spacing="1.6" '
        f'fill="{t["text"]}">{label}</text>'
        f'<circle cx="{w-16}" cy="{h/2}" r="2.5" fill="{col}">'
        f'<animate attributeName="opacity" values=".3;1;.3" dur="2.4s" repeatCount="indefinite"/>'
        f'</circle>'
    )
    s.append("</svg>")
    return finish("".join(s))


for _k, _l, _c, _p in BADGES:
    PANELS[f"badge-{_k}"] = (lambda k, l, c, pa: (lambda t: _badge(t, k, l, c, pa)))(_k, _l, _c, _p)
