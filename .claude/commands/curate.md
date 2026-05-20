# /curate — AI Signal full curation pass

Full curation: verify existing sources, discover new ones, surface landmark posts.
All changes go directly into `sources.yaml`. Review with `git diff`, then run
`python generate_opml.py` and commit.

**Do NOT write a report file. Edit `sources.yaml` directly.**

---

## Coverage target

The goal is **80–100 sources**. If the current count is below 80, discovery (Step 4)
is the most important step — bias toward proposing more candidates rather than fewer.
A curated list with 35 sources feels like a personal bookmark folder. One with 90
feels like a resource the community trusts.

---

## Vocabulary — use these definitions consistently

### Source types
| Value | Use when |
|-------|----------|
| `lab` | Official research blog of an AI lab (Anthropic, OpenAI, DeepMind, Meta AI, BAIR, etc.) |
| `individual` | A person's personal blog or newsletter — single author, strong POV |
| `systems` | Infrastructure, inference, GPU serving, ML platform engineering |
| `paper-explainer` | Newsletters or blogs that translate research papers for practitioners |
| `applied` | Company engineering blog primarily about building *with* AI (tools, evals, production) |
| `news` | Weekly digest or news aggregator — broad coverage, not deep technical |

### Depth
| Value | Means |
|-------|-------|
| `deep` | Assumes strong ML background. Follows math notation, knows KL divergence, attention internals. Posts reward focused reading time. |
| `medium` | Assumes software engineering competence. Introduces ML concepts without drowning in them. Most working ML engineers can follow without a textbook. |
| `shallow` | Good for orientation. Summaries, digests, news. Low time commitment. |

### Audience
| Value | Means |
|-------|-------|
| `researcher` | PhD-level ML background expected. Reads papers, implements from scratch. |
| `ml-engineer` | Strong engineering + solid ML fundamentals. Trains and deploys models. |
| `builder` | Software engineer building AI products. Uses APIs and frameworks, not training from scratch. |
| `curious` | Technical but not ML-specialist. Wants to stay oriented, not go deep. |

Use multiple audiences only when genuinely appropriate. A `researcher`-only source should not also get `builder` to seem inclusive.

### Activity
| Value | Means | Threshold |
|-------|-------|-----------|
| `active` | Posts regularly | At least once every ~6 weeks |
| `slow` | Infrequent but still publishing | Less than monthly, but posted in last 18 months |
| `archived` | No longer updating | No posts in 18+ months — keep only if landmark posts exist |

### Landmark posts
A landmark post is one that meets ALL three:
1. Covers a concept or technique not already in that source's `landmark_posts` list
2. Will be useful to an ML engineer reading it 12 months from now — not news, not a release note, not a product announcement
3. Demonstrates unusual depth, breadth, or clarity — something you'd recommend to a colleague by name

The `why` field must be specific: not "great post about RAG" but "the clearest explanation of why naive RAG fails at scale and exactly which retrieval strategies fix it."

---

## Step 1 — Activity scan (web search, not RSS)

Read `sources.yaml`. For each source, run: `site:{domain} {current year}`
Example: `site:simonwillison.net 2026`

If that returns nothing: `"{source name}" blog post {current year}`.

Determine: has the source published in the last 90 days? What is the most recent post date?

Apply the activity rules:

| Current | Recent posts (last 90 days)? | Action |
|---------|------------------------------|--------|
| `active` | Yes | No change |
| `active` | No | → `slow` |
| `slow` | Yes | → `active` |
| `slow` | No, last post < 18 months ago | No change |
| `slow` | No, last post > 18 months ago | → `archived` |
| `archived` | — | No change |

Update `last_checked` to current YYYY-MM for every source you verify.
Edit `activity` and `last_checked` in-place — do not change other fields unless you also find a landmark post.

---

## Step 2 — Landmark post detection on existing sources

While scanning each source, check whether any recent posts are landmark-worthy (see definition above). Add qualifying posts to that source's `landmark_posts` in `sources.yaml`:

```yaml
landmark_posts:
  - title: "Post Title"
    url: https://...
    why: "Specific one sentence — what this teaches and why it matters, not 'great post about X'"
```

---

## Step 3 — Evaluate candidates.yaml

If `candidates.yaml` exists and has entries, evaluate each one using the five-point check below. Do this before running discovery searches so you don't duplicate work.

---

## Step 4 — Discover new sources

This step must find sources NOT currently in `sources.yaml`. The goal is to propose
enough candidates to move the list toward 80–100 sources total. Cast a wide net.

### 4a — Check known gaps first

Before running discovery searches, check whether these canonical sources are already
in `sources.yaml`. For any that are missing, evaluate them and add as candidates:

**Labs and academic:**
- Google AI Blog (blog.google/technology/ai)
- Microsoft Research Blog (microsoft.com/en-us/research/blog)
- BAIR Blog — Berkeley AI Research (bair.berkeley.edu/blog)
- NVIDIA Developer Blog — AI section (developer.nvidia.com/blog)
- EleutherAI Blog (blog.eleuther.ai)
- Apple Machine Learning Research (machinelearning.apple.com)
- IBM Research Blog — AI (research.ibm.com/blog)
- Stability AI Blog (stability.ai/blog)
- xAI Blog (x.ai/blog)
- Cohere Blog (cohere.com/blog)

**Individual researchers and educators:**
- fast.ai / Jeremy Howard (fast.ai)
- Answer.AI (answer.ai) — Jeremy Howard's research lab
- Yannic Kilcher — if he maintains a written blog alongside YouTube
- François Chollet — if he has a blog with RSS (primary presence is Twitter/Medium)
- Dan Hendrycks (hendrycks.com or substack)
- Robert Miles — AI safety educator

**Infrastructure and systems:**
- LlamaIndex Blog (llamaindex.ai/blog)
- Replicate Blog (replicate.com/blog)
- Ollama Blog (ollama.com/blog)
- Groq Blog (groq.com/blog)
- Lightning AI Blog (lightning.ai/blog)
- BentoML Blog (bentoml.com/blog)
- Fireworks AI Blog (fireworks.ai/blog)
- Cerebras Blog (cerebras.net/blog)

**Applied / company engineering blogs:**
- Roboflow Blog (blog.roboflow.com) — computer vision
- Scale AI Blog (scale.com/blog)
- Nomic AI Blog (nomic.ai/blog)
- Runway Blog (runwayml.com/blog)
- Pydantic AI Blog / Instructor Blog (jxnl.co)
- Arize AI Blog (arize.com/blog)
- Evidently AI Blog (evidentlyai.com/blog)

**Paper explainers and safety:**
- AI Alignment Forum (alignmentforum.org)
- LessWrong AI section (lesswrong.com/tag/ai)
- Papers With Code Blog (paperswithcode.com/blog)
- ML Research Highlights (ml-research-highlights.com or similar)
- Ahead of AI — check if not already listed as a named source vs. Sebastian Raschka's main blog

**News and digests:**
- Ben's Bites (bensbites.com)
- TLDR AI (tldr.tech/ai)
- Alpha Signal (alphasignal.ai)

### 4b — Run discovery searches

Run all of these searches to find sources not covered in 4a:

```
best AI ML technical blogs 2026 -site:medium.com -site:kdnuggets.com
top AI newsletters 2026 substack researchers practitioners
site:news.ycombinator.com "AI blog" OR "ML blog" 2026
new AI researcher blog active 2026
mechanistic interpretability blog 2026
AI inference serving systems blog 2026
AI safety alignment blog active 2026
LLM fine-tuning quantization blog 2026
applied AI engineering blog production 2026
AI company engineering blog 2026
computer vision ML blog active 2026
AI evaluation evals blog 2026
```

Also consider: authors cited repeatedly in recent landmark posts from existing sources who publish their own blog not yet in the list.

---

## Five-point check for every candidate

1. Has a working RSS feed URL?
2. Meets the activity threshold — one of:
   - **For company/org blogs:** at least 3 posts in the last 90 days
   - **For individual researcher blogs:** at least 3 posts in the last 12 months, OR a landmark-quality archive even if posting slowly (a researcher who posts 6×/year with exceptional depth qualifies; one who posts 6×/year with shallow content does not)
3. Has a specific editorial POV — not a link dump, not generic?
4. Not already in `sources.yaml`?
5. Not paywalled?

Only propose sources that pass all five.

**Explicitly excluded categories** — do not propose these regardless of quality:
- Paywalled sources (readers must be able to access it freely)
- Tutorial farms (sites that exist to rank on Google, not share genuine knowledge)
- Primarily marketing or product announcement blogs
- Podcast-only sources with **no written content** (audio/video transcript dumps don't count; but a podcast with substantive written show notes or companion posts *does* qualify — evaluate the writing, not the medium)
- Generic aggregators with no editorial judgement
- Sources with no RSS feed (can't be imported into an RSS reader)
- Dead sources (no posts in 18+ months) unless landmark posts justify archiving

---

## Step 5 — Edit sources.yaml directly

### Existing sources — edit in-place
Change `activity:`, update `last_checked:`, append to `landmark_posts:`. No markers needed for changes to existing entries.

### New source candidates — append with PROPOSED marker
Add at the bottom of the correct section, with a `# PROPOSED` comment:

```yaml
  # PROPOSED — review before committing
  - name: "Source Name"
    url: https://...
    rss: https://...
    type: X
    depth: X
    audience: [X, Y]
    tags: [tag1, tag2, tag3]
    activity: active
    last_checked: 2026-05
```

After evaluating candidates.yaml entries (pass or fail), remove them from candidates.yaml.

---

## Step 6 — Run generate_opml.py

```bash
python generate_opml.py
```

---

## Step 7 — Print summary

```
Curation complete — YYYY-MM-DD
  Sources scanned: N
  Activity updated: N (list names + change)
  Landmark posts added: N (source name + post title)
  New sources proposed: N (list names, marked # PROPOSED)
  Candidates evaluated: N (pass/fail breakdown)
  Current total: N  (target: 80–100)

Review:  git diff sources.yaml
Commit:  git add sources.yaml sources.opml && git commit -m "curate: YYYY-MM-DD"
Push:    git push
```
