import json
from core.paths import CREDENTIALS_FILE, SETTINGS_FILE

# Global dictionaries
credentials = {}
settings = {}

def load_json(file_path):
    # Load JSON from a file and return as a dict.
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing file: {file_path}")
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")

# Load credentials
credentials = load_json(CREDENTIALS_FILE)

# Validate required credential fields
required_fields = ["server", "port", "channel", "nickname"]
missing = [f for f in required_fields if not credentials.get(f)]
if missing:
    raise ValueError(f"Missing required credential fields: {', '.join(missing)}")

# Load settings
settings = load_json(SETTINGS_FILE)

# Helper to check if a command is enabled
def is_command_enabled(command_name: str) -> bool:
    # Return True if the command is not listed in disabled_commands.
    return command_name not in settings.get("disabled_commands", [])
