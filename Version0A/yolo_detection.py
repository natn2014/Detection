import cv2
from ultralytics import YOLO
from PySide6.QtGui import QImage, QPixmap

class YoloDetection:
    def __init__(self, model_path, cvalue=0.6, device="cpu"):
        """
        Initialize the YOLO Detection class.
        :param model_path: Path to the YOLO model (.pt file).
        :param cvalue: Confidence threshold for detections.
        :param device: Device to run the model on ("cpu" or "cuda").
        """
        model_path = "yolov8n.pt"
        self.model = YOLO(model_path)  # Load YOLO model
        self.conf = cvalue
        print(self.conf)
        self.device = device  # Set device for inference (cpu/cuda)

    def process_frame(self, frame):
        """
        Process a frame with YOLO detection
        :param frame: Input frame to process
        :return: Original frame and results for drawing annotations
        """
        try:
            results = self.model.predict(frame, save=False, imgsz=320, conf=self.conf, device=self.device)
            return frame, results
        except Exception as e:
            print(f"Error during model prediction: {e}")
            return None, None

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
