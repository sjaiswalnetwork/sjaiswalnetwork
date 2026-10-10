# ↻ Sync from LinkedIn (no AI, ~3 minutes)

1. On LinkedIn: **Me → Settings & Privacy → Data privacy → Get a copy of your data**.
2. Choose **"Want something in particular?"**, tick **only "Positions"**, click **Request archive**.
   *(Do not download the full archive — it contains your messages and contacts.)*
3. LinkedIn emails you a link (usually within 10 minutes). Download the small `.zip`.
4. Come back to this folder and click **Add file → Upload files**, drop the `.zip` (or the `Positions.csv` inside it), click **Commit changes**.
5. Wait ~1 minute. The Experience timeline on your profile redraws itself and the uploaded file is removed automatically.

Company names are never shown — they're replaced with the labels in [`data/experience.yml`](../data/experience.yml) (`company_labels`). Bullet points mentioning hidden words (e.g. pharma) are skipped.
