import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, panels
from core import THEMES

OUT = os.path.join(core.ROOT, "assets")
os.makedirs(OUT, exist_ok=True)

only = set(sys.argv[1:]) or None
total = 0.0
for name, fn in panels.PANELS.items():
    if only and name not in only:
        continue
    for t in THEMES:
        svg = fn(t)
        p = os.path.join(OUT, f"{name}.{t['key']}.svg")
        open(p, "w").write(svg)
        kb = os.path.getsize(p) / 1024
        total += kb
        print(f"  {name+'.'+t['key']+'.svg':34} {kb:7.1f} KB")
print(f"  {'TOTAL':34} {total:7.1f} KB")
