from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QMessageBox, QWidget)
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relay Sequence Controller")
        self.setGeometry(100, 100, 1000, 700)

        self.init_ui()
        self.load_configuration()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Save Configuration Button
        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_configuration)
        layout.addWidget(save_button)

        # Other UI elements initialization...

    def save_configuration(self):
        """Save the current configuration to a file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as config_file:
                    json.dump(self.sequences, config_file, indent=4)
                QMessageBox.information(self, "Success", "Configuration saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {e}")

    def load_configuration(self):
        """Load the configuration from a file."""
        default_config_path = os.path.join(os.path.dirname(__file__), '../../configs/default_config.json')
        if os.path.exists(default_config_path):
            try:
                with open(default_config_path, 'r') as config_file:
                    self.sequences = json.load(config_file)
                # Update UI with loaded sequences...
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration: {e}")