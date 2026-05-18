from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from launch import LaunchDescription

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

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription([
    move_group_node
])
