"""Core build helpers: theme tokens, font subsetting/embedding, text measurement."""
import base64, io, os, re, functools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "fonts")

# ---------------------------------------------------------------- theme tokens
# Dark base matches GitHub's dark canvas (#0d1117) and light matches #ffffff so
# the artwork melts into the page instead of sitting on it as a pasted rectangle.
DARK = dict(
    key="dark",
    base="#0D1117", panel="#11161F", panelHi="#161D28", inset="#0B0F16",
    line="#222C3A", lineHi="#31405280", grid="#FFFFFF",
    gridOp=".035", auroraOp=".55", shadowOp=".55",
    text="#E8EEF7", muted="#8FA0B6", dim="#5D6B7D",
    a1="#4EC9F5", a2="#8B7BFF", a3="#5CE7B0", a4="#FFB86B",
    glow="#4EC9F5", ok="#3FD68C",
)
LIGHT = dict(
    key="light",
    base="#FFFFFF", panel="#F5F8FB", panelHi="#FFFFFF", inset="#EEF3F8",
    line="#DCE4ED", lineHi="#C2CFDD80", grid="#0B1220",
    gridOp=".045", auroraOp=".30", shadowOp=".13",
    text="#0B1220", muted="#55637A", dim="#8593A6",
    a1="#0E86BD", a2="#6553D6", a3="#0E9E72", a4="#B4661A",
    glow="#0E86BD", ok="#12A05F",
)
THEMES = [DARK, LIGHT]


# ------------------------------------------------------------------ font logic
@functools.lru_cache(maxsize=None)
def _base_font(path):
    from fontTools.ttLib import TTFont
    return path  # loaded fresh each time; instancing mutates


@functools.lru_cache(maxsize=None)
def subset_b64(font_file, weight, chars):
    """Instance a variable font at `weight`, subset to `chars`, return base64 woff2."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools import subset

    font = TTFont(os.path.join(FONT_DIR, font_file))
    font = instancer.instantiateVariableFont(font, {"wght": weight}, inplace=True)

    opts = subset.Options()
    opts.layout_features = ["kern", "liga", "calt", "ccmp", "locl"]
    opts.drop_tables += ["DSIG"]
    opts.hinting = False
    opts.desubroutinize = True
    opts.name_IDs = []
    opts.notdef_outline = False
    opts.recalc_bounds = True

    s = subset.Subsetter(options=opts)
    s.populate(text="".join(sorted(set(chars))))
    s.subset(font)

    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


# Family alias -> (file, [weights])
FAMILIES = {"D": ("Inter.woff2", []), "M": ("JetBrainsMono.woff2", [])}

_TEXT_RE = re.compile(r"<(?:text|tspan)\b[^>]*>(.*?)</(?:text|tspan)>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def collect_chars(svg):
    out = set()
    for m in _TEXT_RE.findall(svg):
        out |= set(_TAG_RE.sub("", m))
    out |= set("0123456789")  # digits are cheap and often built dynamically
    out.discard("\n")
    return "".join(sorted(out))


# Two weights per family keeps every panel's embedded payload small. CSS font
# matching resolves any 600/700 request upward to 800, which is what the design
# wants anyway, so nothing needs a third cut.
W_DISPLAY = (800, 500)
W_MONO = (700, 500)


def snap(family, weight):
    """Match measurement to the weight the browser will actually render."""
    avail = W_DISPLAY if family == "D" else W_MONO
    lo, hi = min(avail), max(avail)
    return float(lo if weight <= lo else hi)


def font_faces(svg, weights_d=W_DISPLAY, weights_m=W_MONO):
    """Build @font-face CSS with per-file subsets covering only this SVG's glyphs."""
    chars = collect_chars(svg)
    if not chars.strip():
        return ""
    css = []
    for alias, file, weights in (
        ("D", "Inter.woff2", weights_d),
        ("M", "JetBrainsMono.woff2", weights_m),
    ):
        for w in weights:
            b64 = subset_b64(file, float(w), chars)
            css.append(
                f"@font-face{{font-family:'{alias}';font-style:normal;font-weight:{w};"
                f"font-display:block;src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
            )
    return "".join(css)


# ------------------------------------------------------------- text measurement
@functools.lru_cache(maxsize=None)
def _metrics(font_file, weight):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    font = TTFont(os.path.join(FONT_DIR, font_file))
    font = instancer.instantiateVariableFont(font, {"wght": weight}, inplace=True)
    upem = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    widths = {}
    for cp, name in cmap.items():
        widths[chr(cp)] = hmtx[name][0] / upem
    return widths


def measure(text, family="D", weight=600, size=16, tracking=0.0):
    """Advance width in px for `text`. `tracking` is extra px per character."""
    file = "Inter.woff2" if family == "D" else "JetBrainsMono.woff2"
    w = _metrics(file, snap(family, weight))
    total = sum(w.get(ch, w.get("n", 0.5)) for ch in text) * size
    return total + tracking * max(len(text) - 1, 0)


# ----------------------------------------------------------------- svg helpers
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def svg_open(w, h, t, extra_css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img">'
        f"{defs}<style>{{FONTS}}{BASE_CSS}{extra_css}</style>"
    )


BASE_CSS = (
    "text{font-family:'D',ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;"
    "white-space:pre;dominant-baseline:auto}"
    ".m{font-family:'M',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def finish(svg):
    """Inject the font faces sized to the glyphs actually present."""
    return svg.replace("{FONTS}", font_faces(svg))


def grid(w, h, t, step=32, op_mul=1.0, dur="26s"):
    """Slow-drifting background grid."""
    lines = []
    for x in range(0, w + step, step):
        lines.append(f"M{x} 0V{h}")
    for y in range(0, h + step, step):
        lines.append(f"M0 {y}H{w}")
    op = float(t["gridOp"]) * op_mul
    return (
        f'<g clip-path="url(#clip)"><g><animateTransform attributeName="transform" '
        f'type="translate" values="0 0;{step} {step};0 0" dur="{dur}" repeatCount="indefinite"/>'
        f'<path d="{"".join(lines)}" stroke="{t["grid"]}" stroke-opacity="{op:.4f}" '
        f'stroke-width="1" transform="translate(-{step} -{step})"/></g></g>'
    )
