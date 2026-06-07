from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = ROOT / "data" / "repo_metadata.json"
OVERRIDES_PATH = ROOT / "data" / "overrides.json"
MANUAL_CSV_PATH = ROOT / "data" / "manual_categories.csv"
CUSTOM_CATEGORIES_PATH = ROOT / "data" / "custom_categories.json"
OUTPUT_PATH = ROOT / "data" / "classified_repos.json"
REVIEW_QUEUE_PATH = ROOT / "data" / "review_queue.csv"


CATEGORIES = [
    {
        "id": "lidar-inertial-odometry",
        "name": "LiDAR-Inertial State Estimation",
        "name_zh": "激光惯导里程计",
        "description": "LiDAR-IMU state estimation, LIO SLAM, filtering/smoothing-based LIO, and LIO mapping systems.",
        "kind": "algorithm",
        "keywords": {
            "lidar-inertial odometry": 18,
            "lidar inertial odometry": 18,
            "lidar-imu": 12,
            "lidar imu": 12,
            "lio": 12,
            "lio-sam": 18,
            "fast-lio": 18,
            "eskf": 6,
            "iekf": 6,
            "ikf": 5,
        },
        "lists": {"slam-lio": 12},
    },
    {
        "id": "lidar-odometry",
        "name": "LiDAR State Estimation",
        "name_zh": "纯激光里程计",
        "description": "LiDAR-only state estimation and LiDAR SLAM front-ends, including LOAM, ICP/NDT, and scan-to-map systems.",
        "kind": "algorithm",
        "keywords": {
            "lidar odometry": 18,
            "laser odometry": 18,
            "lidar-only odometry": 18,
            "lidar only odometry": 18,
            "lidar slam": 9,
            "loam": 10,
            "kiss-icp": 10,
            "ct-icp": 10,
            "odometry pipeline": 8,
        },
        "lists": {"lo": 12},
    },
    {
        "id": "visual-inertial-odometry",
        "name": "Visual / Visual-Inertial State Estimation",
        "name_zh": "视觉里程计与视觉惯导",
        "description": "Visual state estimation, visual-inertial state estimation, monocular/stereo/RGB-D VO, and VIO SLAM systems.",
        "kind": "algorithm",
        "keywords": {
            "visual-inertial odometry": 18,
            "visual inertial odometry": 18,
            "inertial odometry": 14,
            "learned inertial odometry": 18,
            "visual odometry": 16,
            "vio": 12,
            "stereo visual odometry": 18,
            "stereo vo": 14,
            "monocular": 5,
            "rgb-d": 5,
        },
        "lists": {"vio": 12, "stereo-visual-odometry": 12},
    },
    {
        "id": "lidar-visual-inertial-odometry",
        "name": "LiDAR-Visual-Inertial State Estimation",
        "name_zh": "激光视觉惯导里程计",
        "description": "LiDAR-camera-IMU state estimation, LIVO, LIC, and multi-modal state estimation / SLAM systems.",
        "kind": "algorithm",
        "keywords": {
            "lidar-inertial-visual": 20,
            "lidar visual inertial": 20,
            "lidar-inertial-camera": 18,
            "lidar inertial camera": 18,
            "livo": 16,
            "lic": 9,
            "camera lidar imu": 14,
            "multi-modal odometry": 14,
            "multi modal odometry": 14,
        },
        "lists": {"slam-livo": 14},
    },
    {
        "id": "place-recognition-loop-closure",
        "name": "Place Recognition & Loop Closure",
        "name_zh": "地点识别与回环检测",
        "description": "Place recognition, loop closure, scan context, global descriptors, retrieval, and relocalization triggers.",
        "kind": "algorithm",
        "keywords": {
            "place recognition": 20,
            "loop closure": 18,
            "loop detection": 16,
            "scan context": 16,
            "global descriptor": 12,
            "descriptor": 6,
            "retrieval": 6,
        },
        "lists": {"place-recognition": 12},
    },
    {
        "id": "mapping-map-representation",
        "name": "Mapping & Map Representation",
        "name_zh": "建图与地图表达",
        "description": "Mapping, map representation, occupancy/voxel/surfel/TSDF maps, neural maps, NeRF, and 3D Gaussian Splatting.",
        "kind": "algorithm",
        "keywords": {
            "mapping": 9,
            "map representation": 18,
            "occupancy": 12,
            "voxel map": 12,
            "voxel": 6,
            "surfel": 12,
            "tsdf": 12,
            "submap": 9,
            "dense 3d slam": 12,
            "nerf": 14,
            "neural radiance field": 16,
            "radiance field": 14,
            "3d gaussian splatting": 18,
            "gaussian splatting": 18,
            "3dgs": 18,
            "splatting": 12,
        },
        "lists": {"slam-map": 12, "nerf": 10, "3dgs": 10},
    },
    {
        "id": "point-cloud-registration",
        "name": "Point Cloud Registration",
        "name_zh": "点云配准",
        "description": "Point cloud registration, ICP/GICP/NDT, scan matching, feature matching, and correspondence-based alignment.",
        "kind": "algorithm",
        "keywords": {
            "point cloud registration": 20,
            "registration": 11,
            "scan matching": 16,
            "icp": 14,
            "gicp": 16,
            "ndt": 12,
            "correspondence": 8,
            "align point": 8,
        },
        "lists": {"point-cloud": 5},
    },
    {
        "id": "point-cloud-perception",
        "name": "Point Cloud Perception",
        "name_zh": "点云感知",
        "description": "Point cloud processing, segmentation, detection, completion, representation learning, and 3D perception networks.",
        "kind": "algorithm",
        "keywords": {
            "point cloud": 9,
            "point-cloud": 9,
            "3d object detection": 18,
            "point cloud detection": 18,
            "semantic segmentation": 16,
            "instance segmentation": 15,
            "point cloud segmentation": 18,
            "mmdetection3d": 16,
            "completion": 8,
            "downsampling": 8,
            "normal estimation": 8,
            "meshing": 8,
            "open3d": 10,
            "pcl": 8,
        },
        "lists": {"point-cloud": 10, "point-cloud-detect": 14},
    },
    {
        "id": "multi-robot-slam",
        "name": "Multi-Robot SLAM & Collaborative Perception",
        "name_zh": "多机器人 SLAM 与协同感知",
        "description": "Multi-robot SLAM, distributed mapping, collaborative perception, V2X perception, and multi-agent fusion.",
        "kind": "algorithm",
        "keywords": {
            "multi-robot slam": 20,
            "multi robot slam": 20,
            "distributed slam": 18,
            "collaborative slam": 18,
            "multi-agent slam": 16,
            "multi agent slam": 16,
            "collaborative perception": 18,
            "cooperative perception": 18,
            "v2x": 12,
            "pose graph merging": 12,
        },
        "lists": {"slam-multirobot": 12, "collaborative-perception": 14},
    },
    {
        "id": "radar-slam-perception",
        "name": "Radar SLAM & Perception",
        "name_zh": "雷达 SLAM 与感知",
        "description": "Radar state estimation, radar SLAM, mmWave radar perception, imaging radar, and radar-LiDAR fusion.",
        "kind": "algorithm",
        "keywords": {
            "radar slam": 20,
            "radar odometry": 18,
            "radar": 12,
            "mmwave": 14,
            "mm-wave": 14,
            "imaging radar": 14,
        },
        "lists": {"radar": 14},
    },
    {
        "id": "calibration-synchronization",
        "name": "Calibration & Time Synchronization",
        "name_zh": "标定与时间同步",
        "description": "Camera/LiDAR/IMU/radar calibration, extrinsics, intrinsics, targetless calibration, and time synchronization.",
        "kind": "algorithm",
        "keywords": {
            "calibration": 18,
            "extrinsic": 14,
            "intrinsic": 12,
            "hand-eye": 14,
            "hand eye": 14,
            "time synchronization": 14,
            "time sync": 12,
            "targetless": 10,
        },
        "lists": {"slam-calib": 14},
    },
    {
        "id": "degeneracy-robustness",
        "name": "Degeneracy, Robustness & Failure Analysis",
        "name_zh": "退化、鲁棒性与失效分析",
        "description": "Degeneracy analysis, robustness, failure detection, outlier rejection, and uncertainty-aware SLAM.",
        "kind": "algorithm",
        "keywords": {
            "degenerate": 16,
            "degeneracy": 16,
            "degenercy": 16,
            "degradation": 10,
            "robust slam": 14,
            "failure detection": 12,
            "outlier rejection": 10,
            "uncertainty": 8,
        },
        "lists": {"slam-degenerate": 14},
    },
    {
        "id": "uav-aerial-robotics",
        "name": "UAV & Aerial Robotics",
        "name_zh": "无人机与空中机器人",
        "description": "UAV autonomy, aerial robotics, quadrotor navigation, flight systems, and aerial mapping.",
        "kind": "algorithm",
        "keywords": {
            "uav": 20,
            "quadrotor": 18,
            "drone": 16,
            "aerial": 14,
            "flight": 12,
        },
        "lists": {"uav": 14},
    },
    {
        "id": "evaluation-metrics",
        "name": "Evaluation & Metrics",
        "name_zh": "评测工具与指标",
        "description": "Trajectory evaluation, benchmark metrics, result analysis, and evaluation tools.",
        "kind": "tool",
        "keywords": {
            "evaluation": 16,
            "metric": 14,
            "trajectory evaluation": 18,
            "benchmark tool": 14,
            "evo": 10,
            "result analysis": 10,
        },
        "lists": {"slam-tools": 4},
    },
    {
        "id": "event-camera",
        "name": "Event Camera Vision",
        "name_zh": "事件相机视觉",
        "description": "Event-camera perception, event-based SLAM, asynchronous vision, and event-based state estimation.",
        "kind": "algorithm",
        "keywords": {
            "event camera": 20,
            "event-based": 18,
            "event based": 18,
            "dvs": 14,
            "asynchronous vision": 16,
        },
        "lists": {"event": 14},
    },
    {
        "id": "multi-lidar-fusion",
        "name": "Multi-LiDAR Fusion",
        "name_zh": "多激光雷达融合",
        "description": "Multi-LiDAR calibration, fusion, synchronization, and multi-LiDAR SLAM systems.",
        "kind": "algorithm",
        "keywords": {
            "multi-lidar": 20,
            "multi lidar": 20,
            "multiple lidar": 18,
            "dual lidar": 14,
            "lidar fusion": 14,
        },
        "lists": {"slam-multilidar": 14},
    },
    {
        "id": "gnss-hd-map-localization",
        "name": "GNSS, HD Map & Global Localization",
        "name_zh": "GNSS、高精地图与全局定位",
        "description": "GNSS/INS, RTK, HD maps, map matching, global localization, and map-based relocalization.",
        "kind": "algorithm",
        "keywords": {
            "gnss": 18,
            "gps": 12,
            "rtk": 12,
            "ins": 10,
            "hd map": 18,
            "high-definition map": 18,
            "lane map": 12,
            "map matching": 12,
            "global localization": 16,
            "relocalization": 14,
            "map-based localization": 14,
        },
        "lists": {"gnss": 14, "hd-map": 14, "slam-loc": 10},
    },
    {
        "id": "planning-navigation",
        "name": "Planning & Navigation",
        "name_zh": "规划与导航",
        "description": "Motion planning, path planning, trajectory optimization, navigation stacks, and control.",
        "kind": "algorithm",
        "keywords": {
            "motion planning": 20,
            "path planning": 20,
            "trajectory optimization": 18,
            "navigation": 14,
            "planner": 12,
            "nav2": 12,
            "mpc": 10,
            "control": 7,
        },
        "lists": {"plan": 12},
    },
    {
        "id": "datasets-benchmarks",
        "name": "Datasets & Benchmarks",
        "name_zh": "数据集与基准",
        "description": "Datasets, benchmarks, leaderboards, dataset APIs, ground truth, and evaluation protocols.",
        "kind": "resource",
        "keywords": {
            "dataset": 18,
            "benchmark": 16,
            "leaderboard": 14,
            "ground truth": 12,
            "evaluation protocol": 11,
            "dataset api": 10,
        },
        "lists": {"slam-dataset": 14},
    },
    {
        "id": "slam-learning-handbooks",
        "name": "SLAM Learning, Handbooks & Notes",
        "name_zh": "SLAM 学习资料、手册与笔记",
        "description": "SLAM handbooks, tutorials, courses, annotated code, code-reading notes, and learning resources.",
        "kind": "resource",
        "keywords": {
            "handbook": 18,
            "slam handbook": 22,
            "slambook": 18,
            "tutorial": 11,
            "course": 10,
            "notes": 10,
            "detailednote": 12,
            "code reading": 12,
            "annotated": 9,
            "learn slam": 10,
            "learning": 6,
        },
        "lists": {"slam-learning": 14},
    },
    {
        "id": "tools-engineering-productivity",
        "name": "Tools, Engineering & Productivity",
        "name_zh": "工具、工程与科研效率",
        "description": "ROS/ROS2 tools, Docker/reproduction environments, visualization, annotation, productivity, LLM tools, C++ resources, and research utilities.",
        "kind": "tool",
        "keywords": {
            "ros": 12,
            "ros2": 12,
            "rosbag": 14,
            "driver": 10,
            "docker": 18,
            "container": 14,
            "deployment": 12,
            "visualization": 12,
            "annotation": 12,
            "viewer": 10,
            "gui": 8,
            "llm": 14,
            "large language model": 14,
            "agent": 10,
            "claude": 10,
            "chatgpt": 10,
            "cursor": 8,
            "c++": 14,
            "cpp": 12,
            "latex": 8,
            "zotero": 12,
            "citation": 10,
            "download": 7,
            "productivity": 8,
        },
        "lists": {"slam-tools": 8, "other-tools": 8, "c-learning": 10, "llm": 10},
    },
    {
        "id": "paper-survey-awesome",
        "name": "Paper Lists, Surveys & Awesome Collections",
        "name_zh": "论文列表、综述与 Awesome 集合",
        "description": "Curated paper lists, surveys, awesome lists, and literature collections.",
        "kind": "resource",
        "keywords": {
            "awesome": 14,
            "survey": 12,
            "paper list": 12,
            "papers": 8,
            "reading list": 10,
            "literature": 9,
            "collection": 6,
            "curated list": 12,
        },
        "lists": {},
    },
]


SUBTOPICS = {
    "mapping-map-representation": [
        ("3D Gaussian Splatting", ["3d gaussian splatting", "gaussian splatting", "3dgs", "splatting"]),
        ("NeRF & Neural Rendering", ["nerf", "neural radiance field", "radiance field", "novel view synthesis"]),
        ("Voxel / TSDF / Occupancy Maps", ["voxel", "tsdf", "occupancy", "submap"]),
        ("General Mapping", ["mapping", "map representation", "surfel"]),
    ],
    "point-cloud-perception": [
        ("3D Detection", ["3d object detection", "point cloud detection", "mmdetection3d", "bev"]),
        ("Segmentation", ["semantic segmentation", "instance segmentation", "point cloud segmentation", "segmentation"]),
        ("Processing Libraries", ["open3d", "pcl", "downsampling", "normal estimation", "meshing"]),
        ("Representation Learning", ["representation learning", "completion", "transformer"]),
    ],
    "tools-engineering-productivity": [
        ("ROS / Robotics Tools", ["ros", "ros2", "rosbag", "driver", "nodelet"]),
        ("Docker / Reproducibility", ["docker", "container", "deployment", "reproducible"]),
        ("Research Productivity", ["latex", "zotero", "citation", "paper", "download", "productivity"]),
        ("LLM / AI Tools", ["llm", "claude", "chatgpt", "cursor", "agent", "rag"]),
        ("C++ / Development", ["c++", "cpp", "modern cpp", "linux", "programming"]),
        ("Visualization / Annotation", ["visualization", "annotation", "viewer", "gui", "label"]),
    ],
}


CONTENT_REQUIRED_CATEGORIES = {
    "datasets-benchmarks",
    "evaluation-metrics",
    "slam-learning-handbooks",
    "tools-engineering-productivity",
    "paper-survey-awesome",
}

README_WEAK_CATEGORIES = {
    "datasets-benchmarks",
    "tools-engineering-productivity",
    "paper-survey-awesome",
}

GENERIC_DESCRIPTIONS = (
    "contribute to",
    "development by creating an account on github",
)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    return re.sub(r"\s+", " ", text)


def normalized_repo_name(name: str) -> str:
    return name.replace(" /", "/").replace("/ ", "/").replace(" ", "")


def keyword_in_text(text: str, keyword: str) -> bool:
    keyword = normalize_text(keyword).strip()
    if not keyword:
        return False
    if re.search(r"[+#./]", keyword):
        return keyword in text
    pattern = r"(?<![a-z0-9])" + re.escape(keyword).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def load_metadata() -> dict:
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def load_overrides() -> dict:
    overrides: dict[str, dict] = {}
    if OVERRIDES_PATH.exists():
        raw = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
        for repo, value in raw.items():
            if repo == "README":
                continue
            overrides[normalized_repo_name(repo)] = value
    if MANUAL_CSV_PATH.exists():
        with MANUAL_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                repo = normalized_repo_name(row.get("repo", ""))
                category = (row.get("category") or "").strip()
                if repo and category:
                    overrides[repo] = {
                        "category": category,
                        "labels": [item.strip() for item in (row.get("labels") or "").split(";") if item.strip()],
                        "note": row.get("note", ""),
                    }
    return overrides


def load_custom_categories() -> list[dict]:
    if not CUSTOM_CATEGORIES_PATH.exists():
        return []
    payload = json.loads(CUSTOM_CATEGORIES_PATH.read_text(encoding="utf-8"))
    raw_categories = payload.get("categories", []) if isinstance(payload, dict) else payload
    categories = []
    for item in raw_categories:
        cat_id = (item.get("id") or "").strip().lower().replace(" ", "-").replace("/", "-")
        if not cat_id:
            continue
        categories.append(
            {
                "id": cat_id,
                "name": item.get("name") or cat_id,
                "name_zh": item.get("name_zh") or item.get("name") or cat_id,
                "description": item.get("description") or "Custom user-defined category.",
                "kind": item.get("kind") or "custom",
                "keywords": item.get("keywords") or {},
                "lists": item.get("lists") or {},
            }
        )
    return categories


def all_categories() -> list[dict]:
    merged = {item["id"]: item for item in CATEGORIES}
    for item in load_custom_categories():
        merged[item["id"]] = item
    return list(merged.values())


def useful_description(repo: dict) -> str:
    for key in ("about", "list_description"):
        text = " ".join((repo.get(key) or "").split())
        lowered = text.lower()
        if text and not any(fragment in lowered for fragment in GENERIC_DESCRIPTIONS):
            return text
    return ""


def text_fields(repo: dict) -> dict:
    main = " ".join(
        [
            repo.get("repo", ""),
            repo.get("about", ""),
            repo.get("list_description", ""),
            " ".join(repo.get("topics", [])),
        ]
    )
    return {
        "main": normalize_text(main),
        "readme": normalize_text(repo.get("readme_excerpt", "")),
        "lists": set(repo.get("source_lists", [])),
    }


def has_algorithm_signal(repo: dict, fields: dict) -> bool:
    lists = fields["lists"]
    if any(slug.startswith("slam-") for slug in lists) and "slam-tools" not in lists:
        return True
    main = fields["main"]
    return any(
        keyword_in_text(main, kw)
        for kw in [
            "slam",
            "odometry",
            "localization",
            "mapping",
            "registration",
            "calibration",
            "planning",
            "perception",
        ]
    )


def score_repo(repo: dict) -> tuple[dict, list[dict]]:
    fields = text_fields(repo)
    algorithm_signal = has_algorithm_signal(repo, fields)
    scored = []

    for category in all_categories():
        score = 0
        hits = []
        has_content_hit = False
        for keyword, weight in category["keywords"].items():
            if keyword_in_text(fields["main"], keyword):
                score += weight
                hits.append(keyword)
                has_content_hit = True
            elif keyword_in_text(fields["readme"], keyword):
                factor = 0.2 if category["id"] in README_WEAK_CATEGORIES else 0.35
                score += max(1, round(weight * factor))
                hits.append(f"readme:{keyword}")
                has_content_hit = True
        for slug, weight in category["lists"].items():
            if slug in fields["lists"]:
                score += weight
                hits.append(f"list:{slug}")

        if category["id"] in CONTENT_REQUIRED_CATEGORIES and not has_content_hit:
            continue

        if algorithm_signal and category["kind"] == "algorithm" and has_content_hit:
            score += 5
        if algorithm_signal and category["kind"] in {"tool", "resource"} and not has_content_hit:
            score -= 8

        if score > 0:
            scored.append({"id": category["id"], "score": score, "hits": sorted(set(hits))})

    if not scored:
        return {"id": "uncategorized", "score": 0, "hits": []}, []
    scored.sort(key=lambda item: (-item["score"], item["id"]))
    primary = scored[0]
    secondary = [item for item in scored[1:5] if item["score"] >= max(10, primary["score"] - 6)]
    return primary, secondary


def subtopic_for(repo: dict, category_id: str) -> str:
    fields = text_fields(repo)
    rules = SUBTOPICS.get(category_id, [])
    best = ("", 0)
    for name, keywords in rules:
        score = 0
        for keyword in keywords:
            if keyword_in_text(fields["main"], keyword):
                score += 3
            elif keyword_in_text(fields["readme"], keyword):
                score += 1
        if score > best[1]:
            best = (name, score)
    return best[0]


def category_lookup() -> dict:
    return {item["id"]: item for item in all_categories()}


def main() -> None:
    metadata = load_metadata()
    overrides = load_overrides()
    categories = category_lookup()
    category_items = list(categories.values())
    classified = {}
    category_counts = Counter()
    uncategorized = []

    for full_name, repo in metadata["repos"].items():
        primary, secondary = score_repo(repo)
        repo_key = normalized_repo_name(full_name)
        override = overrides.get(repo_key)
        if override:
            forced_category = override.get("category")
            if forced_category in categories:
                primary = {"id": forced_category, "score": 999, "hits": ["manual override"]}
                secondary = []

        category_id = primary["id"]
        if category_id == "uncategorized":
            uncategorized.append(full_name)
            category_name = "Uncategorized"
            category_name_zh = "未分类"
            description = "Needs manual review."
            kind = "review"
        else:
            category_counts[category_id] += 1
            category = categories[category_id]
            category_name = category["name"]
            category_name_zh = category["name_zh"]
            description = category["description"]
            kind = category["kind"]

        manual_labels = []
        if override:
            manual_labels = [
                label
                for label in override.get("labels", [])
                if label in categories and label != category_id
            ]
        labels = []
        if category_id != "uncategorized":
            labels.append(category_id)
        for label in manual_labels:
            if label not in labels:
                labels.append(label)

        classified[full_name] = {
            **repo,
            "display_name": repo_key,
            "display_description": useful_description(repo),
            "manual_note": override.get("note", "") if override else "",
            "manual_labels": manual_labels,
            "labels": labels,
            "primary_category": category_id,
            "primary_category_name": category_name,
            "primary_category_name_zh": category_name_zh,
            "primary_category_description": description,
            "primary_category_kind": kind,
            "primary_subtopic": subtopic_for(repo, category_id),
            "primary_score": primary["score"],
            "secondary_categories": [item["id"] for item in secondary],
            "match_hits": primary["hits"],
        }

    grouped = defaultdict(list)
    category_membership_counts = Counter()
    for repo in classified.values():
        if repo["primary_category"] == "uncategorized":
            grouped["uncategorized"].append(repo)
        for label in repo.get("labels", []):
            grouped[label].append(repo)
            category_membership_counts[label] += 1
    for repos in grouped.values():
        repos.sort(key=lambda item: item["display_name"].lower())

    review_rows = []
    for repo in classified.values():
        if repo["primary_category"] == "uncategorized" or repo["primary_score"] < 12:
            review_rows.append(
                {
                    "repo": repo["display_name"],
                    "current_category": repo["primary_category"],
                    "score": repo["primary_score"],
                    "description": repo["display_description"],
                    "suggested_manual_category": "",
                    "note": "",
                }
            )

    output = {
        "generated_at": metadata["generated_at"],
        "total_unique_repos": metadata["total_unique_repos"],
        "categories": {
            item["id"]: {
                "name": item["name"],
                "name_zh": item["name_zh"],
                "description": item["description"],
                "kind": item["kind"],
                "count": category_membership_counts.get(item["id"], 0),
                "primary_count": category_counts.get(item["id"], 0),
            }
            for item in category_items
        },
        "uncategorized_count": len(uncategorized),
        "uncategorized": sorted(uncategorized),
        "repos": classified,
        "grouped": grouped,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    with REVIEW_QUEUE_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "repo",
                "current_category",
                "score",
                "description",
                "suggested_manual_category",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(sorted(review_rows, key=lambda item: (item["current_category"], item["repo"].lower())))
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Wrote {REVIEW_QUEUE_PATH}")
    print("Top categories:")
    for cat_id, count in category_counts.most_common(25):
        print(cat_id, count)
    print("Uncategorized:", len(uncategorized))


if __name__ == "__main__":
    main()
