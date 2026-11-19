"""nextgen: the animated "evidence console" components for the profile README.

GitHub shows README SVGs as <img>: no scripts and no web fonts, but CSS animation inside the SVG
runs. Every animated element is written so its BASE style is the finished frame; keyframes only
describe how it arrives. So prefers-reduced-motion (which switches animation off) and any renderer
that ignores animation both show the complete, readable image.

Each component takes a palette c (svgkit.LIGHT / svgkit.DARK) and a layout m: "d" desktop (840
wide) or "m" mobile (420 wide, served under 600px by a <picture> source).
"""
import os
import svgkit as K
from svgkit import text, width, wrap, _fmt

HERE = os.path.dirname(os.path.abspath(__file__))

# Signal colours, the website's roles: green = won (merged / accepted / recognised / PASS), amber = the one accent.
# The evidence console is a dark terminal in both themes, like the site's own panels.
_TERM = {'ok': '#3ccf91', 'warn': '#febd59', 'term': '#0a1119', 'termhair': '#1f2c3a', 'termink': '#f2f3f0',
         'termmute': '#76838f', 'termacc': '#febd59'}
SIG = {"dark": dict(_TERM, dot="#17222e"), "light": dict(_TERM, dot="#17222e")}  # panels are dark in both themes

BASE_CSS = (
    "@keyframes fi{from{opacity:0;transform:translateY(8px)}}"
    "@keyframes fo{from{opacity:0}}"
    "@keyframes dr{from{stroke-dashoffset:1}}"
    "@keyframes gx{from{transform:scaleX(.001)}}"
    "@keyframes gy{from{transform:scaleY(.001)}}"
    "@keyframes pp{from{opacity:0;transform:scale(.3)}}"
    "@keyframes pl{50%{opacity:.3}}"
    "@keyframes bl{50%{opacity:0}}"
    "@keyframes ring{0%{opacity:.7;transform:scale(1)}70%,100%{opacity:0;transform:scale(2.6)}}"
    ".fi{animation:fi .8s cubic-bezier(.2,.7,.2,1) both}"
    ".fo{animation:fo .9s ease both}"
    ".dr{stroke-dasharray:1;animation:dr 1.6s cubic-bezier(.6,0,.2,1) both}"
    ".gx{transform-box:fill-box;transform-origin:left center;animation:gx 1.2s cubic-bezier(.2,.7,.2,1) both}"
    ".gy{transform-box:fill-box;transform-origin:center bottom;animation:gy 1s cubic-bezier(.2,.7,.2,1) both}"
    ".pp{transform-box:fill-box;transform-origin:center;animation:pp .45s cubic-bezier(.3,1.5,.5,1) both}"
    ".pl{animation:pl 2.6s ease-in-out infinite}"
    ".bl{animation:bl 1.1s steps(1) infinite}"
    ".ring{transform-box:fill-box;transform-origin:center;animation:ring 3.2s ease-out infinite}"
    "@keyframes fl{to{stroke-dashoffset:-20}}"
    "@keyframes br{0%,100%{transform:scaleX(1)}50%{transform:scaleX(.82)}}"
    "@keyframes rs{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.55)}}"
    "@keyframes tw{0%,100%{opacity:1}50%{opacity:.35}}"
    "@keyframes sl{from{transform:translateX(0)}to{transform:translateX(var(--run))}}"
    ".fl{stroke-dasharray:4 6;animation:fl 1.6s linear infinite}"
    ".br{transform-box:fill-box;transform-origin:left center;animation:br 4.8s ease-in-out infinite}"
    ".rs{transform-box:fill-box;transform-origin:center bottom;animation:rs 3.6s ease-in-out infinite}"
    ".tw{animation:tw 5.5s ease-in-out infinite}"
    ".sl{animation:sl 7s ease-in-out infinite alternate}"
    "@keyframes tr{to{stroke-dashoffset:-1}}"
    "@keyframes icd{0%{stroke-dashoffset:1}35%,80%{stroke-dashoffset:0}100%{stroke-dashoffset:-1}}"
    "@keyframes wv{0%,100%{transform:scaleY(.25)}50%{transform:scaleY(1)}}"
    "@keyframes trr{to{stroke-dashoffset:1}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def svg(W, H, body, title, css=""):
    return K.svg(W, H, "<style>%s%s</style>%s" % (BASE_CSS, css, body), title)


def tracer(W, H, rx, c, seed, dash=.07, base=10.0):
    """A short gold light that runs round the panel border forever; seed staggers panels."""
    dur = base + (seed % 7) * 0.6
    dl = -((seed * 1.37) % dur)
    one = ('<rect x="1" y="1" width="%s" height="%s" rx="%s" fill="none" stroke="%s" stroke-width="%s" stroke-opacity="%s" pathLength="1" '
           'stroke-dasharray="%s %s" style="animation:tr %ss linear infinite;animation-delay:%ss"/>')
    return (one % (_fmt(W - 2), _fmt(H - 2), rx, c["brand"], 4.5, ".12", dash, _fmt(1 - dash), _fmt(dur), _fmt(dl)) +
            one % (_fmt(W - 2), _fmt(H - 2), rx, c["brand"], 1.3, ".85", dash, _fmt(1 - dash), _fmt(dur), _fmt(dl)))


def seedof(*parts):
    return sum(ord(ch) * (i + 1) for i, ch in enumerate("".join(str(p) for p in parts))) % 997


def icon_live(name, x, y, size, color, delay=0.0):
    """Icon strokes draw on, hold, draw off, forever. Base = fully drawn."""
    g = K.ICONS[name]
    for tag in ("<path ", "<circle ", "<rect "):
        g = g.replace(tag, tag + 'pathLength="1" ')
    k = size / 24.0
    return ('<g transform="translate(%s %s) scale(%s)" fill="none" stroke="%s" color="%s" stroke-width="1.9" '
            'stroke-linecap="round" stroke-linejoin="round" style="stroke-dasharray:1;animation:icd 5s ease-in-out infinite;'
            'animation-delay:%ss">%s</g>' % (_fmt(x), _fmt(y), _fmt(k), color, color, _fmt(delay), g))


def d(s):
    """animation-delay attribute."""
    return ' style="animation-delay:%ss"' % _fmt(s)


def S(c):
    return SIG[c["mode"]]


def mono(x, y, s, size, fill, anchor="start", bold=False, track=0.0, w=None):
    return text(x, y, s, w or ("mb" if bold else "mr"), size, fill, anchor, track)


def fit(s, w, size, maxw, track=0.0):
    """Clip a single line to maxw with an ellipsis (never overflow the box)."""
    if width(s, w, size, track) <= maxw:
        return s
    while s and width(s + "\u2026", w, size, track) > maxw:
        s = s[:-1]
    return s.rstrip(" ,;:-") + "\u2026"


def label(x, y, s, c, size=11, color=None, anchor="start"):
    """The site's mono category label: uppercase, tracked .12em."""
    return mono(x, y, s.upper(), size, color or c["mute"], anchor, track=size * 0.12, w="mm")


def arrow(x, y, color, size=16):
    """Arrow-out mark for link cards (top right)."""
    k = size / 16.0
    return ('<g transform="translate(%s %s) scale(%s)" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M3 13 L13 3 M5 3 H13 V11"/></g>' % (_fmt(x), _fmt(y), _fmt(k), color))


def grid_bg(W, H, c, rx=22, step=22):
    dot = S(c)["dot"]
    return (
        '<defs><pattern id="gd" width="%d" height="%d" patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r="1" fill="%s"/></pattern>'
        '<clipPath id="cl"><rect width="%d" height="%d" rx="%d"/></clipPath>'
        '<linearGradient id="sc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="%s" stop-opacity=".09"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="gl"><stop offset="0" stop-color="%s" stop-opacity="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
        '</defs>'
        '<rect x=".5" y=".5" width="%d" height="%d" rx="%d" fill="%s" stroke="%s"/>'
        '<g clip-path="url(#cl)"><rect width="%d" height="%d" fill="url(#gd)" opacity=".9"/>'
        % (step, step, dot, W, H, rx, c["brand"], c["brand"], c["brand"], c["brand"],
           ".10", c["brand"], W - 1, H - 1, rx, c["ground"], c["hair2"], W, H)
    )


# ------------------------------------------------------------------------------------- hero
# The website's hero line, word for word (johnbjoseph-cybersec.github.io, 2026-11-19).
HERO_LINE = [("Your AI agents act in seconds.", "ink"), ("Your audit evidence shouldn't take four weeks.", "acc")]
HERO_SUB = ("I build both halves: AI security that decides what an agent is allowed to do before it does it, "
            "and the compliance software that proves your controls actually work.")
# (verb, subject, ref, status). Clause numbers are real: ISO/IEC 42001 Annex A A.6.2.6 (AI system
# operation and monitoring), NIST AI RMF MEASURE 2.7 (security and resilience), EU AI Act Art. 15
# (accuracy, robustness and cybersecurity). The hash is illustrative; the window says "example run".
CONSOLE = [
    ("map", "ISO/IEC 42001", "A.6.2.6", None),
    ("map", "NIST AI RMF", "MEASURE 2.7", None),
    ("map", "EU AI Act", "Art. 15", None),
    ("eval", "inspect log", "sha256:9f3c..a71e", None),
    ("test", "tool-call authz", "", "PASS"),
    ("test", "ML-KEM-768 kex", "", "PASS"),
]
CYCLE = 16
THESIS = "The question behind everything I build: what control proves this is safe, and what evidence shows it is working?"


def console(x, y, w, fs, c):
    s = S(c)
    cw = fs * 0.6                       # JetBrains Mono advance = 600/1000 em
    lh = round(fs * 1.75)
    h = 46 + lh * (len(CONSOLE) + 3) + 14
    b = ['<g class="fi"%s>' % d(0.15)]
    b.append('<rect x="%s" y="%s" width="%s" height="%s" rx="12" fill="%s" stroke="%s"/>' % (x + .5, y + .5, w - 1, h - 1, s["term"], s["termhair"]))
    b.append('<rect x="%s" y="%s" width="%s" height="%s" rx="12" fill="none" stroke="%s" stroke-width="1.4" pathLength="1" '
             'stroke-dasharray=".09 .91" style="animation:trr 7s linear infinite"/>' % (x + .5, y + .5, w - 1, h - 1, s["termacc"]))
    b.append('<path d="M%s %s H%s" stroke="%s"/>' % (x, y + 34.5, x + w, s["termhair"]))
    b.append(mono(x + 16, y + 22, "evidence-engine", fs - 1, s["termink"], bold=True))
    b.append(mono(x + w - 16, y + 22, "example run", fs - 1.5, s["termmute"], anchor="end"))
    b.append('<circle class="pl" cx="%s" cy="%s" r="3.5" fill="%s"/>' % (_fmt(x + w - 16 - width("example run", "mr", fs - 1.5) - 12), y + 18, s["ok"]))
    b.append("</g>")
    ty = y + 34 + lh + 4
    cmd = 'prove --claim "agent tool calls are safe"'
    b.append(mono(x + 16, ty, "$", fs, s["termacc"], bold=True))
    b.append(mono(x + 16 + cw * 2, ty, cmd, fs, s["termink"]))
    # The run replays every CYCLE s. Each element gets its own keyframes so all of them hold together
    # and clear together. Base styles are the finished frame (reduced motion = complete still).
    n = len(cmd)
    C = CYCLE
    pc = lambda t: _fmt(100.0 * t / C)
    css = (".ty{transform-box:fill-box;transform-origin:right center;transform:scaleX(0);animation:ty %ss linear infinite}"
           "@keyframes ty{0%%,%s%%{transform:scaleX(1);animation-timing-function:steps(%d)}%s%%,93%%{transform:scaleX(0)}96%%,100%%{transform:scaleX(1)}}"
           % (C, pc(0.6), n, pc(2.1)))
    b.append('<rect class="ty" x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (_fmt(x + 16 + cw * 2 - 1), ty - fs, _fmt(cw * n + 3), fs + 6, s["term"]))
    kn = [0]

    def show(t):
        kn[0] += 1
        k = "c%d" % kn[0]
        css_k = ("@keyframes %s{0%%,%s%%{opacity:0;transform:translateY(5px)}%s%%,92%%{opacity:1;transform:none}95%%,100%%{opacity:0}}"
                 % (k, pc(t), pc(t + 0.35)))
        return ' style="animation:%s %ss cubic-bezier(.2,.7,.2,1) infinite"' % (k, C), css_k

    t0 = 2.3
    for i, (verb, subj, ref, st) in enumerate(CONSOLE):
        ly = ty + lh * (i + 1)
        st_attr, k = show(t0 + i * 0.32)
        css += k
        b.append('<g%s>' % st_attr)
        b.append(mono(x + 16 + cw * 2, ly, verb, fs, s["termacc"]))
        b.append(mono(x + 16 + cw * 8, ly, subj, fs, s["termink"]))
        if ref:
            b.append(mono(x + w - 16, ly, ref, fs, s["termmute"], anchor="end"))
        if st:
            b.append(mono(x + w - 16, ly, st, fs, s["ok"], anchor="end", bold=True))
        b.append("</g>")
    ly = ty + lh * (len(CONSOLE) + 1) + 2
    tend = t0 + len(CONSOLE) * 0.32 + 0.2
    st_attr, k = show(tend)
    css += k
    b.append('<path%s d="M%s %s H%s" stroke="%s" stroke-dasharray="3 4"/>' % (st_attr, x + 16, ly - fs - 2, x + w - 16, s["termhair"]))
    st_attr, k = show(tend + 0.25)
    css += k
    b.append('<g%s>' % st_attr)
    b.append(mono(x + 16, ly + 6, "evidence", fs, s["termmute"]))
    b.append(mono(x + 16 + cw * 9, ly + 6, "6/6 attached", fs, s["ok"], bold=True))
    end = x + 16 + cw * 22
    b.append(mono(end, ly + 6, "OSCAL", fs, s["termink"]))
    b.append('<rect class="bl" x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (_fmt(end + cw * 6), ly + 6 - fs * 0.78, _fmt(cw * 0.9), _fmt(fs * 0.95), s["termacc"]))
    b.append("</g>")
    return "".join(b), h, css


def rich_wrap(segs, w, size, maxw, track=0.0):
    """Word-wrap coloured segments [(text, colour key)] into lines of [(word, key)]."""
    words = [(wd, k) for t, k in segs for wd in t.split()]
    lines, cur = [], []
    for wd in words:
        if cur and width(" ".join(x for x, _ in cur + [wd]), w, size, track) > maxw:
            lines.append(cur)
            cur = [wd]
        else:
            cur.append(wd)
    if cur:
        lines.append(cur)
    return lines


def rich_line(x, y, words, w, size, colors, track=0.0):
    out, cx = [], x
    sp = width(" ", w, size, track) + 2 * track
    for wd, k in words:
        out.append(text(cx, y, wd, w, size, colors[k], track=track))
        cx += width(wd, w, size, track) + sp
    return "".join(out)


def proof(x, y, W, items, c, m, css_acc):
    """The site's proof strip: number (mono 600, '+' in amber), label, source. items: (value, label, source)."""
    cols = 4 if m == "d" else 2
    cw = W / float(cols)
    rh = 128 if m == "d" else 134
    vs = 30 if m == "d" else 26
    ls = 13 if m == "d" else 12
    b, css = [], ""
    b.append('<path d="M%s %s H%s" stroke="%s"/>' % (_fmt(x), _fmt(y + .5), _fmt(x + W), c["hair2"]))
    for i, (val, lab, src) in enumerate(items):
        col, row = i % cols, i // cols
        cx = x + col * cw + (0 if col == 0 else 18)
        cy = y + row * rh
        if col:
            b.append('<path d="M%s %s V%s" stroke="%s"/>' % (_fmt(x + col * cw + .5), _fmt(cy + 16), _fmt(cy + rh - 12), c["hair"]))
        if row:
            b.append('<path d="M%s %s H%s" stroke="%s"/>' % (_fmt(x + col * cw), _fmt(cy + .5), _fmt(x + (col + 1) * cw), c["hair"]))
        b.append('<g class="fi"%s>' % d(0.2 + i * 0.12))
        ob, ocss = odometer(cx, cy + 22 + vs * 0.74, val, vs, c["ink"], "pf%s%d" % (m, i), 0.2 + i * 0.25, w="mb", acc=css_acc)
        b.append(ob)
        css += ocss
        maxw = cw - (18 if col == 0 else 36)
        ll = wrap(lab, "r", ls, maxw, 2)
        for j, ln in enumerate(ll):
            b.append(text(cx, cy + 22 + vs + 16 + j * (ls + 5), ln, "r", ls, c["body"]))
        sw_ = cw - (8 if col == 0 else 22)
        sl = [src] if width(src, "mr", 9) <= sw_ else [x.strip() for x in src.split("\u00b7")]
        for j, ln in enumerate(sl):
            b.append(mono(cx, cy + rh - 16 - (len(sl) - 1 - j) * 13, fit(ln, "mr", 9, sw_), 9, c["mute"]))
        b.append("</g>")
    rows = (len(items) + cols - 1) // cols
    return "".join(b), rows * rh, css


def hero(c, proof_items, m="d"):
    s = S(c)
    colors = {"ink": c["ink"], "acc": c["accent"]}
    if m == "d":
        W, P = 840, 40
        ns, hs, hl, ss, sl = 46, 24, 29, 14.5, 23
        colw = 404
    else:
        W, P = 420, 22
        ns, hs, hl, ss, sl = 34, 20, 25, 13.5, 21
        colw = W - 2 * P
    parts = []
    y = 54 if m == "d" else 44
    parts.append('<g class="fi">')
    parts.append('<circle class="pl" cx="%s" cy="%s" r="4" fill="%s"/>' % (P + 4, y - 4, c["ok"]))
    parts.append(mono(P + 16, y, "~/john-b-joseph", 12 if m == "d" else 11, c["accent"]))
    parts.append("</g>")
    y += 14 + ns * 0.73
    parts.append('<g class="fi"%s>' % d(0.1))
    parts.append(text(P - K._left_bearing("b", "J", ns), y, "John B Joseph", "b", ns, c["ink"], track=-0.035 * ns))
    parts.append("</g>")
    y += 28 if m == "d" else 24
    es = 11 if m == "d" else 10
    et = es * 0.14
    e1, e2 = "CO-FOUNDER & CPTO", "PURPLECOP SECURITY"
    parts.append('<g class="fi"%s>' % d(0.2))
    parts.append(mono(P, y, e1, es, c["body"], track=et, w="mm"))
    x2 = P + width(e1, "mm", es, et) + et
    parts.append(mono(x2, y, " / ", es, c["accent"], track=et, w="mm"))
    parts.append(mono(x2 + width(" / ", "mm", es, et) + et, y, e2, es, c["body"], track=et, w="mm"))
    parts.append("</g>")
    y += 22 + hs * 0.75
    lines = rich_wrap(HERO_LINE, "b", hs, colw, -0.035 * hs)
    parts.append('<g class="fi"%s>' % d(0.3))
    for i, ln in enumerate(lines):
        parts.append(rich_line(P, y + i * hl, ln, "b", hs, colors, -0.035 * hs))
    parts.append("</g>")
    y += (len(lines) - 1) * hl + 14 + sl
    sub = wrap(HERO_SUB, "r", ss, colw, 5)
    parts.append('<g class="fi"%s>' % d(0.45))
    for i, ln in enumerate(sub):
        parts.append(text(P, y + i * sl, ln, "r", ss, c["body"]))
    parts.append("</g>")
    y += (len(sub) - 1) * sl
    css = ""
    if m == "d":
        cb, ch, ccss = console(472, 40, 328, 11.5, c)
        top = max(y + 10, 40 + ch) + 34
    else:
        cb, ch, ccss = console(P, y + 26, W - 2 * P, 10.5, c)
        top = y + 26 + ch + 30
    parts.append(cb)
    css += ccss
    pb, ph, pcss = proof(P, top, W - 2 * P, proof_items, c, m, c["accent"])
    parts.append('<path class="dr gx" pathLength="1" d="M%d %s H%d" stroke="%s" stroke-width="2"/>' % (P, _fmt(top + .5), P + 56, c["brand"]))
    parts.append(pb)
    css += pcss
    H = int(top + ph + 6)
    bg = grid_bg(W, H, c)
    glow = '<circle cx="%s" cy="%s" r="%s" fill="url(#gl)"/>' % ((250, 130, 330) if m == "d" else (140, 110, 230))
    pk = ['<defs><linearGradient id="pkg" x1="0" x2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
          '<stop offset="1" stop-color="%s" stop-opacity=".9"/></linearGradient></defs>' % (c["brand"], c["brand"])]
    # Packets run only on grid rows that cross empty space (above the name), never behind text.
    rows = [r for r in range(1, H // 22 + 1) if r * 22 + 1 <= (30 if m == "d" else 22)]
    for i, row in enumerate(rows):
        yy = row * 22 + 1
        dur = 7 + (i * 2.3) % 6
        css += "@keyframes pk%d{from{transform:translateX(0)}to{transform:translateX(%dpx)}}" % (i, W + 80)
        pk.append('<g style="animation:pk%d %ss linear infinite;animation-delay:-%ss" opacity=".75">'
                  '<rect x="-60" y="%s" width="48" height="1.4" fill="url(#pkg)"/><circle cx="-11" cy="%s" r="2" fill="%s"/></g>'
                  % (i, _fmt(dur), _fmt(i * 1.7), _fmt(yy - 0.7), yy, c["brand"]))
    trace = tracer(W, H, 22, c, seedof("hero", m), dash=.1, base=10.0)
    body = bg + glow + "".join(pk) + "</g>" + trace + "".join(parts)
    alt = ("John B Joseph. Co-founder and CPTO, Purplecop Security. " + " ".join(t for t, _ in HERO_LINE) + " " + HERO_SUB +
           " " + ". ".join("%s %s (%s)" % it for it in proof_items) + ".")
    return svg(W, H, body, alt, css)


# ------------------------------------------------------------------------------------ stats
def stats(items, c, m="d"):
    """items: (value, label, itemization). Itemization is shown so every derived number can be
    checked by hand."""
    W = 840 if m == "d" else 420
    cols = 4 if m == "d" else 2
    cw = W / cols
    rh = 118
    css = ""
    rows = (len(items) + cols - 1) // cols
    H = rh * rows
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
    for i in range(1, cols):
        b.append('<path d="M%s 18 V%d" stroke="%s"/>' % (_fmt(cw * i), H - 18, c["hair"]))
    for r in range(1, rows):
        b.append('<path d="M18 %d H%d" stroke="%s"/>' % (rh * r, W - 18, c["hair"]))
    vs = 36 if m == "d" else 30
    for i, (val, lab, sub) in enumerate(items):
        x = (i % cols) * cw + (24 if m == "d" else 18)
        y = (i // cols) * rh
        b.append('<g class="fi"%s>' % d(0.1 + i * 0.12))
        ob, ocss = odometer(x, y + 52, val, vs, c["ink"], "o%s%d" % (m, i), 0.15 + i * 0.25, w="mb", acc=c["accent"])
        b.append(ob)
        css += ocss
        b.append(text(x, y + 76, lab, "m", 13.5 if m == "d" else 12.5, c["body"]))
        b.append(mono(x, y + 96, sub, 10.5 if m == "d" else 9.5, c["mute"]))
        b.append("</g>")
        assert width(sub, "mr", 10.5 if m == "d" else 9.5) < cw - 30, sub
        assert width(lab, "m", 13.5 if m == "d" else 12.5) < cw - 30, lab
        b.append('<rect class="gx"%s x="%s" y="%d" width="%s" height="2" rx="1" fill="%s"/>' % (
            d(0.4 + i * 0.12), _fmt(x), y + rh - 12, 40, c["brand"]))
        b.append('<rect class="sl" x="%s" y="%d" width="10" height="2" rx="1" fill="%s" opacity=".55" style="--run:%dpx;animation-duration:3.2s;animation-delay:%ss"/>' % (
            _fmt(x + 40), y + rh - 12, c["brand"], int(cw - 90), _fmt(-i * 0.8)))
    b.append(tracer(W, H, 16, c, seedof("stats", m)))
    return svg(W, H, "".join(b), ". ".join("%s %s (%s)" % it for it in items), css)


ODO = 14  # seconds per roll cycle


def odometer(x, base, val, size, fill, uid, delay, w="mb", acc=None):
    """Number whose digits roll into place like a counter, hold, then roll again. Base style =
    the final number. Non-digits (, + .) stay still; '+' takes the accent, as on the site."""
    lh = size * 1.18
    out, css, cx = [], "", x
    track = -0.04 * size
    top = base - size * 0.80
    out.append('<defs><clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath></defs>' % (
        uid, _fmt(x - 4), _fmt(top), _fmt(width(val, w, size, track) + 12), _fmt(size * 0.98)))
    out.append('<g clip-path="url(#%s)">' % uid)
    for j, ch in enumerate(val):
        adv = width(ch, w, size) + track
        if ch.isdigit():
            dgt = int(ch)
            col = []
            for k in range(20):
                g = str(k % 10)
                col.append(text(cx + (adv - track - width(g, w, size)) / 2, base + k * lh, g, w, size, fill))
            fin = -(10 + dgt) * lh
            name = "%s%d" % (uid, j)
            t0 = delay + j * 0.12
            css += ("@keyframes %s{0%%,%s%%{transform:translateY(0);opacity:0}%s%%{opacity:1}%s%%,90%%{transform:translateY(%spx);opacity:1}"
                    "96%%,100%%{transform:translateY(%spx);opacity:0}}"
                    % (name, _fmt(100 * t0 / ODO), _fmt(100 * (t0 + 0.2) / ODO), _fmt(100 * (t0 + 1.6) / ODO), _fmt(fin), _fmt(fin)))
            out.append('<g style="transform:translateY(%spx);animation:%s %ss cubic-bezier(.2,.8,.2,1) infinite">%s</g>' % (
                _fmt(fin), name, ODO, "".join(col)))
        else:
            out.append(text(cx, base, ch, w, size, acc if (acc and ch == "+") else fill))
        cx += adv
    out.append("</g>")
    return "".join(out), css


# ---------------------------------------------------------------------------------- section
def section(path, eyebrow, title, caption, c, m="d"):
    """The site's section head: amber ~/slug + mono eyebrow, the heading (Inter Tight 650, -0.035em),
    then a hairline with a 56px amber bar. Transparent, so it sits on GitHub's own page colour."""
    W = 840 if m == "d" else 420
    ts = 28 if m == "d" else 22
    tr = -0.035 * ts
    lh = round(ts * 1.12)
    b = [mono(0, 16, path, 12, c["page_acc"], w="mm")]
    ex = width(path, "mm", 12) + 12
    if eyebrow:
        b.append(mono(ex, 16, eyebrow.upper(), 11, c["page_mute"], track=11 * 0.14, w="mm"))
    lines = wrap(title, "b", ts, W, 3)
    y = 34 + ts * 0.74
    b.append('<g class="fi">%s</g>' % "".join(text(0, y + i * lh, ln, "b", ts, c["page_ink"], track=tr) for i, ln in enumerate(lines)))
    y += (len(lines) - 1) * lh
    if caption:
        cs = 11.5 if m == "d" else 10.5
        if m == "d" and eyebrow and width(caption, "mr", cs) + ex + width(eyebrow.upper(), "mm", 11, 1.54) + 40 < W:
            b.append(mono(W, 16, caption, cs, c["page_mute"], anchor="end"))
        else:
            y += 26
            b.append(mono(0, y, caption, cs, c["page_mute"]))
    H = int(y + 24)
    b.append('<path d="M0 %s H%d" stroke="%s"/>' % (_fmt(H - 1.5), W, c["page_hair"]))
    b.append('<rect class="gx" x="0" y="%d" width="56" height="2" fill="%s"/>' % (H - 2, c["page_bar"]))
    b.append('<rect class="sl" x="56" y="%s" width="28" height="1.5" rx=".75" fill="%s" opacity=".7" style="--run:%dpx"/>' % (_fmt(H - 2), c["page_bar"], W - 84))
    alt = "%s %s. %s" % (eyebrow or "", title, caption or "")
    return svg(W, H, "".join(b), alt.strip())


# ---------------------------------------------------------------------------------- motifs
def motif(kind, x, y, c):
    """A small animated mark, 104 x 40, unique to each project."""
    a = c["accent"]
    s = S(c)
    b = []
    if kind == "crosswalk":
        L = [(x + 6, y + 6 + 14 * i) for i in range(3)]
        R = [(x + 98, y + 2 + 12 * i) for i in range(4)]
        links = [(0, 0), (0, 2), (1, 1), (1, 3), (2, 2), (2, 3)]
        for k, (i, j) in enumerate(links):
            (x1, y1), (x2, y2) = L[i], R[j]
            b.append('<path d="M%s %s C%s %s %s %s %s %s" fill="none" stroke="%s" stroke-width="1" opacity=".35"/>' % (
                x1, y1, x1 + 46, y1, x2 - 46, y2, x2, y2, a))
            b.append('<path class="fl"%s d="M%s %s C%s %s %s %s %s %s" fill="none" stroke="%s" stroke-width="1.6"/>' % (
                d(-k * 0.27), x1, y1, x1 + 46, y1, x2 - 46, y2, x2, y2, a))
        for (px, py) in L:
            b.append('<circle cx="%s" cy="%s" r="3.5" fill="%s"/>' % (px, py, c["ink"]))
        for k, (px, py) in enumerate(R):
            b.append('<circle class="pl"%s cx="%s" cy="%s" r="3" fill="%s"/>' % (d(k * 0.6), px, py, a))
    elif kind == "oscal":
        for i, (lab, w) in enumerate([("L", 34), ("M", 60), ("H", 86)]):
            yy = y + 4 + i * 13
            b.append(mono(x, yy + 7, lab, 9.5, c["mute"], bold=True))
            b.append('<rect x="%s" y="%s" width="86" height="7" rx="3.5" fill="%s"/>' % (x + 14, yy, c["chipbg"]))
            b.append('<rect class="br"%s x="%s" y="%s" width="%s" height="7" rx="3.5" fill="%s"/>' % (d(-i * 1.4), x + 14, yy, w, a))
    elif kind == "pipeline":
        pts = [x + 8, x + 52, x + 96]
        yy = y + 20
        b.append('<path d="M%s %s H%s" stroke="%s" stroke-width="1.5" stroke-dasharray="3 4"/>' % (pts[0], yy, pts[2], c["hair"]))
        for i, px in enumerate(pts):
            b.append('<rect x="%s" y="%s" width="14" height="14" rx="%s" fill="%s" stroke="%s"/>' % (
                px - 7, yy - 7, 7 if i == 1 else 3, c["panel"], a if i < 2 else s["ok"]))
        b.append('<circle cx="%s" cy="%s" r="3.2" fill="%s" style="animation:pv 2.8s cubic-bezier(.5,0,.5,1) infinite"/>' % (pts[0], yy, a))
        b.append('<style>@keyframes pv{0%%{transform:translateX(0);opacity:0}10%%{opacity:1}90%%{opacity:1}100%%{transform:translateX(%dpx);opacity:0}}</style>' % (pts[2] - pts[0]))
        for lab, px in zip(["log", "hash", "oscal"], pts):
            b.append(mono(px, yy + 22, lab, 8.5, c["mute"], anchor="middle"))
    elif kind == "ledger":
        hs = [8, 12, 15, 19, 24, 28, 33, 38]
        for i, h in enumerate(hs):
            b.append('<rect class="rs"%s x="%s" y="%s" width="9" height="%s" rx="2" fill="%s" opacity="%s"/>' % (
                d(-i * 0.3), x + 6 + i * 12.5, y + 40 - h, h, a, _fmt(0.45 + i * 0.07)))
    elif kind == "sheets":
        for i in range(4):
            sx = x + 4 + i * 25
            b.append('<rect x="%s" y="%s" width="20" height="28" rx="3" fill="%s" stroke="%s"/>' % (sx, y + 6, c["panel"], c["hair"]))
            for r in range(4):
                b.append('<rect class="tw"%s x="%s" y="%s" width="%s" height="2.4" rx="1.2" fill="%s"/>' % (
                    d(-(i * 0.9 + r * 0.45)), sx + 4, y + 12 + r * 5, 12 if r % 2 else 9, a if r == 0 else c["mute"]))
    return "".join(b)


# ----------------------------------------------------------------------------------- cards
CARD_W, CARD_H = 414, 236   # two per row: 414 + 12 + 414 = 840, the full column
ROW_GAP = 12


def nest(W, H, kids, title):
    """One row/grid SVG holding several finished panel SVGs (nested <svg x y>), so a row spans the
    README column edge to edge with exact gaps on every screen."""
    body = "".join(k.replace("<svg ", '<svg x="%s" y="%s" ' % (_fmt(x), _fmt(y)), 1) for k, x, y in kids)
    return K.svg(W, H, body, title, defs=False)


def grid(panels, c, m, cols=2, gap=ROW_GAP, title=""):
    """panels: finished SVG strings of width CARD_W and equal height. Desktop: cols across; mobile: stacked."""
    import re as _re
    hs = [float(_re.search(r'height="([0-9.]+)"', p_).group(1)) for p_ in panels]
    cols = cols if m == "d" else 1
    W = cols * CARD_W + (cols - 1) * gap
    kids, y = [], 0.0
    for r in range(0, len(panels), cols):
        rowh = max(hs[r:r + cols])
        for j, p_ in enumerate(panels[r:r + cols]):
            kids.append((p_, j * (CARD_W + gap), y))
        y += rowh + gap
    return nest(W, y - gap, kids, title)


def card(tag, title, body, metrics, kind, c, m="m"):
    """Site tile: mono category label, title, body, footer row of big number + mono unit, arrow (link card).
    m="d": the full-width (840) row version; m="m": the 420 stacked version."""
    if m == "d":
        return card_wide(tag, title, body, metrics, kind, c)
    W, H = 420, CARD_H
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel2"], c["hair"])]
    b.append('<rect x="24" y="23" width="7" height="7" rx="1.5" fill="%s"/>' % c["brand"])
    b.append(label(38, 31, tag, c, 10.5))
    b.append(arrow(W - 40, 18, c["mute"]))
    tl = wrap(title, "b", 19, W - 48, 2)
    y = 64
    for ln in tl:
        b.append(text(24, y, ln, "b", 19, c["ink"], track=-0.02 * 19))
        y += 24
    bl = wrap(body, "r", 13.5, W - 48, 5 - len(tl))
    y += 2
    for ln in bl:
        b.append(text(24, y, ln, "r", 13.5, c["body"]))
        y += 20
    assert y <= H - 50, (title, y)
    b.append('<path d="M24 %d H%d" stroke="%s"/>' % (H - 56, W - 24, c["hair"]))
    x = 24
    for val, lab in metrics:
        b.append(mono(x, H - 22, val, 19, c["ink"], track=-0.04 * 19, w="mb"))
        x += width(val, "mb", 19, -0.04 * 19) + 7
        b.append(mono(x, H - 23, lab, 10, c["mute"]))
        x += width(lab, "mr", 10) + 18
    assert x < W - 24 - 104 - 4, (title, x)
    b.append(motif(kind, W - 24 - 104, H - 46, c))
    alt = "%s. %s %s" % (title, body, " ".join("%s %s" % mm for mm in metrics))
    b.append(tracer(W, H, 16, c, seedof(title)))
    return svg(W, H, "".join(b), alt.strip())


def card_wide(tag, title, body, metrics, kind, c):
    W = 840
    TW = 520                                   # text column; the right column holds the numbers + motif
    tl = wrap(title, "b", 20, TW, 2)
    bl = wrap(body, "r", 14, TW, 4)
    H = max(176, int(64 + 26 * (len(tl) - 1) + 12 + 22 * len(bl) + 18))
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel2"], c["hair"])]
    b.append('<rect x="24" y="23" width="7" height="7" rx="1.5" fill="%s"/>' % c["brand"])
    b.append(label(38, 31, tag, c, 10.5))
    b.append(arrow(W - 40, 18, c["mute"]))
    y = 64
    for ln in tl:
        b.append(text(24, y, ln, "b", 20, c["ink"], track=-0.02 * 20))
        y += 26
    y += 6
    for ln in bl:
        b.append(text(24, y, ln, "r", 14, c["body"]))
        y += 22
    sx = 24 + TW + 36
    b.append('<path d="M%s 24 V%d" stroke="%s"/>' % (_fmt(sx - 18.5), H - 24, c["hair"]))
    my = 70
    for val, lab in metrics:
        b.append(mono(sx, my, val, 24, c["ink"], track=-0.04 * 24, w="mb"))
        b.append(mono(sx + width(val, "mb", 24, -0.96) + 8, my - 1, lab, 10.5, c["mute"]))
        assert sx + width(val, "mb", 24, -0.96) + 8 + width(lab, "mr", 10.5) < W - 24, (title, lab)
        my += 36
    b.append(motif(kind, W - 24 - 104, H - 24 - 40, c))
    alt = "%s. %s %s" % (title, body, " ".join("%s %s" % mm for mm in metrics))
    b.append(tracer(W, H, 16, c, seedof(title, "w")))
    return svg(W, H, "".join(b), alt.strip())


def feature(tag, title, body, metrics, c, m="d"):
    """The wide GRC Practice Lab card: text left, a live control heatmap right."""
    W = 840 if m == "d" else 420
    a = c["accent"]
    s = S(c)
    tw = 420 if m == "d" else W - 48
    tl = wrap(body, "r", 14 if m == "d" else 13, tw, 4)
    H = 268 if m == "d" else 250 + 22 * len(tl) + 120
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="22" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
    b.append('<circle class="pl" cx="30" cy="30" r="4" fill="%s"/>' % c["ok"])
    b.append(label(42, 34, tag, c, 10.5))
    b.append(arrow(W - 40, 20, c["mute"]))
    ts = 26 if m == "d" else 22
    b.append(text(24, 74, title, "b", ts, c["ink"], track=-0.035 * ts))
    y = 104
    for ln in tl:
        b.append(text(24, y, ln, "r", 14 if m == "d" else 13, c["body"]))
        y += 22
    # metrics: 2 x 2 under the text
    my = y + 22
    for i, (val, lab) in enumerate(metrics):
        mx = 24 + (i % 2) * (tw / 2)
        yy = my + (i // 2) * 44
        b.append(mono(mx, yy, val, 22, c["ink"], track=-0.88, w="mb"))
        b.append(mono(mx + width(val, "mb", 22, -0.88) + 8, yy - 1, lab, 10.5, c["mute"]))
    yend = my + 44
    # heatmap of controls being assessed
    cols, rows, cs, gp = (16, 8, 14, 5) if m == "d" else (17, 6, 14, 5)
    gx = W - 24 - cols * (cs + gp) + gp if m == "d" else 24
    gy = 70 if m == "d" else yend + 10
    import random
    rnd = random.Random(27001)
    for r in range(rows):
        for k in range(cols):
            v = rnd.random()
            fill = c["ok"] if v > 0.62 else c["brand"] if v > 0.3 else c["chipbg"]
            op = "1" if v > 0.62 else _fmt(0.25 + v * 0.9) if v > 0.3 else "1"
            tile = '<rect x="%s" y="%s" width="%d" height="%d" rx="3" fill="%s" opacity="%s"/>' % (
                gx + k * (cs + gp), gy + r * (cs + gp), cs, cs, fill, op)
            b.append('<g class="tw"%s>%s</g>' % (d(-rnd.random() * 5.5), tile) if rnd.random() < 0.34 else tile)
    ly = gy + rows * (cs + gp) + 16
    lg = [("implemented", c["ok"]), ("in progress", c["brand"]), ("not started", c["chipbg"])]
    lx = gx
    for lab, col in lg:
        b.append('<rect x="%s" y="%s" width="10" height="10" rx="2" fill="%s" stroke="%s"/>' % (lx, ly - 9, col, c["hair"]))
        b.append(mono(lx + 15, ly, lab, 10, c["mute"]))
        lx += 15 + width(lab, "mr", 10) + 16
    b.append(mono(gx, ly + 20, "illustration of a learner's control board", 9.5, c["mute"]))
    H = int(ly + 40) if m == "m" else int(max(yend + 26, ly + 36))
    b[0] = '<rect x=".5" y=".5" width="%d" height="%d" rx="22" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])
    alt = "%s. %s %s" % (title, body, " ".join("%s %s" % mm for mm in metrics))
    b.append(tracer(W, H, 22, c, seedof("lab", m)))
    return svg(W, H, "".join(b), alt)


# ------------------------------------------------------------------------- contributions chart
STATUS = {  # label, kind of mark
    "merged": ("merged / accepted / recognised", "fill"),
    "pr": ("open PR", "ring"),
    "proposed": ("proposed", "ring2"),
}


def contrib_kind(dd, parse_ref):
    st = dd.get("status", "").lower()
    if st in ("merged", "accepted", "recognised"):
        return "merged"
    ref = parse_ref(dd["url"])
    return "pr" if ref and ref[2] == "PR" else "proposed"


def chart(data, parse_ref, c, m="d"):
    import datetime as dt
    s = S(c)
    a = c["accent"]
    W = 840 if m == "d" else 420
    days = sorted({x["date"] for x in data})
    d0 = dt.date.fromisoformat(days[0])
    d1 = dt.date.fromisoformat(days[-1])
    n = (d1 - d0).days + 1
    order = {"merged": 0, "pr": 1, "proposed": 2}
    byday = {}
    for x in data:
        byday.setdefault(x["date"], []).append(contrib_kind(x, parse_ref))
    maxn = max(len(v) for v in byday.values())
    per = 2 if m == "d" else 2
    r = 4.6 if m == "d" else 3.6
    sp = 13 if m == "d" else 10
    rowsmax = (maxn + per - 1) // per
    top = 70
    base = top + rowsmax * sp + 10
    H = base + 48
    left, right = (30, W - 30)
    step = (right - left) / float(max(n - 1, 1))
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
    counts = {k: sum(1 for x in data if contrib_kind(x, parse_ref) == k) for k in order}
    # legend
    lx, ly = 24, 32
    for k in ("merged", "pr", "proposed"):
        lab = "%d %s" % (counts[k], STATUS[k][0])
        b.append(_mark(lx + 5, ly - 4, 4.6, k, a, s, c))
        b.append(mono(lx + 15, ly, lab, 10.5 if m == "d" else 9.5, c["body"]))
        lx += 15 + width(lab, "mr", 10.5 if m == "d" else 9.5) + 18
    if m == "d":
        b.append(mono(W - 24, ly, "%d contributions to other people's repos" % len(data), 10.5, c["mute"], anchor="end"))
    for i in range(1, 4):
        yy = base - i * (base - top) / 4.0
        b.append('<path d="M%d %s H%d" stroke="%s" stroke-dasharray="2 5"/>' % (18, _fmt(yy), W - 18, c["hair"]))
    b.append('<path d="M18 %s H%d" stroke="%s"/>' % (_fmt(base + 0.5), W - 18, c["hair"]))
    idx = 0
    for di in range(n):
        day = (d0 + dt.timedelta(days=di)).isoformat()
        cx = left + di * step
        ks = sorted(byday.get(day, []), key=lambda k: order[k])
        for j, k in enumerate(ks):
            col, row = j % per, j // per
            px = cx + (col - (per - 1) / 2.0) * sp
            py = base - 10 - row * sp
            b.append(_mark(px, py, r, k, a, s, c, delay=0.25 + idx * 0.022))
            if k == "merged":
                b.append('<circle class="ring"%s cx="%s" cy="%s" r="%s" fill="none" stroke="%s"/>' % (d(1.8 + j * 0.4), _fmt(px), _fmt(py), r, c["ok"]))
            idx += 1
        lab = (d0 + dt.timedelta(days=di)).strftime("%d")
        if m == "d" or di % 2 == 0 or di == n - 1:
            b.append(mono(cx, base + 22, lab, 10 if m == "d" else 9, c["mute"], anchor="middle"))
    sw = right - left + 60
    b.append('<defs><linearGradient id="swg" x1="0" x2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
             '<stop offset="1" stop-color="%s" stop-opacity=".22"/></linearGradient></defs>' % (c["brand"], c["brand"]))
    b.append('<g style="animation:sw 7s cubic-bezier(.45,0,.55,1) infinite"><rect x="%s" y="%s" width="56" height="%s" fill="url(#swg)"/>'
             '<rect x="%s" y="%s" width="1.5" height="%s" fill="%s" opacity=".8"/></g>' % (
                 left - 86, top - 14, base - top + 14, left - 30, top - 14, base - top + 14, c["brand"]))
    b.append('<style>@keyframes sw{from{transform:translateX(0)}to{transform:translateX(%dpx)}}</style>' % sw)
    mon = d0.strftime("%b %Y").upper()
    b.append(mono(left - 6, base + 40, mon, 9.5, c["mute"]))
    alt = "Contributions by day, %s to %s: %d merged or accepted, %d open PRs, %d proposed." % (
        days[0], days[-1], counts["merged"], counts["pr"], counts["proposed"])
    b.append(tracer(W, H, 16, c, seedof("chart", m)))
    return svg(W, H, "".join(b), alt)


def _mark(x, y, r, k, a, s, c, delay=None):
    dl = d(delay) if delay is not None else ""
    cls = ' class="pp"' if delay is not None else ""
    if k == "merged":
        return '<circle%s%s cx="%s" cy="%s" r="%s" fill="%s"/>' % (cls, dl, _fmt(x), _fmt(y), r, c["ok"])
    if k == "pr":
        return '<circle%s%s cx="%s" cy="%s" r="%s" fill="%s" fill-opacity=".25" stroke="%s" stroke-width="1.6"/>' % (cls, dl, _fmt(x), _fmt(y), _fmt(r - 0.6), a, a)
    return ('<circle%s%s cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="2 2"/>'
            % (cls, dl, _fmt(x), _fmt(y), _fmt(r - 0.6), a))


# ---------------------------------------------------------------------------- contribution row
def name_lines(name, maxw, size=15):
    """Project name for a row: one line if it fits, else wrapped at hyphens over two lines at 14px.
    Repo slugs like www-project-ai-security-and-privacy-guide have no spaces, so wrap() cannot break them
    and they overflowed into the title column (John, 2026-11-17)."""
    if width(name, "s", size) <= maxw:
        return [name], size
    size = 14
    parts = [p + "-" for p in name.split("-")]
    parts[-1] = parts[-1][:-1]
    lines, cur = [], ""
    for p in parts:
        if cur and width(cur + p, "s", size) > maxw:
            lines.append(cur)
            cur = p
        else:
            cur += p
    lines.append(cur)
    if len(lines) > 2:
        lines = [lines[0], "".join(lines[1:])]
    fixed = []
    for ln in (x.strip() for x in lines):
        while width(ln, "s", size) > maxw and len(ln) > 2:
            ln = ln[:-2] + "\u2026"
        fixed.append(ln)
    return fixed, size


WON_LABELS = ("MERGED", "ACCEPTED", "RECOGNISED")


def row(dd, label, ref_txt, c, m="d"):
    s = S(c)
    a = c["accent"]
    W = 840 if m == "d" else 420
    merged = label in WON_LABELS
    # The site's chips: won = solid green, open = amber outline.
    pill_fill = c["ok"] if merged else "none"
    pill_ink = c["ok_ink"] if merged else a
    pill_stroke = c["ok"] if merged else a
    pw = width(label, "mb", 9.5, 0.8) + 18
    b = []
    if m == "d":
        rw = width(ref_txt, "mb", 11.5)
        tl = wrap(dd["title"], "r", 13.5, W - 244 - 20 - rw - 28, 3)
        nl, nsz = name_lines(dd["project"], 210)
        hb = 84 if len(nl) == 1 else 102
        H = max(84 if len(tl) <= 2 else 100, hb)
        b.append('<rect x=".5" y=".5" width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"]))
        oy = (H - hb) / 2
        b.append('<rect x="20.5" y="%s" width="%s" height="19" rx="9.5" fill="%s" stroke="%s"/>' % (_fmt(16.5 + oy), _fmt(pw), pill_fill, pill_stroke))
        b.append(mono(29.5, 29.5 + oy, label, 9.5, pill_ink, bold=True, track=0.8))
        for i, ln in enumerate(nl):
            b.append(text(20, 58 + oy + i * 17, ln, "s", nsz, c["ink"]))
        b.append(mono(20, 74 + oy + (len(nl) - 1) * 17, dd.get("area", ""), 10, c["mute"]))
        ty = H / 2 + 5 - (len(tl) - 1) * 10.5
        for i, ln in enumerate(tl):
            b.append(text(244, ty + i * 21, ln, "r", 13.5, c["body"]))
        b.append(mono(W - 20, H / 2 + 4, ref_txt, 11.5, a, anchor="end", bold=True))
        b[1:1] = []
    else:
        tl = wrap(dd["title"], "r", 12.5, W - 40, 4)
        H = 96 + 19 * len(tl)
        b.append('<rect x=".5" y=".5" width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"]))
        b.append('<rect x="18.5" y="16.5" width="%s" height="19" rx="9.5" fill="%s" stroke="%s"/>' % (_fmt(pw), pill_fill, pill_stroke))
        b.append(mono(27.5, 29.5, label, 9.5, pill_ink, bold=True, track=0.8))
        b.append(mono(W - 18, 30, ref_txt, 10.5, a, anchor="end", bold=True))
        nl, nsz = name_lines(dd["project"], W - 36)
        ex = (len(nl) - 1) * 17
        H += ex
        b[0] = '<rect x=".5" y=".5" width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])
        for i, ln in enumerate(nl):
            b.append(text(18, 62 + i * 17, ln, "s", nsz, c["ink"]))
        b.append(mono(18, 79 + ex, dd.get("area", ""), 9.5, c["mute"]))
        for i, ln in enumerate(tl):
            b.append(text(18, 104 + ex + i * 19, ln, "r", 12.5, c["body"]))
    alt = "%s: %s. %s. %s" % (label.title(), dd["project"], dd["title"], ref_txt)
    b.append(tracer(W, H, 10, c, seedof(dd["id"], m), dash=.05, base=12.0))
    if merged:
        px = (20.5 if m == "d" else 18.5) + pw + 12
        py = (26 + oy) if m == "d" else 26
        b.append('<circle class="ring" cx="%s" cy="%s" r="3.5" fill="none" stroke="%s"/><circle class="pl" cx="%s" cy="%s" r="3.5" fill="%s"/>' % (
            _fmt(px), _fmt(py), c["ok"], _fmt(px), _fmt(py), c["ok"]))
    return svg(W, H, "".join(b), alt)


# ------------------------------------------------------------------------------- focus + misc
FOCUS_ICON_CSS = ""


def focus(title, ic, body, c, H=None):
    W = CARD_W
    a = c["accent"]
    lines = wrap(body, "r", 14, W - 48, 4)
    H = H or 100 + 21 * len(lines)
    b = ['<rect x=".5" y=".5" width="%d" height="%s" rx="16" fill="%s" stroke="%s"/>' % (W - 1, _fmt(H - 1), c["panel2"], c["hair"])]
    b.append('<rect x="24.5" y="20.5" width="40" height="40" rx="10" fill="%s" stroke="%s"/>' % (c["panel3"], c["hair2"]))
    b.append('<rect x="24.5" y="20.5" width="40" height="40" rx="10" fill="none" stroke="%s" class="pl" opacity=".6" style="animation-delay:-%ss"/>'
             % (c["brand"], _fmt((seedof(title) % 26) / 10.0)))
    b.append(K.icon(ic, 33.5, 29.5, 22, a))
    b.append(text(78, 46, title, "b", 19, c["ink"], track=-0.02 * 19))
    for i, ln in enumerate(lines):
        b.append(text(24, 88 + 21 * i, ln, "r", 14, c["body"]))
    b.append(tracer(W, H, 16, c, seedof(title)))
    return svg(W, H, "".join(b), "%s. %s" % (title, body))


def focus_height(body):
    return 100 + 21 * len(wrap(body, "r", 14, CARD_W - 48, 4))


def creds(items, c, H):
    W = CARD_W
    a = c["accent"]
    b = ['<rect x=".5" y=".5" width="%d" height="%s" rx="16" fill="%s" stroke="%s"/>' % (W - 1, _fmt(H - 1), c["panel2"], c["hair"])]
    b.append('<rect x="24" y="24" width="7" height="7" rx="1.5" fill="%s"/>' % c["brand"])
    b.append(label(38, 32, "Credentials", c, 10.5))
    cyc = len(items) * 1.1
    css = ("@keyframes cr{0%%{stroke:%s;fill:%s}%s%%{stroke:%s;fill:%s}%s%%,100%%{stroke:%s;fill:%s}}"
           % (c["hair2"], c["chipbg"], _fmt(100 * 0.45 / cyc), c["brand"], c["acc_soft"], _fmt(100 * 1.4 / cyc), c["hair2"], c["chipbg"]))
    idx = 0
    for r, rw in enumerate(K._chip_rows(items, W, x0=24)):
        y = 52 + r * 36
        for k, (x, it, cw) in enumerate(rw):
            b.append('<rect x="%s" y="%d" width="%s" height="27" rx="6" fill="%s" stroke="%s" style="animation:cr %ss ease-in-out infinite;'
                     'animation-delay:%ss"/>%s' % (_fmt(x + .5), y, _fmt(cw - 1), c["chipbg"], c["hair2"], _fmt(cyc), _fmt(idx * 1.1),
                                                   text(x + 13, y + 18.2, it, "m", 13, c["chipink"])))
            idx += 1
    b.append(tracer(W, H, 16, c, seedof("creds")))
    return svg(W, H, "".join(b), "Credentials: " + ", ".join(items), css)


def creds_height(items):
    return 52 + len(K._chip_rows(items, CARD_W, x0=24)) * 36 + 12


def teach(value, l1, l2, body, c, H):
    W = CARD_W
    s = S(c)
    a = c["accent"]
    b = ['<rect x=".5" y=".5" width="%d" height="%s" rx="16" fill="%s" stroke="%s"/>' % (W - 1, _fmt(H - 1), c["panel2"], c["hair"])]
    b.append('<circle class="pl" cx="28" cy="28" r="4" fill="%s"/>' % c["ok"])
    b.append(label(40, 32, "Teaching", c, 10.5))
    ob, ocss = odometer(24, 96, value, 40, c["ink"], "tch", 0.3, w="mb", acc=c["accent"])
    b.append(ob)
    vw = width(value, "mb", 40, -1.6)
    b.append(text(24 + vw + 14, 76, l1, "b", 16, c["ink"]))
    b.append(text(24 + vw + 14, 98, l2, "m", 16, c["mute"]))
    for i, ln in enumerate(wrap(body, "r", 14, W - 48, 4)):
        b.append(text(24, 134 + 21 * i, ln, "r", 14, c["body"]))
    b.append(tracer(W, H, 16, c, seedof("teach")))
    return svg(W, H, "".join(b), "Teaching: %s %s %s. %s" % (value, l1, l2, body), ocss)


def teach_height(body):
    return 134 + 21 * len(wrap(body, "r", 14, CARD_W - 48, 4)) + 4


PILL_GAP = 8


def pill(text_, ic, c, m, n, last, primary=False):
    """One of n equal pill buttons that together span the row exactly. The gap to the next button is
    transparent space inside this SVG, so the row has no inline-whitespace gaps to account for.
    primary = the site's amber button; the rest are ghost buttons."""
    W = 840 if m == "d" else 420
    gap = PILL_GAP if m == "d" else PILL_GAP / 2
    body = (W - (n - 1) * gap) / n
    sw = body + (0 if last else gap)
    h = 42 if m == "d" else 44
    fs = 13.5
    fill, stroke, ink, icc = (c["brand"], c["brand"], c["acc_ink"], c["acc_ink"]) if primary else (c["panel"], c["hair2"], c["ink"], c["accent"])
    b = '<rect x=".5" y=".5" width="%s" height="%d" rx="%s" fill="%s" stroke="%s"/>' % (_fmt(body - 1), h - 1, _fmt((h - 1) / 2.0), fill, stroke)
    tw = width(text_, "s", fs)
    if m == "d":
        assert 16 + 9 + tw + 20 <= body, "pill label does not fit: " + text_
        x0 = (body - (16 + 9 + tw)) / 2
        b += K.icon(ic, x0, (h - 16) / 2, 16, icc)
        b += text(x0 + 25, h / 2 + fs * 0.36, text_, "s", fs, ink)
    else:
        b += K.icon(ic, (body - 20) / 2, (h - 20) / 2, 20, icc)
    if not primary:
        b += tracer(body, h, _fmt((h - 2) / 2.0), c, seedof(text_, n), dash=.12, base=5.0)
    else:
        b += ('<rect x=".5" y=".5" width="%s" height="%d" rx="%s" fill="none" stroke="%s" stroke-width="6" class="pl" opacity=".35"/>'
              % (_fmt(body - 1), h - 1, _fmt((h - 1) / 2.0), c["brand"]))
    return svg(sw, h, b, text_)


def pill_pct(n, last):
    body = (840 - (n - 1) * PILL_GAP) / float(n)
    return (body + (0 if last else PILL_GAP)) / 840 * 100


def footer(c, m="d"):
    W = 840 if m == "d" else 420
    H = 56
    s = S(c)
    b = ['<path d="M0 .5 H%d" stroke="%s"/>' % (W, c["page_hair"])]
    b.append('<circle class="pl" cx="5" cy="31" r="4" fill="%s"/>' % c["ok"])
    t = "regenerated from the contributions ledger" if m == "d" else "regenerated from the ledger"
    b.append(mono(18, 35, "~/eof", 11.5, c["page_acc"], w="mm"))
    b.append(mono(W, 35, t, 11, c["page_mute"], anchor="end"))
    x0, x1 = 70, W - width(t, "mr", 11) - 24
    pts, xx = [], x0
    while xx < x1 - 60:
        pts += ["%s 31" % _fmt(xx + 30), "%s 22" % _fmt(xx + 36), "%s 40" % _fmt(xx + 42), "%s 31" % _fmt(xx + 48)]
        xx += 90
    pts.append("%s 31" % _fmt(x1))
    path = "M%d 31 L" % x0 + " L".join(pts)
    b.append('<path d="%s" fill="none" stroke="%s" stroke-opacity=".3" stroke-width="1.2"/>' % (path, c["page_bar"]))
    b.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linejoin="round" pathLength="1" stroke-dasharray=".14 .86" '
             'style="animation:tr 3.2s linear infinite"/>' % (path, c["page_bar"]))
    return svg(W, H, "".join(b), "")


# ------------------------------------------------------------------------------------ ticker
def ticker(events, c, m="d"):
    """events: (label, project, ref, age). A LIVE badge and the latest ledger events scrolling past.
    Rebuilt from the ledger on every refresh, so 'age' is current to the last run."""
    s = S(c)
    W = 840 if m == "d" else 420
    H = 46
    fs = 11.5 if m == "d" else 10.5
    col = {"MERGED": c["ok_text"], "ACCEPTED": c["ok_text"], "RECOGNISED": c["ok_text"], "OPEN PR": c["accent"], "PROPOSED": c["accent"]}
    items, x = [], 0
    for lab, proj, ref, age in events:
        seg = []
        seg.append('<circle cx="%s" cy="%s" r="3" fill="%s"/>' % (_fmt(x + 3), H / 2 - 0.5, col.get(lab, c["mute"])))
        x += 12
        seg.append(mono(x, H / 2 + 4, lab, fs - 1, col.get(lab, c["mute"]), bold=True, track=0.8))
        x += width(lab, "mb", fs - 1, 0.8) + 10
        seg.append(text(x, H / 2 + 4.5, proj, "b", fs + 1.5, c["ink"]))
        x += width(proj, "b", fs + 1.5) + 9
        seg.append(mono(x, H / 2 + 4, "%s  ·  %s" % (ref, age), fs, c["mute"]))
        x += width("%s  ·  %s" % (ref, age), "mr", fs) + 34
        items.append("".join(seg))
    strip = "".join(items)
    sw = x
    bx = 96 if m == "d" else 78
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="%s" fill="%s" stroke="%s"/>' % (W - 1, H - 1, _fmt((H - 1) / 2.0), c["panel"], c["hair"])]
    b.append('<defs><clipPath id="tk"><rect x="%d" y="0" width="%d" height="%d"/></clipPath>'
             '<linearGradient id="tf" x1="0" x2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>'
             '<linearGradient id="tf2" x1="1" x2="0"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient></defs>'
             % (bx, W - bx - 1, H, c["panel"], c["panel"], c["panel"], c["panel"]))
    dur = sw / 38.0
    b.append('<g clip-path="url(#tk)"><g style="animation:tk %ss linear infinite"><g transform="translate(%d 0)">%s</g>'
             '<g transform="translate(%s 0)">%s</g></g></g>' % (_fmt(dur), bx + 14, strip, _fmt(bx + 14 + sw), strip))
    b.append('<style>@keyframes tk{from{transform:translateX(0)}to{transform:translateX(-%spx)}}</style>' % _fmt(sw))
    b.append('<rect x="%d" y="1" width="28" height="%d" fill="url(#tf)"/>' % (bx, H - 2))
    b.append('<rect x="%d" y="1" width="28" height="%d" fill="url(#tf2)"/>' % (W - 29, H - 2))
    # LIVE badge
    b.append('<path d="M%d 10 V%d" stroke="%s"/>' % (bx, H - 10, c["hair"]))
    b.append('<circle class="ring" cx="20" cy="%s" r="4" fill="none" stroke="%s"/>' % (H / 2, c["ok"]))
    b.append('<circle class="pl" cx="20" cy="%s" r="4" fill="%s"/>' % (H / 2, c["ok"]))
    b.append(mono(32, H / 2 + 4, "LIVE", fs, c["ok_text"], bold=True, track=1.5))
    alt = "Latest activity: " + "; ".join("%s %s %s, %s" % e for e in events)
    b.append(tracer(W, H, _fmt((H - 2) / 2.0), c, seedof("ticker", m)))
    return svg(W, H, "".join(b), alt)


# --------------------------------------------------------------------------------- intro
SHIFTS = ["AI agents acting on real systems", "AI regulation becoming enforceable", "the move to post-quantum cryptography"]
INTRO = ("I lead product and technology at Purplecop Security, where we build compliance automation for GRC, "
         "AI governance and privacy. My work sits where three shifts meet:")


def intro(c, m="d"):
    W = 840 if m == "d" else 420
    fs = 15.5 if m == "d" else 14
    lines = wrap(INTRO, "r", fs, W - 48, 5)
    y0 = 38
    H = int(y0 + 24 * (len(lines) - 1) + 30 + len(SHIFTS) * 36 + 10)
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
    for i, ln in enumerate(lines):
        b.append(text(24, y0 + 24 * i, ln, "r", fs, c["body"]))
    y = y0 + 24 * (len(lines) - 1) + 44
    cyc, css = 9.0, ""
    for i, sh in enumerate(SHIFTS):
        yy = y + i * 36
        t0 = i * 3.0
        css += ("@keyframes sh%d{0%%,%s%%{transform:scaleX(.001)}%s%%,%s%%{transform:scaleX(1)}%s%%,100%%{transform:scaleX(.001)}}"
                % (i, _fmt(100 * t0 / cyc), _fmt(100 * (t0 + 1.2) / cyc), _fmt(100 * (t0 + 2.6) / cyc), _fmt(100 * (t0 + 3.0) / cyc)))
        tw = width(sh, "b", fs + 0.5)
        assert 76 + tw < W - 16, sh
        b.append('<rect x="22" y="%s" width="%s" height="28" rx="10" fill="%s" fill-opacity="%s" style="transform-box:fill-box;'
                 'transform-origin:left center;transform:scaleX(.001);animation:sh%d %ss cubic-bezier(.4,0,.2,1) infinite"/>'
                 % (_fmt(yy - 19), _fmt(tw + 66), c["brand"], ".12", i, _fmt(cyc)))
        b.append('<circle cx="34" cy="%s" r="4" fill="%s" style="animation:pl 3s ease-in-out infinite;animation-delay:%ss"/>' % (
            _fmt(yy - 5), c["brand"], _fmt(t0)))
        b.append(mono(46, yy, "0%d" % (i + 1), 10.5, c["accent"], w="mm"))
        b.append(text(72, yy, sh, "b", fs + 0.5, c["ink"], track=-0.01 * fs))
    b.append(tracer(W, H, 16, c, seedof("intro", m)))
    return svg(W, H, "".join(b), INTRO + " " + "; ".join(SHIFTS) + ".", css)


def subhead(title, count, c, m="d", dot=None):
    W = 840 if m == "d" else 420
    H = 42 if m == "d" else 58
    dot = dot or c["page_bar"]
    b = ['<circle class="ring" cx="6" cy="20" r="4" fill="none" stroke="%s"/><circle class="pl" cx="6" cy="20" r="4" fill="%s"/>' % (dot, dot)]
    b.append(text(20, 26, title, "b", 17 if m == "d" else 15, c["page_ink"], track=-0.02 * 17))
    if m == "d":
        b.append(mono(W, 25, count, 11, c["page_mute"], anchor="end"))
    else:
        b.append(mono(20, 46, count, 10, c["page_mute"]))
    b.append('<path d="M0 %s H%d" stroke="%s"/>' % (_fmt(H - 1.5), W, c["page_hair"]))
    b.append('<rect class="sl" x="0" y="%s" width="40" height="1.5" rx=".75" fill="%s" style="--run:%dpx"/>' % (_fmt(H - 2.25), c["page_bar"], W - 40))
    return svg(W, H, "".join(b), "%s, %s" % (title, count))


SPEAK = ("Virtual keynotes, panels and podcasts on securing AI agents, operationalising ISO/IEC 42001 and the "
         "EU AI Act, and post-quantum migration for security and GRC leaders.")


def speaking(c, m="d"):
    import math
    W = 840 if m == "d" else 420
    fs = 15 if m == "d" else 13.5
    n = 30
    tw = (W - 48 - n * 7 - 24) if m == "d" else (W - 48)
    lines = wrap(SPEAK, "r", fs, tw, 6)
    H = int(max(140, 76 + 23 * len(lines))) if m == "d" else int(76 + 23 * len(lines) + 70)
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
    b.append('<circle class="ring" cx="30" cy="30" r="4" fill="none" stroke="%s"/><circle class="pl" cx="30" cy="30" r="4" fill="%s"/>' % (c["ok"], c["ok"]))
    tag = "ON AIR  ·  KEYNOTES  ·  PANELS  ·  PODCASTS" if m == "d" else "ON AIR  ·  TALKS"
    b.append(label(42, 34, tag, c, 10.5, color=c["accent"]))
    for i, ln in enumerate(lines):
        b.append(text(24, 68 + 23 * i, ln, "r", fs, c["body"]))
    wx = (W - 24 - n * 7) if m == "d" else (W - n * 7) / 2
    wy = (H / 2 + 6) if m == "d" else (H - 38)
    for i in range(n):
        h = 8 + 36 * abs(math.sin(i * 0.55)) * (0.6 + 0.4 * math.sin(i * 0.21))
        b.append('<rect x="%s" y="%s" width="4" height="%s" rx="2" fill="%s" style="transform-box:fill-box;transform-origin:center;'
                 'animation:wv %ss ease-in-out infinite;animation-delay:-%ss"/>' % (
                     _fmt(wx + i * 7), _fmt(wy - h / 2), _fmt(h), c["brand"], _fmt(0.9 + (i % 5) * 0.17), _fmt((i * 0.13) % 1.3)))
    b.append(tracer(W, H, 16, c, seedof("speak", m)))
    return svg(W, H, "".join(b), "Speaking. " + SPEAK)


# ------------------------------------------------------------------------------ achievements
def _img(uri, x, y, w, h, rx, uid, bg=None):
    """An embedded raster (data: URI) clipped to a rounded box. GitHub serves README SVGs as images, which
    may not fetch anything, so logos travel inside the SVG."""
    out = ['<defs><clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s" rx="%s"/></clipPath></defs>' % (
        uid, _fmt(x), _fmt(y), _fmt(w), _fmt(h), _fmt(rx))]
    if bg:
        out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s"/>' % (_fmt(x), _fmt(y), _fmt(w), _fmt(h), _fmt(rx), bg))
    out.append('<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="xMidYMid meet" clip-path="url(#%s)"/>' % (
        uri, _fmt(x), _fmt(y), _fmt(w), _fmt(h), uid))
    return "".join(out)


def _count_line(t):
    parts = [(t.get("recognised", 0), "recognised"), (t.get("merged", 0), "merged"), (t.get("accepted", 0), "accepted")]
    return "  ·  ".join("%d %s" % (n, k) for n, k in parts if n).upper()


def achievements(badges, tiles, more, c, m="d"):
    """GitHub badges + Hall of Fame + organisations with official logos, from the website's own data.
    badges: dicts name/tier/blurb/uri. tiles: dicts name/sub/uri/merged/accepted/recognised. more: tiles not shown."""
    W = 840 if m == "d" else 420
    P = 24 if m == "d" else 18
    b, css = [], ""
    # --- badges row
    y = 34
    b.append('<rect x="%d" y="24" width="7" height="7" rx="1.5" fill="%s"/>' % (P, c["ok"]))
    b.append(label(P + 14, 32, "GitHub achievements", c, 10.5))
    b.append(mono(W - P, 32, "%d badges" % len(badges), 10.5, c["mute"], anchor="end"))
    n = max(len(badges), 1)
    bw = (W - 2 * P) / float(n)
    isz = 64 if m == "d" else 48
    y = 52
    css += ("@keyframes bf{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}"
            "@keyframes bs{0%,60%{opacity:0}75%{opacity:.9}100%{opacity:0}}")
    for i, bd in enumerate(badges):
        cx = P + bw * i + bw / 2
        g = ['<g style="animation:bf 4.2s ease-in-out infinite;animation-delay:-%ss">' % _fmt(i * 0.7)]
        g.append('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s"/>' % (_fmt(cx), _fmt(y + isz / 2), _fmt(isz / 2 + 4), c["panel3"], c["hair2"]))
        g.append(_img(bd["uri"], cx - isz / 2, y, isz, isz, isz / 2, "bd%s%d" % (m, i)))
        g.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="2" style="animation:bs 5s ease-in-out infinite;'
                 'animation-delay:%ss"/>' % (_fmt(cx), _fmt(y + isz / 2), _fmt(isz / 2 + 4), c["brand"], _fmt(i * 1.0)))
        g.append("</g>")
        b.append("".join(g))
        if bd.get("tier"):
            tw = width(bd["tier"], "mb", 9.5) + 12
            tx, ty = cx + isz / 2 - tw / 2 + 2, y - 2
            b.append('<rect x="%s" y="%s" width="%s" height="17" rx="8.5" fill="%s" stroke="%s"/>' % (_fmt(tx), _fmt(ty), _fmt(tw), c["panel"], c["brand"]))
            b.append(mono(tx + tw / 2, ty + 12.2, bd["tier"], 9.5, c["accent"], anchor="middle", bold=True))
        ny = y + isz + 24
        ns = 13.5 if m == "d" else 11
        b.append(text(cx, ny, fit(bd["name"], "b", ns, bw - 8), "b", ns, c["ink"], anchor="middle"))
        if m == "d":
            for j, ln in enumerate(wrap(bd.get("blurb", ""), "r", 11.5, bw - 14, 2)):
                b.append(text(cx, ny + 18 + j * 15, ln, "r", 11.5, c["mute"], anchor="middle"))
    y = y + isz + (24 + 18 + 15 + 22 if m == "d" else 24 + 20)
    # --- organisations grid
    b.append('<path d="M%d %s H%d" stroke="%s"/>' % (P, _fmt(y + .5), W - P, c["hair"]))
    y += 30
    tot = {k: sum(t.get(k, 0) for t in tiles + more) for k in ("merged", "accepted", "recognised")}
    b.append('<rect x="%d" y="%s" width="7" height="7" rx="1.5" fill="%s"/>' % (P, _fmt(y - 8), c["ok"]))
    b.append(label(P + 14, y, "Accepted work", c, 10.5))
    summ = "%d organisations" % (len(tiles) + len(more))
    b.append(mono(W - P, y, summ, 10.5, c["mute"], anchor="end"))
    y += 18
    cols = 3 if m == "d" else 2
    gap = 12 if m == "d" else 8
    tw_ = (W - 2 * P - (cols - 1) * gap) / float(cols)
    th = 74 if m == "d" else 70
    lsz = 40 if m == "d" else 34
    nt = len(tiles)
    cyc = max(nt, 1) * 0.9
    css += ("@keyframes tl{0%%{stroke:%s}%s%%{stroke:%s}%s%%,100%%{stroke:%s}}"
            % (c["hair"], _fmt(100 * 0.4 / cyc), c["brand"], _fmt(100 * 1.4 / cyc), c["hair"]))
    for i, t in enumerate(tiles):
        col, row_ = i % cols, i // cols
        tx = P + col * (tw_ + gap)
        ty = y + row_ * (th + gap)
        b.append('<rect x="%s" y="%s" width="%s" height="%s" rx="10" fill="%s" stroke="%s" style="animation:tl %ss ease-in-out infinite;'
                 'animation-delay:%ss"/>' % (_fmt(tx + .5), _fmt(ty + .5), _fmt(tw_ - 1), th - 1, c["panel2"], c["hair"], _fmt(cyc), _fmt(i * 0.9)))
        lx, ly = tx + 14, ty + (th - lsz) / 2
        if t.get("uri"):
            b.append(_img(t["uri"], lx, ly, lsz, lsz, 9, "lg%s%d" % (m, i), bg="#ffffff"))
        else:
            b.append('<rect x="%s" y="%s" width="%s" height="%s" rx="9" fill="%s"/>' % (_fmt(lx), _fmt(ly), lsz, lsz, c["brand"]))
            b.append(text(lx + lsz / 2, ly + lsz / 2 + 6, t["name"][:1].upper(), "b", 18, c["acc_ink"], anchor="middle"))
        b.append('<rect x="%s" y="%s" width="%s" height="%s" rx="9" fill="none" stroke="%s"/>' % (_fmt(lx + .5), _fmt(ly + .5), lsz - 1, lsz - 1, c["hair2"]))
        x0 = lx + lsz + 12
        mw = tx + tw_ - 12 - x0
        nsz = 14 if m == "d" else 12.5
        b.append(text(x0, ty + 26, fit(t["name"], "b", nsz, mw), "b", nsz, c["ink"], track=-0.01 * nsz))
        b.append(mono(x0, ty + 43, fit(t.get("sub", ""), "mr", 10, mw), 10, c["mute"]))
        cl = _count_line(t) if m == "d" else _count_line(t).replace("  \u00b7  ", " \u00b7 ")
        csz, ctr = (9.5, 0.76) if m == "d" else (9, 0.0)
        b.append(mono(x0, ty + 60, fit(cl, "mm", csz, mw, ctr), csz, c["ok_text"], track=ctr, w="mm"))
    rows = (nt + cols - 1) // cols
    y += rows * (th + gap) - gap
    if more:
        y += 26
        b.append(mono(P, y, "+ %d more organisations on the website" % len(more), 10.5, c["mute"]))
        b.append(arrow(P + width("+ %d more organisations on the website" % len(more), "mr", 10.5) + 6, y - 11, c["accent"], 12))
    H = int(y + 26)
    bg = ('<rect x=".5" y=".5" width="%d" height="%d" rx="16" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"]) +
          '<defs><linearGradient id="ag" x1="0" x2="1"><stop offset="0" stop-color="%s"/><stop offset=".7" stop-color="%s" stop-opacity="0"/></linearGradient>'
          '<clipPath id="ac"><rect width="%d" height="%d" rx="16"/></clipPath></defs>'
          '<rect x="0" y="0" width="%d" height="2" fill="url(#ag)" opacity=".6" clip-path="url(#ac)"/>' % (c["ok"], c["ok"], W, H, W))
    alt = ("GitHub achievements: " + ", ".join(("%s %s" % (x["name"], x.get("tier", ""))).strip() for x in badges) + ". Accepted work: " +
           "; ".join("%s (%s)" % (t["name"], _count_line(t).lower()) for t in tiles + more) + ". %d merged, %d accepted, %d recognised." % (
               tot["merged"], tot["accepted"], tot["recognised"]))
    return svg(W, H, bg + "".join(b) + tracer(W, H, 16, c, seedof("ach", m)), alt, css)


# -------------------------------------------------------------------------------- newsletter
NL_LEAD = ("That's how every edition of GRC Made Simple Daily starts. Everything that happened in GRC, AI governance, "
           "AI security, privacy and post-quantum today, in one place.")


def newsletter(published, latest, logo_uri, c, m="d"):
    """GRC Made Simple Daily: the site's newsletter block. latest: (date, title) newest first."""
    W = 840 if m == "d" else 420
    P = 24 if m == "d" else 18
    b, css = [], ""
    lw = 372 if m == "d" else W - 2 * P
    y = 24
    if logo_uri:
        b.append(_img(logo_uri, P, y, 40, 40, 20, "gms%s" % m))
        b.append('<circle cx="%s" cy="%s" r="19.5" fill="none" stroke="%s"/>' % (P + 20, y + 20, c["hair2"]))
    b.append(label(P + 52, y + 17, "Newsletter", c, 10.5, color=c["accent"]))
    b.append(text(P + 52, y + 35, "GRC Made Simple Daily", "b", 14, c["ink"], track=-0.2))
    y += 40 + 42
    hs = 28 if m == "d" else 24
    b.append('<g class="fi">%s</g>' % text(P, y, "Hey Control Freaks!", "b", hs, c["ink"], track=-0.035 * hs))
    y += 30
    for i, ln in enumerate(wrap(NL_LEAD, "r", 14, lw, 5)):
        b.append(text(P, y + i * 22, ln, "r", 14, c["body"]))
        last = y + i * 22
    y = last + 46
    ob, ocss = odometer(P, y, str(published), 34, c["ink"], "nl%s" % m, 0.3, w="mb", acc=c["accent"])
    b.append(ob)
    css += ocss
    nx = P + width(str(published), "mb", 34, -1.36) + 10
    b.append(mono(nx, y - 14, "editions published", 10.5, c["mute"]))
    b.append(mono(nx, y, "on LinkedIn", 10.5, c["mute"]))
    y += 24
    btn = "Subscribe on LinkedIn"
    bw = width(btn, "s", 13.5) + 16 + 9 + 40
    b.append('<rect x="%d" y="%s" width="%s" height="40" rx="20" fill="%s"/>' % (P, _fmt(y), _fmt(bw), c["brand"]))
    b.append(K.icon("mail", P + 20, y + 12, 16, c["acc_ink"]))
    b.append(text(P + 45, y + 20 + 13.5 * 0.36, btn, "s", 13.5, c["acc_ink"]))
    b.append('<rect x="%d" y="%s" width="%s" height="40" rx="20" fill="none" stroke="%s" stroke-width="6" class="pl" opacity=".3"/>' % (P, _fmt(y), _fmt(bw), c["brand"]))
    left_end = y + 40
    # latest editions
    if m == "d":
        x0, y = 430, 34
        xw = W - P - x0
    else:
        x0, y = P, left_end + 40
        xw = W - 2 * P
    b.append(label(x0, y, "Latest editions", c, 10.5))
    b.append(mono(x0 + xw, y, "new every weekday", 10.5, c["mute"], anchor="end"))
    y += 14
    n = len(latest)
    cyc = max(n, 1) * 3.0
    for i, (dt_, title) in enumerate(latest):
        tl = wrap(title, "b", 14.5, xw - 28, 2)
        rh = 34 + 19 * len(tl)
        css += ("@keyframes ne%d{0%%,%s%%{opacity:0}%s%%,%s%%{opacity:1}%s%%,100%%{opacity:0}}" % (
            i, _fmt(100 * i * 3.0 / cyc), _fmt(100 * (i * 3.0 + 0.5) / cyc), _fmt(100 * (i * 3.0 + 2.5) / cyc), _fmt(100 * (i * 3.0 + 3.0) / cyc)))
        b.append('<rect x="%s" y="%s" width="%s" height="%s" rx="10" fill="%s" fill-opacity="%s" opacity="0" style="animation:ne%d %ss ease-in-out infinite"/>' % (
            _fmt(x0 - 10), _fmt(y + 4), _fmt(xw + 20), rh - 8, c["brand"], ".08", i, _fmt(cyc)))
        b.append('<path d="M%s %s H%s" stroke="%s"/>' % (_fmt(x0), _fmt(y + .5), _fmt(x0 + xw), c["hair"]))
        b.append(mono(x0, y + 26, dt_, 10.5, c["accent"], w="mm"))
        if i == 0:
            dx = x0 + width(dt_, "mm", 10.5) + 14
            b.append('<circle class="ring" cx="%s" cy="%s" r="3.5" fill="none" stroke="%s"/><circle class="pl" cx="%s" cy="%s" r="3.5" fill="%s"/>' % (
                _fmt(dx), _fmt(y + 22.5), c["ok"], _fmt(dx), _fmt(y + 22.5), c["ok"]))
            b.append(label(dx + 10, y + 26, "latest", c, 9.5, color=c["ok_text"]))
        for j, ln in enumerate(tl):
            b.append(text(x0, y + 48 + j * 19, ln, "b", 14.5, c["ink"], track=-0.15))
        y += rh
    right_end = y
    H = int(max(left_end, right_end) + 26) if m == "d" else int(right_end + 18)
    if m == "d":
        b.append('<path d="M%s 24 V%d" stroke="%s"/>' % (_fmt(x0 - 26.5), H - 24, c["hair"]))
    bg = '<rect x=".5" y=".5" width="%d" height="%d" rx="22" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])
    alt = ("GRC Made Simple Daily newsletter. Hey Control Freaks! " + NL_LEAD + " %s editions published, new every weekday. Latest: " % published +
           "; ".join("%s %s" % e for e in latest) + ". Subscribe on LinkedIn.")
    return svg(W, H, bg + "".join(b) + tracer(W, H, 22, c, seedof("nl", m)), alt, css)
