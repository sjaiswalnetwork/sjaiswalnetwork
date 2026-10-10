# 📘 How to update my GitHub profile + website

**No AI needed.** One update changes **both** places:
- GitHub profile → github.com/sjaiswalnetwork (redraws in ~1 min)
- Website → **sjaiswalnetwork.github.io** (shows changes within ~5 min)

---

## ✏️ Way 1: Type the change (fastest, ~1 min)

Open the file → click the ✏️ pencil (top-right) → edit → green **Commit changes…** → **Commit changes**.

| To change… | File |
|---|---|
| Jobs / experience timeline | [`data/experience.yml`](data/experience.yml) |
| Certifications / awards | [`data/credentials.yml`](data/credentials.yml) |
| Website text: headline, "Open to" roles, counters, about, quick facts, impact, projects, achievements, skills | [`data/profile.yml`](data/profile.yml) |
| LinkedIn posts on the website (paste post links) | [`data/posts.yml`](data/posts.yml) |
| Recommendations on the website | [`data/recommendations.yml`](data/recommendations.yml) |

> ⚠️ Keep the spaces at the start of each line exactly as they are, and keep text inside "quotes". To add an item, copy the block above it and change the words.

**To add a LinkedIn post:** on LinkedIn, click **⋯** on your post → **Copy link to post**. In `data/posts.yml`, replace `posts: []` the first time with:
```yaml
posts:
  - link: "PASTE THE LINK"
    date: "Oct 2026"
    text: "First line of the post"
```

---

## ↻ Way 2: Copy from LinkedIn (~3 min + LinkedIn's email wait)

### A. Experience, certifications, awards, recommendations
1. Update your LinkedIn first.
2. LinkedIn → **Me** → **Settings & Privacy** → **Data privacy** → **Get a copy of your data**.
3. Choose **"Want something in particular?"** → tick **Profile** and **Recommendations** only → **Request archive**.
4. LinkedIn emails a link (usually within 10 min). Download the small `.zip`.
5. Open the [`linkedin/`](linkedin/) folder → **Add file → Upload files** → drop the `.zip` → **Commit changes**.

### B. All your posts (optional)
LinkedIn only includes posts in its **large** archive, which also has your **messages and contacts**, so never upload that zip.
1. Same page → choose **"Download larger data archive"** → Request. (LinkedIn can take up to 24 h.)
2. Unzip it **on your computer**. Find the single file **`Shares.csv`**.
3. Upload **only `Shares.csv`** to the [`linkedin/`](linkedin/) folder → **Commit changes**.
4. Delete the rest of the unzipped folder from your computer.

> 🛡️ Safety net: if the full archive is uploaded by mistake, the robot refuses to read it and removes it. It still stays in the page's history, though, so don't rely on this.

After either upload, wait ~1 minute. The uploaded file is removed automatically.

---

## Good to know
- **Company names never show.** They're replaced by the labels in `data/experience.yml` → `company_labels`. When you join a new company, add one line there, e.g. `"New Company Name": "Manufacturing · City"`.
- **Hidden words:** bullet points containing words in `hide_words` (e.g. pharma) are skipped.
- **Check it ran:** the [Actions tab](../../actions/workflows/experience.yml) shows a ✅ green tick. A ❌ red cross means a typo; open the file and compare with the line above it.
- **Updates itself, nothing to do:** live commit feed, the snake, GitHub stats, view counter.
