"""Builds assets/now.svg: a live cyberpunk terminal of recent GitHub activity.
Run by .github/workflows/cyber-refresh.yml. Uses only the Python standard library."""
import json, os, sys, urllib.request
from datetime import datetime, timezone, timedelta
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "sjaiswalnetwork")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/now.svg"
IST = timezone(timedelta(hours=5, minutes=30))
PINK, CYAN, PURP, YEL = "#ff2a6d", "#05d9e8", "#b967ff", "#f9f002"
FONT = "'Courier New',Consolas,'DejaVu Sans Mono',monospace"


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={"Accept": "application/vnd.github+json", "User-Agent": "now-svg"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def ago(iso):
    d = datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))
    s = int(d.total_seconds())
    if s < 3600: return f"{max(1, s // 60)}m ago"
    if s < 86400: return f"{s // 3600}h ago"
    return f"{s // 86400}d ago"


def cut(t, n):
    t = " ".join(str(t).split())
    return t if len(t) <= n else t[: n - 1] + "…"


commits, repos = [], []
try:
    for r in api(f"/users/{USER}/repos?sort=pushed&per_page=8"):
        if r.get("fork"):
            continue
        if r["name"] != USER:
            repos.append((r["name"], r.get("language") or "—", r.get("stargazers_count", 0), ago(r["pushed_at"])))
        if len(repos) <= 4:
            try:
                for c in api(f"/repos/{USER}/{r['name']}/commits?per_page=4"):
                    msg = c["commit"]["message"].splitlines()[0]
                    if msg.lower().startswith("merge") or "[skip ci]" in msg:
                        continue
                    when = c["commit"]["author"]["date"]
                    commits.append((when, r["name"], msg))
            except Exception as e:
                print("commits error", r["name"], e)
    commits.sort(reverse=True)
    commits = [(n, m, ago(w)) for w, n, m in commits]
except Exception as e:  # keep the panel alive even if the API hiccups
    print("API error:", e)
commits, repos = commits[:5], repos[:4]
stamp = datetime.now(IST).strftime("%d %b %Y · %H:%M IST")

L = []  # (text_svg, delay)
y = 72
def line(svg, gap=24):
    global y
    L.append((y, svg)); y += gap

line(f'<tspan fill="{PINK}">sj@neon-grid</tspan><tspan fill="#fff">:~$ </tspan><tspan fill="{CYAN}">git log --all --recent</tspan>')
if commits:
    for repo, msg, when in commits:
        line(f'<tspan fill="{YEL}">  ▸ {escape(cut(repo, 22)):<22}</tspan><tspan fill="#d1c6ff"> {escape(cut(msg, 58))}</tspan><tspan fill="{PURP}">  [{when}]</tspan>', 22)
else:
    line(f'<tspan fill="{PURP}">  ▸ syncing commit stream…</tspan>', 22)
y += 8
line(f'<tspan fill="{PINK}">sj@neon-grid</tspan><tspan fill="#fff">:~$ </tspan><tspan fill="{CYAN}">ls ./repos --sort=pushed</tspan>')
if repos:
    cells = []
    for i, (n, lang, st, when) in enumerate(repos):
        cells.append(f'<tspan x="{40 + i * 285}" fill="{[CYAN, PINK, YEL, PURP][i]}">◆ {escape(cut(n, 18))}</tspan><tspan fill="#8a7fb0"> {escape(cut(lang, 6))}</tspan>')
    line("".join(cells), 22)
    line("".join(f'<tspan x="{56 + i * 285}" fill="#8a7fb0">★{st} · pushed {w}</tspan>' for i, (_, _, st, w) in enumerate(repos)), 30)
else:
    line(f'<tspan fill="{PURP}">  ◆ scanning…</tspan>', 30)
line(f'<tspan fill="{PINK}">sj@neon-grid</tspan><tspan fill="#fff">:~$ </tspan><tspan class="blink" fill="{YEL}">█</tspan>')
H = y + 20

rows = "\n".join(
    f'<text x="40" y="{yy}" class="ln" style="animation-delay:{i * 0.22:.2f}s" xml:space="preserve">{s}</text>' for i, (yy, s) in enumerate(L))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{H}" viewBox="0 0 1200 {H}">
<defs><filter id="g" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity=".45"/></pattern>
<linearGradient id="bd" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{PINK}"/><stop offset="1" stop-color="{PURP}"/></linearGradient></defs>
<style>
text{{font-family:{FONT};font-weight:700;font-size:15px;white-space:pre}}
.ln{{opacity:0;animation:in .35s steps(2) forwards}} @keyframes in{{to{{opacity:1}}}}
.blink{{animation:bk 1s infinite steps(1)}} @keyframes bk{{50%{{opacity:0}}}}
.jit{{animation:j 4s infinite steps(1)}} @keyframes j{{0%,93%,100%{{transform:none}}94%{{transform:translate(6px,0)}}96%{{transform:translate(-4px,1px)}}}}
.sw{{animation:sw 3.5s linear infinite}} @keyframes sw{{from{{transform:translateY(-30px)}}to{{transform:translateY({H}px)}}}}
.dash{{stroke-dasharray:60 30;animation:da 3s linear infinite}} @keyframes da{{to{{stroke-dashoffset:-180}}}}
</style>
<rect x="2" y="2" width="1196" height="{H - 4}" rx="10" fill="#07000f"/>
<rect x="2" y="2" width="1196" height="{H - 4}" rx="10" fill="none" stroke="url(#bd)" stroke-width="2.5" class="dash" filter="url(#g)"/>
<rect x="2" y="2" width="1196" height="34" rx="10" fill="#14022a"/>
<circle cx="26" cy="19" r="6" fill="{PINK}"/><circle cx="46" cy="19" r="6" fill="{YEL}"/><circle cx="66" cy="19" r="6" fill="{CYAN}"/>
<text x="600" y="24" text-anchor="middle" fill="{CYAN}" font-size="13" letter-spacing="3" filter="url(#g)">NOW_BUILDING.SH  ::  LIVE FEED</text>
<text x="1180" y="24" text-anchor="end" fill="{PURP}" font-size="11">SYNC {stamp}</text>
<g class="jit" filter="url(#g)">
{rows}
</g>
<rect class="sw" x="2" width="1196" height="30" fill="{CYAN}" opacity=".06"/>
<rect x="2" y="2" width="1196" height="{H - 4}" rx="10" fill="url(#scan)"/>
</svg>'''
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, len(commits), "commits", len(repos), "repos")
