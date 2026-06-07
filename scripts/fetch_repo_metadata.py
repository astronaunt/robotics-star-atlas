from __future__ import annotations

import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Dict, Iterable

import requests


ROOT = Path(__file__).resolve().parents[1]
LISTS_PATH = ROOT / "data" / "lists.json"
MANUAL_REPOS_PATH = ROOT / "data" / "manual_repos.json"
OUTPUT_PATH = ROOT / "data" / "repo_metadata.json"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0 Safari/537.36"
)


@dataclass(frozen=True)
class RepoSeed:
    full_name: str
    url: str
    repo: str
    owner: str
    description: str
    stars_label: str
    language: str
    source_lists: tuple[str, ...]


def load_unique_repo_seeds() -> list[RepoSeed]:
    payload = json.loads(LISTS_PATH.read_text(encoding="utf-8"))
    repo_map: Dict[str, dict] = {}
    for list_item in payload["lists"]:
        slug = list_item["slug"]
        for repo in list_item["repositories"]:
            key = repo["full_name"]
            record = repo_map.setdefault(
                key,
                {
                    **repo,
                    "source_lists": set(),
                },
            )
            record["source_lists"].add(slug)

    if MANUAL_REPOS_PATH.exists():
        manual_payload = json.loads(MANUAL_REPOS_PATH.read_text(encoding="utf-8"))
        for item in manual_payload.get("repos", []):
            full_name = item.get("full_name", "")
            if "/" not in full_name:
                continue
            owner, repo_name = full_name.split("/", 1)
            record = repo_map.setdefault(
                f"{owner} /{repo_name}",
                {
                    "owner": owner,
                    "repo": repo_name,
                    "full_name": f"{owner} /{repo_name}",
                    "url": f"https://github.com/{owner}/{repo_name}",
                    "description": item.get("description", ""),
                    "stars_label": "",
                    "language": "",
                    "source_lists": set(),
                },
            )
            record["source_lists"].add("manual")

    seeds = []
    for key, record in sorted(repo_map.items()):
        seeds.append(
            RepoSeed(
                full_name=key,
                url=record["url"],
                repo=record["repo"],
                owner=record["owner"],
                description=record.get("description", ""),
                stars_label=record.get("stars_label", ""),
                language=record.get("language", ""),
                source_lists=tuple(sorted(record["source_lists"])),
            )
        )
    return seeds


def clean_text(raw: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", raw, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(" ".join(text.split()))


def extract_topics(html: str) -> list[str]:
    topics = re.findall(
        r'class="topic-tag topic-tag-link"[^>]*>\s*([^<]+?)\s*</a>',
        html,
        re.S,
    )
    return sorted({clean_text(topic).lower() for topic in topics if topic.strip()})


def extract_about(html: str) -> str:
    about_match = re.search(
        r'<h2 class="tmp-mb-3 h4">About</h2>.*?<p class="f4 tmp-my-3">\s*(.*?)\s*</p>',
        html,
        re.S,
    )
    if about_match:
        return clean_text(about_match.group(1))
    meta_match = re.search(r'<meta name="description" content="(.*?)">', html, re.S)
    return clean_text(meta_match.group(1)) if meta_match else ""


def extract_readme_excerpt(html: str, limit: int = 2800) -> str:
    readme_match = re.search(
        r'<article class="markdown-body entry-content container-lg"[^>]*>(.*?)</article>',
        html,
        re.S,
    )
    if not readme_match:
        return ""
    text = clean_text(readme_match.group(1))
    return text[:limit]


def extract_homepage(html: str) -> str:
    match = re.search(
        r'href="(https?://[^"]+)"[^>]*rel="nofollow"',
        html,
        re.S,
    )
    return match.group(1) if match else ""


def parse_repo_page(seed: RepoSeed, session: requests.Session) -> dict:
    response = session.get(seed.url, timeout=30)
    response.raise_for_status()
    html = response.text

    archived = "This repository was archived by the owner" in html
    about = extract_about(html)
    topics = extract_topics(html)
    readme_excerpt = extract_readme_excerpt(html)

    return {
        "full_name": seed.full_name,
        "url": seed.url,
        "owner": seed.owner,
        "repo": seed.repo,
        "list_description": seed.description,
        "list_stars_label": seed.stars_label,
        "list_language": seed.language,
        "source_lists": list(seed.source_lists),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "archived": archived,
        "about": about,
        "topics": topics,
        "homepage": extract_homepage(html),
        "readme_excerpt": readme_excerpt,
    }


def fetch_with_retry(seed: RepoSeed, session: requests.Session) -> dict:
    last_error: Exception | None = None
    for attempt in range(1, 5):
        try:
            return parse_repo_page(seed, session)
        except Exception as exc:
            last_error = exc
            time.sleep(1.0 * attempt)
    raise RuntimeError(f"Failed to fetch metadata for {seed.full_name}") from last_error


def load_cache() -> dict:
    if not OUTPUT_PATH.exists():
        return {}
    return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))


def save_cache(cache: dict) -> None:
    OUTPUT_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def pending_repos(seeds: Iterable[RepoSeed], cache: dict) -> list[RepoSeed]:
    existing = cache.get("repos", {})
    pending = []
    for seed in seeds:
        record = existing.get(seed.full_name)
        if record and record.get("fetched_ok"):
            continue
        pending.append(seed)
    return pending


def worker(seed: RepoSeed) -> dict:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return fetch_with_retry(seed, session)


def main() -> None:
    seeds = load_unique_repo_seeds()
    cache = load_cache()
    repo_records = cache.get("repos", {})
    failures = cache.get("failures", {})
    todo = pending_repos(seeds, cache)

    save_lock = threading.Lock()
    completed = 0
    total = len(todo)

    cache.update(
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_unique_repos": len(seeds),
            "repos": repo_records,
            "failures": failures,
        }
    )
    save_cache(cache)

    if not todo:
        print(f"All {len(seeds)} repositories already have metadata.")
        return

    print(f"Fetching metadata for {total} repositories...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(worker, seed): seed for seed in todo}
        for index, future in enumerate(as_completed(futures), start=1):
            seed = futures[future]
            with save_lock:
                completed += 1
                try:
                    result = future.result()
                    result["fetched_ok"] = True
                    repo_records[seed.full_name] = result
                    failures.pop(seed.full_name, None)
                except Exception as exc:
                    repo_records.setdefault(seed.full_name, {})
                    repo_records[seed.full_name].update(
                        {
                            "full_name": seed.full_name,
                            "url": seed.url,
                            "owner": seed.owner,
                            "repo": seed.repo,
                            "list_description": seed.description,
                            "list_stars_label": seed.stars_label,
                            "list_language": seed.language,
                            "source_lists": list(seed.source_lists),
                            "fetched_at": datetime.now(timezone.utc).isoformat(),
                            "fetched_ok": False,
                            "fetch_error": str(exc),
                        }
                    )
                    failures[seed.full_name] = str(exc)
                if completed % 25 == 0 or completed == total:
                    cache["generated_at"] = datetime.now(timezone.utc).isoformat()
                    save_cache(cache)
                    print(f"Saved {completed}/{total}")

    cache["generated_at"] = datetime.now(timezone.utc).isoformat()
    save_cache(cache)
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Failures: {len(failures)}")


if __name__ == "__main__":
    main()
