"""Neon tic-tac-toe played through GitHub issues.
Issue title format:  ttt|move|<0-8>   or   ttt|new
Usage: python game/ttt.py            (reads ISSUE_TITLE / ISSUE_USER env, updates state + README)
       python game/ttt.py --render   (re-render README section only)
Writes the bot's reply to $COMMENT_FILE (default /tmp/ttt_comment.md)."""
import json, os, random, re, sys
from datetime import datetime, timezone

REPO = os.environ.get("GITHUB_REPOSITORY", "sjaiswalnetwork/sjaiswalnetwork")
STATE = "game/state.json"
README = "README.md"
COMMENT = os.environ.get("COMMENT_FILE", "/tmp/ttt_comment.md")
SKILL = 0.8  # chance the AI plays the perfect move — beatable, but not by much
LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]


def load():
    try:
        return json.load(open(STATE))
    except Exception:
        return {"board": "_________", "scores": {"human": 0, "ai": 0, "draw": 0}, "log": [], "last_result": "", "players": {}}


def winner(b):
    for a, c, d in LINES:
        if b[a] != "_" and b[a] == b[c] == b[d]:
            return b[a]
    return "D" if "_" not in b else None


def minimax(b, me):
    w = winner(b)
    if w == "O": return 10, None
    if w == "X": return -10, None
    if w == "D": return 0, None
    best = (-99, None) if me == "O" else (99, None)
    for i in range(9):
        if b[i] != "_": continue
        nb = b[:i] + me + b[i+1:]
        s, _ = minimax(nb, "X" if me == "O" else "O")
        s -= 1 if s > 0 else -1 if s < 0 else 0  # prefer faster wins / slower losses
        if (me == "O" and s > best[0]) or (me == "X" and s < best[0]):
            best = (s, i)
    return best


def ai_move(b):
    free = [i for i in range(9) if b[i] == "_"]
    # always take an immediate win; otherwise sometimes slip up
    for i in free:
        if winner(b[:i] + "O" + b[i+1:]) == "O":
            return i
    if random.random() < SKILL:
        return minimax(b, "O")[1]
    return random.choice(free)


def issue_link(title, label):
    from urllib.parse import quote
    body = f"🎮 Just click **Submit new issue**. The neon AI answers in about 30 seconds, then check the README.\n\n({label})"
    return f"https://github.com/{REPO}/issues/new?title={quote(title)}&body={quote(body)}"


def render(st):
    b = st["board"]
    w = winner(b)
    rows = []
    for r in range(3):
        cells = []
        for c in range(3):
            i = r * 3 + c
            if b[i] == "X":
                cells.append('<img src="assets/ttt/x.svg" width="112" alt="X" />')
            elif b[i] == "O":
                cells.append('<img src="assets/ttt/o.svg" width="112" alt="O" />')
            else:
                cells.append(f'<a href="{issue_link(f"ttt|move|{i}", f"move to cell {i}")}"><img src="assets/ttt/e{i}.svg" width="112" alt="Play cell {i}" /></a>')
        rows.append("".join(cells))
    s = st["scores"]
    status = "▶ YOUR MOVE, HUMAN — pick a glowing cell" if not w else "GAME OVER"
    log = "".join(f"<tr><td>{e['t']}</td><td>{'🤖 neon-ai' if e['u'] == 'neon-ai' else '@' + e['u']}</td><td>{e['m']}</td></tr>" for e in st["log"][:5]) or "<tr><td colspan=3>no moves yet — be the first</td></tr>"
    top = sorted(st.get("players", {}).items(), key=lambda kv: -kv[1])[:3]
    hall = " · ".join(f"@{u} ({n})" for u, n in top) or "nobody yet"
    return f"""<!--TTT_START-->
<div align="center">

**`YOU = ✖ PINK` · `AI = ◯ CYAN` · click an empty cell → hit "Submit new issue" → the AI replies in ~30 s**

{"<br/>".join(rows)}

<code>{status}</code>{f'<br/><sub>last game: {st["last_result"]}</sub>' if st.get("last_result") else ""}

| 🧑 HUMANS | 🤖 AI | 🤝 DRAWS |
|:---:|:---:|:---:|
| **{s['human']}** | **{s['ai']}** | **{s['draw']}** |

<sub>🏆 Most moves: {hall} · <a href="{issue_link('ttt|new', 'reset board')}">↻ reset board</a></sub>

<details><summary><sub>recent moves</sub></summary>
<table><tr><th>time (UTC)</th><th>player</th><th>move</th></tr>{log}</table>
</details>

</div>
<!--TTT_END-->"""


def write_readme(st):
    md = open(README, encoding="utf-8").read()
    new = re.sub(r"<!--TTT_START-->.*?<!--TTT_END-->", lambda m: render(st), md, flags=re.S)
    open(README, "w", encoding="utf-8").write(new)


def finish(st, w, user):
    if w == "X":
        st["scores"]["human"] += 1; res = f"🏆 @{user} beat the AI!"
    elif w == "O":
        st["scores"]["ai"] += 1; res = "🤖 the AI won"
    else:
        st["scores"]["draw"] += 1; res = "🤝 draw"
    st["last_result"] = res
    st["board"] = "_________"
    return res


def main():
    st = load()
    if "--render" in sys.argv:
        write_readme(st); return
    title = os.environ.get("ISSUE_TITLE", "").strip().lower()
    user = re.sub(r"[^A-Za-z0-9-]", "", os.environ.get("ISSUE_USER", "someone"))[:39] or "someone"
    now = datetime.now(timezone.utc).strftime("%d %b %H:%M")
    msg = ""
    if title == "ttt|new":
        st["board"] = "_________"; st["last_result"] = f"board reset by @{user}"
        msg = "↻ Board reset. Your move!"
    else:
        m = re.fullmatch(r"ttt\|move\|([0-8])", title)
        if not m:
            msg = "⚠️ Couldn't read that move. Use the links in the README."
        else:
            i = int(m.group(1)); b = st["board"]
            if b[i] != "_":
                msg = f"⚠️ Cell {i} is already taken — someone got there first. Pick another glowing cell."
            else:
                b = b[:i] + "X" + b[i+1:]
                st["players"][user] = st["players"].get(user, 0) + 1
                st["log"].insert(0, {"t": now, "u": user, "m": f"✖ → {i}"})
                w = winner(b)
                if w:
                    st["board"] = b; res = finish(st, w, user)
                    msg = f"You played cell {i}. {res} New board is ready."
                else:
                    j = ai_move(b); b = b[:j] + "O" + b[j+1:]
                    st["log"].insert(0, {"t": now, "u": "neon-ai", "m": f"◯ → {j}"})
                    w = winner(b); st["board"] = b
                    if w:
                        res = finish(st, w, user)
                        msg = f"You played {i}, the AI answered {j}. {res} New board is ready."
                    else:
                        msg = f"You played **{i}**, the AI answered **{j}**. Your move!"
    st["log"] = st["log"][:20]
    os.makedirs("game", exist_ok=True)
    json.dump(st, open(STATE, "w"), indent=1)
    write_readme(st)
    open(COMMENT, "w").write(msg + f"\n\n[▶ Back to the board](https://github.com/{REPO.split('/')[0]})")
    print(msg)


if __name__ == "__main__":
    main()
