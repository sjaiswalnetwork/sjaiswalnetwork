# 📘 How to update my GitHub profile

No AI needed. Pick **one** way. The profile redraws itself about **1 minute** after you save.

---

## Way 1: Type the change (fastest, ~1 min)

| To change… | Open this file | What to do |
|---|---|---|
| Jobs / experience timeline | [`data/experience.yml`](data/experience.yml) → click ✏️ (pencil, top-right) | Edit the text inside "quotes". Newest job on top. |
| Certifications / awards | [`data/credentials.yml`](data/credentials.yml) → click ✏️ | Copy any 3-line block (`name`, `issuer`, `date`), paste it at the top, change the words. |

Then click the green **Commit changes…** button → **Commit changes** again. Done.

> ⚠️ Keep the spaces at the start of each line exactly as they are. If the picture doesn't update, a space or a quote mark is probably missing. Compare with the line above it.

---

## Way 2: Copy from LinkedIn (~3 min + LinkedIn's email wait)

1. Update your LinkedIn first.
2. LinkedIn → **Me** → **Settings & Privacy** → **Data privacy** → **Get a copy of your data**.
3. Choose **"Want something in particular?"** and tick **only**:
   - ✅ Positions
   - ✅ Certifications
   - ✅ Honors
   
   ❌ Do **not** download the full archive. It contains your messages and contacts.
4. Click **Request archive**. LinkedIn emails you a link (usually within 10 minutes). Download the small `.zip`.
5. Open the [`linkedin/`](linkedin/) folder here → **Add file** → **Upload files** → drop the `.zip` → **Commit changes**.
6. Wait ~1 minute. Experience + certifications on your profile are redrawn, and the uploaded file is removed automatically.

---

## Good to know

- **Company names never show.** They're replaced by labels in `data/experience.yml` → `company_labels` (e.g. "Manufacturing · Noida"). Add a new line there when you join a new company.
- **Hidden words:** bullet points containing words in `hide_words` (e.g. pharma) are skipped automatically.
- **Check it ran:** the [Actions tab](../../actions/workflows/experience.yml) shows a ✅ green tick. A ❌ red cross means a typo in the file; open the file and compare with the line above it.
- **Other things that update themselves** (no action needed): live feed of recent commits, the snake, GitHub stats and the view counter.
