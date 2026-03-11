from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.diffusion.modeling_diffusion import DiffusionPolicy
from lerobot.policies.factory import make_pre_post_processors

from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

from lerobot.scripts.lerobot_record import record_loop
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import init_rerun
from lerobot.processor import make_default_processors

import json
import time

with open("single_arm_home.json") as f:
    HOME_ACTION = json.load(f)

def open_gripper(home_action):
    ha = home_action.copy()
    ha["gripper.pos"] = 50.0
    return ha

def reset_robot(robot, home_action, steps=100):
    for _ in range(steps):
        robot.send_action(home_action)
        time.sleep(0.04)  # 25Hz

# ===================== Basic Settings =====================
NUM_EPISODES = 20
FPS = 30
EPISODE_TIME_SEC = 30
TASK_DESCRIPTION = "Pick and Place"

# local checkpoint path
LOCAL_CKPT_PATH = "/home/zhiyuan/Project/lerobot/outputs/train_act_test/checkpoints/last/pretrained_model"
HF_DATASET_ID = "zhiyuan/eval_pick_place"

# ===================== Camera =====================
camera_config = {
    "front": OpenCVCameraConfig(index_or_path=0, width=640, height=480, fps=FPS)
}

# ===================== Robot Config =====================
robot_config = SO101FollowerConfig(
    port="/dev/ttyACM0",
    id="follower",
    cameras=camera_config
)

robot = SO101Follower(robot_config)

# ===================== Load Policy =====================
policy = ACTPolicy.from_pretrained(LOCAL_CKPT_PATH)
# policy = DiffusionPolicy.from_pretrained(LOCAL_CKPT_PATH)

# ===================== Dataset Features =====================
action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

dataset = LeRobotDataset.create(
    repo_id=HF_DATASET_ID,
    fps=FPS,
    features=dataset_features,
    robot_type=robot.name,
    use_videos=True,
    image_writer_threads=4,
)

# ===================== UI =====================
_, events = init_keyboard_listener()
init_rerun(session_name="single_inference")

# ===================== Connect =====================
robot.connect()

# ===================== Pre/Post Processors =====================
preprocessor, postprocessor = make_pre_post_processors(
    policy_cfg=policy,
    pretrained_path=LOCAL_CKPT_PATH,
    dataset_stats=dataset.meta.stats,
)

teleop_action_processor, robot_action_processor, robot_observation_processor = make_default_processors()

# ===================== Inference Loop =====================
for episode_idx in range(NUM_EPISODES):
    log_say(f"Episode {episode_idx + 1}")

    record_loop(
        robot=robot,
        events=events,
        fps=FPS,
        policy=policy,
        teleop_action_processor=teleop_action_processor,
        robot_action_processor=robot_action_processor,
        robot_observation_processor=robot_observation_processor,
        preprocessor=preprocessor,
        postprocessor=postprocessor,
        dataset=dataset,
        control_time_s=EPISODE_TIME_SEC,
        single_task=TASK_DESCRIPTION,
        display_data=False,
    )

    dataset.save_episode()

    reset_robot(robot, open_gripper(HOME_ACTION), steps=50)
    reset_robot(robot, HOME_ACTION, steps=100)

# ===================== Cleanup =====================
robot.disconnect()