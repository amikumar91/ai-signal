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
