from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.teleoperators.so_leader import SO101LeaderConfig
from lerobot.robots.so_follower import SO101FollowerConfig
from lerobot.teleoperators.bi_so_leader import BiSOLeader, BiSOLeaderConfig
from lerobot.robots.bi_so_follower import BiSOFollower, BiSOFollowerConfig
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import init_rerun
from lerobot.scripts.lerobot_record import record_loop
from lerobot.processor import make_default_processors

# ===================== Basic Settings =====================
NUM_EPISODES = 50
FPS = 30
EPISODE_TIME_SEC = 20
RESET_TIME_SEC = 5
TASK_DESCRIPTION = "Bimanual Hanging"

# ===================== Camera =====================
camera_config = {
    "head": OpenCVCameraConfig(index_or_path=0, width=640, height=480, fps=FPS)
}

# ===================== Teleop Config =====================
left_teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM0",
    id="left_leader",
)

right_teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM1",
    id="right_leader",
)

bi_teleop_config = BiSOLeaderConfig(
    left_teleop_config,
    right_teleop_config,
    id="leader"
)

# ===================== Robot Config =====================
left_robot_config = SO101FollowerConfig(
    port="/dev/ttyACM2",
    id="left_follower",
    cameras=camera_config
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

# ===================== Init Robot & Teleop =====================
robot = BiSOFollower(bi_robot_config)
teleop = BiSOLeader(bi_teleop_config)

# ===================== Dataset Features (自动适配双臂) =====================
action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

dataset = LeRobotDataset.create(
    repo_id="ZhiyuanZhangZhiyuan/lerobot_hanging",
    fps=FPS,
    features=dataset_features,
    robot_type=robot.name,
    use_videos=True,
    image_writer_threads=4,
    metadata_buffer_size=10,
)

# ===================== UI & Processors =====================
_, events = init_keyboard_listener()
init_rerun(session_name="bi_recording")

robot.connect()
teleop.connect()

teleop_action_processor, robot_action_processor, robot_observation_processor = make_default_processors()

# ===================== Record Loop =====================
episode_idx = 0
while episode_idx < NUM_EPISODES and not events["stop_recording"]:
    log_say(f"Episode {episode_idx + 1}")
    print(f"Episode {episode_idx + 1}")

    record_loop(
        robot=robot,
        events=events,
        fps=FPS,
        teleop_action_processor=teleop_action_processor,
        robot_action_processor=robot_action_processor,
        robot_observation_processor=robot_observation_processor,
        teleop=teleop,
        dataset=dataset,
        control_time_s=EPISODE_TIME_SEC,
        single_task=TASK_DESCRIPTION,
        display_data=False,
    )

    if not events["stop_recording"] and (episode_idx < NUM_EPISODES - 1 or events["rerecord_episode"]):
        log_say("Reset the environment")
        record_loop(
            robot=robot,
            events=events,
            fps=FPS,
            teleop_action_processor=teleop_action_processor,
            robot_action_processor=robot_action_processor,
            robot_observation_processor=robot_observation_processor,
            teleop=teleop,
            control_time_s=RESET_TIME_SEC,
            single_task=TASK_DESCRIPTION,
            display_data=False,
        )

    if events["rerecord_episode"]:
        log_say("Re-recording episode")
        events["rerecord_episode"] = False
        events["exit_early"] = False
        dataset.clear_episode_buffer()
        continue

    dataset.save_episode()
    episode_idx += 1

# ===================== Cleanup =====================
log_say("Stop recording")
robot.disconnect()
teleop.disconnect()
