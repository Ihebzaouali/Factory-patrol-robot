#!/usr/bin/env python3
"""
Security Manager Node - v9  (align → approach)
------------------------------------------------
Flow:
  NAVIGATING
    → PERSON_DETECTED       cancel Nav2, pick target
    → ALIGNING_TO_PERSON    rotate in place until person centred ±dead_zone px
    → NAVIGATING_TO_PERSON  drive forward with yaw correction, stop at 1 m
    → WAITING_FOR_RFID
    → RFID_VALID / RFID_INVALID  (invalid = freeze 10 s)
    → RESUMING_MISSION
    → NAVIGATING

Timeout during approach always → RFID.
Camera "unknown" near the end just means the person's body fills / exits
the frame because the robot is very close — we do NOT give up in that case.
"""

import rclpy
import math
import time
from rclpy.node import Node
from rclpy.action import ActionClient

from enum import Enum, auto

from std_msgs.msg import String, Bool
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseStamped, TwistStamped
from nav_msgs.msg import Path
from vision_msgs.msg import Detection2DArray
from nav2_msgs.action import NavigateToPose


class SecurityState(Enum):
    IDLE                 = auto()
    NAVIGATING           = auto()
    PERSON_DETECTED      = auto()
    ALIGNING_TO_PERSON   = auto()
    NAVIGATING_TO_PERSON = auto()
    WAITING_FOR_RFID     = auto()
    RFID_VALID           = auto()
    RFID_INVALID         = auto()
    RESUMING_MISSION     = auto()


PERSON_REAL_HEIGHT_M = 1.7
IMAGE_CENTER_X       = 320.0   # px  (640 / 2)


class SecurityManagerNode(Node):

    def __init__(self):
        super().__init__('security_manager_node')

        # ── Parameters ──────────────────────────────────────────────────
        self.declare_parameter('namespace',               'rallp_0000')
        self.declare_parameter('safe_stop_distance',      1.0)
        self.declare_parameter('detection_confidence',    0.5)
        self.declare_parameter('rfid_timeout',            30.0)
        self.declare_parameter('approach_speed',          0.3)
        self.declare_parameter('detection_cooldown',      5.0)
        self.declare_parameter('approach_timeout',        8.0)
        self.declare_parameter('lidar_topic',
            '/rallp_0000/sensors/lidar2d_0/scan')
        self.declare_parameter('nav_idle_timeout',        3.0)
        self.declare_parameter('post_rfid_suppress',      4.0)
        self.declare_parameter('invalid_freeze_duration', 10.0)
        self.declare_parameter('focal_length_px',         554.0)
        self.declare_parameter('use_bbox_distance',       True)
        self.declare_parameter('max_engage_distance',     5.0)
        # ── Alignment ────────────────────────────────────────────────────
        self.declare_parameter('align_kp',                0.003)
        self.declare_parameter('align_max_angular',       0.5)
        self.declare_parameter('align_dead_zone_px',      30.0)
        self.declare_parameter('align_stable_ticks',      5)
        self.declare_parameter('align_timeout',           6.0)
        self.declare_parameter('approach_yaw_kp',         0.001)

        ns = self.get_parameter('namespace').value
        self.ns                   = ns
        self.safe_stop_distance   = self.get_parameter('safe_stop_distance').value
        self.detection_confidence = self.get_parameter('detection_confidence').value
        self.rfid_timeout         = self.get_parameter('rfid_timeout').value
        self.approach_speed       = self.get_parameter('approach_speed').value
        self.detection_cooldown   = self.get_parameter('detection_cooldown').value
        self.approach_timeout     = self.get_parameter('approach_timeout').value
        lidar_topic               = self.get_parameter('lidar_topic').value
        self.nav_idle_timeout     = self.get_parameter('nav_idle_timeout').value
        self.post_rfid_suppress   = self.get_parameter('post_rfid_suppress').value
        self.invalid_freeze_dur   = self.get_parameter('invalid_freeze_duration').value
        self.focal_length_px      = self.get_parameter('focal_length_px').value
        self.use_bbox_distance    = self.get_parameter('use_bbox_distance').value
        self.max_engage_distance  = self.get_parameter('max_engage_distance').value
        self.align_kp             = self.get_parameter('align_kp').value
        self.align_max_angular    = self.get_parameter('align_max_angular').value
        self.align_dead_zone_px   = self.get_parameter('align_dead_zone_px').value
        self.align_stable_ticks   = self.get_parameter('align_stable_ticks').value
        self.align_timeout        = self.get_parameter('align_timeout').value
        self.approach_yaw_kp      = self.get_parameter('approach_yaw_kp').value

        # ── State ────────────────────────────────────────────────────────
        self.state                  = SecurityState.IDLE
        self.rfid_timer_start       = None
        self.approach_start_time    = None
        self.align_start_time       = None
        self.align_stable_count     = 0
        self.invalid_freeze_start   = None
        self.last_detection_time    = 0.0
        self.last_idle_log_time     = 0.0
        self.last_rfid_resolve_time = 0.0
        self.last_plan_time         = 0.0
        self.last_goal_pose         = None
        self.tracked_goal_handle    = None

        # ── Sensor data ──────────────────────────────────────────────────
        self.front_distance         = float('inf')
        self.lidar_received         = False
        self.camera_person_distance = float('inf')
        self.target_bbox_center_x   = None   # px, updated every detection tick
        # True once camera saw person ≤ was_close_threshold during this approach.
        # If camera then goes unknown → robot is right in front of them → stop.
        self.was_close              = False
        self.was_close_threshold    = 3.0    # metres — camera goes unknown ~2.68m so 3.0 is safe
        # Timestamp when robot started resuming mission — used to prevent
        # re-detecting the same person while the robot is still turning away
        self.resume_start_time      = 0.0
        self.min_navigate_before_detect = 6.0  # seconds of navigation before re-engaging

        # ── Nav2 action client ───────────────────────────────────────────
        self.nav2_client = ActionClient(
            self, NavigateToPose, f'/{ns}/navigate_to_pose')

        # ── Publishers ───────────────────────────────────────────────────
        self.joy_cmd_pub = self.create_publisher(
            TwistStamped, f'/{ns}/joy_teleop/cmd_vel', 10)
        self.base_cmd_pub = self.create_publisher(
            TwistStamped, f'/{ns}/cmd_vel', 10)
        self.state_pub = self.create_publisher(
            String, f'/{ns}/security/state', 10)
        self.alert_pub = self.create_publisher(
            String, f'/{ns}/security/alert', 10)
        self.rfid_request_pub = self.create_publisher(
            Bool, f'/{ns}/security/rfid_request', 10)

        # ── Subscribers ──────────────────────────────────────────────────
        self.create_subscription(Path, f'/{ns}/plan', self.plan_callback, 10)
        self.create_subscription(PoseStamped, f'/{ns}/goal_pose',
                                 self.goal_pose_callback, 10)
        self.create_subscription(Detection2DArray, f'/{ns}/person_detections',
                                 self.detection_callback, 10)
        self.create_subscription(String, f'/{ns}/security/rfid_result',
                                 self.rfid_callback, 10)
        self.create_subscription(LaserScan, lidar_topic, self.lidar_callback, 10)

        # ── Timers ───────────────────────────────────────────────────────
        self.create_timer(0.1, self.state_machine_tick)
        self.create_timer(1.0, self.check_nav_idle)

        self.get_logger().info('=' * 62)
        self.get_logger().info('  Security Manager Node  v9  (align → approach)')
        self.get_logger().info(f'  Namespace          : {ns}')
        self.get_logger().info(f'  Stop distance      : {self.safe_stop_distance} m')
        self.get_logger().info(f'  Max engage dist    : {self.max_engage_distance} m')
        self.get_logger().info(f'  Approach timeout   : {self.approach_timeout} s')
        self.get_logger().info(f'  Align Kp           : {self.align_kp}')
        self.get_logger().info(f'  Align dead zone    : ±{self.align_dead_zone_px} px')
        self.get_logger().info(f'  Align timeout      : {self.align_timeout} s')
        self.get_logger().info(f'  RFID timeout       : {self.rfid_timeout} s')
        self.get_logger().info(f'  Invalid freeze     : {self.invalid_freeze_dur} s')
        self.get_logger().info(f'  Post-RFID suppress : {self.post_rfid_suppress} s')
        self.get_logger().info(f'  Focal length (px)  : {self.focal_length_px}')
        self.get_logger().info(f'  Image center X     : {IMAGE_CENTER_X} px')
        self.get_logger().info('=' * 62)
        self.get_logger().info('⚠️  IDLE — send a Nav2 goal from RViz2 to ARM security')

    # ════════════════════════════════════════════════════════════════════
    # Camera helpers
    # ════════════════════════════════════════════════════════════════════

    def _estimate_person_distance(self, detection) -> float:
        if not self.use_bbox_distance:
            return float('inf')
        try:
            h_px = detection.bbox.size_y
            if h_px < 5.0:
                return float('inf')
            return (PERSON_REAL_HEIGHT_M * self.focal_length_px) / h_px
        except Exception:
            return float('inf')

    def _pick_target_person(self, msg: Detection2DArray) -> bool:
        """Pick the closest detected person. Updates camera_person_distance
        and target_bbox_center_x. Returns True if someone found."""
        best_dist   = float('inf')
        best_center = None
        for det in msg.detections:
            for result in det.results:
                if (result.hypothesis.class_id == 'person' and
                        result.hypothesis.score >= self.detection_confidence):
                    d = self._estimate_person_distance(det)
                    if d < best_dist:
                        best_dist   = d
                        best_center = det.bbox.center.position.x
        self.camera_person_distance = best_dist
        if best_center is not None:
            self.target_bbox_center_x = best_center
            return True
        self.camera_person_distance = float('inf')
        return False

    # ════════════════════════════════════════════════════════════════════
    # Callbacks
    # ════════════════════════════════════════════════════════════════════

    def plan_callback(self, msg: Path):
        self.last_plan_time = time.time()
        if self.state == SecurityState.IDLE:
            self.get_logger().info('🟢 Nav2 plan detected — security ARMED')
            self.transition_to(SecurityState.NAVIGATING)

    def goal_pose_callback(self, msg: PoseStamped):
        """Save pose only — RViz already sent it to Nav2."""
        self.last_goal_pose = msg
        self.get_logger().info(
            f'🎯 Goal saved: x={msg.pose.position.x:.2f} y={msg.pose.position.y:.2f}')
        if self.state == SecurityState.IDLE:
            self.transition_to(SecurityState.NAVIGATING)

    def check_nav_idle(self):
        if self.state != SecurityState.NAVIGATING:
            return
        if self.last_plan_time == 0.0:
            return
        if time.time() - self.last_plan_time > self.nav_idle_timeout:
            self.get_logger().info('🏁 Goal reached — IDLE')
            self.transition_to(SecurityState.IDLE)

    def lidar_callback(self, msg: LaserScan):
        self.lidar_received = True
        ranges     = msg.ranges
        total      = len(ranges)
        cone_angle = math.radians(30)
        steps      = max(1, int(cone_angle / msg.angle_increment))
        center     = total // 2
        front_ranges = [
            r for r in ranges[max(0, center - steps): center + steps]
            if msg.range_min < r < msg.range_max
        ]
        self.front_distance = min(front_ranges) if front_ranges else float('inf')

    def detection_callback(self, msg: Detection2DArray):
        found = self._pick_target_person(msg)

        if self.state != SecurityState.NAVIGATING:
            if self.state == SecurityState.IDLE and found:
                now = time.time()
                if now - self.last_idle_log_time > 10.0:
                    self.get_logger().info(
                        f'👁️  Person at ~{self.camera_person_distance:.1f} m — '
                        f'IDLE (send goal to ARM)')
                    self.last_idle_log_time = now
            return

        if not found:
            return

        now = time.time()
        if now - self.last_detection_time < self.detection_cooldown:
            return
        if now - self.last_rfid_resolve_time < self.post_rfid_suppress:
            remaining = self.post_rfid_suppress - (now - self.last_rfid_resolve_time)
            self.get_logger().info(f'🛡️  Person suppressed ({remaining:.1f}s remaining)')
            return

        # Fix: don't re-engage while robot is still physically turning away after resume.
        # The camera keeps seeing the person while Nav2 rotates the robot back to its goal.
        navigate_elapsed = now - self.resume_start_time
        if self.resume_start_time > 0.0 and navigate_elapsed < self.min_navigate_before_detect:
            remaining = self.min_navigate_before_detect - navigate_elapsed
            self.get_logger().info(
                f'🛡️  Post-resume lockout — waiting {remaining:.1f}s before re-engaging')
            return
        if self.camera_person_distance > self.max_engage_distance:
            self.get_logger().info(
                f'👁️  Person at {self.camera_person_distance:.1f} m '
                f'> max_engage {self.max_engage_distance} m — ignoring')
            return

        self.last_detection_time = now
        self.get_logger().warn(
            f'🚨 Person at ~{self.camera_person_distance:.1f} m  '
            f'bbox_x={self.target_bbox_center_x:.0f} px — engaging!')
        self.transition_to(SecurityState.PERSON_DETECTED)

    def rfid_callback(self, msg: String):
        if self.state != SecurityState.WAITING_FOR_RFID:
            return
        result = msg.data.strip().lower()
        self.get_logger().info(f'RFID result: "{result}"')
        if result == 'valid':
            self.transition_to(SecurityState.RFID_VALID)
        elif result == 'invalid':
            self.transition_to(SecurityState.RFID_INVALID)

    # ════════════════════════════════════════════════════════════════════
    # State machine
    # ════════════════════════════════════════════════════════════════════

    def transition_to(self, new_state: SecurityState):
        self.get_logger().info(f'State: {self.state.name}  →  {new_state.name}')
        self.state = new_state
        msg = String()
        msg.data = new_state.name
        self.state_pub.publish(msg)

    def state_machine_tick(self):
        s = self.state
        if   s == SecurityState.PERSON_DETECTED:
            self._handle_person_detected()
        elif s == SecurityState.ALIGNING_TO_PERSON:
            self._handle_aligning()
        elif s == SecurityState.NAVIGATING_TO_PERSON:
            self._handle_navigating_to_person()
        elif s == SecurityState.WAITING_FOR_RFID:
            self._stop_robot()
            self._handle_waiting_rfid()
        elif s == SecurityState.RFID_VALID:
            self._stop_robot()
            self._handle_rfid_valid()
        elif s == SecurityState.RFID_INVALID:
            self._stop_robot()
            self._handle_rfid_invalid()
        elif s == SecurityState.RESUMING_MISSION:
            self._handle_resuming()

    # ── State handlers ─────────────────────────────────────────────────

    def _handle_person_detected(self):
        self._cancel_nav2()
        self._stop_robot()
        self.align_start_time   = time.time()
        self.align_stable_count = 0
        self.get_logger().info(
            f'🔄 Starting alignment — bbox_x={self.target_bbox_center_x} px  '
            f'image_center={IMAGE_CENTER_X} px')
        self.transition_to(SecurityState.ALIGNING_TO_PERSON)

    def _handle_aligning(self):
        """Rotate in place until person is centred in the frame."""
        elapsed = time.time() - self.align_start_time

        # Camera lost person this tick — hold still, keep waiting
        if self.target_bbox_center_x is None:
            self._stop_robot()
            return

        error_px  = self.target_bbox_center_x - IMAGE_CENTER_X
        angular_z = -self.align_kp * error_px
        angular_z = max(-self.align_max_angular,
                        min(self.align_max_angular, angular_z))

        self.get_logger().info(
            f'🔄 Aligning — bbox_x={self.target_bbox_center_x:.0f}  '
            f'error={error_px:+.0f} px  ω={angular_z:+.3f} rad/s  '
            f't={elapsed:.1f}s')

        if abs(error_px) < self.align_dead_zone_px:
            self.align_stable_count += 1
        else:
            self.align_stable_count = 0

        if self.align_stable_count >= self.align_stable_ticks:
            self._stop_robot()
            self.get_logger().info(
                f'✅ Aligned (error={error_px:+.0f} px) — starting approach')
            self.approach_start_time = time.time()
            self.was_close           = False
            self.transition_to(SecurityState.NAVIGATING_TO_PERSON)
            return

        if elapsed >= self.align_timeout:
            self._stop_robot()
            self.get_logger().warn(
                f'⏱️  Align timeout — proceeding to approach anyway')
            self.approach_start_time = time.time()
            self.was_close           = False
            self.transition_to(SecurityState.NAVIGATING_TO_PERSON)
            return

        cmd = TwistStamped()
        cmd.header.stamp    = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        cmd.twist.angular.z = angular_z
        self.joy_cmd_pub.publish(cmd)

    def _handle_navigating_to_person(self):
        """Drive forward with yaw correction. Stop at safe_stop_distance."""
        elapsed = time.time() - self.approach_start_time

        cam_str   = (f'{self.camera_person_distance:.2f} m'
                     if self.camera_person_distance < float('inf') else 'unknown')
        lidar_str = (f'{self.front_distance:.2f} m'
                     if self.lidar_received else 'no lidar')

        if int(elapsed) % 3 == 0 and elapsed > 0.1:
            self.get_logger().info(
                f'🚶 Approaching — cam={cam_str}  lidar={lidar_str}  t={elapsed:.1f}s')

        # Wait for first lidar reading
        if not self.lidar_received:
            self.approach_start_time = time.time()
            return

        # Track whether camera has seen the person close enough
        if (self.camera_person_distance != float('inf') and
                self.camera_person_distance <= self.was_close_threshold):
            self.was_close = True

        # ── Stop: camera was close and now went unknown → robot is right there ──
        if self.was_close and self.camera_person_distance == float('inf'):
            self._stop_robot()
            self.get_logger().info(
                '✅ Camera went unknown after being close — '
                'person fills frame, robot is right in front → RFID')
            self._start_rfid_verification()
            return

        # Primary stop: camera says person is within safe distance
        cam_close = (self.camera_person_distance != float('inf') and
                     self.camera_person_distance <= self.safe_stop_distance)

        # Fused stop: lidar obstacle AND camera also agrees person is nearby
        lidar_fused = (self.front_distance <= self.safe_stop_distance and
                       self.camera_person_distance != float('inf') and
                       self.camera_person_distance <= self.safe_stop_distance * 1.5)

        if cam_close or lidar_fused:
            self._stop_robot()
            self.get_logger().info(
                f'✅ Stopped — cam={cam_str}  lidar={lidar_str}')
            self._start_rfid_verification()
            return

        # Hard lidar safety: stop for any obstacle ≤ 0.9 m regardless of camera.
        # 0.5 m was too close — robot was bumping into the person.
        if self.front_distance <= 0.9:
            self._stop_robot()
            self.get_logger().warn(
                f'🛑 Lidar safety stop at {self.front_distance:.2f} m — requesting RFID')
            self._start_rfid_verification()
            return

        # Timeout → always request RFID.
        # "unknown" distance here just means the robot is very close and the
        # person's body fills/exits the frame — we are definitely next to them.
        if elapsed >= self.approach_timeout:
            self._stop_robot()
            self.get_logger().warn(
                f'⏱️  Approach timeout — cam={cam_str} '
                f'(unknown = robot is very close) — requesting RFID')
            self._start_rfid_verification()
            return

        # Drive forward with small yaw correction to stay aimed at person
        yaw_correction = 0.0
        if self.target_bbox_center_x is not None:
            error_px       = self.target_bbox_center_x - IMAGE_CENTER_X
            yaw_correction = -self.approach_yaw_kp * error_px

        cmd = TwistStamped()
        cmd.header.stamp    = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        cmd.twist.linear.x  = self.approach_speed
        cmd.twist.angular.z = yaw_correction
        self.joy_cmd_pub.publish(cmd)

    def _start_rfid_verification(self):
        self.rfid_timer_start = time.time()
        self._request_rfid_scan()
        self.transition_to(SecurityState.WAITING_FOR_RFID)

    def _handle_waiting_rfid(self):
        elapsed   = time.time() - self.rfid_timer_start
        remaining = int(self.rfid_timeout - elapsed)
        if int(elapsed) % 5 == 0 and elapsed > 0.5:
            self.get_logger().warn(f'⏳ Waiting for RFID... {remaining}s left')
        if elapsed >= self.rfid_timeout:
            self.get_logger().error('⏰ RFID timeout — UNAUTHORIZED')
            self.last_rfid_resolve_time = time.time()
            self.invalid_freeze_start   = time.time()
            self.transition_to(SecurityState.RFID_INVALID)

    def _handle_rfid_valid(self):
        self.get_logger().info('✅ RFID valid — resuming mission')
        self.last_rfid_resolve_time = time.time()
        alert = String()
        alert.data = 'RFID_VALID: Authorized person, mission resuming'
        self.alert_pub.publish(alert)
        self.transition_to(SecurityState.RESUMING_MISSION)

    def _handle_rfid_invalid(self):
        """Freeze both cmd_vel topics for invalid_freeze_dur seconds then resume."""
        if self.invalid_freeze_start is None:
            self.invalid_freeze_start = time.time()
            self.get_logger().error('🚨 RFID INVALID — FREEZING ROBOT!')
            alert = String()
            alert.data = 'RFID_INVALID: UNAUTHORIZED PERSON — ALARM TRIGGERED'
            self.alert_pub.publish(alert)

        elapsed   = time.time() - self.invalid_freeze_start
        remaining = int(self.invalid_freeze_dur - elapsed)

        if int(elapsed * 10) % 10 == 0:
            self.get_logger().error(
                f'🔴 ROBOT FROZEN — UNAUTHORIZED — {remaining}s remaining')

        if elapsed >= self.invalid_freeze_dur:
            self.get_logger().info(
                f'⏱️  Freeze complete ({self.invalid_freeze_dur:.0f}s) — resuming')
            self.invalid_freeze_start   = None
            self.last_rfid_resolve_time = time.time()
            self.transition_to(SecurityState.RESUMING_MISSION)

    def _handle_resuming(self):
        goal = self.last_goal_pose
        if goal is None:
            self.get_logger().info('No saved goal — IDLE')
            self.transition_to(SecurityState.IDLE)
            return
        self.get_logger().info(
            f'🔄 Resuming: x={goal.pose.position.x:.2f} y={goal.pose.position.y:.2f}')
        self._send_nav2_goal(goal)
        self.resume_start_time = time.time()   # start the re-detect lockout clock
        self.transition_to(SecurityState.NAVIGATING)

    # ════════════════════════════════════════════════════════════════════
    # Stop — zero BOTH cmd_vel topics every tick
    # ════════════════════════════════════════════════════════════════════

    def _stop_robot(self):
        stamp = self.get_clock().now().to_msg()
        for pub in (self.joy_cmd_pub, self.base_cmd_pub):
            cmd = TwistStamped()
            cmd.header.stamp    = stamp
            cmd.header.frame_id = 'base_link'
            pub.publish(cmd)

    # ════════════════════════════════════════════════════════════════════
    # Nav2 helpers
    # ════════════════════════════════════════════════════════════════════

    def _cancel_nav2(self):
        if self.tracked_goal_handle:
            try:
                self.tracked_goal_handle.cancel_goal_async()
                self.get_logger().info('✅ Nav2 cancel sent')
                self.tracked_goal_handle = None
            except Exception as e:
                self.get_logger().warn(f'Cancel failed: {e}')
        else:
            self.get_logger().warn('⚠️  No tracked handle — relying on dual stop')
        self._stop_robot()

    def _send_nav2_goal(self, pose: PoseStamped):
        if not self.nav2_client.wait_for_server(timeout_sec=3.0):
            self.get_logger().error('Nav2 action server unavailable!')
            self.transition_to(SecurityState.IDLE)
            return
        goal_msg      = NavigateToPose.Goal()
        goal_msg.pose = pose
        future = self.nav2_client.send_goal_async(goal_msg)
        future.add_done_callback(self._goal_accepted_callback)

    def _goal_accepted_callback(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('Resume goal rejected!')
            return
        self.tracked_goal_handle = handle
        self.get_logger().info('✅ Resume goal accepted')
        handle.get_result_async().add_done_callback(self._goal_done_callback)

    def _goal_done_callback(self, future):
        self.get_logger().info('🏁 Navigation complete — IDLE')
        if self.state == SecurityState.NAVIGATING:
            self.transition_to(SecurityState.IDLE)

    def _request_rfid_scan(self):
        self.get_logger().info(
            '\n' + '=' * 54 +
            '\n  🤖 ROBOT: Please scan your RFID card!' +
            '\n  👉 Type in the RFID xterm window:' +
            '\n     CARD001 / CARD002 / CARD003 / valid / invalid' +
            '\n' + '=' * 54)
        msg = Bool()
        msg.data = True
        self.rfid_request_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SecurityManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
