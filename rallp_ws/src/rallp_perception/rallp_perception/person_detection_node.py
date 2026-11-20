#!/usr/bin/env python3
"""
Person Detection Node using YOLOv8
Subscribes to camera images and publishes detected persons
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import cv2
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not installed. Install with: pip install ultralytics")


class PersonDetectionNode(Node):
    def __init__(self):
        super().__init__('person_detection_node')
        
        # Parameters
        self.declare_parameter('camera_topic', '/rallp_0000/camera_0/image_raw')
        self.declare_parameter('detection_topic', '/rallp_0000/person_detections')
        self.declare_parameter('visualization_topic', '/rallp_0000/camera_0/image_detections')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('model_size', 'yolov8n.pt')  # n, s, m, l, x
        self.declare_parameter('visualize', True)
        
        camera_topic = self.get_parameter('camera_topic').value
        detection_topic = self.get_parameter('detection_topic').value
        viz_topic = self.get_parameter('visualization_topic').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        model_size = self.get_parameter('model_size').value
        self.visualize = self.get_parameter('visualize').value
        
        # CV Bridge
        self.bridge = CvBridge()
        
        # Load YOLO model
        if YOLO_AVAILABLE:
            self.get_logger().info(f'Loading YOLO model: {model_size}')
            self.model = YOLO(model_size)
            self.get_logger().info('YOLO model loaded successfully')
        else:
            self.get_logger().error('YOLO not available. Please install: pip install ultralytics')
            return
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            camera_topic,
            self.image_callback,
            10
        )
        
        # Publishers
        self.detection_pub = self.create_publisher(
            Detection2DArray,
            detection_topic,
            10
        )
        
        if self.visualize:
            self.viz_pub = self.create_publisher(
                Image,
                viz_topic,
                10
            )
        
        self.get_logger().info(f'Person detection node started')
        self.get_logger().info(f'Subscribed to: {camera_topic}')
        self.get_logger().info(f'Publishing detections to: {detection_topic}')
        
    def image_callback(self, msg):
        try:
            # Convert ROS Image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Run YOLO inference
            results = self.model(cv_image, verbose=False)
            
            # Create detection message
            detection_array = Detection2DArray()
            detection_array.header = msg.header
            
            # Process detections
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get class ID (0 = person in COCO dataset)
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    
                    # Only process person detections (class_id = 0)
                    if class_id == 0 and confidence >= self.confidence_threshold:
                        # Get bounding box
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Create Detection2D message
                        detection = Detection2D()
                        detection.header = msg.header
                        
                        # Bounding box center
                        detection.bbox.center.position.x = float((x1 + x2) / 2)
                        detection.bbox.center.position.y = float((y1 + y2) / 2)
                        detection.bbox.size_x = float(x2 - x1)
                        detection.bbox.size_y = float(y2 - y1)
                        
                        # Hypothesis
                        hypothesis = ObjectHypothesisWithPose()
                        hypothesis.hypothesis.class_id = 'person'
                        hypothesis.hypothesis.score = confidence
                        detection.results.append(hypothesis)
                        
                        detection_array.detections.append(detection)
                        
                        # Draw on visualization image
                        if self.visualize:
                            cv2.rectangle(cv_image, 
                                        (int(x1), int(y1)), 
                                        (int(x2), int(y2)), 
                                        (0, 255, 0), 2)
                            label = f'Person: {confidence:.2f}'
                            cv2.putText(cv_image, label, 
                                      (int(x1), int(y1) - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 
                                      0.5, (0, 255, 0), 2)
            
            # Publish detections
            self.detection_pub.publish(detection_array)
            
            # Publish visualization
            if self.visualize:
                # Add person count
                person_count = len(detection_array.detections)
                cv2.putText(cv_image, f'Persons detected: {person_count}',
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                          1.0, (0, 255, 0), 2)
                
                viz_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
                viz_msg.header = msg.header
                self.viz_pub.publish(viz_msg)
            
            # Log detection count
            if len(detection_array.detections) > 0:
                self.get_logger().info(f'Detected {len(detection_array.detections)} person(s)')
                
        except Exception as e:
            self.get_logger().error(f'Error processing image: {str(e)}')


def main(args=None):
    rclpy.init(args=args)
    
    if not YOLO_AVAILABLE:
        print("Please install ultralytics: pip install ultralytics")
        return
    
    node = PersonDetectionNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
