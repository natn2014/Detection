#!/bin/bash

# Navigate to the desired directory
cd /home/jetson/detection/Detection/Wireharness || {
    echo "Failed to change directory. Exiting."
    exit 1
}

# Run the Python script
python main.py
