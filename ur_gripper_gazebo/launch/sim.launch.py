import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_name = "ur_gripper_gazebo"
    pkg_share = get_package_share_directory(pkg_name)

    world_path = os.path.join(pkg_share, "worlds", "IRAC_2.world")

    d435_xacro_path = os.path.join(
        pkg_share,
        "urdf",
        "d435_camera.xacro"
    )

    d435_urdf_path = "/tmp/d435_camera.urdf"

    ur3_launch_path = os.path.join(
        pkg_share,
        "launch",
        "ur3e_robotiq_gazebo.launch.py"
    )

    gazebo = ExecuteProcess(
        cmd=[
            "gazebo",
            "--verbose",
            "-s", "/opt/ros/humble/lib/libgazebo_ros_init.so",
            "-s", "/opt/ros/humble/lib/libgazebo_ros_factory.so",
            world_path
        ],
        output="screen"
    )

    ur3_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(ur3_launch_path)
    )

    convert_d435_xacro = ExecuteProcess(
        cmd=[
            "ros2", "run", "xacro", "xacro",
            d435_xacro_path,
            "-o", d435_urdf_path
        ],
        output="screen"
    )

    spawn_d435 = ExecuteProcess(
        cmd=[
            "ros2", "run", "gazebo_ros", "spawn_entity.py",
            "-entity", "d435_cameras",
            "-file", d435_urdf_path
        ],
        output="screen"
    )

    return LaunchDescription([
        gazebo,

        TimerAction(
            period=3.0,
            actions=[
                ur3_launch
            ]
        ),

        TimerAction(
            period=6.0,
            actions=[
                convert_d435_xacro
            ]
        ),

        TimerAction(
            period=8.0,
            actions=[
                spawn_d435
            ]
        ),
    ])
