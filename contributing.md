# Contributing to AI Signal

Thank you for helping keep this list high-quality. The goal is signal, not comprehensiveness — every addition should make the list more useful, not just longer.

## Before you open a PR

Ask yourself: **would a serious practitioner find this source valuable 6 months from now?**

If yes, add it. If you're unsure, open an issue first.

---

## The one rule

**After any edit to `sources.yaml`, regenerate the OPML before committing:**

```bash
python generate_opml.py
git add sources.yaml sources.opml
git commit -m "your message"
```

Never commit `sources.yaml` without regenerating `sources.opml`. They must stay in sync.

---

## Adding a new source

1. Fork the repo and edit `sources.yaml`
2. Add your source following the schema below
3. `python generate_opml.py`
4. Open a PR with a brief note on why this source deserves inclusion

### Required fields

```yaml
- name: "Source Name"
  url: https://example.com
  rss: https://example.com/feed.xml   # strongly preferred
  type: individual                    # see types below
  depth: deep                         # shallow | medium | deep
  audience: [ml-engineer, builder]    # see audiences below
  tags: [inference, production]       # 3–6 lowercase tags
  activity: active                    # active | slow | archived
  last_checked: 2026-05               # YYYY-MM of when you verified this
```

### Optional but valued

```yaml
  landmark_posts:
    - title: "Post title"
      url: https://example.com/post
      why: "One sentence on why this specific post matters"
```

Landmark posts are what make this different from every other list. A good `why` is specific: not "great post about transformers" but "the clearest explanation of why attention is O(n²) and what alternatives exist."

---

## Source types

| Type | Use when |
|------|----------|
| `lab` | Official research blog of an AI lab |
| `individual` | A person's personal blog/newsletter |
| `systems` | Infrastructure, inference, or ML platform engineering |
| `paper-explainer` | Newsletters that translate research for practitioners |
| `applied` | Company engineering blog primarily about building with AI |
| `news` | Weekly digest or news aggregator |

## Audiences

| Audience | Means |
|----------|-------|
| `researcher` | PhD-level ML background expected |
| `ml-engineer` | Strong engineering + solid ML fundamentals |
| `builder` | Software engineer building AI products |
| `curious` | Technical but not ML-specialist |

Use multiple audiences when genuinely appropriate. Don't inflate — if a source is truly researcher-only, don't add `builder` to seem more inclusive.

## Depth guide

**`deep`** — assumes significant ML background. Follows mathematical notation, knows KL divergence, understands attention mechanisms. Posts require focused reading time.

**`medium`** — assumes software engineering competence. Introduces ML concepts without drowning in them. Most working ML engineers can follow without a textbook.

**`shallow`** — good for orientation. Summaries, digests, news. Valuable for staying aware without deep engagement.

---

## Updating activity status

| Status | Threshold |
|--------|-----------|
| `active` | Posts at least once every ~6 weeks |
| `slow` | Less than monthly, but posted in the last 18 months |
| `archived` | No posts in 18+ months — keep only if landmark posts exist |

To update:
1. Check the source URL — sometimes the blog is active but the main site looks stale
2. Edit `activity:` and update `last_checked:` to today's YYYY-MM
3. `python generate_opml.py`, commit, open a PR

Activity update PRs can batch multiple sources in one commit.

---

## What we won't add

- **Paywalled content** — readers must be able to access it freely
- **Tutorial farms** — sites that exist to rank on Google, not share genuine knowledge
- **Primarily marketing content** — blogs that are mostly product announcements
- **Podcast-only sources** — no written content, or transcripts only
- **Sources without a clear point of view** — generic aggregators with no editorial judgement
- **Dead sources** — no posts in 18+ months, unless landmark posts justify keeping it archived

### Non-English sources

Welcome, if they meet the same bar as everything else: focused on AI, free to read, original analysis or a clear editorial point of view. Reviewers work mainly in English, so evaluation may take a little longer.

### AI-assisted writing

Using AI as a writing tool is fine. Sites where most content is AI-generated, or that mainly summarise other outlets' news, usually fall under "no clear point of view" above.

### Same process for every source

Every listed source is handled the same way: its feed is checked weekly by automation, and its public posts may be read by the optional `/curate` tooling. We can't offer per-source exceptions to this.

---

## Removing a source

We remove sources if:
- They've been `archived` for 6+ months with no landmark posts
- The domain has changed hands and content is no longer relevant
- Quality has significantly degraded

Open an issue before removing — sometimes someone has context on a temporarily quiet source.

---

## PR etiquette

- One PR per source addition (keeps review clean)
- Activity update PRs can batch multiple sources
- Always include an updated `last_checked` date
- Always regenerate `sources.opml` before submitting

---

## Optional: AI-assisted curation

If you have Claude Code (Claude Pro), two slash commands can automate a curation pass. They edit `sources.yaml` directly using web search — no manual checking required.

This is entirely optional. The manual workflow above is the primary path.

```bash
# Open Claude Code in this directory, then run:
/scan-sources    # checks all sources for activity changes
/curate          # full pass: activity + landmark posts + new source discovery
```

After the command finishes, the agent prints a summary. Then:

```bash
git diff sources.yaml              # read what changed
# edit sources.yaml if you want to adjust or remove anything
python generate_opml.py            # regenerate if you made any edits
git add sources.yaml sources.opml
git commit -m "curate: YYYY-MM-DD"
git push
```

When submitting a PR for sources found via `/curate`, note that in your PR description — it helps reviewers understand the provenance.

---

## License

By contributing, you agree your contributions are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

This licence covers the catalogue entries in this repo — names, tags, ratings, and short notes like landmark `why` lines. It does not cover the linked articles, feeds, or images, which remain with their authors. AI Signal links to posts; it doesn't republish them.
