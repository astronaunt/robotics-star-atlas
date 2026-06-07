from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Dict, Iterable, List
from urllib.parse import urljoin
from urllib.request import Request, urlopen

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "data" / "taxonomy.json"
OUTPUT_PATH = ROOT / "data" / "lists.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0 Safari/537.36"
)
BASE_URL = "https://github.com"
PROFILE_URL_TEMPLATE = "https://github.com/{user}?tab=stars"
LIST_URL_TEMPLATE = "https://github.com/stars/{user}/lists/{slug}"
CARD_MARKER = '<div class="col-12 d-block width-full tmp-py-4 border-bottom color-border-muted"'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_text(url: str) -> str:
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            if requests is not None:
                response = requests.get(
                    url,
                    timeout=30,
                    headers={"User-Agent": USER_AGENT},
                )
                response.raise_for_status()
                return response.text

            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except Exception as exc:  # pragma: no cover
            last_error = exc
            time.sleep(1.2 * attempt)
    raise RuntimeError(f"Failed to fetch {url}") from last_error


def clean_html_text(raw: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", raw)
    return unescape(" ".join(without_tags.split()))


def parse_count_label(raw: str) -> int | None:
    if raw is None:
        return None
    text = raw.strip().lower().replace(",", "")
    if not text:
        return None
    multiplier = 1
    if text.endswith("k"):
        multiplier = 1000
        text = text[:-1]
    elif text.endswith("m"):
        multiplier = 1_000_000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return None


def extract_profile_lists(profile_html: str, user: str) -> Dict[str, dict]:
    pattern = re.compile(
        rf'<a[^>]+href="(/stars/{re.escape(user)}/lists/[^"]+)"[^>]*>(.*?)</a>',
        re.S,
    )
    lists: Dict[str, dict] = {}
    for href, inner_html in pattern.findall(profile_html):
        slug = href.rsplit("/", 1)[-1]
        text = clean_html_text(inner_html)
        if slug in lists:
            continue
        name = re.sub(r"\s+\d+\s+repositories?$", "", text).strip()
        count_match = re.search(r"(\d+)\s+repositories?$", text)
        lists[slug] = {
            "slug": slug,
            "href": href,
            "name": name,
            "profile_count": int(count_match.group(1)) if count_match else None,
        }
    return lists


def extract_profile_summary(profile_html: str, user: str) -> dict:
    stars_match = None
    tab_block_match = re.search(
        rf'<a[^>]+href="/{re.escape(user)}\?tab=stars"[^>]*>(.*?)</a>',
        profile_html,
        re.S,
    )
    if tab_block_match:
        stars_match = re.search(
            r'<span[^>]*class="Counter"[^>]*>(.*?)</span>',
            tab_block_match.group(1),
            re.S,
        )
    lists_match = re.search(r"Lists\s*\((\d+)\)", profile_html)
    return {
        "stars_label": clean_html_text(stars_match.group(1)) if stars_match else None,
        "lists_count": int(lists_match.group(1)) if lists_match else None,
    }


def iter_repo_chunks(html: str) -> Iterable[str]:
    starts = [match.start() for match in re.finditer(re.escape(CARD_MARKER), html)]
    if not starts:
        return
    page_end = html.find('<div class="paginate-container"', starts[0])
    if page_end == -1:
        page_end = html.find('<div class="Subhead Subhead--spacious"', starts[0])
    if page_end == -1:
        page_end = len(html)
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else page_end
        yield html[start:end]


def parse_repo_chunk(chunk: str) -> dict | None:
    link_match = re.search(
        r'<h2 class="h3">\s*<a href="(/[^"/]+/[^"/]+)">\s*'
        r'<span class="text-normal">\s*([^<]+?)\s*</span>\s*([^<]+?)\s*</a>',
        chunk,
        re.S,
    )
    if not link_match:
        return None

    path = link_match.group(1)
    owner = clean_html_text(link_match.group(2)).rstrip("/")
    repo = clean_html_text(link_match.group(3))

    desc_match = re.search(r'itemprop="description">\s*(.*?)\s*</p>', chunk, re.S)
    language_match = re.search(r'itemprop="programmingLanguage">\s*(.*?)\s*</span>', chunk, re.S)
    stars_match = re.search(
        rf'href="{re.escape(path)}/stargazers">.*?</svg>\s*([^<]+?)\s*</a>',
        chunk,
        re.S,
    )

    return {
        "owner": owner,
        "repo": repo,
        "full_name": f"{owner}/{repo}",
        "path": path,
        "url": urljoin(BASE_URL, path),
        "description": clean_html_text(desc_match.group(1)) if desc_match else "",
        "language": clean_html_text(language_match.group(1)) if language_match else "",
        "stars_label": clean_html_text(stars_match.group(1)) if stars_match else "",
        "stars": parse_count_label(clean_html_text(stars_match.group(1))) if stars_match else None,
    }


def find_page_count(html: str, user: str, slug: str) -> int:
    matches = re.findall(
        rf'/stars/{re.escape(user)}/lists/{re.escape(slug)}\?page=(\d+)',
        html,
    )
    pages = [int(page) for page in matches]
    return max(pages) if pages else 1


def fetch_list_repositories(user: str, slug: str) -> dict:
    first_page_url = LIST_URL_TEMPLATE.format(user=user, slug=slug)
    first_html = fetch_text(first_page_url)
    page_count = find_page_count(first_html, user, slug)

    repositories: List[dict] = []
    seen: set[str] = set()
    pages_fetched = []

    for page in range(1, page_count + 1):
        url = first_page_url if page == 1 else f"{first_page_url}?page={page}"
        html = first_html if page == 1 else fetch_text(url)
        pages_fetched.append(url)
        found_any = False
        for chunk in iter_repo_chunks(html):
            repo = parse_repo_chunk(chunk)
            if not repo:
                continue
            found_any = True
            if repo["full_name"] in seen:
                continue
            seen.add(repo["full_name"])
            repositories.append(repo)
        if not found_any:
            break
        time.sleep(0.15)

    return {
        "slug": slug,
        "source_url": first_page_url,
        "pages_fetched": pages_fetched,
        "page_count": len(pages_fetched),
        "repo_count": len(repositories),
        "repositories": repositories,
    }


def configured_slugs(taxonomy: dict) -> List[str]:
    slugs: List[str] = []
    for section in taxonomy["sections"]:
        for item in section["lists"]:
            slugs.append(item["slug"])
    return slugs


def main() -> None:
    taxonomy = load_json(TAXONOMY_PATH)
    user = taxonomy["github_user"]

    profile_html = fetch_text(PROFILE_URL_TEMPLATE.format(user=user))
    public_lists = extract_profile_lists(profile_html, user)
    profile_summary = extract_profile_summary(profile_html, user)

    configured = configured_slugs(taxonomy)
    results = []
    for slug in configured:
        list_data = fetch_list_repositories(user, slug)
        list_data.update(public_lists.get(slug, {}))
        results.append(list_data)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "github_user": user,
        "profile": profile_summary,
        "configured_slugs": configured,
        "public_lists_seen": sorted(public_lists),
        "missing_from_profile": [slug for slug in configured if slug not in public_lists],
        "unconfigured_public_lists": [slug for slug in sorted(public_lists) if slug not in configured],
        "lists": results,
    }
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Fetched {len(results)} configured lists for @{user}.")


if __name__ == "__main__":
    main()
