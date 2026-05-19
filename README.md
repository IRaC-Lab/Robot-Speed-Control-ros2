# Robot-Speed-Control-ROS2

ROS2 Humble + Gazebo + MoveIt2 based UR3e & Robotiq Pick-and-Place simulation project.  
This project uses a RealSense D435 depth camera and YOLO segmentation to dynamically adjust robot speed based on the distance between a human and the robot.

---

# Environment

- Ubuntu 22.04
- ROS2 Humble
- Gazebo Classic
- MoveIt2
- Python 3

---

# 1. Install ROS2 Humble Dependencies

```bash
sudo apt install -y \
python3-colcon-common-extensions \
python3-rosdep \
python3-vcstool \
python3-argcomplete \
python3-pip
```

```bash
sudo rosdep init
rosdep update
```

---

# 2. Create Workspace

```bash
mkdir -p ~/colcon_ws/src
cd ~/colcon_ws
```

---

# 3. Install Gazebo / MoveIt2 Packages

```bash
sudo apt install -y \
ros-humble-gazebo-ros-pkgs \
ros-humble-gazebo-ros2-control \
ros-humble-moveit \
ros-humble-ros2-control \
ros-humble-ros2-controllers \
ros-humble-joint-state-publisher-gui \
ros-humble-xacro \
ros-humble-rviz2 \
ros-humble-tf-transformations
```

---

# 4. Clone Repository

```bash
cd ~/colcon_ws/src
git clone https://github.com/dlwldbs1226/Robot-Speed-Control-ros2.git
```

---

# 5. Install Additional Repositories

## serial (ROS2 branch)

```bash
cd ~/colcon_ws/src
git clone -b ros2 https://github.com/tylerjw/serial.git serial
```

## pymoveit2

```bash
cd ~/colcon_ws/src
git clone https://github.com/AndrejOrsula/pymoveit2.git
```

---

# 6. Install Dependencies with rosdep

```bash
cd ~/colcon_ws
rosdep install --from-paths src --ignore-src -r -y
```

---

# 7. Configure Gazebo Model Path

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/colcon_ws/src/Robot-Speed-Control-ros2/ur_gripper_gazebo/models
```

Disable Gazebo online model database:

```bash
echo 'export GAZEBO_MODEL_DATABASE_URI=""' >> ~/.bashrc
source ~/.bashrc
```

---

# 8. Install YOLO / Torch Dependencies

```bash
pip3 install torch==1.13.1 torchvision==0.14.1 ultralytics==8.4.50 numpy==1.26.4
```

```bash
pip3 install pandas
```

---

# 9. Build Workspace

```bash
cd ~/colcon_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

Add workspace setup to bashrc:

```bash
echo "source ~/colcon_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

# 10. Launch Simulation

## Gazebo + Robot + Camera

```bash
ros2 launch ur_gripper_gazebo sim.launch.py
```

---

## Move Group

Open a new terminal:

```bash
source ~/colcon_ws/install/setup.bash
ros2 launch ur_robotiq_moveit_config move_group.launch.py use_sim_time:=true
```

---

# 11. Run Pick-and-Place Demo

```bash
python3 ~/colcon_ws/src/Robot-Speed-Control-ros2/ur_robotiq_moveit_config/scripts/pick_place.py
```

---

# 12. Run YOLO Segmentation

```bash
cd ~/colcon_ws/src/Robot-Speed-Control-ros2/yolov5/segment
python3 predict.py --conf 0.7 --imgsz 256
```

- `conf` : detection confidence threshold
- `imgsz` : inference image size

Both values can be adjusted.

---

# 13. Run Depth Alignment & Distance Nodes

```bash
cd ~/colcon_ws/src/Robot-Speed-Control-ros2/realsense-ros/realsense2_camera/scripts
```

```bash
python3 align_depth_to_color_ros2.py
```

```bash
python3 depth_distance_seg_ros2.py
```

---

# Features

- UR3e + Robotiq Gripper Pick-and-Place
- Gazebo Simulation
- RealSense D435 Depth Camera
- YOLO Segmentation
- Human-Robot Distance Monitoring
- Dynamic Robot Speed Scaling (SSM-style)
