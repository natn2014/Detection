#!/bin/python
import sys
import cv2
import time
import json
import easyocr
import re
import socket
import threading
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap, QColor, QIcon
from PySide6.QtWidgets import (
    QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QLineEdit, QInputDialog, QSizePolicy
)
from relay_b import Relay
from PySide6.QtCore import QObject, Signal

class RelayWorker(QObject):
    """Worker class to monitor relay inputs in a separate thread."""
    start_signal = Signal()  # Signal for starting the inspection
    finish_signal = Signal()  # Signal for finishing the inspection

    def __init__(self, relay: Relay, parent=None):
        super().__init__(parent)
        self.relay = relay
        self.running = True  # Control flag for the thread

    def monitor_relay_inputs(self):
        """Monitor DI1 and DI2 for signals to start and stop inspection."""
        self.relay.connect()
        self.relay.all_on()
        time.sleep(0.5)  # Allow time for the relay to initialize
        self.relay.all_off()
        time.sleep(0.5)  # Ensure all relays are off before starting
        print("Started monitoring relay inputs.")
        try:
            while self.running:
                if self.relay.is_DI_on(1):  # Check if DI1 is ON
                    self.start_signal.emit()  # Emit start signal
                    print("DI1 is ON, starting inspection.")

                elif self.relay.is_DI_on(2):  # Check if DI2 is ON
                    print("DI2 is ON, stopping inspection.")
                    self.finish_signal.emit()  # Emit finish signal

                time.sleep(0.5)
        finally:
            self.relay.disconnect()

    def stop(self):
        """Stop the monitoring thread."""
        self.running = False


class VideoOCRApp(QWidget):
    def __init__(self):
        super().__init__()

        # Relay for DI control
        self.relay = Relay(host="192.168.1.254")  # Replace with your relay's IP address
        self.relay.connect()  # Ensure connection is established once

        # Worker for monitoring relay inputs
        self.relay_worker = RelayWorker(self.relay)
        self.relay_worker.start_signal.connect(self.perform_ocr)  # Connect start signal
        self.relay_worker.finish_signal.connect(self.resume_video_feed)  # Connect finish signal

        # Start relay monitoring in a separate thread
        self.relay_thread = threading.Thread(target=self.relay_worker.monitor_relay_inputs, daemon=True)
        self.relay_thread.start()
        print("Started relay monitoring thread.")



        # Initialize EasyOCR Reader
        self.reader = easyocr.Reader(['en'])

        # State variables
        self.current_json_file = None  # Name of the loaded JSON file
        self.original_data = []  # Original data from JSON for rollback
        self.camera_width = 640  # Placeholder for camera width
        self.camera_height = 480  # Placeholder for camera height

        # Set up the main layout with tabs
        self.setWindowTitle("Real-Time OCR with PySide6")
        #self.setGeometry(100, 100, 1200, 800)
        self.setWindowState(Qt.WindowMaximized)  # Start maximized

        self.tab_widget = QTabWidget(self)
        self.monitor_tab = self.create_monitor_tab()
        self.setting_tab = self.create_setting_tab()
        self.log_tab = self.create_log_tab()

        self.tab_widget.addTab(self.monitor_tab, "Monitor")
        self.tab_widget.addTab(self.setting_tab, "Setting")
        self.tab_widget.addTab(self.log_tab, "Log")

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # Additonal logo.png
        self.setWindowIcon(QIcon("logo1.jpg"))  # Ensure you have a logo.png in the same directory
        self.setWindowTitle("AGC LOGO MARK Real-Time OCR")

        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Unable to access the camera.")
            sys.exit()

        # Get camera resolution
        self.camera_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.camera_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Timer to update the video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms (approx. 33 FPS)

        # State to manage OCR processing
        self.is_ocr_processing = False

    def create_monitor_tab(self):
        """Create the Monitor Tab."""
        tab = QWidget()
        layout = QHBoxLayout()

        # Left: Video feed display
        self.video_label = QLabel(tab)
        self.video_label.setAlignment(Qt.AlignCenter)
        #self.video_label.setFixedSize(self.camera_width, self.camera_height)  # Match camera resolution dynamically
        self.video_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding           
            )

        # Logo under video_label, using thumbnail size
        logo_layout = QVBoxLayout()
        logo_layout.addWidget(self.video_label)
        self.logo_label = QLabel(tab)
        self.logo_label.setPixmap(QPixmap("AGC_logo.png").scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        logo_layout.addWidget(self.logo_label)

        # Right: Controls and table
        right_layout = QVBoxLayout()

        # Model Data: File selector
        self.model_data_label = QLabel("Model Name:")
        self.model_data_file = QLineEdit()
        self.model_data_file.setReadOnly(True)
        self.browse_button = QPushButton("Job Change")
        self.browse_button.clicked.connect(self.browse_json_file)

        model_data_layout = QHBoxLayout()
        model_data_layout.addWidget(self.model_data_label)
        model_data_layout.addWidget(self.model_data_file)
        model_data_layout.addWidget(self.browse_button)

        # Table for displaying JSON data
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["Text to Compare", "Result"])
        self.data_table.setColumnWidth(0, 300)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing by default

        # Buttons for Save, Edit, Cancel, and Perform OCR
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.enable_table_editing)

        self.save_button = QPushButton("Save")
        self.save_button.setEnabled(False)  # Initially disabled
        self.save_button.clicked.connect(self.save_json_data)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)  # Initially disabled
        self.cancel_button.clicked.connect(self.cancel_editing)

        self.ocr_button = QPushButton("Trigger OCR")
        self.ocr_button.clicked.connect(self.perform_ocr)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ocr_button)

        # Add widgets to the right layout
        right_layout.addLayout(model_data_layout)
        right_layout.addWidget(self.data_table)
        right_layout.addLayout(button_layout)

        # Add to the main layout
        layout.addLayout(logo_layout, 1)
        layout.addLayout(right_layout, 1)

        tab.setLayout(layout)
        return tab

    def create_setting_tab(self):
        """Create the Setting Tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Table for displaying and editing data
        self.setting_table = QTableWidget()
        self.setting_table.setColumnCount(1)
        self.setting_table.setHorizontalHeaderLabels(["Text to Compare"])
        self.setting_table.horizontalHeader().setStretchLastSection(True)
        self.setting_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing by default

        # Buttons for Save, Edit, Cancel, and Add Model Data
        self.setting_edit_button = QPushButton("Edit")
        self.setting_edit_button.clicked.connect(self.enable_setting_table_editing)

        self.setting_save_button = QPushButton("Save")
        self.setting_save_button.setEnabled(False)  # Initially disabled
        self.setting_save_button.clicked.connect(self.save_setting_data)

        self.setting_cancel_button = QPushButton("Cancel")
        self.setting_cancel_button.setEnabled(False)  # Initially disabled
        self.setting_cancel_button.clicked.connect(self.cancel_setting_editing)

        self.add_model_button = QPushButton("Add Model Data")
        self.add_model_button.clicked.connect(self.add_model_data)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.setting_edit_button)
        button_layout.addWidget(self.setting_save_button)
        button_layout.addWidget(self.setting_cancel_button)
        button_layout.addWidget(self.add_model_button)

        layout.addWidget(self.setting_table)
        layout.addLayout(button_layout)

        tab.setLayout(layout)
        return tab

    def create_log_tab(self):
        """Create the Log Tab (currently empty)."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Logs will appear here."))
        tab.setLayout(layout)
        return tab

    def browse_json_file(self):
        """Browse and load a JSON file using barcode scanner input."""
        scan_barcode, ok = QInputDialog.getText(self, "Scan Barcode", "Please scan the barcode or enter the model name:")
        if not ok or not scan_barcode:
            return
        # Decode Free 3 of 9 Extended font to normal ASCII
        decoded_barcode = self.decode_free_3_of_9_extended(scan_barcode)
        # Remove everything after and including '$'
        sanitized_barcode = decoded_barcode.split("$")[0]
        file_path = f"{sanitized_barcode}.json"
        print(f"Sanitized barcode: {sanitized_barcode}, loading file: {file_path}")
        self.current_json_file = file_path
        self.model_data_file.setText(file_path)
        self.load_json_to_table(file_path)

    def load_json_to_table(self, file_path):
        """Load JSON data into the table."""
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                self.original_data = data.copy()  # Keep a copy for rollback
                self.populate_table(data, self.data_table)
                print(f"Loaded data Texts: {data}")
        except FileNotFoundError:
            # If the file does not exist, create a new one
            self.original_data = []
            self.save_json_data()
        except Exception as e:
            print(f"Error loading JSON file: {e}")

    def populate_table(self, data, table, detected_texts=None):
        """Populate the QTableWidget with data and optionally show match status."""
        table.setRowCount(0)
        found_match_or_partial = False
        found_not_found = False
        for item in data:
            row_position = table.rowCount()
            table.insertRow(row_position)
            table.setItem(row_position, 0, QTableWidgetItem(item))
            result = ""
            if detected_texts is not None:
                item_upper = item.upper()
                if item_upper in detected_texts:
                    result = "Match"
                else:
                    partial_found = False
                    for dt in detected_texts:
                        item_digits = re.findall(r'\d{2,}', item_upper)
                        dt_digits = re.findall(r'\d{2,}', dt)
                        if any(d in dt for d in item_digits) or any(d in item_upper for d in dt_digits):
                            partial_found = True
                            break
                        for i in range(len(item_upper)-1):
                            sub = item_upper[i:i+2]
                            if sub in dt:
                                partial_found = True
                                break
                        for i in range(len(dt)-1):
                            sub = dt[i:i+2]
                            if sub in item_upper:
                                partial_found = True
                                break
                        if partial_found:
                            break
                    if partial_found:
                        result = "Partial Match"
                    else:
                        result = "Not Found"
                result_item = QTableWidgetItem(result)
                if result == "Match":
                    result_item.setBackground(QColor(0, 255, 0))  # Green
                    found_match_or_partial = True
                elif result == "Partial Match":
                    result_item.setBackground(QColor(255, 255, 0))  # Yellow
                    found_match_or_partial = True
                else:
                    result_item.setBackground(QColor(255, 0, 0))  # Red
                    found_not_found = True
                table.setItem(row_position, 1, result_item)
        # Relay logic after all rows processed
        if detected_texts is not None:
            if found_not_found:
                print("on relay 5")
                Relay.on(self.relay, 5)
            elif found_match_or_partial:
                print("on relay 4")
                Relay.on(self.relay, 4)
                # Wait 2 seconds then turn off relay 4
                threading.Timer(2.0, lambda: Relay.off(self.relay, 4)).start()
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing by default

    def enable_table_editing(self):
        """Enable editing in the monitor table."""
        self.data_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(True)

    def cancel_editing(self):
        """Cancel editing and revert to the original data in the monitor table."""
        self.populate_table(self.original_data, self.data_table)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

    def enable_setting_table_editing(self):
        """Enable editing in the setting table."""
        self.setting_table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.setting_save_button.setEnabled(True)
        self.setting_cancel_button.setEnabled(True)

    def cancel_setting_editing(self):
        """Cancel editing and revert to the original data in the setting table."""
        self.populate_table(self.original_data, self.setting_table)
        self.setting_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setting_save_button.setEnabled(False)
        self.setting_cancel_button.setEnabled(False)

    def decode_free_3_of_9_extended(self, text):
        """
        Decode Free 3 of 9 Extended barcode font to normal ASCII text.
        Handles /A-Z for control chars, /H for (, /I for ), /D for $, %Q for prefix, etc.
        """
        # Replace special sequences
        decoded = text
        decoded = decoded.replace("/H", "(").replace("/I", ")").replace("/D", "$")
        # Replace /A-Z with corresponding ASCII control chars
        import string
        for c in string.ascii_uppercase:
            decoded = decoded.replace(f"/{c}", chr(ord(c) - 64))  # /A -> SOH (chr(1)), /B -> STX (chr(2)), etc.
        # Remove %Q prefix if present
        if decoded.startswith("%Q"):
            decoded = decoded[2:]
        return decoded

    def save_setting_data(self):
        """Save the edited setting data to a new JSON file."""
        data = []
        for row in range(self.setting_table.rowCount()):
            item = self.setting_table.item(row, 0)
            if item:
                data.append(item.text())

        # Open a dialog to get the model name
        model_name, ok = QInputDialog.getText(self, "Save Model", "Enter model name:")
        if ok and model_name:
            # Decode Free 3 of 9 Extended font to normal ASCII
            decoded_model_name = self.decode_free_3_of_9_extended(model_name)
            sanitized_model_name = decoded_model_name.split("$")[0]
            file_path = f"{sanitized_model_name}.json"
            try:
                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)
                print(f"Model data saved to {file_path}")
            except Exception as e:
                print(f"Error saving model data: {e}")

            # Disable editing
            self.setting_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.setting_save_button.setEnabled(False)
            self.setting_cancel_button.setEnabled(False)

    def add_model_data(self):
        """Add a new row to the setting table."""
        row_position = self.setting_table.rowCount()
        self.setting_table.insertRow(row_position)

    def update_frame(self):
        """Update the video feed."""
        if not self.is_ocr_processing:
            ret, frame = self.cap.read()
            if ret:
                # Resize the frame to match the camera's original aspect ratio
                frame = cv2.resize(frame, (self.camera_width, self.camera_height))

                # Convert the frame to QImage for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))
                
            else:
                print("Error: Unable to read frame.")

    def perform_ocr(self):
        """Perform OCR, draw rectangles around detected text, and display results."""
        if self.is_ocr_processing:
            return
        self.is_ocr_processing = True

        # Freeze the current frame
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Unable to capture frame.")
            self.is_ocr_processing = True
            return

        # Resize the frame to match the camera's original aspect ratio
        frame = cv2.resize(frame, (self.camera_width, self.camera_height))

        # Perform OCR on the frame
        results = self.reader.readtext(frame, detail=1, paragraph=False)
        detected_texts = []

        # Draw rectangles and put text above them
        for (bbox, text, _) in results:
            detected_texts.append(text.upper())
            # Extract bounding box coordinates
            top_left = tuple(map(int, bbox[0]))  # Top-left corner
            bottom_right = tuple(map(int, bbox[2]))  # Bottom-right corner
    
            # Draw the rectangle around the detected text
            cv2.rectangle(frame, top_left, bottom_right, (255, 255, 0), 1)
    
            # Put the OCR-detected text above the rectangle
            cv2.putText(
                frame,
                text.upper(),
                (top_left[0], max(0, top_left[1] - 10)),  # Ensure text is above rectangle and within frame
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 0),
                1,
                cv2.LINE_AA,
            )
    
        # Ensure the frame with rectangles is displayed
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert color format for PySide6 display
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))
        print("OCR performed, detected texts:", detected_texts)

        # Update table with match status
        self.populate_table(self.original_data, self.data_table, detected_texts)

        # Wait for a short duration to allow the user to see the results
        QTimer.singleShot(2000, self.resume_video_feed)

    def resume_video_feed(self):
        self.is_ocr_processing = False

    def closeEvent(self, event):
        """Release resources on closing."""
        self.cap.release()
        super().closeEvent(event)

    def save_json_data(self):
        """Save the edited data back to the JSON file."""
        if not self.current_json_file:
            return

        # Gather data from the table
        data = []
        for row in range(self.data_table.rowCount()):
            item = self.data_table.item(row, 0)
            if item:
                data.append(item.text())

        # Save the data to the JSON file
        try:
            with open(self.current_json_file, "w") as file:
                json.dump(data, file, indent=4)

            # Update the original data
            self.original_data = data.copy()

            # Disable editing
            self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.save_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
        except Exception as e:
            print(f"Error saving JSON file: {e}")
        
    #When try to enter text call function self.browse_json_file
    def keyPressEvent(self, event):
        """Handle key press events to trigger JSON file browsing."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.browse_json_file()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoOCRApp()
    window.show()
    sys.exit(app.exec())
