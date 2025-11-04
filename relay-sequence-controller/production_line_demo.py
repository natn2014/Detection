#!/usr/bin/env python3
"""
Production Line Demo Script
Demonstrates the new sensor-driven manufacturing control system.
"""

import sys
import os
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import MainWindow
from PySide6.QtWidgets import QApplication

def create_demo_sequences():
    """Create demonstration sequences for a typical production line."""
    
    sequences = [
        {
            "type": "station",
            "operation_type": "Part Detection & Process",
            "part_sensor": 1,      # Part arrival sensor
            "process_device": 1,   # Clamping device
            "feedback_sensor": 2,  # Clamp position sensor
            "skip_sensor": 3,      # Part defect sensor
            "timeout": 10,
            "duration": 3,         # Clamp for 3 seconds
            "blink_mode": False,
            "initial_states": {},
            "end_states": {}
        },
        {
            "type": "station", 
            "operation_type": "Sequential Operation",
            "part_sensor": 2,      # Part in position sensor
            "process_device": 2,   # Drilling machine
            "feedback_sensor": 4,  # Drill completion sensor
            "skip_sensor": 5,      # Skip if clamp failed
            "timeout": 15,
            "duration": 0,         # Wait for feedback
            "blink_mode": True,    # Visual indicator
            "initial_states": {},
            "end_states": {}
        },
        {
            "type": "production_line",
            "steps": "PART_DI3->INSPECT_DO3:2s\nINSPECT_COMPLETE_DI6->PASS_DI7|FAIL_DI8->SORT_DO4\nSORT_COMPLETE_DI9->TRANSFER_DO5:3s",
            "return_to_initial": False,
            "initial_states": {},
            "end_states": {}
        },
        {
            "type": "station",
            "operation_type": "Safety Interlock", 
            "part_sensor": 8,      # Emergency stop sensor (inverted)
            "process_device": 8,   # Alarm/Warning device
            "feedback_sensor": 7,  # Reset button
            "skip_sensor": 6,      # Not used for safety
            "timeout": 5,
            "duration": 0,         # Continuous until reset
            "blink_mode": True,    # Blinking alarm
            "initial_states": {},
            "end_states": {}
        }
    ]
    
    return sequences

def simulate_production_cycle():
    """Simulate a production cycle with sensor triggers."""
    print("\n" + "="*60)
    print("PRODUCTION LINE SIMULATION")
    print("="*60)
    print("This demo shows how the new system works:")
    print()
    print("STATION 1 (Clamping):")
    print("  - Part arrives → DI1 triggered")
    print("  - Clamp activates → DO1 ON") 
    print("  - Clamp confirms → DI2 triggered")
    print("  - If defect detected → DI3 skips process")
    print()
    print("STATION 2 (Drilling):") 
    print("  - Part in position → DI2 triggered")
    print("  - Drill starts → DO2 ON (blinking)")
    print("  - Drill completes → DI4 triggered")
    print("  - Process stops → DO2 OFF")
    print()
    print("STATION 3 (Quality & Sort):")
    print("  - Part enters → DI3 triggered")
    print("  - Inspection → DO3 ON for 2s")
    print("  - Pass/Fail → DI7 or DI8 triggered")
    print("  - Sort mechanism → DO4 activates")
    print()
    print("SAFETY SYSTEM:")
    print("  - Emergency stop → DI8 OFF (inverted)")
    print("  - Alarm activates → DO8 blinking")
    print("  - Reset required → DI7 to clear")
    print()
    print("Key Benefits:")
    print("✓ Real sensor feedback - no blind timing")
    print("✓ Error handling - skip defective parts") 
    print("✓ Safety interlocks - immediate response")
    print("✓ Production tracking - complete visibility")
    print("✓ Flexible reconfiguration - easy setup changes")

def main():
    """Run the production line demo."""
    print("Starting Production Line Relay Controller Demo...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Load demo sequences
    demo_sequences = create_demo_sequences()
    
    print(f"\nLoading {len(demo_sequences)} demo sequences...")
    
    for i, seq in enumerate(demo_sequences):
        window.sequences.append(seq)
        window.add_sequence_to_ui(seq, enabled=True)
    
    print("Demo sequences loaded!")
    print("\nSequence Overview:")
    print("1. Clamping Station - Part detection with clamp feedback")
    print("2. Drilling Station - Sequential operation with visual indicator") 
    print("3. Quality Control - Multi-step inspection and sorting")
    print("4. Safety System - Emergency stop with alarm")
    
    # Show simulation info
    simulate_production_cycle()
    
    print(f"\n{'='*60}")
    print("Open the application to:")
    print("• View the configured production stations")
    print("• Monitor real-time sequence status")
    print("• Test with actual relay hardware")
    print("• Check DI/DO states with new inspection tools")
    print("• Configure your own production sequences")
    print(f"{'='*60}")
    
    # Show the application
    window.show()
    
    return app.exec()

if __name__ == '__main__':
    main()
