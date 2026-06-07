from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLASSIFIED_PATH = ROOT / "data" / "classified_repos.json"
METADATA_PATH = ROOT / "data" / "repo_metadata.json"
README_PATH = ROOT / "README.md"
DOCS_DIR = ROOT / "docs"
CATEGORY_DIR = DOCS_DIR / "categories"

CJK_RE = re.compile(r"[\u3400-\u9fff]")
MOJIBAKE_MARKERS = ("�", "æ", "ç", "å", "è", "é", "ã", "ï¼", "€")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def slug_path(category_id: str) -> str:
    return f"docs/categories/{category_id}.md"


def display_name(repo: dict) -> str:
    return repo["full_name"].replace(" /", "/").replace("/ ", "/").replace(" ", "")


def star_value(repo: dict) -> float:
    label = repo.get("list_stars_label", "")
    if not label:
        return 0.0
    try:
        return float(label.lower().replace("k", "000").replace(",", ""))
    except ValueError:
        return 0.0


def repo_sort_key(repo: dict) -> tuple:
    return (-star_value(repo), display_name(repo).lower())


def public_text(text: str) -> str:
    text = " ".join((text or "").split())
    if not text:
        return ""
    if CJK_RE.search(text):
        return ""
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        return ""
    return text


def short_text(text: str, limit: int = 180) -> str:
    text = public_text(text)
    if not text:
        return ""
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def category_name(cat_id: str, info: dict) -> str:
    return public_text(info.get("name", "")) or cat_id.replace("-", " ").title()


def category_description(info: dict) -> str:
    return public_text(info.get("description", ""))


def repo_line(repo: dict) -> str:
    desc = short_text(repo.get("display_description") or "", 190)
    line = f"- [{display_name(repo)}]({repo['url']})"
    if desc:
        line += f" - {desc}"
    return line


def category_entries(payload: dict) -> list[tuple[str, dict]]:
    return [
        (cat_id, info)
        for cat_id, info in payload["categories"].items()
        if info["count"] > 0
    ]


def build_category_doc(cat_id: str, info: dict, payload: dict) -> str:
    repos = [
        repo
        for repo in payload["repos"].values()
        if cat_id in repo.get("labels", [])
    ]
    repos.sort(key=repo_sort_key)

    groups: dict[str, list[dict]] = {}
    for repo in repos:
        subtopic = public_text(repo.get("primary_subtopic") or "") or "General"
        groups.setdefault(subtopic, []).append(repo)

    lines = [
        f"# {category_name(cat_id, info)}",
        "",
        category_description(info),
        "",
        f"Repositories: `{len(repos)}`",
        "",
        "[Back to README](../../README.md)",
        "",
    ]

    if len(groups) > 1:
        lines.extend(["| Topic | Repos |", "| --- | ---: |"])
        for subtopic, subtopic_repos in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
            lines.append(f"| {subtopic} | {len(subtopic_repos)} |")
        lines.append("")

    for subtopic, subtopic_repos in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(groups) > 1:
            lines.extend([f"## {subtopic}", ""])
        for repo in subtopic_repos:
            lines.append(repo_line(repo))
        if len(groups) > 1:
            lines.append("")

    return "\n".join(line for line in lines if line is not None).strip() + "\n"


def build_category_index(payload: dict) -> str:
    lines = [
        "# Category Index",
        "",
        "Direct small-category index generated from repository metadata and the original GitHub Lists as weak priors.",
        "",
        "| Category | Repos | Description |",
        "| --- | ---: | --- |",
    ]
    for cat_id, info in category_entries(payload):
        lines.append(
            f"| [{category_name(cat_id, info)}](categories/{cat_id}.md) | {info['count']} | {category_description(info)} |"
        )
    return "\n".join(lines).strip() + "\n"


def build_update_guide(metadata: dict) -> str:
    failures = len(metadata.get("failures", {}))
    lines = [
        "# Update Guide",
        "",
        "This repository is generated from GitHub stars, cached repository metadata, and manual curation files.",
        "",
        "## Recommended Daily Workflow",
        "",
        "Use the local review UI for normal updates:",
        "",
        "```powershell",
        "python scripts\\review_server.py",
        "```",
        "",
        "Open `http://127.0.0.1:8765` and use these actions:",
        "",
        "- `Add Repo URL`: paste a GitHub repository URL when you only want to add one new star immediately.",
        "- `Add Category`: create a new category without editing JSON or CSV by hand.",
        "- `Primary Category`: choose the main category for the selected repository.",
        "- `Additional Labels`: assign extra categories when one repository belongs to multiple topics.",
        "- `Rebuild README`: regenerate `README.md` and `docs/` after manual changes.",
        "",
        "## Full Refresh",
        "",
        "Run the full pipeline when you have added many stars, changed GitHub Lists, or want to resync everything:",
        "",
        "```powershell",
        "python scripts\\sync_lists.py",
        "python scripts\\fetch_repo_metadata.py",
        "python scripts\\classify_repos.py",
        "python scripts\\build_readme.py",
        "```",
        "",
        "## Fast Single-Repository Update",
        "",
        "If you only added one new star and do not want to resync all GitHub Lists:",
        "",
        "1. Start the UI with `python scripts\\review_server.py`.",
        "2. Paste the repository URL into `Add Repo URL`.",
        "3. Select a primary category and any additional labels.",
        "4. Click `Rebuild README`.",
        "",
        "This stores the repository in `data/manual_repos.json`, fetches only that repository, and keeps the generated README up to date.",
        "",
        "## Manual Files",
        "",
        "The UI is the easiest option, but the underlying files are simple and can be edited directly if needed.",
        "",
        "| File | Purpose |",
        "| --- | --- |",
        "| `data/manual_categories.csv` | Manual primary category, extra labels, and notes. |",
        "| `data/custom_categories.json` | User-defined categories created by the UI. |",
        "| `data/manual_repos.json` | Manually added repositories outside the GitHub Lists sync. |",
        "| `data/review_queue.csv` | Low-confidence or uncategorized repositories to review. |",
        "",
        "A manual category row looks like this:",
        "",
        "```csv",
        "repo,category,labels,note",
        "owner/repo,primary-category-id,extra-label-a;extra-label-b,why this belongs here",
        "```",
        "",
        "After direct file edits, rerun:",
        "",
        "```powershell",
        "python scripts\\classify_repos.py",
        "python scripts\\build_readme.py",
        "```",
        "",
        "## Pipeline Reference",
        "",
        "- `sync_lists.py` refreshes your public GitHub Lists and repository membership.",
        "- `fetch_repo_metadata.py` fetches metadata for newly seen repositories and reuses the local cache for old ones.",
        "- `classify_repos.py` assigns each repository to a direct category and applies manual labels.",
        "- `build_readme.py` regenerates the README and category pages.",
        "- `data/review_queue.csv` lists repositories that need manual review or have low classification confidence.",
        "",
        "## Curation Notice",
        "",
        "The classification is semi-automatic and intended for personal research navigation. Some repositories may be missing, outdated, multi-topic, or placed in a category that is not the best fit. Treat the index as a curated starting point rather than an authoritative benchmark.",
        "",
        "Do not edit generated docs directly because they will be overwritten.",
        "",
        f"Current metadata fetch failures: `{failures}`. These can usually be retried later by rerunning `fetch_repo_metadata.py`.",
    ]
    return "\n".join(lines).strip() + "\n"


def build_fetch_failures(metadata: dict) -> str:
    failures = metadata.get("failures", {})
    lines = [
        "# Fetch Failures",
        "",
        "Repositories whose GitHub pages could not be fetched during the latest metadata sync.",
        "",
        f"Count: `{len(failures)}`",
        "",
    ]
    if not failures:
        lines.append("No failures.")
        return "\n".join(lines).strip() + "\n"

    for name, error in sorted(failures.items()):
        url_name = name.replace(" /", "/").replace("/ ", "/").replace(" ", "")
        safe_error = public_text(error) or "Fetch failed."
        lines.append(f"- [{url_name}](https://github.com/{url_name}) - {safe_error}")
    return "\n".join(lines).strip() + "\n"


def build_readme(payload: dict, metadata: dict) -> str:
    total_repos = payload["total_unique_repos"]
    fetched_ok = sum(1 for repo in metadata["repos"].values() if repo.get("fetched_ok"))
    failures = len(metadata.get("failures", {}))
    categories = category_entries(payload)
    uncategorized = payload["uncategorized_count"]
    star_badge = f"https://img.shields.io/badge/indexed%20repos-{total_repos}-1f6f5b"
    category_badge = f"https://img.shields.io/badge/categories-{len(categories)}-2f4858"
    review_badge = f"https://img.shields.io/badge/review%20queue-{uncategorized}-b84a2f"
    fetched_badge = f"https://img.shields.io/badge/fetched-{fetched_ok}-4f7f52"

    lines = [
        "# Robotics Star Atlas",
        "",
        "<p align=\"center\">",
        "  <strong>A curated atlas of GitHub repositories for SLAM, LiDAR, localization, mapping, perception, planning, and robotics research tooling.</strong>",
        "</p>",
        "",
        "<p align=\"center\">",
        f"  <img alt=\"Indexed repositories\" src=\"{star_badge}\">",
        f"  <img alt=\"Categories\" src=\"{category_badge}\">",
        f"  <img alt=\"Fetched repositories\" src=\"{fetched_badge}\">",
        f"  <img alt=\"Review queue\" src=\"{review_badge}\">",
        "</p>",
        "",
        "Robotics Star Atlas turns my GitHub stars into a searchable, manually curated research map. It is designed as a personal navigation system first, and as a public reference for researchers and engineers who work around robotics, 3D vision, and autonomous systems.",
        "",
        "## Quick Links",
        "",
        "| Link | Description |",
        "| --- | --- |",
        "| [Category Index](docs/category-index.md) | Compact category overview. |",
        "| [Update Guide](docs/update-guide.md) | How to add new stars, categories, and manual labels. |",
        "| [Fetch Failures](docs/fetch-failures.md) | Repositories that could not be fetched during the latest sync. |",
        "",
        "## Setup",
        "",
        "```powershell",
        "python -m pip install -r requirements.txt",
        "```",
        "",
        "The generated README and category pages can be browsed directly on GitHub. The local UI is only needed when you want to curate or rebuild the index.",
        "",
        "## Overview",
        "",
        "<table>",
        "  <tr>",
        f"    <td><strong>GitHub user</strong><br><code>@astronaunt</code></td>",
        f"    <td><strong>Indexed repositories</strong><br><code>{total_repos}</code></td>",
        f"    <td><strong>Categories</strong><br><code>{len(categories)}</code></td>",
        "  </tr>",
        "  <tr>",
        f"    <td><strong>Fetched successfully</strong><br><code>{fetched_ok}</code></td>",
        f"    <td><strong>Fetch failures</strong><br><code>{failures}</code></td>",
        f"    <td><strong>Needs review</strong><br><code>{uncategorized}</code></td>",
        "  </tr>",
        "</table>",
        "",
        "## Curation Notice",
        "",
        "This index is semi-automatic. Repository metadata, GitHub Lists, README snippets, and manual corrections are combined to assign categories and labels. Some repositories may be missing, outdated, multi-topic, or placed in a category that is not the best fit. Please treat this as a personal research map and a useful starting point, not as an authoritative benchmark or taxonomy.",
        "",
        "## Categories",
        "",
        "| Category | Repos | Description |",
        "| --- | ---: | --- |",
    ]
    for cat_id, info in categories:
        lines.append(
            f"| [{category_name(cat_id, info)}]({slug_path(cat_id)}) | {info['count']} | {category_description(info)} |"
        )

    lines.extend(
        [
            "",
            "## How To Update",
            "",
            "For day-to-day maintenance, use the visual local UI:",
            "",
            "```powershell",
            "python scripts\\review_server.py",
            "```",
            "",
            "Then open `http://127.0.0.1:8765`.",
            "",
            "| Scenario | Recommended action |",
            "| --- | --- |",
            "| You starred one new repository | Paste its GitHub URL into `Add Repo URL`, assign labels, then click `Rebuild README`. |",
            "| You created a new research direction | Use `Add Category`, then assign the category as primary or as an additional label. |",
            "| Many GitHub stars or Lists changed | Run the full refresh pipeline below. |",
            "| A category is wrong | Select the repository in the UI, change the primary category or additional labels, then save. |",
            "",
            "Full refresh pipeline:",
            "",
            "```powershell",
            "python scripts\\sync_lists.py",
            "python scripts\\fetch_repo_metadata.py",
            "python scripts\\classify_repos.py",
            "python scripts\\build_readme.py",
            "```",
            "",
            "See [Update Guide](docs/update-guide.md) for details.",
            "",
            "## Method",
            "",
            "- Classification uses repository name, About text, Topics, original list description, and a short README excerpt.",
            "- Original GitHub Lists are used as weak priors, especially for learning resources and domain-specific collections.",
            "- Manual corrections and multi-label assignments can be made with `python scripts\\review_server.py`, or by editing `data/manual_categories.csv` / `data/overrides.json`.",
            "- Repository rows intentionally omit internal classification evidence, so the public README stays clean.",
            "",
            "## Supporting Docs",
            "",
            "- [Category Index](docs/category-index.md)",
            "- [Fetch Failures](docs/fetch-failures.md)",
            "- [Update Guide](docs/update-guide.md)",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def clean_generated_docs() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    if CATEGORY_DIR.exists():
        shutil.rmtree(CATEGORY_DIR)
    CATEGORY_DIR.mkdir(parents=True, exist_ok=True)

    keep = {"category-index.md", "fetch-failures.md", "update-guide.md"}
    for path in DOCS_DIR.glob("*.md"):
        if path.name not in keep:
            path.unlink()


def main() -> None:
    payload = load_json(CLASSIFIED_PATH)
    metadata = load_json(METADATA_PATH)
    clean_generated_docs()

    README_PATH.write_text(build_readme(payload, metadata), encoding="utf-8")
    (DOCS_DIR / "category-index.md").write_text(build_category_index(payload), encoding="utf-8")
    (DOCS_DIR / "fetch-failures.md").write_text(build_fetch_failures(metadata), encoding="utf-8")
    (DOCS_DIR / "update-guide.md").write_text(build_update_guide(metadata), encoding="utf-8")

    for cat_id, info in category_entries(payload):
        (CATEGORY_DIR / f"{cat_id}.md").write_text(
            build_category_doc(cat_id, info, payload),
            encoding="utf-8",
        )

    print(f"Wrote {README_PATH}")
    print(f"Wrote {DOCS_DIR / 'category-index.md'}")
    print(f"Wrote {DOCS_DIR / 'update-guide.md'}")
    print(f"Wrote {CATEGORY_DIR}")


if __name__ == "__main__":
    main()
