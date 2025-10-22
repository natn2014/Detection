import json
from pathlib import Path

# Configuration file path
CONFIG_DIR = Path.home() / '.relay_controller'
CONFIG_FILE = CONFIG_DIR / 'sequences.json'

def load_config():
    """Load configuration from file."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            print(f"Config file not found: {CONFIG_FILE}")
    except Exception as e:
        print(f"Error loading config: {e}")
    return None

def save_config(config):
    """Save configuration to file."""
    try:
        # Create directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"Configuration saved to: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False