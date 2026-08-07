"""Build a self-contained preview page: every SVG and font inlined as a data URI.

The chrome deliberately mimics GitHub's own canvas so the preview is honest about
what the README will look like once it is pushed.
"""
import base64, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, readme as rm

ROOT = core.ROOT
ASSETS = os.path.join(ROOT, "out", "assets")
ASCII = "".join(chr(c) for c in range(32, 127)) + "—·’“”→↗"


def b64_svg(name, theme):
    with open(os.path.join(ASSETS, f"{name}.{theme}.svg"), "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


def font_face(alias, file, weight):
    b64 = core.subset_b64(file, float(weight), ASCII)
    return (f"@font-face{{font-family:'{alias}';font-style:normal;font-weight:{weight};"
            f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


PANELS = rm.ORDER
BADGES = [(n, h, a) for n, h, a in rm.LINKS]


def main():
    faces = "".join([font_face("P", "Inter.woff2", 500), font_face("P", "Inter.woff2", 800),
                     font_face("PM", "JetBrainsMono.woff2", 500),
                     font_face("PM", "JetBrainsMono.woff2", 700)])

    srcs = {}
    for n in PANELS + [b[0] for b in BADGES]:
        srcs[n] = {th: b64_svg(n, th) for th in ("dark", "light")}

    import json
    data = json.dumps({"panels": PANELS, "badges": [[b[0], b[2]] for b in BADGES], "src": srcs})

    html = f"""<title>Amish Tufail GitHub Profile README</title>
<style>
{faces}
:root{{
  --ground:#ffffff; --chrome:#f6f8fa; --line:#d1d9e0; --ink:#1f2328;
  --muted:#59636e; --accent:#0E86BD; --shadow:0 1px 3px rgba(31,35,40,.08);
}}
@media (prefers-color-scheme: dark){{
  :root{{ --ground:#0d1117; --chrome:#161b22; --line:#30363d; --ink:#e6edf3;
    --muted:#8b949e; --accent:#4EC9F5; --shadow:0 1px 3px rgba(1,4,9,.5); }}
}}
:root[data-theme="dark"]{{ --ground:#0d1117; --chrome:#161b22; --line:#30363d; --ink:#e6edf3;
  --muted:#8b949e; --accent:#4EC9F5; --shadow:0 1px 3px rgba(1,4,9,.5); }}
:root[data-theme="light"]{{ --ground:#ffffff; --chrome:#f6f8fa; --line:#d1d9e0; --ink:#1f2328;
  --muted:#59636e; --accent:#0E86BD; --shadow:0 1px 3px rgba(31,35,40,.08); }}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);
  font:400 15px/1.6 'P',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;
  -webkit-font-smoothing:antialiased}}
.mono{{font-family:'PM',ui-monospace,SFMono-Regular,Menlo,monospace}}

.tool{{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:10px;flex-wrap:wrap;
  padding:10px 20px;background:var(--chrome);border-bottom:1px solid var(--line)}}
.tool .grow{{flex:1}}
.seg{{display:flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}}
.seg button{{border:0;background:transparent;color:var(--muted);padding:6px 13px;cursor:pointer;
  font:700 11px/1 'PM',monospace;letter-spacing:.09em}}
.seg button[aria-pressed="true"]{{background:var(--accent);color:#fff}}
.seg button:focus-visible{{outline:2px solid var(--accent);outline-offset:-2px}}
.lbl{{font:700 10px/1 'PM',monospace;letter-spacing:.14em;color:var(--muted);text-transform:uppercase}}

.stage{{padding:34px 20px 70px;display:flex;flex-direction:column;align-items:center;gap:34px}}
.card{{width:100%;background:var(--ground);border:1px solid var(--line);border-radius:6px;
  box-shadow:var(--shadow);padding:32px}}
.card img{{display:block;width:100%;max-width:100%}}
.rows{{display:flex;flex-direction:column;gap:14px}}
.rows .tight{{margin-bottom:-14px}}
.badges{{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;padding-top:4px}}
.badges img{{width:auto;height:44px}}

.notes{{width:100%;max-width:860px;display:flex;flex-direction:column;gap:14px}}
.notes h2{{font:800 20px/1.25 'P',sans-serif;margin:0;letter-spacing:-.01em;text-wrap:balance}}
.notes p{{margin:0;color:var(--muted);max-width:64ch}}
.notes ol{{margin:0;padding-left:20px;color:var(--muted);display:flex;flex-direction:column;gap:8px}}
.notes code{{font:500 13px/1.5 'PM',monospace;background:var(--chrome);border:1px solid var(--line);
  border-radius:5px;padding:1px 6px;color:var(--ink)}}
.files{{border:1px solid var(--line);border-radius:8px;overflow:hidden}}
.files div{{display:flex;gap:14px;padding:9px 14px;border-top:1px solid var(--line);
  font:500 12.5px/1.4 'PM',monospace}}
.files div:first-child{{border-top:0;background:var(--chrome);color:var(--muted);
  font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:10.5px}}
.files span:first-child{{flex:0 0 230px;color:var(--ink)}}
.files span:last-child{{color:var(--muted)}}
@media (max-width:700px){{
  .files span:first-child{{flex:0 0 140px}}
  .card{{padding:16px}}
}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>

<div class="tool">
  <span class="lbl">Theme</span>
  <div class="seg" id="theme">
    <button data-v="dark" aria-pressed="true">Dark</button>
    <button data-v="light" aria-pressed="false">Light</button>
  </div>
  <span class="lbl">Column</span>
  <div class="seg" id="width">
    <button data-v="830" aria-pressed="true">Profile</button>
    <button data-v="948" aria-pressed="false">Repo</button>
  </div>
  <span class="grow"></span>
  <div class="seg"><button id="replay" aria-pressed="false">Replay animations</button></div>
</div>

<div class="stage">
  <div class="card" id="card"><div class="rows" id="rows"></div></div>

  <div class="notes">
    <h2>What this is</h2>
    <p>Your profile README, rendered exactly as GitHub will show it. Every panel is an
    animated SVG with the fonts embedded inside the file, so it looks identical on any
    machine and loads nothing from a third-party service. Both themes are drawn separately
    and GitHub picks one automatically.</p>

    <h2>What gets committed</h2>
    <div class="files">
      <div><span>Path</span><span>Purpose</span></div>
      <div><span>README.md</span><span>Generated. Points at the SVGs.</span></div>
      <div><span>assets/*.svg</span><span>40 files, one light and one dark per panel.</span></div>
      <div><span>build/*.py</span><span>The generator. Edit copy here, not in the SVG.</span></div>
      <div><span>fonts/*.woff2</span><span>Inter and JetBrains Mono, both OFL licensed.</span></div>
      <div><span>stats.json</span><span>Live numbers pulled from the GitHub API.</span></div>
      <div><span>.github/workflows/</span><span>Daily job that refreshes the streak and calendar.</span></div>
    </div>

    <h2>Numbers on this page are real</h2>
    <p>The streak, the contribution calendar and the repository count come from the GitHub
    API, not from text I typed. A scheduled workflow regenerates them every morning, so the
    244-day streak stays correct on its own.</p>
  </div>
</div>

<script>
const D = {data};
const rows = document.getElementById("rows");
const card = document.getElementById("card");
const state = {{theme:"dark", width:"830"}};
const TIGHT = new Set(["div-context","div-build","div-principles","div-stack","div-signal","div-focus","heatmap"]);

function paint(){{
  document.documentElement.setAttribute("data-theme", state.theme);
  card.style.maxWidth = (parseInt(state.width,10) + 64) + "px";
  const bust = "";
  let h = "";
  for (const n of D.panels){{
    h += `<img class="${{TIGHT.has(n) ? "tight" : ""}}" alt="${{n}}" src="${{D.src[n][state.theme]}}">`;
  }}
  h += '<div class="badges">' + D.badges.map(([n,a]) =>
      `<img alt="${{a}}" src="${{D.src[n][state.theme]}}">`).join("") + "</div>";
  rows.innerHTML = h;
}}
function seg(id, key){{
  const el = document.getElementById(id);
  el.addEventListener("click", e => {{
    const b = e.target.closest("button"); if(!b) return;
    [...el.children].forEach(c => c.setAttribute("aria-pressed", String(c === b)));
    state[key] = b.dataset.v; paint();
  }});
}}
seg("theme","theme"); seg("width","width");
document.getElementById("replay").addEventListener("click", paint);
paint();
</script>
"""
    out = os.path.join(ROOT, "preview.html")
    open(out, "w").write(html)
    print(f"  preview.html  {os.path.getsize(out)/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
