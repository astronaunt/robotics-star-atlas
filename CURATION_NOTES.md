# Curation Notes

This repository already provides a cleaner top-level taxonomy for the current GitHub Lists, but a few source lists are large enough that a second pass would make the public presentation even stronger.

## Priority Lists to Split Further

### 1. `SLAM-single algorithm` (`385` repos)

Recommended next split:

- LiDAR SLAM
- Visual SLAM
- Multi-sensor fusion
- Back-end / optimization
- Dynamic / semantic SLAM
- Robustness / degeneration

### 2. `SLAM-tools` (`229` repos)

Recommended next split:

- Math / optimization libraries
- Geometry / point-cloud libraries
- Visualization / UI tools
- ROS / robotics middleware
- Evaluation / benchmarking tools

### 3. `SLAM-learning` (`92` repos)

Recommended next split:

- Tutorials
- Notes / blogs
- Course projects
- Survey / reading lists

### 4. `Other Tools` (`88` repos)

Recommended next split:

- Productivity tools
- Writing / paper tools
- DevOps / deployment
- Visualization / annotation

### 5. `plan` (`77` repos)

Recommended next split:

- Motion planning
- Trajectory optimization
- Navigation stack
- Decision-making / behavior planning

## Practical Recommendation

For the public version, the current structure is already strong enough to publish.

If you want to make it even more polished later, the best investment is:

1. Split `SLAM-single algorithm`.
2. Split `SLAM-tools`.
3. Rename a few broad lists with more descriptive public-facing names.

That order will improve readability much more than trying to fine-tune every small category first.
