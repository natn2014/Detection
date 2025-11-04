import sys
import time
import json
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
                                QDialog, QLabel, QComboBox, QSpinBox, QDialogButtonBox,
                                QGroupBox, QCheckBox, QListWidget, QTextEdit, QTableWidget,
                                QTableWidgetItem, QHeaderView, QMenu, QLineEdit, QMessageBox,
                                QInputDialog)
from PySide6.QtCore import QTimer, Qt
from relay_b import Relay
from utils.config_manager import load_config, save_config

class SequenceDialog(QDialog):
    """Dialog to add a new sequence rule."""
    def __init__(self, parent=None, edit_sequence=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Sequence" if edit_sequence else "Add Sequence")
        self.setModal(True)
        self.resize(600, 650)
        layout = QVBoxLayout()
        
        # Sequence Type
        type_group = QGroupBox("Sequence Type")
        type_layout = QVBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Station Operation", "Production Line Sequence"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Simple Logic Group
        self.simple_group = QGroupBox("Station Operation Configuration")
        simple_layout = QVBoxLayout()
        
        # Station Operation Type
        self.operation_combo = QComboBox()
        self.operation_combo.addItems([
            "Tool Picking Sequence",
            "Part Detection & Process", 
            "Sequential Operation", 
            "Conditional Process",
            "Safety Interlock"
        ])
        self.operation_combo.currentTextChanged.connect(self.on_operation_changed)
        simple_layout.addWidget(QLabel("Operation Type:"))
        simple_layout.addWidget(self.operation_combo)
        
        # Part Detection Sensor
        self.part_sensor_label = QLabel("Part Detection Sensor (DI):")
        self.part_sensor_spin = QSpinBox()
        self.part_sensor_spin.setRange(1, 8)
        self.part_sensor_spin.setValue(4)  # Default DI4 for part detect
        simple_layout.addWidget(self.part_sensor_label)
        simple_layout.addWidget(self.part_sensor_spin)
        
        # Process Device
        self.process_device_label = QLabel("Process Device (DO):")
        self.process_device_spin = QSpinBox()
        self.process_device_spin.setRange(1, 8)
        self.process_device_spin.setValue(4)  # Default DO4 for main process
        simple_layout.addWidget(self.process_device_label)
        simple_layout.addWidget(self.process_device_spin)
        
        # First Tool Light
        self.first_tool_label = QLabel("1st Tool Light (DO):")
        self.first_tool_spin = QSpinBox()
        self.first_tool_spin.setRange(1, 8)
        self.first_tool_spin.setValue(2)  # Default DO2
        simple_layout.addWidget(self.first_tool_label)
        simple_layout.addWidget(self.first_tool_spin)
        
        # Second Tool Light
        self.second_tool_label = QLabel("2nd Tool Light (DO):")
        self.second_tool_spin = QSpinBox()
        self.second_tool_spin.setRange(1, 8)
        self.second_tool_spin.setValue(3)  # Default DO3
        simple_layout.addWidget(self.second_tool_label)
        simple_layout.addWidget(self.second_tool_spin)
        
        # Tools Picked Sensor
        self.tools_picked_label = QLabel("Tools Picked Sensor (DI):")
        self.tools_picked_spin = QSpinBox()
        self.tools_picked_spin.setRange(1, 8)
        self.tools_picked_spin.setValue(3)  # Default DI3
        simple_layout.addWidget(self.tools_picked_label)
        simple_layout.addWidget(self.tools_picked_spin)
        
        # Tools Collected Sensor
        self.tools_collected_label = QLabel("Tools Collected Sensor (DI):")
        self.tools_collected_spin = QSpinBox()
        self.tools_collected_spin.setRange(1, 8)
        self.tools_collected_spin.setValue(2)  # Default DI2
        simple_layout.addWidget(self.tools_collected_label)
        simple_layout.addWidget(self.tools_collected_spin)
        
        # Alarm Device
        self.alarm_device_label = QLabel("Alarm Device (DO):")
        self.alarm_device_spin = QSpinBox()
        self.alarm_device_spin.setRange(1, 8)
        self.alarm_device_spin.setValue(5)  # Default DO5
        simple_layout.addWidget(self.alarm_device_label)
        simple_layout.addWidget(self.alarm_device_spin)
        
        # Step Configuration for Tool Picking
        step_config_group = QGroupBox("Tool Picking Steps")
        step_config_layout = QVBoxLayout(step_config_group)
        
        # Timeout Configuration
        self.timeout_label = QLabel("Timeout (seconds):")
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)  # Default 30 seconds
        step_config_layout.addWidget(self.timeout_label)
        step_config_layout.addWidget(self.timeout_spin)
        
        # Step sequence display
        self.step_sequence_text = QTextEdit()
        self.step_sequence_text.setReadOnly(True)
        self.step_sequence_text.setMaximumHeight(150)
        self.step_sequence_text.setText("""Tool Picking Sequence:
1. Wait for Part Detection (DI4)
2. Turn ON Process Device (DO4)
3. Show 1st Tool Light (DO2)
4. Wait for Tools Picked (DI3)
5. Show 2nd Tool Light (DO3)
6. Wait for Tools Collected (DI2)
7. Complete sequence and turn OFF all outputs
        
If timeout occurs, Alarm (DO5) will activate until operator action.""")
        step_config_layout.addWidget(QLabel("Sequence Steps:"))
        step_config_layout.addWidget(self.step_sequence_text)
        
        simple_layout.addWidget(step_config_group)
        
        # Expected Feedback Sensor
        self.feedback_sensor_label = QLabel("Expected Feedback Sensor (DI):")
        self.feedback_sensor_spin = QSpinBox()
        self.feedback_sensor_spin.setRange(1, 8)
        self.feedback_sensor_spin.setValue(2)
        simple_layout.addWidget(self.feedback_sensor_label)
        simple_layout.addWidget(self.feedback_sensor_spin)
        
        # Skip/Error Sensor
        self.skip_sensor_label = QLabel("Skip/Error Sensor (DI):")
        self.skip_sensor_spin = QSpinBox()
        self.skip_sensor_spin.setRange(1, 8)
        self.skip_sensor_spin.setValue(3)
        simple_layout.addWidget(self.skip_sensor_label)
        simple_layout.addWidget(self.skip_sensor_spin)
        
        # Timeout settings
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(10)
        self.timeout_spin.setSuffix(" sec")
        simple_layout.addWidget(QLabel("Operation Timeout:"))
        simple_layout.addWidget(self.timeout_spin)
        
        # Process Duration
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(0, 3600)
        self.duration_spin.setValue(5)
        self.duration_spin.setSuffix(" sec")
        simple_layout.addWidget(QLabel("Process Duration (0 = until feedback):"))
        simple_layout.addWidget(self.duration_spin)
        
        self.blink_check = QCheckBox("Blink Process Device (ON/OFF every 1 sec)")
        simple_layout.addWidget(self.blink_check)
        
        self.simple_group.setLayout(simple_layout)
        layout.addWidget(self.simple_group)
        
        # Multi-Step Group
        self.multi_group = QGroupBox("Production Line Sequence Configuration")
        multi_layout = QVBoxLayout()
        
        multi_layout.addWidget(QLabel("Production Line Step Format:"))
        info_label = QLabel(
            "• Part Detection: PART_DI1->PROCESS_DO2->FEEDBACK_DI3:10s\n"
            "• Process with Skip: PART_DI1->PROCESS_DO2->FEEDBACK_DI3|SKIP_DI4:15s\n"
            "• Station Process: STATION_DI2->CLAMP_DO1:2s->DRILL_DO2:5s->UNCLAMP_DO1(OFF)\n"
            "• Quality Check: PART_DI1->INSPECT_DO3->PASS_DI2|FAIL_DI3->SORT_DO4\n"
            "• One-Shot Trigger: DI2(EDGE)->DO2(ON) or DI2(ONCE)->DO2(ON)\n"
            "• Wait for Clear: PART_DI1->PROCESS_DO2->WAIT_CLEAR:DI5:30s\n"
            "• Error Handling: PART_DI1->PROCESS_DO2->TIMEOUT:10s->ERROR_DO8\n"
            "• Multi-Station: STATION1_DI1->PROCESS1_DO1->TRANSFER_DO2->STATION2_DI2\n"
            "• Safety: ESTOP_DI8(OFF)->ALL_STOP"
        )
        info_label.setStyleSheet("color: #666; font-size: 9pt;")
        multi_layout.addWidget(info_label)
        
        self.steps_text = QTextEdit()
        self.steps_text.setPlaceholderText(
            "Production Line Examples:\n"
            "DI2(EDGE)->DO2(ON)     # Trigger once per DI2 activation\n"
            "PART_DI1->CLAMP_DO1:2s\n"
            "CLAMP_FEEDBACK_DI2->DRILL_DO2:5s\n"
            "DRILL_FEEDBACK_DI3->UNCLAMP_DO1(OFF)\n"
            "UNCLAMP_FEEDBACK_DI4->TRANSFER_DO3:3s\n"
            "TRANSFER_COMPLETE_DI5->STATION_READY_DO4(OFF)\n"
            "QUALITY_CHECK_DI6->PASS_DO5|FAIL_DO6\n"
            "ERROR_DI7->ALARM_DO8(BLINK):10s\n"
            "ESTOP_DI8(OFF)->EMERGENCY_STOP"
        )
        self.steps_text.setMaximumHeight(180)
        multi_layout.addWidget(self.steps_text)
        
        # Return to initial state option
        self.return_initial_check = QCheckBox("Return to initial state after completion")
        self.return_initial_check.setChecked(True)
        multi_layout.addWidget(self.return_initial_check)
        
        self.multi_group.setLayout(multi_layout)
        self.multi_group.hide()
        layout.addWidget(self.multi_group)
        
        # Initial State Group
        state_group = QGroupBox("Initial & End State Configuration")
        state_layout = QVBoxLayout()
        
        state_layout.addWidget(QLabel("Set which DO channels should be ON/OFF at start and end:"))
        
        self.state_table = QTableWidget(8, 3)
        self.state_table.setHorizontalHeaderLabels(["DO Channel", "Initial State", "End State"])
        self.state_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.state_table.setMaximumHeight(200)
        
        for i in range(8):
            # Channel label
            channel_item = QTableWidgetItem(f"DO {i+1}")
            channel_item.setFlags(channel_item.flags() & ~Qt.ItemIsEditable)
            self.state_table.setItem(i, 0, channel_item)
            
            # Initial state combo
            initial_combo = QComboBox()
            initial_combo.addItems(["No Change", "OFF", "ON"])
            self.state_table.setCellWidget(i, 1, initial_combo)
            
            # End state combo
            end_combo = QComboBox()
            end_combo.addItems(["No Change", "OFF", "ON"])
            self.state_table.setCellWidget(i, 2, end_combo)
        
        state_layout.addWidget(self.state_table)
        state_group.setLayout(state_layout)
        layout.addWidget(state_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Load existing sequence data if editing
        if edit_sequence:
            self.load_sequence(edit_sequence)
    
    def load_sequence(self, seq):
        """Load sequence data into dialog fields."""
        # Set sequence type
        if seq['type'] == 'station':
            self.type_combo.setCurrentText("Station Operation")
            self.operation_combo.setCurrentText(seq.get('operation_type', 'Part Detection & Process'))
            self.part_sensor_spin.setValue(seq.get('part_sensor', 1))
            self.process_device_spin.setValue(seq.get('process_device', 1))
            self.feedback_sensor_spin.setValue(seq.get('feedback_sensor', 2))
            self.skip_sensor_spin.setValue(seq.get('skip_sensor', 3))
            self.timeout_spin.setValue(seq.get('timeout', 10))
            self.duration_spin.setValue(seq.get('duration', 5))
            self.blink_check.setChecked(seq.get('blink_mode', False))
        else:
            self.type_combo.setCurrentText("Production Line Sequence")
            self.steps_text.setPlainText(seq.get('steps', ''))
            self.return_initial_check.setChecked(seq.get('return_to_initial', True))
        
        # Load initial states
        if seq.get('initial_states'):
            for do_ch, state in seq['initial_states'].items():
                initial_combo = self.state_table.cellWidget(int(do_ch) - 1, 1)
                initial_combo.setCurrentText("ON" if state else "OFF")
        
        # Load end states
        if seq.get('end_states'):
            for do_ch, state in seq['end_states'].items():
                end_combo = self.state_table.cellWidget(int(do_ch) - 1, 2)
                end_combo.setCurrentText("ON" if state else "OFF")
    
    def on_type_changed(self, text):
        """Toggle between station operation and production line sequence."""
        is_production_line = text == "Production Line Sequence"
        self.simple_group.setVisible(not is_production_line)
        self.multi_group.setVisible(is_production_line)
    
    def on_operation_changed(self, text):
        """Show/hide fields based on operation type."""
        show_feedback = text in ["Sequential Operation", "Part Detection & Process"]
        show_skip = text in ["Conditional Process", "Part Detection & Process"]
        
        self.feedback_sensor_label.setVisible(show_feedback)
        self.feedback_sensor_spin.setVisible(show_feedback)
        self.skip_sensor_label.setVisible(show_skip)
        self.skip_sensor_spin.setVisible(show_skip)
        
        # Update step sequence display based on operation type
        if text == "Tool Picking Sequence":
            self.step_sequence_text.setText("""Tool Picking Sequence:
1. Wait for Part Detection (DI4)
2. Turn ON Process Device (DO4)
3. Show 1st Tool Light (DO2)
4. Wait for Tools Picked (DI3)
5. Show 2nd Tool Light (DO3)
6. Wait for Tools Collected (DI2)
7. Complete sequence and turn OFF all outputs
        
If timeout occurs, Alarm (DO5) will activate until operator action.""")
        else:
            self.step_sequence_text.setText("""Generic Station Operation:
1. Wait for sensor trigger
2. Activate process device
3. Wait for completion feedback
4. Turn OFF all outputs
        
Configure specific sensors and devices above.""")
    
    def get_sequence(self):
        """Return the configured sequence."""
        # Get initial and end states
        initial_states = {}
        end_states = {}
        for i in range(8):
            initial_combo = self.state_table.cellWidget(i, 1)
            end_combo = self.state_table.cellWidget(i, 2)
            
            initial_state = initial_combo.currentText()
            end_state = end_combo.currentText()
            
            if initial_state != "No Change":
                initial_states[i + 1] = (initial_state == "ON")
            if end_state != "No Change":
                end_states[i + 1] = (end_state == "ON")
        
        base_seq = {
            'initial_states': initial_states,
            'end_states': end_states
        }
        
        if self.type_combo.currentText() == "Station Operation":
            operation_type = self.operation_combo.currentText()
            base_seq.update({
                'type': 'station',
                'operation_type': operation_type,
                'part_sensor': self.part_sensor_spin.value(),
                'process_device': self.process_device_spin.value(),
                'feedback_sensor': self.feedback_sensor_spin.value(),
                'skip_sensor': self.skip_sensor_spin.value(),
                'timeout': self.timeout_spin.value(),
                'duration': self.duration_spin.value(),
                'blink_mode': self.blink_check.isChecked()
            })
            
            # Add specific configuration for Tool Picking Sequence
            if operation_type == "Tool Picking Sequence":
                base_seq.update({
                    'first_tool_light': self.first_tool_spin.value(),
                    'second_tool_light': self.second_tool_spin.value(),
                    'tools_picked_sensor': self.tools_picked_spin.value(),
                    'tools_collected_sensor': self.tools_collected_spin.value(),
                    'alarm_device': self.alarm_device_spin.value()
                })
        else:
            base_seq.update({
                'type': 'production_line',
                'steps': self.steps_text.toPlainText(),
                'return_to_initial': self.return_initial_check.isChecked()
            })
        
        return base_seq


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relay Sequence Controller")
        self.setGeometry(100, 100, 1000, 700)
        
        # Relay connection
        self.relay = None
        self.sequences = []
        self.active_sequences = {}
        self.di_history = {i: False for i in range(1, 9)}
        self.do_history = {i: False for i in range(1, 9)}
        self.multi_step_states = {}
        self.sequence_initialized = {}
        self.step_timers = {}
        self.wait_timers = {}  # Track wait/delay timers
        self.blink_timers = {}  # Track blink states
        self.blink_states = {}  # Track current blink state (ON/OFF)
        self.edge_detected = {}  # Track edge detection for one-shot triggers
        
        self.init_ui()
        self.connect_relay()
        
        # Load configuration
        self.load_configuration()
        
        # Timer for polling DI status
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(250)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel
        left_layout = QVBoxLayout()
        
        # Connection status
        self.status_label = QLabel("Connecting to relay...")
        left_layout.addWidget(self.status_label)
        
        # DI Status Tree
        di_group = QGroupBox("Digital Input Status")
        di_layout = QVBoxLayout()
        self.di_tree = QTreeWidget()
        self.di_tree.setHeaderLabels(["Channel", "Status", "History"])
        self.di_tree.setMaximumHeight(200)
        self.di_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.di_tree.customContextMenuRequested.connect(self.show_di_context_menu)
        for i in range(1, 9):
            item = QTreeWidgetItem([f"DI {i}", "OFF", "Never ON"])
            self.di_tree.addTopLevelItem(item)
        di_layout.addWidget(self.di_tree)
        
        di_btn_layout = QHBoxLayout()
        reset_di_history_btn = QPushButton("Reset DI History")
        reset_di_history_btn.clicked.connect(self.reset_di_history)
        di_btn_layout.addWidget(reset_di_history_btn)
        
        check_di_btn = QPushButton("Check DI States")
        check_di_btn.clicked.connect(self.log_all_di_states)
        di_btn_layout.addWidget(check_di_btn)
        
        di_layout.addLayout(di_btn_layout)
        
        di_group.setLayout(di_layout)
        left_layout.addWidget(di_group)
        
        # DO Status Tree
        do_group = QGroupBox("Digital Output Status")
        do_layout = QVBoxLayout()
        self.do_tree = QTreeWidget()
        self.do_tree.setHeaderLabels(["Channel", "Status", "History"])
        self.do_tree.setMaximumHeight(200)
        self.do_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.do_tree.customContextMenuRequested.connect(self.show_do_context_menu)
        for i in range(1, 9):
            item = QTreeWidgetItem([f"DO {i}", "OFF", "Never ON"])
            self.do_tree.addTopLevelItem(item)
        do_layout.addWidget(self.do_tree)
        
        do_btn_layout = QHBoxLayout()
        reset_do_history_btn = QPushButton("Reset DO History")
        reset_do_history_btn.clicked.connect(self.reset_do_history)
        do_btn_layout.addWidget(reset_do_history_btn)
        
        check_do_btn = QPushButton("Check DO States")
        check_do_btn.clicked.connect(self.log_all_do_states)
        do_btn_layout.addWidget(check_do_btn)
        
        reset_all_do_btn = QPushButton("🔄 Reset All DO OFF")
        reset_all_do_btn.setStyleSheet("background-color: #FF6B6B; color: white; font-weight: bold;")
        reset_all_do_btn.clicked.connect(self.reset_all_do_with_password)
        do_btn_layout.addWidget(reset_all_do_btn)
        
        do_layout.addLayout(do_btn_layout)
        
        do_group.setLayout(do_layout)
        left_layout.addWidget(do_group)
        
        main_layout.addLayout(left_layout)
        
        # Right panel
        right_layout = QVBoxLayout()
        
        # Sequence Tree
        seq_group = QGroupBox("Active Sequences")
        seq_layout = QVBoxLayout()
        self.seq_tree = QTreeWidget()
        self.seq_tree.setHeaderLabels(["Type", "Configuration", "Enabled"])
        self.seq_tree.itemDoubleClicked.connect(self.edit_sequence)
        seq_layout.addWidget(self.seq_tree)
        
        # Sequence buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Sequence")
        add_btn.clicked.connect(self.add_sequence)
        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(lambda: self.edit_sequence(self.seq_tree.currentItem(), 0))
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_sequence)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(remove_btn)
        
        # Save Configuration Button
        save_btn = QPushButton("💾 Save Config")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        save_btn.clicked.connect(self.save_configuration)
        btn_layout.addWidget(save_btn)
        
        btn_layout.addStretch()
        seq_layout.addLayout(btn_layout)
        
        seq_group.setLayout(seq_layout)
        right_layout.addWidget(seq_group)
        
        # Sequence Status Display
        status_group = QGroupBox("Sequence Status")
        status_layout = QVBoxLayout()
        
        self.current_seq_label = QLabel("Current Sequence: None")
        self.current_seq_label.setStyleSheet("font-weight: bold; color: blue;")
        status_layout.addWidget(self.current_seq_label)
        
        self.next_step_label = QLabel("Next Step: None")
        self.next_step_label.setStyleSheet("color: #FFA500;")  # Orange/Yellow
        status_layout.addWidget(self.next_step_label)
        
        self.completed_label = QLabel("Completed Sequences: None")
        self.completed_label.setStyleSheet("color: green;")
        status_layout.addWidget(self.completed_label)
        
        self.next_seq_label = QLabel("Next Sequence: None")
        self.next_seq_label.setStyleSheet("color: yellow; background-color: #333;")
        status_layout.addWidget(self.next_seq_label)
        
        status_group.setLayout(status_layout)
        right_layout.addWidget(status_group)
        
        # Event Log
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout()
        self.log_list = QListWidget()
        log_layout.addWidget(self.log_list)
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_list.clear)
        log_layout.addWidget(clear_log_btn)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)
        
        main_layout.addLayout(right_layout)

    def add_sequence_to_ui(self, seq, enabled=True):
        """Add a sequence to the UI from the configuration."""
        config_parts = []
        
        if seq['type'] == 'station':
            operation_type = seq.get('operation_type', 'Part Detection & Process')
            part_sensor = seq.get('part_sensor', 1)
            process_device = seq.get('process_device', 1)
            feedback_sensor = seq.get('feedback_sensor', 2)
            skip_sensor = seq.get('skip_sensor', 3)
            timeout = seq.get('timeout', 10)
            duration = seq.get('duration', 5)
            blink_text = " [BLINK]" if seq.get('blink_mode', False) else ""
            
            config_parts.append(f"{operation_type}: Part_DI{part_sensor} -> Process_DO{process_device}")
            config_parts.append(f"Feedback_DI{feedback_sensor} | Skip_DI{skip_sensor}")
            config_parts.append(f"Timeout: {timeout}s, Duration: {duration}s{blink_text}")
        else:
            steps = seq.get('steps', '').replace('\n', '; ')
            config_parts.append(f"Production Line: {steps[:100]}{'...' if len(steps) > 100 else ''}")
            if seq.get('return_to_initial', False):
                config_parts.append("Return to initial")
        
        if seq.get('initial_states'):
            init_str = ', '.join([f"DO{k}={'ON' if v else 'OFF'}" for k, v in seq['initial_states'].items()])
            config_parts.append(f"Init: {init_str}")
        if seq.get('end_states'):
            end_str = ', '.join([f"DO{k}={'ON' if v else 'OFF'}" for k, v in seq['end_states'].items()])
            config_parts.append(f"End: {end_str}")
        
        config = ' | '.join(config_parts)
        
        item = QTreeWidgetItem([seq['type'].capitalize(), config, ""])
        self.seq_tree.addTopLevelItem(item)
        
        checkbox = QCheckBox()
        checkbox.setChecked(enabled)
        idx = self.seq_tree.indexOfTopLevelItem(item)
        checkbox.stateChanged.connect(lambda state, i=idx: self.on_sequence_toggled(i, state))
        self.seq_tree.setItemWidget(item, 2, checkbox)

    def load_configuration(self):
        """Load configuration from a file."""
        config = load_config()
        if config:
            self.sequences = config.get('sequences', [])
            enabled_states = config.get('enabled_states', [True] * len(self.sequences))
            
            for seq, enabled in zip(self.sequences, enabled_states):
                # Add sequences to the UI with their saved enabled state
                self.add_sequence_to_ui(seq, enabled=enabled)
            
            self.log_event(f"Loaded {len(self.sequences)} sequences from configuration")
    
    def show_di_context_menu(self, position):
        """Show context menu for DI tree items."""
        item = self.di_tree.itemAt(position)
        if item:
            # Extract channel number from item text (e.g., "DI 1" -> 1)
            channel_text = item.text(0)
            try:
                channel = int(channel_text.split()[-1])
            except (ValueError, IndexError):
                return
            
            menu = QMenu(self)
            check_action = menu.addAction(f"Check DI{channel} State")
            check_action.triggered.connect(lambda: self.check_and_log_di(channel))
            
            menu.exec(self.di_tree.mapToGlobal(position))
    
    def show_do_context_menu(self, position):
        """Show context menu for DO tree items."""
        item = self.do_tree.itemAt(position)
        if item:
            # Extract channel number from item text (e.g., "DO 1" -> 1)
            channel_text = item.text(0)
            try:
                channel = int(channel_text.split()[-1])
            except (ValueError, IndexError):
                return
            
            menu = QMenu(self)
            check_action = menu.addAction(f"Check DO{channel} State")
            check_action.triggered.connect(lambda: self.check_and_log_do(channel))
            
            toggle_action = menu.addAction(f"Toggle DO{channel}")
            toggle_action.triggered.connect(lambda: self.toggle_do_channel(channel))
            
            menu.exec(self.do_tree.mapToGlobal(position))
    
    def check_and_log_di(self, channel):
        """Check a specific DI channel and log its state."""
        state = self.check_di_channel(channel)
        state_text = "ON" if state else "OFF"
        self.log_event(f"DI{channel} is currently {state_text}")
    
    def check_and_log_do(self, channel):
        """Check a specific DO channel and log its state."""
        state = self.check_do_channel(channel)
        state_text = "ON" if state else "OFF"
        self.log_event(f"DO{channel} is currently {state_text}")
    
    def toggle_do_channel(self, channel):
        """Toggle a specific DO channel for testing."""
        if not self.relay:
            self.log_event("Cannot toggle DO - relay not connected")
            return
        
        try:
            current_state = self.relay.status(channel)
            if current_state:
                self.relay.off(channel)
                self.log_event(f"Manually turned DO{channel} OFF")
            else:
                self.relay.on(channel)
                self.log_event(f"Manually turned DO{channel} ON")
        except Exception as e:
            self.log_event(f"Error toggling DO{channel}: {e}")

    def log_all_di_states(self):
        """Log the current state of all DI channels."""
        di_states = self.get_all_di_states()
        if di_states:
            states_str = ", ".join([f"DI{ch}={'ON' if state else 'OFF'}" for ch, state in di_states.items()])
            self.log_event(f"DI States: {states_str}")
        else:
            self.log_event("Could not read DI states - relay not connected")
    
    def log_all_do_states(self):
        """Log the current state of all DO channels."""
        do_states = self.get_all_do_states()
        if do_states:
            states_str = ", ".join([f"DO{ch}={'ON' if state else 'OFF'}" for ch, state in do_states.items()])
            self.log_event(f"DO States: {states_str}")
        else:
            self.log_event("Could not read DO states - relay not connected")

    def reset_di_history(self):
        """Reset all DI history."""
        self.di_history = {i: False for i in range(1, 9)}
        for i in range(8):
            item = self.di_tree.topLevelItem(i)
            item.setText(2, "Never ON")
            item.setForeground(2, Qt.gray)
        self.log_event("DI history reset")
    
    def reset_do_history(self):
        """Reset all DO history."""
        self.do_history = {i: False for i in range(1, 9)}
        for i in range(8):
            item = self.do_tree.topLevelItem(i)
            item.setText(2, "Never ON")
            item.setForeground(2, Qt.gray)
        self.log_event("DO history reset")
    
    def reset_edge_detection(self):
        """Reset all edge detection states."""
        self.edge_detected.clear()
        self.log_event("Edge detection states reset - all DI(EDGE) triggers will work again")
    
    def reset_all_do_with_password(self):
        """Reset all DO channels to OFF with password protection."""
        # Create a custom dialog with numeric keypad
        dialog = QDialog(self)
        dialog.setWindowTitle('Password Required')
        dialog.setModal(True)
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instruction_label = QLabel('Enter password to reset all DO channels to OFF:')
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
            msg.setInformativeText("Access denied. Cannot reset DO channels.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            self.log_event("Reset All DO - Incorrect password entered")
            return
        
        # Password is correct, show confirmation dialog
        reply = QMessageBox.question(
            self,
            'Confirm Reset All DO',
            'Are you sure you want to turn OFF all DO channels?\n\nThis will:\n• Turn OFF all 8 DO channels (DO1-DO8)\n• Stop all active sequences\n• Clear all timers and blink states\n\nThis action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.reset_all_do_channels()
        else:
            self.log_event("Reset All DO - Operation cancelled by user")
    
    def reset_all_do_channels(self):
        """Reset all DO channels to OFF and clear all sequences."""
        if not self.relay:
            self.log_event("Cannot reset DO channels - relay not connected")
            return
        
        try:
            # Stop all timers and clear states
            self.step_timers.clear()
            self.wait_timers.clear()
            self.blink_timers.clear()
            self.blink_states.clear()
            self.active_sequences.clear()
            
            # Reset all sequence states
            for i in range(len(self.sequences)):
                # Reset initialization flags
                if i in self.sequence_initialized:
                    del self.sequence_initialized[i]
                
                # Reset multi-step states
                seq_key = f"production_{i}"
                if seq_key in self.multi_step_states:
                    del self.multi_step_states[seq_key]
                
                old_seq_key = f"multi_{i}"
                if old_seq_key in self.multi_step_states:
                    del self.multi_step_states[old_seq_key]
            
            # Turn OFF all DO channels
            self.relay.all_off()
            
            # Reset DO history
            self.do_history = {i: False for i in range(1, 9)}
            for i in range(8):
                item = self.do_tree.topLevelItem(i)
                item.setText(2, "Never ON")
                item.setForeground(2, Qt.gray)
            
            # Log the action
            self.log_event("🔄 EMERGENCY RESET: All DO channels turned OFF, all sequences stopped")
            
            # Show success message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Reset Complete")
            msg.setText("All DO channels have been turned OFF successfully!")
            msg.setInformativeText("All sequences have been stopped and timers cleared.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            
        except Exception as e:
            # Show error message
            error_msg = QMessageBox()
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setWindowTitle("Reset Failed")
            error_msg.setText("Failed to reset DO channels!")
            error_msg.setInformativeText(f"Error: {str(e)}")
            error_msg.setStandardButtons(QMessageBox.Ok)
            error_msg.exec()
            self.log_event(f"ERROR: Failed to reset DO channels - {str(e)}")

    def edit_sequence(self, item, column):
        """Edit the selected sequence."""
        if not item:
            return
        
        index = self.seq_tree.indexOfTopLevelItem(item)
        if index < 0 or index >= len(self.sequences):
            return
        
        # Get the current sequence
        current_seq = self.sequences[index]
        
        # Get current enabled state
        checkbox = self.seq_tree.itemWidget(item, 2)
        was_enabled = checkbox.isChecked() if checkbox else True
        
        # Open edit dialog with current sequence data
        dialog = SequenceDialog(self, edit_sequence=current_seq)
        if dialog.exec():
            # Update the sequence
            updated_seq = dialog.get_sequence()
            self.sequences[index] = updated_seq
            
            # Reset initialization flag for this sequence
            if index in self.sequence_initialized:
                del self.sequence_initialized[index]
            
            # Reset multi-step state
            seq_key = f"multi_{index}"
            if seq_key in self.multi_step_states:
                del self.multi_step_states[seq_key]
            
            # Remove old item and add updated one
            self.seq_tree.takeTopLevelItem(index)
            
            # Re-insert at same position
            config_parts = []
            
            if updated_seq['type'] == 'station':
                operation_type = updated_seq.get('operation_type', 'Part Detection & Process')
                part_sensor = updated_seq.get('part_sensor', 1)
                process_device = updated_seq.get('process_device', 1)
                feedback_sensor = updated_seq.get('feedback_sensor', 2)
                skip_sensor = updated_seq.get('skip_sensor', 3)
                timeout = updated_seq.get('timeout', 10)
                duration = updated_seq.get('duration', 5)
                blink_text = " [BLINK]" if updated_seq.get('blink_mode', False) else ""
                
                config_parts.append(f"{operation_type}: Part_DI{part_sensor} -> Process_DO{process_device}")
                config_parts.append(f"Feedback_DI{feedback_sensor} | Skip_DI{skip_sensor}")
                config_parts.append(f"Timeout: {timeout}s, Duration: {duration}s{blink_text}")
            else:
                steps = updated_seq.get('steps', '').replace('\n', '; ')
                config_parts.append(f"Production Line: {steps[:100]}{'...' if len(steps) > 100 else ''}")
                if updated_seq.get('return_to_initial', False):
                    config_parts.append("Return to initial")
            
            if updated_seq.get('initial_states'):
                init_str = ', '.join([f"DO{k}={'ON' if v else 'OFF'}" for k, v in updated_seq['initial_states'].items()])
                config_parts.append(f"Init: {init_str}")
            if updated_seq.get('end_states'):
                end_str = ', '.join([f"DO{k}={'ON' if v else 'OFF'}" for k, v in updated_seq['end_states'].items()])
                config_parts.append(f"End: {end_str}")
            
            config = ' | '.join(config_parts)
            
            new_item = QTreeWidgetItem([updated_seq['type'].capitalize(), config, ""])
            self.seq_tree.insertTopLevelItem(index, new_item)
            
            checkbox = QCheckBox()
            checkbox.setChecked(was_enabled)
            checkbox.stateChanged.connect(lambda state, i=index: self.on_sequence_toggled(i, state))
            self.seq_tree.setItemWidget(new_item, 2, checkbox)
            
            self.log_event(f"Updated sequence #{index}")
    
    def on_sequence_toggled(self, seq_id, state):
        """Handle sequence enable/disable."""
        if state == Qt.Unchecked:
            # Sequence disabled, apply end state
            if seq_id < len(self.sequences):
                seq = self.sequences[seq_id]
                if not seq.get('return_to_initial', False):
                    self.apply_end_state(seq, seq_id)
                # Reset initialization flag
                if seq_id in self.sequence_initialized:
                    del self.sequence_initialized[seq_id]
                # Reset multi-step state
                seq_key = f"production_{seq_id}"
                if seq_key in self.multi_step_states:
                    del self.multi_step_states[seq_key]
                # Also check for old format
                old_seq_key = f"multi_{seq_id}"
                if old_seq_key in self.multi_step_states:
                    del self.multi_step_states[old_seq_key]
                # Clear wait timers
                wait_key = f"wait_{seq_id}"
                if wait_key in self.wait_timers:
                    del self.wait_timers[wait_key]
                # Clear edge detection states
                edge_keys_to_remove = [key for key in self.edge_detected.keys() if f"_{seq_id}_" in key or key.startswith('edge_')]
                for key in edge_keys_to_remove:
                    if key in self.edge_detected:
                        del self.edge_detected[key]
                # Clear blink timers
                blink_keys_to_remove = [key for key in self.blink_timers.keys() if f"_{seq_id}_" in key]
                for key in blink_keys_to_remove:
                    if key in self.blink_timers:
                        del self.blink_timers[key]
                    if key in self.blink_states:
                        del self.blink_states[key]
                self.log_event(f"Sequence {seq_id} disabled")
    
    def remove_sequence(self):
        """Remove selected sequence."""
        current = self.seq_tree.currentItem()
        if current:
            index = self.seq_tree.indexOfTopLevelItem(current)
            
            # Apply end state before removing
            if index < len(self.sequences):
                seq = self.sequences[index]
                if not seq.get('return_to_initial', False):
                    self.apply_end_state(seq, index)
            
            self.seq_tree.takeTopLevelItem(index)
            self.sequences.pop(index)
            
            # Clean up state tracking
            if index in self.sequence_initialized:
                del self.sequence_initialized[index]
            
            self.log_event(f"Removed sequence #{index}")

    def add_sequence(self):
        """Open dialog to add a new sequence."""
        dialog = SequenceDialog(self)
        if dialog.exec():
            seq = dialog.get_sequence()
            self.sequences.append(seq)
            self.add_sequence_to_ui(seq, enabled=True)
            self.log_event(f"Added new sequence")   

    def connect_relay(self):
        """Connect to the relay board."""
        try:
            self.relay = Relay(host='192.168.1.200')
            self.relay.connect()
            self.status_label.setText("Connected to relay at 192.168.1.200")
            self.status_label.setStyleSheet("color: green")
            self.log_event("Connected to relay")
        except Exception as e:
            self.status_label.setText(f"Connection failed: {e}")
            self.status_label.setStyleSheet("color: red")
            self.log_event(f"Connection failed: {e}")    

    def closeEvent(self, event):
        """Clean up on close."""
        self.timer.stop()
        if self.relay:
            # Stop all blink timers
            self.blink_timers.clear()
            self.blink_states.clear()
            
            # Apply end states for all enabled sequences
            for i in range(self.seq_tree.topLevelItemCount()):
                item = self.seq_tree.topLevelItem(i)
                checkbox = self.seq_tree.itemWidget(item, 2)
                if checkbox and checkbox.isChecked() and i < len(self.sequences):
                    seq = self.sequences[i]
                    if not seq.get('return_to_initial', False):
                        self.apply_end_state(seq, i)
            
            self.relay.all_off()
            self.relay.disconnect()
        self.log_event("Application closed")
        event.accept()

    def log_event(self, message):
        """Add event to log with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_list.insertItem(0, f"[{timestamp}] {message}")
        if self.log_list.count() > 100:
            self.log_list.takeItem(self.log_list.count() - 1)
    
    def update_status(self):
        """Poll DI/DO status and process sequences."""
        if not self.relay:
            return
        
        try:
            # Update DI status
            di_mask = self.relay.check_DI()
            for i in range(8):
                item = self.di_tree.topLevelItem(i)
                status = "ON" if (di_mask & (1 << i)) else "OFF"
                item.setText(1, status)
                item.setForeground(1, Qt.green if status == "ON" else Qt.gray)
                
                # Update history
                if status == "ON" and not self.di_history[i + 1]:
                    self.di_history[i + 1] = True
                    item.setText(2, "Was ON")
                    item.setForeground(2, Qt.yellow)
                    self.log_event(f"DI{i + 1} triggered for first time")
            
            # Update DO status
            for i in range(8):
                item = self.do_tree.topLevelItem(i)
                try:
                    status = "ON" if self.relay.status(i + 1) else "OFF"
                    item.setText(1, status)
                    item.setForeground(1, Qt.green if status == "ON" else Qt.gray)
                    
                    # Update history
                    if status == "ON" and not self.do_history[i + 1]:
                        self.do_history[i + 1] = True
                        item.setText(2, "Was ON")
                        item.setForeground(2, Qt.yellow)
                        self.log_event(f"DO{i + 1} activated for first time")
                except:
                    pass
            
            # Check step timers for timed DO off
            current_time = time.time()
            timers_to_remove = []
            for timer_key, (off_time, do_ch, seq_id) in self.step_timers.items():
                if current_time >= off_time:
                    self.relay.off(do_ch)
                    self.log_event(f"Sequence {seq_id}: DO{do_ch} turned OFF (timer)")
                    timers_to_remove.append(timer_key)
            
            for key in timers_to_remove:
                del self.step_timers[key]
            
            # Check wait timers
            waits_to_remove = []
            for wait_key, wait_data in self.wait_timers.items():
                if len(wait_data) == 4:  # New format with subsequent actions
                    wait_end_time, seq_id, step_idx, subsequent_actions = wait_data
                elif len(wait_data) == 2:  # Old format compatibility
                    wait_end_time, seq_id = wait_data
                    step_idx = None
                    subsequent_actions = None
                else:
                    continue
                    
                if current_time >= wait_end_time:
                    # Execute subsequent actions if any
                    if subsequent_actions:
                        self.execute_actions(subsequent_actions, seq_id, step_idx if step_idx is not None else 0, f"Wait completion -> {subsequent_actions}")
                        self.log_event(f"Sequence {seq_id}: Wait completed, executed: {subsequent_actions}")
                    else:
                        self.log_event(f"Sequence {seq_id}: Wait completed")
                    
                    waits_to_remove.append(wait_key)
                    # Advance to next step
                    multi_key = f"production_{seq_id}"
                    if multi_key in self.multi_step_states:
                        self.multi_step_states[multi_key]['waiting'] = False
            
            for key in waits_to_remove:
                del self.wait_timers[key]
            
            # Process blink timers
            blinks_to_toggle = []
            for blink_key, (next_toggle_time, do_ch, seq_id, end_time) in self.blink_timers.items():
                if current_time >= next_toggle_time:
                    # Toggle the relay
                    current_state = self.blink_states.get(blink_key, False)
                    new_state = not current_state
                    self.blink_states[blink_key] = new_state
                    
                    if new_state:
                        self.relay.on(do_ch)
                    else:
                        self.relay.off(do_ch)
                    
                    # Schedule next toggle in 1 second
                    next_time = current_time + 1.0
                    self.blink_timers[blink_key] = (next_time, do_ch, seq_id, end_time)
                    
                    # Check if blink period has ended
                    if current_time >= end_time:
                        blinks_to_toggle.append(blink_key)
                        self.relay.off(do_ch)
                        self.log_event(f"Sequence {seq_id}: DO{do_ch} blink completed")
            
            for key in blinks_to_toggle:
                if key in self.blink_timers:
                    del self.blink_timers[key]
                if key in self.blink_states:
                    del self.blink_states[key]
            
            # Process sequences
            self.process_sequences(di_mask)
            
            # Update sequence status display
            self.update_sequence_status_display()
            
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
            self.log_event(f"Error: {e}")

    def process_sequences(self, di_mask):
        """Process all enabled sequences based on current DI state."""
        for i in range(self.seq_tree.topLevelItemCount()):
            item = self.seq_tree.topLevelItem(i)
            checkbox = self.seq_tree.itemWidget(item, 2)
            
            if not checkbox or not checkbox.isChecked():
                continue
            
            seq = self.sequences[i]
            
            # Apply initial state if first time enabled
            self.apply_initial_state(seq, i)
            
            if seq['type'] == 'station':
                self.process_station_operation(seq, di_mask, i)
            else:
                self.process_production_line(seq, di_mask, i)
    
    def process_station_operation(self, seq, di_mask, seq_id):
        """Process station operation with sensor feedback and error handling."""
        operation_type = seq.get('operation_type', 'Part Detection & Process')
        
        # Handle Tool Picking Sequence
        if operation_type == "Tool Picking Sequence":
            return self.process_tool_picking_sequence(seq, di_mask, seq_id)
        
        # Handle other station operations
        part_sensor = seq.get('part_sensor', 1)
        process_device = seq.get('process_device', 1)
        feedback_sensor = seq.get('feedback_sensor', 2)
        skip_sensor = seq.get('skip_sensor', 3)
        timeout = seq.get('timeout', 10)
        duration = seq.get('duration', 5)
        
        # Check if part is detected
        part_detected = bool(di_mask & (1 << (part_sensor - 1)))
        feedback_detected = bool(di_mask & (1 << (feedback_sensor - 1)))
        skip_detected = bool(di_mask & (1 << (skip_sensor - 1)))
        
        station_key = f"station_{seq_id}_{process_device}"
        blink_key = f"station_blink_{seq_id}_{process_device}"
        
        # State tracking for this station
        if station_key not in self.active_sequences:
            self.active_sequences[station_key] = {
                'state': 'waiting_for_part',
                'start_time': None,
                'process_start_time': None
            }
        
        station_state = self.active_sequences[station_key]
        current_time = time.time()
        
        if station_state['state'] == 'waiting_for_part':
            if part_detected:
                if skip_detected:
                    # Skip process due to error condition
                    self.log_event(f"Station {seq_id}: Part detected but skip sensor active - skipping process")
                    station_state['state'] = 'waiting_for_part'  # Reset to wait for next part
                else:
                    # Start process
                    station_state['state'] = 'processing'
                    station_state['start_time'] = current_time
                    station_state['process_start_time'] = current_time
                    
                    if seq.get('blink_mode', False):
                        # Start blink mode
                        if duration > 0:
                            end_time = current_time + duration
                            next_toggle = current_time + 1.0
                            self.blink_timers[blink_key] = (next_toggle, process_device, seq_id, end_time)
                            self.blink_states[blink_key] = True
                            self.relay.on(process_device)
                            self.log_event(f"Station {seq_id}: Started processing (blinking) for {duration}s")
                        else:
                            # Process until feedback
                            self.relay.on(process_device)
                            self.log_event(f"Station {seq_id}: Started processing (blink until feedback)")
                    else:
                        # Normal processing
                        self.relay.on(process_device)
                        if duration > 0:
                            self.log_event(f"Station {seq_id}: Started processing for {duration}s")
                        else:
                            self.log_event(f"Station {seq_id}: Started processing until feedback")
        
        elif station_state['state'] == 'processing':
            # Check for completion conditions
            process_complete = False
            
            if duration > 0 and (current_time - station_state['process_start_time']) >= duration:
                # Duration-based completion
                process_complete = True
                self.log_event(f"Station {seq_id}: Process completed (duration timeout)")
            elif duration == 0 and feedback_detected:
                # Feedback-based completion
                process_complete = True
                self.log_event(f"Station {seq_id}: Process completed (feedback received)")
            elif (current_time - station_state['start_time']) >= timeout:
                # Timeout - process failed
                self.relay.off(process_device)
                self.log_event(f"Station {seq_id}: Process TIMEOUT - stopping operation")
                station_state['state'] = 'waiting_for_part'
                # Clear any blink timers
                if blink_key in self.blink_timers:
                    del self.blink_timers[blink_key]
                if blink_key in self.blink_states:
                    del self.blink_states[blink_key]
                return
            
            if process_complete:
                # Stop processing
                if not seq.get('blink_mode', False) or duration > 0:
                    self.relay.off(process_device)
                
                # Clear blink timers if they exist
                if blink_key in self.blink_timers:
                    del self.blink_timers[blink_key]
                if blink_key in self.blink_states:
                    del self.blink_states[blink_key]
                
                station_state['state'] = 'waiting_for_clear'
                self.log_event(f"Station {seq_id}: Waiting for part to clear")
        
        elif station_state['state'] == 'waiting_for_clear':
            if not part_detected:
                # Part has cleared, ready for next cycle
                station_state['state'] = 'waiting_for_part'
                self.log_event(f"Station {seq_id}: Part cleared - ready for next part")
    
    def process_tool_picking_sequence(self, seq, di_mask, seq_id):
        """Process tool picking sequence with specific workflow."""
        # Get configuration
        part_sensor = seq.get('part_sensor', 4)  # DI4
        process_device = seq.get('process_device', 4)  # DO4
        first_tool_light = seq.get('first_tool_light', 2)  # DO2
        second_tool_light = seq.get('second_tool_light', 3)  # DO3
        tools_picked_sensor = seq.get('tools_picked_sensor', 3)  # DI3
        tools_collected_sensor = seq.get('tools_collected_sensor', 2)  # DI2
        alarm_device = seq.get('alarm_device', 5)  # DO5
        timeout = seq.get('timeout', 30)
        
        # Get sensor states
        part_detected = bool(di_mask & (1 << (part_sensor - 1)))
        tools_picked = bool(di_mask & (1 << (tools_picked_sensor - 1)))
        tools_collected = bool(di_mask & (1 << (tools_collected_sensor - 1)))
        
        tool_key = f"tool_picking_{seq_id}"
        current_time = time.time()
        
        # Initialize state if not exists
        if tool_key not in self.active_sequences:
            self.active_sequences[tool_key] = {
                'state': 'waiting_for_part',
                'start_time': None,
                'step_start_time': None
            }
        
        tool_state = self.active_sequences[tool_key]
        
        if tool_state['state'] == 'waiting_for_part':
            if part_detected:
                # Step 1: Part detected, start process
                self.relay.on(process_device)  # DO4 ON
                self.relay.on(first_tool_light)  # DO2 ON (1st tool light)
                tool_state['state'] = 'waiting_for_first_tool'
                tool_state['start_time'] = current_time
                tool_state['step_start_time'] = current_time
                self.log_event(f"Tool Picking {seq_id}: Part detected - Process ON, 1st tool light ON")
        
        elif tool_state['state'] == 'waiting_for_first_tool':
            if tools_picked:
                # Step 2: Tools picked, show second tool
                self.relay.off(first_tool_light)  # DO2 OFF
                self.relay.on(second_tool_light)  # DO3 ON (2nd tool light)
                tool_state['state'] = 'waiting_for_second_tool'
                tool_state['step_start_time'] = current_time
                self.log_event(f"Tool Picking {seq_id}: 1st tools picked - 2nd tool light ON")
            elif (current_time - tool_state['step_start_time']) >= timeout:
                # Timeout - activate alarm
                self.relay.on(alarm_device)  # DO5 ON (alarm)
                tool_state['state'] = 'alarm_first_tool'
                self.log_event(f"Tool Picking {seq_id}: TIMEOUT waiting for 1st tools - ALARM ON")
        
        elif tool_state['state'] == 'alarm_first_tool':
            if tools_picked:
                # Clear alarm and continue
                self.relay.off(alarm_device)  # DO5 OFF
                self.relay.off(first_tool_light)  # DO2 OFF
                self.relay.on(second_tool_light)  # DO3 ON
                tool_state['state'] = 'waiting_for_second_tool'
                tool_state['step_start_time'] = current_time
                self.log_event(f"Tool Picking {seq_id}: 1st tools picked (after alarm) - continuing")
        
        elif tool_state['state'] == 'waiting_for_second_tool':
            if tools_collected:
                # Step 3: All tools collected, complete sequence
                self.relay.off(second_tool_light)  # DO3 OFF
                self.relay.off(process_device)  # DO4 OFF
                tool_state['state'] = 'waiting_for_part_clear'
                self.log_event(f"Tool Picking {seq_id}: All tools collected - sequence complete")
            elif (current_time - tool_state['step_start_time']) >= timeout:
                # Timeout - activate alarm
                self.relay.on(alarm_device)  # DO5 ON (alarm)
                tool_state['state'] = 'alarm_second_tool'
                self.log_event(f"Tool Picking {seq_id}: TIMEOUT waiting for 2nd tools - ALARM ON")
        
        elif tool_state['state'] == 'alarm_second_tool':
            if tools_collected:
                # Clear alarm and complete
                self.relay.off(alarm_device)  # DO5 OFF
                self.relay.off(second_tool_light)  # DO3 OFF
                self.relay.off(process_device)  # DO4 OFF
                tool_state['state'] = 'waiting_for_part_clear'
                self.log_event(f"Tool Picking {seq_id}: All tools collected (after alarm) - complete")
        
        elif tool_state['state'] == 'waiting_for_part_clear':
            if not part_detected:
                # Part cleared, ready for next cycle
                tool_state['state'] = 'waiting_for_part'
                self.log_event(f"Tool Picking {seq_id}: Part cleared - ready for next cycle")

    def process_production_line(self, seq, di_mask, seq_id):
        """Process simple logic sequence."""
        di1_on = bool(di_mask & (1 << (seq['di1'] - 1)))
        
        # Evaluate logic
        trigger = False
        if seq['logic'] == "Single DI":
            trigger = di1_on
        elif seq['logic'] == "AND Gate":
            di2_on = bool(di_mask & (1 << (seq['di2'] - 1)))
            trigger = di1_on and di2_on
        elif seq['logic'] == "OR Gate":
            di2_on = bool(di_mask & (1 << (seq['di2'] - 1)))
            trigger = di1_on or di2_on
        
        # Control DO
        do_ch = seq['do']
        seq_key = f"simple_{seq_id}_{do_ch}"
        blink_key = f"blink_{seq_id}_{do_ch}"
        
        if trigger and seq_key not in self.active_sequences and blink_key not in self.blink_timers:
            if seq.get('blink_mode', False):
                # Start blink mode
                if seq['duration'] > 0:
                    end_time = time.time() + seq['duration']
                    next_toggle = time.time() + 1.0  # First toggle in 1 second
                    self.blink_timers[blink_key] = (next_toggle, do_ch, seq_id, end_time)
                    self.blink_states[blink_key] = True
                    self.relay.on(do_ch)
                    self.log_event(f"Sequence {seq_id}: DO{do_ch} started blinking for {seq['duration']}s")
                else:
                    # Infinite blink until trigger goes off
                    self.relay.on(do_ch)
                    self.log_event(f"Sequence {seq_id}: DO{do_ch} turned ON (blink mode)")
            else:
                # Normal mode
                self.relay.on(do_ch)
                self.log_event(f"Sequence {seq_id}: DO{do_ch} turned ON")
                if seq['duration'] > 0:
                    # Schedule turn off
                    self.active_sequences[seq_key] = time.time() + seq['duration']
        
        # Handle trigger off for infinite blink mode
        if not trigger and seq.get('blink_mode', False) and seq['duration'] == 0:
            if blink_key in self.blink_timers:
                del self.blink_timers[blink_key]
            if blink_key in self.blink_states:
                del self.blink_states[blink_key]
            self.relay.off(do_ch)
            self.log_event(f"Sequence {seq_id}: DO{do_ch} blink stopped (trigger off)")
        
        # Check for timed turn-off (normal mode)
        if seq_key in self.active_sequences:
            if time.time() >= self.active_sequences[seq_key]:
                self.relay.off(do_ch)
                self.log_event(f"Sequence {seq_id}: DO{do_ch} turned OFF (timer)")
                del self.active_sequences[seq_key]
    
    def process_production_line(self, seq, di_mask, seq_id):
        """Process production line sequence with enhanced sensor-based control."""
        steps = seq.get('steps', '').strip().split('\n')
        seq_key = f"production_{seq_id}"
        
        if seq_key not in self.multi_step_states:
            self.multi_step_states[seq_key] = {
                'current_step': 0, 
                'completed': set(),
                'waiting': False
            }
        
        state = self.multi_step_states[seq_key]
        
        # If waiting, don't process new steps
        if state.get('waiting', False):
            return
        
        for step_idx, step in enumerate(steps):
            if step_idx < state['current_step']:
                continue
                
            step = step.strip()
            if not step:
                continue
            
            # Check if this is a WAIT step
            if step.upper().startswith('WAIT:'):
                if step_idx not in state['completed']:
                    # Check if it has subsequent actions: WAIT:10s->Actions
                    if '->' in step:
                        wait_part, subsequent_actions = step.split('->', 1)
                        duration_str = wait_part.split(':', 1)[1].strip()
                        if duration_str.endswith('s'):
                            try:
                                wait_duration = int(duration_str[:-1])
                                wait_key = f"wait_{seq_id}_{step_idx}"
                                self.wait_timers[wait_key] = (time.time() + wait_duration, seq_id, step_idx, subsequent_actions.strip())
                                state['waiting'] = True
                                state['completed'].add(step_idx)
                                state['current_step'] = step_idx + 1
                                self.log_event(f"Sequence {seq_id} Step {step_idx}: Waiting {wait_duration}s, then executing: {subsequent_actions.strip()}")
                                break
                            except ValueError:
                                pass
                    else:
                        # Simple wait without actions
                        duration_str = step.split(':', 1)[1].strip()
                        if duration_str.endswith('s'):
                            try:
                                wait_duration = int(duration_str[:-1])
                                wait_key = f"wait_{seq_id}_{step_idx}"
                                self.wait_timers[wait_key] = (time.time() + wait_duration, seq_id, step_idx, None)
                                state['waiting'] = True
                                state['completed'].add(step_idx)
                                state['current_step'] = step_idx + 1
                                self.log_event(f"Sequence {seq_id} Step {step_idx}: Waiting {wait_duration}s")
                                break
                            except ValueError:
                                pass
                continue
            
            # Check if step has condition
            if '->' not in step:
                continue
            
            condition, action = step.split('->', 1)
            condition = condition.strip()
            action = action.strip()
            
            # Parse condition
            trigger = self.evaluate_condition(condition, di_mask)
            
            if trigger and step_idx not in state['completed']:
                # Check if action is WAIT with subsequent actions
                if action.upper().startswith('WAIT:') and '->' in action:
                    # Format: WAIT:10s->DO2(OFF)|DO3(OFF)
                    wait_part, subsequent_actions = action.split('->', 1)
                    duration_str = wait_part.split(':', 1)[1].strip()
                    if duration_str.endswith('s'):
                        try:
                            wait_duration = int(duration_str[:-1])
                            wait_key = f"wait_{seq_id}_{step_idx}"
                            self.wait_timers[wait_key] = (time.time() + wait_duration, seq_id, step_idx, subsequent_actions.strip())
                            state['waiting'] = True
                            state['completed'].add(step_idx)
                            state['current_step'] = step_idx + 1
                            self.log_event(f"Sequence {seq_id} Step {step_idx}: Waiting {wait_duration}s, then executing: {subsequent_actions.strip()}")
                            break
                        except ValueError:
                            pass
                # Check if action is simple WAIT
                elif action.upper().startswith('WAIT:'):
                    duration_str = action.split(':', 1)[1].strip()
                    if duration_str.endswith('s'):
                        try:
                            wait_duration = int(duration_str[:-1])
                            wait_key = f"wait_{seq_id}_{step_idx}"
                            self.wait_timers[wait_key] = (time.time() + wait_duration, seq_id, step_idx, None)
                            state['waiting'] = True
                            state['completed'].add(step_idx)
                            state['current_step'] = step_idx + 1
                            self.log_event(f"Sequence {seq_id} Step {step_idx}: Waiting {wait_duration}s")
                            break
                        except ValueError:
                            pass
                else:
                    # Parse and execute actions
                    self.execute_actions(action, seq_id, step_idx, step)
                    
                    state['completed'].add(step_idx)
                    state['current_step'] = step_idx + 1
                    
                    # Check if this is the last step
                    if step_idx == len(steps) - 1:
                        # Sequence complete
                        if seq.get('return_to_initial', False):
                            self.log_event(f"Sequence {seq_id}: Completed, returning to initial state")
                            self.reapply_initial_state(seq, seq_id)
                        else:
                            self.apply_end_state(seq, seq_id)
                        
                        # Reset sequence state for next run
                        self.multi_step_states[seq_key] = {
                            'current_step': 0, 
                            'completed': set(),
                            'waiting': False
                        }
                    break
    
    def execute_actions(self, action_str, seq_id, step_idx, full_step):
        """Execute one or more actions from action string."""
        # Parse duration if present (at the end)
        duration = 0
        if ':' in action_str:
            parts = action_str.rsplit(':', 1)
            action_str = parts[0].strip()
            duration_str = parts[1].strip()
            if duration_str.endswith('s'):
                try:
                    duration = int(duration_str[:-1])
                except ValueError:
                    pass
        
        # Split multiple actions by & (AND) or | (OR)
        if '&' in action_str:
            actions = [a.strip() for a in action_str.split('&')]
        elif '|' in action_str:
            actions = [a.strip() for a in action_str.split('|')]
        else:
            actions = [action_str.strip()]
        
        for action in actions:
            if not action:
                continue
            
            # Parse DO channel and state: DO2(ON), DO2(OFF), DO2
            if '(' in action and ')' in action:
                # Format: DO2(ON) or DO2(OFF)
                do_part, state_part = action.split('(', 1)
                do_part = do_part.strip()
                state_part = state_part.replace(')', '').strip()
                
                if not do_part.startswith('DO'):
                    continue
                
                try:
                    do_ch = int(do_part[2:])
                except ValueError:
                    continue
                
                # Execute action
                if state_part == 'ON':
                    self.relay.on(do_ch)
                    self.log_event(f"Multi-sequence {seq_id} Step {step_idx}: DO{do_ch} ON")
                    
                    # Schedule turn off if duration specified
                    if duration > 0:
                        timer_key = f"multi_{seq_id}_step_{step_idx}_do_{do_ch}"
                        self.step_timers[timer_key] = (time.time() + duration, do_ch, seq_id)
                        self.log_event(f"Sequence {seq_id}: DO{do_ch} will turn OFF in {duration}s")
                
                elif state_part == 'OFF':
                    self.relay.off(do_ch)
                    self.log_event(f"Multi-sequence {seq_id} Step {step_idx}: DO{do_ch} OFF")
                
                elif state_part == 'BLINK':
                    # Start blink mode
                    blink_key = f"multi_blink_{seq_id}_{step_idx}_{do_ch}"
                    if duration > 0:
                        end_time = time.time() + duration
                        next_toggle = time.time() + 1.0
                        self.blink_timers[blink_key] = (next_toggle, do_ch, seq_id, end_time)
                        self.blink_states[blink_key] = True
                        self.relay.on(do_ch)
                        self.log_event(f"Multi-sequence {seq_id} Step {step_idx}: DO{do_ch} started blinking for {duration}s")
                    else:
                        self.log_event(f"Multi-sequence {seq_id} Step {step_idx}: BLINK requires duration")
            
            else:
                # Legacy format: DO2 or DO2:5s (defaults to ON)
                if not action.startswith('DO'):
                    continue
                
                try:
                    do_ch = int(action[2:])
                except ValueError:
                    continue
                
                self.relay.on(do_ch)
                self.log_event(f"Multi-sequence {seq_id} Step {step_idx}: DO{do_ch} ON")
                
                if duration > 0:
                    timer_key = f"multi_{seq_id}_step_{step_idx}_do_{do_ch}"
                    self.step_timers[timer_key] = (time.time() + duration, do_ch, seq_id)
                    self.log_event(f"Sequence {seq_id}: DO{do_ch} will turn OFF in {duration}s")
    
    def evaluate_condition(self, condition, di_mask):
        """Evaluate condition string supporting DO state checks."""
        condition = condition.replace(' ', '')
        
        # Handle AND
        if '&' in condition:
            parts = condition.split('&')
            return all(self.check_input(p, di_mask) for p in parts)
        
        # Handle OR
        if '|' in condition:
            parts = condition.split('|')
            return any(self.check_input(p, di_mask) for p in parts)
        
        # Single input
        return self.check_input(condition, di_mask)
    
    def check_input(self, input_str, di_mask):
        """Check if a single input is in the specified state."""
        input_str = input_str.strip()
        
        # Check for edge detection: DI2(EDGE) or DI2(ONCE)
        if '(' in input_str and ')' in input_str:
            base_part, state_part = input_str.split('(', 1)
            base_part = base_part.strip()
            state_part = state_part.replace(')', '').strip()
            
            if base_part.startswith('DI') and state_part in ['EDGE', 'ONCE']:
                try:
                    ch = int(base_part[2:])
                    current_state = bool(di_mask & (1 << (ch - 1)))
                    edge_key = f"edge_{base_part}"
                    
                    # Get previous state
                    previous_state = self.edge_detected.get(edge_key, False)
                    
                    # Update current state
                    self.edge_detected[edge_key] = current_state
                    
                    # Return True only on rising edge (OFF -> ON)
                    return current_state and not previous_state
                except:
                    return False
            
            elif base_part.startswith('DO'):
                try:
                    ch = int(base_part[2:])
                    current_state = self.relay.status(ch)
                    
                    if state_part == 'ON':
                        return current_state
                    elif state_part == 'OFF':
                        return not current_state
                except:
                    return False
        
        # Standard format
        if input_str.startswith('DI'):
            try:
                ch = int(input_str[2:])
                return bool(di_mask & (1 << (ch - 1)))
            except:
                return False
        elif input_str.startswith('DO'):
            try:
                ch = int(input_str[2:])
                return self.relay.status(ch)
            except:
                return False
        
        return False
    
    def apply_initial_state(self, seq, seq_id):
        """Apply initial state for a sequence."""
        if seq_id in self.sequence_initialized:
            return
        
        if seq.get('initial_states'):
            for do_ch, state in seq['initial_states'].items():
                do_ch = int(do_ch)  # Ensure it's an integer
                if state:
                    self.relay.on(do_ch)
                    self.log_event(f"Sequence {seq_id}: Initial state - DO{do_ch} ON")
                else:
                    self.relay.off(do_ch)
                    self.log_event(f"Sequence {seq_id}: Initial state - DO{do_ch} OFF")
        
        self.sequence_initialized[seq_id] = True
    
    def reapply_initial_state(self, seq, seq_id):
        """Re-apply initial state without checking initialization flag."""
        if seq.get('initial_states'):
            for do_ch, state in seq['initial_states'].items():
                do_ch = int(do_ch)  # Ensure it's an integer
                if state:
                    self.relay.on(do_ch)
                    self.log_event(f"Sequence {seq_id}: Return to initial - DO{do_ch} ON")
                else:
                    self.relay.off(do_ch)
                    self.log_event(f"Sequence {seq_id}: Return to initial - DO{do_ch} OFF")
    
    def apply_end_state(self, seq, seq_id):
        """Apply end state for a sequence."""
        if seq.get('end_states'):
            for do_ch, state in seq['end_states'].items():
                do_ch = int(do_ch)  # Ensure it's an integer
                if state:
                    self.relay.on(do_ch)
                    self.log_event(f"Sequence {seq_id}: End state - DO{do_ch} ON")
                else:
                    self.relay.off(do_ch)
                    self.log_event(f"Sequence {seq_id}: End state - DO{do_ch} OFF")

    def save_configuration(self):
        """Save the current configuration to a file."""
        # Get enabled state for each sequence
        enabled_states = []
        for i in range(self.seq_tree.topLevelItemCount()):
            item = self.seq_tree.topLevelItem(i)
            checkbox = self.seq_tree.itemWidget(item, 2)
            enabled_states.append(checkbox.isChecked() if checkbox else True)
        
        config = {
            'sequences': self.sequences,
            'enabled_states': enabled_states,
            'saved_at': datetime.now().isoformat()
        }
        
        if save_config(config):
            self.log_event(f"Configuration saved: {len(self.sequences)} sequences")
        else:
            self.log_event("ERROR: Failed to save configuration")

    def update_sequence_status_display(self):
        """Update the sequence status display with current sequence information."""
        current_sequences = []
        completed_sequences = []
        next_steps = []
        next_sequence = None
        
        # Analyze all sequences
        for i in range(self.seq_tree.topLevelItemCount()):
            item = self.seq_tree.topLevelItem(i)
            checkbox = self.seq_tree.itemWidget(item, 2)
            
            if not checkbox or not checkbox.isChecked():
                continue
            
            seq = self.sequences[i]
            seq_key = f"multi_{i}"
            
            # Check if sequence is currently active
            is_active = False
            
            if seq['type'] == 'station':
                operation_type = seq.get('operation_type', 'Part Detection & Process')
                
                if operation_type == "Tool Picking Sequence":
                    # Handle tool picking sequence status
                    tool_key = f"tool_picking_{i}"
                    if tool_key in self.active_sequences:
                        is_active = True
                        tool_state = self.active_sequences[tool_key]['state']
                        state_display = {
                            'waiting_for_part': 'Waiting for Part',
                            'waiting_for_first_tool': 'Waiting for 1st Tool',
                            'alarm_first_tool': 'ALARM - 1st Tool',
                            'waiting_for_second_tool': 'Waiting for 2nd Tool', 
                            'alarm_second_tool': 'ALARM - 2nd Tool',
                            'waiting_for_part_clear': 'Waiting for Clear'
                        }.get(tool_state, tool_state)
                        current_sequences.append(f"#{i}: Tool Picking - {state_display}")
                        
                        # Show next step for tool picking
                        if tool_state == 'waiting_for_part':
                            next_steps.append(f"#{i}: Wait for part detection (DI{seq.get('part_sensor', 4)})")
                        elif tool_state == 'waiting_for_first_tool':
                            next_steps.append(f"#{i}: Pick 1st tools (DI{seq.get('tools_picked_sensor', 3)})")
                        elif tool_state == 'waiting_for_second_tool':
                            next_steps.append(f"#{i}: Collect all tools (DI{seq.get('tools_collected_sensor', 2)})")
                        elif 'alarm' in tool_state:
                            next_steps.append(f"#{i}: Clear alarm condition")
                        elif tool_state == 'waiting_for_part_clear':
                            next_steps.append(f"#{i}: Remove part from station")
                else:
                    # Handle other station operations
                    station_key = f"station_{i}_{seq.get('process_device', 1)}"
                    blink_key = f"station_blink_{i}_{seq.get('process_device', 1)}"
                    if station_key in self.active_sequences or blink_key in self.blink_timers:
                        is_active = True
                        station_state = self.active_sequences.get(station_key, {}).get('state', 'unknown')
                        process_device = seq.get('process_device', 1)
                        current_sequences.append(f"#{i}: Station Operation - DO{process_device} ({station_state})")
            else:
                # Production line sequence
                if seq_key in self.multi_step_states:
                    state = self.multi_step_states[seq_key]
                    current_step = state.get('current_step', 0)
                    steps = seq.get('steps', '').strip().split('\n')
                    
                    if current_step < len(steps):
                        is_active = True
                        current_sequences.append(f"#{i}: Production Line (Step {current_step + 1}/{len(steps)})")
                        
                        # Show next step
                        if current_step < len(steps):
                            next_step_text = steps[current_step].strip()
                            if len(next_step_text) > 50:
                                next_step_text = next_step_text[:50] + "..."
                            next_steps.append(f"#{i}: {next_step_text}")
                    else:
                        # Sequence completed
                        completed_sequences.append(f"#{i}: Production Line Completed")
            
            # Check for completed station operations
            if seq['type'] == 'station' and not is_active:
                station_key = f"station_{i}_{seq.get('process_device', 1)}"
                if i in self.sequence_initialized and station_key not in self.active_sequences:
                    # This could be considered "completed" if it was triggered before
                    pass
        
        # Find next sequence that will be triggered
        for i in range(self.seq_tree.topLevelItemCount()):
            item = self.seq_tree.topLevelItem(i)
            checkbox = self.seq_tree.itemWidget(item, 2)
            
            if checkbox and checkbox.isChecked():
                seq = self.sequences[i]
                if seq['type'] == 'station':
                    operation_type = seq.get('operation_type', 'Part Detection & Process')
                    
                    if operation_type == "Tool Picking Sequence":
                        tool_key = f"tool_picking_{i}"
                        if tool_key not in self.active_sequences:
                            part_sensor = seq.get('part_sensor', 4)
                            next_sequence = f"#{i}: Tool Picking - Wait for Part_DI{part_sensor}"
                            break
                    else:
                        part_sensor = seq.get('part_sensor', 1)
                        process_device = seq.get('process_device', 1)
                        next_sequence = f"#{i}: {operation_type} - Part_DI{part_sensor} -> Process_DO{process_device}"
                        break
                else:
                    seq_key = f"production_{i}"
                    if seq_key not in self.multi_step_states or self.multi_step_states[seq_key]['current_step'] == 0:
                        steps = seq.get('steps', '').strip().split('\n')
                        if steps:
                            first_step = steps[0].strip()
                            if len(first_step) > 40:
                                first_step = first_step[:40] + "..."
                            next_sequence = f"#{i}: {first_step}"
                            break
        
        # Update UI labels
        if current_sequences:
            self.current_seq_label.setText(f"Current Sequence: {', '.join(current_sequences)}")
            self.current_seq_label.setStyleSheet("font-weight: bold; color: blue;")
        else:
            self.current_seq_label.setText("Current Sequence: None")
            self.current_seq_label.setStyleSheet("font-weight: bold; color: gray;")
        
        if next_steps:
            self.next_step_label.setText(f"Next Step: {'; '.join(next_steps)}")
            self.next_step_label.setStyleSheet("color: #FFA500; font-weight: bold;")
        else:
            self.next_step_label.setText("Next Step: None")
            self.next_step_label.setStyleSheet("color: gray;")
        
        if completed_sequences:
            self.completed_label.setText(f"Completed: {', '.join(completed_sequences)}")
            self.completed_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.completed_label.setText("Completed Sequences: None")
            self.completed_label.setStyleSheet("color: gray;")
        
        if next_sequence:
            self.next_seq_label.setText(f"Next Sequence: {next_sequence}")
            self.next_seq_label.setStyleSheet("color: yellow; background-color: #333; font-weight: bold; padding: 2px;")
        else:
            self.next_seq_label.setText("Next Sequence: None")
            self.next_seq_label.setStyleSheet("color: gray; background-color: transparent;")

    def check_di_channel(self, channel):
        """Check if a specific DI channel is ON or OFF.
        
        Args:
            channel (int): DI channel number (1-8)
            
        Returns:
            bool: True if channel is ON, False if OFF or invalid channel
        """
        if not self.relay:
            return False
        
        if not (1 <= channel <= 8):
            self.log_event(f"Invalid DI channel: {channel}. Must be 1-8")
            return False
        
        try:
            di_mask = self.relay.check_DI()
            is_on = bool(di_mask & (1 << (channel - 1)))
            return is_on
        except Exception as e:
            self.log_event(f"Error checking DI{channel}: {e}")
            return False
    
    def get_all_di_states(self):
        """Get the current state of all DI channels.
        
        Returns:
            dict: Dictionary with channel numbers as keys and boolean states as values
        """
        di_states = {}
        
        if not self.relay:
            return di_states
        
        try:
            di_mask = self.relay.check_DI()
            for i in range(8):
                channel = i + 1
                is_on = bool(di_mask & (1 << i))
                di_states[channel] = is_on
        except Exception as e:
            self.log_event(f"Error getting DI states: {e}")
        
        return di_states
    
    def check_do_channel(self, channel):
        """Check if a specific DO channel is ON or OFF.
        
        Args:
            channel (int): DO channel number (1-8)
            
        Returns:
            bool: True if channel is ON, False if OFF or invalid channel
        """
        if not self.relay:
            return False
        
        if not (1 <= channel <= 8):
            self.log_event(f"Invalid DO channel: {channel}. Must be 1-8")
            return False
        
        try:
            return self.relay.status(channel)
        except Exception as e:
            self.log_event(f"Error checking DO{channel}: {e}")
            return False
    
    def get_all_do_states(self):
        """Get the current state of all DO channels.
        
        Returns:
            dict: Dictionary with channel numbers as keys and boolean states as values
        """
        do_states = {}
        
        if not self.relay:
            return do_states
        
        try:
            for channel in range(1, 9):
                is_on = self.relay.status(channel)
                do_states[channel] = is_on
        except Exception as e:
            self.log_event(f"Error getting DO states: {e}")
        
        return do_states

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

