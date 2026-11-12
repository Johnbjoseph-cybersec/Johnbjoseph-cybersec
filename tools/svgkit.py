"""svgkit: tiny stdlib SVG toolkit for the profile README.

GitHub renders README SVGs as plain images: no web fonts, no scripts. So all text is OUTLINED
from Poppins (tools/glyphs.json, made once by extract_glyphs.py) and every asset looks the
same on every device. Nothing here needs a third-party package.
"""
import json
import os
import re
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
_G = json.load(open(os.path.join(HERE, "glyphs.json")))

# Purplecop palette: dark purple ground, brand purple #7B00FF, Poppins (creative kit).
DARK = dict(
    mode="dark", ground="#0a0514", ground2="#06030c", panel="#150b29", hair="#2c1a52",
    ink="#ffffff", body="#c3b8e3", mute="#8f82b8", accent="#a56bff", brand="#7B00FF",
    node="#0a0514", line="#6d3fd1", chipbg="#1a0f33", chipink="#e9ddff",
)
LIGHT = dict(
    mode="light", ground="#f6f3fc", ground2="#efe9fa", panel="#ece6f8", hair="#d6c9ee",
    ink="#150b2b", body="#43386a", mute="#6d6296", accent="#6a00dc", brand="#7B00FF",
    node="#f6f3fc", line="#9b6ce8", chipbg="#e6dcf7", chipink="#2b1760",
)
MODES = (LIGHT, DARK)

_NUM = re.compile(r"([MLHVQCZ])|(-?\d*\.?\d+)")


def _fmt(v):
    s = "%.2f" % v
    return s.rstrip("0").rstrip(".") if "." in s else s


def _xform(d, k, ox, oy):
    """Scale + translate an absolute SVG path string (M L H V Q C Z) from the glyph file."""
    out, cmd, nums = [], "", []
    for m in _NUM.finditer(d):
        if m.group(1):
            if cmd:
                out.append(_emit(cmd, nums, k, ox, oy))
            cmd, nums = m.group(1), []
        else:
            nums.append(float(m.group(2)))
    if cmd:
        out.append(_emit(cmd, nums, k, ox, oy))
    return "".join(out)


def _emit(cmd, nums, k, ox, oy):
    if cmd == "Z":
        return "Z"
    if cmd == "H":
        return "H" + _fmt(nums[0] * k + ox)
    if cmd == "V":
        return "V" + _fmt(nums[0] * k + oy)
    pts = []
    for i in range(0, len(nums), 2):
        pts.append(_fmt(nums[i] * k + ox) + " " + _fmt(nums[i + 1] * k + oy))
    return cmd + " ".join(pts)


def width(s, w="r", size=16, track=0.0):
    f = _G[w]
    k = size / f["upm"]
    return sum(f["g"].get(c, f["g"]["?"])[0] * k + track for c in s) - (track if s else 0)


def text(x, y, s, w="r", size=16, fill="#000", anchor="start", track=0.0, opacity=None):
    """Outlined text as one <path>. y is the baseline."""
    f = _G[w]
    k = size / f["upm"]
    tw = width(s, w, size, track)
    cx = x - (tw if anchor == "end" else tw / 2 if anchor == "middle" else 0)
    parts = []
    for c in s:
        adv, d = f["g"].get(c, f["g"]["?"])
        if d:
            parts.append(_xform(d, k, cx, y))
        cx += adv * k + track
    op = ' fill-opacity="%s"' % opacity if opacity is not None else ""
    return '<path fill="%s"%s d="%s"/>' % (fill, op, "".join(parts))


def wrap(s, w, size, maxw, maxlines):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if width(t, w, size) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        last = lines[-1]
        while width(last + "...", w, size) > maxw and " " in last:
            last = last.rsplit(" ", 1)[0]
        lines[-1] = last + "..."
    return lines


def svg(wd, ht, body, title):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s" '
        'role="img" aria-label="%s"><title>%s</title>%s</svg>\n'
        % (_fmt(wd), _fmt(ht), _fmt(wd), _fmt(ht), escape(title, {'"': "&quot;"}), escape(title), body)
    )


# ---------------------------------------------------------------- icons (24 grid, stroke)
ICONS = {
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3.2 3 3.2 15 0 18M12 3c-3.2 3-3.2 15 0 18"/>',
    "flask": '<path d="M9.5 3h5M10 3v6.2L5.2 17.6A2 2 0 0 0 7 20.6h10a2 2 0 0 0 1.8-3L14 9.2V3M7.6 14.5h8.8"/>',
    "play": '<rect x="2.5" y="5.5" width="19" height="13" rx="3.6"/><path d="M10.2 9v6l5-3z" fill="currentColor"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.4"/><path d="M3.8 7.2l8.2 6 8.2-6"/>',
    "in": '<rect x="3" y="3" width="18" height="18" rx="3.4"/><path d="M8 11v6M12 17v-6M12 13.6c0-1.8 1.3-2.6 2.6-2.6 1.6 0 2.4 1 2.4 2.7V17"/><circle cx="8" cy="8" r="1" fill="currentColor"/>',
    "shield": '<path d="M12 3l7 2.8v5.4c0 4.6-3 8.1-7 9.8-4-1.7-7-5.2-7-9.8V5.8z"/><path d="M8.8 12l2.3 2.3 4.2-4.4"/>',
    "ledger": '<path d="M6 3h8.5L18 6.5V21H6z"/><path d="M14 3v4h4M9 11h6M9 14.5h6M9 18h3.5"/>',
    "lattice": '<path d="M12 3l7.8 4.5v9L12 21l-7.8-4.5v-9z"/><path d="M12 12l7.8-4.5M12 12v9M12 12L4.2 7.5"/>',
    "loop": '<path d="M20 12a8 8 0 1 1-2.5-5.8"/><path d="M20 4v4.5h-4.5"/><path d="M9 12l2 2 4-4"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.7 2.7L16 9.5"/>',
}


def icon(name, x, y, size, color):
    k = size / 24.0
    return (
        '<g transform="translate(%s %s) scale(%s)" fill="none" stroke="%s" color="%s" '
        'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">%s</g>'
        % (_fmt(x), _fmt(y), _fmt(k), color, color, ICONS[name])
    )


# ---------------------------------------------------------------- components
def hero(c):
    """Name, title and three lane tags share one left edge (PAD); tags sit on one baseline,
    each a dot + label, joined by equal-length lines so the gaps are identical."""
    W, H = 840, 246
    PAD = 44
    b = []
    b.append(
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/>'
        '<stop offset="1" stop-color="%s"/></linearGradient></defs>' % (c["ground"], c["ground2"])
    )
    b.append('<rect x="0.5" y="0.5" width="%d" height="%d" rx="22" fill="url(#g)" stroke="%s"/>' % (W - 1, H - 1, c["hair"]))

    # name: cap top sits PAD from the top edge. J has a small left bearing, removed so ink starts at PAD.
    ns = 60
    f = _G["b"]
    k = ns / f["upm"]
    cap = 0.70 * ns
    nb = PAD + cap
    bearing = _left_bearing("b", "J", ns)
    b.append(text(PAD - bearing, nb, "John B Joseph", "b", ns, c["ink"], track=-1.1))
    ts = 22
    tb = nb + 40
    b.append(text(PAD - _left_bearing("m", "C", ts), tb, "Co-founder & CPTO, Purplecop Security", "m", ts, c["body"]))

    # lanes: a hairline (with a short brand cap, as in the footer rule), then the three tags
    ry = tb + 32
    b.append('<path d="M%d %s H%d" stroke="%s" stroke-width="1"/>' % (PAD, _fmt(ry + 0.5), W - PAD, c["hair"]))
    b.append('<rect x="%d" y="%s" width="46" height="4" rx="2" fill="%s"/>' % (PAD, _fmt(ry - 1.5), c["brand"]))
    labels = ["AI security", "AI governance", "Post-quantum readiness"]
    ls, dot_r, gap_dt = 18, 5, 10
    lb = ry + 44                             # lane baseline
    cy = lb - 0.30 * ls                      # dot centre = optical middle of the lowercase body
    unit = [2 * dot_r + gap_dt + width(t, "s", ls) for t in labels]
    gap = ((W - 2 * PAD) - sum(unit)) / 2.0  # identical gap between tags; first starts at PAD, last ends at W-PAD
    x = PAD
    for t, u in zip(labels, unit):
        b.append('<circle cx="%s" cy="%s" r="%d" fill="%s"/>' % (_fmt(x + dot_r), _fmt(cy), dot_r, c["brand"] if c["mode"] == "dark" else c["accent"]))
        b.append(text(x + 2 * dot_r + gap_dt, lb, t, "s", ls, c["ink"]))
        x += u + gap
    return svg(W, H, "".join(b), "John B Joseph. Co-founder and CPTO, Purplecop Security. AI security, AI governance, post-quantum readiness.")


def _left_bearing(w, ch, size):
    """Distance from the glyph origin to its first ink, from the outline's smallest x."""
    d = _G[w]["g"][ch][1]
    xs = [float(v) for m in re.finditer(r"[MLQC]([^MLQCZHV]*)", d) for v in re.findall(r"-?\d*\.?\d+", m.group(1))[0::2]]
    return (min(xs) if xs else 0) * size / _G[w]["upm"]

def pill(label, ic, c, h=32):
    fs = 13.5
    tw = width(label, "s", fs)
    W = 14 + 16 + 8 + tw + 16
    b = '<rect x="0.5" y="0.5" width="%s" height="%d" rx="%s" fill="%s" stroke="%s"/>' % (_fmt(W - 1), h - 1, (h - 1) / 2, c["panel"], c["hair"])
    b += '<circle cx="%s" cy="%s" r="3" fill="%s"/>' % (_fmt(W - 13), h / 2, c["brand"] if c["mode"] == "dark" else c["accent"]) if False else ""
    b += icon(ic, 12, (h - 16) / 2, 16, c["accent"])
    b += text(36, h / 2 + fs * 0.36, label, "s", fs, c["ink"])
    return svg(W, h, b, label)


def band(num, title, caption, c):
    W, H = 840, 56
    b = '<defs><clipPath id="k"><rect x="0.5" y="0.5" width="%d" height="%d" rx="14"/></clipPath></defs>' % (W - 1, H - 1)
    b += '<rect x="0.5" y="0.5" width="%d" height="%d" rx="14" fill="%s"/>' % (W - 1, H - 1, c["panel"])
    b += '<rect x="0" y="0" width="7" height="%d" fill="%s" clip-path="url(#k)"/>' % (H, c["brand"])
    b += '<rect x="0.5" y="0.5" width="%d" height="%d" rx="14" fill="none" stroke="%s"/>' % (W - 1, H - 1, c["hair"])
    b += text(28, 35, num, "m", 15, c["accent"], track=1)
    b += text(62, 37, title, "b", 24, c["ink"], track=-0.3)
    if caption:
        b += text(W - 24, 34, caption, "m", 14, c["mute"], anchor="end")
    return svg(W, H, b, "%s %s" % (title, caption or "") if caption else title)


def subband(title, caption, c):
    W, H = 840, 40
    b = '<path d="M0.5 %s H%d" stroke="%s" stroke-width="1"/>' % (H - 0.5, W, c["hair"])
    b += '<rect x="0" y="10" width="4" height="20" rx="2" fill="%s"/>' % c["brand"]
    b += text(16, 27, title, "s", 19, c["ink"], track=-0.1)
    if caption:
        b += text(W, 26, caption, "m", 14, c["mute"], anchor="end")
    return svg(W, H, b, "%s. %s" % (title, caption) if caption else title)

def chip(label, c, h=28):
    fs = 13
    tw = width(label, "m", fs)
    W = tw + 26
    b = '<rect x="0.5" y="0.5" width="%s" height="%d" rx="%s" fill="%s" stroke="%s"/>' % (_fmt(W - 1), h - 1, (h - 1) / 2, c["chipbg"], c["hair"])
    b += text(13, h / 2 + fs * 0.36, label, "m", fs, c["chipink"])
    return svg(W, h, b, label)


def footer_link(label, ic, c, h=34):
    fs = 14
    tw = width(label, "s", fs)
    W = 14 + 18 + 9 + tw + 16
    b = '<rect x="0.5" y="0.5" width="%s" height="%d" rx="10" fill="none" stroke="%s"/>' % (_fmt(W - 1), h - 1, c["hair"])
    b += icon(ic, 13, (h - 18) / 2, 18, c["accent"])
    b += text(41, h / 2 + fs * 0.36, label, "s", fs, c["ink"])
    return svg(W, h, b, label)


def rule(c):
    W, H = 840, 14
    b = '<path d="M0 7 H%d" stroke="%s" stroke-width="1"/>' % (W, c["hair"])
    b += '<rect x="0" y="4" width="46" height="6" rx="3" fill="%s"/>' % c["brand"]
    return svg(W, H, b, "")


# Opaque two-segment badge: reads on both light and dark GitHub grounds.
def badge(left, right, left_fill="#7B00FF", left_ink="#ffffff", right_fill="#1d1236", right_ink="#e9ddff", h=26):
    fs = 12
    lw = width(left, "b", fs, 0.8) + 20
    rw = width(right, "m", fs + 0.5) + 20 if right else 0
    W = lw + rw
    clip = '<clipPath id="r"><rect width="%s" height="%d" rx="%s"/></clipPath>' % (_fmt(W), h, h / 2)
    b = '<defs>%s</defs><g transform="translate(0 6)"><g clip-path="url(#r)">' % clip
    b += '<rect width="%s" height="%d" fill="%s"/>' % (_fmt(lw), h, left_fill)
    if right:
        b += '<rect x="%s" width="%s" height="%d" fill="%s"/>' % (_fmt(lw), _fmt(rw), h, right_fill)
    b += "</g>"
    b += text(10, h / 2 + fs * 0.36, left, "b", fs, left_ink, track=0.8)
    if right:
        b += text(lw + 10, h / 2 + fs * 0.36, right, "m", fs + 0.5, right_ink)
    return svg(W, h + 6, b + "</g>", ("%s %s" % (left, right)).strip())


CARD_W = 406


def _card_base(H, num, title, c, ic=None):
    W = CARD_W
    b = '<defs><clipPath id="k"><rect x="0.5" y="0.5" width="%d" height="%s" rx="14"/></clipPath></defs>' % (W - 1, _fmt(H - 1))
    b += '<rect x="0.5" y="0.5" width="%d" height="%s" rx="14" fill="%s"/>' % (W - 1, _fmt(H - 1), c["panel"])
    b += '<rect x="0" y="0" width="7" height="%s" fill="%s" clip-path="url(#k)"/>' % (_fmt(H), c["brand"])
    b += '<rect x="0.5" y="0.5" width="%d" height="%s" rx="14" fill="none" stroke="%s"/>' % (W - 1, _fmt(H - 1), c["hair"])
    x = 28
    if ic:
        b += icon(ic, x, 20, 28, c["accent"])
        x += 40
    if num:
        b += text(x, 42, num, "m", 16, c["accent"], track=1)
        x += width(num, "m", 16, 1) + 12
    b += text(x, 43, title, "b", 21, c["ink"], track=-0.2)
    return b


def text_card(title, ic, body, c, H=None):
    lines = wrap(body, "r", 15.5, CARD_W - 28 - 24, 6)
    H = H or 70 + 24 * len(lines) + 16
    b = _card_base(H, None, title, c, ic)
    for i, ln in enumerate(lines):
        b += text(28, 82 + 24 * i, ln, "r", 15.5, c["body"])
    return svg(CARD_W, H, b, "%s. %s" % (title, body))


def text_card_height(body):
    return 70 + 24 * len(wrap(body, "r", 15.5, CARD_W - 28 - 24, 6)) + 16


def _chip_rows(items, W, fs=13, h=28, gap=8, x0=28):
    rows, x, row = [], x0, []
    for it in items:
        cw = width(it, "m", fs) + 26
        if x + cw > W - 20 and row:
            rows.append(row)
            x, row = x0, []
        row.append((x, it, cw))
        x += cw + gap
    rows.append(row)
    return rows


def credentials_height(items):
    return 70 + len(_chip_rows(items, CARD_W)) * 36 + 14


def credentials_card(num, title, items, c, H):
    b = _card_base(H, num, title, c)
    fs, h = 13, 28
    for r, row in enumerate(_chip_rows(items, CARD_W)):
        y = 70 + r * 36
        for x, it, cw in row:
            b += '<rect x="%s" y="%d" width="%s" height="%d" rx="%s" fill="%s" stroke="%s"/>' % (_fmt(x + .5), y, _fmt(cw - 1), h - 1, (h - 1) / 2, c["chipbg"], c["hair"])
            b += text(x + 13, y + h / 2 + fs * 0.36, it, "m", fs, c["chipink"])
    return svg(CARD_W, H, b, "%s: %s" % (title, ", ".join(items)))


def stat_card(num, title, value, label, body, c, H):
    b = _card_base(H, num, title, c)
    b += text(28, 118, value, "b", 46, c["accent"], track=-1)
    vw = width(value, "b", 46, -1)
    b += text(28 + vw + 14, 98, label[0], "s", 17, c["ink"])
    b += text(28 + vw + 14, 122, label[1], "m", 17, c["mute"])
    for i, ln in enumerate(wrap(body, "r", 15.5, CARD_W - 28 - 24, 4)):
        b += text(28, 158 + 24 * i, ln, "r", 15.5, c["body"])
    return svg(CARD_W, H, b, "%s: %s %s. %s" % (title, value, " ".join(label), body))


def stat_card_height(body):
    return 158 + 24 * len(wrap(body, "r", 15.5, CARD_W - 28 - 24, 4)) - 8
