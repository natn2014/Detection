import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
from math import atan2, degrees
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QTimer


class GaugeReaderApp(QMainWindow):
    def __init__(self, model_path, video_path):
        super().__init__()
        self.setWindowTitle("Analog Gauge Reader")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Video label to display the video feed
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)

        # Table widget to display gauge values
        self.table_widget = QTableWidget(self)
        self.table_widget.setRowCount(1)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(['Min Value', 'Max Value', 'Current Value', 'Converted Value'])
        self.layout.addWidget(self.table_widget)

        # Load YOLO model
        self.model = YOLO(model_path)

        # Initialize EasyOCR reader
        self.reader = easyocr.Reader(['en'])

        # Video capture
        self.cap = cv2.VideoCapture(video_path)

        # Timer to refresh video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(30)  # Refresh every 30 ms
        
    def calculate_distance(self, point1, point2):
        """
        Calculate the Euclidean distance between two points.
        """
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def sanitize_ocr_result(self, ocr_result):
        """
        Sanitize the OCR result to extract a valid float value.
        """
        if not ocr_result:
            return None
        try:
            # Attempt to clean and convert the value
            raw_text = ocr_result[0][1]  # Extract the OCR-detected text
            sanitized_text = raw_text.replace("~", "").replace(",", "").strip()  # Remove unwanted characters
            return float(sanitized_text)
        except ValueError:
            return None  # Return None if conversion fails

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.cap.release()
            return

        # Process the current frame
        results = self.model(frame, verbose=True)
        detections = results[0].boxes.data

        # Initialize dictionaries to store detected positions
        positions = {}
        for detection in detections:
            class_id = int(detection[5])  # Class ID
            x1, y1, x2, y2 = detection[:4]
            x, y = int((x1 + x2) / 2), int((y1 + y2) / 2)  # Get center point
            if class_id == 0:  # Start
                positions['Center'] = (x, y) #should be center
            elif class_id == 1:  # End
                positions['Start'] = (x, y)
            elif class_id == 2:  # Center
                positions['End'] = (x, y) #should be start
            elif class_id == 3:  # Tip
                positions['Tip'] = (x, y)

        # Ensure all required components are detected
        if not all(key in positions for key in ['Center', 'Start', 'End', 'Tip']):
            self.display_frame(frame)
            return
        # Ensure Start and End are not too close
        if self.calculate_distance(positions['Start'], positions['End']) < 50:
            self.display_frame(frame)
            return

        gauge_min_value = 0.0  # Default to -1.0 if OCR fails
        gauge_max_value = 100  # Default to 1.0 if OCR fails

        # Calculate angles
        def calculate_angle(point1, point2, center):
            dx1, dy1 = point1[0] - center[0], point1[1] - center[1]
            dx2, dy2 = point2[0] - center[0], point2[1] - center[1]
            angle1 = degrees(atan2(dy1, dx1))
            angle2 = degrees(atan2(dy2, dx2))
            print(f"Angle1: {angle1}, Angle2: {angle2}")  # Debugging output
            return (angle2 - angle1) % 360

        center = positions['Center']
        angle_start_to_tip = calculate_angle(positions['Start'], positions['Tip'], center)
        angle_start_to_end = calculate_angle(positions['Start'], positions['End'], center)

        # Convert angles to gauge values
        gauge_range = gauge_max_value - gauge_min_value
        if angle_start_to_end == 0:  # Prevent division by zero
            gauge_current_value = gauge_min_value
        else:
            current_value_ratio = angle_start_to_tip / angle_start_to_end
            gauge_current_value = gauge_min_value + current_value_ratio * gauge_range

        # Update table widget
        self.table_widget.setItem(0, 0, QTableWidgetItem(f"{gauge_min_value:.2f}%"))
        self.table_widget.setItem(0, 1, QTableWidgetItem(f"{gauge_max_value:.2f}%"))
        self.table_widget.setItem(0, 2, QTableWidgetItem(f"{gauge_current_value:.2f}%"))
        self.table_widget.setItem(0, 3, QTableWidgetItem(f"{self.convert_gauge_values(gauge_current_value):.2f}"))



        # Display the frame with annotations
        annotated_frame = frame.copy()
        for key, (x, y) in positions.items():
            color = (0, 255, 0) if key == 'Tip' else (255, 0, 0)
            cv2.circle(annotated_frame, (x, y), 5, color, -1)
            cv2.putText(annotated_frame, key, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        self.display_frame(annotated_frame)

    def display_frame(self, frame):
        # Convert the frame to QImage and display it in the QLabel
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.video_label.setPixmap(pixmap)


    def convert_gauge_values(self, gauge_current_value):
        # Convert using 1 - (gauge_current_value/100)
        converted_value = 1 - (gauge_current_value / 100)
        return converted_value

if __name__ == "__main__":
    import sys

    # Path to YOLO model and video file
    model_path = "best.pt"
    video_path = "gauge_video.mp4"

    # Application setup
    app = QApplication(sys.argv)
    main_window = GaugeReaderApp(model_path, video_path)
    main_window.show()
    sys.exit(app.exec())
