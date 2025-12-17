#!/usr/bin/env python3
"""
Poka-Yoke Table Control - Table-based Step Sequence
Uses table widget with 20 rows for 20 steps
Each step: DO sends signal -> wait for DI -> wait for DI OFF -> DO off
With job sequence save/load and alarm management
"""

import sys
import os

import json
from threading import Thread, Lock
from time import sleep
from typing import List, Dict
from functools import partial
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QComboBox, QLabel, QMessageBox, 
    QTabWidget, QPushButton, QGroupBox, QLineEdit, QSpinBox, QCheckBox, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer
from PySide6.QtGui import QColor, QBrush

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime as dt

from relay_client import RelayClient


# Configuration
RELAY_CONFIGS = [
    {'ip': '192.168.1.200', 'port': 4196, 'name': 'Table 1'},
    {'ip': '192.168.1.201', 'port': 4196, 'name': 'Table 2'},
    {'ip': '192.168.1.202', 'port': 4196, 'name': 'Table 3'},
    {'ip': '192.168.1.203', 'port': 4196, 'name': 'Table 4'},
]
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '500'))  # milliseconds
JOBS_FILE = 'job_sequences.json'
ALARM_CONFIG_FILE = 'alarm_config.json'

# Number of IO points per relay
NUM_INPUTS = 8
NUM_OUTPUTS = 8
NUM_STEPS = 20


# ============================================================================
# Data Models for Jobs and Alarms
# ============================================================================

class AlarmConfig:
    """Alarm configuration"""
    def __init__(self, relay_id: str = "", do_channel: int = 0, enabled: bool = True):
        self.relay_id = relay_id
        self.do_channel = do_channel
        self.enabled = enabled

    def to_dict(self):
        return {
            'relay_id': self.relay_id,
            'do_channel': self.do_channel,
            'enabled': self.enabled
        }

    @staticmethod
    def from_dict(data):
        return AlarmConfig(
            relay_id=data.get('relay_id', ''),
            do_channel=data.get('do_channel', 0),
            enabled=data.get('enabled', True)
        )


class JobSequence:
    """Job sequence configuration"""
    def __init__(self, job_name: str = "New Job"):
        self.job_name = job_name
        self.created_at = datetime.now().isoformat()
        self.relay_sequences = {}  # relay_id -> [box_nums]
        
        # Initialize for all relays
        for config in RELAY_CONFIGS:
            relay_id = config['ip']
            self.relay_sequences[relay_id] = [0] * NUM_STEPS

    def to_dict(self):
        return {
            'job_name': self.job_name,
            'created_at': self.created_at,
            'relay_sequences': self.relay_sequences
        }

    @staticmethod
    def from_dict(data):
        job = JobSequence(data['job_name'])
        job.created_at = data.get('created_at', '')
        job.relay_sequences = data.get('relay_sequences', {})
        return job


# ============================================================================
# Signals
# ============================================================================

class RelaySignals(QObject):
    """Signals for relay communication"""
    di_updated = Signal(str, list)  # relay_id, states
    do_updated = Signal(str, list)  # relay_id, states
    connection_status_changed = Signal(str, bool)  # relay_id, connected
    error_occurred = Signal(str)


class SequenceSignals(QObject):
    """Signals for sequence execution"""
    step_executed = Signal(str, int)  # relay_id, step_number
    step_status_changed = Signal(str, int, str)  # relay_id, step_number, status
    sequence_error = Signal(str, str)  # relay_id, error_msg
    unexpected_di = Signal(str, int)  # relay_id, di_channel


# ============================================================================
# Sequence Executor
# ============================================================================

class StepSequenceExecutor:
    """Executes a step-based sequence on a relay"""

    def __init__(self, relay_id: str, relay_client: RelayClient,
                 relay_states: Dict, signals: SequenceSignals, 
                 step_configs: List[int], alarm_config: AlarmConfig):
        """
        relay_id: IP address of relay
        relay_client: RelayClient instance
        relay_states: Dict with 'di' and 'do' lists
        signals: SequenceSignals for updates
        step_configs: List of BOX numbers (1-8) for each step (index 0 = step 1)
        alarm_config: AlarmConfig for unexpected DI detection
        """
        self.relay_id = relay_id
        self.relay_client = relay_client
        self.relay_states = relay_states
        self.signals = signals
        self.step_configs = step_configs
        self.alarm_config = alarm_config
        self.current_step = 0
        self.running = False
        self.lock = Lock()
        self.step_status = ['IDLE'] * NUM_STEPS
        self.previous_di_states = [False] * NUM_INPUTS

    def set_step_config(self, step_num: int, box_num: int):
        """Set BOX number for a step (1-based step_num)"""
        if 1 <= step_num <= NUM_STEPS:
            self.step_configs[step_num - 1] = box_num

    def update_relay_states(self, di_states: List[bool], do_states: List[bool]):
        """Update relay states from polling"""
        self.relay_states['di'] = di_states
        self.relay_states['do'] = do_states
        
        # Check for unexpected DI (DI ON outside of expected channel)
        self.check_unexpected_di(di_states)

    def check_unexpected_di(self, di_states: List[bool]):
        """Check for unexpected DI signals"""
        expected_di_channel = self.step_configs[self.current_step - 1] if self.current_step > 0 else 0
        
        for channel_num in range(1, NUM_INPUTS + 1):
            if di_states[channel_num - 1]:  # DI is ON
                # Check if this is unexpected
                if self.running and channel_num != expected_di_channel:
                    # Unexpected DI detected
                    self.signals.unexpected_di.emit(self.relay_id, channel_num)
                    
                    # Trigger alarm if configured
                    if self.alarm_config.enabled and self.alarm_config.do_channel > 0:
                        self.trigger_alarm()

    def trigger_alarm(self):
        """Trigger alarm DO - keep ON until reset"""
        if not self.alarm_config.enabled or self.alarm_config.do_channel == 0:
            return
        
        try:
            # Verify relay is connected
            if not self.relay_client.is_connected():
                print(f"[{self.relay_id}] Relay not connected, attempting to connect for alarm...")
                if not self.relay_client.connect():
                    print(f"[{self.relay_id}] Failed to connect relay for alarm")
                    return
            
            alarm_channel = self.alarm_config.do_channel
            print(f"[{self.relay_id}] Triggering alarm on DO{alarm_channel}")
            
            # Turn ON alarm DO and keep it ON until reset
            success = self.relay_client.write_digital_output(alarm_channel, True)
            if success:
                print(f"[{self.relay_id}] A`larm on DO{alarm_channel} sent successfully")
            else:
                print(f"[{self.relay_id}] Failed to set DO{alarm_channel} ON")
            
        except Exception as e:
            print(f"[{self.relay_id}] Error triggering alarm on DO{self.alarm_config.do_channel}: {e}")


    def send_do_signal(self, box_num: int) -> bool:
        """Send DO signal for box (box_num 1-8 maps to DO channel)"""
        if not (1 <= box_num <= NUM_OUTPUTS):
            return False
        try:
            self.relay_client.write_digital_output(box_num, True)
            sleep(0.1)
            return True
        except Exception as e:
            print(f"Error sending DO signal for box {box_num}: {e}")
            return False

    def turn_off_do(self, box_num: int) -> bool:
        """Turn off DO signal for box"""
        if not (1 <= box_num <= NUM_OUTPUTS):
            return False
        try:
            self.relay_client.write_digital_output(box_num, False)
            sleep(0.1)
            return True
        except Exception as e:
            print(f"Error turning off DO for box {box_num}: {e}")
            return False

    def wait_for_di(self, box_num: int) -> bool:
        """Wait for DI signal for box (box_num 1-8 maps to DI channel)"""
        if not (1 <= box_num <= NUM_INPUTS):
            return False

        # Wait indefinitely for DI to turn ON
        while True:
            if box_num - 1 < len(self.relay_states.get('di', [])):
                if self.relay_states['di'][box_num - 1]:
                    return True
            sleep(0.1)

    def wait_for_di_off(self, box_num: int) -> bool:
        """Wait for DI signal to turn OFF before proceeding to next step"""
        if not (1 <= box_num <= NUM_INPUTS):
            return False

        # Wait indefinitely for DI to turn OFF
        while True:
            if box_num - 1 < len(self.relay_states.get('di', [])):
                if not self.relay_states['di'][box_num - 1]:
                    return True
            sleep(0.1)

    def run(self):
        """Execute the step sequence"""
        with self.lock:
            if self.running:
                return
            self.running = True

        try:
            # Continuous loop - sequence restarts automatically
            while self.running:
                for step_num in range(1, NUM_STEPS + 1):
                    if not self.running:
                        break

                    self.current_step = step_num
                    box_num = self.step_configs[step_num - 1]

                    # Skip if box is 0 (not configured)
                    if box_num == 0:
                        self.step_status[step_num - 1] = 'SKIP'
                        self.signals.step_status_changed.emit(self.relay_id, step_num, 'SKIP')
                        continue

                    try:
                        # Step 1: Send DO signal
                        self.step_status[step_num - 1] = 'SIGNAL'
                        self.signals.step_status_changed.emit(self.relay_id, step_num, 'SIGNAL')
                        
                        if not self.send_do_signal(box_num):
                            self.step_status[step_num - 1] = 'ERROR'
                            self.signals.step_status_changed.emit(self.relay_id, step_num, 'ERROR')
                            continue

                        # Step 2: Wait for DI ON
                        self.step_status[step_num - 1] = 'WAIT'
                        self.signals.step_status_changed.emit(self.relay_id, step_num, 'WAIT')
                        
                        if not self.wait_for_di(box_num):
                            self.step_status[step_num - 1] = 'ERROR'
                            self.signals.step_status_changed.emit(self.relay_id, step_num, 'ERROR')
                            continue

                        # Step 3: Wait for DI OFF before proceeding
                        self.step_status[step_num - 1] = 'WAIT_OFF'
                        self.signals.step_status_changed.emit(self.relay_id, step_num, 'WAIT_OFF')
                        
                        if not self.wait_for_di_off(box_num):
                            self.step_status[step_num - 1] = 'ERROR'
                            self.signals.step_status_changed.emit(self.relay_id, step_num, 'ERROR')
                            continue

                        # Step 4: Turn off DO
                        self.step_status[step_num - 1] = 'OFF'
                        self.signals.step_status_changed.emit(self.relay_id, step_num, 'OFF')
                        
                        if not self.turn_off_do(box_num):
                            self.step_status[step_num - 1] = 'ERROR'
                            self.signals.step_status_changed.emit(self.relay_id, step_num, 'ERROR')
                            continue

                        # Step complete
                        self.step_status[step_num - 1] = 'OK'
                        self.signals.step_status_changed.emit(self.relay_id, step_num, 'OK')
                        
                    except Exception as e:
                        print(f"Step {step_num} error: {e}")
                        self.step_status[step_num - 1] = 'ERROR'
                        self.signals.step_status_changed.emit(self.relay_id, step_num, 'ERROR')

                    sleep(0.5)

                # Sequence loop completed
                print(f"[{self.relay_id}] Sequence loop completed")

        except Exception as e:
            print(f"Execution error: {e}")
            self.signals.sequence_error.emit(self.relay_id, str(e))
        finally:
            with self.lock:
                self.running = False

    def stop(self):
        """Stop sequence execution"""
        with self.lock:
            self.running = False


# ============================================================================
# Job Management
# ============================================================================

class JobManager:
    """Manage job sequences"""
    
    @staticmethod
    def save_job(job: JobSequence):
        """Save job to file"""
        try:
            jobs = []
            if os.path.exists(JOBS_FILE):
                with open(JOBS_FILE, 'r') as f:
                    jobs = json.load(f)
            
            # Replace or add job
            jobs = [j for j in jobs if j.get('job_name') != job.job_name]
            jobs.append(job.to_dict())
            
            with open(JOBS_FILE, 'w') as f:
                json.dump(jobs, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving job: {e}")
            return False

    @staticmethod
    def load_job(job_name: str) -> JobSequence:
        """Load job from file"""
        try:
            if os.path.exists(JOBS_FILE):
                with open(JOBS_FILE, 'r') as f:
                    jobs = json.load(f)
                    for job_data in jobs:
                        if job_data['job_name'] == job_name:
                            return JobSequence.from_dict(job_data)
        except Exception as e:
            print(f"Error loading job: {e}")
        return None

    @staticmethod
    def list_jobs() -> List[str]:
        """List all job names"""
        try:
            if os.path.exists(JOBS_FILE):
                with open(JOBS_FILE, 'r') as f:
                    jobs = json.load(f)
                    return [j['job_name'] for j in jobs]
        except Exception as e:
            print(f"Error listing jobs: {e}")
        return []


class AlarmManager:
    """Manage alarm configurations"""
    
    @staticmethod
    def save_alarm_config(relay_id: str, config: AlarmConfig):
        """Save alarm config"""
        try:
            configs = {}
            if os.path.exists(ALARM_CONFIG_FILE):
                with open(ALARM_CONFIG_FILE, 'r') as f:
                    configs = json.load(f)
            
            configs[relay_id] = config.to_dict()
            
            with open(ALARM_CONFIG_FILE, 'w') as f:
                json.dump(configs, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving alarm config: {e}")
            return False

    @staticmethod
    def load_alarm_config(relay_id: str) -> AlarmConfig:
        """Load alarm config"""
        try:
            if os.path.exists(ALARM_CONFIG_FILE):
                with open(ALARM_CONFIG_FILE, 'r') as f:
                    configs = json.load(f)
                    if relay_id in configs:
                        return AlarmConfig.from_dict(configs[relay_id])
        except Exception as e:
            print(f"Error loading alarm config: {e}")
        return AlarmConfig(relay_id=relay_id)


# ============================================================================
# Alarm Password Dialog
# ============================================================================

class AlarmPasswordDialog(QDialog):
    """Dialog for password-protected alarm reset with numeric keypad"""
    
    def __init__(self, relay_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Alarm Reset - {relay_name}")
        self.setGeometry(300, 300, 400, 550)
        self.setModal(True)
        self.password_correct = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI with password input and numeric keypad"""
        layout = QVBoxLayout()
        
        # Instructions
        instruction_label = QLabel("Enter password to reset alarm:")
        instruction_label.setStyleSheet("font-size: 12pt; margin: 10px; font-weight: bold;")
        layout.addWidget(instruction_label)
        
        # Password input field
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font-size: 16pt; padding: 10px; margin: 10px;")
        self.password_input.setPlaceholderText("Enter 4-digit password")
        self.password_input.setMaxLength(4)
        layout.addWidget(self.password_input)
        
        # Numeric keypad
        keypad_group = QGroupBox("Numeric Keypad")
        keypad_layout = QVBoxLayout()
        
        # Create number buttons in rows
        # Row 1: 1, 2, 3
        button_layout1 = QHBoxLayout()
        for num in [1, 2, 3]:
            btn = QPushButton(str(num))
            btn.setStyleSheet("QPushButton { font-size: 20pt; padding: 15px; margin: 2px; }")
            btn.clicked.connect(lambda checked, n=num: self._add_digit(str(n)))
            button_layout1.addWidget(btn)
        keypad_layout.addLayout(button_layout1)
        
        # Row 2: 4, 5, 6
        button_layout2 = QHBoxLayout()
        for num in [4, 5, 6]:
            btn = QPushButton(str(num))
            btn.setStyleSheet("QPushButton { font-size: 20pt; padding: 15px; margin: 2px; }")
            btn.clicked.connect(lambda checked, n=num: self._add_digit(str(n)))
            button_layout2.addWidget(btn)
        keypad_layout.addLayout(button_layout2)
        
        # Row 3: 7, 8, 9
        button_layout3 = QHBoxLayout()
        for num in [7, 8, 9]:
            btn = QPushButton(str(num))
            btn.setStyleSheet("QPushButton { font-size: 20pt; padding: 15px; margin: 2px; }")
            btn.clicked.connect(lambda checked, n=num: self._add_digit(str(n)))
            button_layout3.addWidget(btn)
        keypad_layout.addLayout(button_layout3)
        
        # Row 4: Clear, 0, Backspace
        button_layout4 = QHBoxLayout()
        
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("QPushButton { font-size: 16pt; padding: 15px; margin: 2px; background-color: #FF6B6B; color: white; font-weight: bold; }")
        clear_btn.clicked.connect(self._clear_password)
        button_layout4.addWidget(clear_btn)
        
        zero_btn = QPushButton("0")
        zero_btn.setStyleSheet("QPushButton { font-size: 20pt; padding: 15px; margin: 2px; }")
        zero_btn.clicked.connect(lambda: self._add_digit("0"))
        button_layout4.addWidget(zero_btn)
        
        backspace_btn = QPushButton("⌫")
        backspace_btn.setStyleSheet("QPushButton { font-size: 16pt; padding: 15px; margin: 2px; background-color: #FFA500; color: white; font-weight: bold; }")
        backspace_btn.clicked.connect(self._backspace)
        button_layout4.addWidget(backspace_btn)
        
        keypad_layout.addLayout(button_layout4)
        keypad_group.setLayout(keypad_layout)
        layout.addWidget(keypad_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.verify_password)
        button_box.rejected.connect(self.reject)
        
        # Style the OK and Cancel buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setStyleSheet("QPushButton { font-size: 14pt; padding: 10px; background-color: #4CAF50; color: white; font-weight: bold; }")
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setStyleSheet("QPushButton { font-size: 14pt; padding: 10px; background-color: #757575; color: white; font-weight: bold; }")
        
        layout.addWidget(button_box)
        self.setLayout(layout)
    
    def _add_digit(self, digit: str):
        """Add digit to password input"""
        current = self.password_input.text()
        if len(current) < 4:
            self.password_input.setText(current + digit)
    
    def _backspace(self):
        """Remove last character from password input"""
        current = self.password_input.text()
        if current:
            self.password_input.setText(current[:-1])
    
    def _clear_password(self):
        """Clear password input"""
        self.password_input.clear()
    
    def verify_password(self):
        """Verify entered password"""
        password = self.password_input.text()
        correct_password = "5435"
        
        if password == correct_password:
            self.password_correct = True
            self.accept()
        else:
            QMessageBox.warning(self, "Incorrect Password", "The password you entered is incorrect!\n\nPlease try again.")
            self.password_input.clear()
    
    def is_correct(self):
        """Check if password was correct"""
        return self.password_correct


# ============================================================================
# Main Application Window
# ============================================================================

class PokayokeTableWindow(QMainWindow):
    """Main application window with table-based step control"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poka-Yoke Table Control with Job Management")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize relay clients
        self.relay_clients = {}
        self.relay_signals = {}
        self.relay_states = {}
        self.sequence_signals = SequenceSignals()
        self.sequence_executors = {}
        self.alarm_configs = {}
        self.polling_threads = {}
        self.polling_active = False
        self.active_alarms = {}  # Track which relays have active alarms
        
        # Cycle time tracking
        self.cycle_start_time = {}  # relay_id -> start time
        self.cycle_time_labels = {}  # relay_id -> QLabel
        self.cycle_count_labels = {}  # relay_id -> QLabel for cycle counter
        self.cycle_count = {}  # relay_id -> number of completed cycles
        self.total_cycle_time = {}  # relay_id -> total time of all completed cycles
        self.avg_cycle_time_labels = {}  # relay_id -> QLabel for average cycle time
        self.cycle_time_buttons = {}  # relay_id -> {'start': btn, 'stop': btn, 'reset': btn}
        self.cycle_timer = None  # Qt timer for cycle time updates
        self.last_step_status = {}  # relay_id -> last configured step status
        
        # Graph tracking - store cycle times for graphing
        self.graph_cycle_times = {}  # relay_id -> {'timestamps': [], 'durations': []}
        self.graph_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']  # Colors for 4 tables
        self.graph_canvas = None  # Matplotlib canvas for graph tab
        
        # Initialize graph data structures
        for config in RELAY_CONFIGS:
            relay_id = config['ip']
            self.graph_cycle_times[relay_id] = {'timestamps': [], 'durations': []}

        for config in RELAY_CONFIGS:
            relay_id = config['ip']
            self.relay_clients[relay_id] = RelayClient(config['ip'], config['port'])
            self.relay_signals[relay_id] = RelaySignals()
            self.relay_states[relay_id] = {
                'di': [False] * NUM_INPUTS,
                'do': [False] * NUM_OUTPUTS,
                'connected': False
            }
            self.active_alarms[relay_id] = False  # Initialize alarm state
            self.alarm_configs[relay_id] = AlarmManager.load_alarm_config(relay_id)

        self.current_job = None
        self.init_ui()
        self.setup_signals()
        self.start_polling()

    def init_ui(self):
        """Initialize UI programmatically"""
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Tab widget
        self.tab_widget = QTabWidget()

        # Monitor tab
        self.setup_monitor_tab()
        self.tab_widget.addTab(self.monitor_widget, "Monitor")

        # Job Change tab
        self.setup_job_change_tab()
        self.tab_widget.addTab(self.job_change_widget, "Job Change")

        # Machine Data tab
        self.setup_machine_data_tab()
        self.tab_widget.addTab(self.machine_data_widget, "Machine Data")

        # Alarm tab
        self.setup_alarm_tab()
        self.tab_widget.addTab(self.alarm_widget, "Alarm")

        # Manual tab
        self.setup_manual_tab()
        self.tab_widget.addTab(self.manual_widget, "Manual")
        
        # Graph tab
        self.setup_graph_tab()
        self.tab_widget.addTab(self.graph_widget, "Graph")

        main_layout.addWidget(self.tab_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def setup_graph_tab(self):
        """Setup Graph tab for cycle time visualization"""
        self.graph_widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Cycle Time Graph - Real-time Trends")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Create matplotlib figure
        self.graph_figure = Figure(figsize=(12, 6), dpi=100)
        self.graph_ax = self.graph_figure.add_subplot(111)
        self.graph_ax.set_xlabel("Time")
        self.graph_ax.set_ylabel("Cycle Time (seconds)")
        self.graph_ax.set_title("Cycle Time Trends for All Tables")
        self.graph_ax.grid(True, alpha=0.3)
        
        # Format X-axis for time
        self.graph_ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.graph_figure.autofmt_xdate(rotation=45)
        
        # Create canvas
        self.graph_canvas = FigureCanvas(self.graph_figure)
        layout.addWidget(self.graph_canvas)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Legend:"))
        for idx, config in enumerate(RELAY_CONFIGS):
            color_box = QLabel("■")
            color_box.setStyleSheet(f"color: {self.graph_colors[idx]}; font-size: 16px;")
            legend_layout.addWidget(color_box)
            legend_layout.addWidget(QLabel(config['name']))
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        clear_graph_btn = QPushButton("Clear Graph")
        clear_graph_btn.clicked.connect(self.on_clear_graph)
        button_layout.addWidget(clear_graph_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.graph_widget.setLayout(layout)
    
    def on_clear_graph(self):
        """Clear all graph data"""
        for relay_id in self.graph_cycle_times:
            self.graph_cycle_times[relay_id] = {'timestamps': [], 'durations': []}
        self.update_graph()
    
    def update_graph(self):
        """Update the cycle time graph"""
        if self.graph_canvas is None:
            return
        
        self.graph_ax.clear()
        self.graph_ax.set_xlabel("Time")
        self.graph_ax.set_ylabel("Cycle Time (seconds)")
        self.graph_ax.set_title("Cycle Time Trends for All Tables")
        self.graph_ax.grid(True, alpha=0.3)
        
        # Plot data for each relay
        for idx, config in enumerate(RELAY_CONFIGS):
            relay_id = config['ip']
            relay_name = config['name']
            
            if relay_id in self.graph_cycle_times:
                data = self.graph_cycle_times[relay_id]
                if len(data['timestamps']) > 0 and len(data['durations']) > 0:
                    self.graph_ax.plot(
                        data['timestamps'],
                        data['durations'],
                        marker='o',
                        linestyle='-',
                        linewidth=2,
                        color=self.graph_colors[idx],
                        label=relay_name,
                        markersize=6
                    )
        
        # Format X-axis for time
        self.graph_ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.graph_figure.autofmt_xdate(rotation=45)
        
        # Add legend
        if len(self.graph_ax.get_lines()) > 0:
            self.graph_ax.legend(loc='upper left')
        
        self.graph_figure.tight_layout()
        self.graph_canvas.draw()

    def setup_manual_tab(self):
        """Setup Manual tab for relay control - all 4 relays in horizontal layout"""
        self.manual_widget = QWidget()
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Manual Relay Control")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title)

        # Horizontal layout for all 4 relays
        relays_layout = QHBoxLayout()

        self.manual_ui_di_indicators = {}
        self.manual_ui_do_buttons = {}
        self.manual_ui_do_indicators = {}
        self.manual_ui_connection_labels = {}

        for config in RELAY_CONFIGS:
            relay_id = config['ip']
            relay_name = config['name']

            group_box = QGroupBox(relay_name)
            group_layout = QVBoxLayout()

            # Connection status
            conn_label = QLabel("Disconnected ✗")
            conn_label.setStyleSheet("color: red; font-weight: bold;")
            self.manual_ui_connection_labels[relay_id] = conn_label
            group_layout.addWidget(conn_label)

            # DI section
            di_group = QGroupBox("Digital Inputs (DI)")
            di_grid = QGridLayout()
            di_indicators = []
            for i in range(NUM_INPUTS):
                label = QLabel(f"DI{i+1}: OFF")
                label.setStyleSheet("background-color: #CCCCCC; padding: 5px; font-size: 9px;")
                di_indicators.append(label)
                di_grid.addWidget(label, i // 4, i % 4)
            di_group.setLayout(di_grid)
            group_layout.addWidget(di_group)
            self.manual_ui_di_indicators[relay_id] = di_indicators

            # DO control section
            do_control_group = QGroupBox("Relay Control")
            do_grid = QGridLayout()
            do_buttons = []
            for i in range(NUM_OUTPUTS):
                btn = QPushButton(f"CH{i+1}")
                btn.setMinimumHeight(30)
                btn.setMinimumWidth(40)
                btn.clicked.connect(partial(self.on_manual_do_button_clicked, relay_id, i))
                do_buttons.append(btn)
                do_grid.addWidget(btn, i // 4, i % 4)
            do_control_group.setLayout(do_grid)
            group_layout.addWidget(do_control_group)
            self.manual_ui_do_buttons[relay_id] = do_buttons

            # DO status section
            do_status_group = QGroupBox("Relay Status")
            do_status_grid = QGridLayout()
            do_indicators = []
            for i in range(NUM_OUTPUTS):
                label = QLabel(f"CH{i+1}: OFF")
                label.setStyleSheet("background-color: #CCCCCC; padding: 5px; font-size: 9px;")
                do_indicators.append(label)
                do_status_grid.addWidget(label, i // 4, i % 4)
            do_status_group.setLayout(do_status_grid)
            group_layout.addWidget(do_status_group)
            self.manual_ui_do_indicators[relay_id] = do_indicators

            group_layout.addStretch()
            group_box.setLayout(group_layout)
            relays_layout.addWidget(group_box)

        main_layout.addLayout(relays_layout)
        self.manual_widget.setLayout(main_layout)

    def setup_alarm_tab(self):
        """Setup Alarm tab for reset control - Horizontal layout"""
        self.alarm_widget = QWidget()
        main_layout = QVBoxLayout()
        
        title = QLabel("Active Alarms - Reset with Password")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title)
        
        # Horizontal layout for all relays
        relays_layout = QHBoxLayout()
        
        # Create section for each relay
        self.alarm_reset_buttons = {}
        
        for config in RELAY_CONFIGS:
            relay_id = config['ip']
            relay_name = config['name']
            
            # Group box for each relay
            relay_group = QGroupBox(relay_name)
            relay_layout = QVBoxLayout()
            
            # Status label
            status_label = QLabel("No Alarm")
            status_label.setStyleSheet("color: green; font-weight: bold; font-size: 12pt; text-align: center;")
            relay_layout.addWidget(status_label)
            
            # Reset button
            reset_btn = QPushButton("Reset Alarm")
            reset_btn.setEnabled(False)
            reset_btn.setMinimumHeight(40)
            reset_btn.clicked.connect(partial(self.on_reset_alarm, relay_id, relay_name, status_label, reset_btn))
            relay_layout.addWidget(reset_btn)
            
            relay_layout.addStretch()
            relay_group.setLayout(relay_layout)
            relays_layout.addWidget(relay_group)
            
            self.alarm_reset_buttons[relay_id] = {
                'button': reset_btn,
                'status': status_label
            }
        
        main_layout.addLayout(relays_layout)
        main_layout.addStretch()
        self.alarm_widget.setLayout(main_layout)

    def on_reset_alarm(self, relay_id: str, relay_name: str, status_label: QLabel, reset_btn: QPushButton):
        """Handle alarm reset with password"""
        dialog = AlarmPasswordDialog(relay_name, self)
        
        if dialog.exec() == QDialog.Accepted and dialog.is_correct():
            # Turn off the alarm DO
            try:
                executor = self.sequence_executors.get(relay_id)
                if executor and executor.alarm_config.do_channel > 0:
                    do_channel = executor.alarm_config.do_channel
                    self.relay_clients[relay_id].write_digital_output(do_channel, False)
                    print(f"[{relay_id}] Alarm reset - DO{do_channel} turned OFF")
                    
                    # Update UI
                    self.active_alarms[relay_id] = False
                    status_label.setText("No Alarm")
                    status_label.setStyleSheet("color: green;")
                    reset_btn.setEnabled(False)
                    
                    QMessageBox.information(self, "Success", f"Alarm reset for {relay_name}")
            except Exception as e:
                print(f"Error resetting alarm: {e}")
                QMessageBox.critical(self, "Error", f"Failed to reset alarm: {e}")

    def setup_monitor_tab(self):
        """Setup the Monitor tab with table controls - Horizontal layout"""
        self.monitor_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Monitor - 4 Relay Tables")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title)
        
        # Horizontal layout for tables
        tables_layout = QHBoxLayout()

        self.table_widgets = {}
        self.table_combos = {}

        for config in RELAY_CONFIGS:
            relay_id = config['ip']
            relay_name = config['name']

            group_box = QGroupBox(relay_name)
            group_layout = QVBoxLayout()

            # Create table for this relay
            table_widget = QTableWidget()
            self.table_widgets[relay_id] = table_widget

            # Initialize executor for this relay
            step_configs = [0] * NUM_STEPS
            executor = StepSequenceExecutor(
                relay_id,
                self.relay_clients[relay_id],
                self.relay_states[relay_id],
                self.sequence_signals,
                step_configs,
                self.alarm_configs[relay_id]
            )
            self.sequence_executors[relay_id] = executor

            # Setup table
            table_widget.setRowCount(NUM_STEPS)
            table_widget.setColumnCount(2)
            table_widget.setHorizontalHeaderLabels(["BOX", "STAT"])

            combos = {}
            for step_num in range(1, NUM_STEPS + 1):
                row = step_num - 1

                step_label = QTableWidgetItem(f"Step {step_num}")
                step_label.setFlags(step_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table_widget.setVerticalHeaderItem(row, step_label)

                combo = QComboBox()
                combo.addItems(["0", "1", "2", "3", "4", "5", "6", "7", "8"])
                combo.setCurrentText("0")
                combo.currentTextChanged.connect(
                    partial(self.on_box_selection_changed, relay_id, step_num)
                )
                table_widget.setCellWidget(row, 0, combo)
                combos[step_num] = combo

                stat_label = QTableWidgetItem("IDLE")
                stat_label.setFlags(stat_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table_widget.setItem(row, 1, stat_label)

            table_widget.horizontalHeader().setStretchLastSection(True)
            table_widget.setMaximumWidth(250)
            self.table_combos[relay_id] = combos

            group_layout.addWidget(table_widget)
            
            # Cycle time display
            cycle_time_label = QLabel("Cycle Time: 00:00:00")
            cycle_time_label.setStyleSheet("font-size: 12pt; font-weight: bold; text-align: center; padding: 5px;")
            self.cycle_time_labels[relay_id] = cycle_time_label
            group_layout.addWidget(cycle_time_label)
            
            # Cycle counter display
            cycle_count_label = QLabel("Cycles: 0 pcs")
            cycle_count_label.setStyleSheet("font-size: 12pt; font-weight: bold; text-align: center; padding: 5px; color: #2196F3;")
            self.cycle_count_labels[relay_id] = cycle_count_label
            self.cycle_count[relay_id] = 0  # Initialize cycle counter
            self.total_cycle_time[relay_id] = 0  # Initialize total cycle time
            group_layout.addWidget(cycle_count_label)
            
            # Average cycle time display
            avg_cycle_time_label = QLabel("Avg: 00:00:00")
            avg_cycle_time_label.setStyleSheet("font-size: 12pt; font-weight: bold; text-align: center; padding: 5px; color: #006600;")
            self.avg_cycle_time_labels[relay_id] = avg_cycle_time_label
            group_layout.addWidget(avg_cycle_time_label)

            # Control buttons
            button_layout = QHBoxLayout()
            run_btn = QPushButton("Start")
            run_btn.clicked.connect(partial(self.on_start_sequence, relay_id))
            stop_btn = QPushButton("Stop")
            stop_btn.clicked.connect(partial(self.on_stop_sequence, relay_id))
            reset_btn = QPushButton("Reset")
            reset_btn.clicked.connect(partial(self.on_reset_table, relay_id))
            
            button_layout.addWidget(run_btn)
            button_layout.addWidget(stop_btn)
            button_layout.addWidget(reset_btn)
            group_layout.addLayout(button_layout)
            
            # Store button references for color changes
            self.cycle_time_buttons[relay_id] = {
                'start': run_btn,
                'stop': stop_btn,
                'reset': reset_btn
            }

            group_box.setLayout(group_layout)
            tables_layout.addWidget(group_box)

        main_layout.addLayout(tables_layout)
        self.monitor_widget.setLayout(main_layout)

    def setup_job_change_tab(self):
        """Setup Job Change tab"""
        self.job_change_widget = QWidget()
        layout = QVBoxLayout()

        # Job list
        job_group = QGroupBox("Available Jobs Models")
        job_layout = QVBoxLayout()

        self.job_combo = QComboBox()
        self.refresh_job_list()
        job_layout.addWidget(QLabel("Select Job Model:"))
        job_layout.addWidget(self.job_combo)

        # Load button
        load_btn = QPushButton("Load Job Model")
        load_btn.clicked.connect(self.on_load_job)
        job_layout.addWidget(load_btn)

        job_group.setLayout(job_layout)
        layout.addWidget(job_group)

        # Save current job section
        save_group = QGroupBox("Save Current Sequence as Job Model")
        save_layout = QVBoxLayout()

        self.job_name_input = QLineEdit()
        self.job_name_input.setPlaceholderText("Enter job Model name...")
        save_layout.addWidget(QLabel("Job Name:"))
        save_layout.addWidget(self.job_name_input)

        save_btn = QPushButton("Save Job Model")
        save_btn.clicked.connect(self.on_save_job)
        save_layout.addWidget(save_btn)

        save_group.setLayout(save_layout)
        layout.addWidget(save_group)

        layout.addStretch()
        self.job_change_widget.setLayout(layout)

    def setup_machine_data_tab(self):
        """Setup Machine Data tab for alarm settings"""
        self.machine_data_widget = QWidget()
        layout = QVBoxLayout()

        alarm_group = QGroupBox("Alarm Configuration (Unexpected DI Detection)")
        alarm_layout = QVBoxLayout()

        self.alarm_widgets = {}

        for config in RELAY_CONFIGS:
            relay_id = config['ip']
            relay_name = config['name']

            # Sub-group for each relay
            relay_group_layout = QHBoxLayout()
            relay_group_layout.addWidget(QLabel(f"{relay_name}:"))

            # Enable checkbox
            enable_check = QCheckBox("Enabled")
            enable_check.setChecked(self.alarm_configs[relay_id].enabled)
            enable_check.stateChanged.connect(
                partial(self.on_alarm_enabled_changed, relay_id)
            )
            relay_group_layout.addWidget(enable_check)

            # DO channel spinner
            do_spin = QSpinBox()
            do_spin.setRange(0, 8)
            do_spin.setValue(self.alarm_configs[relay_id].do_channel)
            do_spin.valueChanged.connect(
                partial(self.on_alarm_do_changed, relay_id)
            )
            relay_group_layout.addWidget(QLabel("Alarm DO:"))
            relay_group_layout.addWidget(do_spin)

            relay_group_layout.addStretch()
            alarm_layout.addLayout(relay_group_layout)

            self.alarm_widgets[relay_id] = {
                'enable': enable_check,
                'do_spin': do_spin
            }

        alarm_group.setLayout(alarm_layout)
        layout.addWidget(alarm_group)

        layout.addStretch()
        self.machine_data_widget.setLayout(layout)

    def on_alarm_enabled_changed(self, relay_id: str, state):
        """Handle alarm enable/disable"""
        if relay_id in self.alarm_widgets:
            enabled = self.alarm_widgets[relay_id]['enable'].isChecked()
            self.alarm_configs[relay_id].enabled = enabled
            AlarmManager.save_alarm_config(relay_id, self.alarm_configs[relay_id])
            if relay_id in self.sequence_executors:
                self.sequence_executors[relay_id].alarm_config = self.alarm_configs[relay_id]
            print(f"[{relay_id}] Alarm enabled: {enabled}")

    def on_alarm_do_changed(self, relay_id: str, value):
        """Handle alarm DO channel change"""
        if relay_id in self.alarm_widgets:
            do_channel = self.alarm_widgets[relay_id]['do_spin'].value()
            self.alarm_configs[relay_id].do_channel = do_channel
            AlarmManager.save_alarm_config(relay_id, self.alarm_configs[relay_id])
            if relay_id in self.sequence_executors:
                self.sequence_executors[relay_id].alarm_config = self.alarm_configs[relay_id]
            print(f"[{relay_id}] Alarm DO set to: {do_channel}")

    def refresh_job_list(self):
        """Refresh job combo box"""
        self.job_combo.clear()
        jobs = JobManager.list_jobs()
        self.job_combo.addItems(jobs)

    def on_save_job(self):
        """Save current sequence as job"""
        job_name = self.job_name_input.text().strip()
        if not job_name:
            QMessageBox.warning(self, "Warning", "Please enter a job name")
            return

        job = JobSequence(job_name)
        
        # Collect current sequences from all relays
        for relay_id in self.relay_clients.keys():
            if relay_id in self.sequence_executors:
                executor = self.sequence_executors[relay_id]
                job.relay_sequences[relay_id] = executor.step_configs[:]

        if JobManager.save_job(job):
            QMessageBox.information(self, "Success", f"Job '{job_name}' saved successfully")
            self.job_name_input.clear()
            self.refresh_job_list()
        else:
            QMessageBox.critical(self, "Error", "Failed to save job")

    def on_load_job(self):
        """Load selected job"""
        job_name = self.job_combo.currentText()
        if not job_name:
            QMessageBox.warning(self, "Warning", "Please select a job")
            return

        job = JobManager.load_job(job_name)
        if not job:
            QMessageBox.critical(self, "Error", "Failed to load job")
            return

        # Apply job sequences to all relays
        for relay_id in self.relay_clients.keys():
            if relay_id in job.relay_sequences:
                # Update executor
                executor = self.sequence_executors[relay_id]
                executor.step_configs = job.relay_sequences[relay_id][:]

                # Update table display
                if relay_id in self.table_combos:
                    for step_num in range(1, NUM_STEPS + 1):
                        box_num = job.relay_sequences[relay_id][step_num - 1]
                        combo = self.table_combos[relay_id][step_num]
                        combo.setCurrentText(str(box_num))

        self.current_job = job
        QMessageBox.information(self, "Success", f"Job '{job_name}' loaded successfully")

    def on_box_selection_changed(self, relay_id: str, step_num: int, box_num_str: str):
        """Handle BOX selection change"""
        try:
            box_num = int(box_num_str)
            if relay_id in self.sequence_executors:
                executor = self.sequence_executors[relay_id]
                executor.set_step_config(step_num, box_num)
        except Exception as e:
            print(f"Error setting box config: {e}")

    def on_start_sequence(self, relay_id: str):
        """Start the sequence for relay"""
        if relay_id not in self.sequence_executors:
            QMessageBox.warning(self, "Error", f"Relay {relay_id} not found")
            return

        executor = self.sequence_executors[relay_id]

        if executor.running:
            QMessageBox.warning(self, "Warning", "Sequence already running for this relay")
            return

        # Change Start button to green
        if relay_id in self.cycle_time_buttons:
            self.cycle_time_buttons[relay_id]['start'].setStyleSheet(
                "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 5px; }"
            )
        
        thread = Thread(target=executor.run, daemon=True)
        thread.start()
        print(f"[{relay_id}] Sequence started")

    def on_stop_sequence(self, relay_id: str):
        """Stop the sequence for relay"""
        if relay_id in self.sequence_executors:
            executor = self.sequence_executors[relay_id]
            executor.stop()
            
            # Change Stop button to red
            if relay_id in self.cycle_time_buttons:
                self.cycle_time_buttons[relay_id]['stop'].setStyleSheet(
                    "QPushButton { background-color: #FF6B6B; color: white; font-weight: bold; padding: 5px; }"
                )
                # Restore Start button to default color
                self.cycle_time_buttons[relay_id]['start'].setStyleSheet("")
            
            print(f"[{relay_id}] Sequence stopped")

    def on_reset_table(self, relay_id: str):
        """Reset all BOX selections for a table"""
        if relay_id not in self.table_combos:
            return

        for step_num in range(1, NUM_STEPS + 1):
            combo = self.table_combos[relay_id][step_num]
            combo.setCurrentText("0")

        # Reset status display
        if relay_id in self.table_widgets:
            table = self.table_widgets[relay_id]
            for row in range(NUM_STEPS):
                item = table.item(row, 1)
                if item:
                    item.setText("IDLE")
                    item.setBackground(QBrush(QColor("white")))
        
        # Reset cycle time and button colors
        if relay_id in self.cycle_time_buttons:
            # Reset cycle time label
            if relay_id in self.cycle_time_labels:
                self.cycle_time_labels[relay_id].setText("Cycle Time: 00:00:00")
            
            # Reset cycle counter
            if relay_id in self.cycle_count_labels:
                self.cycle_count[relay_id] = 0
                self.cycle_count_labels[relay_id].setText("Cycles: 0 pcs")
            
            # Reset average cycle time
            if relay_id in self.avg_cycle_time_labels:
                self.total_cycle_time[relay_id] = 0
                self.avg_cycle_time_labels[relay_id].setText("Avg: 00:00:00")
            
            # Restore button colors to default
            self.cycle_time_buttons[relay_id]['start'].setStyleSheet("")
            self.cycle_time_buttons[relay_id]['stop'].setStyleSheet("")
        
        # Clear cycle start time
        if relay_id in self.cycle_start_time:
            del self.cycle_start_time[relay_id]
        
        # Clear graph data for this relay
        if relay_id in self.graph_cycle_times:
            self.graph_cycle_times[relay_id] = {'timestamps': [], 'durations': []}
            self.update_graph()

    def _update_cycle_times(self):
        """Update cycle time display for all active tables"""
        from time import time
        
        # Check if any sequence is still running
        any_running = False
        
        for relay_id in self.cycle_start_time.keys():
            if relay_id in self.sequence_executors and self.sequence_executors[relay_id].running:
                any_running = True
                elapsed = time() - self.cycle_start_time[relay_id]
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                if relay_id in self.cycle_time_labels:
                    self.cycle_time_labels[relay_id].setText(f"Cycle Time: {time_str}")
        
        # Stop timer if no sequences are running
        if not any_running and self.cycle_timer is not None:
            self.cycle_timer.stop()
            self.cycle_timer = None
    
    def setup_signals(self):
        """Setup relay signals"""
        for relay_id in self.relay_signals.keys():
            self.relay_signals[relay_id].di_updated.connect(self.on_di_updated)
            self.relay_signals[relay_id].do_updated.connect(self.on_do_updated)
            self.relay_signals[relay_id].connection_status_changed.connect(
                self.on_connection_status_changed
            )

        self.sequence_signals.step_status_changed.connect(self.on_step_status_changed)
        self.sequence_signals.unexpected_di.connect(self.on_unexpected_di)

    def on_di_updated(self, relay_id: str, states: List[bool]):
        """Update DI states"""
        if relay_id in self.relay_states:
            self.relay_states[relay_id]['di'] = states
            if relay_id in self.sequence_executors:
                self.sequence_executors[relay_id].update_relay_states(
                    states,
                    self.relay_states[relay_id]['do']
                )
            # Update manual tab
            self.on_manual_di_updated(relay_id, states)

    def on_do_updated(self, relay_id: str, states: List[bool]):
        """Update DO states"""
        if relay_id in self.relay_states:
            self.relay_states[relay_id]['do'] = states
            if relay_id in self.sequence_executors:
                self.sequence_executors[relay_id].update_relay_states(
                    self.relay_states[relay_id]['di'],
                    states
                )
            # Update manual tab
            self.on_manual_do_updated(relay_id, states)

    def on_connection_status_changed(self, relay_id: str, connected: bool):
        """Handle connection status change"""
        if relay_id in self.relay_states:
            self.relay_states[relay_id]['connected'] = connected
            status = "Connected ✓" if connected else "Disconnected ✗"
            print(f"[{relay_id}] {status}")
            # Update manual tab
            self.on_manual_connection_status_changed(relay_id, connected)

    def on_step_status_changed(self, relay_id: str, step_num: int, status: str):
        """Update step status in table and manage cycle time"""
        if relay_id not in self.table_widgets:
            return

        row = step_num - 1
        table = self.table_widgets[relay_id]

        # Cycle time management: start at Step 1 SIGNAL (actual execution)
        if step_num == 1 and status == 'SIGNAL':
            # Step 1 has started - begin cycle time counting
            from time import time
            if relay_id not in self.cycle_start_time:
                self.cycle_start_time[relay_id] = time()
                
                # Start cycle time update timer if not already running
                if self.cycle_timer is None:
                    self.cycle_timer = QTimer()
                    self.cycle_timer.timeout.connect(self._update_cycle_times)
                    self.cycle_timer.start(100)  # Update every 100ms
                
                print(f"[{relay_id}] Cycle started at Step 1")
        
        # Detect if this is the last configured step
        executor = self.sequence_executors.get(relay_id)
        if executor:
            # Find the last configured step (box_num != 0)
            last_configured_step = 0
            for i in range(NUM_STEPS - 1, -1, -1):
                if executor.step_configs[i] != 0:
                    last_configured_step = i + 1  # Convert to 1-based
                    break
            
            # When last configured step completes with OK status
            if step_num == last_configured_step and status == 'OK':
                # Calculate cycle time elapsed
                from time import time
                if relay_id in self.cycle_start_time:
                    cycle_time = time() - self.cycle_start_time[relay_id]
                    self.total_cycle_time[relay_id] = self.total_cycle_time.get(relay_id, 0) + cycle_time
                else:
                    cycle_time = 0
                
                # Increment cycle counter
                self.cycle_count[relay_id] = self.cycle_count.get(relay_id, 0) + 1
                if relay_id in self.cycle_count_labels:
                    self.cycle_count_labels[relay_id].setText(f"Cycles: {self.cycle_count[relay_id]} pcs")
                
                # Calculate and display average cycle time
                if self.cycle_count[relay_id] > 0:
                    avg_time = self.total_cycle_time[relay_id] / self.cycle_count[relay_id]
                    avg_hours = int(avg_time // 3600)
                    avg_minutes = int((avg_time % 3600) // 60)
                    avg_seconds = int(avg_time % 60)
                    avg_time_str = f"{avg_hours:02d}:{avg_minutes:02d}:{avg_seconds:02d}"
                    
                    if relay_id in self.avg_cycle_time_labels:
                        self.avg_cycle_time_labels[relay_id].setText(f"Avg: {avg_time_str}")
                
                # Reset cycle time for next cycle
                if relay_id in self.cycle_start_time:
                    del self.cycle_start_time[relay_id]
                if relay_id in self.cycle_time_labels:
                    self.cycle_time_labels[relay_id].setText("Cycle Time: 00:00:00")
                
                # Add to graph data
                if relay_id in self.graph_cycle_times:
                    self.graph_cycle_times[relay_id]['timestamps'].append(dt.now())
                    self.graph_cycle_times[relay_id]['durations'].append(cycle_time)
                    self.update_graph()
                
                print(f"[{relay_id}] Cycle completed at Step {last_configured_step}. Total cycles: {self.cycle_count[relay_id]}, Avg time: {avg_time_str}")        
        # Update step status display
        if row < table.rowCount():
            item = table.item(row, 1)
            if item:
                item.setText(status)

                # Color code the status
                if status == 'OK':
                    item.setBackground(QBrush(QColor("#00AA00")))
                elif status == 'WAIT' or status == 'WAIT_OFF':
                    item.setBackground(QBrush(QColor("#FFFF00")))
                elif status == 'SIGNAL':
                    item.setBackground(QBrush(QColor("#00CCFF")))
                elif status == 'ERROR':
                    item.setBackground(QBrush(QColor("#FF0000")))
                elif status == 'SKIP':
                    item.setBackground(QBrush(QColor("#CCCCCC")))
                else:
                    item.setBackground(QBrush(QColor("white")))

    def on_unexpected_di(self, relay_id: str, di_channel: int):
        """Handle unexpected DI detection"""
        # Mark alarm as active
        self.active_alarms[relay_id] = True
        
        # Update Alarm tab UI
        if relay_id in self.alarm_reset_buttons:
            self.alarm_reset_buttons[relay_id]['status'].setText(f"Alarm Active - DI{di_channel}")
            self.alarm_reset_buttons[relay_id]['status'].setStyleSheet("color: red; font-weight: bold;")
            self.alarm_reset_buttons[relay_id]['button'].setEnabled(True)
        
        alarm_config = self.alarm_configs.get(relay_id)
        alarm_info = f"No alarm configured"
        if alarm_config and alarm_config.enabled and alarm_config.do_channel > 0:
            alarm_info = f"Alarm sent to DO{alarm_config.do_channel}"
        
        print(f"[{relay_id}] Unexpected DI detected on channel DI{di_channel} - {alarm_info}")
        
        # Switch to Alarm tab automatically
        alarm_tab_index = self.tab_widget.indexOf(self.alarm_widget)
        if alarm_tab_index >= 0:
            self.tab_widget.setCurrentIndex(alarm_tab_index)

    def on_manual_do_button_clicked(self, relay_id: str, index: int):
        """Handle manual relay button click"""
        new_state = not self.relay_states[relay_id]['do'][index]
        channel = index + 1

        # Send DO command in background thread
        thread = Thread(
            target=self._write_relay_manual,
            args=(relay_id, channel, new_state),
            daemon=True
        )
        thread.start()

    def _write_relay_manual(self, relay_id: str, channel: int, value: bool):
        """Write relay state in manual mode"""
        try:
            success = self.relay_clients[relay_id].write_digital_output(channel, value)
            if success:
                print(f"[{relay_id}] Manual control: CH{channel} set to {'ON' if value else 'OFF'}")
            else:
                print(f"[{relay_id}] Failed to set CH{channel}")
        except Exception as e:
            print(f"[{relay_id}] Error in manual control: {e}")

    def on_manual_di_updated(self, relay_id: str, states: List[bool]):
        """Update manual tab DI display"""
        if relay_id in self.manual_ui_di_indicators:
            for i, indicator in enumerate(self.manual_ui_di_indicators[relay_id]):
                if i < len(states):
                    state = states[i]
                    indicator.setText(f"DI{i+1}: {'ON' if state else 'OFF'}")
                    color = "#00AA00" if state else "#CCCCCC"
                    text_color = "white" if state else "black"
                    indicator.setStyleSheet(
                        f"background-color: {color}; color: {text_color}; padding: 5px; font-size: 9px; font-weight: bold;"
                    )

    def on_manual_do_updated(self, relay_id: str, states: List[bool]):
        """Update manual tab DO display"""
        if relay_id in self.manual_ui_do_indicators:
            for i, indicator in enumerate(self.manual_ui_do_indicators[relay_id]):
                if i < len(states):
                    state = states[i]
                    indicator.setText(f"CH{i+1}: {'ON' if state else 'OFF'}")
                    color = "#00AA00" if state else "#CCCCCC"
                    text_color = "white" if state else "black"
                    indicator.setStyleSheet(
                        f"background-color: {color}; color: {text_color}; padding: 5px; font-size: 9px; font-weight: bold;"
                    )
                    # Also update button appearance
                    if i < len(self.manual_ui_do_buttons[relay_id]):
                        btn = self.manual_ui_do_buttons[relay_id][i]
                        btn.setStyleSheet(
                            f"background-color: {color}; color: {text_color}; font-weight: bold;"
                        )

    def on_manual_connection_status_changed(self, relay_id: str, connected: bool):
        """Update manual tab connection status"""
        if relay_id in self.manual_ui_connection_labels:
            label = self.manual_ui_connection_labels[relay_id]
            if connected:
                label.setText("Connected \u2713")
                label.setStyleSheet("color: green; font-weight: bold;")
            else:
                label.setText("Disconnected \u2717")
                label.setStyleSheet("color: red; font-weight: bold;")

    def start_polling(self):
        """Start polling threads"""
        self.polling_active = True
        for relay_id in self.relay_clients.keys():
            thread = Thread(target=self._polling_loop, args=(relay_id,), daemon=True)
            self.polling_threads[relay_id] = thread
            thread.start()

    def _polling_loop(self, relay_id: str):
        """Main polling loop for relay"""
        while self.polling_active:
            try:
                client = self.relay_clients[relay_id]
                signals = self.relay_signals[relay_id]
                was_connected = self.relay_states[relay_id]['connected']

                if not client.is_connected():
                    if was_connected:
                        signals.connection_status_changed.emit(relay_id, False)
                    if not client.connect():
                        sleep(UPDATE_INTERVAL / 1000.0)
                        continue

                di_states = client.read_digital_inputs()
                if di_states:
                    signals.di_updated.emit(relay_id, di_states)
                else:
                    if was_connected:
                        signals.connection_status_changed.emit(relay_id, False)

                do_states = client.read_digital_outputs()
                if do_states:
                    signals.do_updated.emit(relay_id, do_states)
                    if not was_connected:
                        signals.connection_status_changed.emit(relay_id, True)

                sleep(UPDATE_INTERVAL / 1000.0)

            except Exception as e:
                print(f"Polling error for {relay_id}: {e}")
                if relay_id in self.relay_clients:
                    self.relay_clients[relay_id].disconnect()
                sleep(UPDATE_INTERVAL / 1000.0)

    def closeEvent(self, event):
        """Handle window close"""
        self.polling_active = False
        for executor in self.sequence_executors.values():
            executor.stop()
        for relay_id in self.relay_clients.keys():
            self.relay_clients[relay_id].disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = PokayokeTableWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


def main():
    app = QApplication(sys.argv)
    window = PokayokeTableWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
