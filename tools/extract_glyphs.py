"""One-time: outline Poppins into tools/glyphs.json so every SVG renders identically on GitHub
(which loads no web fonts). Needs fontTools; nothing else in this folder does."""
import json, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
W = {"r": "Regular", "m": "Medium", "s": "SemiBold", "b": "Bold"}
chars = [chr(c) for c in range(32, 127)] + list("·–—×")
out = {}
for k, name in W.items():
    f = TTFont(f"{sys.argv[1]}/Poppins-{name}.ttf")
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    d = {"upm": upm, "g": {}}
    for ch in chars:
        gn = cmap[ord(ch)]
        pen = SVGPathPen(gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
        gs[gn].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))  # flip y
        d["g"][ch] = [f["hmtx"][gn][0], pen.getCommands()]
    out[k] = d
json.dump(out, open("glyphs.json", "w"), separators=(",", ":"))
