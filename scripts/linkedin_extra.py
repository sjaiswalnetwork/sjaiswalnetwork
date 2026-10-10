"""Imports LinkedIn posts (Shares.csv) and recommendations (Recommendations_Received.csv)
into data/posts.yml and data/recommendations.yml. No AI involved.

  python scripts/linkedin_extra.py FILE    (a .csv or a LinkedIn .zip)
"""
import csv, io, os, re, sys, zipfile
from datetime import datetime
import yaml

WANTED = ("shares.csv", "recommendations_received.csv")


def read(path):
    out = {}
    def parse(name, text):
        lines = text.splitlines()
        hdr = next((i for i, l in enumerate(lines) if "," in l and not l.lower().startswith("notes")), 0)
        out[os.path.basename(name).lower()] = list(csv.DictReader(io.StringIO("\n".join(lines[hdr:]))))
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if os.path.basename(n).lower() in WANTED:
                    parse(n, z.read(n).decode("utf-8-sig"))
    elif os.path.basename(path).lower() in WANTED:
        parse(path, open(path, encoding="utf-8-sig").read())
    return out


def nice_date(s):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%y, %I:%M %p", "%m/%d/%y"):
        try:
            return datetime.strptime((s or "").strip(), fmt)
        except ValueError:
            pass
    return None


def keep_header(path, key):
    return open(path, encoding="utf-8").read().split(key + ":")[0]


def main(path):
    found = read(path)
    if "shares.csv" in found:
        posts = []
        for r in found["shares.csv"]:
            if (r.get("Visibility") or "").upper() == "CONNECTIONS_ONLY":
                continue
            link = (r.get("ShareLink") or "").strip()
            text = re.sub(r"\s+", " ", (r.get("ShareCommentary") or "").replace('""', '"')).strip()
            if not link or not text:
                continue
            d = nice_date(r.get("Date"))
            posts.append({"link": link, "date": d.strftime("%b %Y") if d else "", "text": text[:280] + ("…" if len(text) > 280 else ""), "_d": d or datetime.min})
        posts.sort(key=lambda p: p["_d"], reverse=True)
        for p in posts:
            p.pop("_d")
        f = "data/posts.yml"
        open(f, "w", encoding="utf-8").write(keep_header(f, "posts") + yaml.safe_dump({"posts": posts[:12]}, allow_unicode=True, sort_keys=False, width=300))
        print(f"imported {len(posts[:12])} posts")
    if "recommendations_received.csv" in found:
        recs = []
        for r in found["recommendations_received.csv"]:
            if (r.get("Status") or "VISIBLE").upper() != "VISIBLE":
                continue
            text = re.sub(r"\s+", " ", r.get("Text") or "").strip()
            name = f"{(r.get('First Name') or '').strip()} {(r.get('Last Name') or '').strip()}".strip()
            if text and name:
                recs.append({"name": name, "role": (r.get("Job Title") or "").strip(), "text": text})
        f = "data/recommendations.yml"
        open(f, "w", encoding="utf-8").write(keep_header(f, "recommendations") + yaml.safe_dump({"recommendations": recs}, allow_unicode=True, sort_keys=False, width=300))
        print(f"imported {len(recs)} recommendations")


if __name__ == "__main__":
    main(sys.argv[1])
