# Factory-patrol-robot
Autonomous factory patrol robot for industrial environments with security monitoring 

# 🤖 RALLP Workspace: Setup and Navigation

This repository provides a comprehensive environment for simulating and controlling the **RALLP** robot. It integrates **ROS 2 Jazzy**, **Gazebo Sim**, and **Nav2** to provide a robust platform for SLAM (Simultaneous Localization and Mapping) and autonomous navigation.

---

## 🎯 Motivation

The goal of this project is to bridge the gap between robot simulation and real-world navigation. By utilizing the latest **ROS 2 Jazzy** features, this workspace allows developers to:

* Simulate realistic robot physics in Gazebo.
* Generate high-fidelity maps using SLAM.
* Test autonomous path planning and obstacle avoidance in a virtual "warehouse" environment before deployment.

---

## 🛠 Prerequisites & Installation

Follow these steps to prepare your environment. We assume a fresh installation of **Ubuntu 24.04 (Noble Numbat)**.

### 1. System & IDE Setup 💻

* **Operating System:** [Install Ubuntu 24.04 Desktop](https://ubuntu.com/download/desktop).
* **Code Editor:** [Install VS Code](https://code.visualstudio.com/download) for an optimized development experience.
* **Version Control:** Install Git via the terminal:
```bash
sudo apt update && sudo apt install git -y

```



### 2. Workspace Preparation 📁

We need to clone the repository and organize the directory structure for **colcon** (the ROS 2 build tool).

```bash
cd ~
git clone https://github.com/Ihebzaouali/Factory-patrol-robot.git
cd rallp_ws/
mv rallp ~          # Move configuration files to home
mkdir src           # Create source folder
mv * src/           # Move packages into src (ignore error about moving src into itself)

```
## Fix the LFS files:

#### 1. Install Git LFS if not already installed:
```bash
sudo apt update
sudo apt install git-lfs
git lfs install
```

#### 2. Fetch and checkout the LFS files:
```bash
cd rallp_oorb_ws
git lfs fetch --all
git lfs checkout
```

### 3. ROS 2 Jazzy Installation 🐢

Install **ROS 2 Jazzy Jalisco** by following the [official documentation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html). After installation, source your environment:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc

```

### 4. Dependencies & Toolkits 📦

This project relies on several ROS 2 plugins for Gazebo integration, sensor processing, and navigation.

```bash
# Gazebo & Control Plugins
sudo apt install ros-jazzy-ros-gz-* ros-jazzy-ros2-control ros-jazzy-gz-ros2-control

# Navigation & Localization Tools
sudo apt install ros-jazzy-nav2-* ros-jazzy-robot-localization ros-jazzy-tf2-ros

# Teleop & Utilities
sudo apt install ros-jazzy-interactive-marker-twist-server ros-jazzy-twist-mux \
ros-jazzy-joy-linux ros-jazzy-teleop-twist-joy ros-jazzy-teleop-twist-keyboard \
ros-jazzy-nmea-msgs ros-jazzy-rtcm-msgs libasio-dev

```

---

## 🚀 Launching the Simulation

### Build the Workspace

Before running any nodes, you must build the packages:

```bash
cd ~/rallp_oorb_ws/
colcon build
source install/setup.bash

```


### Scenario A: SLAM & Mapping 🗺️

Use this mode to explore an unknown environment and generate a digital map.

1. **Launch Gazebo Sim:**
2. **Spawn Robot:**
```bash
ros2 launch rallp_gz combined_launch.py
```

3. **Start Nav2:**
```bash
ros2 launch rallp_nav2_demos nav2.launch.py use_sim_time:=true

```


4. **Run SLAM:**
```bash
ros2 launch rallp_nav2_demos slam.launch.py use_sim_time:=true setup_path:=/home/$USER/rallp/

```


5. **Visualize in RViz:**
```bash
ros2 launch rallp_viz view_navigation.launch.py namespace:=/rallp_0000 use_sim_time:=true

```



---

### 🕹️ Manual Control & Map Saving

To move the robot and explore the environment, open a new terminal and run:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -r __ns:=/rallp_0000

```

Once you are satisfied with the generated map, save it using the Map Saver CLI:

```bash
ros2 run nav2_map_server map_saver_cli -f "my_map" --ros-args -p map_subscribe_transient_local:=true -r __ns:=/rallp_0000

```


### Scenario B: Localization & Autonomous Navigation 📍

Use this mode if you already have a pre-existing map and want the robot to navigate autonomously to specific goals.

1. **Launch Gazebo & Spawn Robot:**
(Follow steps 1 and 2 from Scenario A to initialize the simulation world and the RALLP robot).
2. **Start Nav2 Stack:**
```bash
ros2 launch rallp_nav2_demos nav2.launch.py use_sim_time:=true

```


3. **Run Localization (AMCL):**
This command loads the map and starts the Adaptive Monte Carlo Localization (AMCL) system.
```bash
ros2 launch rallp_nav2_demos localization.launch.py \
use_sim_time:=true \
map:=/home/$USER/rallp_oorb_ws/src/rallp_nav2_demos/maps/warehouse.yaml \
setup_path:=/home/$USER/rallp/

```


4. **Visualize & Navigate:**
Open the visualization interface to set your "2D Pose Estimate" and "Nav2 Goal".
```bash
ros2 launch rallp_viz view_navigation.launch.py namespace:=/rallp_0000 use_sim_time:=true

```



---

### 💡 Pro Tip

When starting localization, the robot might not know exactly where it is. Use the **2D Pose Estimate** tool in RViz to give it a rough starting position on the map; you will see the "cloud" of particles collapse around the robot as it localizes.


---

## 📚 References

> [!IMPORTANT]
> **Primary Reference:** This workspace follows the architectural patterns and best practices established by **[Clearpath Robotics Documentation](https://docs.clearpathrobotics.com/)**.

