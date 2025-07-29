import socket
import sys
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton


class RelayController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus Relay Controller")
        self.setGeometry(100, 100, 300, 150)

        # Layout setup
        self.layout = QVBoxLayout()
        self.status_label = QLabel("Status: Disconnected")
        self.layout.addWidget(self.status_label)

        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_and_toggle_relay)
        self.layout.addWidget(self.connect_button)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Modbus TCP socket
        self.sock = None

    def connect_to_device(self):
        """Connect to the Modbus TCP device."""
        try:
            MODBUS_DEVICE_IP = "192.168.0.100"  # Replace with your relay's IP
            MODBUS_DEVICE_PORT = 502           # Replace with your relay's port

            # Create and connect the socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((MODBUS_DEVICE_IP, MODBUS_DEVICE_PORT))
            self.status_label.setText("Status: Connected")
            print("Connected to Modbus device.")
            return True
        except Exception as e:
            self.status_label.setText(f"Status: Connection Failed ({e})")
            print(f"Failed to connect: {e}")
            return False

    def send_modbus_command(self, hex_command):
        """Send a raw HEX command to the Modbus relay."""
        try:
            if self.sock:
                command_bytes = bytes.fromhex(hex_command)
                self.sock.sendall(command_bytes)

                # Receive response (optional)
                response = self.sock.recv(1024)
                print(f"Sent: {hex_command}")
                print(f"Received: {response.hex()}")
        except Exception as e:
            print(f"Error sending command: {e}")

    def connect_and_toggle_relay(self):
        """Connect to the device and toggle Relay CH1."""
        if self.connect_to_device():
            # Send OFF command
            relay_off = "00 00 00 00 00 06 01 05 00 00 00 00"
            self.send_modbus_command(relay_off)
            print("Relay CH1 OFF")

            # Wait for 1 second
            time.sleep(1)

            # Send ON command
            relay_on = "00 00 00 00 00 06 01 05 00 00 FF 00"
            self.send_modbus_command(relay_on)
            print("Relay CH1 ON")

    def closeEvent(self, event):
        """Close the Modbus socket when the application is closed."""
        if self.sock:
            self.sock.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RelayController()
    window.show()
    sys.exit(app.exec())
