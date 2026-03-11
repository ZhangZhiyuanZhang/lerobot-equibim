from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

import json

# ===================== Basic Settings =====================
FPS = 30

# ===================== Camera =====================
camera_config = {
    "front": OpenCVCameraConfig(index_or_path=0, width=640, height=480, fps=FPS)
}

# ===================== Robot Config =====================
robot_config = SO101FollowerConfig(
    port="/dev/ttyACM0",
    id="follower",
    # cameras=camera_config
)

robot = SO101Follower(robot_config)

robot.connect()
input("Robot is now at the home pose. Press ENTER to save the home pose.")

obs = robot.get_observation()
home_action = {k: v for k, v in obs.items() if k.endswith(".pos")}

with open("single_arm_home.json", "w") as f:
    json.dump(home_action, f, indent=2)

print("Saved single_arm_home.json")
robot.disconnect()