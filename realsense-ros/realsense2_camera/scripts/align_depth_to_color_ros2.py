#!/usr/bin/env python3

import math
import cv2
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class DepthAlignNode(Node):
    def __init__(self):
        super().__init__('depth_image_processor')

        self.bridge = CvBridge()
        self.resized_img1 = None
        self.resized_img2 = None

        camera_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.sub1 = self.create_subscription(
            Image,
            '/camera1/depth/image_raw',
            self.depth1_callback,
            camera_qos
        )

        self.sub2 = self.create_subscription(
            Image,
            '/camera2/depth/image_raw',
            self.depth2_callback,
            camera_qos
        )

        self.pub = self.create_publisher(
            Image,
            '/resize_multi_depth_image',
            10
        )

        self.timer = self.create_timer(0.1, self.publish_combined_depth)

    def crop_and_resize_depth(self, depth_image):
        rgb_fov = 69.4
        depth_fov = 85.2

        rgb_fov_rad = math.radians(rgb_fov / 2)
        depth_fov_rad = math.radians(depth_fov / 2)

        height, width = depth_image.shape[:2]
        center_x, center_y = width // 2, height // 2

        crop_width = int(math.tan(rgb_fov_rad) / math.tan(depth_fov_rad) * width)
        crop_height = height

        start_x = center_x - crop_width // 2
        start_y = center_y - crop_height // 2
        end_x = start_x + crop_width
        end_y = start_y + crop_height

        cropped_img = depth_image[start_y:end_y, start_x:end_x]
        resized_img = cv2.resize(cropped_img, (640, 480), interpolation=cv2.INTER_AREA)

        return resized_img

    def depth1_callback(self, msg):
        depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        self.resized_img1 = self.crop_and_resize_depth(depth_image)

    def depth2_callback(self, msg):
        depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        self.resized_img2 = self.crop_and_resize_depth(depth_image)

    def publish_combined_depth(self):
        if self.resized_img1 is None or self.resized_img2 is None:
            return

        combined_image = cv2.hconcat([self.resized_img1, self.resized_img2])

        center_x, center_y = 960, 240
        distance_value = combined_image[center_y, center_x]
        self.get_logger().info(f"Distance at center pixel: {distance_value} units")

        ros_image_msg = self.bridge.cv2_to_imgmsg(
            combined_image,
            encoding='passthrough'
        )
        self.pub.publish(ros_image_msg)

        cv_image_normalized = cv2.normalize(combined_image, None, 0, 255, cv2.NORM_MINMAX)
        cv_image_normalized = cv_image_normalized.astype('uint8')
        jet_img = cv2.applyColorMap(cv_image_normalized, cv2.COLORMAP_JET)

        cv2.imshow("Resized Multi Depth Image", jet_img)
        cv2.waitKey(1)


def main():
    rclpy.init()
    node = DepthAlignNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
