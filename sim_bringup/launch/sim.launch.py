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
    rviz_config = get_package_share_directory('robot_visualization') + '/rviz/pointfoot.rviz'

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Launch RViz2',
    )

    controller_delay_arg = DeclareLaunchArgument(
        'controller_delay',
        default_value='10.0',
        description='Seconds to wait before loading joint_state_broadcaster',
    )

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
            condition=IfCondition(LaunchConfiguration('rviz')),
        )]
    )

    load_controllers = TimerAction(
        period=LaunchConfiguration('controller_delay'),
        actions=[ExecuteProcess(
            cmd=['bash', '-c',
                 'ros2 param set /controller_manager joint_state_broadcaster.type '
                 'joint_state_broadcaster/JointStateBroadcaster && '
                 'ros2 control load_controller --set-state active joint_state_broadcaster'],
            output='screen',
        )]
    )

    return LaunchDescription([
        rviz_arg,
        controller_delay_arg,
        sim,
        gzclient,
        rviz,
        load_controllers,
    ])
