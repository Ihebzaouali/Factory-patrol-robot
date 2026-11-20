#!/usr/bin/env python3
"""
RFID Simulator Node
-------------------
Listens for an RFID scan request from the security manager,
then prompts the operator to type 'valid' or 'invalid' in the
terminal, and publishes the result back.
"""

import rclpy
import threading
from rclpy.node import Node
from std_msgs.msg import String, Bool


# Simulated valid card IDs (would come from a database in production)
VALID_CARDS = {
    'CARD001': 'Alice Johnson  (Engineer)',
    'CARD002': 'Bob Smith      (Technician)',
    'CARD003': 'Carol White    (Supervisor)',
    'valid'  : 'Simulated Valid Card',     # shortcut for testing
}


class RFIDSimulatorNode(Node):

    def __init__(self):
        super().__init__('rfid_simulator_node')

        self.declare_parameter('namespace', 'rallp_0000')
        ns = self.get_parameter('namespace').value

        self.waiting_for_scan = False

        # Subscribe to RFID scan requests
        self.create_subscription(
            Bool,
            f'/{ns}/security/rfid_request',
            self.rfid_request_callback,
            10
        )

        # Publish RFID results
        self.result_pub = self.create_publisher(
            String,
            f'/{ns}/security/rfid_result',
            10
        )

        # Run CLI input in a background thread so it doesn't block ROS
        self.input_thread = threading.Thread(
            target=self._input_loop, daemon=True
        )
        self.input_thread.start()

        self.get_logger().info('=' * 50)
        self.get_logger().info('  RFID Simulator Node started')
        self.get_logger().info('  Waiting for scan requests...')
        self.get_logger().info('=' * 50)

    def rfid_request_callback(self, msg: Bool):
        if msg.data:
            self.waiting_for_scan = True
            print('\n' + '=' * 50)
            print('  🔖 RFID SCAN REQUESTED')
            print('  Enter one of the following:')
            print('    • A card ID  : CARD001 / CARD002 / CARD003')
            print('    • Shortcut   : valid  (authorized)')
            print('    •            : invalid (unauthorized)')
            print('=' * 50)

    def _input_loop(self):
        """Blocking input loop running in background thread."""
        while True:
            try:
                user_input = input().strip()
            except EOFError:
                break

            if not self.waiting_for_scan:
                print('[RFID] Not waiting for a scan right now.')
                continue

            self.waiting_for_scan = False
            result_msg = String()

            if user_input in VALID_CARDS:
                name = VALID_CARDS[user_input]
                print(f'\n✅  VALID CARD: {name}')
                result_msg.data = 'valid'
            else:
                print(f'\n❌  INVALID CARD: "{user_input}" not recognized')
                result_msg.data = 'invalid'

            self.result_pub.publish(result_msg)
            self.get_logger().info(f'Published RFID result: {result_msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = RFIDSimulatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
