"""Panel builders. Every function takes a theme dict and returns an SVG string.

Scope rule: nothing here asserts anything that is not either (a) a number pulled
from the GitHub API into stats.json, or (b) evidenced by a repository that
actually exists on the account. No invented architecture, process or effort
splits — if it cannot be backed up, it does not go on the page.
"""
import json, os
from core import svg_open, finish, measure, esc, grid, ROOT

W = 1000

STATS_PATH = os.path.join(ROOT, "stats.json")
DEFAULT_STATS = {"repos": 59, "years": "3+", "total_repos": 115}


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
            f'<animate attributeName="opacity" values=".22;.5;.22" dur="{dur}" '
            f'repeatCount="indefinite"/></ellipse>'
        )
    out.append("</g>")
    return "".join(out)


def cycler(x, y, phrases, size, color, dur=16.0, weight=700, cls="m"):
    """Cycles short phrases by fading them in and out.

    The first version clipped each phrase with a <rect width="0"> that SMIL grew.
    Renderers that do not re-evaluate clipPath geometry mid-animation leave the
    text hidden permanently, which is exactly what happened on GitHub. Opacity
    animates reliably everywhere, so that is what this uses now.
    """
    n = len(phrases)
    g = 1.0 / n
    fade = g * 0.16
    widths = [measure(p, "M" if cls == "m" else "D", weight, size) for p in phrases]
    parts = []
    for i, p in enumerate(phrases):
        s0, e0 = i * g, (i + 1) * g
        # Fade out completely at e0 before the next phrase starts fading in at its
        # own s0 (== e0), otherwise two different strings overlap in the same spot.
        pairs = [(0.0, "0"), (s0, "0"), (s0 + fade, "1"),
                 (e0 - fade, "1"), (e0, "0"), (1.0, "0")]
        kt, vals = [], []
        for k, v in pairs:
            k = min(max(round(k, 5), 0.0), 1.0)
            if kt and abs(k - kt[-1]) < 1e-6:
                vals[-1] = v
            else:
                kt.append(k); vals.append(v)
        parts.append(
            f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" opacity="{1 if i == 0 else 0}">{esc(p)}'
            f'<animate attributeName="opacity" values="{";".join(vals)}" '
            f'keyTimes="{";".join(f"{k:.5f}" for k in kt)}" dur="{dur}s" '
            f'repeatCount="indefinite"/></text>'
        )
    ct = [0.0] + [round(i * g, 5) for i in range(n)] + [1.0]
    cx = ([f"{x + widths[0] + 6:.1f}"] + [f"{x + p + 6:.1f}" for p in widths]
          + [f"{x + widths[-1] + 6:.1f}"])
    parts.append(
        f'<rect y="{y-size*0.82:.1f}" width="2" height="{size*0.95:.1f}" rx="1" fill="{color}" '
        f'x="{cx[0]}">'
        f'<animate attributeName="x" values="{";".join(cx)}" '
        f'keyTimes="{";".join(f"{k:.5f}" for k in ct)}" dur="{dur}s" calcMode="discrete" '
        f'repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.45;.5;.95;1" '
        f'dur="1s" repeatCount="indefinite"/></rect>'
    )
    return "".join(parts)


def pill(x, y, label, t, size=11, pad=13, h=26, fill=None, stroke=None, color=None,
         tracking=0.7, weight=700):
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
    return (
        f'<g stroke="{t["a1"]}" stroke-opacity=".45" stroke-width="1.5" fill="none" '
        f'stroke-linecap="round">'
        f'<path d="M{m} {m+L}V{m}H{m+L}"/><path d="M{w-m-L} {m}H{w-m}V{m+L}"/>'
        f'<path d="M{w-m} {h-m-L}V{h-m}H{w-m-L}"/><path d="M{m+L} {h-m}H{m}V{h-m-L}"/>'
        f'<animate attributeName="stroke-opacity" values=".18;.5;.18" dur="4s" '
        f'repeatCount="indefinite"/></g>'
    )


# ---------------------------------------------------------------------- 1 HERO
def hero(t):
    w, h = W, 380
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
        '<clipPath id="phone"><rect x="778" y="82" width="152" height="238" rx="26"/></clipPath>'
    ))
    s = [svg_open(w, h, t, css, defs), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [
        (110, 30, 200, t["a1"], 60, 40, "17s"),
        (880, 330, 210, t["a2"], -70, -40, "21s"),
        (520, -50, 180, t["a3"], 40, 70, "19s"),
    ]))
    s.append(grid(w, h, t, 34, 1.0, "30s"))
    s.append(corner_ticks(t, w, h))
    s.append(
        f'<circle cx="46" cy="46" r="4" fill="{t["ok"]}">'
        f'<animate attributeName="opacity" values=".35;1;.35" dur="2.2s" '
        f'repeatCount="indefinite"/></circle>'
        f'<circle cx="46" cy="46" r="4" fill="{t["ok"]}">'
        f'<animate attributeName="r" values="4;13;4" dur="2.2s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".45;0;0" dur="2.2s" '
        f'repeatCount="indefinite"/></circle>'
        f'<text class="m" x="62" y="50" font-size="11" font-weight="700" letter-spacing="1.8" '
        f'fill="{t["muted"]}">OPEN TO WORK</text>'
        f'<text class="m" x="{w-46}" y="50" font-size="11" font-weight="500" letter-spacing="1.6" '
        f'fill="{t["dim"]}" text-anchor="end">SYDNEY, AUSTRALIA</text>'
    )
    s.append(f'<text x="44" y="158" font-size="70" font-weight="800" letter-spacing="-2.6" '
             f'fill="url(#nameg)">AMISH TUFAIL</text>')
    s.append(f'<text class="m" x="46" y="194" font-size="14" font-weight="700" '
             f'fill="{t["dim"]}">&#9656;</text>')
    s.append(cycler(64, 194, ["iOS Engineer", "Swift Developer", "SwiftUI",
                              "Server-Side Swift"], 14, t["a1"], dur=16.0))
    s.append(
        f'<text x="44" y="234" font-size="15.5" font-weight="500" fill="{t["muted"]}">'
        f'iOS engineer in Sydney. Three years of Swift, most of it in private</text>'
        f'<text x="44" y="257" font-size="15.5" font-weight="500" fill="{t["muted"]}">'
        f'repositories.</text>'
    )
    x = 44
    for label, col in [("SWIFT", t["a4"]), ("SWIFTUI", t["a1"]), ("UIKIT", t["a3"]),
                       ("VAPOR", t["a2"]), ("PYTHON", t["muted"])]:
        p, pw = pill(x, 286, label, t, color=col)
        s.append(p); x += pw + 8

    s.append(f'<path d="M44 344H{w-44}" stroke="{t["line"]}"/>')
    mx = 44
    for k, v in [("REPOS", str(st.get("total_repos", 115))),
                 ("STREAK", f'{st.get("streak_current", 0)} DAYS'),
                 ("CONTRIBUTIONS", f'{st.get("contrib_total", 0):,}'),
                 ("PRIMARY", "SWIFT")]:
        s.append(
            f'<text class="m" x="{mx}" y="368" font-size="10" font-weight="700" '
            f'letter-spacing="1.4" fill="{t["dim"]}">{k}</text>'
            f'<text class="m" x="{mx+measure(k, "M", 700, 10, 1.4)+12:.0f}" y="368" '
            f'font-size="10" font-weight="700" letter-spacing="1.4" fill="{t["text"]}">{v}</text>'
        )
        mx += 232

    s.append(
        f'<ellipse cx="854" cy="202" rx="130" ry="130" stroke="{t["line"]}" fill="none"/>'
        f'<g><animateTransform attributeName="transform" type="rotate" from="0 854 202" '
        f'to="360 854 202" dur="24s" repeatCount="indefinite"/>'
        f'<circle cx="854" cy="72" r="4" fill="{t["a1"]}"/>'
        f'<circle cx="984" cy="202" r="2.6" fill="{t["a3"]}"/>'
        f'<circle cx="854" cy="332" r="3" fill="{t["a2"]}"/></g>'
        f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -9;0 0" '
        f'dur="6s" repeatCount="indefinite"/>'
        f'<rect x="778" y="82" width="152" height="238" rx="26" fill="{t["panel"]}" '
        f'stroke="{t["lineHi"]}" stroke-width="1.5"/><g clip-path="url(#phone)">'
        f'<rect x="778" y="82" width="152" height="44" fill="{t["panelHi"]}"/>'
        f'<rect x="832" y="92" width="44" height="13" rx="6.5" fill="{t["base"]}"/>'
        f'<text class="m" x="794" y="148" font-size="8.5" font-weight="700" letter-spacing="1.2" '
        f'fill="{t["dim"]}">TODAY</text>'
    )
    for i in range(3):
        y = 160 + i * 38
        d = i * 0.13
        s.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" '
            f'keyTimes="0;{0.05+d:.3f};{0.16+d:.3f};.84;1" dur="6s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 10;0 10;0 0;0 0" keyTimes="0;{0.05+d:.3f};{0.16+d:.3f};1" dur="6s" '
            f'repeatCount="indefinite"/>'
            f'<rect x="792" y="{y}" width="124" height="30" rx="9" fill="{t["inset"]}" '
            f'stroke="{t["line"]}"/>'
            f'<circle cx="807" cy="{y+15}" r="5" fill="{[t["a1"],t["a3"],t["a4"]][i]}"/>'
            f'<rect x="819" y="{y+9}" width="{[54,66,44][i]}" height="4.5" rx="2.25" '
            f'fill="{t["muted"]}" opacity=".55"/>'
            f'<rect x="819" y="{y+18}" width="{[38,30,52][i]}" height="4" rx="2" '
            f'fill="{t["dim"]}" opacity=".45"/></g>'
        )
    s.append(
        f'<rect x="792" y="278" width="124" height="5" rx="2.5" fill="{t["inset"]}"/>'
        f'<rect x="792" y="278" width="0" height="5" rx="2.5" fill="url(#sweep)">'
        f'<animate attributeName="width" values="0;124;124" keyTimes="0;.75;1" dur="6s" '
        f'repeatCount="indefinite"/></rect>'
        f'<rect class="shine" x="778" y="82" width="46" height="238" fill="url(#shineg)"/></g></g>'
    )
    s.append("</g></svg>")
    return finish("".join(s))


# ------------------------------------------------------------------ 2 TERMINAL
def terminal(t):
    """Only facts: name, place, languages, and numbers straight from the API."""
    w, h = W, 288
    st = stats()
    defs = defs_common(t, w, h, extra=(
        f'<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{t["panelHi"]}"/><stop offset="1" stop-color="{t["panel"]}"/>'
        "</linearGradient>"))
    s = [svg_open(w, h, t, "", defs), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(140, 320, 170, t["a3"], 60, -40, "23s"),
                              (900, -20, 170, t["a2"], -50, 50, "19s")]))
    s.append(
        f'<rect width="{w}" height="46" fill="url(#tg)"/><path d="M0 46H{w}" stroke="{t["line"]}"/>'
        f'<circle cx="26" cy="23" r="5" fill="#FF5F57" opacity=".9"/>'
        f'<circle cx="44" cy="23" r="5" fill="#FEBC2E" opacity=".9"/>'
        f'<circle cx="62" cy="23" r="5" fill="#28C840" opacity=".9"/>'
        f'<text class="m" x="{w/2}" y="27" font-size="11.5" font-weight="500" fill="{t["dim"]}" '
        f'text-anchor="middle">amish@sydney &#8212; zsh</text>'
    )
    cmd = "amish --whoami"
    s.append(
        f'<text class="m" x="30" y="88" font-size="13.5" font-weight="700" '
        f'fill="{t["a3"]}">&#10095;</text>'
        f'<text class="m" x="48" y="88" font-size="13.5" font-weight="500" '
        f'fill="{t["text"]}">{esc(cmd)}</text>'
        f'<rect x="{48+measure(cmd, "M", 500, 13.5)+5:.1f}" y="76" width="7.5" height="15" '
        f'fill="{t["a3"]}" opacity=".9">'
        f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.45;.5;.95;1" '
        f'dur=".9s" repeatCount="indefinite"/></rect>'
    )
    priv, tot = st.get("contrib_private", 0), st.get("contrib_total", 0)
    rows = [
        ("name",          "Amish Tufail", t["text"], t["a1"]),
        ("role",          "iOS Engineer", t["text"], None),
        ("location",      "Sydney, Australia", t["muted"], None),
        ("languages",     "Swift (primary) &#183; Python", t["muted"], None),
        ("repositories",  f'{st.get("total_repos", 115)}, most of them private',
         t["muted"], None),
        ("contributions", f'{tot:,} in the last year, {priv:,} in private repos',
         t["muted"], None),
        ("streak",        f'{st.get("streak_current", 0)} consecutive days',
         t["a3"], t["a3"]),
    ]
    y0 = 124
    for i, (k, v, col, dot) in enumerate(rows):
        y = y0 + i * 23
        b = 0.25 + i * 0.13
        s.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur=".4s" begin="{b:.2f}s" '
            f'fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-10 0" to="0 0" '
            f'dur=".4s" begin="{b:.2f}s" fill="freeze"/>'
            f'<rect x="30" y="{y-10}" width="3" height="13" rx="1.5" fill="{dot or t["line"]}"/>'
            f'<text class="m" x="46" y="{y}" font-size="12.5" font-weight="700" '
            f'fill="{t["dim"]}">{k}</text>'
            f'<text class="m" x="180" y="{y}" font-size="12.5" font-weight="500" '
            f'fill="{col}">{v}</text></g>'
        )
    s.append("</g></svg>")
    return finish("".join(s))


# ------------------------------------------------------------------- 3 MARQUEE
# Every entry below has a repository behind it on the account.
ROWS = [
    (["Swift", "SwiftUI", "UIKit", "Core Data", "SwiftData", "Combine",
      "Swift Concurrency", "MapKit", "Vision", "ARKit", "Swift Testing"], False, "38s"),
    (["Vapor", "Fluent", "Firebase", "Supabase", "CloudKit", "RevenueCat",
      "Stripe", "Alamofire", "REST APIs", "Realm", "Kingfisher", "Rive"], True, "44s"),
]


def marquee(t):
    w, h = W, 138
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
    s.append(aurora(w, h, t, [(500, 70, 280, t["a1"], 90, 0, "25s")]))
    inner = []
    for i, (body, total, start, end, dur) in enumerate(rows):
        y = 22 + i * 56
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


# ------------------------------------------------------------------- 4 DIVIDER
def div_activity(t):
    w, h = W, 74
    title, sub = "Every commit, last 12 months", "straight from the GitHub API"
    defs = (f'<defs><linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{t["a1"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{t["a1"]}"/>'
            f'<stop offset="1" stop-color="{t["a2"]}" stop-opacity="0"/></linearGradient></defs>')
    s = [svg_open(w, h, t, "", defs)]
    s.append(
        f'<text class="m" x="2" y="30" font-size="11" font-weight="700" letter-spacing="2.4" '
        f'fill="{t["a1"]}">ACTIVITY</text>'
        f'<text x="2" y="58" font-size="25" font-weight="800" letter-spacing="-.7" '
        f'fill="{t["text"]}">{title}</text>'
        f'<text class="m" x="{measure(title, "D", 800, 25, -0.7)+22:.0f}" y="57" font-size="11.5" '
        f'font-weight="500" fill="{t["dim"]}">{sub}</text>'
        f'<path d="M2 71H{w-2}" stroke="{t["line"]}"/>'
        f'<rect x="2" y="70" width="120" height="2" rx="1" fill="url(#sweep)">'
        f'<animate attributeName="x" values="2;{w-124};2" dur="9s" repeatCount="indefinite"/></rect>'
    )
    s.append("</svg>")
    return finish("".join(s))


# ------------------------------------------------------------------- 5 HEATMAP
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def heatmap(t):
    st = stats()
    weeks = st.get("contrib_weeks") or [[0] * 7 for _ in range(53)]
    starts = st.get("week_starts") or []
    peak = max(st.get("peak", 1), 1)
    pitch, cell = 16, 13
    x0, y0 = 56, 74
    w, h = W, 344

    def level(c):
        if c == 0:
            return 0
        r = c / peak
        return 1 if r <= .12 else 2 if r <= .3 else 3 if r <= .6 else 4

    OPS = [None, ".28", ".48", ".72", "1"]
    s = [svg_open(w, h, t, "", defs_common(t, w, h)), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(140, 20, 200, t["a3"], 70, 40, "22s"),
                              (880, 330, 200, t["a1"], -60, -40, "26s")]))
    s.append(
        f'<text class="m" x="30" y="38" font-size="10.5" font-weight="700" letter-spacing="2" '
        f'fill="{t["dim"]}">CONTRIBUTION CALENDAR</text>'
        f'<text class="m" x="{w-30}" y="38" font-size="12" font-weight="700" fill="{t["text"]}" '
        f'text-anchor="end">{st.get("contrib_total", 0):,} contributions</text>'
    )
    seen = set()
    for i, ds in enumerate(starts):
        try:
            _, m, d = (int(v) for v in ds.split("-"))
        except Exception:
            continue
        if m not in seen and d <= 7:
            seen.add(m)
            s.append(f'<text class="m" x="{x0+i*pitch}" y="{y0-10}" font-size="10" '
                     f'font-weight="500" fill="{t["dim"]}">{MONTHS[m-1]}</text>')
    for i, lbl in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        s.append(f'<text class="m" x="{x0-10}" y="{y0+i*pitch+10}" font-size="9.5" '
                 f'font-weight="500" fill="{t["dim"]}" text-anchor="end">{lbl}</text>')
    for wi, wk in enumerate(weeks):
        for di, c in enumerate(wk):
            lv = level(c)
            s.append(
                f'<rect x="{x0+wi*pitch}" y="{y0+di*pitch}" width="{cell}" height="{cell}" rx="3" '
                f'fill="{t["panelHi"] if lv == 0 else t["a3"]}" '
                f'fill-opacity="{"1" if lv == 0 else OPS[lv]}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur=".5s" '
                f'begin="{0.15+wi*0.018+di*0.012:.3f}s" fill="freeze"/></rect>'
            )
    ly = y0 + 7 * pitch + 28
    lx = w - 30 - (5 * 17 + 76)
    s.append(f'<text class="m" x="{lx}" y="{ly+10}" font-size="10" font-weight="500" '
             f'fill="{t["dim"]}">Less</text>')
    for i in range(5):
        s.append(f'<rect x="{lx+36+i*17}" y="{ly}" width="13" height="13" rx="3" '
                 f'fill="{t["panelHi"] if i == 0 else t["a3"]}" '
                 f'fill-opacity="{"1" if i == 0 else OPS[i]}"/>')
    s.append(f'<text class="m" x="{lx+36+5*17+6}" y="{ly+10}" font-size="10" font-weight="500" '
             f'fill="{t["dim"]}">More</text>')

    sy = ly + 40
    s.append(f'<path d="M30 {sy}H{w-30}" stroke="{t["line"]}"/>')
    priv_pct = round(st.get("contrib_private", 0) / max(st.get("contrib_total", 1), 1) * 100)
    strip = [(f'{st.get("streak_current", 0)}', "DAY STREAK", "a4"),
             (f'{st.get("active_days", 0)}', f'ACTIVE DAYS OF {st.get("total_days", 0)}', "a3"),
             (f'{st.get("best_day_count", 0)}', "BUSIEST DAY", "a1"),
             (f'{priv_pct}%', "IN PRIVATE REPOS", "a2")]
    for i, (big, label, key) in enumerate(strip):
        sx = 30 + i * 236
        s.append(
            f'<text x="{sx}" y="{sy+42}" font-size="30" font-weight="800" letter-spacing="-1.2" '
            f'fill="{t["text"]}">{big}</text>'
            f'<text class="m" x="{sx}" y="{sy+62}" font-size="10" font-weight="700" '
            f'letter-spacing="1.5" fill="{t[key]}">{label}</text>'
        )
    s.append("</g></svg>")
    return finish("".join(s))


# -------------------------------------------------------------------- 6 FOOTER
def footer(t):
    w, h = W, 236
    defs = defs_common(t, w, h, extra=(
        '<linearGradient id="fg" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{t["a1"]}"/><stop offset=".5" stop-color="{t["a2"]}"/>'
        f'<stop offset="1" stop-color="{t["a3"]}"/></linearGradient>'))
    s = [svg_open(w, h, t, "", defs), frame(t, w, h), '<g clip-path="url(#clip)">']
    s.append(aurora(w, h, t, [(200, 220, 220, t["a1"], 70, -40, "19s"),
                              (800, 20, 220, t["a2"], -60, 50, "23s")]))
    s.append(grid(w, h, t, 34, 0.9, "36s"))
    wave = ("M0 160 C 90 130 150 190 250 160 S 410 130 500 160 S 660 190 750 160 "
            "S 910 130 1000 160")
    s.append(
        f'<path d="{wave}" stroke="url(#fg)" stroke-width="2" fill="none" opacity=".26"/>'
        f'<path d="{wave}" stroke="url(#fg)" stroke-width="2.5" fill="none" opacity=".95" '
        f'stroke-linecap="round" stroke-dasharray="150 1250" stroke-dashoffset="150">'
        f'<animate attributeName="stroke-dashoffset" values="150;-1250" dur="7s" '
        f'repeatCount="indefinite"/></path>'
        f'<path d="{wave}" stroke="{t["line"]}" stroke-width="1.5" fill="none" opacity=".5" '
        f'transform="translate(0 16)"/>'
    )
    s.append(
        f'<text x="{w/2}" y="88" font-size="38" font-weight="800" letter-spacing="-1.5" '
        f'fill="{t["text"]}" text-anchor="middle">Let&#8217;s build something native.</text>'
        f'<text x="{w/2}" y="120" font-size="15" font-weight="500" fill="{t["muted"]}" '
        f'text-anchor="middle">Open to iOS roles and interesting problems.</text>'
    )
    s.append("</g></svg>")
    return finish("".join(s))


# --------------------------------------------------------------------- 7 LINKS
BADGES = [
    ("email", "EMAIL", "a1", "M3 5.2h14v9.6H3zM3 5.8l7 5 7-5"),
    ("instagram", "@BISCKOOT", "a2",
     "M5.6 3.4h8.8a2.2 2.2 0 012.2 2.2v8.8a2.2 2.2 0 01-2.2 2.2H5.6a2.2 2.2 0 01-2.2-2.2V5.6"
     "a2.2 2.2 0 012.2-2.2zM10 6.9a3.1 3.1 0 100 6.2 3.1 3.1 0 000-6.2zM14.35 5.55v.02"),
    ("repos", "REPOSITORIES", "a3",
     "M4.5 4h9a2 2 0 012 2v10H6.5a2 2 0 01-2-2zM4.5 14a2 2 0 012-2h9"),
]


def _badge(t, key, label, colkey, path):
    col = t[colkey]
    w, h = int(measure(label, "M", 700, 11, 1.6) + 78), 46
    s = [svg_open(w, h, t), "<defs>"
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
        f'<text class="m" x="48" y="{h/2+4}" font-size="11" font-weight="700" '
        f'letter-spacing="1.6" fill="{t["text"]}">{label}</text>'
        f'<circle cx="{w-16}" cy="{h/2}" r="2.5" fill="{col}">'
        f'<animate attributeName="opacity" values=".3;1;.3" dur="2.4s" '
        f'repeatCount="indefinite"/></circle>'
    )
    s.append("</svg>")
    return finish("".join(s))


# --------------------------------------------------------------------- REGISTRY
PANELS = {
    "hero": hero,
    "terminal": terminal,
    "marquee": marquee,
    "div-activity": div_activity,
    "heatmap": heatmap,
    "footer": footer,
}
for _k, _l, _c, _p in BADGES:
    PANELS[f"badge-{_k}"] = (lambda k, l, c, pa: (lambda t: _badge(t, k, l, c, pa)))(_k, _l, _c, _p)
