import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    rviz_config = get_package_share_directory('robot_visualization') + '/rviz/pointfoot.rviz'

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('robot_hw'), '/launch/pointfoot_hw_sim.launch.py'
        ]),
        launch_arguments={'gui': 'false'}.items(),
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
        )]
    )

    # Load joint_state_broadcaster after sim is fully up (WheelfootController starts at ~6s)
    load_controllers = TimerAction(
        period=15.0,
        actions=[ExecuteProcess(
            cmd=['bash', '-c',
                 'ros2 param set /controller_manager joint_state_broadcaster.type '
                 'joint_state_broadcaster/JointStateBroadcaster && '
                 'ros2 control load_controller --set-state active joint_state_broadcaster'],
            output='screen',
        )]
    )

    return LaunchDescription([
        sim,
        gzclient,
        rviz,
        load_controllers,
    ])
