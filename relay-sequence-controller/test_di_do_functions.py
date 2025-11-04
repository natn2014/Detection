#!/usr/bin/env python3
"""
Test script to demonstrate the new DI/DO checking functionality.
This script shows how to use the new functions programmatically.
"""

import sys
import os

# Add the src directory to the path so we can import the main module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import MainWindow
from PySide6.QtWidgets import QApplication

def test_di_do_functions():
    """Test the new DI/DO checking functions."""
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Give the relay a moment to connect
    app.processEvents()
    
    print("Testing DI/DO Check Functions")
    print("=" * 40)
    
    # Test individual DI channel checking
    print("\n1. Checking individual DI channels:")
    for channel in range(1, 9):
        state = window.check_di_channel(channel)
        print(f"   DI{channel}: {'ON' if state else 'OFF'}")
    
    # Test getting all DI states at once
    print("\n2. Getting all DI states:")
    all_di_states = window.get_all_di_states()
    for channel, state in all_di_states.items():
        print(f"   DI{channel}: {'ON' if state else 'OFF'}")
    
    # Test individual DO channel checking
    print("\n3. Checking individual DO channels:")
    for channel in range(1, 9):
        state = window.check_do_channel(channel)
        print(f"   DO{channel}: {'ON' if state else 'OFF'}")
    
    # Test getting all DO states at once
    print("\n4. Getting all DO states:")
    all_do_states = window.get_all_do_states()
    for channel, state in all_do_states.items():
        print(f"   DO{channel}: {'ON' if state else 'OFF'}")
    
    # Test error handling with invalid channels
    print("\n5. Testing error handling:")
    print(f"   DI0 (invalid): {window.check_di_channel(0)}")
    print(f"   DI9 (invalid): {window.check_di_channel(9)}")
    print(f"   DO0 (invalid): {window.check_do_channel(0)}")
    print(f"   DO9 (invalid): {window.check_do_channel(9)}")
    
    print("\nTest complete! Check the application log for detailed messages.")
    
    # Show the window for interactive testing
    window.show()
    
    return app.exec()

if __name__ == '__main__':
    test_di_do_functions()
