#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd  "$SCRIPT_DIR/ros2_ws/src"

git clone https://github.com/limxdynamics/limxsdk-lowlevel.git
git clone https://github.com/The-RoboTUM/robot-description.git
git clone https://github.com/limxdynamics/robot-visualization.git
git clone -b feature/humble https://github.com/The-RoboTUM/tron1-gazebo-ros2.git
git clone -b feature/humble https://github.com/The-RoboTUM/tron1-rl-deploy-ros2.git
