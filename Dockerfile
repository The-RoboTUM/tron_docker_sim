FROM osrf/ros:humble-desktop-full

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Install Gazebo + RViz + common ROS2 tooling
RUN apt-get update && apt-get install -y \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    ros-humble-rviz2 \
    ros-humble-rqt \
    ros-humble-rqt-common-plugins \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    python3-colcon-common-extensions \
    python3-rosdep \
    git \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Limx Dependencies
RUN apt-get update && apt-get install -y \
    ros-humble-urdf \
    ros-humble-urdfdom \
    ros-humble-urdfdom-headers \
    ros-humble-kdl-parser \
    ros-humble-hardware-interface \
    ros-humble-controller-manager \
    ros-humble-controller-interface \
    ros-humble-controller-manager-msgs \
    ros-humble-control-msgs \
    ros-humble-controller-interface \
    ros-humble-gazebo-* \
    ros-humble-rviz* \
    ros-humble-rqt-gui \
    ros-humble-rqt-robot-steering \
    ros-humble-plotjuggler* \
    ros-humble-control-toolbox \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-robot-localization \
    ros-dev-tools \
    cmake build-essential libpcl-dev libeigen3-dev libopencv-dev libmatio-dev \
    python3-pip libboost-all-dev libtbb-dev liburdfdom-dev liborocos-kdl-dev \
    nano -y

# onnxruntime Depenency
RUN wget https://github.com/microsoft/onnxruntime/releases/download/v1.10.0/onnxruntime-linux-x64-1.10.0.tgz && \
    tar xvf onnxruntime-linux-x64-1.10.0.tgz && \
    cp -a onnxruntime-linux-x64-1.10.0/include/* /usr/include && \
    cp -a onnxruntime-linux-x64-1.10.0/lib/* /usr/lib && \
    rm -rf onnxruntime-linux-x64-1.10.0 onnxruntime-linux-x64-1.10.0.tgz


# Set up the workspace
RUN mkdir -p /ros2_ws/src
WORKDIR /ros2_ws

# Set up Limx workspace
RUN cd /ros2_ws/src && \
    git clone https://github.com/limxdynamics/limxsdk-lowlevel.git && \
    git clone -b feature/humble https://github.com/The-RoboTUM/tron1-gazebo-ros2.git && \
    git clone https://github.com/The-RoboTUM/robot-description.git && \
    git clone https://github.com/limxdynamics/robot-visualization.git && \
    git clone -b feature/humble https://github.com/The-RoboTUM/tron1-rl-deploy-ros2.git

# sim_bringup is our own package, baked in directly (overridden by the runtime bind mount)
COPY ros2_ws/src/sim_bringup/ /ros2_ws/src/sim_bringup/

# Compile the whole workspace
RUN /bin/bash -c "cd /ros2_ws && source /opt/ros/humble/setup.bash && colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release"

# Fix mesh URIs: add file:// prefix so both Gazebo and RViz2 can load them
RUN find /ros2_ws/install/robot_description -name "*.xacro" | \
    xargs sed -i 's|<mesh filename="$(find robot_description)|<mesh filename="file://$(find robot_description)|g'

# Fix mrosbridger IP for simulation
RUN find /ros2_ws/install/robot_visualization -name "*.launch.py" | \
    xargs sed -i "s|os.environ\['MROS_AGENT_IP'\] = '10.192.1.2'|os.environ\['MROS_AGENT_IP'\] = '127.0.0.1'|g"

# Source ROS2 on every shell
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc
RUN echo "[ -f /ros2_ws/install/setup.bash ] && source /ros2_ws/install/setup.bash" >> /root/.bashrc

# Select Robot Type and RL Type
ENV ROBOT_TYPE=WF_TRON1A
ENV RL_TYPE=isaacgym
RUN echo "export ROBOT_TYPE=WF_TRON1A" >> /root/.bashrc
RUN echo "export RL_TYPE=isaacgym" >> /root/.bashrc

# Get more Gazebo assets (this is 1GB! If rebuilding often, better to install it on host and do a volume mount instead!)
RUN git clone https://github.com/osrf/gazebo_models ~/.gazebo/models

# X11 display for GUI apps (Gazebo, RViz)
ENV DISPLAY=:0

CMD ["/bin/bash"]
