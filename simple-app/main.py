import sys
import cv2
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer
from ShowerTest_UI import Ui_MainWindow  # Import the generated UI class


class MultiCameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Camera connections
        self.cameras = {
            "CAM1": {"index": 0, "label": self.ui.label_CAM1_VideoLabel},
            "CAM2": {"index": 1, "label": self.ui.label_CAM2_VideoLabel},
            "CAM3": {"index": 2, "label": self.ui.label_CAM3_VideoLabel},
            "CAM4": {"index": 3, "label": self.ui.label_CAM4_VideoLabel},
        }

        self.camera_streams = {}
        self.setup_connections()

    def setup_connections(self):
        # Connect buttons to camera control functions
        self.ui.pushButton_CAM1.clicked.connect(lambda: self.toggle_camera("CAM1"))
        self.ui.pushButton_CAM2.clicked.connect(lambda: self.toggle_camera("CAM2"))
        self.ui.pushButton_CAM3.clicked.connect(lambda: self.toggle_camera("CAM3"))
        self.ui.pushButton_CAM4.clicked.connect(lambda: self.toggle_camera("CAM4"))

    def toggle_camera(self, camera_id):
        if camera_id in self.camera_streams:
            self.stop_camera(camera_id)
        else:
            self.start_camera(camera_id)

    def start_camera(self, camera_id):
        camera_index = self.cameras[camera_id]["index"]
        label = self.cameras[camera_id]["label"]

        # Open camera stream
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Failed to open {camera_id}")
            return

        self.camera_streams[camera_id] = cap

        # Start timer to update video feed
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.update_video_feed(camera_id))
        timer.start(30)  # Refresh rate: 30ms
        self.cameras[camera_id]["timer"] = timer

    def stop_camera(self, camera_id):
        if camera_id in self.camera_streams:
            # Stop timer
            self.cameras[camera_id]["timer"].stop()

            # Release camera stream
            self.camera_streams[camera_id].release()
            del self.camera_streams[camera_id]

            # Clear video feed
            self.cameras[camera_id]["label"].clear()

    def update_video_feed(self, camera_id):
        if camera_id not in self.camera_streams:
            return

        cap = self.camera_streams[camera_id]
        ret, frame = cap.read()
        if not ret:
            return

        # Convert frame to QPixmap and display
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        image = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        self.cameras[camera_id]["label"].setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiCameraApp()
    window.show()
    sys.exit(app.exec())
