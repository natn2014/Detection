import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from ultralytics import YOLO
import easyocr
from math import atan2, degrees
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QTimer
from ui_mainwindow import Ui_MainWindow
import seaborn as sns

class GaugeReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        model_path = "gauge_epoch-100.pt"
        video_path = "gauge_video.mp4"

        self.ui.tableWidget_Gauge_Values.setRowCount(1)
        self.ui.tableWidget_Gauge_Values.setColumnCount(5)
        self.ui.tableWidget_Gauge_Values.setHorizontalHeaderLabels(
            ['Min Value', 'Max Value', 'Current Value', 'Converted Value', 'QR Code Data']
        )

        self.model = YOLO(model_path)
        self.reader = easyocr.Reader(['en'])
        self.cap = cv2.VideoCapture(video_path)

        # Use a rolling buffer for data (max 1000 rows)
        self.data_buffer_size = 1000
        self.data = pd.DataFrame(columns=['Timestamp', 'Converted Value', 'QR Code Data'])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(30)

        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self.append_data)
        self.record_timer.start(1000)

        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(5000)

        self.ui.pushButton_Export_CSV.clicked.connect(self.export_data)

        self.qr_timer = QTimer(self)
        self.qr_timer.timeout.connect(self.read_qr_code)
        self.qr_timer.start(2000)
        self.ui.dateEdit_Start.dateChanged.connect(self.date_changed)
        self.ui.dateEdit_End.dateChanged.connect(self.date_changed) 

    def calculate_distance(self, point1, point2):
        return np.hypot(point1[0] - point2[0], point1[1] - point2[1])

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.cap.release()
            return

        results = self.model.predict(frame, verbose=False, imgsz=640, conf=0.25, iou=0.45)
        detections = results[0].boxes.data

        positions = {}
        for detection in detections:
            class_id = int(detection[5])
            x1, y1, x2, y2 = detection[:4]
            x, y = int((x1 + x2) / 2), int((y1 + y2) / 2)
            if class_id == 0:
                positions['Center'] = (x, y)
            elif class_id == 1:
                positions['Start'] = (x, y)
            elif class_id == 2:
                positions['End'] = (x, y)
            elif class_id == 3:
                positions['Tip'] = (x, y)

        if not all(key in positions for key in ['Center', 'Start', 'End', 'Tip']):
            self.display_frame(frame)
            return

        if self.calculate_distance(positions['Start'], positions['End']) < 50:
            self.display_frame(frame)
            return
        if not (self.calculate_distance(positions['Start'], positions['Center']) < self.calculate_distance(positions['Start'], positions['End']) and
                self.calculate_distance(positions['End'], positions['Center']) < self.calculate_distance(positions['Start'], positions['End'])):
            self.display_frame(frame)
            return
        if positions['Start'][0] > positions['End'][0]:
            positions['Start'], positions['End'] = positions['End'], positions['Start']

        gauge_min_value = 0.0
        gauge_max_value = 100

        def calculate_angle(point1, point2, center):
            dx1, dy1 = point1[0] - center[0], point1[1] - center[1]
            dx2, dy2 = point2[0] - center[0], point2[1] - center[1]
            angle1 = degrees(atan2(dy1, dx1))
            angle2 = degrees(atan2(dy2, dx2))
            return (angle2 - angle1) % 360

        center = positions['Center']
        angle_start_to_tip = calculate_angle(positions['Start'], positions['Tip'], center)
        angle_start_to_end = calculate_angle(positions['Start'], positions['End'], center)

        gauge_range = gauge_max_value - gauge_min_value
        if angle_start_to_end == 0:
            gauge_current_value = gauge_min_value
        else:
            current_value_ratio = angle_start_to_tip / angle_start_to_end
            gauge_current_value = gauge_min_value + current_value_ratio * gauge_range

        self.ui.tableWidget_Gauge_Values.setItem(0, 0, QTableWidgetItem(f"{gauge_min_value:.2f}%"))
        self.ui.tableWidget_Gauge_Values.setItem(0, 1, QTableWidgetItem(f"{gauge_max_value:.2f}%"))
        self.ui.tableWidget_Gauge_Values.setItem(0, 2, QTableWidgetItem(f"{gauge_current_value:.2f}%"))
        self.ui.tableWidget_Gauge_Values.setItem(0, 3, QTableWidgetItem(f"{self.convert_gauge_values(gauge_current_value):.4f}  MPa"))

        # Only annotate the frame, do not keep frames in memory
        annotated_frame = frame.copy()
        for key, (x, y) in positions.items():
            color = (0, 255, 0) if key == 'Tip' else (255, 0, 0)
            cv2.circle(annotated_frame, (x, y), 5, color, -1)
            cv2.putText(annotated_frame, key, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.putText(annotated_frame, f"Angle to Tip: {angle_start_to_tip:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(annotated_frame, f"Angle to End: {angle_start_to_end:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        self.display_frame(annotated_frame)

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.ui.label_Guage_Video.setPixmap(pixmap)

    def convert_gauge_values(self, gauge_current_value):
        converted_value = 1 - (gauge_current_value / 100)
        converted_value = converted_value / 10
        converted_value = max(0, min(converted_value, 1))
        return converted_value

    def append_data(self):
        if self.ui.tableWidget_Gauge_Values.item(0, 3):
            converted_value_text = self.ui.tableWidget_Gauge_Values.item(0, 3).text()
            QR_code_text = self.ui.tableWidget_Gauge_Values.item(0, 4).text() if self.ui.tableWidget_Gauge_Values.item(0, 4) else "N/A"
            try:
                converted_value = float(converted_value_text.split()[0])
                timestamp = pd.Timestamp.now()
                new_row = pd.DataFrame({'Timestamp': [timestamp], 'Converted Value': [converted_value], 'QR Code Data': [QR_code_text]})
                self.data = pd.concat([self.data, new_row], ignore_index=True)
                # Keep only the last N rows in memory
                if len(self.data) > self.data_buffer_size:
                    self.data = self.data.iloc[-self.data_buffer_size:].reset_index(drop=True)
            except ValueError:
                pass

    def update_plot(self):
        if not self.data.empty:
            plt.figure(figsize=(5, 4))
            # Use boxplot instead of seaborn to save RAM
            self.data.boxplot(column='Converted Value', by='QR Code Data', grid=False)
            #plt.title('Gauge Converted Values Distribution')
            plt.ylabel('Converted Value (MPa)')
            plt.xlabel('QR Code Data')
            plt.tight_layout()
            plt.savefig('temp_plot.png')
            plt.close('all')  # Release memory
            pixmap = QPixmap('temp_plot.png')
            self.ui.label_Past_Records_Graph.setPixmap(pixmap)

    def export_data(self):
        if not self.data.empty:
            try:
                existing_data = pd.read_csv('gauge_data.csv')
                combined_data = pd.concat([existing_data, self.data]).drop_duplicates().reset_index(drop=True)
                combined_data.to_csv('gauge_data.csv', index=False)
            except FileNotFoundError:
                self.data.to_csv('gauge_data.csv', index=False)

    def read_qr_code(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        qr_detector = cv2.QRCodeDetector()
        data, bbox, _ = qr_detector.detectAndDecode(frame)
        if bbox is not None and data:
            self.ui.tableWidget_Gauge_Values.setItem(0, 4, QTableWidgetItem(data))
        else:
            self.ui.tableWidget_Gauge_Values.setItem(0, 4, QTableWidgetItem("N/A"))

    # When dateEdit_Start or dateEdit_End changes, update the plot into label_Selected_Graph
    def date_changed(self):
        self.ui.label_Selected_Graph.clear()
        start_date = self.ui.dateEdit_Start.date().toPython()
        end_date = self.ui.dateEdit_End.date().toPython()
        if not self.data.empty:
            mask = (self.data['Timestamp'].dt.date >= start_date) & (self.data['Timestamp'].dt.date <= end_date)
            filtered_data = self.data.loc[mask]
            if not filtered_data.empty:
                plt.figure(figsize=(5, 4))
                filtered_data.boxplot(column='Converted Value', by='QR Code Data', grid=False)
                plt.ylabel('Converted Value (MPa)')
                plt.xlabel('QR Code Data')
                plt.tight_layout()
                plt.savefig('temp_selected_plot.png')
                plt.close('all')
                pixmap = QPixmap('temp_selected_plot.png')
                self.ui.label_Selected_Graph.setPixmap(pixmap)
    
def main():
    app = QApplication([])
    window = GaugeReaderApp()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
