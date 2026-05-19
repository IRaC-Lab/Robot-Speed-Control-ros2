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
        self.current_scaling_factor = 1.0
        
        self.current_target_joint_deg = None
        self.current_target_name = ""
        self.need_replan = False
        self.current_scaling_factor = 1.0

    def deg_list(self, values):
        return [math.radians(v) for v in values]
        
    def scaling_callback(self, msg):
        new_scaling = float(msg.data)
        new_scaling = max(0.01, min(new_scaling, 1.0))

        old_scaling = self.current_scaling_factor
        self.current_scaling_factor = new_scaling

        self.arm.max_velocity = new_scaling
        self.arm.max_acceleration = new_scaling

        self.get_logger().info(
            f"scaling_factor: {new_scaling}"
        )

        if abs(new_scaling - old_scaling) > 0.001:
            self.need_replan = True

            try:
                self.arm.cancel_execution()

            except Exception as e:
                self.get_logger().warn(
                    f"cancel_execution failed: {e}"
                )

    def move_arm(self, joint_deg, name=""):
        self.current_target_joint_deg = joint_deg
        self.current_target_name = name

        while rclpy.ok():
            self.need_replan = False

            rclpy.spin_once(self, timeout_sec=0.1)

            self.get_logger().info(
                f"Move arm: {name}, velocity={self.arm.max_velocity}"
            )

            joint_rad = self.deg_list(joint_deg)

            self.arm.move_to_configuration(joint_rad)
            self.arm.wait_until_executed()

            rclpy.spin_once(self, timeout_sec=0.1)

            if self.need_replan:
                self.get_logger().info(
                    f"Replanning same waypoint: {name}"
                )
                continue

            break

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
        self.num = 0

        self.move_init()
        self.gripper_open()

        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)

            self.num += 1

            if self.num == 1:
                self.waypoint_1()

            elif self.num == 2:
                self.waypoint_2()

            elif self.num == 3:
                self.gripper_close()
                time.sleep(1.0)

            elif self.num == 4:
                self.waypoint_1()

            elif self.num == 5:
                self.waypoint_3()

            elif self.num == 6:
                self.waypoint_4()

            elif self.num == 7:
                self.gripper_open()
                time.sleep(1.0)

            elif self.num == 8:
                self.waypoint_3()

            elif self.num == 9:
                self.waypoint_3()

            elif self.num == 10:
                self.waypoint_4()

            elif self.num == 11:
                self.gripper_close()
                time.sleep(1.0)

            elif self.num == 12:
                self.waypoint_3()

            elif self.num == 13:
                self.waypoint_1()

            elif self.num == 14:
                self.waypoint_2()

            elif self.num == 15:
                self.gripper_open()
                time.sleep(1.0)

            elif self.num == 16:
                self.waypoint_1()

            elif self.num == 17:
                self.num = 0

            self.get_logger().info(f"current_num: {self.num}")
            rclpy.spin_once(self, timeout_sec=0.1)
            time.sleep(0.1)


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
