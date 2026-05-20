# Contributing to AI Signal

Thank you for helping keep this list high-quality. The goal is signal, not comprehensiveness — every addition should make the list more useful, not just longer.

## Before you open a PR

Ask yourself: **would a serious practitioner find this source valuable 6 months from now?**

If yes, add it. If you're unsure, open an issue first.

## Adding a new source

1. Fork the repo and edit `sources.yaml`
2. Add your source following the schema below
3. Run `python generate_opml.py` to regenerate `sources.opml`
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
  last_checked: 2025-05               # YYYY-MM of when you verified this
```

### Optional but valued

```yaml
  landmark_posts:
    - title: "Post title"
      url: https://example.com/post
      why: "One sentence on why this specific post matters"
```

Landmark posts are what make this different from every other list. A good `why` is specific: not "great post about transformers" but "the clearest explanation of why attention is O(n²) and what alternatives exist."

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
| `ml-engineer` | Strong engineering + some ML background |
| `builder` | Software engineer building AI products |
| `curious` | Technical but not ML-specialist |

Use multiple audiences when genuinely appropriate. Don't inflate — if a source is truly researcher-only, don't add `builder` to seem more inclusive.

## Depth guide

**`deep`** — assumes significant ML background. Expects the reader to follow mathematical notation, know what KL divergence is, understand attention mechanisms. Posts require focused reading time.

**`medium`** — assumes software engineering competence. May introduce ML concepts but doesn't drown in them. Most working ML engineers can follow without a textbook.

**`shallow`** — good for orientation. Summaries, digests, news. Valuable for staying aware without deep engagement.

## What we won't add

- **Hype/marketing content** — company blog posts that are primarily product announcements
- **Tutorial farms** — sites that exist to rank on Google, not to share genuine knowledge
- **Dead sources** — if the last post was more than 18 months ago and there are no landmark posts
- **Paywalled content** — readers should be able to access it
- **Sources without a clear point of view** — generic aggregators that add no editorial judgement

## Updating activity status

If you notice a source has gone quiet:

1. Check the RSS feed directly — sometimes the blog is active but the main site looks stale
2. If no posts in 90+ days, change `activity: active` → `activity: slow`
3. If no posts in 18+ months, change to `activity: archived`
4. Open a PR with the change

The staleness bot will flag these automatically every Monday, but human verification is better.

## Removing a source

We remove sources if:
- They've been `archived` for 6+ months with no landmark posts
- The domain has changed hands and the content is no longer relevant
- The quality has significantly degraded

Open an issue before removing — sometimes someone has context on why a source is temporarily quiet.

## PR etiquette

- One PR per source addition (keeps review clean)
- Activity update PRs can batch multiple sources
- Include the `last_checked` date as today's YYYY-MM
- Regenerate `sources.opml` before submitting (`python generate_opml.py`)

## Using the curation agent

The curation agent is the recommended way to discover new sources and audit
existing ones for landmark post candidates.

See `SETUP.md §4` for the full workflow. Short version:

```bash
python -m pip install pyyaml feedparser
python curate.py           # gather RSS data
# open Claude Code → say: run curation
# review CURATION_REPORT.md → apply to sources.yaml
python generate_opml.py
git add sources.yaml sources.opml && git commit -m "curate: YYYY-MM-DD"
```

When submitting a PR for sources found via the curation agent, note that in your
PR description — it helps reviewers understand the provenance.

## License

By contributing, you agree your contributions are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
