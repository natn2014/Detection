import sys
import time
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


ALLOWED_FPS = [24, 30, 60]


def find_cameras(max_index: int = 10) -> List[int]:
    available = []
    for idx in range(max_index):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            available.append(idx)
            cap.release()
        else:
            cap.release()
    return available


def nearest_allowed_fps(value: float) -> int:
    if value <= 1:
        return 30
    return min(ALLOWED_FPS, key=lambda x: abs(x - value))


class VideoWorker(QThread):
    frame_ready = Signal(QImage, list)
    status = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._running = False
        self._camera_index: Optional[int] = None
        self._model_path: Optional[Path] = None
        self._model = None
        self._target_fps: int = 30

    def set_camera_index(self, index: Optional[int]) -> None:
        self._camera_index = index

    def set_model_path(self, path: Optional[Path]) -> None:
        self._model_path = path
        self._model = None

    def stop(self) -> None:
        self._running = False

    def _load_model(self) -> None:
        if self._model_path is None:
            return
        if YOLO is None:
            self.status.emit("Ultralytics not available. Install requirements.")
            return
        try:
            self._model = YOLO(str(self._model_path))
            self.status.emit(f"Model loaded: {self._model_path.name}")
        except Exception as exc:
            self.status.emit(f"Model load failed: {exc}")
            self._model = None

    def _extract_detections(self, results) -> List[dict]:
        detections: List[dict] = []
        if results is None:
            return detections
        boxes = results.boxes
        names = results.names
        if boxes is None:
            return detections
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item()) if box.conf is not None else 0.0
            class_name = str(names.get(cls_id, cls_id))
            label = f"{class_name} {conf:.2f}"
            x1, y1, x2, y2 = xyxy.tolist()
            detections.append(
                {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "label": label,
                    "class_name": class_name,
                }
            )
        return detections

    def run(self) -> None:
        if self._camera_index is None:
            self.status.emit("Select a camera.")
            return

        cap = cv2.VideoCapture(self._camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.status.emit("Camera open failed.")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        self._target_fps = nearest_allowed_fps(fps)
        self.status.emit(f"Camera FPS: {fps:.2f} -> Target FPS: {self._target_fps}")

        if self._model_path is not None and self._model is None:
            self._load_model()

        self._running = True
        frame_period = 1.0 / self._target_fps

        while self._running:
            start_time = time.perf_counter()

            ret, frame = cap.read()
            if not ret:
                self.status.emit("Frame grab failed.")
                break

            detections = []
            if self._model is not None:
                try:
                    results = self._model(frame, verbose=False)[0]
                except Exception as exc:
                    self.status.emit(f"Inference error: {exc}")
                    results = None
                detections = self._extract_detections(results)

            elapsed = time.perf_counter() - start_time

            if elapsed < frame_period:
                time.sleep(frame_period - elapsed)
            else:
                frames_to_skip = int(elapsed / frame_period) - 1
                for _ in range(max(0, frames_to_skip)):
                    cap.grab()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_ready.emit(image, detections)

        cap.release()
        self.status.emit("Stopped.")


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("YOLO Object Detection Concept")
        self._worker = VideoWorker()
        self._worker.frame_ready.connect(self.on_frame)
        self._worker.status.connect(self.on_status)
        self._class_counts = {}
        self._class_colors = {}
        self._current_pixmap = None
        self._selected_classes = set()
        self._confidence_threshold = 0.0
        self._model_classes = []  # Store all classes from model

        self.model_label = QLabel("No model selected")
        self.load_model_button = QPushButton("Load .pt Model")
        self.load_model_button.clicked.connect(self.load_model)

        self.camera_combo = QComboBox()
        self.scan_button = QPushButton("Scan Cameras")
        self.scan_button.clicked.connect(self.scan_cameras)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_stream)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_stream)
        self.capture_button = QPushButton("Capture Frame")
        self.capture_button.clicked.connect(self.capture_frame)

        self.status_label = QLabel("Ready")
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 360)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Class", "Count"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumWidth(220)

        # Filter panel
        filter_label = QLabel("<b>Filters</b>")
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(0)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(0)
        self.confidence_slider.setTickPosition(QSlider.TicksBelow)
        self.confidence_slider.setTickInterval(10)
        self.confidence_slider.valueChanged.connect(self.on_confidence_changed)
        
        self.confidence_label = QLabel("Confidence: 0%")
        
        # Scrollable class filters
        self.class_filters_scroll = QScrollArea()
        self.class_filters_scroll.setWidgetResizable(True)
        self.class_filters_container = QWidget()
        self.class_filters_layout = QVBoxLayout()
        self.class_filters_container.setLayout(self.class_filters_layout)
        self.class_filters_scroll.setWidget(self.class_filters_container)
        self.class_filters_scroll.setMinimumHeight(200)
        
        filter_panel_layout = QVBoxLayout()
        filter_panel_layout.addWidget(filter_label)
        filter_panel_layout.addWidget(QLabel("Confidence Threshold:"))
        filter_panel_layout.addWidget(self.confidence_slider)
        filter_panel_layout.addWidget(self.confidence_label)
        filter_panel_layout.addSpacing(10)
        filter_panel_layout.addWidget(QLabel("Classes to Show:"))
        filter_panel_layout.addWidget(self.class_filters_scroll, 1)
        
        filter_widget = QWidget()
        filter_widget.setLayout(filter_panel_layout)
        filter_widget.setMaximumWidth(220)

        top_row = QHBoxLayout()
        top_row.addWidget(self.load_model_button)
        top_row.addWidget(self.model_label, 1)

        cam_row = QHBoxLayout()
        cam_row.addWidget(QLabel("Camera:"))
        cam_row.addWidget(self.camera_combo)
        cam_row.addWidget(self.scan_button)
        cam_row.addWidget(self.start_button)
        cam_row.addWidget(self.stop_button)
        cam_row.addWidget(self.capture_button)

        content_row = QHBoxLayout()
        content_row.addWidget(self.video_label, 1)
        
        sidebar = QVBoxLayout()
        sidebar.addWidget(filter_widget)
        sidebar.addWidget(self.table)
        
        content_row.addLayout(sidebar)

        layout = QVBoxLayout()
        layout.addLayout(top_row)
        layout.addLayout(cam_row)
        layout.addLayout(content_row, 1)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.scan_cameras()

    @Slot()
    def scan_cameras(self) -> None:
        self.camera_combo.clear()
        cameras = find_cameras()
        if not cameras:
            self.camera_combo.addItem("No camera", None)
            return
        for idx in cameras:
            self.camera_combo.addItem(f"Camera {idx}", idx)

    @Slot()
    def load_model(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select YOLO .pt Model",
            "",
            "PyTorch Model (*.pt)",
        )
        if not file_path:
            return
        model_path = Path(file_path)
        self.model_label.setText(model_path.name)
        self._worker.set_model_path(model_path)
        self.status_label.setText("Loading model...")
        
        # Load model to extract class names
        if YOLO is not None:
            try:
                model = YOLO(str(model_path))
                self._model_classes = list(model.names.values())
                self._populate_class_filters()
                self.status_label.setText(f"Model loaded: {len(self._model_classes)} classes")
            except Exception as exc:
                self.status_label.setText(f"Failed to load model: {exc}")
                self._model_classes = []
        else:
            self.status_label.setText("Ultralytics not available.")
            self._model_classes = []

    def _populate_class_filters(self) -> None:
        """Create checkboxes for all model classes."""
        # Clear existing checkboxes
        while self.class_filters_layout.count() > 0:
            item = self.class_filters_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self._selected_classes.clear()
        
        # Create checkbox for each class
        for class_name in sorted(self._model_classes):
            checkbox = QCheckBox(class_name)
            checkbox.setChecked(True)
            checkbox.toggled.connect(
                lambda checked, cn=class_name: self._toggle_class_filter(cn, checked)
            )
            self.class_filters_layout.addWidget(checkbox)
            self._selected_classes.add(class_name)

    @Slot()
    def start_stream(self) -> None:
        if self._worker.isRunning():
            self.status_label.setText("Already running.")
            return
        index = self.camera_combo.currentData()
        if index is None:
            self.status_label.setText("Select a valid camera.")
            return
        self._worker.set_camera_index(int(index))
        self._worker.start()

    @Slot()
    def stop_stream(self) -> None:
        if self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(2000)

    @Slot()
    def capture_frame(self) -> None:
        if self._current_pixmap is None:
            self.status_label.setText("No frame to capture.")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Captured Frame",
            "",
            "Images (*.png *.jpg *.bmp)",
        )
        if not file_path:
            return
        if self._current_pixmap.save(file_path):
            self.status_label.setText(f"Frame saved: {Path(file_path).name}")
        else:
            self.status_label.setText("Frame save failed.")

    @Slot(int)
    def on_confidence_changed(self, value: int) -> None:
        self._confidence_threshold = value / 100.0
        self.confidence_label.setText(f"Confidence: {value}%")

    def _toggle_class_filter(self, class_name: str, checked: bool) -> None:
        if checked:
            self._selected_classes.add(class_name)
        else:
            self._selected_classes.discard(class_name)

    @Slot(QImage, list)
    def on_frame(self, image: QImage, detections: list) -> None:
        pixmap = QPixmap.fromImage(image)
        
        # Filter detections based on selected classes and confidence threshold
        filtered_detections = []
        for det in detections:
            class_name = det.get("class_name", "unknown")
            conf = float(det["label"].split()[-1]) if " " in det["label"] else 0.0
            
            # Filter by selected classes and confidence
            if class_name in self._selected_classes and conf >= self._confidence_threshold:
                filtered_detections.append(det)
        
        detections = filtered_detections  # Use filtered for drawing and table
        
        if detections:
            # Assign colors to each detection based on class name
            for det in detections:
                class_name = det.get("class_name", "unknown")
                if class_name not in self._class_colors:
                    hue = (len(self._class_colors) * 37) % 360
                    self._class_colors[class_name] = QColor.fromHsv(hue, 200, 255)
                det["color"] = self._class_colors[class_name]
            
            painter = QPainter(pixmap)
            pen = QPen()
            pen.setWidth(2)
            for det in detections:
                color = det.get("color", Qt.green)
                pen.setColor(color)
                painter.setPen(pen)
                x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]
                painter.drawRect(x1, y1, x2 - x1, y2 - y1)
                painter.drawText(x1, max(0, y1 - 6), det["label"])
            painter.end()
        self._current_pixmap = pixmap
        self.video_label.setPixmap(pixmap)
        self._update_class_table(detections)

    def _update_class_table(self, detections: list) -> None:
        self._class_counts.clear()
        for det in detections:
            class_name = det.get("class_name", "unknown")
            self._class_counts[class_name] = self._class_counts.get(class_name, 0) + 1

        self.table.setRowCount(len(self._class_counts))
        for row, (class_name, count) in enumerate(sorted(self._class_counts.items())):
            color = self._class_colors.get(class_name, Qt.white)

            class_item = QTableWidgetItem(class_name)
            count_item = QTableWidgetItem(str(count))
            brush = QBrush(color)
            class_item.setForeground(brush)
            count_item.setForeground(brush)

            self.table.setItem(row, 0, class_item)
            self.table.setItem(row, 1, count_item)

    @Slot(str)
    def on_status(self, message: str) -> None:
        self.status_label.setText(message)

    def closeEvent(self, event) -> None:
        self.stop_stream()
        super().closeEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(960, 640)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
