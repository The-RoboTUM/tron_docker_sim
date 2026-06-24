# ROS2 Package: TRON1 Docker Sim

This repository contains the Dockerfile, bash scripts and ROS2 package necessary to easily get the Tron1 Gazebo simulation running on a container, with X11 forwarding for GUI. The instructions here assume that the user is running them from an Ubuntu (or other Linux distro) system.

### Step 0: Have Docker

If not installed already, go ahead and get Docker from [here](https://docs.docker.com/engine/install/ubuntu/). Verify that it has been installed:

```[bash]
docker run hello-world
```

If asked for sudo privileges, I would recommend adding your user to a docker group to run docker commands without the need of sudo. You can check how to do it [here](https://docs.docker.com/engine/install/linux-postinstall/).

### Step 1: Build the Docker Image

On a terminal standing on the cloned repository

```
cd ~/tron_docker_sim # or wherever you cloned it
```

run the following command to build the image (will give it the name `ros2_humble_sim`:

```[bash]
docker build -t ros2_humble_sim .
```

The process might take a few minutes, but it only needs to be done once (unless changes are made to the Dockerfile).

### Step 2: Make the scripts executable

The bash scripts included in this repo make the process of running an instance of the container easier. They should be executable already, but if they don't work do (e.g. for run_gpu.sh):

```[bash]
chmod +x run_gpu.sh
```

## Step 3: Clone the limx sources

### Step 4: Run the container

There are two ways to run the container: with and without GPU. Running it with GPU (if available in host machine) makes the simulation go considerably smoother. However, this requires the user to have installed on the host machine the container toolkit (assuming Nvidia GPU).

(optional) Make the `install_nvidia_toolkit.sh` script executable and run it. Disclaimer: This script was only tested on a 24.04 machine with Nvidia Toolkit and drivers already installed.
```[bash]
chmod +x install_nvidia_toolkit.sh && ./install_nvidia_toolkit.sh
```

Then, you can decide whether you want to run the container on CPU or GPU:

```[bash]
./run_gpu.sh
```

or

```[bash]
./run_nogpu.sh
```

The terminal should now be inside of the container, and we are ready to launch the simulation.

### Step 5: Running the simulation

The included ROS2 Package `sim_bringup` includes a launch file which lets us easily launch the simulation. Because of some Docker shenanigans, a gzclient needs to be launched a couple of seconds after Gazebo to get the GUI. All the ROS2 packages are already sourced, so don't worry about doing so.

```[bash]
ros2 launch sim_bringup sim.launch.py
```

The simulation should start and you should get a window with Gazebo and the robot. Additionally, you can also get a window running Rviz2 by adding one additional argument:

```[bash]
ros2 launch sim_bringup sim.launch.py rviz:=true
```

## Step 6: Making the robot stand up

By default, the robot will spawn crouching down in a newly added `:IDLE:`state. In order to get it to stand up, the `/start_stand` service needs to be called on a new terminal on the same docker instance (see next section)

```[bash]
ros2 service call /start_stand std_srvs/srv/Trigger {}
```

Alternativelly, an additional argument can be added to the launch file to make it so the robot stands on its own as soon as the simulation begins:

```[bash]
ros2 launch sim_bringup sim.launch.py stand:=true
```

### Executing additional instances of the same container

If you need a second terminal inside of the container, getting one is straightforward. On a new terminal, simply run:

```[bash]
docker exec -it ros2_sim bash
```
