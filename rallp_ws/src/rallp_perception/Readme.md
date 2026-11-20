# 🤖 RALLP OORB Workspace: Perception

---

### Dependencies 

# Perception dependecies
```bash
sudo apt install python3-pip -y
sudo apt install ros-${ROS_DISTRO}-cv-bridge ros-${ROS_DISTRO}-vision-opencv -y
sudo apt install xterm
sudo apt install python3-pygame -y
sudo apt install python3.12-venv
python3 -m venv my_vision_env
source my_vision_env/bin/activate
pip install ultralytics opencv-python
pip install catkin_pkg
pip install empy==3.3.4
pip install lark
pip install "numpy<2" 
```

---

### Person Detection test
```bash
# In a new terminal (after robot is launched)
ros2 run rallp_perception person_detection_node 

# View detections with bounding boxes
ros2 run rqt_image_view rqt_image_view /rallp_0000/camera_0/image_detections

# Move the robot and explore the environment, open a new terminal and run:
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -r __ns:=/rallp_0000

```
### Run Alert system

1. **Launch Gazebo & Spawn Robot:**
```bash
ros2 launch rallp_gz combined_launch.py

```
2. **Run Complete Navigation Stack:**
(Follow steps 2, 3 and 4 from Scenario B Navigation)

3. **Run Person Detection Node:**
```bash
ros2 run rallp_perception person_detection_node	

```
4. **View detections with bounding boxes:**
```bash
ros2 run rqt_image_view rqt_image_view /rallp_0000/camera_0/image_detections

```
5. **Run Security system:**
```bash
ros2 launch rallp_perception security_system.launch.py \
    gmail_sender:=YOUR_ROBOT_GMAIL@gmail.com \
    gmail_password:="xxxx xxxx xxxx xxxx" \
    gmail_recipient:=EMAIL_TO_RECEIVE_ALERTS@gmail.com
```

**What to change:**

| Placeholder | Replace with |
|-------------|-------------|
| `YOUR_ROBOT_GMAIL@gmail.com` | The Gmail account the robot sends FROM |
| `xxxx xxxx xxxx xxxx` | The **App Password** (not your real Gmail password!) |
| `EMAIL_TO_RECEIVE_ALERTS@gmail.com` | Where alerts get sent TO (can be same or different) |

**⚠️ Getting the App Password (required):**

Gmail blocks normal passwords for scripts. You need an App Password:
```
Go to: https://myaccount.google.com/apppasswords
You must have 2FA enabled on the sender Gmail account
**Step 1: Enable 2FA first**
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification"
3. Click it and follow the steps to enable it
   (use your phone number or authenticator app)
**Step 2: Then go back to App Passwords**
1. Go to: https://myaccount.google.com/apppasswords
2. Now it will work
3. Type "RALLP Robot" in the name field
4. Click "Create"
5. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)
6. Paste it in the command above
```

---

