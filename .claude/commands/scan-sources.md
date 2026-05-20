# /scan-sources — AI Signal source activity checker

Check every source in `sources.yaml` for recent activity using web search, then
update `sources.yaml` directly with corrected `activity` and `last_checked` fields.

## Why web search, not RSS

RSS feeds break, change URLs, or silently fail. Web search is ground truth —
it shows what has actually been published. Never rely solely on RSS to determine
whether a source is active.

## Steps

### 1. Read sources

Read `sources.yaml` to get all sources and their current `activity` status.

### 2. Search each source for recent posts

For each source run a web search using `site:{domain} {current year}`.
Examples:
- `site:simonwillison.net 2026`
- `site:lilianweng.github.io 2026`
- `site:blog.vllm.ai 2026`

If that returns nothing, try: `"{source name}" blog post 2026`.

From the results determine:
- Has the source published in the last 90 days? (yes / no)
- Approximate date of the most recent post
- Any posts that look landmark-worthy (title + URL)

You can run several sources in one search where domains are distinct enough.

### 3. Apply activity rules

| Current status | Recent posts in last 90 days? | Action |
|----------------|-------------------------------|--------|
| `active` | Yes | No change |
| `active` | No | Change to `slow` |
| `slow` | Yes | Change to `active` |
| `slow` | No, last post < 18 months ago | No change |
| `slow` | No, last post > 18 months ago | Change to `archived` |
| `archived` | Any | No change |

### 4. Edit sources.yaml in-place

For every source where activity or last_checked changed:
- Update the `activity:` field
- Set `last_checked:` to the current YYYY-MM
- If you found a landmark-worthy post, add it to `landmark_posts:` too

Do not change any other fields.

### 5. Run generate_opml.py

```bash
python generate_opml.py
```

### 6. Print a summary of changes

```
Scanned N sources.
  ✓ confirmed active: [list names]
  ↓ downgraded active → slow: [list names, last post date]
  ↑ upgraded slow → active: [list names, last post date]
  → archived: [list names]
  ⚠ could not verify: [list names — check manually]

Review: git diff sources.yaml
Commit: git add sources.yaml sources.opml && git commit -m "chore: activity scan YYYY-MM-DD"
```
