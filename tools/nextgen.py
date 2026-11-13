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

# Signal colours on top of the Purplecop palette: green = verified, amber = in review.
_GOLD = {'ok': '#f4d06f', 'warn': '#e3b84f', 'term': '#070605', 'termhair': '#2b2518', 'termink': '#f3ead2', 'termmute': '#8a8068', 'termacc': '#e3b84f', 'dot': '#211c12'}
SIG = {"dark": _GOLD, "light": _GOLD}

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
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def svg(W, H, body, title, css=""):
    return K.svg(W, H, "<style>%s%s</style>%s" % (BASE_CSS, css, body), title)


def d(s):
    """animation-delay attribute."""
    return ' style="animation-delay:%ss"' % _fmt(s)


def S(c):
    return SIG[c["mode"]]


def mono(x, y, s, size, fill, anchor="start", bold=False, track=0.0):
    return text(x, y, s, "mb" if bold else "mr", size, fill, anchor, track)


def grid_bg(W, H, c, rx=18, step=22):
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
           ".22", c["brand"], W - 1, H - 1, rx, c["ground"], c["hair"], W, H)
    )


# ------------------------------------------------------------------------------------- hero
WORDS = ["AI agents", "AI regulation", "post-quantum migration", "OT networks"]
LANES = ["AI SECURITY", "AI GOVERNANCE", "POST-QUANTUM", "OT SECURITY"]
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
THESIS = "The question behind everything I build: what control proves this is safe, and what evidence shows it is working?"


def console(x, y, w, fs, c):
    s = S(c)
    cw = fs * 0.6                       # JetBrains Mono advance = 600/1000 em
    lh = round(fs * 1.75)
    h = 46 + lh * (len(CONSOLE) + 3) + 14
    b = ['<g class="fi"%s>' % d(0.15)]
    b.append('<rect x="%s" y="%s" width="%s" height="%s" rx="12" fill="%s" stroke="%s"/>' % (x + .5, y + .5, w - 1, h - 1, s["term"], s["termhair"]))
    b.append('<path d="M%s %s H%s" stroke="%s"/>' % (x, y + 34.5, x + w, s["termhair"]))
    b.append(mono(x + 16, y + 22, "evidence-engine", fs - 1, s["termink"], bold=True))
    b.append(mono(x + w - 16, y + 22, "example run", fs - 1.5, s["termmute"], anchor="end"))
    b.append('<circle class="pl" cx="%s" cy="%s" r="3.5" fill="%s"/>' % (_fmt(x + w - 16 - width("example run", "mr", fs - 1.5) - 12), y + 18, s["ok"]))
    b.append("</g>")
    ty = y + 34 + lh + 4
    cmd = 'prove --claim "agent tool calls are safe"'
    b.append(mono(x + 16, ty, "$", fs, s["termacc"], bold=True))
    b.append(mono(x + 16 + cw * 2, ty, cmd, fs, s["termink"]))
    # typing: a cover in the console colour shrinks toward the right edge of the command in
    # character steps (scaleX, origin right), so it never paints outside the text. Base = scaleX(0).
    n = len(cmd)
    b.append('<rect class="ty" x="%s" y="%s" width="%s" height="%s" fill="%s" style="animation-duration:1.5s;'
             'animation-timing-function:steps(%d);animation-delay:.6s"/>' % (_fmt(x + 16 + cw * 2 - 1), ty - fs, _fmt(cw * n + 3), fs + 6, s["term"], n))
    css = ".ty{transform-box:fill-box;transform-origin:right center;transform:scaleX(0);animation-name:ty;animation-fill-mode:both}@keyframes ty{from{transform:scaleX(1)}}"
    t0 = 2.3
    for i, (verb, subj, ref, st) in enumerate(CONSOLE):
        ly = ty + lh * (i + 1)
        b.append('<g class="fi"%s>' % d(t0 + i * 0.32))
        b.append(mono(x + 16 + cw * 2, ly, verb, fs, s["termacc"]))
        b.append(mono(x + 16 + cw * 8, ly, subj, fs, s["termink"]))
        if ref:
            b.append(mono(x + w - 16, ly, ref, fs, s["termmute"], anchor="end"))
        if st:
            b.append(mono(x + w - 16, ly, st, fs, s["ok"], anchor="end", bold=True))
        b.append("</g>")
    ly = ty + lh * (len(CONSOLE) + 1) + 2
    tend = t0 + len(CONSOLE) * 0.32 + 0.2
    b.append('<path class="fo"%s d="M%s %s H%s" stroke="%s" stroke-dasharray="3 4"/>' % (d(tend), x + 16, ly - fs - 2, x + w - 16, s["termhair"]))
    b.append('<g class="fi"%s>' % d(tend + 0.2))
    b.append(mono(x + 16, ly + 6, "evidence", fs, s["termmute"]))
    b.append(mono(x + 16 + cw * 9, ly + 6, "6/6 attached", fs, s["ok"], bold=True))
    end = x + 16 + cw * 22
    b.append(mono(end, ly + 6, "OSCAL", fs, s["termink"]))
    b.append('<rect class="bl" x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (_fmt(end + cw * 6), ly + 6 - fs * 0.78, _fmt(cw * 0.9), _fmt(fs * 0.95), s["termacc"]))
    b.append("</g>")
    return "".join(b), h, css


def hero(c, m="d"):
    s = S(c)
    acc = c["accent"]
    if m == "d":
        W, H, P = 840, 404, 44
    else:
        W, H, P = 420, 0, 24
    parts = []
    # left / top text column
    ns, ts, rs = (52, 19, 22) if m == "d" else (36, 15, 17)
    y = 58 if m == "d" else 46
    parts.append('<g class="fi">')
    parts.append('<circle class="pl" cx="%s" cy="%s" r="4" fill="%s"/>' % (P + 4, y - 4, s["ok"]))
    parts.append(mono(P + 16, y, "~/john-b-joseph", 12 if m == "d" else 11, c["mute"]))
    parts.append("</g>")
    y += 18 + ns * 0.72
    parts.append('<g class="fi"%s>' % d(0.1))
    parts.append(text(P - K._left_bearing("b", "J", ns), y, "John B Joseph", "b", ns, c["ink"], track=-1.2))
    y += ts + 14
    parts.append(text(P, y, "Co-founder & CPTO, Purplecop Security", "m", ts, c["body"]))
    parts.append("</g>")
    y += rs + 26
    lead = "Securing "
    parts.append(text(P, y, lead, "s", rs, c["ink"]))
    wx = P + width(lead, "s", rs)
    css = ("@keyframes rw{0%{opacity:0;transform:translateY(10px)}3%,22%{opacity:1;transform:none}"
           "25%,100%{opacity:0;transform:translateY(-10px)}}.rw{animation:rw 12s cubic-bezier(.2,.7,.2,1) infinite both}")
    for i, wd in enumerate(WORDS):
        op = "" if i == 0 else ' opacity="0"'
        parts.append('<g class="rw"%s%s>%s</g>' % (op, d(i * 3), text(wx, y, wd, "s", rs, acc)))
    colw = (452 - P - 28) if m == "d" else (W - 2 * P)
    y += 30
    tl = wrap(THESIS, "r", 15 if m == "d" else 13.5, colw, 4)
    parts.append('<g class="fi"%s>' % d(0.5))
    for i, ln in enumerate(tl):
        parts.append(text(P, y + i * (24 if m == "d" else 21), ln, "r", 15 if m == "d" else 13.5, c["mute"]))
    parts.append("</g>")
    y += (len(tl) - 1) * (24 if m == "d" else 21)
    if m == "d":
        cb, ch, ccss = console(452, 36, 344, 12, c)
        lane_y = 362
    else:
        cb, ch, ccss = console(P, y + 26, W - 2 * P, 10.5, c)
        lane_y = y + 26 + ch + 44
    parts.append(cb)
    css += ccss
    # lane strip
    ly = lane_y
    parts.append('<path d="M%d %s H%d" stroke="%s"/>' % (P, _fmt(ly - 26.5), W - P, c["hair"]))
    parts.append('<path class="dr gx" pathLength="1" d="M%d %s H%d" stroke="%s" stroke-width="2"/>' % (P, _fmt(ly - 26.5), P + 64, c["brand"]))
    ls = 11.5 if m == "d" else 10
    if m == "d":
        units = [12 + width(t, "mr", ls, 1.2) for t in LANES]
        gap = (W - 2 * P - sum(units)) / 3.0
        x = P
        pos = []
        for u in units:
            pos.append((x, ly))
            x += u + gap
    else:
        pos = [(P, ly), (W / 2 + 4, ly), (P, ly + 26), (W / 2 + 4, ly + 26)]
        H = int(ly + 26 + 30)
    for i, (t, (x, yy)) in enumerate(zip(LANES, pos)):
        parts.append('<g class="fi"%s><circle cx="%s" cy="%s" r="3.5" fill="%s"/>%s</g>' % (
            d(0.9 + i * 0.12), _fmt(x + 3.5), _fmt(yy - 4), c["accent"], mono(x + 13, yy, t, ls, c["ink"], track=1.2)))
    bg = grid_bg(W, H, c)
    glow = '<circle cx="%s" cy="%s" r="%s" fill="url(#gl)"/>' % ((640, 40, 300) if m == "d" else (380, 30, 220))
    body = bg + glow + "</g>" + "".join(parts)
    return svg(W, H, body, "John B Joseph. Co-founder and CPTO, Purplecop Security. Securing AI agents, AI regulation, "
               "post-quantum migration and OT networks. " + THESIS, css)


# ------------------------------------------------------------------------------------ stats
def stats(items, c, m="d"):
    """items: (value, label, itemization). Itemization is shown so every derived number can be
    checked by hand."""
    W = 840 if m == "d" else 420
    cols = 4 if m == "d" else 2
    cw = W / cols
    rh = 118
    rows = (len(items) + cols - 1) // cols
    H = rh * rows
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="14" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
    for i in range(1, cols):
        b.append('<path d="M%s 18 V%d" stroke="%s"/>' % (_fmt(cw * i), H - 18, c["hair"]))
    for r in range(1, rows):
        b.append('<path d="M18 %d H%d" stroke="%s"/>' % (rh * r, W - 18, c["hair"]))
    vs = 36 if m == "d" else 30
    for i, (val, lab, sub) in enumerate(items):
        x = (i % cols) * cw + (24 if m == "d" else 18)
        y = (i // cols) * rh
        b.append('<g class="fi"%s>' % d(0.1 + i * 0.12))
        b.append(text(x, y + 52, val, "b", vs, c["ink"], track=-0.8))
        b.append(text(x, y + 76, lab, "s", 13.5 if m == "d" else 12.5, c["body"]))
        b.append(mono(x, y + 96, sub, 10.5 if m == "d" else 9.5, c["mute"]))
        b.append("</g>")
        assert width(sub, "mr", 10.5 if m == "d" else 9.5) < cw - 30, sub
        assert width(lab, "s", 13.5 if m == "d" else 12.5) < cw - 30, lab
        b.append('<rect class="gx"%s x="%s" y="%d" width="%s" height="2" rx="1" fill="%s"/>' % (
            d(0.4 + i * 0.12), _fmt(x), y + rh - 12, 40, c["accent"]))
    return svg(W, H, "".join(b), ". ".join("%s %s (%s)" % it for it in items))


# ---------------------------------------------------------------------------------- section
def section(path, title, caption, c, m="d"):
    W = 840 if m == "d" else 420
    H = 74
    ts = 28 if m == "d" else 22
    b = [mono(0, 22, path, 12, c["page_acc"])]
    b.append('<g class="fi">%s</g>' % text(0, 56, title, "b", ts, c["page_ink"], track=-0.4))
    if caption:
        if m == "d":
            b.append(mono(W, 54, caption, 11.5, c["page_mute"], anchor="end"))
        else:
            b.append(mono(W, 22, caption, 10, c["page_mute"], anchor="end"))
    b.append('<path d="M0 %s H%d" stroke="%s"/>' % (H - 1.5, W, c["page_hair"]))
    b.append('<rect class="gx" x="0" y="%d" width="56" height="3" rx="1.5" fill="%s"/>' % (H - 3, c["brand"]))
    return svg(W, H, "".join(b), "%s. %s" % (title, caption) if caption else title)


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
            b.append('<path class="dr" pathLength="1"%s d="M%s %s C%s %s %s %s %s %s" fill="none" stroke="%s" stroke-width="1.3" opacity=".8"/>' % (
                d(0.4 + k * 0.18), x1, y1, x1 + 46, y1, x2 - 46, y2, x2, y2, a))
        for (px, py) in L:
            b.append('<circle cx="%s" cy="%s" r="3.5" fill="%s"/>' % (px, py, c["ink"]))
        for k, (px, py) in enumerate(R):
            b.append('<circle class="pp"%s cx="%s" cy="%s" r="3" fill="%s"/>' % (d(1.2 + k * 0.15), px, py, a))
    elif kind == "oscal":
        for i, (lab, w) in enumerate([("L", 34), ("M", 60), ("H", 86)]):
            yy = y + 4 + i * 13
            b.append(mono(x, yy + 7, lab, 9.5, c["mute"], bold=True))
            b.append('<rect x="%s" y="%s" width="86" height="7" rx="3.5" fill="%s"/>' % (x + 14, yy, c["chipbg"]))
            b.append('<rect class="gx"%s x="%s" y="%s" width="%s" height="7" rx="3.5" fill="%s"/>' % (d(0.4 + i * 0.25), x + 14, yy, w, a))
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
            b.append('<rect class="gy"%s x="%s" y="%s" width="9" height="%s" rx="2" fill="%s" opacity="%s"/>' % (
                d(0.3 + i * 0.1), x + 6 + i * 12.5, y + 40 - h, h, a, _fmt(0.45 + i * 0.07)))
    elif kind == "sheets":
        for i in range(4):
            sx = x + 4 + i * 25
            b.append('<rect x="%s" y="%s" width="20" height="28" rx="3" fill="%s" stroke="%s"/>' % (sx, y + 6, c["panel"], c["hair"]))
            for r in range(4):
                b.append('<rect class="gx"%s x="%s" y="%s" width="%s" height="2.4" rx="1.2" fill="%s"/>' % (
                    d(0.4 + i * 0.15 + r * 0.08), sx + 4, y + 12 + r * 5, 12 if r % 2 else 9, a if r == 0 else c["mute"]))
    return "".join(b)


# ----------------------------------------------------------------------------------- cards
CARD_W, CARD_H = 406, 236


def card(tag, title, body, metrics, kind, c):
    W, H = CARD_W, CARD_H
    a = c["accent"]
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="12" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
    b.append(mono(24, 34, tag, 10.5, a, bold=True, track=1.4))
    # arrow-out mark, top right
    b.append('<g transform="translate(%d 20)" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round"><path d="M3 13 L13 3 M5 3 H13 V11"/></g>' % (W - 40, c["mute"]))
    tl = wrap(title, "s", 18.5, W - 48, 2)
    y = 66
    for ln in tl:
        b.append(text(24, y, ln, "s", 18.5, c["ink"], track=-0.2))
        y += 25
    bl = wrap(body, "r", 13.5, W - 48, 5 - len(tl))
    y += 2
    for ln in bl:
        b.append(text(24, y, ln, "r", 13.5, c["body"]))
        y += 20
    assert y <= H - 50, (title, y)
    b.append('<path d="M24 %d H%d" stroke="%s"/>' % (H - 56, W - 24, c["hair"]))
    x = 24
    for val, lab in metrics:
        b.append(text(x, H - 22, val, "b", 19, c["ink"], track=-0.3))
        x += width(val, "b", 19, -0.3) + 6
        b.append(mono(x, H - 23, lab, 10, c["mute"]))
        x += width(lab, "mr", 10) + 18
    assert x < W - 24 - 104 - 4, (title, x)
    b.append(motif(kind, W - 24 - 104, H - 46, c))
    alt = "%s. %s %s" % (title, body, " ".join("%s %s" % mm for mm in metrics))
    return svg(W, H, "".join(b), alt.strip())


def feature(tag, title, body, metrics, c, m="d"):
    """The wide GRC Practice Lab card: text left, a live control heatmap right."""
    W = 840 if m == "d" else 420
    a = c["accent"]
    s = S(c)
    tw = 420 if m == "d" else W - 48
    tl = wrap(body, "r", 14 if m == "d" else 13, tw, 4)
    H = 268 if m == "d" else 250 + 22 * len(tl) + 120
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="12" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
    b.append('<circle class="pl" cx="30" cy="30" r="4" fill="%s"/>' % s["ok"])
    b.append(mono(42, 34, tag, 10.5, a, bold=True, track=1.4))
    b.append('<g transform="translate(%d 20)" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round"><path d="M3 13 L13 3 M5 3 H13 V11"/></g>' % (W - 40, c["mute"]))
    b.append(text(24, 74, title, "b", 26 if m == "d" else 22, c["ink"], track=-0.5))
    y = 104
    for ln in tl:
        b.append(text(24, y, ln, "r", 14 if m == "d" else 13, c["body"]))
        y += 22
    # metrics: 2 x 2 under the text
    my = y + 22
    for i, (val, lab) in enumerate(metrics):
        mx = 24 + (i % 2) * (tw / 2)
        yy = my + (i // 2) * 44
        b.append(text(mx, yy, val, "b", 22, c["ink"], track=-0.4))
        b.append(mono(mx + width(val, "b", 22, -0.4) + 8, yy - 1, lab, 10.5, c["mute"]))
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
            fill = s["ok"] if v > 0.62 else "#8a6514" if v > 0.3 else c["chipbg"]
            op = "1" if v > 0.62 else _fmt(0.35 + v)
            b.append('<rect class="pp"%s x="%s" y="%s" width="%d" height="%d" rx="3" fill="%s" opacity="%s"/>' % (
                d(0.2 + (r + k) * 0.035), gx + k * (cs + gp), gy + r * (cs + gp), cs, cs, fill, op))
    ly = gy + rows * (cs + gp) + 16
    lg = [("implemented", s["ok"]), ("in progress", "#8a6514"), ("not started", c["chipbg"])]
    lx = gx
    for lab, col in lg:
        b.append('<rect x="%s" y="%s" width="10" height="10" rx="2" fill="%s" stroke="%s"/>' % (lx, ly - 9, col, c["hair"]))
        b.append(mono(lx + 15, ly, lab, 10, c["mute"]))
        lx += 15 + width(lab, "mr", 10) + 16
    b.append(mono(gx, ly + 20, "illustration of a learner's control board", 9.5, c["mute"]))
    H = int(ly + 40) if m == "m" else int(max(yend + 26, ly + 36))
    b[0] = '<rect x=".5" y=".5" width="%d" height="%d" rx="12" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])
    alt = "%s. %s %s" % (title, body, " ".join("%s %s" % mm for mm in metrics))
    return svg(W, H, "".join(b), alt)


# ------------------------------------------------------------------------- contributions chart
STATUS = {  # label, kind of mark
    "merged": ("merged / accepted", "fill"),
    "pr": ("open PR", "ring"),
    "proposed": ("proposed", "ring2"),
}


def contrib_kind(dd, parse_ref):
    st = dd.get("status", "").lower()
    if st in ("merged", "accepted"):
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
    b = ['<rect x=".5" y=".5" width="%d" height="%d" rx="14" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"])]
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
                b.append('<circle class="ring"%s cx="%s" cy="%s" r="%s" fill="none" stroke="%s"/>' % (d(1.8 + j * 0.4), _fmt(px), _fmt(py), r, s["ok"]))
            idx += 1
        lab = (d0 + dt.timedelta(days=di)).strftime("%d")
        if m == "d" or di % 2 == 0 or di == n - 1:
            b.append(mono(cx, base + 22, lab, 10 if m == "d" else 9, c["mute"], anchor="middle"))
    mon = d0.strftime("%b %Y").upper()
    b.append(mono(left - 6, base + 40, mon, 9.5, c["mute"]))
    alt = "Contributions by day, %s to %s: %d merged or accepted, %d open PRs, %d proposed." % (
        days[0], days[-1], counts["merged"], counts["pr"], counts["proposed"])
    return svg(W, H, "".join(b), alt)


def _mark(x, y, r, k, a, s, c, delay=None):
    dl = d(delay) if delay is not None else ""
    cls = ' class="pp"' if delay is not None else ""
    if k == "merged":
        return '<circle%s%s cx="%s" cy="%s" r="%s" fill="%s"/>' % (cls, dl, _fmt(x), _fmt(y), r, s["ok"])
    if k == "pr":
        return '<circle%s%s cx="%s" cy="%s" r="%s" fill="%s" fill-opacity=".25" stroke="%s" stroke-width="1.6"/>' % (cls, dl, _fmt(x), _fmt(y), _fmt(r - 0.6), a, a)
    return '<circle%s%s cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (cls, dl, _fmt(x), _fmt(y), _fmt(r - 0.6), c["mute"])


# ---------------------------------------------------------------------------- contribution row
def row(dd, label, ref_txt, c, m="d"):
    s = S(c)
    a = c["accent"]
    W = 840 if m == "d" else 420
    merged = label in ("MERGED", "ACCEPTED")
    pill_fill = s["ok"] if merged else "none"
    pill_ink = c["ground"] if merged else (a if label == "OPEN PR" else c["mute"])
    pill_stroke = s["ok"] if merged else (a if label == "OPEN PR" else c["mute"])
    pw = width(label, "mb", 9.5, 1) + 18
    b = []
    if m == "d":
        rw = width(ref_txt, "mb", 11.5)
        tl = wrap(dd["title"], "r", 13.5, W - 244 - 20 - rw - 28, 3)
        H = 84 if len(tl) <= 2 else 100
        b.append('<rect x=".5" y=".5" width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>' % (W - 1, H - 1, c["panel"], c["hair"]))
        oy = (H - 84) / 2
        b.append('<rect x="20.5" y="%s" width="%s" height="19" rx="9.5" fill="%s" stroke="%s"/>' % (_fmt(16.5 + oy), _fmt(pw), pill_fill, pill_stroke))
        b.append(mono(29.5, 29.5 + oy, label, 9.5, pill_ink, bold=True, track=1))
        name = wrap(dd["project"], "s", 15, 210, 1)[0]
        b.append(text(20, 58 + oy, name, "s", 15, c["ink"]))
        b.append(mono(20, 74 + oy, dd.get("area", ""), 10, c["mute"]))
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
        b.append(mono(27.5, 29.5, label, 9.5, pill_ink, bold=True, track=1))
        b.append(mono(W - 18, 30, ref_txt, 10.5, a, anchor="end", bold=True))
        b.append(text(18, 62, wrap(dd["project"], "s", 15, W - 36, 1)[0], "s", 15, c["ink"]))
        b.append(mono(18, 79, dd.get("area", ""), 9.5, c["mute"]))
        for i, ln in enumerate(tl):
            b.append(text(18, 104 + i * 19, ln, "r", 12.5, c["body"]))
    alt = "%s: %s. %s. %s" % (label.title(), dd["project"], dd["title"], ref_txt)
    return svg(W, H, "".join(b), alt)


# ------------------------------------------------------------------------------- focus + misc
FOCUS_ICON_CSS = ""


def focus(title, ic, body, c, H=None):
    W = CARD_W
    a = c["accent"]
    lines = wrap(body, "r", 14, W - 48, 4)
    H = H or 100 + 21 * len(lines)
    b = ['<rect x=".5" y=".5" width="%d" height="%s" rx="12" fill="%s" stroke="%s"/>' % (W - 1, _fmt(H - 1), c["panel"], c["hair"])]
    b.append('<rect x="24" y="22" width="36" height="36" rx="9" fill="%s" stroke="%s"/>' % (c["chipbg"], c["hair"]))
    b.append('<g class="fi"%s>%s</g>' % (d(0.2), K.icon(ic, 32, 30, 20, a)))
    b.append(text(74, 46, title, "s", 18.5, c["ink"], track=-0.2))
    for i, ln in enumerate(lines):
        b.append(text(24, 88 + 21 * i, ln, "r", 14, c["body"]))
    return svg(W, H, "".join(b), "%s. %s" % (title, body))


def focus_height(body):
    return 100 + 21 * len(wrap(body, "r", 14, CARD_W - 48, 4))


def creds(items, c, H):
    W = CARD_W
    a = c["accent"]
    b = ['<rect x=".5" y=".5" width="%d" height="%s" rx="12" fill="%s" stroke="%s"/>' % (W - 1, _fmt(H - 1), c["panel"], c["hair"])]
    b.append(mono(24, 34, "CREDENTIALS", 10.5, a, bold=True, track=1.4))
    for r, rw in enumerate(K._chip_rows(items, W, x0=24)):
        y = 52 + r * 36
        for k, (x, it, cw) in enumerate(rw):
            b.append('<g class="fi"%s><rect x="%s" y="%d" width="%s" height="27" rx="6" fill="%s" stroke="%s"/>%s</g>' % (
                d(0.1 + (r * 3 + k) * 0.06), _fmt(x + .5), y, _fmt(cw - 1), c["chipbg"], c["hair"], text(x + 13, y + 18.2, it, "m", 13, c["chipink"])))
    return svg(W, H, "".join(b), "Credentials: " + ", ".join(items))


def creds_height(items):
    return 52 + len(K._chip_rows(items, CARD_W, x0=24)) * 36 + 12


def teach(value, l1, l2, body, c, H):
    W = CARD_W
    s = S(c)
    a = c["accent"]
    b = ['<rect x=".5" y=".5" width="%d" height="%s" rx="12" fill="%s" stroke="%s"/>' % (W - 1, _fmt(H - 1), c["panel"], c["hair"])]
    b.append('<circle class="pl" cx="30" cy="30" r="4" fill="%s"/>' % s["ok"])
    b.append(mono(42, 34, "TEACHING", 10.5, a, bold=True, track=1.4))
    b.append('<g class="fi">%s</g>' % text(24, 96, value, "b", 46, c["ink"], track=-1.2))
    vw = width(value, "b", 46, -1.2)
    b.append(text(24 + vw + 14, 76, l1, "s", 16, c["ink"]))
    b.append(text(24 + vw + 14, 98, l2, "m", 16, c["mute"]))
    for i, ln in enumerate(wrap(body, "r", 14, W - 48, 4)):
        b.append(text(24, 134 + 21 * i, ln, "r", 14, c["body"]))
    return svg(W, H, "".join(b), "Teaching: %s %s %s. %s" % (value, l1, l2, body))


def teach_height(body):
    return 134 + 21 * len(wrap(body, "r", 14, CARD_W - 48, 4)) + 4


def pill(label, ic, c, h=34):
    fs = 13.5
    tw = width(label, "s", fs)
    W = 14 + 16 + 9 + tw + 16
    b = '<rect x=".5" y=".5" width="%s" height="%d" rx="8" fill="%s" stroke="%s"/>' % (_fmt(W - 1), h - 1, c["panel"], c["hair"])
    b += K.icon(ic, 13, (h - 16) / 2, 16, c["accent"])
    b += text(39, h / 2 + fs * 0.36, label, "s", fs, c["ink"])
    return K.svg(W, h, b, label)


def footer(c, m="d"):
    W = 840 if m == "d" else 420
    H = 56
    s = S(c)
    b = ['<path d="M0 .5 H%d" stroke="%s"/>' % (W, c["page_hair"])]
    b.append('<circle class="pl" cx="5" cy="31" r="4" fill="%s"/>' % s["ok"])
    t = "regenerated from the contributions ledger" if m == "d" else "regenerated from the ledger"
    b.append(mono(18, 35, "~/eof", 11.5, c["page_acc"], bold=True))
    b.append(mono(W, 35, t, 11, c["page_mute"], anchor="end"))
    return svg(W, H, "".join(b), "")
