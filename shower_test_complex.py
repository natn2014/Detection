import sys
import cv2
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QGridLayout, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer
from ultralytics import YOLO  # YOLOv8 import
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Load YOLOv8 model (ensure you have YOLOv8 installed via `pip install ultralytics`)
model = YOLO("yolov8n.pt")  # Replace with your model file (e.g., yolov8x.pt)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Camera YOLOv8 Object Detection with Thumbnail Management")
        self.setGeometry(100, 100, 1600, 900)

        # State variables
        self.inspection_running = False
        self.ng_counts = {"Top Left": 0, "Top Right": 0, "Bottom Left": 0, "Bottom Right": 0}
        self.total_ok_count = 0
        self.total_ng_count = 0
        self.start_time = None
        self.previous_start_time = None
        self.inspection_durations = []  # Duration between Start and Finish
        self.start_to_start_times = []  # Duration between consecutive Start signals
        self.blink_state = False  # State for blinking
        self.ng_thumbnails = []  # List of NG thumbnail frames (FIFO structure for thumbnails)

        # Flags to ensure NG is counted only once per camera per inspection
        self.camera_ng_flags = {"Top Left": False, "Top Right": False, "Bottom Left": False, "Bottom Right": False}

        # Timer for blinking the Start button
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_start_button_color)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QGridLayout(self.central_widget)

        # Camera sections
        self.camera_labels = {}
        self.status_labels = {}
        self.ng_count_labels = {}

        camera_positions = ["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
        for i, position in enumerate(camera_positions):
            camera_label = QLabel(self)
            camera_label.setFixedSize(500, 350)
            camera_label.setStyleSheet("border: 2px solid black; background-color: #f0f0f0;")
            camera_label.setAlignment(Qt.AlignCenter)

            status_label = QLabel(position, self)
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet("background-color: gray; color: white; font-size: 16px; font-weight: bold; padding: 5px;")

            self.main_layout.addWidget(status_label, i // 2 * 2, i % 2)
            self.main_layout.addWidget(camera_label, i // 2 * 2 + 1, i % 2)

            self.camera_labels[position] = camera_label
            self.status_labels[position] = status_label

        # NG Counter section on the right side
        self.ng_layout = QVBoxLayout()
        self.ng_layout.setAlignment(Qt.AlignTop)
        self.ng_layout.setSpacing(15)

        # NG counters per camera
        for position in camera_positions:
            ng_label = QLabel(f"{position} NG = 0 Pcs", self)
            ng_label.setAlignment(Qt.AlignLeft)
            ng_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
            self.ng_layout.addWidget(ng_label)
            self.ng_count_labels[position] = ng_label

        # Total OK and NG counters
        self.total_ok_label = QLabel("Total OK = 0 Pcs", self)
        self.total_ok_label.setAlignment(Qt.AlignLeft)
        self.total_ok_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        self.ng_layout.addWidget(self.total_ok_label)

        self.total_ng_label = QLabel("Total NG = 0 Pcs", self)
        self.total_ng_label.setAlignment(Qt.AlignLeft)
        self.total_ng_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
        self.ng_layout.addWidget(self.total_ng_label)

        # Add Start and Finish buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Inspection", self)
        self.start_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        self.start_button.clicked.connect(self.start_inspection)

        self.finish_button = QPushButton("Finish Inspection", self)
        self.finish_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #f44336; color: white;")
        self.finish_button.clicked.connect(self.finish_inspection)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.finish_button)

        # Add NG thumbnails area
        self.thumbnail_layout = QHBoxLayout()
        self.thumbnail_labels = [QLabel(self) for _ in range(4)]  # Create 4 thumbnail slots
        for label in self.thumbnail_labels:
            label.setFixedSize(150, 100)
            label.setStyleSheet("border: 1px solid black; background-color: #e0e0e0;")
            label.setAlignment(Qt.AlignCenter)
            self.thumbnail_layout.addWidget(label)

        self.ng_layout.addLayout(button_layout)
        self.ng_layout.addLayout(self.thumbnail_layout)

        # Add a graph for inspection durations
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ng_layout.addWidget(self.canvas)

        # Add NG layout to the right side of the screen
        self.main_layout.addLayout(self.ng_layout, 0, 2, 4, 1)

        # Camera threads
        self.camera_threads = {}
        self.camera_indices = {
            "Top Left": 0,  # USB camera index 0
            "Top Right": 1,  # USB camera index 1
            "Bottom Left": 2,  # USB camera index 2
            "Bottom Right": 3,  # USB camera index 3
        }

        self.start_cameras()

    def start_cameras(self):
        for position, index in self.camera_indices.items():
            thread = threading.Thread(target=self.camera_thread, args=(position, index))
            thread.daemon = True
            thread.start()
            self.camera_threads[position] = thread

    def start_inspection(self):
        self.inspection_running = True
        self.blink_timer.start(500)  # Start blinking every 0.5 seconds

        # Reset NG flags for all cameras
        for position in self.camera_ng_flags:
            self.camera_ng_flags[position] = False

        current_time = time.time()

        # Calculate start-to-start duration and store it
        if self.previous_start_time is not None:
            start_to_start_duration = round(current_time - self.previous_start_time)
            self.start_to_start_times.append(start_to_start_duration)
        self.previous_start_time = current_time  # Update the previous start time

        self.start_time = current_time  # Record the current start time
        for position in self.ng_counts:
            self.update_ng_label(position)  # Reset NG labels visually

    def finish_inspection(self):
        if not self.inspection_running:
            return

        self.inspection_running = False
        self.blink_timer.stop()  # Stop blinking
        self.start_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")  # Reset button color

        end_time = time.time()  # Record the end time
        duration = round(end_time - self.start_time)  # Calculate duration (in whole seconds)
        self.inspection_durations.append(duration)  # Add duration to the list

        # Check if any NG was detected during the inspection
        if sum(self.camera_ng_flags.values()) > 0:
            self.total_ng_count += sum(self.camera_ng_flags.values())  # Add NG counts from cameras that flagged NG during this inspection
        else:
            self.total_ok_count += 1  # Increment OK counter only if no NG was detected

        self.update_total_counters()

        for position in self.status_labels:
            if self.camera_ng_flags[position]:
                self.update_status(position, "NG Detected", "red")
            else:
                self.update_status(position, "OK (Inspection Finished)", "green")

        self.update_graph()

    def toggle_start_button_color(self):
        if self.inspection_running:
            self.blink_state = not self.blink_state
            if self.blink_state:
                self.start_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #FF0000; color: white;")  # Red color
            else:
                self.start_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")  # Green color

    def camera_thread(self, position, index):
        cap = None
        try:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                raise Exception(f"Failed to connect to {position} camera.")
        except Exception as e:
            print(f"Error: {e}")
            self.update_status(position, "Connection Failed", "red")
            return

        while True:
            ret, frame = cap.read()
            if ret:
                frame_with_boxes, detected_classes = self.perform_detection(frame)

                # Update GUI
                self.update_camera_feed(position, frame_with_boxes)

                if self.inspection_running:
                    # Check if NG is detected and hasn't been counted yet
                    if "person" in detected_classes and not self.camera_ng_flags[position]:  # "class2" is NG
                        self.camera_ng_flags[position] = True  # Flag NG for this camera
                        self.ng_counts[position] += 1  # Increment NG count for the specific camera
                        self.update_ng_label(position)
                        self.update_status(position, "NG Detected", "red")
                        self.capture_thumbnail(frame)  # Capture the frame as a thumbnail
                    elif "class1" in detected_classes:  # "class1" is OK
                        self.update_status(position, "OK", "green")
                    else:
                        self.update_status(position, "No Detection", "gray")
            else:
                self.update_status(position, "Disconnected", "red")
                break

        cap.release()

    def perform_detection(self, frame):
        # Perform YOLOv8 inference
        results = model.predict(frame, conf=0.5, verbose=False)
        detected_classes = []

        for detection in results[0].boxes.data:
            # Extract bounding box coordinates, confidence, and class ID
            x1, y1, x2, y2, conf, class_id = detection
            class_id = int(class_id)  # Convert class ID to integer
            class_name = model.names[class_id]  # Get class name
            detected_classes.append(class_name)

            # Draw bounding box and label on the frame
            color = (0, 255, 0) if class_name == "class1" else (0, 0, 255)  # Green for class1, red for class2
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            label = f"{class_name} {conf:.2f}"
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame, detected_classes

    def capture_thumbnail(self, frame):
        # Convert the frame to QImage and then to QPixmap for display as thumbnail
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Add the pixmap to the thumbnails list
        self.ng_thumbnails.append(pixmap)
        if len(self.ng_thumbnails) > 4:  # Keep only the last 4 thumbnails
            self.ng_thumbnails.pop(0)

        # Update the thumbnail labels
        for i, label in enumerate(self.thumbnail_labels):
            if i < len(self.ng_thumbnails):
                label.setPixmap(self.ng_thumbnails[i])
            else:
                label.clear()  # Clear unused labels

    def update_camera_feed(self, position, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        self.camera_labels[position].setPixmap(pixmap)

    def update_status(self, position, status, color):
        self.status_labels[position].setText(status)
        self.status_labels[position].setStyleSheet(f"background-color: {color}; color: white; font-size: 16px; font-weight: bold;")

    def update_ng_label(self, position):
        self.ng_count_labels[position].setText(f"{position} NG = {self.ng_counts[position]} Pcs")

    def update_total_counters(self):
        self.total_ok_label.setText(f"Total OK = {self.total_ok_count} Pcs")
        self.total_ng_label.setText(f"Total NG = {self.total_ng_count} Pcs")

    def update_graph(self):
        ax = self.figure.add_subplot(111)
        ax.clear()  # Clear the previous graph

        # Plot inspection durations
        ax.plot(range(1, len(self.inspection_durations) + 1), self.inspection_durations, marker="o", color="b", label="Inspection Duration")

        # Plot start-to-start durations
        if len(self.start_to_start_times) > 0:
            ax.plot(range(1, len(self.start_to_start_times) + 1), self.start_to_start_times, marker="x", color="g", label="Start-to-Start Time")

        # Add grid to the graph
        ax.grid(True, which="both", linestyle="--", linewidth=0.5)

        ax.set_title("Inspection Durations and Start-to-Start Times")
        ax.set_ylabel("Duration (seconds)")
        ax.set_xlim(1, max(len(self.inspection_durations), len(self.start_to_start_times)))  # Limit X-axis dynamically
        ax.set_ylim(0, 240)  # Set Y-axis limit to a maximum of 240 seconds
        ax.set_xticks([])  # Remove X-axis labels
        ax.set_yticks(range(0, 241, 20))  # Y-axis ticks every 20 seconds
        ax.legend(loc="upper right")  # Add a legend to distinguish the lines
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
