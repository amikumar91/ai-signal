# /curate — AI Signal full curation pass

Full curation: verify existing sources via web search, discover new ones, surface
landmark posts. All changes go directly into `sources.yaml` — review with `git diff`,
then run `python generate_opml.py` and commit.

Do NOT write a separate report file. Edit `sources.yaml` directly.

---

## Step 1 — Activity scan (same logic as /scan-sources)

Read `sources.yaml`. For each source, web search `site:{domain} {current year}` to
confirm recent activity. Apply the activity rules below and edit in-place.

| Current | Recent posts (last 90 days)? | Action |
|---------|------------------------------|--------|
| `active` | Yes | No change |
| `active` | No | → `slow` |
| `slow` | Yes | → `active` |
| `slow` | No, last post < 18 months ago | No change |
| `slow` | No, last post > 18 months ago | → `archived` |
| `archived` | Any | No change |

Update `last_checked` to current YYYY-MM for every source you verify.

---

## Step 2 — Landmark post detection on existing sources

While scanning each source, check whether any recent posts are landmark-worthy.
A post qualifies if ALL three are true:
1. Covers a topic not already in that source's `landmark_posts`
2. Will still be useful to an ML engineer 12 months from now (not news, not a release note)
3. Demonstrates unusual depth, breadth, or clarity — not a routine post

Add qualifying posts directly to the source's `landmark_posts` list in `sources.yaml`:

```yaml
landmark_posts:
  - title: "Post Title"
    url: https://...
    why: "One sentence — specific reason this post matters, not 'great post about X'"
```

---

## Step 3 — Check candidates.yaml

If `candidates.yaml` exists and has entries under `candidates:`, evaluate each one:
1. Web search `site:{domain} 2026` to confirm the source has posted recently
2. Verify it has a working RSS feed URL
3. Check it is NOT already in `sources.yaml`
4. Check it is NOT paywalled
5. Check it passes the `contributing.md` "signal not noise" bar — specific POV, not a
   tutorial farm, not primarily marketing or product announcements

If a candidate passes all five checks → add it to sources.yaml (see Step 4).
If it fails → skip it (do not add).

---

## Step 4 — Discover new sources via web search

Run these searches to find candidates not in `sources.yaml` and not already in
`candidates.yaml`:

```
best AI ML blogs 2026 -site:medium.com
top AI newsletters 2026 site:substack.com OR site:github.io
site:news.ycombinator.com "AI blog" 2026
new AI researcher blog active 2026
mechanistic interpretability blog 2026
AI inference systems blog 2026
```

Apply the same five-point check from Step 3 to each candidate found.

---

## Step 5 — Edit sources.yaml directly

### For existing sources (activity + landmark posts)
Edit in-place — change the `activity:` value, update `last_checked:`, append to
`landmark_posts:` if applicable. No markers needed.

### For new source candidates
Append at the bottom of the correct category section with a `# PROPOSED` marker:

```yaml
  # PROPOSED — review before committing
  - name: "Source Name"
    url: https://...
    rss: https://...
    type: X              # lab | individual | applied | systems | paper-explainer | news
    depth: X             # shallow | medium | deep
    audience: [X, Y]     # researcher | ml-engineer | builder | curious
    tags: [tag1, tag2, tag3]
    activity: active
    last_checked: 2026-05
```

Remove entries from `candidates.yaml` after evaluating them (pass or fail).

---

## Step 6 — Run generate_opml.py

```bash
python generate_opml.py
```

---

## Step 7 — Print a summary

```
Curation complete — YYYY-MM-DD
  Activity changes: N sources updated
  Landmark posts added: N
  New sources proposed: N (marked # PROPOSED in sources.yaml)

Review all changes:
  git diff sources.yaml

Commit when ready:
  git add sources.yaml sources.opml
  git commit -m "curate: YYYY-MM-DD"
  git push
```
