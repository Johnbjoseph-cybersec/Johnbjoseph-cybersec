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
RAW = "https://raw.githubusercontent.com/Johnbjoseph-cybersec/Johnbjoseph-cybersec/main/"
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import svgkit as K  # noqa: E402
import nextgen as N  # noqa: E402

# Lab figures come from Dude's stats.json (the same file the website reads), so the profile and
# the site cannot drift apart when John reports a new number (2026-11-14).
def _stats():
    try:
        with open(os.path.expanduser("~/team-agents/dude/stats.json")) as f:
            d = json.load(f)
        return d["lab_active_users"]["display"], str(d["countries"]["display"]), d["controls"]["display"]
    except (OSError, KeyError, ValueError):
        return "12,000+", "34", "400+"


LEARNERS, COUNTRIES, CONTROLS = _stats()

FLAGSHIPS = [  # ledger ids, in display order
    "promptfoo-12396",
    "ai-governance-framework-449",
    "trivy-discussion-11625",
    "osv-scanner-97",
]
MERGED_STATES = {"merged", "accepted"}
# John 2026-11-15: big-name work must reach "Flagship proposals" with no reminder. Any OPEN ledger row whose org is
# here, or that carries "flagship": true, is featured automatically after the pinned FLAGSHIPS (newest first).
PRESTIGE_ORGS = {
    "google", "googlecloudplatform", "google-deepmind", "nasa", "nasa-jpl", "finos", "nationalsecurityagency",
    "mitre", "mitre-attack", "mitre-atlas", "d3fend", "cisagov", "open-quantum-safe", "pqca", "hl7", "hapifhir",
    "boeing", "owasp", "ossf", "openssf", "cloudsecurityalliance", "microsoft", "aws", "awslabs", "nvidia", "ibm",
}
FLAGSHIP_MAX = 8


def flagship_rows(data):
    byid = {d["id"]: d for d in data}
    pinned = [byid[i] for i in FLAGSHIPS if i in byid]
    seen = {d["id"] for d in pinned}
    auto = sorted(
        (d for d in data
         if d["id"] not in seen
         and d.get("status", "").lower() not in MERGED_STATES
         and (d.get("flagship") is True or d.get("org", "").lower() in PRESTIGE_ORGS)),
        key=lambda d: (d.get("date", ""), d["id"]), reverse=True)
    return (pinned + auto)[:FLAGSHIP_MAX]

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


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def write(path, content):
    path = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.endswith(".svg"):
        # Gate: a malformed SVG renders as a broken image on GitHub (duplicate style attribute, 2026-11-13).
        import xml.dom.minidom
        xml.dom.minidom.parseString(content.encode("utf-8"))
    if os.path.exists(path) and open(path, encoding="utf-8").read() == content:
        return
    open(path, "w", encoding="utf-8").write(content)


# ------------------------------------------------------------------ static themed assets
def themed(name, fn, mobile=False):
    for c in K.MODES:
        write("assets/%s/%s.svg" % (c["mode"], name), fn(c, "d") if mobile else fn(c))
        if mobile:
            write("assets/%s/%s-m.svg" % (c["mode"], name), fn(c, "m"))


# Itemized so each total can be checked by hand on the page.
CROSSWALKS = [("India AI", 48, 157), ("India OT", 99, 285)]
PROJECTS = [  # (asset, tag, title, body, metrics, motif, url)
    ("card-rewindagents", "OPEN SOURCE", "rewindagents",
     "Undo for AI coding agents, including rm -rf: hooks record every step, then take back one step, one file or a whole session. MCP server, Claude Code plugin, VS Code extension.",
     [("7", "agent hooks"), ("0", "network calls")], "ledger",
     "https://github.com/Johnbjoseph-cybersec/rewindagents"),
    ("card-ai-crosswalk", "CROSSWALK", "India AI Regulation Crosswalk",
     "RBI FREE-AI, the DPDP Act and Rules, and CERT-In mapped to ISO/IEC 42001, NIST AI RMF, the EU AI Act and FINOS. Every quote checked against the primary text.",
     [("48", "provisions"), ("157", "mappings")], "crosswalk",
     "https://github.com/Johnbjoseph-cybersec/india-ai-regulation-crosswalk"),
    ("card-ot-crosswalk", "CROSSWALK", "India OT Regulation Crosswalk",
     "CEA Cyber Security in Power Sector Regulations, 2026 mapped to NIST CSF 2.0, the SP 800-82r3 OT overlay and NERC CIP. Every quote checked against the Gazette text.",
     [("99", "provisions"), ("285", "mappings")], "crosswalk",
     "https://github.com/Johnbjoseph-cybersec/india-ot-regulation-crosswalk"),
    ("card-oscal-overlay", "OSCAL", "SP 800-82r4 OT overlay in OSCAL",
     "Unofficial machine-readable rendering of the OT overlay in the NIST SP 800-82r4 draft, over SP 800-53r5, validated with oscal-cli.",
     [("3", "profiles"), ("387", "controls")], "oscal",
     "https://github.com/Johnbjoseph-cybersec/nist-800-82r4-ot-overlay-oscal"),
    ("card-inspect-oscal", "EVIDENCE", "inspect-oscal",
     "Turns UK AI Security Institute Inspect eval logs into validated OSCAL assessment-results mapped to NIST AI RMF, each log's SHA-256 as evidence. Evidence, not a verdict.",
     [("SHA-256", "per log")], "pipeline",
     "https://github.com/Johnbjoseph-cybersec/inspect-oscal"),
    ("card-templates", "TEMPLATES", "GRC Made Simple templates",
     "Four free, practitioner-grade Excel workbooks: AI system risk register, PQC migration, AI vendor due diligence and DPDP readiness.",
     [("4", "workbooks"), ("CC BY", "4.0")], "sheets",
     "https://johnbjoseph-cybersec.github.io/grc-made-simple-templates/"),
    ("card-mindledger", "LEDGER", "MindLedger",
     "Local-first ledger for Claude Code: every session and token in an append-only ledger that never goes backwards, plus memory and settings backups.",
     [("0", "network calls")], "ledger",
     "https://github.com/Johnbjoseph-cybersec/mindledger"),
]
LAB = ("FREE WITH AN ACCOUNT", "GRC Practice Lab",
       "A full ISO 27001 Lead Implementer course plus hands-on practice: guided scenarios, portfolio projects and controls across nine frameworks, used by %s active learners in %s countries." % (LEARNERS, COUNTRIES),
       [(CONTROLS, "controls"), ("9", "frameworks"), ("11", "guided scenarios"), ("12", "portfolio projects")])


def build_static(merged_n, open_n):
    themed("hero", N.hero, mobile=True)
    prov = sum(p for _, p, _ in CROSSWALKS)
    maps = sum(mm for _, _, mm in CROSSWALKS)
    items = [
        (LEARNERS, "Practice Lab learners", "active users, %s countries" % COUNTRIES),
        (str(maps), "regulation mappings", " + ".join("%d %s" % (mm, n) for n, _, mm in CROSSWALKS)),
        (str(prov), "provisions verified", " + ".join("%d %s" % (p, n) for n, p, _ in CROSSWALKS)),
        (str(merged_n), "merged upstream", "+%d open, in review" % open_n),
    ]
    themed("stats", lambda c, m: N.stats(items, c, m), mobile=True)
    for group, items in (("pill", PILLS), ("pfoot", FOOTER)):
        for j, (key, label, ic) in enumerate(items):
            last = j == len(items) - 1
            themed("%s-%s" % (group, key), lambda c, m, l=label, i=ic, n=len(items), la=last: N.pill(l, i, c, m, n, la), mobile=True)
    themed("intro", N.intro, mobile=True)
    themed("speaking", N.speaking, mobile=True)
    themed("sec-built", lambda c, m: N.section("~/built", "Built", "open source + free to use", c, m), mobile=True)
    themed("sec-oss", lambda c, m: N.section("~/open-source", "Upstream work", "%d merged  ·  %d in review" % (merged_n, open_n), c, m), mobile=True)
    themed("sec-focus", lambda c, m: N.section("~/focus", "Focus", "", c, m), mobile=True)
    themed("sec-speaking", lambda c, m: N.section("~/speaking", "Speaking", "", c, m), mobile=True)
    themed("foot", N.footer, mobile=True)
    themed("card-lab", lambda c, m: N.feature(LAB[0], LAB[1], LAB[2], LAB[3], c, m), mobile=True)
    for key, tag, title, body, metrics, kind, _ in PROJECTS:
        themed(key, lambda c, t=tag, ti=title, bo=body, me=metrics, k=kind: N.card(t, ti, bo, me, k, c))
    fh = max(N.focus_height(t) for _, _, _, t in FOCUS)
    for key, label, ic, body in FOCUS:
        themed("focus-" + key, lambda c, l=label, i=ic, t=body: N.focus(l, i, t, c, fh))
    ph = max(N.creds_height(CREDENTIALS), N.teach_height(TEACH_TEXT))
    themed("panel-credentials", lambda c: N.creds(CREDENTIALS, c, ph))
    themed("panel-teaching", lambda c: N.teach(LEARNERS, "active users", "in %s countries" % COUNTRIES, TEACH_TEXT, c, ph))


LINKS = {"website": "https://johnbjoseph-cybersec.github.io/", "lab": "https://grclab.purplecop.io",
         "youtube": "https://www.youtube.com/@GRCMadeSimple",
         "newsletter": "https://www.linkedin.com/newsletters/grc-made-simple-7493284804747251713/",
         "linkedin": "https://www.linkedin.com/in/john-bj/"}


def pills_md(group, items):
    """One line, no whitespace between buttons: the gaps live inside each SVG, so the row spans
    exactly 100% (any inline space would push the last button to a new line)."""
    out = []
    for j, (key, label, ic) in enumerate(items):
        pct = N.pill_pct(len(items), j == len(items) - 1) - 0.01
        out.append('<a href="%s">%s</a>' % (LINKS[key], pic2("%s-%s" % (group, key), label, 'width="%.3f%%"' % pct)))
    return "<p>" + "".join(out) + "</p>"


def projects_md():
    out = []
    for i in range(0, len(PROJECTS), 2):
        cells = []
        for key, tag, title, body, metrics, kind, url in PROJECTS[i:i + 2]:
            cells.append('  <a href="%s">%s</a>' % (url, pic(key, "%s. %s" % (title, body), 'width="406"')))
        out.append("<p>\n%s\n</p>" % "\n".join(cells))
    return "\n\n".join(out)


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


def rows_md(items, label_fn):
    out = []
    for d in items:
        ref = parse_ref(d["url"])
        label = label_fn(d)
        ref_txt = ("%s #%s" % (ref[2], ref[3])) if ref else d.get("date", "")
        dd = dict(d, title=short(d["title"], 400))
        for c in K.MODES:
            for m in ("d", "m"):
                write("assets/rows/%s/%s%s.svg" % (c["mode"], d["id"], "-m" if m == "m" else ""), N.row(dd, label, ref_txt, c, m))
        alt = "%s: %s. %s" % (label.title(), d["project"], short(d["title"]))
        out.append('  <a href="%s">%s</a>' % (d["url"], pic2("rows/%s/" + d["id"], alt, 'width="100%"')))
    return "<p>\n%s\n</p>" % "\n".join(out)


def tables(data):
    byid = {d["id"]: d for d in data}
    merged = sorted([d for d in data if d.get("status", "").lower() in MERGED_STATES],
                    key=lambda d: (d.get("date", ""), d["id"]), reverse=True)
    flag = flagship_rows(data)
    open_n = sum(1 for d in data if d.get("status", "").lower() not in MERGED_STATES)
    keep = {d["id"] + suf for d in merged + flag for suf in (".svg", "-m.svg")}
    for mode in ("light", "dark"):
        cdir = os.path.join(ROOT, "assets", "rows", mode)
        os.makedirs(cdir, exist_ok=True)
        for f in os.listdir(cdir):
            if f.endswith(".svg") and f not in keep:
                os.remove(os.path.join(cdir, f))
    for c in K.MODES:
        for m in ("d", "m"):
            suf = "-m" if m == "m" else ""
            write("assets/%s/sub-merged%s.svg" % (c["mode"], suf), N.subhead("Merged and accepted", "%d merged or accepted" % len(merged), c, m))
            write("assets/%s/sub-flagship%s.svg" % (c["mode"], suf), N.subhead("Flagship proposals in review", "open, not merged", c, m))
    mt = rows_md(merged, lambda d: status_style(d)[0])
    ft = rows_md(flag, lambda d: status_style(d)[0])
    today = datetime.date.today()

    def age(ds):
        n = (today - datetime.date.fromisoformat(ds)).days
        return "today" if n <= 0 else "yesterday" if n == 1 else "%dd ago" % n
    recent = sorted(data, key=lambda d: (d.get("date", ""), d["id"]), reverse=True)[:14]
    ev = []
    for d in recent:
        ref = parse_ref(d["url"])
        ev.append((status_style(d)[0], d["project"], ("%s #%s" % (ref[2], ref[3])) if ref else "", age(d["date"])))
    for c in K.MODES:
        write("assets/%s/ticker.svg" % c["mode"], N.ticker(ev, c, "d"))
        write("assets/%s/ticker-m.svg" % c["mode"], N.ticker(ev, c, "m"))
    for c in K.MODES:
        write("assets/%s/chart.svg" % c["mode"], N.chart(data, parse_ref, c, "d"))
        write("assets/%s/chart-m.svg" % c["mode"], N.chart(data, parse_ref, c, "m"))
    return mt, ft, len(merged), open_n


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
        # Absolute raw URL: github.com/<repo>/raw/... 302-redirects WITHOUT the query string, so a
        # same-named file stayed cached (old purple hero after the 2026-11-13 redesign). The raw host
        # keys its cache on the full URL, so a content hash in ?v= gives every change a fresh URL.
        return '%s"%s%s?v=%s"' % (m.group(1), RAW, path, h)
    return _re.sub(r'((?:src|srcset)=)"(assets/[^"?]+\.svg)"', rep, md)


def pic(name, alt, attrs):
    return ('<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/%s.svg">'
            '<img src="assets/light/%s.svg" alt="%s" %s></picture>' % (name, name, alt.replace("&", "&amp;"), attrs))


def pic2(name, alt, attrs):
    """Light/dark x desktop/mobile. name may contain %s for the mode folder (rows/%s/<id>)."""
    p = (lambda mode, suf: "assets/" + (name % mode if "%s" in name else mode + "/" + name) + suf + ".svg")
    return ('<picture>'
            '<source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="%s">'
            '<source media="(max-width: 600px)" srcset="%s">'
            '<source media="(prefers-color-scheme: dark)" srcset="%s">'
            '<img src="%s" alt="%s" %s></picture>' % (
                p("dark", "-m"), p("light", "-m"), p("dark", ""), p("light", ""), alt.replace("&", "&amp;").replace('"', "&quot;"), attrs))


def macro(m):
    kind, args = m.group(1), [a.strip() for a in m.group(2).split("|")]
    if kind == "pic":
        return pic(args[0], args[1], args[2] if len(args) > 2 else "")
    if kind == "pic2":
        return pic2(args[0], args[1], args[2] if len(args) > 2 else "")
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
    mt, ft, merged_n, open_n = tables(data)
    build_static(merged_n, open_n)
    tpl = open(os.path.join(HERE, "README.template.md"), encoding="utf-8").read()
    tpl = tpl.replace("{{merged_table}}", mt).replace("{{flagship_table}}", ft)
    tpl = tpl.replace("{{asof}}", datetime.date.today().isoformat()).replace("{{projects}}", projects_md())
    tpl = tpl.replace("{{pills_top}}", pills_md("pill", PILLS)).replace("{{pills_foot}}", pills_md("pfoot", FOOTER))
    tpl = tpl.replace("{{merged_n}}", str(merged_n)).replace("{{open_n}}", str(open_n)).replace("{{total_n}}", str(len(data)))
    out = re.sub(r"\{\{(\w+) ([^}]*)\}\}", macro, tpl)
    assert chr(167) not in out
    write("README.md", _bust(out))
    print("ok: %d ledger rows, %d merged/accepted, %d open" % (len(data), merged_n, open_n))


if __name__ == "__main__":
    main()
