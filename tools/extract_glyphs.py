"""One-time: outline the website's two typefaces into tools/glyphs.json + tools/glyphs_mono.json so
every SVG renders identically on GitHub (which loads no web fonts).

    python3 extract_glyphs.py InterTight[wght].ttf JetBrainsMono[wght].ttf

Inter Tight (OFL) at the weights the site uses: r 400, m 500, s 600, b 650 (headings).
JetBrains Mono (OFL): mr 400, mm 500, mb 600. Needs fontTools; nothing else in this folder does.
"""
import json
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

CHARS = [chr(c) for c in range(32, 127)] + [chr(c) for c in (0xB7, 0x2013, 0x2014, 0xD7, 0x2026, 0x2019, 0x2018, 0x201C, 0x201D, 0x2192, 0x2197, 0xE9)]


def outline(path, weights):
    out = {}
    for key, wght in weights.items():
        f = TTFont(path)
        if "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
        d = {"upm": upm, "g": {}}
        for ch in CHARS:
            gn = cmap.get(ord(ch))
            if gn is None:
                continue
            pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
            gs[gn].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))  # flip y
            d["g"][ch] = [f["hmtx"][gn][0], pen.getCommands()]
        out[key] = d
    return out


if __name__ == "__main__":
    sans, mono = sys.argv[1], sys.argv[2]
    json.dump(outline(sans, {"r": 400, "m": 500, "s": 600, "b": 650}), open("glyphs.json", "w"), separators=(",", ":"))
    json.dump(outline(mono, {"mr": 400, "mm": 500, "mb": 600}), open("glyphs_mono.json", "w"), separators=(",", ":"))
