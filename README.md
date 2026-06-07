# Robotics Star Atlas

<p align="center">
  <strong>A curated atlas of GitHub repositories for SLAM, LiDAR, localization, mapping, perception, planning, and robotics research tooling.</strong>
</p>

<p align="center">
  <img alt="Indexed repositories" src="https://img.shields.io/badge/indexed%20repos-1373-1f6f5b">
  <img alt="Categories" src="https://img.shields.io/badge/categories-26-2f4858">
  <img alt="Fetched repositories" src="https://img.shields.io/badge/fetched-1370-4f7f52">
</p>

Robotics Star Atlas turns my GitHub stars into a searchable, manually curated research map. It is designed as a personal navigation system first, and as a public reference for researchers and engineers who work around robotics, 3D vision, and autonomous systems.

## Quick Links

| Link | Description |
| --- | --- |
| [Category Index](docs/category-index.md) | Compact category overview. |
| [Update Guide](docs/update-guide.md) | How to add new stars, categories, and manual labels. |

## Setup

```powershell
python -m pip install -r requirements.txt
```

The generated README and category pages can be browsed directly on GitHub. The local UI is only needed when you want to curate or rebuild the index.

## Overview

<table>
  <tr>
    <td><strong>GitHub user</strong><br><code>@astronaunt</code></td>
    <td><strong>Indexed repositories</strong><br><code>1373</code></td>
    <td><strong>Categories</strong><br><code>26</code></td>
  </tr>
  <tr>
    <td><strong>Fetched successfully</strong><br><code>1370</code></td>
    <td><strong>Focus</strong><br><code>Robotics & 3D Vision</code></td>
    <td><strong>Maintenance</strong><br><code>Manual + Generated</code></td>
  </tr>
</table>

## Curation Notice

This index is semi-automatic. Repository metadata, GitHub Lists, README snippets, and manual corrections are combined to assign categories and labels. Some repositories may be missing, outdated, multi-topic, or placed in a category that is not the best fit. Please treat this as a personal research map and a useful starting point, not as an authoritative benchmark or taxonomy.

## Categories

| Category | Repos | Description |
| --- | ---: | --- |
| [LiDAR-Inertial State Estimation](docs/categories/lidar-inertial-odometry.md) | 147 | LiDAR-IMU state estimation, LIO SLAM, filtering/smoothing-based LIO, and LIO mapping systems. |
| [LiDAR State Estimation](docs/categories/lidar-odometry.md) | 71 | LiDAR-only state estimation and LiDAR SLAM front-ends, including LOAM, ICP/NDT, and scan-to-map systems. |
| [Visual / Visual-Inertial State Estimation](docs/categories/visual-inertial-odometry.md) | 67 | Visual state estimation, visual-inertial state estimation, monocular/stereo/RGB-D VO, and VIO SLAM systems. |
| [LiDAR-Visual-Inertial State Estimation](docs/categories/lidar-visual-inertial-odometry.md) | 32 | LiDAR-camera-IMU state estimation, LIVO, LIC, and multi-modal state estimation / SLAM systems. |
| [Place Recognition & Loop Closure](docs/categories/place-recognition-loop-closure.md) | 97 | Place recognition, loop closure, scan context, global descriptors, retrieval, and relocalization triggers. |
| [Mapping & Map Representation](docs/categories/mapping-map-representation.md) | 173 | Mapping, map representation, occupancy/voxel/surfel/TSDF maps, neural maps, NeRF, and 3D Gaussian Splatting. |
| [Point Cloud Registration](docs/categories/point-cloud-registration.md) | 43 | Point cloud registration, ICP/GICP/NDT, scan matching, feature matching, and correspondence-based alignment. |
| [Point Cloud Perception](docs/categories/point-cloud-perception.md) | 69 | Point cloud processing, segmentation, detection, completion, representation learning, and 3D perception networks. |
| [Multi-Robot SLAM & Collaborative Perception](docs/categories/multi-robot-slam.md) | 55 | Multi-robot SLAM, distributed mapping, collaborative perception, V2X perception, and multi-agent fusion. |
| [Radar SLAM & Perception](docs/categories/radar-slam-perception.md) | 37 | Radar state estimation, radar SLAM, mmWave radar perception, imaging radar, and radar-LiDAR fusion. |
| [Calibration & Time Synchronization](docs/categories/calibration-synchronization.md) | 33 | Camera/LiDAR/IMU/radar calibration, extrinsics, intrinsics, targetless calibration, and time synchronization. |
| [Degeneracy, Robustness & Failure Analysis](docs/categories/degeneracy-robustness.md) | 18 | Degeneracy analysis, robustness, failure detection, outlier rejection, and uncertainty-aware SLAM. |
| [UAV & Aerial Robotics](docs/categories/uav-aerial-robotics.md) | 25 | UAV autonomy, aerial robotics, quadrotor navigation, flight systems, and aerial mapping. |
| [Evaluation & Metrics](docs/categories/evaluation-metrics.md) | 11 | Trajectory evaluation, benchmark metrics, result analysis, and evaluation tools. |
| [Event Camera Vision](docs/categories/event-camera.md) | 15 | Event-camera perception, event-based SLAM, asynchronous vision, and event-based state estimation. |
| [Multi-LiDAR Fusion](docs/categories/multi-lidar-fusion.md) | 16 | Multi-LiDAR calibration, fusion, synchronization, and multi-LiDAR SLAM systems. |
| [GNSS, HD Map & Global Localization](docs/categories/gnss-hd-map-localization.md) | 38 | GNSS/INS, RTK, HD maps, map matching, global localization, and map-based relocalization. |
| [Planning & Navigation](docs/categories/planning-navigation.md) | 70 | Motion planning, path planning, trajectory optimization, navigation stacks, and control. |
| [Datasets & Benchmarks](docs/categories/datasets-benchmarks.md) | 59 | Datasets, benchmarks, leaderboards, dataset APIs, ground truth, and evaluation protocols. |
| [SLAM Learning, Handbooks & Notes](docs/categories/slam-learning-handbooks.md) | 49 | SLAM handbooks, tutorials, courses, annotated code, code-reading notes, and learning resources. |
| [Tools, Engineering & Productivity](docs/categories/tools-engineering-productivity.md) | 201 | ROS/ROS2 tools, Docker/reproduction environments, visualization, annotation, productivity, LLM tools, C++ resources, and research utilities. |
| [Paper Lists, Surveys & Awesome Collections](docs/categories/paper-survey-awesome.md) | 61 | Curated paper lists, surveys, awesome lists, and literature collections. |
| [Deep IMU](docs/categories/deep-imu.md) | 6 | Custom user-defined category. |
| [FMCW SLAM](docs/categories/fmcw-slam.md) | 2 | Custom user-defined category. |
| [Leg](docs/categories/leg.md) | 6 | Custom user-defined category. |
| [uwb](docs/categories/uwb.md) | 1 | Custom user-defined category. |

## How To Update

For day-to-day maintenance, use the visual local UI:

```powershell
python scripts\review_server.py
```

Then open `http://127.0.0.1:8765`.

| Scenario | Recommended action |
| --- | --- |
| You starred one new repository | Paste its GitHub URL into `Add Repo URL`, assign labels, then click `Rebuild README`. |
| You created a new research direction | Use `Add Category`, then assign the category as primary or as an additional label. |
| Many GitHub stars or Lists changed | Run the full refresh pipeline below. |
| A category is wrong | Select the repository in the UI, change the primary category or additional labels, then save. |

Full refresh pipeline:

```powershell
python scripts\sync_lists.py
python scripts\fetch_repo_metadata.py
python scripts\classify_repos.py
python scripts\build_readme.py
```

See [Update Guide](docs/update-guide.md) for details.

## Method

- Classification uses repository name, About text, Topics, original list description, and a short README excerpt.
- Original GitHub Lists are used as weak priors, especially for learning resources and domain-specific collections.
- Manual corrections and multi-label assignments can be made with `python scripts\review_server.py`, or by editing `data/manual_categories.csv` / `data/overrides.json`.
- Repository rows intentionally omit internal classification evidence, so the public README stays clean.

## Supporting Docs

- [Category Index](docs/category-index.md)
- [Update Guide](docs/update-guide.md)
