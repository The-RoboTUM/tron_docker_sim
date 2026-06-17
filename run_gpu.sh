#!/bin/bash
xhost +local:docker

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

EXTRA_MOUNTS=""
if [ -d "$SCRIPT_DIR/limx_ws" ]; then
    echo "Found limx_ws — mounting local repositories."
    EXTRA_MOUNTS="\
        --volume $SCRIPT_DIR/limx_ws/tron1-gazebo-ros2:/root/limx_ws/src/tron1-gazebo-ros2 \
        --volume $SCRIPT_DIR/limx_ws/tron1-rl-deploy-ros2:/root/limx_ws/src/tron1-rl-deploy-ros2 \
        --volume $SCRIPT_DIR/limx_ws/robot-description:/root/limx_ws/src/robot-description \
        --volume $SCRIPT_DIR/limx_ws/robot-visualization:/root/limx_ws/src/robot-visualization \
        --volume $SCRIPT_DIR/limx_ws/limxsdk-lowlevel:/root/limx_ws/src/limxsdk-lowlevel \
        --volume limx_build:/root/limx_ws/build \
        --volume limx_install:/root/limx_ws/install"
else
    echo "No limx_ws found — using baked-in image repositories."
fi

docker run -it --rm \
    --name ros2_sim \
    --runtime=nvidia \
    --gpus all \
    --env DISPLAY=$DISPLAY \
    --env QT_X11_NO_MITSHM=1 \
    --env NVIDIA_DRIVER_CAPABILITIES=all \
    --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --volume "$SCRIPT_DIR/ros2_ws:/ros2_ws/src" \
    $EXTRA_MOUNTS \
    --network host \
    ros2_humble_sim
