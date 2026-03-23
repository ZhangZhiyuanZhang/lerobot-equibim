# EquiBim: Learning Symmetry-Equivariant Policy for Bimanual Manipulation

[Paper](https://arxiv.org/abs/2603.08541) |
[Video](https://drive.google.com/file/d/1VZJ6U43vMfH2eT5yAYKibg7k1hce5Wp5/view?usp=drive_link)  
<a href="https://zhangzhiyuanzhang.github.io/personal_website/">Zhiyuan Zhang</a><sup>1</sup>, 
<a href="">Aditya Mohan</a><sup>1</sup>, 
<a href="">Seungho Han</a><sup>1</sup>, 
<a href="https://showone90.wixsite.com/show">Wan Shou</a><sup>2</sup>, 
<a href="https://dw-bioag.github.io/safelab/">Dongyi Wang</a><sup>2</sup>, 
<a href="https://www.purduemars.com/">Yu She</a><sup>1</sup>  

<sup>1</sup> Purdue University, <sup>2</sup> University of Arkansas


![](media/readme/teaser.gif)

#### This repository builds upon the real-world robotic platform provided by LeRobot and extends it to bimanual manipulation with symmetry-equivariant policy learning.

## Installation
1. Install [Miniforge](https://github.com/conda-forge/miniforge)
    ```bash
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh
    bash Miniforge3-$(uname)-$(uname -m).sh
    source ~/.bashrc
    ```

1. Install environment:
    ```bash
    conda create -y -n lerobot python=3.12
    conda activate lerobot
    ```
    When using conda, install ffmpeg in your environment:
    ```bash
    conda install ffmpeg -c conda-forge
    ffmpeg -version
    ```

1. Clone this repo
    First, clone the repository and navigate into the directory:
    ```bash
    git clone https://github.com/ZhangZhiyuanZhang/lerobot-equibim.git
    cd lerobot-equibim
    ```

    Then, install the library in editable mode:
    ```bash
    pip install -e .
    pip install -e ".[feetech]"  # Required for real robot support (e.g., motor control, calibration)
    ```

2. Experiment Tracking:
    To use [Weights and Biases](https://docs.wandb.ai/models/quickstart) for experiment tracking, log in with
    ```bash
    wandb login
    ```

![](img/Pipeline.svg)


## Quick Guide: From Single-Arm to Bimanual Data Collection, Training, and Evaluation

### Single-Arm Setup

1. **Motor Calibration**

    To find the port for each bus servo adapter, connect the MotorBus to your computer via USB and power. Run the following script and disconnect the MotorBus when prompted:

    ```bash
    lerobot-find-port
    ```

    Example output:

    ```bash
    Finding all available ports for the MotorBus.
    ['/dev/ttyACM0', '/dev/ttyACM1']
    Remove the usb cable from your MotorsBus and press Enter when done.

    [...Disconnect corresponding leader or follower arm and press Enter...]

    The port of this MotorsBus is /dev/ttyACM1
    Reconnect the USB cable.
    ```

    On Linux, you might need to grant access to the USB ports:

    ```bash
    sudo chmod 666 /dev/ttyACM0
    sudo chmod 666 /dev/ttyACM1
    ```

    In my case, the port of the **follower arm** is `/dev/ttyACM0`, and the port of the **leader arm** is `/dev/ttyACM1`.

    Next, you need to calibrate the robot to ensure that the leader and follower arms produce the same position values when they are at the same physical configuration. This calibration step is important because it allows a neural network trained on one robot to generalize to another.

    Run the following command to calibrate the **follower arm**:

    ```bash
    lerobot-calibrate \
        --robot.type=so101_follower \
        --robot.port=/dev/ttyACM0 \
        --robot.id=follower
    ```

    First move the robot so that all joints are roughly in the middle of their ranges. After pressing Enter, move each joint through its full range of motion.

    The calibration file will be saved to:

    ```bash
    ${HOME}/.cache/huggingface/lerobot/calibration/robots/so_follower/follower.json
    ```

    Repeat the same procedure for the **leader arm**:

    ```bash
    lerobot-calibrate \
        --teleop.type=so101_leader \
        --teleop.port=/dev/ttyACM1 \
        --teleop.id=leader
    ```

    The calibration file will be saved to:

    ```bash
    ${HOME}/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/leader.json
    ```

---

2. **Teleoperation**

    The robot `id` is used to store the calibration file. It is important to use the same `id` when teleoperating, recording, and evaluating with the same setup.

    Run:

    ```bash
    python single_arm_teleop.py
    ```

    The follower arm will mirror the movements of the leader arm.

---

3. **Teleoperation with Camera**

    Each camera requires a unique identifier so that multiple devices can be distinguished.

    `OpenCVCamera` and `RealSenseCamera` support automatic discovery. Run:

    ```bash
    lerobot-find-cameras opencv
    ```

    Example output:

    ```bash
    --- Detected Cameras ---
    Camera #0:
    Name: OpenCV Camera @ 0
    Type: OpenCV
    Id: 0
    Backend api: AVFOUNDATION
    Default stream profile:
        Format: 16.0
        Width: 1920
        Height: 1080
        Fps: 15.0
    --------------------
    (more cameras ...)
    ```

    After identifying your camera, test it with:

    ```bash
    python test_camera.py
    ```

    Then run teleoperation with camera input:

    ```bash
    python single_arm_teleop_camera.py
    ```

    The provided example uses a single camera as input.

---

4. **Record a Dataset**

    Before recording your dataset, make sure to update the `<username>` field in the Python scripts to match your Hugging Face username or local dataset namespace.

    Replace `<username>` with your own username (e.g., `alice`, `bob`, etc.).  
    You should also update the corresponding `<username>` field in the Python scripts if needed.

    Once you are familiar with teleoperation, you can record your first dataset.

    Before recording, delete any existing dataset with the same name:

    ```bash
    rm -rf ${HOME}/.cache/huggingface/lerobot/<username>/record-test
    ```

    The provided example records **30 episodes** for a pick-and-place task:

    ```bash
    python single_arm_data_collection.py
    ```

    You can modify the parameters in the script based on your needs.

    The dataset will be stored locally at:

    ```bash
    ${HOME}/.cache/huggingface/lerobot/<username>/record-test
    ```

---

5. **Train a Policy**

    Before training, remove any previous outputs with the same name:

    ```bash
    rm -rf ${HOME}/Project/lerobot/outputs/train_act_test
    ```

    We use the **ACT policy** for training and set the number of training steps to **200000**:

    ```bash
    bash train_single_arm.sh
    ```

    The checkpoints will be saved to:

    ```bash
    {your_path}/outputs/train_act_test
    ```

---

6. **Run Inference and Evaluate the Policy**

    Remove any existing evaluation dataset:

    ```bash
    rm -rf ${HOME}/.cache/huggingface/lerobot/<username>/eval_so101_test
    ```

    First capture the robot's **home pose**, which the robot will return to after each inference episode:

    ```bash
    python single_arm_capture_home_pose.py
    ```

    After generating the home pose JSON file, run inference:

    ```bash
    python single_arm_inference.py
    ```


### Bimanual Extension
The workflow for **bimanual manipulation** is largely the same as the single-arm setup.  
The main difference is that **two pairs of leader–follower arms** must be calibrated.

First, find the ports for each arm:

```bash
lerobot-find-port
```

Then calibrate the four arms (example):
```bash
lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM0 \
    --teleop.id=left_leader

lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM1 \
    --teleop.id=right_leader

lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM2 \
    --robot.id=left_follower

lerobot-calibrate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM3 \
    --robot.id=right_follower
```
Make sure each arm uses a unique `robot.id`, as calibration files are stored based on this identifier.

After calibration, the remaining workflow is identical to the single-arm pipeline. Simply replace the single_arm_* scripts with their bimanual_* counterparts.

The overall pipeline is:
1. Validate bimanual teleoperation
    ```bash
    python bimanual_teleop.py
    ```
1. Validate bimanual teleoperation with camera
    ```bash
    python bimanual_teleop_camera.py
    ```
1. Collect demonstration data
    ```bash
    python bimanual_data_collection.py
    ```
1. Train a policy
    ```bash
    bash train_bimanual.sh
    ```
1. Capture the robot home pose
    ```bash
    python bimanual_capture_home_pose.py
    ```
1. Run inference
    ```bash
    bimanual_inference.py
    ```

### Leveraging Inherent Symmetry for Bimanual Policies
To enable symmetry-aware learning for bimanual manipulation, we introduce an **equivariance loss** in the ACT policy.

#### Enable Symmetry Loss
First, modify the configuration file: `src/lerobot/policies/act/configuration_act.py`

Change the following line (around line 136):

```python
use_sym_loss: bool = False
```
to
```python
use_sym_loss: bool = True
```
This enables the symmetry loss during training.

#### Implementation Details
The symmetry-aware learning is implemented inside the ACT policy: `src/lerobot/policies/act/modeling_act.py`

The main modifications include:
1. Observation Mirroring Function
    A mirror function is added to transform the observation under the bilateral symmetry transformation.
    See lines 41–89 in `modeling_act.py`.
1. Symmetry Loss
    A symmetry-equivariant loss is introduced to enforce consistent policy predictions under mirrored observations.
    See lines 206–232 in `modeling_act.py`.

#### Training and Inference
After enabling use_sym_loss, the training and evaluation workflow remains the same as described above.

You can directly run:
```bash
bash train_bimanual.sh
```
Then run inference:
```bash
python bimanual_inference.py
```
No additional modifications are required in the training or evaluation pipeline.


## Citation
If you find this work helpful, please cite:

```bibtex
@article{zhang2026equibim,
  title={EquiBim: Learning Symmetry-Equivariant Policy for Bimanual Manipulation},
  author={Zhang, Zhiyuan and Mohan, Aditya and Han, Seungho and Shou, Wan and Wang, Dongyi and She, Yu},
  journal={arXiv preprint arXiv:2603.08541},
  year={2026}
}
```

## License
This repository is released under the MIT license. See [LICENSE](LICENSE) for additional details.

## Acknowledgement
* Our repo is built upon the origional [LeRobot](https://github.com/huggingface/lerobot.git)

