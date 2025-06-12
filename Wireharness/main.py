import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QDialogButtonBox, QTableWidgetItem, QComboBox, QInputDialog
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage
import cv2
import numpy as np
from ui_user_interface_version0 import Ui_DetectWindows  # Import the UI class
from barcode_model_scan import sanitize_barcode_input  # Import your barcode sanitization function
from ultralytics import YOLO  # Import YOLO from Ultralytics
from yolo_detection import YoloDetection

class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.ui = Ui_DetectWindows()
        self.ui.setupUi(self)
        self.init_ui()

    def init_ui(self):
        # Connect buttons to their respective functions
        self.ui.pushButton_connect.clicked.connect(self.connect_device)
        self.ui.pushButton_disconnect.clicked.connect(self.disconnect_yolo)

        # Connect the slider and spinbox for "Confident" value
        self.ui.horizontalSlider_confident.valueChanged.connect(self.update_confidence_from_slider)
        self.ui.spinBox_confident.valueChanged.connect(self.update_confidence_from_spinbox)

        # Example of connecting a checkbox to an action
        self.ui.checkBox_signal_Alarm.toggled.connect(self.toggle_signal_alarm)

        # Example: Add logic to the "Add Model" and "Remove Model" buttons
        self.ui.pushButton_add_model.clicked.connect(self.add_model)
        self.ui.pushButton_remove_model.clicked.connect(self.remove_model)

        # Connect the clicked signal to a handler function
        self.ui.buttonBox_yolo_open_apply.clicked.connect(self.handle_button_click)

        # Connect double-click on label_Model_Name
        self.ui.label_Model_Name.mouseDoubleClickEvent = self.on_label_model_name_double_clicked

        # Initialize variables
        self.yolo_detector = None
        self.timer = None
        self.cvalue = 0.7  # Default confidence threshold (25%)
        self.ui.horizontalSlider_confident.valueChanged.connect(self.conf_value)
        self.ui.spinBox_confident.valueChanged.connect(self.conf_value)

    def conf_value(self, cvalue):
        self.cvalue = cvalue * 0.01
        print(f"Confident value: {self.cvalue}")

    def update_frame(self):
        """
        Update the QLabel with the latest YOLO detection frame.
        """
        pixmap = self.yolo_detector.process_frame()
        if pixmap:
            self.ui.frame_Detection.setPixmap(pixmap)

    def closeEvent(self, event):
        """
        Clean up resources on window close.
        """
        if self.yolo_detector:
            self.yolo_detector.release_camera()
        if self.timer:
            self.timer.stop()
        #event.accept()

    def handle_button_click(self, button):
        # Determine which button was clicked
        standard_button = self.ui.buttonBox_yolo_open_apply.standardButton(button)
        
        if standard_button == QDialogButtonBox.StandardButton.Apply:
            self.readYoloModelName()  # Call the Apply function

        elif standard_button == QDialogButtonBox.StandardButton.Open:
            self.openYoloModel()  # Call the Open function
            if self.file_path:
                self.readYoloModelName()

    def connect_device(self):
        self.start_yolo_detection(self.file_path)
        QMessageBox.information(self, "Connection", "Device connected successfully!")

    def disconnect_device(self):
        YoloDetection.release_camera()
        self.closeEvent()
        QMessageBox.warning(self, "Disconnection", "Device disconnected.")

    def disconnect_yolo(self):
        """
        Disconnect the camera and stop YOLO detection.
        """
        print("Disconnecting YOLO detection...")
        if self.yolo_detector:
            self.yolo_detector.release_camera()
        if self.timer:
            self.timer.stop()

        # Set QLabel to blank screen
        blank_image = self.create_blank_image(640, 480)  # Create a blank image
        self.ui.frame_Detection.setPixmap(self.convert_image_to_pixmap(blank_image))  # Set blank pixmap

    def convert_image_to_pixmap(self, image):
        """
        Convert a NumPy image to QPixmap for QLabel display.
        :param image: NumPy image (e.g., blank image).
        :return: QPixmap object.
        """
        height, width, channel = image.shape
        bytes_per_line = channel * width
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return QPixmap.fromImage(QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888))

    def create_blank_image(self, width, height):
        """
        Create a blank black image.
        :param width: Width of the image.
        :param height: Height of the image.
        :return: Blank NumPy image.
        """
        return np.zeros((height, width, 3), dtype=np.uint8)

    def update_confidence_from_slider(self, value):
        """
        Update confidence threshold when slider value changes.
        """
        self.ui.spinBox_confident.setValue(value)  # Sync slider value to spinbox

    def update_confidence_from_spinbox(self, value):
        """
        Update confidence threshold when spinbox value changes.
        """
        self.ui.horizontalSlider_confident.setValue(value)  # Sync spinbox value to slider

    def openYoloModel(self):
        """
        Open file dialog to browse YOLO .pt model.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Open YOLO Model", "", "YOLO Model Files (*.pt)")
        self.file_path = file_path
        if file_path:
            print(f"Selected YOLO model file: {file_path}")
            self.ui.label_yolo_model.setText(f"Model Loaded: {file_path}")
              
    def start_yolo_detection(self, model_path):
        """
        Start YOLO detection with the selected model.
        """
        if self.timer:
            self.timer.stop()

        self.yolo_detector = YoloDetection(model_path=model_path, cvalue=self.cvalue, device="cpu")

        # Timer for updating frames
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms (~33 FPS)

    def readYoloModelName(self):
        self.model = YOLO(self.file_path)
        if self.model:
            class_names = list(self.model.names.values())
            # Add the class names to the QListWidget
            self.ui.listWidget.addItems(class_names)
            print(class_names)

    def toggle_signal_alarm(self, checked):
        if checked:
            print("Signal Alarm enabled")
        else:
            print("Signal Alarm disabled")

    def add_model(self):
        # Access the table widget
        table = self.ui.tableWidget_model_match

        # Add a new row at the end of the table
        row_position = table.rowCount()
        table.insertRow(row_position)

        # Column 1: "Name" (Input via typing)
        name_item = QTableWidgetItem("")  # Empty item for typing
        table.setItem(row_position, 0, name_item)

        # Column 2: "Classes" (QComboBox using values from QListWidget)
        class_combo = QComboBox()
        # Populate the QComboBox with items from the QListWidget
        for i in range(self.ui.listWidget.count()):
            class_combo.addItem(self.ui.listWidget.item(i).text())
        table.setCellWidget(row_position, 1, class_combo)

        # Column 3: "Status" (Default to "Not selected")
        status_item = QTableWidgetItem("Not selected")  # Default to "Not selected"
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make non-editable
        table.setItem(row_position, 2, status_item)

        # Column 4: "Barcode" (Sanitized input via `sanitize_barcode_input`)
        barcode_item = QTableWidgetItem("")  # Default empty item
        table.setItem(row_position, 3, barcode_item)

        # Ensure the double-click signal is connected only once
        if not hasattr(self, "barcode_signal_connected"):
            self.barcode_signal_connected = True

            # Connect double-click signal for Column 4 to open input dialog
            def open_barcode_input_dialog(item):
                if item.column() == 3:  # Ensure the double-click is on Column 4
                    # Open an input dialog for text input
                    input_text, ok = QInputDialog.getText(self, "Input Barcode", "Enter Barcode:")
                    if ok:  # If the user confirms the input
                        # Sanitize the barcode input
                        barcode_input_text = sanitize_barcode_input(input_text, [])
                        # Update the item in the table with the sanitized text
                        item.setText(barcode_input_text)

            table.itemDoubleClicked.connect(open_barcode_input_dialog)
        print(f"Added row {row_position} to the table.")  

    def remove_model(self):
        """Remove the currently selected row from the table."""
        table = self.ui.tableWidget_model_match
        selected_row = table.currentRow()
        if selected_row != -1:
            table.removeRow(selected_row)
            print(f"Removed row {selected_row} from the table.")
        else:
            QMessageBox.warning(self, "Warning", "No row selected!")

    def on_label_model_name_double_clicked(self, event=None):
        """Handle double-click on label_Model_Name."""
        input_text, ok = QInputDialog.getText(self, "Input Barcode", "Enter Barcode:")
        if ok:  # If the user confirms the input
            # Sanitize the barcode input
            model_name_text = sanitize_barcode_input(input_text, [])
            # Set the sanitized text to label_Model_Name
            self.ui.label_Model_Name.setText(model_name_text)
            print(f"Updated Model Name to: {model_name_text}")

            # Update the "Status" column for each row in the table
            table = self.ui.tableWidget_model_match
            for row in range(table.rowCount()):
                barcode_item = table.item(row, 3)  # Get the item in Column 4 ("Barcode")
                if barcode_item:  # Check if the barcode cell is not empty
                    barcode_input_text = barcode_item.text()
                    status_item = table.item(row, 2)  # Get the item in Column 3 ("Status")
                    if model_name_text == barcode_input_text:  # Match condition
                        status_item.setText("Match")
                    else:  # Not match condition
                        status_item.setText("Not Match")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())
