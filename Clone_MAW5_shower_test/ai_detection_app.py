#!/usr/bin/env python3
"""
AI Object Detection Application with YOLO
Dual USB Camera System with Relay Control Integration
"""

import sys
import cv2
import numpy as np
import time
import threading
import glob
import socket
from queue import Queue, Empty
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QTextEdit, QGridLayout,
    QDialog, QDialogButtonBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, Slot, QRect, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QFont, QFontMetrics

# YOLO imports
try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
    CUDA_AVAILABLE = torch.cuda.is_available()
    print(f"✓ Ultralytics YOLO loaded successfully")
    print(f"✓ PyTorch CUDA: {CUDA_AVAILABLE}")
except ImportError as e:
    print(f"Warning: Ultralytics not available: {e}")
    print("Install with: pip3 install ultralytics")
    YOLO_AVAILABLE = False
    CUDA_AVAILABLE = False

# Relay imports
try:
    from Relay_b import Relay
    RELAY_AVAILABLE = True
    print("✓ Relay module loaded successfully")
except (ImportError, AttributeError) as e:
    RELAY_AVAILABLE = False
    print(f"Warning: Could not import Relay class from Relay_b.py: {e}")
    print("Relay functionality will be disabled. Create a proper Relay_b.py file to enable it.")
    
    # Create a dummy Relay class for testing without hardware
    class Relay:
        def __init__(self, host='192.168.1.254', port=4196, address=0x01):
            self.host = host
            self.port = port
            print(f"Using dummy Relay (no hardware connection to {host}:{port})")
            
        def connect(self):
            pass
            
        def disconnect(self):
            pass
            
        def is_DI_on(self, di_number):
            return False
            
        def on(self, channel):
            print(f"Dummy: Relay channel {channel} ON")
            
        def off(self, channel):
            print(f"Dummy: Relay channel {channel} OFF")
            
        def check_DI(self):
            return 0
            
        def status(self, channel):
            return False


class VideoLabel(QLabel):
    """Custom QLabel for displaying video with overlay annotations"""
    def __init__(self):
        super().__init__()
        self.detections = []
        self.detection_active = False
        self.has_object = False
        self.detection_count = 0
        self.original_frame_width = 320  # Original frame width from camera
        self.original_frame_height = 240  # Original frame height from camera
        
    def set_detections(self, detections, detection_active, has_object, frame_width=None, frame_height=None):
        """Update detection data for overlay"""
        self.detections = detections
        self.detection_active = detection_active
        self.has_object = has_object
        self.detection_count = len(detections)
        if frame_width is not None:
            self.original_frame_width = frame_width
        if frame_height is not None:
            self.original_frame_height = frame_height
        self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        """Override paint event to draw video frame and overlays"""
        super().paintEvent(event)
        
        if not self.pixmap():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Get the scaled pixmap dimensions
        pixmap = self.pixmap()
        label_size = self.size()
        pixmap_size = pixmap.size()
        
        # Calculate how the image was scaled to fit in the label (aspect ratio preserved)
        scale_w = label_size.width() / pixmap_size.width()
        scale_h = label_size.height() / pixmap_size.height()
        display_scale = min(scale_w, scale_h)
        
        # Calculate the actual displayed size and offset
        scaled_w = int(pixmap_size.width() * display_scale)
        scaled_h = int(pixmap_size.height() * display_scale)
        offset_x = (label_size.width() - scaled_w) // 2
        offset_y = (label_size.height() - scaled_h) // 2
        
        # Calculate scale from original frame to displayed size
        # Bounding boxes are in original frame coordinates (320x240)
        frame_to_display_scale_x = scaled_w / self.original_frame_width
        frame_to_display_scale_y = scaled_h / self.original_frame_height
        
        # Only draw detection overlays when detection is active
        if self.detection_active:
            # Draw detection bounding boxes
            for det in self.detections:
                if 'bbox' in det:
                    bbox = det['bbox']
                    x1, y1, x2, y2 = bbox
                    
                    # Scale coordinates from original frame to displayed size
                    x1 = int(x1 * frame_to_display_scale_x) + offset_x
                    y1 = int(y1 * frame_to_display_scale_y) + offset_y
                    x2 = int(x2 * frame_to_display_scale_x) + offset_x
                    y2 = int(y2 * frame_to_display_scale_y) + offset_y
                    
                    # Draw green bounding box
                    pen = QPen(QColor(0, 255, 0), 2)
                    painter.setPen(pen)
                    painter.drawRect(x1, y1, x2 - x1, y2 - y1)
                    
                    # Draw label background and text
                    label_text = f"{det['class']}: {det['confidence']:.2f}"
                    font = QFont("Arial", 10, QFont.Bold)
                    painter.setFont(font)
                    metrics = QFontMetrics(font)
                    text_width = metrics.horizontalAdvance(label_text)
                    text_height = metrics.height()
                    
                    # Draw label background (green)
                    painter.fillRect(x1, y1 - text_height - 4, text_width + 8, text_height + 4, QColor(0, 255, 0))
                    
                    # Draw label text (black)
                    painter.setPen(QColor(0, 0, 0))
                    painter.drawText(x1 + 4, y1 - 4, label_text)
        
            # Draw status badges
            # Detection Active badge (bottom right) - yellow with black text
            badge_text = "DETECTION ACTIVE"
            font = QFont("Arial", 11, QFont.Bold)
            painter.setFont(font)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(badge_text)
            text_height = metrics.height()
            
            badge_x = scaled_w + offset_x - text_width - 20
            badge_y = scaled_h + offset_y - text_height - 20
            
            # Draw badge background (yellow)
            painter.fillRect(badge_x - 5, badge_y - 5, text_width + 10, text_height + 10, QColor(255, 255, 0))
            
            # Draw badge text (black)
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(badge_x, badge_y + text_height - 5, badge_text)
            
            # Object Detected badge (top right) - red with white text
            if self.has_object and self.detection_count > 0:
                badge_text = f"OBJECT DETECTED ({self.detection_count})"
                font = QFont("Arial", 11, QFont.Bold)
                painter.setFont(font)
                metrics = QFontMetrics(font)
                text_width = metrics.horizontalAdvance(badge_text)
                text_height = metrics.height()
                
                badge_x = scaled_w + offset_x - text_width - 20
                badge_y = offset_y + 15
                
                # Draw badge background (red)
                painter.fillRect(badge_x - 5, badge_y - 5, text_width + 10, text_height + 10, QColor(255, 0, 0))
                
                # Draw badge text (white)
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(badge_x, badge_y + text_height - 5, badge_text)
        
        painter.end()


class CameraThread(QThread):
    """Thread for capturing frames from a USB camera"""
    frame_ready = Signal(np.ndarray, int)  # frame, camera_id
    error_signal = Signal(str)
    
    def __init__(self, camera_id, camera_index=0):
        super().__init__()
        self.camera_id = camera_id
        self.camera_index = camera_index
        self.running = False
        self.cap = None
        
    def run(self):
        """Main camera capture loop with retry logic"""
        self.running = True
        
        # Try to open camera with retries
        max_retries = 5
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            print(f"Camera {self.camera_id}: Opening /dev/video{self.camera_index} (attempt {attempt + 1}/{max_retries})...")
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if self.cap.isOpened():
                print(f"✓ Camera {self.camera_id} opened successfully")
                break
            
            print(f"Camera {self.camera_id}: Failed to open, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay *= 1.5  # Exponential backoff
        else:
            # All retries failed
            self.error_signal.emit(f"Camera {self.camera_id} (index {self.camera_index}) failed to open after {max_retries} attempts")
            return
            
        # Set camera properties for better performance (lower resolution to save memory)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(frame.copy(), self.camera_id)
            else:
                self.error_signal.emit(f"Camera {self.camera_id} failed to read frame")
                time.sleep(0.1)
                
    def stop(self):
        """Stop the camera thread"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.wait()


class YOLOInferenceThread(QThread):
    """Thread for YOLO inference"""
    detection_result = Signal(bool, list, int)  # has_object, detections, camera_id
    error_signal = Signal(str)
    
    def __init__(self, model_path, conf_threshold=0.25):
        super().__init__()
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.running = False
        self.frame_queue = Queue(maxsize=10)
        self.model = None
        self.yolo_available = YOLO_AVAILABLE
        
    def load_model(self):
        """Load YOLO model from file"""
        try:
            if not self.yolo_available:
                self.error_signal.emit("Ultralytics YOLO not available - running in dummy mode")
                return False
                
            if not Path(self.model_path).exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
                
            # Load YOLO model
            self.model = YOLO(self.model_path)
            
            # Move to GPU if available
            if CUDA_AVAILABLE:
                self.model.to('cuda:0')
                print(f"✓ YOLO model loaded on GPU")
            else:
                print(f"✓ YOLO model loaded on CPU")
            
            return True
            
        except Exception as e:
            self.error_signal.emit(f"YOLO model loading error: {str(e)}")
            return False
        
    def run(self):
        """Main inference loop"""
        self.running = True
        
        if not self.load_model():
            self.error_signal.emit("YOLO not available - detection disabled (camera feeds still work)")
            # Run in dummy mode - just consume frames without inference
            while self.running:
                try:
                    frame, camera_id = self.frame_queue.get(timeout=0.1)
                    # Emit dummy result (no detection)
                    self.detection_result.emit(False, [], camera_id)
                except Empty:
                    continue
                except Exception as e:
                    self.error_signal.emit(f"Error: {str(e)}")
            return
        
    def run(self):
        """Main inference loop"""
        self.running = True
        
        if not self.load_model():
            self.error_signal.emit("YOLO not available - detection disabled (camera feeds still work)")
            # Run in dummy mode - just consume frames without inference
            while self.running:
                try:
                    frame, camera_id = self.frame_queue.get(timeout=0.1)
                    # Emit dummy result (no detection)
                    self.detection_result.emit(False, [], camera_id)
                except Empty:
                    continue
                except Exception as e:
                    self.error_signal.emit(f"Error: {str(e)}")
            return
            
        while self.running:
            try:
                # Get frame from queue with timeout
                frame, camera_id = self.frame_queue.get(timeout=0.1)
                
                # Run YOLO inference
                device = 0 if CUDA_AVAILABLE else 'cpu'
                results = self.model(frame, verbose=False, device=device, conf=self.conf_threshold)
                
                # Extract detections
                detections = []
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        name = r.names[cls]
                        detections.append({
                            'class': name,
                            'confidence': conf,
                            'bbox': box.xyxy[0].cpu().numpy().tolist()
                        })
                
                has_object = len(detections) > 0
                self.detection_result.emit(has_object, detections, camera_id)
                
            except Empty:
                continue
            except Exception as e:
                self.error_signal.emit(f"Inference error: {str(e)}")
                
    def add_frame(self, frame, camera_id):
        """Add frame to inference queue"""
        if not self.frame_queue.full():
            self.frame_queue.put((frame, camera_id))
            
    def stop(self):
        """Stop the inference thread"""
        self.running = False
        self.wait()


class RelayMonitorThread(QThread):
    """Thread for monitoring relay DI signals"""
    di1_changed = Signal(bool)  # DI1 state (start signal)
    di2_changed = Signal(bool)  # DI2 state (stop signal)
    error_signal = Signal(str)
    
    def __init__(self, relay_host='192.168.1.254', relay_port=4196):
        super().__init__()
        self.relay_host = relay_host
        self.relay_port = relay_port
        self.running = False
        self.relay = None
        self.last_di1_state = False
        self.last_di2_state = False
        self.manual_mode = True  # Start in manual mode
        
        # Track current DO states to avoid redundant commands
        self.do_states = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}
        
    def run(self):
        """Main relay monitoring loop"""
        self.running = True
        
        try:
            self.relay = Relay(host=self.relay_host, port=self.relay_port)
            self.relay.connect(timeout=2.0)  # Short timeout
            self.error_signal.emit(f"Connected to relay at {self.relay_host}")
            
            while self.running:
                try:
                    # Only monitor hardware DI when not in manual mode
                    if not self.manual_mode:
                        # Check DI1 state
                        di1_state = self.relay.is_DI_on(1)
                        if di1_state != self.last_di1_state:
                            self.last_di1_state = di1_state
                            self.di1_changed.emit(di1_state)
                            
                        # Check DI2 state
                        di2_state = self.relay.is_DI_on(2)
                        if di2_state != self.last_di2_state:
                            self.last_di2_state = di2_state
                            self.di2_changed.emit(di2_state)
                        
                    time.sleep(0.1)  # Poll every 100ms
                    
                except Exception as e:
                    self.error_signal.emit(f"Relay monitoring error: {str(e)}")
                    time.sleep(1)
                    
        except Exception as e:
            self.error_signal.emit(f"Relay connection error: {str(e)} - using dummy mode")
            # Continue in dummy mode
            while self.running:
                time.sleep(0.5)
            
        finally:
            if self.relay:
                self.relay.disconnect()
                
    def stop(self):
        """Stop the relay monitor thread"""
        self.running = False
        self.wait()
        
    def set_output(self, channel, state):
        """Set relay output channel state (only if state changed)"""
        try:
            if self.relay:
                # Check if state is already set to avoid redundant commands
                if self.do_states.get(channel) == state:
                    # Already in requested state, skip command
                    return
                
                # State is changing, send command
                success = False
                if state:
                    result = self.relay.on(channel)
                    success = result if result is not None else True
                else:
                    result = self.relay.off(channel)
                    success = result if result is not None else True
                
                # Update tracked state only if command succeeded
                if success:
                    self.do_states[channel] = state
        except socket.timeout:
            self.error_signal.emit(f"Relay timeout: DO{channel} command timed out")
        except ConnectionError as e:
            self.error_signal.emit(f"Relay connection error: {str(e)}")
            # Try to reconnect on next operation
            self.relay = None
        except Exception as e:
            # Log error but don't spam - only log unique errors
            error_msg = f"Relay output error on DO{channel}: {str(e)}"
            if not hasattr(self, '_last_error') or self._last_error != error_msg:
                self.error_signal.emit(error_msg)
                self._last_error = error_msg


class DetectionApp(QMainWindow):
    """Main application window"""
    
    def __init__(self, model_path, relay_host='192.168.1.254'):
        super().__init__()
        
        self.model_path = model_path
        self.relay_host = relay_host
        
        # Application state
        self.detection_active = False
        self.di1_active = False
        self.di2_active = False
        self.camera1_has_object = False
        self.camera2_has_object = False
        
        # DO5 lock flag - once ON, can only be turned OFF via password reset
        self.do5_locked = False
        
        # Threads
        self.camera1_thread = None
        self.camera2_thread = None
        self.inference_thread = None
        self.relay_thread = None
        
        # Setup UI
        self.init_ui()
        
        # Start threads
        self.start_threads()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("MAW5 Leakage Detection System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Import QTabWidget
        from PySide6.QtWidgets import QTabWidget
        
        # Main layout with tabs
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Main tab
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout(main_tab)
        
        # Top row - Cameras (side by side)
        top_layout = QHBoxLayout()
        
        # Camera 1 (top left)
        cam1_widget = QWidget()
        cam1_layout = QVBoxLayout(cam1_widget)
        cam1_layout.setContentsMargins(0, 0, 0, 0)
        self.camera1_label = VideoLabel()
        self.camera1_label.setMinimumSize(560, 420)
        self.camera1_label.setAlignment(Qt.AlignCenter)
        self.camera1_label.setStyleSheet("background-color: black; border: 2px solid #333;")
        cam1_layout.addWidget(self.camera1_label)
        top_layout.addWidget(cam1_widget)
        
        # Camera 2 (top right)
        cam2_widget = QWidget()
        cam2_layout = QVBoxLayout(cam2_widget)
        cam2_layout.setContentsMargins(0, 0, 0, 0)
        self.camera2_label = VideoLabel()
        self.camera2_label.setMinimumSize(560, 420)
        self.camera2_label.setAlignment(Qt.AlignCenter)
        self.camera2_label.setStyleSheet("background-color: black; border: 2px solid #333;")
        cam2_layout.addWidget(self.camera2_label)
        top_layout.addWidget(cam2_widget)
        
        main_tab_layout.addLayout(top_layout)
        
        # Bottom row
        bottom_layout = QHBoxLayout()
        
        # System Log (bottom left)
        log_group = QGroupBox("System Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        log_layout.addWidget(self.log_text)
        
        # Reset DO5 button (with password protection)
        self.reset_do5_btn = QPushButton("Reset DO5 (Password Required)")
        self.reset_do5_btn.setStyleSheet("background-color: #FF6B6B; color: white; font-weight: bold; padding: 10px; margin-top: 5px;")
        self.reset_do5_btn.clicked.connect(self.reset_do5_with_password)
        log_layout.addWidget(self.reset_do5_btn)
        
        log_group.setLayout(log_layout)
        bottom_layout.addWidget(log_group, 3)
        
        # System Status (bottom right)
        status_group = QGroupBox("System Status")
        status_layout = QGridLayout()
        
        status_layout.addWidget(QLabel("DI1 (Start):"), 0, 0)
        self.di1_indicator = QLabel("●")
        self.di1_indicator.setStyleSheet("color: red; font-size: 24px;")
        status_layout.addWidget(self.di1_indicator, 0, 1)
        
        status_layout.addWidget(QLabel("DI2 (Stop):"), 1, 0)
        self.di2_indicator = QLabel("●")
        self.di2_indicator.setStyleSheet("color: red; font-size: 24px;")
        status_layout.addWidget(self.di2_indicator, 1, 1)
        
        status_layout.addWidget(QLabel("Detection Mode:"), 2, 0)
        self.mode_label = QLabel("Camera Feed")
        self.mode_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.mode_label, 2, 1)
        
        status_layout.addWidget(QLabel("DO4 (No Object):"), 3, 0)
        self.do4_indicator = QLabel("●")
        self.do4_indicator.setStyleSheet("color: gray; font-size: 24px;")
        status_layout.addWidget(self.do4_indicator, 3, 1)
        
        status_layout.addWidget(QLabel("DO5 (Object):"), 4, 0)
        self.do5_indicator = QLabel("●")
        self.do5_indicator.setStyleSheet("color: gray; font-size: 24px;")
        status_layout.addWidget(self.do5_indicator, 4, 1)
        
        # Detection results
        status_layout.addWidget(QLabel("Camera 1:"), 5, 0)
        self.cam1_detection_label = QLabel("No detection")
        self.cam1_detection_label.setStyleSheet("font-size: 11px;")
        status_layout.addWidget(self.cam1_detection_label, 5, 1)
        
        status_layout.addWidget(QLabel("Camera 2:"), 6, 0)
        self.cam2_detection_label = QLabel("No detection")
        self.cam2_detection_label.setStyleSheet("font-size: 11px;")
        status_layout.addWidget(self.cam2_detection_label, 6, 1)
        
        status_group.setLayout(status_layout)
        bottom_layout.addWidget(status_group, 2)
        
        main_tab_layout.addLayout(bottom_layout)
        
        # Add main tab
        self.tabs.addTab(main_tab, "Main View")
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Manual Control Panel (for testing)
        manual_group = QGroupBox("Manual Control (Testing)")
        manual_layout = QGridLayout()
        
        # DI Manual Control (simulates hardware signals)
        manual_layout.addWidget(QLabel("Digital Inputs (Manual):"), 0, 0, 1, 2)
        
        self.di1_manual_btn = QPushButton("DI1: OFF (Click to Toggle)")
        self.di1_manual_btn.setStyleSheet("background-color: #ffcccc;")
        self.di1_manual_btn.clicked.connect(lambda: self.toggle_di_manual(1))
        manual_layout.addWidget(self.di1_manual_btn, 1, 0)
        
        self.di2_manual_btn = QPushButton("DI2: OFF (Click to Toggle)")
        self.di2_manual_btn.setStyleSheet("background-color: #ffcccc;")
        self.di2_manual_btn.clicked.connect(lambda: self.toggle_di_manual(2))
        manual_layout.addWidget(self.di2_manual_btn, 1, 1)
        
        # DO Manual Control
        manual_layout.addWidget(QLabel("Digital Outputs:"), 2, 0, 1, 2)
        
        self.do4_control_btn = QPushButton("DO4: OFF")
        self.do4_control_btn.clicked.connect(lambda: self.toggle_do(4))
        manual_layout.addWidget(self.do4_control_btn, 3, 0)
        
        self.do5_control_btn = QPushButton("DO5: OFF")
        self.do5_control_btn.clicked.connect(lambda: self.toggle_do(5))
        manual_layout.addWidget(self.do5_control_btn, 3, 1)
        
        # Additional DI/DO status
        manual_layout.addWidget(QLabel("All DI Status:"), 4, 0, 1, 2)
        
        di_grid = QGridLayout()
        self.di_status_labels = {}
        for i in range(1, 9):
            label = QLabel(f"DI{i}: -")
            label.setStyleSheet("padding: 2px; font-size: 10px;")
            di_grid.addWidget(label, (i-1)//4, (i-1)%4)
            self.di_status_labels[i] = label
        manual_layout.addLayout(di_grid, 5, 0, 1, 2)
        
        manual_layout.addWidget(QLabel("All DO Status:"), 6, 0, 1, 2)
        
        do_grid = QGridLayout()
        self.do_status_labels = {}
        for i in range(1, 9):
            label = QLabel(f"DO{i}: -")
            label.setStyleSheet("padding: 2px; font-size: 10px;")
            do_grid.addWidget(label, (i-1)//4, (i-1)%4)
            self.do_status_labels[i] = label
        manual_layout.addLayout(do_grid, 7, 0, 1, 2)
        
        # Mode selection
        manual_layout.addWidget(QLabel("Control Mode:"), 8, 0, 1, 2)
        
        self.di_mode_btn = QPushButton("Mode: Manual DI Control")
        self.di_mode_btn.setStyleSheet("background-color: #ccddff; font-weight: bold;")
        self.di_mode_btn.clicked.connect(self.toggle_di_mode)
        manual_layout.addWidget(self.di_mode_btn, 9, 0, 1, 2)
        
        # Refresh button
        self.refresh_status_btn = QPushButton("Refresh All Status")
        self.refresh_status_btn.clicked.connect(self.refresh_all_status)
        manual_layout.addWidget(self.refresh_status_btn, 10, 0, 1, 2)
        
        manual_group.setLayout(manual_layout)
        settings_layout.addWidget(manual_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("Clear Log")
        self.clear_log_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_log_btn)
        settings_layout.addLayout(button_layout)
        
        settings_layout.addStretch()
        
        # Add settings tab
        self.tabs.addTab(settings_tab, "Settings")
        
        # DO manual states
        self.do4_manual_state = False
        self.do5_manual_state = False
        
        # DI manual states (simulate hardware inputs)
        self.di1_manual_state = False
        self.di2_manual_state = False
        self.manual_di_mode = True  # True = use manual DI, False = use hardware DI
        
        # Camera detection overlays
        self.camera1_last_frame = None
        self.camera2_last_frame = None
        self.camera1_detections = []
        self.camera2_detections = []
        
        # Timer for periodic status refresh
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.refresh_all_status)
        self.status_timer.start(2000)  # Refresh every 2 seconds
        
        self.log("Application started")
        
    def start_threads(self):
        """Start all worker threads"""
        print("Starting camera 1 thread...")
        # Camera threads with delay between initialization
        self.camera1_thread = CameraThread(camera_id=1, camera_index=0)
        self.camera1_thread.frame_ready.connect(self.on_camera1_frame)
        self.camera1_thread.error_signal.connect(self.on_error)
        self.camera1_thread.start()
        
        # Wait for camera 1 to initialize
        print("Waiting for camera 1 to initialize...")
        time.sleep(2)
        
        print("Starting camera 2 thread...")
        self.camera2_thread = CameraThread(camera_id=2, camera_index=2)
        self.camera2_thread.frame_ready.connect(self.on_camera2_frame)
        self.camera2_thread.error_signal.connect(self.on_error)
        self.camera2_thread.start()
        
        # Wait for camera 2 to initialize
        print("Waiting for camera 2 to initialize...")
        time.sleep(2)
        
        print("Starting inference thread...")
        # Inference thread
        self.inference_thread = YOLOInferenceThread(self.model_path, conf_threshold=0.25)
        self.inference_thread.detection_result.connect(self.on_detection_result)
        self.inference_thread.error_signal.connect(self.on_error)
        self.inference_thread.start()
        
        print("Starting relay monitor thread...")
        # Relay monitor thread
        self.relay_thread = RelayMonitorThread(relay_host=self.relay_host)
        self.relay_thread.di1_changed.connect(self.on_di1_changed)
        self.relay_thread.di2_changed.connect(self.on_di2_changed)
        self.relay_thread.error_signal.connect(self.on_error)
        self.relay_thread.start()
        
        print("All threads started")
        self.log("All threads started")
        
    @Slot(np.ndarray, int)
    def on_camera1_frame(self, frame, camera_id):
        """Handle frame from camera 1"""
        self.display_frame(frame, self.camera1_label, camera_id)
        
        # Send to inference if detection is active
        if self.detection_active and self.inference_thread:
            self.inference_thread.add_frame(frame, camera_id)
            
    @Slot(np.ndarray, int)
    def on_camera2_frame(self, frame, camera_id):
        """Handle frame from camera 2"""
        self.display_frame(frame, self.camera2_label, camera_id)
        
        # Send to inference if detection is active
        if self.detection_active and self.inference_thread:
            self.inference_thread.add_frame(frame, camera_id)
            
    def display_frame(self, frame, label, camera_id):
        """Display frame on label with detection overlays using PySide6"""
        # Store frame for detection overlay
        if camera_id == 1:
            self.camera1_last_frame = frame.copy()
        else:
            self.camera2_last_frame = frame.copy()
        
        # Get detection data for this camera
        detections = self.camera1_detections if camera_id == 1 else self.camera2_detections
        has_object = self.camera1_has_object if camera_id == 1 else self.camera2_has_object
        
        # Convert frame to QImage
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Set the pixmap
        label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Update overlay data with original frame dimensions (will trigger repaint with overlays)
        label.set_detections(detections, self.detection_active, has_object, frame_width=w, frame_height=h)
            
    @Slot(bool, list, int)
    def on_detection_result(self, has_object, detections, camera_id):
        """Handle detection results"""
        if camera_id == 1:
            self.camera1_has_object = has_object
            self.camera1_detections = detections
            if has_object:
                det_list = [f"{d['class']}({d['confidence']:.2f})" for d in detections[:3]]
                self.cam1_detection_label.setText(f"{len(detections)}: {', '.join(det_list)}")
                self.cam1_detection_label.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.cam1_detection_label.setText("No detection")
                self.cam1_detection_label.setStyleSheet("")
        else:
            self.camera2_has_object = has_object
            self.camera2_detections = detections
            if has_object:
                det_list = [f"{d['class']}({d['confidence']:.2f})" for d in detections[:3]]
                self.cam2_detection_label.setText(f"{len(detections)}: {', '.join(det_list)}")
                self.cam2_detection_label.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.cam2_detection_label.setText("No detection")
                self.cam2_detection_label.setStyleSheet("")
                
        # Update outputs based on detection state
        self.update_outputs()
        
    @Slot(bool)
    def on_di1_changed(self, state):
        """Handle DI1 (start signal) change - only activates detection, doesn't deactivate"""
        self.di1_active = state
        
        if state:
            self.di1_indicator.setStyleSheet("color: green; font-size: 24px;")
            self.detection_active = True
            self.mode_label.setText("Detection Active")
            self.mode_label.setStyleSheet("color: green; font-weight: bold;")
            self.log("DI1 ON - Detection mode activated")
        else:
            self.di1_indicator.setStyleSheet("color: red; font-size: 24px;")
            # DI1 OFF does not deactivate detection - only DI2 ON can stop detection
            self.log("DI1 OFF - Detection remains active (use DI2 to stop)")
        
        # Update manual control display if in manual mode
        if self.manual_di_mode:
            self.di1_manual_state = state
            self.di1_manual_btn.setText(f"DI1: {'ON' if state else 'OFF'} (Click to Toggle)")
            self.di1_manual_btn.setStyleSheet(f"background-color: {'#ccffcc' if state else '#ffcccc'};")
            
        self.update_outputs()
        
    @Slot(bool)
    def on_di2_changed(self, state):
        """Handle DI2 (stop signal) change - deactivates detection when ON"""
        self.di2_active = state
        
        if state:
            self.di2_indicator.setStyleSheet("color: green; font-size: 24px;")
            # DI2 ON stops detection
            self.detection_active = False
            self.mode_label.setText("Camera Feed")
            self.mode_label.setStyleSheet("font-weight: bold;")
            self.log("DI2 ON - Detection stopped")
        else:
            self.di2_indicator.setStyleSheet("color: red; font-size: 24px;")
            self.log("DI2 OFF - Ready for detection (use DI1 to start)")
        
        # Update manual control display if in manual mode
        if self.manual_di_mode:
            self.di2_manual_state = state
            self.di2_manual_btn.setText(f"DI2: {'ON' if state else 'OFF'} (Click to Toggle)")
            self.di2_manual_btn.setStyleSheet(f"background-color: {'#ccffcc' if state else '#ffcccc'};")
            
        self.update_outputs()
        
    def update_outputs(self):
        """Update DO4 and DO5 based on detection state"""
        if not self.relay_thread:
            return
            
        # Logic:
        # - If DI2 is ON and no object detected in any camera -> DO4 ON
        # - If object detected in any camera -> DO5 ON (and locks - can only be reset with password)
        # - DO5 once ON, stays ON until manual password reset
        # - Otherwise DO4 OFF
        
        any_object = self.camera1_has_object or self.camera2_has_object
        
        # Track previous states for logging
        prev_do4 = self.relay_thread.do_states.get(4)
        prev_do5 = self.relay_thread.do_states.get(5)
        
        if self.detection_active:
            if self.di2_active and not any_object and not self.do5_locked:
                # DI2 is on, no object detected, DO5 not locked -> DO4 ON
                self.relay_thread.set_output(4, True)
                self.do4_indicator.setStyleSheet("color: green; font-size: 24px;")
                # Only log if state changed
                if prev_do4 != True:
                    self.log("DO4 ON - No object detected (DI2 active)")
            elif any_object:
                # Object detected -> DO5 ON and lock it
                self.relay_thread.set_output(4, False)
                self.relay_thread.set_output(5, True)
                self.do4_indicator.setStyleSheet("color: gray; font-size: 24px;")
                self.do5_indicator.setStyleSheet("color: green; font-size: 24px;")
                
                # Lock DO5 - can only be turned off with password
                if not self.do5_locked:
                    self.do5_locked = True
                    self.log("DO5 ON - Object detected (LOCKED - requires password to reset)")
                elif prev_do5 != True:
                    # Just turned on (but was already locked conceptually)
                    self.log("DO5 ON - Object detected")
            elif self.do5_locked:
                # DO5 is locked ON, keep it that way regardless of detection state
                self.relay_thread.set_output(4, False)
                # Don't turn off DO5 - it's locked
                self.do4_indicator.setStyleSheet("color: gray; font-size: 24px;")
                self.do5_indicator.setStyleSheet("color: green; font-size: 24px;")
            else:
                # No conditions met, DO5 not locked -> both OFF
                self.relay_thread.set_output(4, False)
                self.do4_indicator.setStyleSheet("color: gray; font-size: 24px;")
                self.do5_indicator.setStyleSheet("color: gray; font-size: 24px;")
        else:
            # Detection not active
            # DO4 turns off, but DO5 stays locked if it was locked
            self.relay_thread.set_output(4, False)
            self.do4_indicator.setStyleSheet("color: gray; font-size: 24px;")
            
            if not self.do5_locked:
                # Only turn off DO5 if it's not locked
                self.do5_indicator.setStyleSheet("color: gray; font-size: 24px;")
            
    @Slot(str)
    def on_error(self, error_msg):
        """Handle error messages"""
        self.log(f"ERROR: {error_msg}")
        
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.clear()
        self.log("Log cleared")
        
    def toggle_di_manual(self, di_number):
        """Toggle DI manually (simulates hardware input signal)"""
        if di_number == 1:
            self.di1_manual_state = not self.di1_manual_state
            state = self.di1_manual_state
            self.di1_manual_btn.setText(f"DI1: {'ON' if state else 'OFF'} (Click to Toggle)")
            self.di1_manual_btn.setStyleSheet(f"background-color: {'#ccffcc' if state else '#ffcccc'};")
            
            # Trigger the same logic as hardware DI1 change
            self.on_di1_changed(state)
            self.log(f"Manual DI1: {'ON' if state else 'OFF'} - Detection {'activated' if state else 'deactivated'}")
            
        elif di_number == 2:
            self.di2_manual_state = not self.di2_manual_state
            state = self.di2_manual_state
            self.di2_manual_btn.setText(f"DI2: {'ON' if state else 'OFF'} (Click to Toggle)")
            self.di2_manual_btn.setStyleSheet(f"background-color: {'#ccffcc' if state else '#ffcccc'};")
            
            # Trigger the same logic as hardware DI2 change
            self.on_di2_changed(state)
            self.log(f"Manual DI2: {'ON' if state else 'OFF'} - Stop signal {'active' if state else 'inactive'}")
    
    def toggle_do(self, channel):
        """Toggle DO channel manually"""
        if channel == 4:
            self.do4_manual_state = not self.do4_manual_state
            state = self.do4_manual_state
            self.do4_control_btn.setText(f"DO4: {'ON' if state else 'OFF'}")
            self.do4_control_btn.setStyleSheet(f"background-color: {'#ccffcc' if state else '#ffcccc'};")
        elif channel == 5:
            self.do5_manual_state = not self.do5_manual_state
            state = self.do5_manual_state
            self.do5_control_btn.setText(f"DO5: {'ON' if state else 'OFF'}")
            self.do5_control_btn.setStyleSheet(f"background-color: {'#ccffcc' if state else '#ffcccc'};")
        
        if self.relay_thread:
            self.relay_thread.set_output(channel, state)
            self.log(f"Manual control: DO{channel} set to {'ON' if state else 'OFF'}")
    
    def toggle_di_mode(self):
        """Toggle between manual DI control and hardware DI monitoring"""
        self.manual_di_mode = not self.manual_di_mode
        
        # Update relay thread mode
        if self.relay_thread:
            self.relay_thread.manual_mode = self.manual_di_mode
        
        if self.manual_di_mode:
            self.di_mode_btn.setText("Mode: Manual DI Control")
            self.di_mode_btn.setStyleSheet("background-color: #ccddff; font-weight: bold;")
            self.log("Switched to Manual DI Control mode - use buttons to control")
            
            # Enable manual DI buttons
            self.di1_manual_btn.setEnabled(True)
            self.di2_manual_btn.setEnabled(True)
        else:
            self.di_mode_btn.setText("Mode: Hardware DI Monitoring")
            self.di_mode_btn.setStyleSheet("background-color: #ffddcc; font-weight: bold;")
            self.log("Switched to Hardware DI mode - monitoring real relay inputs")
            
            # Disable manual DI buttons (read-only)
            self.di1_manual_btn.setEnabled(False)
            self.di2_manual_btn.setEnabled(False)
    
    def refresh_all_status(self):
        """Refresh all DI and DO status"""
        if not self.relay_thread or not self.relay_thread.relay:
            return
        
        try:
            # Update all DI status
            di_status = self.relay_thread.relay.check_DI()
            for i in range(1, 9):
                is_on = bool(di_status & (1 << (i - 1)))
                self.di_status_labels[i].setText(f"DI{i}: {'ON' if is_on else 'OFF'}")
                self.di_status_labels[i].setStyleSheet(
                    f"padding: 2px; font-size: 10px; color: {'green' if is_on else 'red'}; font-weight: {'bold' if is_on else 'normal'};"
                )
            
            # If in hardware mode, update DI1/DI2 from hardware
            if not self.manual_di_mode:
                di1_on = bool(di_status & 1)
                di2_on = bool(di_status & 2)
                
                self.di1_manual_btn.setText(f"DI1: {'ON' if di1_on else 'OFF'} (Hardware)")
                self.di1_manual_btn.setStyleSheet(f"background-color: {'#ccffcc' if di1_on else '#ffcccc'};")
                
                self.di2_manual_btn.setText(f"DI2: {'ON' if di2_on else 'OFF'} (Hardware)")
                self.di2_manual_btn.setStyleSheet(f"background-color: {'#ccffcc' if di2_on else '#ffcccc'};")
            
            # Update all DO status by checking each one
            for i in range(1, 9):
                try:
                    is_on = self.relay_thread.relay.status(i)
                    self.do_status_labels[i].setText(f"DO{i}: {'ON' if is_on else 'OFF'}")
                    self.do_status_labels[i].setStyleSheet(
                        f"padding: 2px; font-size: 10px; color: {'green' if is_on else 'gray'}; font-weight: {'bold' if is_on else 'normal'};"
                    )
                except:
                    pass
                    
        except Exception as e:
            self.log(f"Status refresh error: {str(e)}")
    
    def reset_do5_with_password(self):
        """Reset DO5 to OFF with password protection."""
        # Create a custom dialog with numeric keypad
        dialog = QDialog(self)
        dialog.setWindowTitle('Password Required - Reset DO5')
        dialog.setModal(True)
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instruction_label = QLabel('Enter password to reset DO5 to OFF:')
        instruction_label.setStyleSheet("font-size: 12pt; margin: 10px;")
        layout.addWidget(instruction_label)
        
        # Password input field
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet("font-size: 16pt; padding: 10px; margin: 10px;")
        password_input.setPlaceholderText("Enter 4-digit password")
        password_input.setMaxLength(4)
        layout.addWidget(password_input)
        
        # Numeric keypad
        keypad_group = QGroupBox("Numeric Keypad")
        keypad_layout = QVBoxLayout()
        
        # Create number buttons in a grid
        button_layout1 = QHBoxLayout()
        button_layout2 = QHBoxLayout()
        button_layout3 = QHBoxLayout()
        button_layout4 = QHBoxLayout()
        
        # Row 1: 1, 2, 3
        for num in [1, 2, 3]:
            btn = QPushButton(str(num))
            btn.setStyleSheet("QPushButton { font-size: 20pt; padding: 15px; margin: 2px; }")
            btn.clicked.connect(lambda checked, n=num: password_input.setText(password_input.text() + str(n)))
            button_layout1.addWidget(btn)
        
        # Row 2: 4, 5, 6
        for num in [4, 5, 6]:
            btn = QPushButton(str(num))
            btn.setStyleSheet("QPushButton { font-size: 20pt; padding: 15px; margin: 2px; }")
            btn.clicked.connect(lambda checked, n=num: password_input.setText(password_input.text() + str(n)))
            button_layout2.addWidget(btn)
        
        # Row 3: 7, 8, 9
        for num in [7, 8, 9]:
            btn = QPushButton(str(num))
            btn.setStyleSheet("QPushButton { font-size: 20pt; padding: 15px; margin: 2px; }")
            btn.clicked.connect(lambda checked, n=num: password_input.setText(password_input.text() + str(n)))
            button_layout3.addWidget(btn)
        
        # Row 4: Clear, 0, Backspace
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("QPushButton { font-size: 16pt; padding: 15px; margin: 2px; background-color: #FF6B6B; color: white; }")
        clear_btn.clicked.connect(lambda: password_input.clear())
        button_layout4.addWidget(clear_btn)
        
        zero_btn = QPushButton("0")
        zero_btn.setStyleSheet("QPushButton { font-size: 20pt; padding: 15px; margin: 2px; }")
        zero_btn.clicked.connect(lambda: password_input.setText(password_input.text() + "0"))
        button_layout4.addWidget(zero_btn)
        
        backspace_btn = QPushButton("⌫")
        backspace_btn.setStyleSheet("QPushButton { font-size: 16pt; padding: 15px; margin: 2px; background-color: #FFA500; color: white; }")
        backspace_btn.clicked.connect(lambda: password_input.setText(password_input.text()[:-1]))
        button_layout4.addWidget(backspace_btn)
        
        # Add all button rows to keypad layout
        keypad_layout.addLayout(button_layout1)
        keypad_layout.addLayout(button_layout2)
        keypad_layout.addLayout(button_layout3)
        keypad_layout.addLayout(button_layout4)
        
        keypad_group.setLayout(keypad_layout)
        layout.addWidget(keypad_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # Style the OK and Cancel buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setStyleSheet("QPushButton { font-size: 14pt; padding: 10px; background-color: #4CAF50; color: white; }")
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setStyleSheet("QPushButton { font-size: 14pt; padding: 10px; background-color: #757575; color: white; }")
        
        layout.addWidget(button_box)
        
        # Show the dialog
        if dialog.exec() != QDialog.Accepted:
            # User cancelled
            self.log("Reset DO5 - Operation cancelled")
            return
        
        # Get the entered password
        password = password_input.text().strip()
        
        # Check password
        correct_password = "5435"
        if password != correct_password:
            # Show error message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Incorrect Password")
            msg.setText("Incorrect password!")
            msg.setInformativeText("Access denied. Cannot reset DO5.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.log("Reset DO5 - Incorrect password entered")
            return
        
        # Password is correct, show confirmation dialog
        reply = QMessageBox.question(
            self,
            'Confirm Reset DO5',
            'Are you sure you want to turn OFF DO5?\n\nThis will deactivate the object detection output signal.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Force DO5 OFF and unlock it
            if self.relay_thread:
                self.relay_thread.set_output(5, False)
                self.relay_thread.do_states[5] = False  # Force update state
                self.do5_locked = False  # Unlock DO5
                self.do5_indicator.setStyleSheet("color: gray; font-size: 24px;")
                self.log("DO5 manually reset to OFF and UNLOCKED (password authenticated)")
        else:
            self.log("Reset DO5 - Operation cancelled by user")
        
    def closeEvent(self, event):
        """Handle window close event"""
        self.log("Shutting down...")
        
        # Stop all threads
        if self.camera1_thread:
            self.camera1_thread.stop()
        if self.camera2_thread:
            self.camera2_thread.stop()
        if self.inference_thread:
            self.inference_thread.stop()
        if self.relay_thread:
            # Turn off all outputs
            self.relay_thread.set_output(4, False)
            self.relay_thread.set_output(5, False)
            self.relay_thread.stop()
            
        event.accept()


def find_model_file():
    """Find .pt or .engine file in current directory and subdirectories"""
    import glob
    
    # Search for .pt files first (preferred), then .engine files
    model_files = glob.glob('**/*.pt', recursive=True)
    if not model_files:
        model_files = glob.glob('*.pt')
    
    if not model_files:
        # Fall back to .engine files
        model_files = glob.glob('**/*.engine', recursive=True)
        if not model_files:
            model_files = glob.glob('*.engine')
    
    if model_files:
        return model_files[0]  # Return first found
    return None


def main():
    """Main application entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MAW5 Leakage Detection System')
    parser.add_argument('--model', '--engine', type=str, required=False, dest='model',
                       help='Path to YOLO model (.pt or .engine). Auto-detects if not specified.')
    parser.add_argument('--relay-host', type=str, default='192.168.1.254',
                       help='Relay board IP address (default: 192.168.1.254)')
    parser.add_argument('--cam1', type=int, default=0,
                       help='Camera 1 index (default: 0)')
    parser.add_argument('--cam2', type=int, default=2,
                       help='Camera 2 index (default: 2)')
    
    args = parser.parse_args()
    
    # Auto-detect model file if not specified
    engine_path = args.model
    if not engine_path:
        engine_path = find_model_file()
        if engine_path:
            model_type = "PyTorch" if engine_path.endswith('.pt') else "TensorRT"
            print(f"Auto-detected {model_type} model: {engine_path}")
        else:
            print("ERROR: No .pt or .engine file found. Please specify with --model parameter.")
            sys.exit(1)
    
    if not Path(engine_path).exists():
        print(f"ERROR: Model file not found: {engine_path}")
        sys.exit(1)
    
    # Create application
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    
    # Create and show main window
    print("Creating main window...")
    window = DetectionApp(
        model_path=engine_path,
        relay_host=args.relay_host
    )
    
    # Update camera indices if specified
    if window.camera1_thread:
        window.camera1_thread.camera_index = args.cam1
    if window.camera2_thread:
        window.camera2_thread.camera_index = args.cam2
    
    print("Showing window...")
    window.show()
    
    print("Starting event loop...")
    # Run application
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
