from lerobot.teleoperators.so_leader import SO101LeaderConfig, SO101Leader
from lerobot.robots.so_follower import SO101FollowerConfig, SO101Follower
from lerobot.teleoperators.bi_so_leader import BiSOLeader, BiSOLeaderConfig
from lerobot.robots.bi_so_follower import BiSOFollower, BiSOFollowerConfig
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig

camera_config = {
    "head": OpenCVCameraConfig(index_or_path=0, width=640, height=480, fps=30)
}

left_teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM0",
    id="left_leader",
)

right_teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM1",
    id="left_leader",
)

left_robot_config = SO101FollowerConfig(
    port="/dev/ttyACM2",
    id="left_follower",
    cameras=camera_config
)

right_robot_config = SO101FollowerConfig(
    port="/dev/ttyACM3",
    id="right_follower",
)

bi_teleop_config = BiSOLeaderConfig(left_teleop_config, right_teleop_config, id="leader")
bi_robot_config = BiSOFollowerConfig(left_robot_config, right_robot_config, id="follower")

robot = BiSOFollower(bi_robot_config)
teleop_device = BiSOLeader(bi_teleop_config)
robot.connect()
teleop_device.connect()

while True:
    observation = robot.get_observation()
    action = teleop_device.get_action()
    robot.send_action(action)