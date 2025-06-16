import cv2
from ultralytics import YOLO
from PySide6.QtGui import QImage, QPixmap

class YoloDetection:
    def __init__(self, model_path, cvalue, device="cpu"):
        """
        Initialize the YOLO Detection class.
        :param model_path: Path to the YOLO model (.pt file).
        :param cvalue: Confidence threshold for detections.
        :param device: Device to run the model on ("cpu" or "cuda").
        """
        self.cap = cv2.VideoCapture(0)  # Open the camera
        self.model = YOLO(model_path)  # Load YOLO model
        self.conf = cvalue  # Set confidence threshold
        self.device = device  # Set device for inference (cpu/cuda)

    def process_frame(self):
        """
        Capture a single frame from the camera, run YOLO detection, and return the annotated frame and detected classes.
        :return: A tuple of (annotated QPixmap, detected classes).
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame from camera.")
            return None, []

        # Run YOLO detection
        try:
            results = self.model.predict(frame, save=False, imgsz=320, conf=self.conf, device=self.device)
        except Exception as e:
            print(f"Error during model prediction: {e}")
            return None, []

        # Extract detected classes
        detected_classes = [self.model.names[int(result.cls)] for result in results[0].boxes]  # Extract class names

        # Annotate detections on the frame
        annotated_frame = results[0].plot()  # Annotated frame with bounding boxes
        return self.convert_frame_to_pixmap(annotated_frame), detected_classes

    def convert_frame_to_pixmap(self, frame):
        """
        Convert OpenCV frame to QPixmap for PySide6 QLabel display.
        :param frame: OpenCV frame.
        :return: QPixmap object.
        """
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        # Convert frame color format from BGR (OpenCV) to RGB (Qt)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return QPixmap.fromImage(QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888))

    def release_camera(self):
        """
        Release the camera resource.
        """
        self.cap.release()

