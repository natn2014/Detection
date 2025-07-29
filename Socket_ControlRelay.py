import socket
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel


class RelayController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus Relay Controller")
        self.setGeometry(100, 100, 300, 200)

        # Layout setup
        self.layout = QVBoxLayout()
        self.status_label = QLabel("Status: Disconnected")
        self.layout.addWidget(self.status_label)

        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_device)
        self.layout.addWidget(self.connect_button)

        # Relay toggle buttons
        self.relay1_button = QPushButton("Toggle Relay CH1")
        self.relay1_button.setEnabled(False)  # Disabled until connected
        self.relay1_button.clicked.connect(self.toggle_relay1)
        self.layout.addWidget(self.relay1_button)

        self.relay2_button = QPushButton("Toggle Relay CH2")
        self.relay2_button.setEnabled(False)  # Disabled until connected
        self.relay2_button.clicked.connect(self.toggle_relay2)
        self.layout.addWidget(self.relay2_button)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Modbus TCP socket
        self.sock = None

    def connect_to_device(self):
        """Connect to the Modbus TCP device."""
        try:
            MODBUS_DEVICE_IP = "192.168.1.200"  # Replace with your relay's IP
            MODBUS_DEVICE_PORT = 502           # Replace with your relay's port

            # Create and connect the socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((MODBUS_DEVICE_IP, MODBUS_DEVICE_PORT))
            self.status_label.setText("Status: Connected")
            self.relay1_button.setEnabled(True)  # Enable buttons
            self.relay2_button.setEnabled(True)
        except Exception as e:
            self.status_label.setText(f"Status: Connection Failed ({e})")

    def send_modbus_command(self, hex_command):
        """Send a raw HEX command to the Modbus relay."""
        try:
            if self.sock:
                command_bytes = bytes.fromhex(hex_command)
                self.sock.sendall(command_bytes)
                response = self.sock.recv(1024)
                print(f"Sent: {hex_command}")
                print(f"Received: {response.hex()}")
        except Exception as e:
            print(f"Error sending command: {e}")

    def toggle_relay1(self):
        """Toggle Relay CH1."""
        # Example: Toggle Relay CH1 using HEX commands
        relay1_on = "00 00 00 00 00 06 01 05 00 00 FF 00"  # Relay CH1 ON
        relay1_off = "00 00 00 00 00 06 01 05 00 00 00 00"  # Relay CH1 OFF

        # Logic to toggle (you can improve this with state tracking if needed)
        self.send_modbus_command(relay1_on)  # Send ON command
        self.send_modbus_command(relay1_off)  # Send OFF command

    def toggle_relay2(self):
        """Toggle Relay CH2."""
        # Example: Toggle Relay CH2 using HEX commands
        relay2_on = "00 00 00 00 00 06 01 05 00 01 FF 00"  # Relay CH2 ON
        relay2_off = "00 00 00 00 00 06 01 05 00 01 00 00"  # Relay CH2 OFF

        # Logic to toggle (you can improve this with state tracking if needed)
        self.send_modbus_command(relay2_on)  # Send ON command
        self.send_modbus_command(relay2_off)  # Send OFF command

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
