#!/usr/bin/env python3
"""Regenerate the profile: SVG assets + README.md. Standard library only.

    python3 tools/build_profile.py                      # uses ../../contributions.json
    python3 tools/build_profile.py --data PATH.json     # or CONTRIBUTIONS_JSON=PATH

Reads the contributions ledger, then rewrites
  assets/contrib/<id>.svg      one status badge per contribution (status + PR/issue number)
  assets/{light,dark}/...      the themed panels (static; rewritten only if bytes change)
  README.md                    from tools/README.template.md (contributions tables filled in)
Open items are never labelled merged or accepted: only status "merged" / "accepted" in the
ledger go in the Merged table; everything else is shown as OPEN PR or PROPOSED.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import svgkit as K  # noqa: E402

FLAGSHIPS = [  # ledger ids, in display order
    "promptfoo-12396",
    "ai-governance-framework-449",
    "trivy-discussion-11625",
    "osv-scanner-97",
]
MERGED_STATES = {"merged", "accepted"}

PILLS = [
    ("website", "Website", "globe"),
    ("lab", "GRC Practice Lab", "flask"),
    ("youtube", "YouTube", "play"),
    ("newsletter", "Newsletter", "mail"),
    ("linkedin", "LinkedIn", "in"),
]
FOOTER = [("website", "Website", "globe"), ("linkedin", "LinkedIn", "in"), ("youtube", "GRC Made Simple", "play")]
FOCUS = [
    ("ai-security", "AI security", "shield",
     "Controls for AI agents: tool-call authorization, runtime governance, agent identity, audit trails that hold up."),
    ("ai-governance", "AI governance", "ledger",
     "ISO/IEC 42001, the EU AI Act, NIST AI RMF and India's DPDP Act, turned into controls a team can actually operate."),
    ("pqc", "Post-quantum readiness", "lattice",
     "Cryptographic inventory, crypto-agility and migration governance, framed as a risk programme rather than an algorithm swap."),
    ("grc-eng", "GRC engineering", "loop",
     "Continuous evidence instead of annual audits, controls as code, multi-framework crosswalks using NIST IR 8477 set-theory mapping."),
]
TEACH_TEXT = ("GRC Made Simple teaches GRC for free: the GRC Practice Lab, a YouTube channel and a daily newsletter "
              "brief on AI security, AI governance and PQC.")
CREDENTIALS = [
    "ISO/IEC 27001:2022 Lead Auditor", "ISO/IEC 42001:2023 Lead Auditor", "ISO/IEC 27701 Lead Auditor",
    "CCEP", "PrivacyOps", "AI Security & Governance", "AWS Solutions Architect", "Qualys VMDR",
    "TryHackMe Top 1%",
]
TEMPLATE_CHIPS = ["ISO 27001", "ISO 42001", "SOC 2", "NIST CSF"]
STATIC_BANDS = [("built", "01", "Built", ""), ("focus", "03", "Focus", ""), ("speaking", "06", "Speaking", "")]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def write(path, content):
    path = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and open(path, encoding="utf-8").read() == content:
        return
    open(path, "w", encoding="utf-8").write(content)


# ------------------------------------------------------------------ static themed assets
def themed(name, fn):
    for c in K.MODES:
        write("assets/%s/%s.svg" % (c["mode"], name), fn(c))


def build_static(counts):
    themed("hero", K.hero)
    for key, label, ic in PILLS:
        themed("pill-" + key, lambda c, l=label, i=ic: K.pill(l, i, c))
    for key, label, ic in FOOTER:
        themed("foot-" + key, lambda c, l=label, i=ic: K.footer_link(l, i, c))
    for key, num, title, cap in STATIC_BANDS:
        themed("band-" + key, lambda c, n=num, t=title, p=cap: K.band(n, t, p, c))
    themed("band-oss", lambda c: K.band("02", "Open-source work", counts, c))
    fh = max(K.text_card_height(t) for _, _, _, t in FOCUS)
    for key, label, ic, body in FOCUS:
        themed("focus-" + key, lambda c, l=label, i=ic, t=body: K.text_card(l, i, t, c, fh))
    ph = max(K.credentials_height(CREDENTIALS), K.stat_card_height(TEACH_TEXT))
    themed("panel-credentials", lambda c: K.credentials_card("04", "Credentials", CREDENTIALS, c, ph))
    themed("panel-teaching", lambda c: K.stat_card("05", "Teaching", "12,000+", ("active users", "in 34 countries"), TEACH_TEXT, c, ph))
    for label in TEMPLATE_CHIPS:
        themed("chip-" + slug(label), lambda c, l=label: K.chip(l, c))
    themed("rule", K.rule)
    for lab, val in [("provisions", "48"), ("mappings", "157"), ("provisions", "99"), ("mappings", "285"), ("controls", "387"), ("profiles", "3"), ("controls", "400+"), ("frameworks", "9"),
                     ("guided scenarios", "11"), ("portfolio projects", "12")]:
        write("assets/badges/%s-%s.svg" % (slug(val), slug(lab)), K.badge(val, lab))


# ------------------------------------------------------------------ contributions
def parse_ref(url):
    m = re.search(r"github\.com/([^/]+)/([^/]+)/(pull|issues|discussions)/(\d+)", url)
    if not m:
        return None
    owner, repo, kind, num = m.groups()
    return owner, repo, {"pull": "PR", "issues": "issue", "discussions": "discussion"}[kind], num


def status_style(d):
    s = d.get("status", "").lower()
    ref = parse_ref(d["url"])
    kind = ref[2] if ref else "item"
    if s == "merged":
        return "MERGED", "#7B00FF", "#ffffff"
    if s == "accepted":
        return "ACCEPTED", "#5b21b6", "#ffffff"
    if kind == "PR":
        return "OPEN PR", "#e9ddff", "#3b1a8a"
    return "PROPOSED", "#e9ddff", "#3b1a8a"


def short(title, n=200):
    title = re.sub(r"\s*\(flagship F\d+\)", "", title)  # internal tracking tag, not for the public page
    if len(title) <= n:
        return title
    cut = title[:n]
    for sep in ("; ", ", "):  # prefer a clean clause break over a mid-phrase ellipsis
        if sep in cut[n // 2:]:
            return cut[: cut.rindex(sep)].rstrip(",;:")
    return cut.rsplit(" ", 1)[0].rstrip(",;:") + "..."


def cell(s):
    return s.replace("|", "&#124;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ")


def row(d):
    ref = parse_ref(d["url"])
    label, fill, ink = status_style(d)
    right = ("%s #%s" % (ref[2], ref[3])) if ref else d.get("date", "")
    write("assets/contrib/%s.svg" % d["id"], K.badge(label, right, left_fill=fill, left_ink=ink))
    alt = "%s, %s" % (label.title(), right)
    name = "%s/%s" % (ref[0], ref[1]) if ref else d["project"]
    proj = "**[%s](%s)**<br>%s" % (cell(d["project"]), d["url"], cell(d.get("area", "")))
    body = "%s<br><sub>%s</sub><br><a href=\"%s\"><img src=\"assets/contrib/%s.svg\" alt=\"%s\" height=\"32\"></a>" % (
        cell(short(d["title"])), cell(name), d["url"], d["id"], alt)
    return "| %s | %s |" % (proj, body)


def tables(data):
    byid = {d["id"]: d for d in data}
    merged = sorted([d for d in data if d.get("status", "").lower() in MERGED_STATES],
                    key=lambda d: (d.get("date", ""), d["id"]), reverse=True)
    flag = [byid[i] for i in FLAGSHIPS if i in byid]
    head = "| Project | Contribution |\n| :-- | :-- |\n"
    open_n = sum(1 for d in data if d.get("status", "").lower() not in MERGED_STATES)
    # clear stale badges for ids no longer in the ledger
    keep = {d["id"] + ".svg" for d in data}
    cdir = os.path.join(ROOT, "assets", "contrib")
    os.makedirs(cdir, exist_ok=True)
    for f in os.listdir(cdir):
        if f.endswith(".svg") and f not in keep:
            os.remove(os.path.join(cdir, f))
    mt = head + "\n".join(row(d) for d in merged)
    ft = head + "\n".join(row(d) for d in flag)
    counts = "%d merged or accepted  ·  %d in review" % (len(merged), open_n)
    for c in K.MODES:
        write("assets/%s/sub-merged.svg" % c["mode"], K.subband("Merged and accepted", "%d contributions" % len(merged), c))
        write("assets/%s/sub-flagship.svg" % c["mode"], K.subband("Flagship proposals in review", "open, not merged", c))
    return mt, ft, counts


# ------------------------------------------------------------------ README
def _bust(md):
    """Append ?v=<content hash> to every local asset path so GitHub's image cache (camo) refetches changed SVGs."""
    import hashlib, re as _re
    def rep(m):
        path = m.group(2)
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            return m.group(0)
        h = hashlib.sha256(open(full, "rb").read()).hexdigest()[:8]
        return '%s"%s?v=%s"' % (m.group(1), path, h)
    return _re.sub(r'((?:src|srcset)=)"(assets/[^"?]+\.svg)"', rep, md)


def pic(name, alt, attrs):
    return ('<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/%s.svg">'
            '<img src="assets/light/%s.svg" alt="%s" %s></picture>' % (name, name, alt.replace("&", "&amp;"), attrs))


def macro(m):
    kind, args = m.group(1), [a.strip() for a in m.group(2).split("|")]
    if kind == "pic":
        return pic(args[0], args[1], args[2] if len(args) > 2 else "")
    if kind == "img":
        return '<img src="%s" alt="%s" %s>' % (args[0], args[1], args[2] if len(args) > 2 else "")
    if kind == "chips":
        return " ".join(pic("chip-" + slug(c), c, 'height="28"') for c in args)
    raise SystemExit("unknown macro " + kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.environ.get("CONTRIBUTIONS_JSON") or os.path.join(ROOT, "..", "..", "contributions.json"))
    a = ap.parse_args()
    data = json.load(open(a.data, encoding="utf-8"))
    mt, ft, counts = tables(data)
    build_static(counts)
    tpl = open(os.path.join(HERE, "README.template.md"), encoding="utf-8").read()
    tpl = tpl.replace("{{merged_table}}", mt).replace("{{flagship_table}}", ft)
    tpl = tpl.replace("{{asof}}", datetime.date.today().isoformat())
    out = re.sub(r"\{\{(\w+) ([^}]*)\}\}", macro, tpl)
    assert chr(167) not in out
    write("README.md", _bust(out))
    print("ok: %d ledger rows, %s" % (len(data), counts))


if __name__ == "__main__":
    main()
