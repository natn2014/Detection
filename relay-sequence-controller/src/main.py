import sys
import time
import json
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
                                QDialog, QLabel, QComboBox, QSpinBox, QDialogButtonBox,
                                QGroupBox, QCheckBox, QListWidget, QTextEdit, QTableWidget,
                                QTableWidgetItem, QHeaderView)
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
        self.type_combo.addItems(["Simple Logic", "Multi-Step Sequence"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Simple Logic Group
        self.simple_group = QGroupBox("Simple Logic Configuration")
        simple_layout = QVBoxLayout()
        
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(["Single DI", "AND Gate", "OR Gate"])
        self.logic_combo.currentTextChanged.connect(self.on_logic_changed)
        simple_layout.addWidget(QLabel("Logic Type:"))
        simple_layout.addWidget(self.logic_combo)
        
        self.di1_spin = QSpinBox()
        self.di1_spin.setRange(1, 8)
        self.di1_spin.setValue(1)
        simple_layout.addWidget(QLabel("DI Channel 1:"))
        simple_layout.addWidget(self.di1_spin)
        
        self.di2_label = QLabel("DI Channel 2:")
        self.di2_spin = QSpinBox()
        self.di2_spin.setRange(1, 8)
        self.di2_spin.setValue(2)
        simple_layout.addWidget(self.di2_label)
        simple_layout.addWidget(self.di2_spin)
        
        self.di2_label.hide()
        self.di2_spin.hide()
        
        self.do_spin = QSpinBox()
        self.do_spin.setRange(1, 8)
        self.do_spin.setValue(1)
        simple_layout.addWidget(QLabel("DO Channel:"))
        simple_layout.addWidget(self.do_spin)
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(0, 3600)
        self.duration_spin.setValue(5)
        self.duration_spin.setSuffix(" sec")
        simple_layout.addWidget(QLabel("ON Duration (0 = toggle):"))
        simple_layout.addWidget(self.duration_spin)
        
        self.simple_group.setLayout(simple_layout)
        layout.addWidget(self.simple_group)
        
        # Multi-Step Group
        self.multi_group = QGroupBox("Multi-Step Sequence Configuration")
        multi_layout = QVBoxLayout()
        
        multi_layout.addWidget(QLabel("Advanced Step Format:"))
        info_label = QLabel(
            "• Turn ON with duration: DI1->DO2(ON):5s\n"
            "• Turn ON: DI1->DO2(ON)\n"
            "• Turn OFF: DI1->DO2(OFF)\n"
            "• Wait/Delay: DI1->WAIT:3s\n"
            "• Multiple actions: DI1&DO2(ON)->DO2(OFF)&DO3(ON):5s\n"
            "• With wait: DI1->DO2(ON)->WAIT:2s->DO3(ON)\n"
            "• Conditions: DI1&DI2, DI1|DI2, DI1&DO2(ON)"
        )
        info_label.setStyleSheet("color: #666; font-size: 9pt;")
        multi_layout.addWidget(info_label)
        
        self.steps_text = QTextEdit()
        self.steps_text.setPlaceholderText(
            "Examples:\n"
            "DI1->DO2(ON):5s\n"
            "DI2->WAIT:3s\n"
            "DI1->DO2(ON)\n"
            "WAIT:2s\n"
            "DI3->DO3(OFF)\n"
            "DI1&DO2(ON)->DO2(OFF)&DO3(ON)\n"
            "DO3(ON)->WAIT:5s->DO1(OFF)"
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
        if seq['type'] == 'simple':
            self.type_combo.setCurrentText("Simple Logic")
            self.logic_combo.setCurrentText(seq['logic'])
            self.di1_spin.setValue(seq['di1'])
            if seq['di2']:
                self.di2_spin.setValue(seq['di2'])
            self.do_spin.setValue(seq['do'])
            self.duration_spin.setValue(seq['duration'])
        else:
            self.type_combo.setCurrentText("Multi-Step Sequence")
            self.steps_text.setPlainText(seq['steps'])
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
        """Toggle between simple and multi-step configuration."""
        is_multi = text == "Multi-Step Sequence"
        self.simple_group.setVisible(not is_multi)
        self.multi_group.setVisible(is_multi)
    
    def on_logic_changed(self, text):
        """Show/hide second DI input based on logic type."""
        show_di2 = text in ["AND Gate", "OR Gate"]
        self.di2_label.setVisible(show_di2)
        self.di2_spin.setVisible(show_di2)
    
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
        
        if self.type_combo.currentText() == "Simple Logic":
            base_seq.update({
                'type': 'simple',
                'logic': self.logic_combo.currentText(),
                'di1': self.di1_spin.value(),
                'di2': self.di2_spin.value() if self.logic_combo.currentText() in ["AND Gate", "OR Gate"] else None,
                'do': self.do_spin.value(),
                'duration': self.duration_spin.value()
            })
        else:
            base_seq.update({
                'type': 'multi',
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
        for i in range(1, 9):
            item = QTreeWidgetItem([f"DI {i}", "OFF", "Never ON"])
            self.di_tree.addTopLevelItem(item)
        di_layout.addWidget(self.di_tree)
        
        di_btn_layout = QHBoxLayout()
        reset_di_history_btn = QPushButton("Reset DI History")
        reset_di_history_btn.clicked.connect(self.reset_di_history)
        di_btn_layout.addWidget(reset_di_history_btn)
        di_layout.addLayout(di_btn_layout)
        
        di_group.setLayout(di_layout)
        left_layout.addWidget(di_group)
        
        # DO Status Tree
        do_group = QGroupBox("Digital Output Status")
        do_layout = QVBoxLayout()
        self.do_tree = QTreeWidget()
        self.do_tree.setHeaderLabels(["Channel", "Status", "History"])
        self.do_tree.setMaximumHeight(200)
        for i in range(1, 9):
            item = QTreeWidgetItem([f"DO {i}", "OFF", "Never ON"])
            self.do_tree.addTopLevelItem(item)
        do_layout.addWidget(self.do_tree)
        
        do_btn_layout = QHBoxLayout()
        reset_do_history_btn = QPushButton("Reset DO History")
        reset_do_history_btn.clicked.connect(self.reset_do_history)
        do_btn_layout.addWidget(reset_do_history_btn)
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
        
        if seq['type'] == 'simple':
            di_text = f"DI{seq['di1']}"
            if seq.get('di2'):
                di_text += f" & DI{seq['di2']}" if seq['logic'] == "AND Gate" else f" | DI{seq['di2']}"
            config_parts.append(f"{seq['logic']}: {di_text} -> DO{seq['do']} ({seq['duration']}s)")
        else:
            config_parts.append(seq['steps'].replace('\n', '; '))
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
            
            if updated_seq['type'] == 'simple':
                di_text = f"DI{updated_seq['di1']}"
                if updated_seq.get('di2'):
                    di_text += f" & DI{updated_seq['di2']}" if updated_seq['logic'] == "AND Gate" else f" | DI{updated_seq['di2']}"
                config_parts.append(f"{updated_seq['logic']}: {di_text} -> DO{updated_seq['do']} ({updated_seq['duration']}s)")
            else:
                config_parts.append(updated_seq['steps'].replace('\n', '; '))
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
                seq_key = f"multi_{seq_id}"
                if seq_key in self.multi_step_states:
                    del self.multi_step_states[seq_key]
                # Clear wait timers
                wait_key = f"wait_{seq_id}"
                if wait_key in self.wait_timers:
                    del self.wait_timers[wait_key]
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
            self.relay = Relay(host='192.168.1.254')
            self.relay.connect()
            self.status_label.setText("Connected to relay at 192.168.1.254")
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
            for wait_key, (wait_end_time, seq_id) in self.wait_timers.items():
                if current_time >= wait_end_time:
                    self.log_event(f"Sequence {seq_id}: Wait completed")
                    waits_to_remove.append(wait_key)
                    # Advance to next step
                    multi_key = f"multi_{seq_id}"
                    if multi_key in self.multi_step_states:
                        self.multi_step_states[multi_key]['waiting'] = False
            
            for key in waits_to_remove:
                del self.wait_timers[key]
            
            # Process sequences
            self.process_sequences(di_mask)
            
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
            
            if seq['type'] == 'simple':
                self.process_simple_sequence(seq, di_mask, i)
            else:
                self.process_multi_sequence(seq, di_mask, i)
    
    def process_simple_sequence(self, seq, di_mask, seq_id):
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
        
        if trigger and seq_key not in self.active_sequences:
            self.relay.on(do_ch)
            self.log_event(f"Sequence {seq_id}: DO{do_ch} turned ON")
            if seq['duration'] > 0:
                # Schedule turn off
                self.active_sequences[seq_key] = time.time() + seq['duration']
        
        # Check for timed turn-off
        if seq_key in self.active_sequences:
            if time.time() >= self.active_sequences[seq_key]:
                self.relay.off(do_ch)
                self.log_event(f"Sequence {seq_id}: DO{do_ch} turned OFF (timer)")
                del self.active_sequences[seq_key]
    
    def process_multi_sequence(self, seq, di_mask, seq_id):
        """Process multi-step sequence with wait functionality."""
        steps = seq['steps'].strip().split('\n')
        seq_key = f"multi_{seq_id}"
        
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
                    # Parse wait duration
                    duration_str = step.split(':', 1)[1].strip()
                    if duration_str.endswith('s'):
                        try:
                            wait_duration = int(duration_str[:-1])
                            wait_key = f"wait_{seq_id}"
                            self.wait_timers[wait_key] = (time.time() + wait_duration, seq_id)
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
                # Check if action is WAIT
                if action.upper().startswith('WAIT:'):
                    duration_str = action.split(':', 1)[1].strip()
                    if duration_str.endswith('s'):
                        try:
                            wait_duration = int(duration_str[:-1])
                            wait_key = f"wait_{seq_id}"
                            self.wait_timers[wait_key] = (time.time() + wait_duration, seq_id)
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
        
        # Split multiple actions by &
        actions = [a.strip() for a in action_str.split('&')]
        
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
        
        # Check for state specification: DO2(ON) or DO2(OFF)
        if '(' in input_str and ')' in input_str:
            base_part, state_part = input_str.split('(', 1)
            base_part = base_part.strip()
            state_part = state_part.replace(')', '').strip()
            
            if base_part.startswith('DO'):
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

