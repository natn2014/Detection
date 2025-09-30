import sys
import cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialogButtonBox
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer
from ShowerTest_UI import Ui_MainWindow  # Import the generated UI class
from yolo_detection import YoloDetection
import time
import threading
from datetime import datetime


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

        self.recording_state = {}
        self.camera_streams = {}
        self.setup_connections()
        self.auto_connect_cameras()

        self.is_recording = False
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_record_button)
        self.blink_state = False

    def setup_connections(self):
        # Connect buttons to camera control functions
        self.ui.pushButton_CAM1.clicked.connect(lambda: self.toggle_camera("CAM1"))
        self.ui.pushButton_CAM2.clicked.connect(lambda: self.toggle_camera("CAM2"))
        self.ui.pushButton_CAM3.clicked.connect(lambda: self.toggle_camera("CAM3"))
        self.ui.pushButton_CAM4.clicked.connect(lambda: self.toggle_camera("CAM4"))
        # Replace buttonBox connection with pushButton_RecordVideo
        self.ui.pushButton_RecordVideo.clicked.connect(self.toggle_recording)

    def toggle_recording(self):
        """Toggle recording state for all active cameras"""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.ui.pushButton_RecordVideo.setText("Stop Recording")
            # Start blinking effect
            self.blink_timer.start(500)  # Blink every 500ms
            # Start recording for all active cameras
            for camera_id in self.cameras.keys():
                if camera_id in self.camera_streams:
                    self.start_recording(camera_id)
        else:
            # Stop recording
            self.is_recording = False
            self.ui.pushButton_RecordVideo.setText("Record Video")
            # Stop blinking effect
            self.blink_timer.stop()
            self.ui.pushButton_RecordVideo.setStyleSheet("")
            # Stop recording for all active cameras
            for camera_id in self.cameras.keys():
                if camera_id in self.recording_state:
                    self.stop_recording(camera_id)

    def blink_record_button(self):
        """Toggle button background color for blinking effect"""
        if self.blink_state:
            self.ui.pushButton_RecordVideo.setStyleSheet("background-color: red;")
        else:
            self.ui.pushButton_RecordVideo.setStyleSheet("background-color: none;")
        self.blink_state = not self.blink_state

    def auto_connect_cameras(self):
        for camera_id in self.cameras.keys():
            time.sleep(1)  # Delay to ensure camera is ready
            self.start_camera(camera_id)

    def toggle_camera(self, camera_id):
        if camera_id in self.camera_streams:
            self.stop_camera(camera_id)
        else:
            self.start_camera(camera_id)

    def start_camera(self, camera_id):
        camera_index = self.cameras[camera_id]["index"]
        label = self.cameras[camera_id]["label"]
        label.setText("Connecting...")
        # Open camera stream
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Failed to open {camera_id}")
            return

        self.camera_streams[camera_id] = cap

        # Initialize YOLO detection for this camera
        try:
            yolo_detector = YoloDetection("yolov8n.pt", cvalue=0.6)  # You can adjust confidence value here
            self.cameras[camera_id]["yolo"] = yolo_detector
        except Exception as e:
            print(f"Failed to initialize YOLO for {camera_id}: {e}")

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

            # Remove YOLO detector
            if "yolo" in self.cameras[camera_id]:
                del self.cameras[camera_id]["yolo"]

            # Clear video feed
            self.cameras[camera_id]["label"].clear()
            label = self.cameras[camera_id]["label"]
            label.setText("Paused")

    def update_video_feed(self, camera_id):
        if camera_id not in self.camera_streams:
            return

        cap = self.camera_streams[camera_id]
        ret, frame = cap.read()
        if not ret:
            return

        # Perform YOLO detection
        try:
            pixmap, results = self.cameras[camera_id]["yolo"].process_frame(frame)
            
            # Get detections and print results
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    name = r.names[cls]
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Draw bounding box and label on frame
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    label = f"{name}: {conf:.2f}"
                    cv2.putText(frame, label, (int(x1), int(y1-10)), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    print(f"{camera_id} Detection: {name}, Confidence: {conf:.2f}")

            # Convert annotated frame to QPixmap and display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            image = QImage(frame_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.cameras[camera_id]["label"].setPixmap(pixmap)
            
        except Exception as e:
            print(f"Error in YOLO detection for {camera_id}: {e}")

    # Save Video stream function when clicked
    def start_recording(self, camera_id):
        if camera_id not in self.camera_streams:
            print(f"{camera_id} is not active.")
            return
        
        if camera_id in self.recording_state:
            print(f"{camera_id} is already recording.")
            return

        # Create and start recording thread
        recording_thread = threading.Thread(
            target=self._record_video,
            args=(camera_id,),
            daemon=True
        )
        self.recording_state[camera_id] = True
        recording_thread.start()

    def stop_recording(self, camera_id):
        if camera_id in self.recording_state:
            self.recording_state[camera_id] = False

    def _record_video(self, camera_id):
        """Helper method to handle video recording in a separate thread"""
        try:
            cap = self.camera_streams[camera_id]
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H_%M")
            filename = f'{camera_id}_output_{timestamp}.avi'
            out = cv2.VideoWriter(filename, fourcc, 24.0, (640, 480))

            while self.recording_state.get(camera_id, False):
                ret, frame = cap.read()
                if not ret:
                    break
                # Add YOLO detection boxes to the recorded video
                try:
                    if "yolo" in self.cameras[camera_id]:
                        _, results = self.cameras[camera_id]["yolo"].process_frame(frame)
                        for r in results:
                            for box in r.boxes:
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                cls = int(box.cls[0])
                                conf = float(box.conf[0])
                                name = r.names[cls]
                                
                                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                                label = f"{name}: {conf:.2f}"
                                cv2.putText(frame, label, (int(x1), int(y1-10)), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                except Exception as e:
                    print(f"Error adding YOLO detection to recording: {e}")
                
                out.write(frame)

            out.release()
            print(f"Video stream from {camera_id} saved successfully as {filename}")
            
            # Show popup dialog in the main thread
            QTimer.singleShot(0, lambda: self._show_save_complete_dialog(camera_id, filename))
            
        except Exception as e:
            print(f"Error saving video stream from {camera_id}: {e}")
            # Show error dialog in the main thread
            QTimer.singleShot(0, lambda: self._show_error_dialog(camera_id, str(e)))
        finally:
            if camera_id in self.recording_state:
                del self.recording_state[camera_id]

    def _show_save_complete_dialog(self, camera_id, filename):
        """Show a popup dialog when video saving is complete"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Video Saved Successfully")
        msg.setInformativeText(f"Camera: {camera_id}\nFilename: {filename}")
        msg.setWindowTitle("Save Complete")
        msg.exec()

    def _show_error_dialog(self, camera_id, error_message):
        """Show a popup dialog when video saving encounters an error"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Error Saving Video")
        msg.setInformativeText(f"Camera: {camera_id}\nError: {error_message}")
        msg.setWindowTitle("Save Error")
        msg.exec()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiCameraApp()
    window.show()
    sys.exit(app.exec())
