# Setup Guide

## 1. Verify the staleness bot

The staleness workflow runs every Monday at 09:00 UTC. To test it manually:

1. Go to **Actions** tab in your repo
2. Click **Staleness Check** in the left list
3. Click **Run workflow** → **Run workflow**

It will check all 31 RSS feeds and open a GitHub issue if any are stale. The issue will be labelled `staleness` and `automated`.

The workflow needs permission to open issues. Verify under:
**Settings** → **Actions** → **General** → **Workflow permissions** → select **Read and write permissions**.

---

## 2. Day-to-day workflow

### Adding a source
1. Edit `sources.yaml` — add an entry following the schema
2. Run `python generate_opml.py` locally
3. Commit both `sources.yaml` and `sources.opml`
4. Push — Pages redeploys automatically

### Reviewing a community PR
1. Check the new entry has all required fields
2. Verify the RSS feed URL actually works (paste into a browser)
3. If a landmark post is included, check the `why` is specific and useful
4. Merge — Pages redeploys automatically

### Responding to a staleness issue
1. Open the issue (auto-generated every Monday if stale sources exist)
2. For each flagged source, visit the URL and check if it's actually dead
3. Edit `sources.yaml`: change `activity: active` → `activity: slow` or `activity: archived`
4. PR or direct push → close the issue

---

## File reference

```
ai-signal/
├── sources.yaml                    ← THE data file — edit this
├── sources.opml                    ← Generated — don't edit by hand
├── generate_opml.py                ← Run after editing sources.yaml
├── index.html                      ← The website (self-contained)
├── README.md                       ← Repo front page
├── contributing.md                 ← Contribution guide
├── SETUP.md                        ← This file
└── .github/
    ├── labels.yml                  ← Label definitions (reference)
    ├── ISSUE_TEMPLATE/
    │   ├── add-source.yml          ← Form for suggesting a source
    │   └── stale-source.yml        ← Form for reporting a dead source
    ├── scripts/
    │   └── check_staleness.py      ← Staleness checker (run by workflow)
    └── workflows/
        ├── pages.yml               ← Deploy site on push to main
        └── staleness.yml           ← Weekly RSS freshness check
```

---

## 3.Troubleshooting

**Pages shows a 404**
- Check Settings → Pages → Source is set to "GitHub Actions" (not a branch)
- Check the Actions tab — the deploy workflow may have failed
- The first deploy takes ~2 minutes

**Staleness workflow fails with permission error**
- Settings → Actions → General → Workflow permissions → Read and write permissions

**OPML doesn't download from the site**
- GitHub Pages serves `.opml` files with the correct MIME type — should just work
- If not, try right-click → Save Link As

**generate_opml.py fails**
```bash
pip install pyyaml
python generate_opml.py
```

---

## 4. Running the curation agent

Two slash commands handle all curation. Both require Claude Code (Claude Pro) and
use **web search** as the primary signal — not RSS, which breaks silently.

### Commands

**`/scan-sources`** — Quick activity check

Opens Claude Code in this directory and runs `/scan-sources`. Claude web-searches
every source, updates `activity` and `last_checked` in `sources.yaml` in-place, and
prints a summary of what changed.

**`/curate`** — Full curation pass

Runs `/curate` in Claude Code. Claude:
1. Checks all existing sources for activity (web search, not RSS)
2. Identifies landmark-worthy recent posts and adds them to `sources.yaml`
3. Evaluates any URLs in `candidates.yaml`
4. Discovers new source candidates via web search
5. Appends qualifying new sources to `sources.yaml` marked `# PROPOSED`

### Workflow

```bash
# Optional: pre-fetch RSS data (supplementary only — web search is authoritative)
python -m pip install pyyaml feedparser
python curate.py

# Open Claude Code in this directory, then run:
/curate       # or /scan-sources for a quick activity-only check

# Review all edits Claude made:
git diff sources.yaml

# When satisfied:
python generate_opml.py
git add sources.yaml sources.opml
git commit -m "curate: YYYY-MM-DD"
git push
```

GitHub Pages redeploys automatically within ~2 minutes.

### Queuing candidate sources

To add a specific URL for evaluation, add it to `candidates.yaml` before running
`/curate`:

```yaml
candidates:
  - name: "Latent Space"
    url: https://www.latent.space/
    rss: https://www.latent.space/feed
```

Claude evaluates it against the `contributing.md` criteria and either adds it to
`sources.yaml` (marked `# PROPOSED`) or skips it. Clear the entry after evaluation.

### Frequency

Run `/curate` monthly. `/scan-sources` can run any time you suspect activity statuses
are drifting. The GitHub Actions staleness workflow (every Monday) only checks RSS
feed liveness — `/scan-sources` goes deeper by verifying the actual website.

### Troubleshooting

**`curate.py` exits with "Missing deps"**
```bash
python -m pip install pyyaml feedparser
```

**curate.py shows 0 recent posts for a clearly active source**
This is an RSS parsing failure, not real inactivity. Ignore it — `/curate` and
`/scan-sources` use web search and will correctly identify the source as active.
