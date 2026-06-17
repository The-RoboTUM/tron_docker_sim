#!/bin/bash

SCRIPT_DIR = "$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$SCRIPT_DIR/limx_ws"

git clone https://github.com/limxdynamics/limxsdk-lowlevel.git
git clone https://github.com/limxdynamics/robot-description.git
git clone https://github.com/limxdynamics/robot-visualization.git
git clone -b feature/hubmle https://github.com/limxdynamics/tron1-gazebo-ros2.git
git clone -b feature/humble https://github.com/limxdynamics/tron1-rl-deploy-ros2.git