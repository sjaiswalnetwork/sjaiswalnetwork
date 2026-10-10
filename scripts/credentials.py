"""Draws assets/credentials.svg from data/credentials.yml. No AI involved.

  python scripts/credentials.py                 -> redraw from data/credentials.yml
  python scripts/credentials.py --import FILE   -> read LinkedIn Certifications.csv / Honors.csv
                                                   (or a LinkedIn .zip containing them), update the
                                                   yml, then redraw. Files without those CSVs are ignored.
"""
import csv, io, os, re, sys, zipfile
from collections import OrderedDict
from xml.sax.saxutils import escape
import yaml

DATA, OUT = "data/credentials.yml", "assets/credentials.svg"
PINK, CYAN, PURP, YEL = "#ff2a6d", "#05d9e8", "#b967ff", "#f9f002"
FONT = "'Courier New',Consolas,'DejaVu Sans Mono',monospace"
SANS = "'Segoe UI',Inter,Helvetica,Arial,sans-serif"
ISSUER_COLORS = [PINK, CYAN, YEL, PURP]
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()


# ---------------- LinkedIn import ----------------
def read_csvs(path):
    """Returns {lowercase filename: rows} for Certifications/Honors CSVs found in path."""
    found = {}
    def parse(name, text):
        lines = text.splitlines()
        hdr = next((i for i, l in enumerate(lines) if "," in l and not l.lower().startswith("notes")), 0)
        found[os.path.basename(name).lower()] = list(csv.DictReader(io.StringIO("\n".join(lines[hdr:]))))
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if os.path.basename(n).lower() in ("certifications.csv", "honors.csv"):
                    parse(n, z.read(n).decode("utf-8-sig"))
    elif os.path.basename(path).lower() in ("certifications.csv", "honors.csv"):
        parse(path, open(path, encoding="utf-8-sig").read())
    return found


def nice_date(s):
    s = (s or "").strip()
    m = re.match(r"([A-Za-z]{3})[a-z]*\s+(\d{4})", s)
    if m:
        return f"{m.group(1).title()} {m.group(2)}"
    m = re.match(r"(\d{4})-(\d{2})", s)
    if m:
        return f"{MONTHS[int(m.group(2)) - 1].title()} {m.group(1)}"
    return s


def sort_key(d):
    m = re.match(r"([A-Za-z]{3}) (\d{4})", d or "")
    return (int(m.group(2)), MONTHS.index(m.group(1).lower()) + 1) if m else (0, 0)


def import_linkedin(path, data):
    found = read_csvs(path)
    if not found:
        return data, False
    names = data.get("issuer_names", {})
    if "certifications.csv" in found:
        certs = []
        for r in found["certifications.csv"]:
            name = re.sub(r"^Claude Academy:\s*", "", (r.get("Name") or "").strip())
            if not name:
                continue
            issuer = (r.get("Authority") or "").strip()
            certs.append({"name": name, "issuer": names.get(issuer, issuer), "date": nice_date(r.get("Started On"))})
        # keep any certificates you typed by hand that LinkedIn doesn't have
        have = {c["name"].lower() for c in certs}
        certs += [c for c in data.get("certifications", []) if c["name"].lower() not in have]
        data["certifications"] = sorted(certs, key=lambda c: sort_key(c["date"]), reverse=True)
    if "honors.csv" in found:
        aw = [{"name": (r.get("Title") or "").strip(), "issuer": (r.get("Issuer") or r.get("Description") or "").strip()[:60],
               "date": nice_date(r.get("Issued On"))} for r in found["honors.csv"] if (r.get("Title") or "").strip()]
        have = {a["name"].lower() for a in aw}
        data["awards"] = aw + [a for a in data.get("awards", []) if a["name"].lower() not in have]
    return data, True


def save_yaml(data):
    head = open(DATA, encoding="utf-8").read().split("certifications:")[0]
    body = yaml.safe_dump({k: data[k] for k in ("certifications", "awards", "issuer_names") if k in data},
                          allow_unicode=True, sort_keys=False, width=200)
    open(DATA, "w", encoding="utf-8").write(head + body)


# ---------------- drawing ----------------
def fit(t, n):
    t = str(t)
    return t if len(t) <= n else t[: n - 1] + "…"


def render(data):
    groups = OrderedDict()
    for c in data.get("certifications", []):
        groups.setdefault(c.get("issuer", "Other"), []).append(c)
    total = sum(len(v) for v in groups.values())
    parts, y = [], 92
    parts.append(f'<text x="40" y="52" class="s" font-weight="700" font-size="26" fill="#fff">{total} certifications</text>'
                 f'<text x="40" y="76" class="m" font-size="12" letter-spacing="2" fill="#8a7fb0">FROM {len(groups)} ISSUERS · VERIFIED ON LINKEDIN</text>')
    COLS, CW, CH, GX = 3, 362, 64, 17
    for gi, (issuer, items) in enumerate(groups.items()):
        c = ISSUER_COLORS[gi % len(ISSUER_COLORS)]
        parts.append(f'<g class="in" style="animation-delay:{gi*0.2:.1f}s">'
                     f'<rect x="40" y="{y}" width="6" height="22" rx="2" fill="{c}" filter="url(#g)"/>'
                     f'<text x="58" y="{y+17}" class="s" font-weight="700" font-size="18" fill="{c}">{escape(issuer)}</text>'
                     f'<text x="1160" y="{y+17}" text-anchor="end" class="m" font-size="12" letter-spacing="2" fill="{c}">{len(items)} ×</text></g>')
        y += 36
        for i, it in enumerate(items):
            col, row = i % COLS, i // COLS
            x, yy = 40 + col * (CW + GX), y + row * (CH + 12)
            parts.append(f'''<g class="in" style="animation-delay:{gi*0.2 + i*0.05:.2f}s">
<rect x="{x}" y="{yy}" width="{CW}" height="{CH}" rx="8" fill="#120326" stroke="{c}" stroke-opacity=".55" stroke-width="1.5"/>
<rect x="{x}" y="{yy}" width="4" height="{CH}" rx="2" fill="{c}"/>
<text x="{x+18}" y="{yy+27}" class="s" font-weight="600" font-size="15" fill="#fff">{escape(fit(it.get("name", ""), 40))}</text>
<text x="{x+18}" y="{yy+49}" class="m" font-size="11" letter-spacing="1.5" fill="{c}">✓ {escape(str(it.get("date", "")).upper())}</text></g>''')
        y += ((len(items) + COLS - 1) // COLS) * (CH + 12) + 18
    awards = data.get("awards", [])
    if awards:
        parts.append(f'<text x="40" y="{y+18}" class="s" font-weight="700" font-size="18" fill="{YEL}">🏆 Awards &amp; recognition</text>')
        y += 34
        for a in awards:
            parts.append(f'''<g class="in"><rect x="40" y="{y}" width="1120" height="62" rx="8" fill="#1a1400" stroke="{YEL}" stroke-opacity=".6" stroke-width="1.5"/>
<text x="60" y="{y+27}" class="s" font-weight="600" font-size="16" fill="#fff">{escape(fit(a.get("name", ""), 110))}</text>
<text x="60" y="{y+48}" class="m" font-size="12" letter-spacing="1" fill="{YEL}">{escape(str(a.get("issuer", "")))} · {escape(str(a.get("date", "")))}</text></g>''')
            y += 74
    H = y + 20
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{H}" viewBox="0 0 1200 {H}">
<defs><filter id="g" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<style>.m{{font-family:{FONT};font-weight:700}} .s{{font-family:{SANS}}}
.in{{animation:in .7s ease-out both}} @keyframes in{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}</style>
<rect x="2" y="2" width="1196" height="{H-4}" rx="12" fill="#0a0014"/>
{"".join(parts)}
</svg>'''
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(svg)
    print(f"drew {total} certifications, {len(awards)} awards -> {OUT}")


if __name__ == "__main__":
    data = yaml.safe_load(open(DATA, encoding="utf-8"))
    if "--import" in sys.argv:
        data, changed = import_linkedin(sys.argv[sys.argv.index("--import") + 1], data)
        if changed:
            save_yaml(data); print("imported LinkedIn certifications/honors")
    render(data)
