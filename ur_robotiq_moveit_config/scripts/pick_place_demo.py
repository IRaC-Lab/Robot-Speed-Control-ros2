#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node
from pymoveit2 import MoveIt2
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import Float64MultiArray, Float32

class PickPlaceDemo(Node):
    def __init__(self):
        super().__init__("pick_place_demo")
        self.callback_group = ReentrantCallbackGroup()

        self.arm = MoveIt2(
            node=self,
            joint_names=[
                "ur3e_shoulder_pan_joint",
                "ur3e_shoulder_lift_joint",
                "ur3e_elbow_joint",
                "ur3e_wrist_1_joint",
                "ur3e_wrist_2_joint",
                "ur3e_wrist_3_joint",
            ],
            base_link_name="ur3e_base_link",
            end_effector_name="ur3e_tool0",
            group_name="arm",
            callback_group=self.callback_group,
        )

        self.gripper_pub = self.create_publisher(
            Float64MultiArray,
            "/gripper_controller/commands",
            10
        )
        
        self.scaling_sub = self.create_subscription(
            Float32,
            "/scaling_factor",
            self.scaling_callback,
            10
        )

        self.arm.max_velocity = 0.3
        self.arm.max_acceleration = 0.3
        self.gripper_q = 0.0

    def deg_list(self, values):
        return [math.radians(v) for v in values]
        
    def scaling_callback(self, msg):
        scaling_factor = float(msg.data)
        
        self.arm.max_velocity = scaling_factor
        self.arm.max_acceleration = scaling_factor

    def move_arm(self, joint_deg, name=""):
        self.get_logger().info(f"Move arm: {name}")
        joint_rad = self.deg_list(joint_deg)

        self.arm.move_to_configuration(joint_rad)
        self.arm.wait_until_executed()

        time.sleep(0.5)

    def send_gripper_smooth(self, target_q, steps=25, delay=0.03):
        start_q = self.gripper_q

        for i in range(steps + 1):
            ratio = i / steps
            q = start_q + (target_q - start_q) * ratio

            msg = Float64MultiArray()
            msg.data = [q, -q, q, -q, -q, q]
            self.gripper_pub.publish(msg)
            time.sleep(delay)

        self.gripper_q = target_q

    def gripper_open(self):
        self.get_logger().info("Gripper open")
        self.send_gripper_smooth(0.0, steps=25, delay=0.03)

    def gripper_close(self):
        self.get_logger().info("Gripper close")
        self.send_gripper_smooth(0.65, steps=25, delay=0.03)

    def move_init(self):
        self.move_arm([0, -90, 0, -90, 0, 0], "init")

    def waypoint_1(self):
        self.move_arm([-58, -137, -27, -107, 91, 32], "pick above")

    def waypoint_2(self):
        self.move_arm([-58, -207, 68, -132, 91, 32], "pick position")

    def waypoint_3(self):
        self.move_arm([-95, -166, 33, -137, 90, -5], "place above")

    def waypoint_4(self):
        self.move_arm([-95, -207, 68, -133, 90, -5], "place position")

    def run_pick_place(self):
        count = 1
        
        self.move_init()
        self.gripper_open()

        while rclpy.ok():

	    # pick -> place
            self.waypoint_1()
            self.waypoint_2()
            self.gripper_close()
            self.waypoint_1()

            self.waypoint_3()
            self.waypoint_4()
            self.gripper_open()
            self.waypoint_3()

            # place -> pick
            self.waypoint_3()
            self.waypoint_4()
            self.gripper_close()
            self.waypoint_3()

            self.waypoint_1()
            self.waypoint_2()
            self.gripper_open()
            self.waypoint_1()
            
            count += 1
            time.sleep(0.5)


def main():
    rclpy.init()
    node = PickPlaceDemo()

    try:
        node.run_pick_place()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
