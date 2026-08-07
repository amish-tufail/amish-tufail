"""Emit README.md. Every panel is a <picture> so GitHub picks the theme."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

ALT = {
    "hero": "Amish Tufail — iOS Engineer, Sydney Australia",
    "terminal": "whoami — Swift, SwiftUI, SwiftData, Vapor, Sydney",
    "marquee": "Tools and frameworks I work in",
    "div-build": "01 / Method — how I actually build",
    "method": "Frame, build, refine, review",
    "div-principles": "02 / Principles — what I optimise for",
    "principles": "Six engineering principles",
    "div-stack": "03 / Architecture — what the inside looks like",
    "architecture": "Presentation, domain, data, persistence layers",
    "div-signal": "04 / Signal — the receipts",
    "heatmap": "Contribution calendar, last 12 months",
    "streak": "Streak and consistency stats",
    "div-focus": "05 / Focus — where the hours go",
    "focus": "How a month splits across the stack",
    "footer": "Let's build something native",
}

ORDER = ["hero", "terminal", "marquee",
         "div-build", "method",
         "div-principles", "principles",
         "div-stack", "architecture",
         "div-signal", "heatmap", "streak",
         "div-focus", "focus",
         "footer"]

LINKS = [("badge-email", "mailto:amish.tufail2002@gmail.com", "Email"),
         ("badge-x", "https://x.com/bisckoot", "X"),
         ("badge-repos", "https://github.com/amish-tufail?tab=repositories", "Repositories")]


def pic(name, alt, width="100%"):
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="./assets/{name}.dark.svg">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="./assets/{name}.light.svg">\n'
        f'  <img alt="{alt}" src="./assets/{name}.dark.svg" width="{width}">\n'
        "</picture>"
    )


def main():
    out = ["<!-- This file is generated. Edit build/panels.py and run `make`, not this. -->", ""]
    for name in ORDER:
        out.append(pic(name, ALT.get(name, name)))
        out.append("")

    out.append("<p align=\"center\">")
    for name, href, alt in LINKS:
        out.append(f'  <a href="{href}">')
        out.append("    " + pic(name, alt, width="").replace("\n", "\n    ").replace(' width=""', ""))
        out.append("  </a>")
    out.append("</p>")
    out.append("")

    path = os.path.join(core.ROOT, "README.md")
    open(path, "w").write("\n".join(out))
    print(f"  README.md  {os.path.getsize(path)} bytes  ({len(ORDER)} panels)")


if __name__ == "__main__":
    main()
