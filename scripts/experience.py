"""Draws assets/experience.svg from data/experience.yml. No AI involved.

  python scripts/experience.py                 -> redraw the timeline from data/experience.yml
  python scripts/experience.py --import FILE   -> first read a LinkedIn export (Positions.csv or the
                                                  whole LinkedIn data .zip), rewrite the jobs in
                                                  data/experience.yml, then redraw.
"""
import csv, io, os, re, sys, zipfile
from datetime import date
from xml.sax.saxutils import escape
import yaml

DATA, OUT = "data/experience.yml", "assets/experience.svg"
PINK, CYAN, PURP, YEL = "#ff2a6d", "#05d9e8", "#b967ff", "#f9f002"
COLORS = [CYAN, PINK, YEL, PURP, CYAN, PINK, YEL, PURP]
FONT = "'Courier New',Consolas,'DejaVu Sans Mono',monospace"
SANS = "'Segoe UI',Inter,Helvetica,Arial,sans-serif"
MONTHS = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


# ---------------- LinkedIn import ----------------
def read_positions(path):
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            name = next((n for n in z.namelist() if n.lower().endswith("positions.csv")), None)
            if not name:
                sys.exit("No Positions.csv inside the zip. Use LinkedIn > Settings > Data privacy > Get a copy of your data.")
            text = z.read(name).decode("utf-8-sig")
    else:
        text = open(path, encoding="utf-8-sig").read()
    # LinkedIn sometimes puts notes above the header row
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.lower().startswith("company name")), 0)
    return list(csv.DictReader(io.StringIO("\n".join(lines[start:]))))


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    m = re.match(r"([A-Za-z]{3})[a-z]*\s+(\d{4})", s)
    if m:
        return date(int(m.group(2)), MONTHS.get(m.group(1).lower(), 1), 1)
    m = re.match(r"(\d{4})", s)
    return date(int(m.group(1)), 1, 1) if m else None


def fmt_range(a, b):
    if a and not b:
        return f"{a.strftime('%b %Y').upper()} — NOW"
    if a and b and a.year == b.year:
        return f"{a.year}"
    return f"{a.year if a else '?'} — {b.year if b else 'NOW'}"


def clean_points(desc, hide, n):
    pts = []
    for raw in re.split(r"[\n\r]+|•", desc or ""):
        t = re.sub(r"^[\s\-–•*·]+", "", raw).strip()
        if len(t) < 15 or any(w.lower() in t.lower() for w in hide):
            continue
        if len(t) > 98:
            t = t[:97].rsplit(" ", 1)[0] + "…"
        pts.append(t)
        if len(pts) >= n:
            break
    return pts


def import_linkedin(path, data):
    cfg = data.get("linkedin_import", {})
    labels, hide = cfg.get("company_labels", {}), cfg.get("hide_words", [])
    default = cfg.get("default_label", "")
    rows = read_positions(path)
    jobs, short = [], []
    for r in rows:
        a, b = parse_date(r.get("Started On")), parse_date(r.get("Finished On"))
        months = ((b or date.today()).year - a.year) * 12 + ((b or date.today()).month - a.month) + 1 if a else 99
        company = (r.get("Company Name") or "").strip()
        label = labels.get(company, default)
        loc = (r.get("Location") or "").split(",")[0].strip()
        where = label if (not loc or loc.lower() in label.lower()) else f"{label} · {loc}" if label else loc
        item = {"_start": a or date(1900, 1, 1), "_end": b, "when": fmt_range(a, b),
                "title": (r.get("Title") or "").strip(), "where": where, "_loc": loc,
                "points": clean_points(r.get("Description"), hide, cfg.get("max_points", 3))}
        # one- or two-month roles (events, programmes) are grouped into a single "leadership" entry
        (short if months <= 2 and b else jobs).append(item)
    if short:
        short.sort(key=lambda x: x["_start"], reverse=True)
        jobs.append({"_start": short[0]["_start"], "_end": short[0]["_end"],
                     "when": f"{short[-1]['_start'].year} — {short[0]['_start'].year}" if short[-1]["_start"].year != short[0]["_start"].year else str(short[0]["_start"].year),
                     "title": "Programme & Event Leadership", "where": short[0]["_loc"],
                     "points": [s["title"][:98] for s in short][: cfg.get("max_points", 3)]})
    jobs.sort(key=lambda x: (x["_end"] is None, x["_end"] or date.max, x["_start"]), reverse=True)
    for j in jobs:
        for k in ("_start", "_end", "_loc"):
            j.pop(k, None)
    data["jobs"] = jobs[: cfg.get("max_jobs", 6)]
    return data


def save_yaml(data):
    head = open(DATA, encoding="utf-8").read().split("jobs:")[0]
    body = yaml.safe_dump({k: data[k] for k in ("jobs", "education", "linkedin_import") if k in data},
                          allow_unicode=True, sort_keys=False, width=200)
    open(DATA, "w", encoding="utf-8").write(head + body)


# ---------------- drawing ----------------
def render(data):
    entries = list(data.get("jobs", [])) + list(data.get("education", []))
    y, parts = 30, []
    for i, e in enumerate(entries):
        c = COLORS[i % len(COLORS)]
        pts = [str(p) for p in (e.get("points") or [])][:4]
        parts.append(f'''<g class="in" style="animation-delay:{i*0.15:.2f}s">
<circle cx="200" cy="{y+8}" r="9" fill="#0a0014" stroke="{c}" stroke-width="3" filter="url(#g)"/>
<circle cx="200" cy="{y+8}" r="3.5" fill="{c}" class="pl" style="animation-delay:{i*0.3:.1f}s"/>
<text x="176" y="{y+13}" text-anchor="end" class="m" font-size="13" letter-spacing="1.5" fill="{c}">{escape(str(e.get("when", "")))}</text>
<text x="226" y="{y+14}" class="s" font-weight="700" font-size="19" fill="#fff">{escape(str(e.get("title", "")))}</text>
<text x="226" y="{y+38}" class="m" font-size="13" letter-spacing="1" fill="{c}" opacity=".9">{escape(str(e.get("where", "")))}</text>
{"".join(f'<text x="226" y="{y+62+k*22}" class="s" font-size="15" fill="#d1c6ff"><tspan fill="{c}">▸ </tspan>{escape(p)}</text>' for k, p in enumerate(pts))}
</g>''')
        y += 62 + 22 * len(pts) + 18
    H = y + 6
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{H}" viewBox="0 0 1200 {H}">
<defs><filter id="g" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="ln" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{PINK}"/><stop offset="1" stop-color="{PURP}"/></linearGradient></defs>
<style>.m{{font-family:{FONT};font-weight:700}} .s{{font-family:{SANS}}}
.in{{animation:in .8s ease-out both}} @keyframes in{{from{{opacity:0;transform:translateX(14px)}}to{{opacity:1;transform:none}}}}
.pl{{animation:pl 2s ease-in-out infinite}} @keyframes pl{{50%{{opacity:.2}}}}
.run{{animation:run 4s linear infinite}} @keyframes run{{from{{transform:translateY(0)}}to{{transform:translateY({max(0, H-60)}px)}}}}</style>
<rect x="2" y="2" width="1196" height="{H-4}" rx="12" fill="#0a0014"/>
<rect x="198" y="30" width="4" height="{max(0, H-70)}" fill="url(#ln)" opacity=".55"/>
<rect class="run" x="196" y="30" width="8" height="30" rx="4" fill="#fff" opacity=".8" filter="url(#g)"/>
{"".join(parts)}
</svg>'''
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(svg)
    print(f"drew {len(entries)} entries -> {OUT}")


if __name__ == "__main__":
    data = yaml.safe_load(open(DATA, encoding="utf-8"))
    if "--import" in sys.argv:
        data = import_linkedin(sys.argv[sys.argv.index("--import") + 1], data)
        save_yaml(data)
        print("imported LinkedIn positions into", DATA)
    render(data)
