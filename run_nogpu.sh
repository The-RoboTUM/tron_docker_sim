#!/bin/bash
xhost +local:docker

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

docker run -it --rm \
    --name ros2_sim \
    --env DISPLAY=$DISPLAY \
    --env QT_X11_NO_MITSHM=1 \
    --env LIBGL_ALWAYS_SOFTWARE=1 \
    --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --volume "$SCRIPT_DIR/ros2_ws/src:/ros2_ws/src" \
    --volume ros2_build:/ros2_ws/build \
    --volume ros2_install:/ros2_ws/install \
    --network host \
    ros2_humble_sim
