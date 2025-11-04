# filepath: /relay-sequence-controller/relay-sequence-controller/src/ui/sequence_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QSpinBox, QDialogButtonBox, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QCheckBox, QGroupBox
import json
import os

class SequenceDialog(QDialog):
    def __init__(self, parent=None, edit_sequence=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Sequence" if edit_sequence else "Add Sequence")
        self.setModal(True)
        self.resize(600, 600)
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
            "• Turn ON with duration: DI1->DO2:5s\n"
            "• Turn ON: DI1->DO2(ON)\n"
            "• Turn OFF: DI1->DO2(OFF)\n"
            "• Multiple actions: DI1&DO2(ON)->DO2(OFF)&DO3(ON):5s\n"
            "• Conditions: DI1&DI2, DI1|DI2, DI1&DO2(ON)"
        )
        info_label.setStyleSheet("color: #666; font-size: 9pt;")
        multi_layout.addWidget(info_label)
        
        self.steps_text = QTextEdit()
        self.steps_text.setPlaceholderText(
            "Examples:\n"
            "DI1->DO2(ON):5s\n"
            "DI2->DO3(ON)\n"
            "DI1&DO2(ON)->DO2(OFF)&DO3(ON)\n"
            "DO3(ON)->DO1(OFF)"
        )
        self.steps_text.setMaximumHeight(150)
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
                initial_combo = self.state_table.cellWidget(do_ch - 1, 1)
                initial_combo.setCurrentText("ON" if state else "OFF")
        
        # Load end states
        if seq.get('end_states'):
            for do_ch, state in seq['end_states'].items():
                end_combo = self.state_table.cellWidget(do_ch - 1, 2)
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

    def save_sequence(self, file_path):
        """Save the current sequence configuration to a file."""
        sequence_data = self.get_sequence()
        with open(file_path, 'w') as f:
            json.dump(sequence_data, f, indent=4)

    def load_sequence_from_file(self, file_path):
        """Load sequence configuration from a file."""
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                sequence_data = json.load(f)
                self.load_sequence(sequence_data)