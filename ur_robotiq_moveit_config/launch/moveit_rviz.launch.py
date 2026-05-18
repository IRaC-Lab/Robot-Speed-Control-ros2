from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():

    moveit_config = (
        MoveItConfigsBuilder("ur3e_robotiq", package_name="ur_robotiq_moveit_config")
        .robot_description(
            file_path="/home/jy/colcon_ws/src/ur_gripper_gazebo/urdf/ur3e_robotiq_2f_85_urdf.xacro",
            mappings={
                "sim_gazebo": "true",
                "simulation_controllers": "/home/jy/colcon_ws/src/ur_gripper_gazebo/config/ur3e_robotiq_controllers.yaml",
            },
        )
        .robot_description_semantic(file_path="config/ur3e_robotiq.srdf")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .to_moveit_configs()
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=[
            "-d",
            "/home/jy/colcon_ws/src/ur_robotiq_moveit_config/config/moveit.rviz",
        ],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription([
        rviz_node
    ])
