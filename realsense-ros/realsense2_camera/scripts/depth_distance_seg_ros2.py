#!/usr/bin/env python3

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image
from std_msgs.msg import Int32MultiArray, Float32
from cv_bridge import CvBridge


class DepthDistanceSegNode(Node):
    def __init__(self):
        super().__init__('depth_and_seg_coord_listener')

        self.bridge = CvBridge()
        self.seg_coords = []
        self.pdr = 0

        image_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.seg_sub = self.create_subscription(
            Int32MultiArray,
            '/seg_coords',
            self.seg_callback,
            10
        )

        self.depth_sub = self.create_subscription(
            Image,
            '/resize_multi_depth_image',
            self.depth_callback,
            image_qos
        )

        self.scaling_pub = self.create_publisher(
            Float32,
            '/scaling_factor',
            10
        )

        self.distance_pub = self.create_publisher(
            Float32,
            '/distance',
            10
        )

    def seg_callback(self, msg):
        self.seg_coords = list(msg.data)

        if not self.seg_coords:
            self.get_logger().info("Received empty seg_coords data")

    def depth_callback(self, msg):
        try:
            cv_depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

            if self.seg_coords and len(self.seg_coords) % 2 == 0:
                seg_depth_values = []

                height, width = cv_depth_image.shape[:2]

                for i in range(0, len(self.seg_coords), 2):
                    x = int(self.seg_coords[i])
                    y = int(self.seg_coords[i + 1])

                    if 0 <= x < width and 0 <= y < height:
                        depth_value = cv_depth_image[y, x]

                        if depth_value > 0:
                            seg_depth_values.append(depth_value)

                if len(seg_depth_values) == 0:
                    self.publish_no_detection()
                    return

                distance = np.min(seg_depth_values)
                distance_meter = float(distance) / 1000.0

                self.get_logger().info(
                    f"Shortest distance in the selected regions: {distance_meter:.2f} meters"
                )

                self.distance_pub.publish(Float32(data=distance_meter))

                if distance_meter <= 3.15:
                    cdr = 1
                    scaling_factor = 0.017
                else:
                    cdr = 2
                    scaling_factor = 1.0

                self.scaling_pub.publish(Float32(data=float(scaling_factor)))
                self.get_logger().info(f"scaling_factor: {scaling_factor}")

            else:
                self.publish_no_detection()

        except Exception as e:
            self.get_logger().error(f"Error processing depth image: {e}")

    def publish_no_detection(self):
        self.get_logger().info("No depth information available in the selected regions")

        scaling_factor = 1.0

        self.distance_pub.publish(Float32(data=-1.0))
        self.scaling_pub.publish(Float32(data=float(scaling_factor)))
        self.get_logger().info(f"scaling_factor: {scaling_factor}")

def main():
    rclpy.init()
    node = DepthDistanceSegNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
