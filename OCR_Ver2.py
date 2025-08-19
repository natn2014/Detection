import sys
import cv2
import json
import easyocr
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap, QColor
from PySide6.QtWidgets import (
    QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QLineEdit, QInputDialog
)


class VideoOCRApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize EasyOCR Reader
        self.reader = easyocr.Reader(['en'])

        # State variables
        self.current_json_file = None  # Name of the loaded JSON file
        self.original_data = []  # Original data from JSON for rollback
        self.camera_width = 640  # Placeholder for camera width
        self.camera_height = 480  # Placeholder for camera height

        # Set up the main layout with tabs
        self.setWindowTitle("Real-Time OCR with PySide6")
        self.setGeometry(100, 100, 1200, 800)

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
        self.video_label.setFixedSize(self.camera_width, self.camera_height)  # Match camera resolution dynamically

        # Right: Controls and table
        right_layout = QVBoxLayout()

        # Model Data: File selector
        self.model_data_label = QLabel("Model Data:")
        self.model_data_file = QLineEdit()
        self.model_data_file.setReadOnly(True)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_json_file)

        model_data_layout = QHBoxLayout()
        model_data_layout.addWidget(self.model_data_label)
        model_data_layout.addWidget(self.model_data_file)
        model_data_layout.addWidget(self.browse_button)

        # Table for displaying JSON data
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["Text to Compare", "Result"])
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
        layout.addWidget(self.video_label, 1)
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
        """Browse and load a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if file_path:
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

    def populate_table(self, data, table):
        """Populate the QTableWidget with data and show matching status."""
        table.setRowCount(0)
        table.setColumnWidth(0, 300)  # Adjust column width for readability
        table.setColumnWidth(1, 200)

        for item in data:
            row_position = table.rowCount()
            table.insertRow(row_position)

            # Add the text to compare in the first column
            table.setItem(row_position, 0, QTableWidgetItem(item))

            # Check match status with detected_texts from OCR
            match_status = "No Match"
            color = QColor(255, 0, 0)  # Default to red for no match

            for detected_text in self.detected_texts:
                if item.upper() == detected_text:
                    match_status = "Match"
                    color = QColor(0, 255, 0)  # Green for match
                    break
                elif item.upper() in detected_text or detected_text in item.upper():
                    match_status = "Partial Match"
                    color = QColor(255, 255, 0)  # Yellow for partial match
                    break

            # Add the match status to the second column
            result_item = QTableWidgetItem(match_status)
            table.setItem(row_position, 1, result_item)

            # Set background color for both columns in the row
            table.item(row_position, 0).setBackground(color)
            table.item(row_position, 1).setBackground(color)


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
            file_path = f"{model_name}.json"
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

    def cancel_setting_editing(self):
        """Cancel editing and revert to the original data in the setting table."""
        self.populate_table(self.original_data, self.setting_table)
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
        self.detected_texts = []  # Store detected texts for comparison

        # Draw rectangles and put text above them
        for (bbox, text, _) in results:
            self.detected_texts.append(text.upper())
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
        print("OCR performed, detected texts:", self.detected_texts)

        # Wait for 2 seconds before resuming the video feed
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoOCRApp()
    window.show()
    sys.exit(app.exec())
