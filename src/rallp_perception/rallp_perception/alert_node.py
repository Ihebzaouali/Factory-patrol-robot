 #!/usr/bin/env python3
"""
Alert Node
----------
Listens on the /security/alert topic and:
  - Prints a loud visual alarm in terminal (Docker-safe)
  - Sends a Gmail notification email
"""

import rclpy
import smtplib
import threading
import datetime
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from rclpy.node import Node
from std_msgs.msg import String


class AlertNode(Node):

    def __init__(self):
        super().__init__('alert_node')

        # ── Parameters ────────────────────────────────────────────────
        self.declare_parameter('namespace',       'rallp_0000')
        self.declare_parameter('gmail_sender',    'your_robot@gmail.com')
        self.declare_parameter('gmail_password',  'your_app_password')
        self.declare_parameter('gmail_recipient', 'security_team@gmail.com')
        self.declare_parameter('robot_name',      'RALLP Security Robot')
        self.declare_parameter('location',        'Warehouse Zone A')
        self.declare_parameter('alarm_duration',  5.0)
        self.declare_parameter('alarm_frequency', 880.0)

        ns                   = self.get_parameter('namespace').value
        self.gmail_sender    = self.get_parameter('gmail_sender').value
        self.gmail_password  = self.get_parameter('gmail_password').value
        self.gmail_recipient = self.get_parameter('gmail_recipient').value
        self.robot_name      = self.get_parameter('robot_name').value
        self.location        = self.get_parameter('location').value
        self.alarm_duration  = self.get_parameter('alarm_duration').value

        # Subscribe to security alerts
        self.create_subscription(
            String,
            f'/{ns}/security/alert',
            self.alert_callback,
            10
        )

        self.get_logger().info('=' * 50)
        self.get_logger().info('  Alert Node started')
        self.get_logger().info(f'  Email sender    : {self.gmail_sender}')
        self.get_logger().info(f'  Email recipient : {self.gmail_recipient}')
        self.get_logger().info('=' * 50)

    # ════════════════════════════════════════════════════════════════════
    #  Visual alarm (Docker-safe, no audio device needed)
    # ════════════════════════════════════════════════════════════════════

    def _play_alarm(self):
        threading.Thread(target=self._alarm_thread, daemon=True).start()

    def _alarm_thread(self):
        alarm_art = """
\033[91m
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   🚨🚨🚨   SECURITY ALARM TRIGGERED   🚨🚨🚨        ║
║                                                      ║
║        ██████  UNAUTHORIZED PERSON  ██████           ║
║                                                      ║
║   ⚠️  RFID VERIFICATION FAILED  ⚠️                   ║
║   📍 Location : {location:<36}║
║   🤖 Robot    : {robot:<36}║
║                                                      ║
╚══════════════════════════════════════════════════════╝
\033[0m"""
        # Flash the alarm message several times
        for i in range(6):
            print(alarm_art.format(
                location=self.location,
                robot=self.robot_name
            ))
            time.sleep(0.5)

        self.get_logger().error('🚨 ALARM: Unauthorized person detected!')

    # ════════════════════════════════════════════════════════════════════
    #  Email
    # ════════════════════════════════════════════════════════════════════

    def _send_email(self, subject: str, body: str):
        threading.Thread(
            target=self._email_thread,
            args=(subject, body),
            daemon=True
        ).start()

    def _email_thread(self, subject: str, body: str):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From']    = self.gmail_sender
            msg['To']      = self.gmail_recipient

            msg.attach(MIMEText(body, 'plain'))

            html_body = f"""
            <html><body>
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
              <div style="background:#cc0000;color:white;padding:20px;border-radius:8px 8px 0 0">
                <h2>🚨 SECURITY ALERT — {self.robot_name}</h2>
              </div>
              <div style="border:1px solid #ddd;padding:20px;border-radius:0 0 8px 8px">
                <pre style="font-size:14px;line-height:1.6">{body}</pre>
                <hr/>
                <p style="color:#888;font-size:12px">
                  Generated automatically by {self.robot_name}.
                </p>
              </div>
            </div>
            </body></html>
            """
            msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_sender, self.gmail_password)
                server.sendmail(
                    self.gmail_sender,
                    self.gmail_recipient,
                    msg.as_string()
                )
            self.get_logger().info(
                f'📧 Alert email sent to {self.gmail_recipient}'
            )

        except smtplib.SMTPAuthenticationError:
            self.get_logger().error(
                'Gmail auth failed. Check your App Password:\n'
                '  https://myaccount.google.com/apppasswords'
            )
        except Exception as e:
            self.get_logger().error(f'Email send failed: {e}')

    # ════════════════════════════════════════════════════════════════════
    #  Alert handler
    # ════════════════════════════════════════════════════════════════════

    def alert_callback(self, msg: String):
        alert_data = msg.data
        now        = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.get_logger().info(f'Alert received: {alert_data}')

        # ── Unauthorized person ─────────────────────────────────────────
        if 'RFID_INVALID' in alert_data:
            self._play_alarm()

            subject = f'🚨 SECURITY ALERT: Unauthorized Person — {self.robot_name}'
            body = (
                f'SECURITY ALERT\n'
                f'{"=" * 40}\n'
                f'Robot    : {self.robot_name}\n'
                f'Location : {self.location}\n'
                f'Time     : {now}\n'
                f'Event    : UNAUTHORIZED PERSON DETECTED\n'
                f'Details  : Person failed RFID verification.\n'
                f'           Robot has stopped and issued alarm.\n'
                f'{"=" * 40}\n'
                f'⚠️  Action required: Please investigate immediately!'
            )
            self._send_email(subject, body)

        # ── Authorized person ───────────────────────────────────────────
        elif 'RFID_VALID' in alert_data:
            print('\033[92m')
            print('╔══════════════════════════════════════════╗')
            print('║   ✅  AUTHORIZED PERSON — ACCESS GRANTED  ║')
            print('║       Robot resuming mission...           ║')
            print('╚══════════════════════════════════════════╝')
            print('\033[0m')

            subject = f'✅ Security Log: Authorized Access — {self.robot_name}'
            body = (
                f'SECURITY LOG\n'
                f'{"=" * 40}\n'
                f'Robot    : {self.robot_name}\n'
                f'Location : {self.location}\n'
                f'Time     : {now}\n'
                f'Event    : AUTHORIZED PERSON VERIFIED\n'
                f'Details  : Person presented valid RFID card.\n'
                f'           Robot resumed mission.\n'
                f'{"=" * 40}\n'
            )
            self._send_email(subject, body)


def main(args=None):
    rclpy.init(args=args)
    node = AlertNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
