import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    rviz_config = get_package_share_directory('sim_bringup') + '/rviz/warehouse.rviz'

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Launch RViz2',
    )

    stand_arg = DeclareLaunchArgument(
        'stand',
        default_value='false',
        description='If true, the robot stands automatically on start. If false, it waits for the /start_stand service.',
    )

    lidar_viz_arg = DeclareLaunchArgument(
        'lidar_viz',
        default_value='false',
        description='Enable LiDAR ray visualization in Gazebo.',
    )

    # Use the warehouse world file
    world_file = os.path.join(
        FindPackageShare('aws_robomaker_small_warehouse_world').find('aws_robomaker_small_warehouse_world'),
        'worlds',
        'small_warehouse',
        'small_warehouse.world'
    )

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('robot_hw'), '/launch/pointfoot_hw_sim.launch.py'
        ]),
        launch_arguments={
            'gui': 'false',
            'stand': LaunchConfiguration('stand'),
            'lidar_viz': LaunchConfiguration('lidar_viz'),
            'world_file' : world_file
        }.items(),
    )

    # gzclient launched without the EOL plugin that causes crashes
    gzclient = TimerAction(
        period=5.0,
        actions=[ExecuteProcess(cmd=['gzclient'], output='screen')]
    )

    rviz = TimerAction(
        period=5.0,
        actions=[Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
            condition=IfCondition(LaunchConfiguration('rviz')),
        )]
    )

    odom_tf_broadcaster = Node(
        package='sim_bringup',
        executable='odom_tf_broadcaster',
        output='screen',
    )

    load_controllers = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    return LaunchDescription([
        rviz_arg,
        stand_arg,
        lidar_viz_arg,
        sim,
        gzclient,
        rviz,
        odom_tf_broadcaster,
        load_controllers,
    ])
