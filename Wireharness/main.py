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
import json
import os
import threading
import subprocess

### When Startup must call config.json

class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.ui = Ui_DetectWindows()
        self.ui.setupUi(self)
        self.init_ui()
        self.load_config_from_json()

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

        # Connect the clicked signal to a handler function
        self.ui.buttonBox_save_cancel_apply.clicked.connect(self.handle_button_save_cancel_apply)

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
        Update the QLabel with the latest YOLO detection frame and check for class matches.
        If no objects are detected, display "Checking . . ." with default color.
        """
        if not self.yolo_detector:
            return

        # Process the frame and get detected classes
        pixmap, detected_classes = self.yolo_detector.process_frame()

        if pixmap:
            self.ui.frame_Detection.setPixmap(pixmap)

        # Check detected classes against the table
        if detected_classes:
            self.check_class_match(detected_classes)
        else:
            # No objects detected: Show "Checking . . ." with default color
            self.ui.label_Classes.setText("Checking . . .")
            self.ui.label_Classes.setStyleSheet("")  # Reset to default color

    def check_class_match(self, detected_classes):
        """
        Check if the detected classes match the "Classes" column in the table where "Status" is "Match".
        Update ui.label_Classes with the result and execute scripts based on the match status.
        """
        table = self.ui.tableWidget_model_match
        found_match = False  # Flag to track if a match was found

        for row in range(table.rowCount()):
            # Get the "Status" column
            status_item = table.item(row, 2)  # Column 3: "Status"
            if status_item and status_item.text() == "Match":  # Check if "Status" is "Match"
                # Get the "Classes" column
                classes_item = table.item(row, 1)  # Column 2: "Classes"
                expected_class = classes_item.text() if classes_item else ""

                # Compare with detected classes
                if expected_class in detected_classes:
                    self.ui.label_Classes.setText(f"{expected_class} & Correct")
                    self.ui.label_Classes.setStyleSheet("background-color: green; color: white;")  # Set text color to green
                    found_match = True

                    # Run the script specified in ui.textEdit_OK_output_script
                    ok_script_path = self.ui.textEdit_OK_output_script.toPlainText().strip()
                    if ok_script_path:
                        self.run_script_in_thread(ok_script_path)
                else:
                    detected_class_text = ", ".join(detected_classes)
                    self.ui.label_Classes.setText(f"{detected_class_text} & Incorrect")
                    self.ui.label_Classes.setStyleSheet("background-color: red; color: white")  # Set text color to red

                    # Run the script specified in ui.textEdit_NG_output_script
                    ng_script_path = self.ui.textEdit_NG_output_script.toPlainText().strip()
                    if ng_script_path:
                        self.run_script_in_thread(ng_script_path)
                break  # Exit after finding the first "Match"

        # If no match is found in the table, show "Checking . . ." with default color
        if not found_match:
            self.ui.label_Classes.setText("Checking . . .")
            self.ui.label_Classes.setStyleSheet("")  # Reset to default color

    def run_script_in_thread(self, script_path):
        """
        Run a script in a separate thread.
        :param script_path: Path to the script to execute.
        """
        def run_script():
            try:
                # Run the script as a subprocess
                subprocess.Popen(script_path, shell=True)
                print(f"Running script: {script_path}")
            except Exception as e:
                print(f"Error running script {script_path}: {e}")

        # Start the script in a new thread
        thread = threading.Thread(target=run_script)
        thread.daemon = True  # Ensure the thread does not block the program from exiting
        thread.start()


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
    
    def handle_button_save_cancel_apply(self, button):
        standard_button = self.ui.buttonBox_save_cancel_apply.standardButton(button)
        if standard_button == QDialogButtonBox.StandardButton.Save:
            self.save_config_to_json()
            QMessageBox.information(self, "Saved", "Setting Save successfully!")
            print("Save")
        elif standard_button == QDialogButtonBox.StandardButton.Cancel:
            print("Cancel")
        elif standard_button == QDialogButtonBox.StandardButton.Apply:
            print("Appy")

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
            self.class_names = class_names
            
            print(class_names)

    def toggle_signal_alarm(self, checked):
        if checked:
            print("Signal Alarm enabled")
        else:
            print("Signal Alarm disabled")

    def add_model(self):
        """
        Add a new row with user input for "Name", dropdown for "Classes",
        and a dialog for scanning the barcode.
        """
        # Read current model
        self.readYoloModelName()

        # Open dialog box for user input
        name_input, ok_name = QInputDialog.getText(self, "Input Name", "Enter Model Name:")
        if not ok_name or not name_input.strip():
            return  # Exit if user cancels or enters empty name

        # Open dialog box for selecting "Classes"
        class_combo = QComboBox()
        class_combo.addItems(self.class_names)  # Example class options
        dialog_box = QMessageBox(self)
        dialog_box.setWindowTitle("Select Classes")
        dialog_box.setText("Choose a class for the model:")
        dialog_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        dialog_box.layout().addWidget(class_combo)

        if dialog_box.exec() == QMessageBox.Ok:
            selected_class = class_combo.currentText()
        else:
            return  # Exit if user cancels

        # Now show the barcode dialog
        self.scan_barcode_dialog(name_input, selected_class)

    def scan_barcode_dialog(self, name_input, selected_class):
        """
        Open a dialog to scan the barcode and handle it using on_label_model_name_double_clicked.
        """
        # Call the barcode input dialog (reusing on_label_model_name_double_clicked logic)
        input_text, ok = QInputDialog.getText(self, "Scan Barcode", "Enter Barcode:")
        if ok:
            # Use the existing on_label_model_name_double_clicked logic to handle the barcode
            model_name_text = sanitize_barcode_input(input_text, [])
            self.ui.label_Model_Name.setText(model_name_text)
            print(f"Updated Model Name to: {model_name_text}")

            # Add the new row to the table with the captured data
            table = self.ui.tableWidget_model_match
            row_position = table.rowCount()
            table.insertRow(row_position)

            # Column 1: "Name" (Input via typing)
            name_item = QTableWidgetItem(name_input.strip())  # Use sanitized input
            table.setItem(row_position, 0, name_item)

            # Column 2: "Classes" (Selected from dropdown)
            class_item = QTableWidgetItem(selected_class)
            table.setItem(row_position, 1, class_item)

            # Column 3: "Status" (Default to "Not selected")
            status_item = QTableWidgetItem("Not selected")  # Default to "Not selected"
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make non-editable
            table.setItem(row_position, 2, status_item)

            # Column 4: "Barcode" (Scanned input)
            barcode_item = QTableWidgetItem(model_name_text)  # Use scanned input
            table.setItem(row_position, 3, barcode_item)

            # Update the "Status" column for each existing row in the table
            for row in range(table.rowCount()):
                barcode_item = table.item(row, 3)  # Get the item in Column 4 ("Barcode")
                if barcode_item:  # Check if the barcode cell is not empty
                    barcode_input_text = barcode_item.text()
                    status_item = table.item(row, 2)  # Get the item in Column 3 ("Status")
                    if model_name_text == barcode_input_text:  # Match condition
                        status_item.setText("Match")
                    else:  # Not match condition
                        status_item.setText("Not Match")

            print(f"Added new row: Name={name_input}, Class={selected_class}, Barcode={model_name_text}")


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

    def save_config_to_json(self):
        """
        Save the application settings and model match table data to a JSON config file.
        """
        config_data = {
            "file_path": self.file_path if hasattr(self, "file_path") else "",
            "cvalue": self.cvalue if hasattr(self, "cvalue") else 0.0,
            "textEdit_OK_output_script": self.ui.textEdit_OK_output_script.toPlainText(),
            "textEdit_NG_output_script": self.ui.textEdit_NG_output_script.toPlainText(),
            "checkBox_signal_Alarm": self.ui.checkBox_signal_Alarm.isChecked(),
            "checkBox_SoundAlarm": self.ui.checkBox_SoundAlarm.isChecked(),
            "checkBox_DigitalOut": self.ui.checkBox_DigitalOut.isChecked(),
            "checkBox_DigitalIN": self.ui.checkBox_DigitalIN.isChecked(),
            "tableWidget_model_match": self.get_table_data(self.ui.tableWidget_model_match)
        }

        # Save to a JSON file
        try:
            with open("config.json", "w") as config_file:
                json.dump(config_data, config_file, indent=4)
            print("Configuration saved successfully.")
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def get_table_data(self, table_widget):
        """
        Extract data from a QTableWidget with specific columns: "Name", "Classes", "Status", "Barcode".
        Handles QComboBox in the "Classes" column.
        Returns data as a list of dictionaries where each dictionary represents a row.
        """
        table_data = []
        row_count = table_widget.rowCount()
        column_count = table_widget.columnCount()

        # Ensure the column headers are correct
        expected_headers = ["Name", "Classes", "Status", "Barcode"]
        headers = [table_widget.horizontalHeaderItem(col).text() for col in range(column_count)]

        if headers != expected_headers:
            print("Warning: Table headers do not match expected headers!")
            return table_data

        # Extract row data
        for row in range(row_count):
            row_data = {}
            for col in range(column_count):
                # Check if the cell contains a widget (e.g., QComboBox)
                cell_widget = table_widget.cellWidget(row, col)
                if isinstance(cell_widget, QComboBox):  # If the cell contains a QComboBox
                    row_data[headers[col]] = cell_widget.currentText()
                else:
                    item = table_widget.item(row, col)  # Get QTableWidgetItem
                    row_data[headers[col]] = item.text() if item else ""
            table_data.append(row_data)

        return table_data

    def load_config_from_json(self, config_file_path="config.json"):
        """
        Load the application settings and model match table data from a JSON config file.
        :param config_file_path: Path to the JSON file.
        """
        if not os.path.exists(config_file_path):
            print(f"Config file '{config_file_path}' does not exist. Skipping load.")
            return

        try:
            with open(config_file_path, "r") as config_file:
                config_data = json.load(config_file)
                print("Loaded Config Data:", config_data)  # Debugging print

            # Populate the UI with the loaded data
            self.yolo_model_filepath = config_data.get("file_path", "")
            print("YOLO Model Filepath:", self.yolo_model_filepath)  # Debugging print

            if self.yolo_model_filepath:
                self.file_path = self.yolo_model_filepath
                self.ui.label_yolo_model.setText(f"Model Loaded: {self.file_path}")
                self.readYoloModelName()

            self.ui.spinBox_confident.setValue(int(config_data.get("cvalue", 0.0) * 100))  # Sync with UI
            self.ui.textEdit_OK_output_script.setPlainText(config_data.get("textEdit_OK_output_script", ""))
            self.ui.textEdit_NG_output_script.setPlainText(config_data.get("textEdit_NG_output_script", ""))
            self.ui.checkBox_signal_Alarm.setChecked(config_data.get("checkBox_signal_Alarm", False))
            self.ui.checkBox_SoundAlarm.setChecked(config_data.get("checkBox_SoundAlarm", False))
            self.ui.checkBox_DigitalOut.setChecked(config_data.get("checkBox_DigitalOut", False))
            self.ui.checkBox_DigitalIN.setChecked(config_data.get("checkBox_DigitalIN", False))

            # Populate the table widget with data
            table_data = config_data.get("tableWidget_model_match", [])
            print("Table Data:", table_data)  # Debugging print
            self.populate_table_widget(self.ui.tableWidget_model_match, table_data, dropdown=False)

            print("Configuration loaded successfully.")

        except Exception as e:
            print(f"Error loading configuration: {e}")


    def populate_table_widget(self, table_widget, table_data, dropdown=True):
        """
        Populate a QTableWidget with data from a list of dictionaries.
        :param table_widget: The QTableWidget to populate.
        :param table_data: A list of dictionaries containing the table data.
        :param dropdown: If True, use dropdown for "Classes". If False, load as text.
        """
        table_widget.setRowCount(0)  # Clear existing rows
        if not table_data:
            print("No data to populate in the table.")  # Debugging print
            return

        headers = list(table_data[0].keys())
        print("Headers:", headers)  # Debugging print
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)

        for row_data in table_data:
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)

            for col, header in enumerate(headers):
                if header == "Classes" and dropdown:  # If dropdown is enabled for "Classes"
                    combo_box = QComboBox()
                    combo_box.addItems(["", "Class A", "Class B", "Class C"])  # Example class options
                    value_to_set = row_data.get(header, "")
                    print(f"Setting ComboBox value: {value_to_set}")  # Debugging print
                    combo_box.setCurrentText(value_to_set)
                    table_widget.setCellWidget(row_position, col, combo_box)
                else:  # Load as text for "Classes" or other columns
                    item_text = row_data.get(header, "")
                    print(f"Setting Table Item: {header} = {item_text}")  # Debugging print
                    table_widget.setItem(row_position, col, QTableWidgetItem(item_text))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())
