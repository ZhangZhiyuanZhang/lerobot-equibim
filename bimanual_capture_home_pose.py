from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.diffusion.modeling_diffusion import DiffusionPolicy
from lerobot.policies.factory import make_pre_post_processors

from lerobot.teleoperators.bi_so_leader import BiSOLeader, BiSOLeaderConfig
from lerobot.robots.bi_so_follower import BiSOFollower, BiSOFollowerConfig
from lerobot.robots.so_follower import SO101FollowerConfig
from lerobot.teleoperators.so_leader import SO101LeaderConfig

from lerobot.scripts.lerobot_record import record_loop
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import init_rerun
from lerobot.processor import make_default_processors

# ===================== Basic Settings =====================
NUM_EPISODES = 15
FPS = 30
EPISODE_TIME_SEC = 60
TASK_DESCRIPTION = "Bimanual Handover"


# ===================== Camera =====================
camera_config = {
    "head": OpenCVCameraConfig(index_or_path=0, width=640, height=480, fps=FPS)
}


# ===================== Robot Config =====================
left_robot_config = SO101FollowerConfig(
    port="/dev/ttyACM2",
    id="left_follower",
    # cameras=camera_config
    
)

right_robot_config = SO101FollowerConfig(
    port="/dev/ttyACM3",
    id="right_follower",
)

bi_robot_config = BiSOFollowerConfig(
    left_robot_config,
    right_robot_config,
    id="follower"
)

robot = BiSOFollower(bi_robot_config)

robot.connect()
input("Robot is now at the home pose. Press ENTER to save the home pose.")

obs = robot.get_observation()
home_action = {k: v for k, v in obs.items() if k.endswith(".pos")}

import json
with open("bimanual_home.json", "w") as f:
    json.dump(home_action, f, indent=2)

print("Saved bimanual_home.json")
robot.disconnect()
