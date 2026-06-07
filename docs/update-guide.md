# Update Guide

This repository is generated from GitHub stars, cached repository metadata, and manual curation files.

## Recommended Daily Workflow

Use the local review UI for normal updates:

```powershell
python scripts\review_server.py
```

Open `http://127.0.0.1:8765` and use these actions:

- `Add Repo URL`: paste a GitHub repository URL when you only want to add one new star immediately.
- `Add Category`: create a new category without editing JSON or CSV by hand.
- `Primary Category`: choose the main category for the selected repository.
- `Additional Labels`: assign extra categories when one repository belongs to multiple topics.
- `Rebuild README`: regenerate `README.md` and `docs/` after manual changes.

## Full Refresh

Run the full pipeline when you have added many stars, changed GitHub Lists, or want to resync everything:

```powershell
python scripts\sync_lists.py
python scripts\fetch_repo_metadata.py
python scripts\classify_repos.py
python scripts\build_readme.py
```

## Fast Single-Repository Update

If you only added one new star and do not want to resync all GitHub Lists:

1. Start the UI with `python scripts\review_server.py`.
2. Paste the repository URL into `Add Repo URL`.
3. Select a primary category and any additional labels.
4. Click `Rebuild README`.

This stores the repository in `data/manual_repos.json`, fetches only that repository, and keeps the generated README up to date.

## Manual Files

The UI is the easiest option, but the underlying files are simple and can be edited directly if needed.

| File | Purpose |
| --- | --- |
| `data/manual_categories.csv` | Manual primary category, extra labels, and notes. |
| `data/custom_categories.json` | User-defined categories created by the UI. |
| `data/manual_repos.json` | Manually added repositories outside the GitHub Lists sync. |
| `data/review_queue.csv` | Low-confidence or uncategorized repositories to review. |

A manual category row looks like this:

```csv
repo,category,labels,note
owner/repo,primary-category-id,extra-label-a;extra-label-b,why this belongs here
```

After direct file edits, rerun:

```powershell
python scripts\classify_repos.py
python scripts\build_readme.py
```

## Pipeline Reference

- `sync_lists.py` refreshes your public GitHub Lists and repository membership.
- `fetch_repo_metadata.py` fetches metadata for newly seen repositories and reuses the local cache for old ones.
- `classify_repos.py` assigns each repository to a direct category and applies manual labels.
- `build_readme.py` regenerates the README and category pages.
- `data/review_queue.csv` lists repositories that need manual review or have low classification confidence.

## Curation Notice

The classification is semi-automatic and intended for personal research navigation. Some repositories may be missing, outdated, multi-topic, or placed in a category that is not the best fit. Treat the index as a curated starting point rather than an authoritative benchmark.

Do not edit generated docs directly because they will be overwritten.

Current metadata fetch failures: `3`. These can usually be retried later by rerunning `fetch_repo_metadata.py`.
