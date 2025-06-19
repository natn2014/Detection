import os
import sys
import shutil
import yaml
import torch
import subprocess
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QProgressDialog, QTableWidgetItem,QVBoxLayout, QLabel, QSpinBox, QComboBox, QDialogButtonBox, QTextEdit
from PySide6.QtCore import Qt, QCoreApplication, QThread, Signal
from PySide6.QtGui import QTextCursor, QPixmap
from ultralytics import YOLO  # Assuming Ultralytics YOLO is used
from GUI_Label_Split_Train3 import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class TrainingThread(QThread):
    """
    A QThread to handle the YOLO training process and emit real-time output.
    """
    output_signal = Signal(str)  # Signal to emit training output (terminal messages)
    graph_signal = Signal(str)  # Signal to emit updates for the graph (result.csv)

    def __init__(self, yaml_file, epochs, batch, imgsz, optimizer, device, output_folder, parent=None):
        super(TrainingThread, self).__init__(parent)
        self.yaml_file = yaml_file
        self.epochs = epochs
        self.batch = batch
        self.imgsz = imgsz
        self.optimizer = optimizer
        self.device = device
        self.output_folder = output_folder
        self.process = None

    def run(self):
        """
        Runs the YOLO training process and captures output in real time.
        """
        try:
            # YOLO command (Replace with the actual command or Python API call)
            command = [
                "yolo",  # Replace with YOLO CLI or Python executable
                "train",
                f"--data={self.yaml_file}",
                f"--epochs={self.epochs}",
                f"--batch={self.batch}",
                f"--imgsz={self.imgsz}",
                f"--optimizer={self.optimizer}",
                f"--device={self.device}"
            ]

            # Start the training process
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Read output line by line and emit it
            for line in self.process.stdout:
                self.output_signal.emit(line.strip())  # Send terminal output

                # Periodically emit graph updates (after every epoch)
                result_csv_path = os.path.join(self.output_folder, "result.csv")
                if os.path.exists(result_csv_path):
                    self.graph_signal.emit(result_csv_path)  # Send graph update signal

            # Wait for the process to complete
            self.process.wait()

        except Exception as e:
            self.output_signal.emit(f"Error: {str(e)}")

    def stop(self):
        """
        Stops the training process.
        """
        if self.process:
            self.process.terminate()
            self.process.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Add AGC logo to frame_agc_logo
        self.add_agc_logo()

        # Connect buttons to functions
        self.ui.buttonBox.accepted.connect(self.select_labeled_folder)
        self.ui.pushButton.clicked.connect(self.start_training)
        self.ui.buttonBox_2.accepted.connect(self.select_output_folder)        
        self.ui.buttonBox_3.accepted.connect(self.split_dataset)

        # Connect SAVE button to the create_yaml_file function
        self.ui.buttonBox_3.accepted.connect(self.create_yaml_file)
        self.setup_spinbox_connections()
        self.labeled_folder = None
        self.output_folder = None
        self.training_thread = None  # Thread for handling training

        # Set up terminal output
        self.terminal_output = QTextEdit(self.ui.frame_terminal)
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setGeometry(self.ui.frame_terminal.rect())
        self.terminal_output.setObjectName("terminalOutput")
        self.terminal_output.show()

        # Populate tableWidget_3
        self.populate_tableWidget_3()

        # Set up double-click events for tableWidget_3
        self.setup_tableWidget_3_events()

        # Connect spinBox changes to update the pie chart
        self.ui.doubleSpinBox_Train.valueChanged.connect(self.update_pie_chart)
        self.ui.doubleSpinBox_Validate.valueChanged.connect(self.update_pie_chart)
        self.ui.doubleSpinBox_Test.valueChanged.connect(self.update_pie_chart)

        self.setup_buttonBox_4_events()  # Connect buttonBox_4 events
        #self.setup_pushButton_event()  # Connect pushButton event

        # Initialize pie chart
        self.init_pie_chart()
        # Default pie chart update
        self.update_pie_chart()

        # Create a figure for the live graph
        #self.figure = Figure()
        #self.canvas = FigureCanvas(self.figure)
        # Add the canvas to the frame_terminal using a layout
        #layout = QVBoxLayout(self.ui.frame_terminal)
        #layout.addWidget(self.canvas)

        # Initialize the graph axes
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Training Metrics")
        self.ax.set_xlabel("Epoch")
        self.ax.set_ylabel("Value (0 - 1)")
        self.ax.set_ylim(0, 1)  # Y-axis range is 0 to 1

    def add_agc_logo(self):
        """
        Add the AGC logo image to the frame_agc_logo.
        """
        # Create a QLabel to hold the image
        logo_label = QLabel(self.ui.frame_agc_logo)
        logo_label.setObjectName("logo_label")

        # Load the image using QPixmap
        pixmap = QPixmap("agc-logo-png-transparent-logo-v2.png")

        # Set the pixmap to the QLabel
        logo_label.setPixmap(pixmap)

        # Scale the image to fit the frame while maintaining aspect ratio
        logo_label.setScaledContents(True)

        # Add the QLabel to the frame_agc_logo using a layout
        layout = QVBoxLayout(self.ui.frame_agc_logo)
        layout.addWidget(logo_label)

    def init_pie_chart(self):
        """
        Initialize the pie chart inside the frame_data_split_ratio.
        """
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Add the canvas to the frame_data_split_ratio using a layout
        layout = QVBoxLayout(self.ui.frame_data_split_ratio)
        layout.addWidget(self.canvas)

    def update_pie_chart(self):
        """
        Update the pie chart based on the current Train, Validate, and Test percentages.
        """
        train_percentage = self.ui.doubleSpinBox_Train.value()
        validate_percentage = self.ui.doubleSpinBox_Validate.value()
        test_percentage = self.ui.doubleSpinBox_Test.value()

        # Clear the previous plot
        self.figure.clear()

        # Add the pie chart
        ax = self.figure.add_subplot(111)
        data = [train_percentage, validate_percentage, test_percentage]
        labels = ['Train', 'Validate', 'Test']
        colors = ['#4CAF50', '#FFC107', '#F44336']  # Green, Yellow, Red
        ax.pie(data, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Refresh the canvas
        self.canvas.draw()


    def select_labeled_folder(self):
        """
        Open a dialog to select the labeled folder, and process the folder with a progress bar.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Labeled Images Folder")
        if folder:
            self.labeled_folder = folder
            self.ui.textEdit.setPlainText(folder)

            # Display a progress bar while processing the folder
            progress_dialog = QProgressDialog("Processing labeled folder...", "Cancel", 0, 100, self)
            progress_dialog.setWindowTitle("Progress")
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setMinimumDuration(0)
            progress_dialog.setValue(0)

            try:
                # Collect class names and count files with progress updates
                classes_file = None

                # Step 1: Search for the "classes.txt" file in the folder
                progress_dialog.setLabelText("Searching for classes.txt...")
                QCoreApplication.processEvents()  # Process UI events
                for root, _, files in os.walk(folder):
                    if progress_dialog.wasCanceled():
                        raise Exception("Operation canceled by the user.")
                    for file in files:
                        if file == "classes.txt":
                            classes_file = os.path.join(root, file)
                            break
                    if classes_file:
                        break

                # Update progress
                progress_dialog.setValue(10)
                QCoreApplication.processEvents()

                if not classes_file:
                    progress_dialog.cancel()
                    QMessageBox.critical(self, "Error", "classes.txt file not found in the selected folder.")
                    return

                # Step 2: Read the class names from "classes.txt"
                progress_dialog.setLabelText("Reading classes.txt...")
                QCoreApplication.processEvents()
                classes = []
                with open(classes_file, "r") as f:
                    for line in f:
                        classes.append(line.strip())

                # Update progress
                progress_dialog.setValue(40)
                QCoreApplication.processEvents()

                # Step 3: Initialize a dictionary to count occurrences of each class
                progress_dialog.setLabelText("Counting labels...")
                QCoreApplication.processEvents()
                class_counts = {class_name: 0 for class_name in classes}
                for root, _, files in os.walk(folder):
                    if progress_dialog.wasCanceled():
                        raise Exception("Operation canceled by the user.")
                    for file in files:
                        if file.endswith(".txt") and file != "classes.txt":
                            label_file = os.path.join(root, file)
                            with open(label_file, "r") as f:
                                for line in f:
                                    class_id = int(line.split()[0])
                                    if 0 <= class_id < len(classes):
                                        class_name = classes[class_id]
                                        class_counts[class_name] += 1

                # Update progress
                progress_dialog.setValue(70)
                QCoreApplication.processEvents()

                # Step 4: Populate the tableWidget_2 with class names and their counts
                progress_dialog.setLabelText("Populating table...")
                QCoreApplication.processEvents()
                self.ui.tableWidget_2.setRowCount(len(classes))
                for i, class_name in enumerate(classes):
                    if progress_dialog.wasCanceled():
                        raise Exception("Operation canceled by the user.")
                    self.ui.tableWidget_2.setItem(i, 0, QTableWidgetItem(class_name))  # Class Name column
                    self.ui.tableWidget_2.setItem(i, 1, QTableWidgetItem(str(class_counts[class_name])))  # Total column

                    # Initialize Train, Validate, and Test counts as 0
                    self.ui.tableWidget_2.setItem(i, 2, QTableWidgetItem("0"))  # Train column
                    self.ui.tableWidget_2.setItem(i, 3, QTableWidgetItem("0"))  # Validate column
                    self.ui.tableWidget_2.setItem(i, 4, QTableWidgetItem("0"))  # Test column

                # Update progress
                progress_dialog.setValue(90)
                QCoreApplication.processEvents()

                # Step 5: Update the table based on the current spinbox values
                train_percentage = self.ui.doubleSpinBox_Train.value()
                validate_percentage = self.ui.doubleSpinBox_Validate.value()
                test_percentage = self.ui.doubleSpinBox_Test.value()
                self.update_table_widget(train_percentage, validate_percentage, test_percentage)

                # Finalize progress
                progress_dialog.setValue(100)
                QCoreApplication.processEvents()
                QMessageBox.information(self, "Success", "Labeled folder processed successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Warning", str(e))
            finally:
                progress_dialog.close()

    def select_output_folder(self):
        """
        Open a dialog to select the output folder. This folder will store the .yaml file and other training outputs.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder  # Set the output_folder attribute
            self.ui.textEdit_2.setPlainText(folder)  # Update the UI with the selected folder
            QMessageBox.information(self, "Success", f"Output folder selected: {folder}")

            # Update the "data" row in tableWidget_3
            self.update_data_row()

    def update_data_row(self):
        """
        Update the "data" row in tableWidget_3 to reflect the current output folder.
        """
        table = self.ui.tableWidget_3

        # Find the row with the label "data"
        for row_index in range(table.rowCount()):
            label_item = table.verticalHeaderItem(row_index)
            if label_item and label_item.text() == "data":
                # Update the "data" cell with the new output folder path
                table.setItem(row_index, 0, self.create_static_item(self.output_folder))
                break


    def populate_classes(self, folder):
        classes_file = None

        # Step 1: Search for the "classes.txt" file in the folder
        for root, _, files in os.walk(folder):
            for file in files:
                if file == "classes.txt":
                    classes_file = os.path.join(root, file)
                    break
            if classes_file:
                break

        # Step 2: If "classes.txt" is not found, show an error message
        if not classes_file:
            QMessageBox.critical(self, "Error", "classes.txt file not found in the selected folder.")
            return

        # Step 3: Read the class names from "classes.txt"
        classes = []
        with open(classes_file, "r") as f:
            for line in f:
                classes.append(line.strip())

        # Step 4: Initialize a dictionary to count occurrences of each class
        class_counts = {class_name: 0 for class_name in classes}

        # Step 5: Search for YOLO label files (.txt) in the folder and count occurrences
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(".txt") and file != "classes.txt":  # Skip the classes.txt file
                    label_file = os.path.join(root, file)

                    # Read the content of the label file
                    with open(label_file, "r") as f:
                        for line in f:
                            class_id = int(line.split()[0])  # Extract class ID (first value in each line)
                            if 0 <= class_id < len(classes):  # Ensure class ID is valid
                                class_name = classes[class_id]
                                class_counts[class_name] += 1

        # Step 6: Populate the tableWidget_2 with class names and their counts
        self.ui.tableWidget_2.setRowCount(len(classes))
        for i, class_name in enumerate(classes):
            self.ui.tableWidget_2.setItem(i, 0, QTableWidgetItem(class_name))  # Class Name column
            self.ui.tableWidget_2.setItem(i, 1, QTableWidgetItem(str(class_counts[class_name])))  # Total column

            # Initialize Train, Validate, and Test counts as 0
            self.ui.tableWidget_2.setItem(i, 2, QTableWidgetItem("0"))  # Train column
            self.ui.tableWidget_2.setItem(i, 3, QTableWidgetItem("0"))  # Validate column
            self.ui.tableWidget_2.setItem(i, 4, QTableWidgetItem("0"))  # Test column

        # Update the table based on the current spinbox values
        train_percentage = self.ui.doubleSpinBox_Train.value()
        validate_percentage = self.ui.doubleSpinBox_Validate.value()
        test_percentage = self.ui.doubleSpinBox_Test.value()
        self.update_table_widget(train_percentage, validate_percentage, test_percentage)

    def split_dataset(self):
        if not self.labeled_folder or not self.output_folder:
            QMessageBox.critical(self, "Error", "Please select both labeled and output folders.")
            return

        train_split = self.ui.doubleSpinBox_Train.value() / 100
        val_split = self.ui.doubleSpinBox_Validate.value() / 100
        test_split = self.ui.doubleSpinBox_Test.value() / 100

        if abs(train_split + val_split + test_split - 1.0) > 0.01:
            QMessageBox.critical(self, "Error", "Train, Validate, and Test splits must sum to 100%.")
            return

        # Create output folders for train, val, and test splits
        for split in ["train", "val", "test"]:
            image_split_path = os.path.join(self.output_folder, "images", split)
            label_split_path = os.path.join(self.output_folder, "labels", split)
            os.makedirs(image_split_path, exist_ok=True)
            os.makedirs(label_split_path, exist_ok=True)

        # Read classes from classes.txt
        classes_file = os.path.join(self.labeled_folder, "classes.txt")
        if not os.path.exists(classes_file):
            QMessageBox.critical(self, "Error", "classes.txt file not found in the labeled folder.")
            return

        # Collect all images and their corresponding labels
        paired_files = []  # List of (image_path, label_path) pairs
        for root, _, files in os.walk(self.labeled_folder):
            for file in files:
                if file.endswith(".jpg") or file.endswith(".png"):  # Find image files
                    image_path = os.path.join(root, file)
                    label_path = image_path.replace("images", "labels").replace(".jpg", ".txt").replace(".png", ".txt")
                    if os.path.exists(label_path):  # Check if corresponding label file exists
                        paired_files.append((image_path, label_path))

        # Check if there are any valid pairs
        if not paired_files:
            QMessageBox.critical(self, "Error", "No valid image-label pairs found in the labeled folder.")
            return

        total_files = len(paired_files)
        train_count = int(train_split * total_files)
        val_count = int(val_split * total_files)

        # Initialize progress dialog
        progress_dialog = QProgressDialog("Splitting dataset...", "Cancel", 0, total_files, self)
        progress_dialog.setWindowTitle("Progress")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)  # Show immediately

        # Split data into train, val, and test
        for i, (image_file, label_file) in enumerate(paired_files):
            if i < train_count:
                split = "train"
            elif i < train_count + val_count:
                split = "val"
            else:
                split = "test"

            # Copy image and label files to the respective split directories
            image_dest = os.path.join(self.output_folder, "images", split, os.path.basename(image_file))
            label_dest = os.path.join(self.output_folder, "labels", split, os.path.basename(label_file))

            shutil.copy(image_file, image_dest)
            shutil.copy(label_file, label_dest)

            # Update progress dialog
            progress_dialog.setValue(i + 1)  # Update progress
            if progress_dialog.wasCanceled():
                QMessageBox.warning(self, "Canceled", "Dataset splitting was canceled.")
                return

        progress_dialog.close()  # Close the progress dialog when done
        QMessageBox.information(self, "Success", "Dataset split and saved successfully!")

    def setup_spinbox_connections(self):
        # Connect spin boxes to the adjust_split function
        self.ui.doubleSpinBox_Train.valueChanged.connect(lambda: self.adjust_split_and_update_table('train'))
        self.ui.doubleSpinBox_Validate.valueChanged.connect(lambda: self.adjust_split_and_update_table('validate'))
        self.ui.doubleSpinBox_Test.valueChanged.connect(lambda: self.adjust_split_and_update_table('test'))


    def adjust_split_and_update_table(self, changed_spinbox):
        # Get current spinbox values
        train_percentage = self.ui.doubleSpinBox_Train.value()
        validate_percentage = self.ui.doubleSpinBox_Validate.value()
        test_percentage = self.ui.doubleSpinBox_Test.value()

        # Ensure the percentages sum to 100%
        total_percentage = train_percentage + validate_percentage + test_percentage
        if total_percentage > 100.0:
            excess = total_percentage - 100.0

            if changed_spinbox == 'train':
                validate_percentage = max(0, validate_percentage - excess / 2)
                test_percentage = max(0, test_percentage - excess / 2)
            elif changed_spinbox == 'validate':
                train_percentage = max(0, train_percentage - excess / 2)
                test_percentage = max(0, test_percentage - excess / 2)
            elif changed_spinbox == 'test':
                train_percentage = max(0, train_percentage - excess / 2)
                validate_percentage = max(0, validate_percentage - excess / 2)

            # Update spinboxes with adjusted percentages
            self.ui.doubleSpinBox_Train.setValue(train_percentage)
            self.ui.doubleSpinBox_Validate.setValue(validate_percentage)
            self.ui.doubleSpinBox_Test.setValue(test_percentage)

        # Update the table widget values
        self.update_table_widget(train_percentage, validate_percentage, test_percentage)

    def update_table_widget(self, train_percentage, validate_percentage, test_percentage):
        """
        Update the tableWidget_2 with the split values (Train, Validate, Test) for each class.
        """
        row_count = self.ui.tableWidget_2.rowCount()

        for row in range(row_count):
            # Get the class name (already populated in the first column)
            class_name_item = self.ui.tableWidget_2.item(row, 0)
            if not class_name_item:
                continue
            class_name = class_name_item.text()  # Class name (used for reference or debugging)

            # Get the total count for this class (already populated in the second column)
            total_item = self.ui.tableWidget_2.item(row, 1)
            if not total_item:
                continue
            total_count = int(total_item.text())  # Total instances of the class

            # Calculate Train, Validate, and Test counts based on percentages
            train_count = int(total_count * train_percentage / 100)
            validate_count = int(total_count * validate_percentage / 100)
            test_count = max(0, total_count - train_count - validate_count)  # Ensure Test count is >= 0

            # Update the Train, Validate, and Test columns
            self.ui.tableWidget_2.setItem(row, 2, QTableWidgetItem(str(train_count)))   # Train column
            self.ui.tableWidget_2.setItem(row, 3, QTableWidgetItem(str(validate_count)))  # Validate column
            self.ui.tableWidget_2.setItem(row, 4, QTableWidgetItem(str(test_count)))    # Test column

            # Debugging Reference (Optional)
            print(f"Class: {class_name}, Total: {total_count}, Train: {train_count}, Validate: {validate_count}, Test: {test_count}")

    def create_yaml_file(self):
        """
        Create a .yaml file for YOLO training format in the selected output folder.
        """
        if not self.output_folder:
            QMessageBox.critical(self, "Error", "Please select an output folder.")
            return

        # Path to save the detect.yaml file
        yaml_file_path = os.path.join(self.output_folder, "detect.yaml")

        # Collect class names from tableWidget_2
        row_count = self.ui.tableWidget_2.rowCount()
        class_names = {}
        for row in range(row_count):
            class_item = self.ui.tableWidget_2.item(row, 0)
            if class_item:
                class_names[row] = class_item.text()

        # YAML structure
        yaml_data = {
            "path": self.output_folder,  # Dataset root dir (same as output folder)
            "train": "images/train",  # Train images (relative to 'path')
            "val": "images/val",  # Validation images (relative to 'path')
            "test": "images/test",  # Test images (optional)
            "names": class_names,  # Class names
            "download": ""  # Download script/URL (optional)
        }

        # Write the YAML file
        try:
            with open(yaml_file_path, "w") as yaml_file:
                yaml.dump(yaml_data, yaml_file, default_flow_style=False)
            QMessageBox.information(self, "Success", f"YAML file created at: {yaml_file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create YAML file: {str(e)}")

    def start_training(self):
        """
        Starts the YOLO training process in a separate thread and displays the output in real time.
        """
        # Check if output folder is set
        if not self.output_folder:
            QMessageBox.critical(self, "Error", "Please select an output folder for training.")
            return

        yaml_file = os.path.join(self.output_folder, "detect.yaml")
        if not os.path.exists(yaml_file):
            QMessageBox.critical(self, "Error", "Missing detect.yaml file in the output folder.")
            return

        # Get training parameters from tableWidget_3
        epochs = int(self.ui.tableWidget_3.cellWidget(2, 0).value())  # Row 2: Spinbox for epochs
        batch = int(self.ui.tableWidget_3.cellWidget(5, 0).value())  # Row 5: Spinbox for batch
        imgsz = int(self.ui.tableWidget_3.cellWidget(6, 0).currentText())  # Row 6: Dropdown for imgsz
        optimizer = self.ui.tableWidget_3.cellWidget(9, 0).currentText()  # Row 9: Dropdown for optimizer

        # Check CUDA availability
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Start the training thread
        self.training_thread = TrainingThread(
            yaml_file, epochs, batch, imgsz, optimizer, device, self.output_folder
        )
        self.training_thread.output_signal.connect(self.update_terminal)  # Only terminal message removed
        self.training_thread.start()

    def populate_tableWidget_3(self):
        """
        Populate tableWidget_3 with the specified values and widgets.
        """
        table = self.ui.tableWidget_3

        # Clear any existing rows
        table.setRowCount(0)

        # Define rows and their corresponding widgets or static values
        rows = [
            ("data", self.create_static_item(self.output_folder or "Not Selected")),  # Dynamically update "data"
            ("pre-train", self.create_static_item("YOLO('yolo11n.pt')")),  # Static value
            ("epochs", self.create_spinbox(100, 1, 10000, 1)),  # Spinbox (default=100)
            ("time", self.create_combobox([None, 1, 2, 3, 4, 5, 6, 8, 12, 24])),  # Dropdown
            ("patience", self.create_spinbox(100, 1, 1000, 1)),  # Spinbox (default=100)
            ("batch", self.create_spinbox(16, 1, 1024, 1)),  # Spinbox (default=16)
            ("imgsz", self.create_combobox([320, 640, 960, 1080])),  # Dropdown
            ("save", self.create_static_item("True")),  # Static value
            ("save_period", self.create_static_item("-1")),  # Static value
            ("optimizer", self.create_combobox(["SGD", "Adam", "Adamax", "AdamW", "NAdam", "RAdam", "RMSProp", "auto"])),  # Dropdown
        ]

        # Populate the table with rows and widgets
        for row_index, (label, widget_or_item) in enumerate(rows):
            table.insertRow(row_index)

            # Set row label
            item_label = QTableWidgetItem(label)
            item_label.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Non-editable
            table.setVerticalHeaderItem(row_index, item_label)

            # Add static item or widget to the table
            if isinstance(widget_or_item, QTableWidgetItem):
                table.setItem(row_index, 0, widget_or_item)  # Use setItem for static values
            else:
                table.setCellWidget(row_index, 0, widget_or_item)  # Use setCellWidget for widgets

    def setup_tableWidget_3_events(self):
        """
        Connects double-click events for tableWidget_3.
        """
        self.ui.tableWidget_3.cellDoubleClicked.connect(self.handle_tableWidget_3_double_click)

    def handle_tableWidget_3_double_click(self, row, column):
        """
        Handles double-click events for tableWidget_3.
        Opens a file dialog to select a folder if the 'data' row is double-clicked.
        """
        table = self.ui.tableWidget_3

        # Check if the double-clicked row corresponds to the "data" label
        label_item = table.verticalHeaderItem(row)
        if label_item and label_item.text() == "data":
            # Open a folder selection dialog
            folder = QFileDialog.getExistingDirectory(self, "Select Dataset Root Directory")
            if folder:
                # Update the output_folder and the "data" row in the table
                self.output_folder = folder
                table.setItem(row, column, self.create_static_item(folder))


    def create_static_item(self, value):
        """
        Create a static (non-editable) QTableWidgetItem.
        """
        item = QTableWidgetItem(str(value))
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Non-editable
        return item
    
    def create_combobox(self, items):
        """
        Create a QComboBox with the specified items.
        """
        combo = QComboBox()
        for item in items:
            combo.addItem(str(item))
        return combo

    def create_spinbox(self, default, minimum, maximum, step):
        """
        Create a QSpinBox with the specified range and default value.
        """
        spinbox = QSpinBox()
        spinbox.setValue(default)
        spinbox.setMinimum(minimum)
        spinbox.setMaximum(maximum)
        spinbox.setSingleStep(step)
        return spinbox

    def setup_buttonBox_4_events(self):
        """
        Connect buttonBox_4 to Reset and Apply behavior.
        """
        # Connect Reset button
        self.ui.buttonBox_4.button(QDialogButtonBox.Reset).clicked.connect(self.reset_tableWidget_3)

        # Connect Apply button
        self.ui.buttonBox_4.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)

    def reset_tableWidget_3(self):
        """
        Reset tableWidget_3 to its default values.
        """
        self.populate_tableWidget_3()  # Repopulate the table with default values
        QMessageBox.information(self, "Reset", "All values in the table have been reset to their default values.")

    def apply_changes(self):
        """
        Change the color of the pushButton to light green when Apply is clicked.
        """
        # Change the color of the pushButton to light green
        self.ui.pushButton.setStyleSheet("background-color: lightgreen;")
        QMessageBox.information(self, "Apply", "Changes applied successfully!")

    def start_training(self):
        """
        Starts the YOLO training process and displays status in frame_terminal.
        """
        # Check if output folder is set
        if not self.output_folder:
            QMessageBox.critical(self, "Error", "Please select an output folder for training.")
            return

        yaml_file = os.path.join(self.output_folder, "detect.yaml")
        if not os.path.exists(yaml_file):
            QMessageBox.critical(self, "Error", "Missing detect.yaml file in the output folder.")
            return

        try:
            # Get training parameters from tableWidget_3
            epochs = int(self.ui.tableWidget_3.cellWidget(2, 0).value())  # Row 2: Spinbox for epochs
            batch = int(self.ui.tableWidget_3.cellWidget(5, 0).value())  # Row 5: Spinbox for batch
            imgsz = int(self.ui.tableWidget_3.cellWidget(6, 0).currentText())  # Row 6: Dropdown for imgsz
            optimizer = self.ui.tableWidget_3.cellWidget(9, 0).currentText()  # Row 9: Dropdown for optimizer

            # Check CUDA availability
            if torch.cuda.is_available():
                device = 'cuda'  # use GPU
                self.update_terminal("GPU is available. Training on GPU.")
            else:
                device = 'cpu'  # use CPU
                self.update_terminal("GPU is not available. Training on CPU.")

            # Load the YOLO model
            model = YOLO("yolo11n.pt")  # Replace with the desired pretrained model
            self.update_terminal("YOLO model loaded successfully.")

            # Start training
            self.update_terminal("Starting training...")
            results = model.train(
                data=yaml_file,
                epochs=epochs,
                batch=batch,
                imgsz=imgsz,
                device=device,
                optimizer=optimizer,
                save=True,
            )

            # Display success message in terminal
            self.update_terminal("Training completed successfully!")
            self.update_terminal(f"Results: {results}")

        except Exception as e:
            self.update_terminal(f"Error during training: {str(e)}")
            QMessageBox.critical(self, "Training Error", str(e))

    def update_terminal(self, message):
        """
        Empty function to handle terminal output (graph and message display removed).
        """
        pass  # No terminal output or graph updates

    def update_graph(self, csv_file_path):
        """
        Function removed since graph updates are no longer required.
        """
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
