# Point Cloud Perception

Point cloud processing, segmentation, detection, completion, representation learning, and 3D perception networks.

Repositories: `61`

[Back to README](../../README.md)

| Topic | Repos |
| --- | ---: |
| Segmentation | 26 |
| Processing Libraries | 17 |
| General | 13 |
| 3D Detection | 3 |
| Representation Learning | 2 |

## Segmentation

- [Pointcept/SegmentAnything3D](https://github.com/Pointcept/SegmentAnything3D) - [ICCV'23 Workshop] SAM3D: Segment Anything in 3D Scenes
- [PRBonn/depth_clustering](https://github.com/PRBonn/depth_clustering) - 🚕 Fast and robust clustering of point clouds generated with a Velodyne sensor.
- [szenergy/awesome-lidar](https://github.com/szenergy/awesome-lidar) - 😎 Awesome LIDAR list. The list includes LIDAR manufacturers, datasets, point cloud-processing algorithms, point cloud frameworks and simulators.
- [PRBonn/semantic-kitti-api](https://github.com/PRBonn/semantic-kitti-api) - SemanticKITTI API for visualizing dataset, processing data, and evaluating results.
- [PRBonn/LiDAR-MOS](https://github.com/PRBonn/LiDAR-MOS) - (LMNet) Moving Object Segmentation in 3D LiDAR Data: A Learning-based Approach Exploiting Sequential Data (RAL/IROS 2021)
- [xuxw98/ESAM](https://github.com/xuxw98/ESAM) - [ICLR 2025, Oral] EmbodiedSAM: Online Segment Any 3D Thing in Real Time
- [LimHyungTae/patchwork](https://github.com/LimHyungTae/patchwork) - SOTA fast and robust ground segmentation using 3D point cloud (accepted in RA-L'21 w/ IROS'21)
- [yzrobot/adaptive_clustering](https://github.com/yzrobot/adaptive_clustering) - [ROS package] Lightweight and Accurate Point Cloud Clustering
- [PRBonn/4DMOS](https://github.com/PRBonn/4DMOS) - Receding Moving Object Segmentation in 3D LiDAR Data Using Sparse 4D Convolutions (RAL 2022)
- [url-kaist/TRAVEL](https://github.com/url-kaist/TRAVEL) - [RA-L] Traversable ground and above-ground object segmentation using graph representation of 3D LiDAR scans
- [dcmlr/groundgrid](https://github.com/dcmlr/groundgrid) - Source code for the article "GroundGrid: LiDAR Point Cloud Ground Segmentation and Terrain Estimation"
- [CN-ADLab/SAM4D](https://github.com/CN-ADLab/SAM4D) - [ICCV 2025] SAM4D: Segment Anything in Camera and LiDAR Streams
- [nv-dvl/segment-anything-lidar](https://github.com/nv-dvl/segment-anything-lidar) - [ECCV 2024] Better Call SAL: Towards Learning to Segment Anything in Lidar
- [wh200720041/mms_slam](https://github.com/wh200720041/mms_slam)
- [EEPT-LAB/DipG-Seg](https://github.com/EEPT-LAB/DipG-Seg) - The official implementation of DipG-Seg.
- [RayFronts/RayFronts](https://github.com/RayFronts/RayFronts) - [IROS'25] Source code for "RayFronts: Open-Set Semantic Ray Frontiers for Online Scene Understanding and Exploration"
- [Cavendish518/SALT](https://github.com/Cavendish518/SALT) - Awesome semi-automatic labeling tool for general LiDAR point clouds!
- [Ilya-Fradlin/Interactive4D](https://github.com/Ilya-Fradlin/Interactive4D) - [ICRA 2025] Interactive4D: Interactive 4D LiDAR Segmentation
- [PRBonn/Mask4D](https://github.com/PRBonn/Mask4D) - Mask4D: End-to-End Mask-Based 4D Panoptic Segmentation for LiDAR Sequences, RA-L, 2023
- [MIT-SPARK/semantic_inference](https://github.com/MIT-SPARK/semantic_inference) - ROS interface to closed and open-set semantic segmentation models
- [NEU-REAL/OTD](https://github.com/NEU-REAL/OTD) - [ICRA'24]Observation Time Difference: an Online Dynamic Objects Removal Method for Ground Vehicles
- [youquanl/M3Net](https://github.com/youquanl/M3Net) - Multi-Space Alignments Towards Universal LiDAR Segmentation
- [neng-wang/Awesome-LiDAR-MOS](https://github.com/neng-wang/Awesome-LiDAR-MOS) - Awesome Point Cloud Moving Object Segmentation
- [PRBonn/forest_inventory_pipeline](https://github.com/PRBonn/forest_inventory_pipeline) - Pipeline for segmenting trees and estimating traits from LiDAR data.
- [Runsong123/PCF-Lift](https://github.com/Runsong123/PCF-Lift) - Code Release for ECCV 2024, "PCF-Lift: Panoptic Lifting by Probabilistic Contrastive Fusion"
- [ROBOT-WSC/SGT-LLC](https://github.com/ROBOT-WSC/SGT-LLC) - iDAR Loop Closing Based on Semantic Graph with Triangular Spatial Topology 2025 RAL

## Processing Libraries

- [fwilliams/point-cloud-utils](https://github.com/fwilliams/point-cloud-utils) - An easy-to-use Python library for processing and manipulating 3D point clouds and meshes.
- [gisbi-kim/removert](https://github.com/gisbi-kim/removert) - Remove then revert (IROS 2020)
- [hku-mars/M-detector](https://github.com/hku-mars/M-detector)
- [hku-mars/HBA](https://github.com/hku-mars/HBA) - [RAL 2023] A globally consistent LiDAR map optimization module
- [RuanJY/SLAMesh](https://github.com/RuanJY/SLAMesh) - ICRA2023, A real-time LiDAR simultaneous localization and meshing method.
- [SS47816/lidar_obstacle_detector](https://github.com/SS47816/lidar_obstacle_detector) - 3D LiDAR Object Detection & Tracking using Euclidean Clustering, RANSAC, & Hungarian Algorithm
- [EPVelasco/lidar-camera-fusion](https://github.com/EPVelasco/lidar-camera-fusion) - The code implemented in ROS projects a point cloud obtained by a Velodyne VLP16 3D-Lidar sensor on an image from an RGB camera.
- [hku-mars/M2Mapping](https://github.com/hku-mars/M2Mapping) - [ICRA 2025] Neural Surface Reconstruction and Rendering for LiDAR-Visual Systems
- [SiyuanHuang95/Livox-Localization](https://github.com/SiyuanHuang95/Livox-Localization) - A simple localization framework that can re-localize in one point-cloud map.
- [Livox-SDK/livox_cloud_undistortion](https://github.com/Livox-SDK/livox_cloud_undistortion) - This project is used for lidar point cloud undistortion.
- [ziquan111/RobustPCLReconstruction](https://github.com/ziquan111/RobustPCLReconstruction) - Robust Point Cloud Based Reconstruction of Large-Scale Outdoor Scenes
- [ctu-mrs/RMS](https://github.com/ctu-mrs/RMS) - Code for RA-L paper "RMS: Redundancy-Minimizing Point Cloud Sampling for Real-Time Pose Estimation"
- [Geekgineer/CloudPeek](https://github.com/Geekgineer/CloudPeek) - CloudPeek is a lightweight, cross-platform, single-header C++ point cloud viewer. It’s designed for simplicity and efficiency, requiring no heavy libraries like PCL or Open3D. Ideal for v...
- [leo-drive/color-point-cloud](https://github.com/leo-drive/color-point-cloud) - Create color point clouds with ROS2
- [ZhangXiaze/DeepPointMap](https://github.com/ZhangXiaze/DeepPointMap) - Implementation of DeepPointMap (AAAI2024), a nerual network-based LiDAR SLAM architecture in Pytorch
- [LTU-RAI/sga-dpcc](https://github.com/LTU-RAI/sga-dpcc) - Official page for SGA-DPCC (Scene Graph-Aware Deep Point Cloud Compression), accepted @ RA-L'25, to be presented @ ICRA'26
- [zhuhongwei123/Point-Cloud-Dynamic-Point-Removal-Framework](https://github.com/zhuhongwei123/Point-Cloud-Dynamic-Point-Removal-Framework)

## General

- [nv-tlabs/NKSR](https://github.com/nv-tlabs/NKSR) - [CVPR 2023 Highlight] Neural Kernel Surface Reconstruction
- [MOLAorg/mola](https://github.com/MOLAorg/mola) - A Modular Optimization framework for Localization and mApping (MOLA)
- [xiaohulugo/3DLineDetection](https://github.com/xiaohulugo/3DLineDetection) - A simple and efficient 3D line detection algorithm for large scale unorganized point cloud
- [LimHyungTae/ERASOR](https://github.com/LimHyungTae/ERASOR) - Official page of ERASOR (Egocentric Ratio of pSeudo Occupancy-based Dynamic Object Removal), which is accepted @ RA-L'21 with ICRA'21
- [PJLab-ADG/PCSim](https://github.com/PJLab-ADG/PCSim) - PCSim: LiDAR Point Cloud Simulation and Sensor Placement! Code of [ICRA 2023] "Analyzing Infrastructure LiDAR Placement with Realistic LiDAR Simulation Library" and [ICCV 2023] "Optimizin...
- [ispc-lab/LiDAR4D](https://github.com/ispc-lab/LiDAR4D) - 💫 [CVPR 2024] LiDAR4D: Dynamic Neural Fields for Novel Space-time View LiDAR Synthesis
- [MKJia/BeautyMap](https://github.com/MKJia/BeautyMap) - [RA-L'24] BeautyMap: Binary-Encoded Adaptable Ground Matrix for Dynamic Points Removal in Global Maps
- [junshengzhou/VP2P-Match](https://github.com/junshengzhou/VP2P-Match) - [NeurIPS'2023 Spotlight]: Differentiable Registration of Images and LiDAR Point Clouds with VoxelPoint-to-Pixel Matching
- [HITSZ-NRSL/RCPCC](https://github.com/HITSZ-NRSL/RCPCC) - [ICRA 2025] Real-Time LiDAR Point Cloud Compression and Transmission for Resource-constrained Robots
- [GuYufeng93/Pointcloud-to-Images](https://github.com/GuYufeng93/Pointcloud-to-Images) - An algorithm for projecting three-dimensional laser point cloud data into serialized two-dimensional images.
- [rsasaki0109/dynamic-3d-object-removal](https://github.com/rsasaki0109/dynamic-3d-object-removal) - Numpy-only dynamic object removal for LiDAR point clouds — 3D box crop + temporal filtering. No GPU, no deep learning.
- [IIT-PAVIS/SC3K](https://github.com/IIT-PAVIS/SC3K) - Repository of the ICCV23 paper "SC3K: Self-supervised and Coherent 3D Keypoints Estimation from Rotated, Noisy, and Decimated Point Cloud Data"
- [NTNU-Math-Chern/FracGM](https://github.com/NTNU-Math-Chern/FracGM) - A Fast Fractional Programming Technique for Geman-McClure Robust Estimator (RA-L 2024)

## 3D Detection

- [yifanzhang713/IA-SSD](https://github.com/yifanzhang713/IA-SSD) - Not All Points Are Equal: Learning Highly Efficient Point-based Detectors for 3D LiDAR Point Clouds (CVPR 2022, Oral)
- [worldbench/Robo3D](https://github.com/worldbench/Robo3D) - [ICCV 2023] Robo3D: Towards Robust and Reliable 3D Perception against Corruptions
- [zimingluo/Point2Graph](https://github.com/zimingluo/Point2Graph) - Point2Graph: An End-to-end Point Cloud-based 3D Open-Vocabulary Scene Graph for Robot Navigation

## Representation Learning

- [youquanl/Segment-Any-Point-Cloud](https://github.com/youquanl/Segment-Any-Point-Cloud) - [NeurIPS'23 Spotlight] Segment Any Point Cloud Sequences by Distilling Vision Foundation Models
- [YuePanEdward/Pointcloud_Format_Transformer](https://github.com/YuePanEdward/Pointcloud_Format_Transformer) - A Tool for various point cloud data format transformation for well-known datasets
