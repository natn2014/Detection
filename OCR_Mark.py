import sys
import time
import cv2
import easyocr
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap, QColor
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QPushButton, QWidget, QTableWidget, QTableWidgetItem


class VideoOCRApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize EasyOCR Reader
        self.reader = easyocr.Reader(['en'])

        # Set up the GUI layout
        self.setWindowTitle("Real-Time OCR with PySide6 and Text Comparison")
        self.setGeometry(100, 100, 1000, 600)

        self.video_label = QLabel(self)  # Label to display the video feed
        self.video_label.setAlignment(Qt.AlignCenter)

        self.ocr_button = QPushButton("Perform OCR", self)  # Button to trigger OCR
        self.ocr_button.clicked.connect(self.perform_ocr)

        # QTableWidget to display and compare texts
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalHeaderLabels(["Text to Compare"])
        self.table_widget.setRowCount(0)
        self.populate_table()  # Fill the table with sample data

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.ocr_button)
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Unable to access the camera.")
            sys.exit()

        # Timer to update the video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms (approx. 33 FPS)

        # State to manage OCR processing
        self.is_ocr_processing = False

    def populate_table(self):
        """Populate the QTableWidget with sample data."""
        sample_texts = ["HELLO", "WORLD", "PYTHON", "OCR", "EASYOCR"]
        for text in sample_texts:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(text))

    def update_frame(self):
        if not self.is_ocr_processing:
            ret, frame = self.cap.read()
            if ret:
                # Convert the frame to QImage for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))
            else:
                print("Error: Unable to read frame.")

    def perform_ocr(self):
        if self.is_ocr_processing:
            return  # Avoid multiple button presses while processing

        self.is_ocr_processing = True

        # Freeze the current frame
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Unable to capture frame.")
            self.is_ocr_processing = False
            return

        # Perform OCR on the frame
        results = self.reader.readtext(frame, detail=1, paragraph=False)
        for (bbox, text, _) in results:
            # Capitalize the recognized text
            capitalized_text = text.upper()

            # Compare the capitalized text with the table
            self.compare_with_table(capitalized_text)

            # Draw a rectangle around the detected text
            (top_left, bottom_right) = bbox[0], bbox[2]
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

            # Put the capitalized text above the rectangle
            cv2.putText(
                frame,
                capitalized_text,
                (top_left[0], top_left[1] - 10),  # Slightly above the rectangle
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        # Display the frame with OCR results
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

        # Wait for 2 seconds before resuming the video feed
        QTimer.singleShot(2000, self.resume_video_feed)

    def compare_with_table(self, capitalized_text):
        """Compare OCR result with items in the table."""
        found_match = False

        # Check each row in the table for a match
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)
            if item:
                table_text = item.text()
                if capitalized_text == table_text:
                    # Match found, change background to green
                    item.setBackground(QColor(Qt.green))
                    found_match = True
                    print(f"Match found: {capitalized_text} in table.")
                    break

        if not found_match:
            # Split capitalized_text into smaller words and compare
            words = capitalized_text.split(" ")
            for word in words:
                for row in range(self.table_widget.rowCount()):
                    item = self.table_widget.item(row, 0)
                    if item:
                        table_text = item.text()
                        if word == table_text:
                            # Match found, change background to green
                            print(f"Partial match found: {word} in table.")
                            

    def resume_video_feed(self):
        self.is_ocr_processing = False

    def closeEvent(self, event):
        # Release the video capture and close the application
        self.cap.release()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoOCRApp()
    window.show()
    sys.exit(app.exec())
