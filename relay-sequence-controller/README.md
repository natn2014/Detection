# Relay Sequence Controller

## Overview
The Relay Sequence Controller is a Python application designed to manage and control relay sequences through a user-friendly interface. It allows users to define sequences based on digital inputs and outputs, providing flexibility for various automation tasks.

## Project Structure
```
relay-sequence-controller
├── src
│   ├── main.py                # Entry point of the application
│   ├── relay_b.py             # Relay hardware interaction
│   ├── ui                     # User interface components
│   │   ├── __init__.py        # UI package initializer
│   │   ├── main_window.py      # Main window UI
│   │   └── sequence_dialog.py  # Sequence configuration dialog
│   ├── models                 # Data models
│   │   ├── __init__.py        # Models package initializer
│   │   └── sequence.py         # Sequence data model
│   └── utils                  # Utility functions
│       ├── __init__.py        # Utils package initializer
│       └── config_manager.py   # Configuration file management
├── configs
│   └── default_config.json     # Default configuration settings
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Features
- **User Interface**: A graphical interface for managing relay sequences.
- **Sequence Configuration**: Ability to add, edit, and remove sequences.
- **Relay Control**: Direct interaction with relay hardware to control digital outputs based on defined sequences.
- **Configuration Management**: Load and save configuration settings to a JSON file.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd relay-sequence-controller
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```
   python src/main.py
   ```
2. Use the interface to configure sequences and control the relay outputs.

## Configuration
The application uses a JSON configuration file to store user-defined sequences and settings. The default configuration can be found in `configs/default_config.json`. Users can modify this file or save their configurations through the application interface.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.