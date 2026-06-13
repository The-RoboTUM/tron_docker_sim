#!/bin/bash
xhost +local:docker

docker run -it --rm \
    --name ros2_sim \
    --runtime=nvidia \
    --gpus all \
    --env DISPLAY=$DISPLAY \
    --env QT_X11_NO_MITSHM=1 \
    --env NVIDIA_DRIVER_CAPABILITIES=all \
    --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --volume "$(pwd)/ros2_ws:/ros2_ws/src" \
    --network host \
    ros2_humble_sim
