from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from fetch_repo_metadata import RepoSeed, load_cache, save_cache, worker


ROOT = Path(__file__).resolve().parents[1]
CLASSIFIED_PATH = ROOT / "data" / "classified_repos.json"
MANUAL_CSV_PATH = ROOT / "data" / "manual_categories.csv"
REVIEW_QUEUE_PATH = ROOT / "data" / "review_queue.csv"
CUSTOM_CATEGORIES_PATH = ROOT / "data" / "custom_categories.json"
MANUAL_REPOS_PATH = ROOT / "data" / "manual_repos.json"

HOST = "127.0.0.1"
PORT = 8765


HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Robotics Star Atlas Review</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f7f3;
      --ink: #20231f;
      --muted: #686d62;
      --line: #d8d8cd;
      --panel: #fffffb;
      --accent: #1f6f5b;
      --accent-2: #b84a2f;
      --soft: #edf3ea;
      --warn: #fff4d6;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.5 ui-sans-serif, "Segoe UI", "Noto Sans SC", "Microsoft YaHei", sans-serif;
    }
    header {
      position: sticky;
      top: 0;
      z-index: 5;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 16px;
      align-items: center;
      padding: 14px 20px;
      border-bottom: 1px solid var(--line);
      background: rgba(247, 247, 243, 0.94);
      backdrop-filter: blur(10px);
    }
    h1 {
      margin: 0;
      font-size: 18px;
      font-weight: 720;
      letter-spacing: 0;
    }
    .sub { color: var(--muted); font-size: 12px; }
    .shell {
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr) 360px;
      min-height: calc(100vh - 66px);
    }
    aside, main, .editor {
      min-width: 0;
      padding: 18px;
    }
    aside {
      border-right: 1px solid var(--line);
      background: #fbfbf6;
    }
    .editor {
      border-left: 1px solid var(--line);
      background: #fbfbf6;
    }
    .toolbar {
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 10px;
      margin-bottom: 14px;
    }
    input, select, textarea, button {
      font: inherit;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
    }
    input, select, textarea {
      width: 100%;
      padding: 9px 10px;
    }
    textarea {
      min-height: 92px;
      resize: vertical;
    }
    button {
      padding: 9px 12px;
      cursor: pointer;
      font-weight: 650;
    }
    button.primary {
      border-color: var(--accent);
      background: var(--accent);
      color: #fff;
    }
    button.ghost {
      background: transparent;
    }
    button:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
    .category-list {
      display: grid;
      gap: 6px;
      margin-top: 12px;
    }
    .side-tools {
      margin-top: 18px;
      padding-top: 16px;
      border-top: 1px solid var(--line);
      display: grid;
      gap: 8px;
    }
    .side-tools h3 {
      margin: 8px 0 0;
      font-size: 13px;
    }
    .side-tools textarea {
      min-height: 70px;
    }
    .category-button {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
      align-items: center;
      width: 100%;
      text-align: left;
      background: transparent;
      border-color: transparent;
      padding: 8px 9px;
    }
    .category-button.active {
      background: var(--soft);
      border-color: #c9d8c3;
    }
    .count {
      color: var(--muted);
      font-size: 12px;
    }
    .repo-list {
      display: grid;
      gap: 8px;
    }
    .repo-card {
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      cursor: pointer;
    }
    .repo-card.active {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(31, 111, 91, 0.13);
    }
    .repo-card.review {
      background: var(--warn);
    }
    .repo-title {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      font-weight: 720;
    }
    .repo-desc {
      margin-top: 5px;
      color: var(--muted);
      font-size: 13px;
    }
    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }
    .pill {
      padding: 2px 7px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--muted);
      background: #fff;
      font-size: 12px;
    }
    .pill.primary-pill {
      border-color: #b8d3ca;
      color: #174f43;
      background: #eaf4f0;
      font-weight: 680;
    }
    .label-grid {
      display: grid;
      gap: 6px;
      max-height: 280px;
      overflow: auto;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
    }
    .check-row {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 8px;
      align-items: start;
      padding: 6px;
      border-radius: 5px;
    }
    .check-row:hover {
      background: var(--soft);
    }
    .check-row input {
      width: auto;
      margin-top: 3px;
    }
    .check-name {
      font-weight: 660;
    }
    .editor h2 {
      margin: 0 0 6px;
      font-size: 18px;
    }
    .field {
      display: grid;
      gap: 6px;
      margin: 14px 0;
    }
    label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 680;
    }
    .status {
      margin-top: 12px;
      color: var(--muted);
      min-height: 20px;
    }
    .danger { color: var(--accent-2); }
    .meta {
      color: var(--muted);
      font-size: 12px;
      margin-top: 8px;
    }
    .empty {
      padding: 24px;
      border: 1px dashed var(--line);
      border-radius: 8px;
      color: var(--muted);
      text-align: center;
    }
    @media (max-width: 1050px) {
      .shell { grid-template-columns: 230px minmax(0, 1fr); }
      .editor {
        grid-column: 1 / -1;
        border-left: 0;
        border-top: 1px solid var(--line);
      }
    }
    @media (max-width: 760px) {
      header, .shell, .toolbar { display: block; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
      .toolbar > * { margin-bottom: 8px; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Robotics Star Atlas Review</h1>
      <div class="sub" id="summary">Loading...</div>
    </div>
    <button id="rebuildButton" class="primary">Rebuild README</button>
  </header>

  <div class="shell">
    <aside>
      <input id="categorySearch" placeholder="Search categories" />
      <div class="category-list" id="categoryList"></div>
      <div class="side-tools">
        <h3>Add Category</h3>
        <input id="newCategoryName" placeholder="English name, e.g. SLAM System" />
        <input id="newCategoryZh" placeholder="中文名，可选" />
        <input id="newCategoryKeywords" placeholder="keywords, comma separated" />
        <textarea id="newCategoryDescription" placeholder="Description, optional"></textarea>
        <button id="addCategoryButton" class="primary">Add Category</button>
        <div class="status" id="categoryStatus"></div>
        <h3>Add Repo URL</h3>
        <input id="newRepoUrl" placeholder="https://github.com/owner/repo" />
        <button id="addRepoButton" class="primary">Add Repo</button>
        <div class="status" id="repoStatus"></div>
      </div>
    </aside>

    <main>
      <div class="toolbar">
        <input id="repoSearch" placeholder="Search repo, description, category" />
        <select id="reviewFilter">
          <option value="all">All repos</option>
          <option value="review">Review queue</option>
          <option value="manual">Only manual edits</option>
        </select>
        <button id="clearButton" class="ghost">Clear</button>
      </div>
      <div class="repo-list" id="repoList"></div>
    </main>

    <section class="editor">
      <div id="editorEmpty" class="empty">Select a repository to edit its category.</div>
      <div id="editorPanel" hidden>
        <h2 id="repoName"></h2>
        <a id="repoLink" target="_blank" rel="noreferrer">Open on GitHub</a>
        <div class="meta" id="repoMeta"></div>
        <p class="repo-desc" id="repoDescription"></p>

        <div class="field">
          <label for="categorySelect">Primary Category</label>
          <select id="categorySelect"></select>
        </div>
        <div class="field">
          <label>Additional Labels</label>
          <div class="label-grid" id="labelsList"></div>
        </div>
        <div class="field">
          <label for="noteInput">Note</label>
          <textarea id="noteInput" placeholder="Optional reason for this correction"></textarea>
        </div>
        <button id="saveButton" class="primary">Save Labels</button>
        <div class="status" id="saveStatus"></div>
      </div>
    </section>
  </div>

  <script>
    let state = null;
    let selectedCategory = "all";
    let selectedRepo = null;

    const el = (id) => document.getElementById(id);

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Request failed");
      return data;
    }

    function normalize(text) {
      return (text || "").toLowerCase();
    }

    function categories() {
      return Object.entries(state.categories)
        .map(([id, info]) => ({ id, ...info }));
    }

    function repoArray() {
      return Object.values(state.repos);
    }

    function isManual(repo) {
      return Boolean(state.manual[repo.display_name]);
    }

    function isReview(repo) {
      return state.review.includes(repo.display_name);
    }

    function renderSummary() {
      const reviewCount = state.review.length;
      el("summary").textContent =
        `${state.total_unique_repos} repos · ${categories().length} categories · ${reviewCount} review items`;
    }

    function renderCategories() {
      const query = normalize(el("categorySearch").value);
      const list = el("categoryList");
      list.innerHTML = "";

      const all = document.createElement("button");
      all.className = "category-button" + (selectedCategory === "all" ? " active" : "");
      all.innerHTML = `<span>All Categories</span><span class="count">${repoArray().length}</span>`;
      all.onclick = () => { selectedCategory = "all"; render(); };
      list.appendChild(all);

      for (const cat of categories()) {
        if (query && !normalize(cat.name + " " + cat.name_zh).includes(query)) continue;
        const button = document.createElement("button");
        button.className = "category-button" + (selectedCategory === cat.id ? " active" : "");
        button.innerHTML = `<span>${cat.name}<br><span class="count">${cat.name_zh}</span></span><span class="count">${cat.count}</span>`;
        button.onclick = () => { selectedCategory = cat.id; render(); };
        list.appendChild(button);
      }
    }

    function filteredRepos() {
      const query = normalize(el("repoSearch").value);
      const filter = el("reviewFilter").value;
      return repoArray().filter((repo) => {
        if (selectedCategory !== "all" && !(repo.labels || []).includes(selectedCategory)) return false;
        if (filter === "review" && !isReview(repo)) return false;
        if (filter === "manual" && !isManual(repo)) return false;
        if (!query) return true;
        const blob = normalize([
          repo.display_name,
          repo.display_description,
          repo.primary_category_name,
          repo.primary_category_name_zh,
          repo.primary_subtopic,
          (repo.labels || []).map((id) => state.categories[id]?.name || id).join(" "),
        ].join(" "));
        return blob.includes(query);
      });
    }

    function renderRepos() {
      const list = el("repoList");
      const repos = filteredRepos();
      list.innerHTML = "";
      if (!repos.length) {
        list.innerHTML = `<div class="empty">No repositories match the current filters.</div>`;
        return;
      }
      for (const repo of repos) {
        const card = document.createElement("article");
        card.className = "repo-card" +
          (selectedRepo && selectedRepo.display_name === repo.display_name ? " active" : "") +
          (isReview(repo) ? " review" : "");
        const desc = repo.display_description ? `<div class="repo-desc">${repo.display_description}</div>` : "";
        const manual = isManual(repo) ? `<span class="pill">manual</span>` : "";
        const review = isReview(repo) ? `<span class="pill">review</span>` : "";
        const subtopic = repo.primary_subtopic ? `<span class="pill">${repo.primary_subtopic}</span>` : "";
        const labelPills = (repo.labels || [])
          .filter((id) => id !== repo.primary_category)
          .slice(0, 4)
          .map((id) => `<span class="pill">${state.categories[id]?.name || id}</span>`)
          .join("");
        card.innerHTML = `
          <div class="repo-title"><span>${repo.display_name}</span><span class="count">${repo.primary_score}</span></div>
          ${desc}
          <div class="pill-row">
            <span class="pill primary-pill">${repo.primary_category_name}</span>
            ${labelPills}${subtopic}${manual}${review}
          </div>
        `;
        card.onclick = () => { selectedRepo = repo; renderEditor(); renderRepos(); };
        list.appendChild(card);
      }
    }

    function renderEditor() {
      if (!selectedRepo) {
        el("editorEmpty").hidden = false;
        el("editorPanel").hidden = true;
        return;
      }
      el("editorEmpty").hidden = true;
      el("editorPanel").hidden = false;
      el("repoName").textContent = selectedRepo.display_name;
      el("repoLink").href = selectedRepo.url;
      el("repoDescription").textContent = selectedRepo.display_description || "";
      el("repoMeta").textContent = `Current: ${selectedRepo.primary_category_name} · score ${selectedRepo.primary_score}`;

      const select = el("categorySelect");
      select.innerHTML = "";
      for (const cat of categories()) {
        const option = document.createElement("option");
        option.value = cat.id;
        option.textContent = `${cat.name} / ${cat.name_zh}`;
        if (cat.id === selectedRepo.primary_category) option.selected = true;
        select.appendChild(option);
      }
      const manual = state.manual[selectedRepo.display_name];
      el("noteInput").value = manual ? manual.note || "" : "";
      renderLabelChecks();
      el("saveStatus").textContent = "";
    }

    function renderLabelChecks() {
      const labels = new Set(selectedRepo.labels || []);
      const primary = el("categorySelect").value;
      const list = el("labelsList");
      list.innerHTML = "";
      for (const cat of categories()) {
        if (cat.id === primary) continue;
        const row = document.createElement("label");
        row.className = "check-row";
        const checked = labels.has(cat.id) ? "checked" : "";
        row.innerHTML = `
          <input type="checkbox" value="${cat.id}" ${checked} />
          <span><span class="check-name">${cat.name}</span><br><span class="count">${cat.name_zh}</span></span>
        `;
        list.appendChild(row);
      }
    }

    function selectedLabels() {
      return [...el("labelsList").querySelectorAll("input:checked")].map((input) => input.value);
    }

    function render() {
      renderSummary();
      renderCategories();
      renderRepos();
      renderEditor();
    }

    async function loadState() {
      state = await api("/api/state");
      selectedRepo = null;
      render();
    }

    async function saveManual() {
      if (!selectedRepo) return;
      const selectedName = selectedRepo.display_name;
      el("saveButton").disabled = true;
      el("saveStatus").textContent = "Saving...";
      try {
        await api("/api/manual", {
          method: "POST",
          body: JSON.stringify({
            repo: selectedRepo.display_name,
            category: el("categorySelect").value,
            labels: selectedLabels(),
            note: el("noteInput").value,
          }),
        });
        await loadState();
        selectedRepo = repoArray().find((repo) => repo.display_name === selectedName) || null;
        render();
        el("saveStatus").textContent = "Saved.";
      } catch (error) {
        el("saveStatus").innerHTML = `<span class="danger">${error.message}</span>`;
      } finally {
        el("saveButton").disabled = false;
      }
    }

    async function rebuild() {
      el("rebuildButton").disabled = true;
      el("rebuildButton").textContent = "Rebuilding...";
      try {
        await api("/api/rebuild", { method: "POST", body: "{}" });
        await loadState();
        el("rebuildButton").textContent = "Rebuilt";
        setTimeout(() => el("rebuildButton").textContent = "Rebuild README", 1400);
      } catch (error) {
        alert(error.message);
        el("rebuildButton").textContent = "Rebuild README";
      } finally {
        el("rebuildButton").disabled = false;
      }
    }

    async function addCategory() {
      el("addCategoryButton").disabled = true;
      el("categoryStatus").textContent = "Adding...";
      try {
        await api("/api/category", {
          method: "POST",
          body: JSON.stringify({
            name: el("newCategoryName").value,
            name_zh: el("newCategoryZh").value,
            keywords: el("newCategoryKeywords").value,
            description: el("newCategoryDescription").value,
          }),
        });
        el("newCategoryName").value = "";
        el("newCategoryZh").value = "";
        el("newCategoryKeywords").value = "";
        el("newCategoryDescription").value = "";
        await loadState();
        el("categoryStatus").textContent = "Category added.";
      } catch (error) {
        el("categoryStatus").innerHTML = `<span class="danger">${error.message}</span>`;
      } finally {
        el("addCategoryButton").disabled = false;
      }
    }

    async function addRepo() {
      el("addRepoButton").disabled = true;
      el("repoStatus").textContent = "Fetching repo...";
      try {
        const result = await api("/api/repo", {
          method: "POST",
          body: JSON.stringify({ url: el("newRepoUrl").value }),
        });
        el("newRepoUrl").value = "";
        await loadState();
        selectedRepo = repoArray().find((repo) => repo.display_name === result.repo) || null;
        render();
        el("repoStatus").textContent = `Added ${result.repo}.`;
      } catch (error) {
        el("repoStatus").innerHTML = `<span class="danger">${error.message}</span>`;
      } finally {
        el("addRepoButton").disabled = false;
      }
    }

    el("categorySearch").addEventListener("input", renderCategories);
    el("repoSearch").addEventListener("input", renderRepos);
    el("reviewFilter").addEventListener("change", renderRepos);
    el("clearButton").onclick = () => {
      selectedCategory = "all";
      el("repoSearch").value = "";
      el("reviewFilter").value = "all";
      render();
    };
    el("saveButton").onclick = saveManual;
    el("rebuildButton").onclick = rebuild;
    el("categorySelect").addEventListener("change", renderLabelChecks);
    el("addCategoryButton").onclick = addCategory;
    el("addRepoButton").onclick = addRepo;

    loadState().catch((error) => {
      document.body.innerHTML = `<pre>${error.stack || error.message}</pre>`;
    });
  </script>
</body>
</html>
"""


def normalized_repo_name(name: str) -> str:
    return name.replace(" /", "/").replace("/ ", "/").replace(" ", "")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_manual_rows() -> list[dict]:
    if not MANUAL_CSV_PATH.exists():
        return []
    with MANUAL_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_manual_rows(rows: list[dict]) -> None:
    MANUAL_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANUAL_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["repo", "category", "labels", "note"])
        writer.writeheader()
        writer.writerows(rows)


def manual_map() -> dict:
    result = {}
    for row in read_manual_rows():
        repo = normalized_repo_name(row.get("repo", ""))
        if repo:
            result[repo] = {
                "category": row.get("category", ""),
                "labels": [item.strip() for item in (row.get("labels") or "").split(";") if item.strip()],
                "note": row.get("note", ""),
            }
    return result


def review_set() -> set[str]:
    if not REVIEW_QUEUE_PATH.exists():
        return set()
    with REVIEW_QUEUE_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return {normalized_repo_name(row.get("repo", "")) for row in csv.DictReader(handle)}


def slugify_category(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "custom-category"


def read_custom_categories() -> dict:
    if not CUSTOM_CATEGORIES_PATH.exists():
        return {"categories": []}
    payload = json.loads(CUSTOM_CATEGORIES_PATH.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {"categories": payload}
    payload.setdefault("categories", [])
    return payload


def write_custom_categories(payload: dict) -> None:
    CUSTOM_CATEGORIES_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def upsert_custom_category(name: str, name_zh: str, keywords: str, description: str) -> str:
    if not name.strip():
        raise ValueError("Category name is required")
    payload = read_custom_categories()
    cat_id = slugify_category(name)
    keyword_map = {
        keyword.strip().lower(): 12
        for keyword in keywords.split(",")
        if keyword.strip()
    }
    item = {
        "id": cat_id,
        "name": name.strip(),
        "name_zh": name_zh.strip() or name.strip(),
        "description": description.strip() or "Custom user-defined category.",
        "kind": "custom",
        "keywords": keyword_map,
        "lists": {},
    }
    categories = [cat for cat in payload["categories"] if cat.get("id") != cat_id]
    categories.append(item)
    categories.sort(key=lambda cat: cat.get("id", ""))
    payload["categories"] = categories
    write_custom_categories(payload)
    return cat_id


def parse_github_repo(value: str) -> tuple[str, str]:
    value = value.strip()
    if not value:
        raise ValueError("Repository URL is required")
    match = re.search(r"github\.com[:/]+([^/\s]+)/([^/#?\s]+)", value)
    if not match and re.match(r"^[^/\s]+/[^/\s]+$", value):
        owner, repo = value.split("/", 1)
        return owner, repo.removesuffix(".git")
    if not match:
        raise ValueError("Use a GitHub URL like https://github.com/owner/repo")
    owner, repo = match.group(1), match.group(2)
    return owner, repo.removesuffix(".git")


def read_manual_repos() -> dict:
    if not MANUAL_REPOS_PATH.exists():
        return {"repos": []}
    payload = json.loads(MANUAL_REPOS_PATH.read_text(encoding="utf-8"))
    payload.setdefault("repos", [])
    return payload


def write_manual_repos(payload: dict) -> None:
    MANUAL_REPOS_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_manual_repo(value: str) -> str:
    owner, repo_name = parse_github_repo(value)
    full_name = f"{owner}/{repo_name}"
    payload = read_manual_repos()
    existing = {item.get("full_name") for item in payload["repos"]}
    if full_name not in existing:
        payload["repos"].append(
            {
                "full_name": full_name,
                "url": f"https://github.com/{full_name}",
                "added_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        payload["repos"].sort(key=lambda item: item["full_name"].lower())
        write_manual_repos(payload)

    seed = RepoSeed(
        full_name=f"{owner} /{repo_name}",
        url=f"https://github.com/{full_name}",
        owner=owner,
        repo=repo_name,
        description="",
        stars_label="",
        language="",
        source_lists=("manual",),
    )
    cache = load_cache()
    cache.setdefault("repos", {})
    cache.setdefault("failures", {})
    result = worker(seed)
    result["fetched_ok"] = True
    cache["repos"][seed.full_name] = result
    cache["failures"].pop(seed.full_name, None)
    cache["generated_at"] = datetime.now(timezone.utc).isoformat()
    cache["total_unique_repos"] = len(cache["repos"])
    save_cache(cache)
    return full_name


def state_payload() -> dict:
    data = load_json(CLASSIFIED_PATH)
    review = sorted(review_set())
    manual = manual_map()
    repos = {}
    for key, repo in data["repos"].items():
        display = repo.get("display_name") or normalized_repo_name(key)
        repos[display] = {
            **repo,
            "display_name": display,
            "display_description": repo.get("display_description", ""),
        }
    return {
        "total_unique_repos": data["total_unique_repos"],
        "categories": data["categories"],
        "repos": repos,
        "review": review,
        "manual": manual,
    }


def upsert_manual(repo: str, category: str, labels: list[str], note: str) -> None:
    repo = normalized_repo_name(repo)
    labels_text = ";".join(label for label in labels if label and label != category)
    rows = read_manual_rows()
    found = False
    for row in rows:
        if normalized_repo_name(row.get("repo", "")) == repo:
            row["repo"] = repo
            row["category"] = category
            row["labels"] = labels_text
            row["note"] = note
            found = True
            break
    if not found:
        rows.append({"repo": repo, "category": category, "labels": labels_text, "note": note})
    rows = [row for row in rows if row.get("repo") and row.get("category")]
    for row in rows:
        row.setdefault("labels", "")
        row.setdefault("note", "")
    rows.sort(key=lambda item: item["repo"].lower())
    write_manual_rows(rows)


class ReviewHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body or "{}")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/state":
            self.send_json(state_payload())
            return
        self.send_json({"error": "Not found"}, 404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/manual":
                payload = self.read_json()
                repo = payload.get("repo", "")
                category = payload.get("category", "")
                labels = payload.get("labels", [])
                note = payload.get("note", "")
                categories = state_payload()["categories"]
                if not isinstance(labels, list):
                    self.send_json({"error": "Labels must be a list"}, 400)
                    return
                labels = [label for label in labels if label in categories]
                if not repo or category not in categories:
                    self.send_json({"error": "Invalid repo or category"}, 400)
                    return
                upsert_manual(repo, category, labels, note)
                subprocess.run([sys.executable, "scripts/classify_repos.py"], cwd=ROOT, check=True)
                self.send_json({"ok": True})
                return
            if path == "/api/category":
                payload = self.read_json()
                cat_id = upsert_custom_category(
                    payload.get("name", ""),
                    payload.get("name_zh", ""),
                    payload.get("keywords", ""),
                    payload.get("description", ""),
                )
                subprocess.run([sys.executable, "scripts/classify_repos.py"], cwd=ROOT, check=True)
                self.send_json({"ok": True, "category": cat_id})
                return
            if path == "/api/repo":
                payload = self.read_json()
                repo = add_manual_repo(payload.get("url", ""))
                subprocess.run([sys.executable, "scripts/classify_repos.py"], cwd=ROOT, check=True)
                subprocess.run([sys.executable, "scripts/build_readme.py"], cwd=ROOT, check=True)
                self.send_json({"ok": True, "repo": repo})
                return
            if path == "/api/rebuild":
                subprocess.run([sys.executable, "scripts/classify_repos.py"], cwd=ROOT, check=True)
                subprocess.run([sys.executable, "scripts/build_readme.py"], cwd=ROOT, check=True)
                self.send_json({"ok": True})
                return
            self.send_json({"error": "Not found"}, 404)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), ReviewHandler)
    print(f"Review UI running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
