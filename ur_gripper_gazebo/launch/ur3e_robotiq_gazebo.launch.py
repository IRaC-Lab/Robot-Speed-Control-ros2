import os
import xacro

from launch import LaunchDescription
from launch.actions import TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessExit

from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    xacro_file = os.path.join(
        get_package_share_directory('ur_gripper_gazebo'),
        'urdf',
        'ur3e_robotiq_2f_85_urdf.xacro'
    )

    controllers_file = os.path.join(
        get_package_share_directory('ur_gripper_gazebo'),
        'config',
        'ur3e_robotiq_controllers.yaml'
    )

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc, mappings={
        'sim_gazebo': 'true',
        'simulation_controllers': controllers_file,
    })

    def remove_comments(node):
        for child in list(node.childNodes):
            if child.nodeType == child.COMMENT_NODE:
                node.removeChild(child)
            else:
                remove_comments(child)

    remove_comments(doc)

    robot_description = {
        'robot_description': doc.documentElement.toxml()
    }

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description, {'use_sim_time': True}],
        output='screen'
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'ur3e_robotiq',
            '-topic', 'robot_description',
            '-x', '-1.21',
            '-y', '1.97',
            '-z', '0.8',
            '-Y', '-1.57'
        ],
        output='screen'
    )
    
    delayed_spawn_entity = TimerAction(
        period=5.0,
        actions=[spawn_entity]
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '-c', '/controller_manager'],
        output='screen'
    )

    joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller', '-c', '/controller_manager'],
        output='screen'
    )
    
    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller', '-c', '/controller_manager'],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        delayed_spawn_entity,

        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_entity,
                on_exit=[joint_state_broadcaster_spawner]
            )
        ),

        RegisterEventHandler(
            OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[joint_trajectory_controller_spawner]
            )
        ),
        
        RegisterEventHandler(
            OnProcessExit(
            target_action=joint_trajectory_controller_spawner,
            on_exit=[gripper_controller_spawner]
            )
        ),
    ])
