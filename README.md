# AI Signal

**A curated, structured reading layer for the AI field.**

Not a link dump. Not a Twitter list. A community-maintained set of sources with depth ratings, audience tags, and landmark post annotations — built for people who want signal, not noise.

→ **[Browse the site](https://amikumar91.github.io/ai-signal)**
→ **[Download OPML](sources.opml)** — import into Feedly, Reeder, NetNewsWire, Inoreader

---

## Why this exists

AI is moving fast enough that:
- A blog post from 6 months ago may already be obsolete
- Good signal is scattered across arXiv, Substacks, GitHub, lab blogs, and Twitter threads
- "Awesome AI" lists are alphabetical link dumps with no curation signal

This repo is the data layer. Community PRs keep it updated. GitHub Actions flags stale sources automatically. You spend zero time curating — and get a feed that actually reflects the field's current state.

## Structure

The entire dataset lives in [`sources.yaml`](sources.yaml). Everything else is generated from it.

```yaml
- name: "Lilian Weng"
  url: https://lilianweng.github.io
  rss: https://lilianweng.github.io/index.xml
  type: individual        # lab | individual | applied | systems | paper-explainer | news
  depth: deep             # shallow | medium | deep
  audience: [researcher, ml-engineer]
  tags: [transformers, rl, diffusion, survey, agents]
  activity: active        # active | slow | archived
  last_checked: 2025-05
  landmark_posts:
    - title: "Extrinsic Hallucinations in LLMs"
      url: https://lilianweng.github.io/posts/2024-07-07-hallucination/
      why: "Best taxonomy of hallucination types — required reading before building any production LLM system"
```

### Generated outputs

| File | What it is |
|------|-----------|
| `sources.yaml` | The canonical data — edit this |
| `sources.opml` | Generated RSS feed list (import into any reader) |
| `index.html` | Rendered, filterable website |

### Source types

| Type | What it means |
|------|--------------|
| `lab` | Official research blogs from AI labs |
| `individual` | Individual practitioners or researchers |
| `systems` | Infrastructure, inference, serving |
| `paper-explainer` | Newsletters and blogs that explain research |
| `applied` | Company engineering blogs building with AI |
| `news` | Weekly digests and news |

### Depth ratings

| Rating | Means |
|--------|-------|
| `deep` | Assumes strong technical background; rewards careful reading |
| `medium` | Accessible to engineers without ML specialisation |
| `shallow` | Good for staying oriented; low time commitment |

### Activity status

| Status | Means |
|--------|-------|
| `active` | Posts regularly (at least monthly) |
| `slow` | Infrequent posts but high quality when they appear |
| `archived` | No longer updating — kept for landmark posts |

## Using the OPML

Import `sources.opml` into:
- **Feedly** — Add Content → OPML import
- **Reeder** (iOS/macOS) — Add Account → OPML
- **NetNewsWire** — File → Import Subscriptions
- **Inoreader** — Preferences → Import

The OPML is grouped by source type so you can subscribe to just the categories you want.

## Automation

A GitHub Actions workflow runs every Monday and:
1. Checks every RSS feed for recent activity
2. Flags sources with no posts in 90+ days
3. Opens a GitHub issue with the stale list for community review

Maintenance becomes optional triage rather than active work.

## Curation

A local curation agent helps discover new sources and surface landmark posts from
existing ones. It runs entirely within Claude Code — no API key needed.

**Requirements:** Claude Code (Claude Pro), Python 3.11+

```bash
python -m pip install pyyaml feedparser
python curate.py          # ~1 min — fetches recent RSS data from all sources
```

Then open Claude Code in this directory and say: **run curation**

Claude reads the gathered RSS data, searches the web for new source candidates,
and writes `CURATION_REPORT.md` — a structured checklist of proposals. Review it,
apply the items you agree with to `sources.yaml`, then:

```bash
python generate_opml.py
git add sources.yaml sources.opml
git commit -m "curate: YYYY-MM-DD curation pass"
```

See `SETUP.md` for the full curation workflow.

## Contributing

Read [`contributing.md`](contributing.md) for the full guide. The short version:

1. Edit `sources.yaml` — add your source following the schema above
2. Run `python generate_opml.py` to regenerate the OPML
3. Open a PR

**Adding a source:** Fill in all required fields. RSS feed URL is strongly preferred. Landmark posts are optional but highly valued — they're what make this more than a link list.

**Updating activity status:** If a source has gone quiet, open a PR changing `activity: active` to `activity: slow` or `activity: archived`.

**Removing a source:** Sources are only removed if they've been `archived` for 6+ months with no landmark posts.

## Stats

| | Count |
|-|-------|
| Total sources | 31 |
| With RSS feeds | 31 |
| Landmark posts | 12+ |
| Categories | 6 |

---

Licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Not affiliated with any listed organization.
