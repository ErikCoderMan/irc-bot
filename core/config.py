import json
from pathlib import Path

''' Project paths '''

# Project root (…/project)
ROOT_DIR = Path(__file__).parent.parent

# Config files
CREDENTIALS_FILE = ROOT_DIR / "credentials.json"
SETTINGS_FILE = ROOT_DIR / "settings.json"

# Data files
NOTES_FILE = ROOT_DIR / "notes.json"

# Log files
LOG_FILE = ROOT_DIR / "bot.log"
CHAT_LOG_FILE = ROOT_DIR / "chat.log"


''' Config loading '''

credentials: dict = {}
settings: dict = {}


def load_json(file_path: Path) -> dict:
    # Load JSON from a file and return it as a dictionary.
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        raise FileNotFoundError(f"Missing file: {file_path}")

    except json.JSONDecodeError as e:
        # Wrap JSON error to make it clear which file is broken
        raise ValueError(f"Invalid JSON in {file_path}") from e


''' Load credentials '''

credentials = load_json(CREDENTIALS_FILE)

# Validate required credential fields
required_fields = ["server", "port", "channel", "nickname"]
missing = [field for field in required_fields if not credentials.get(field)]
if missing:
    raise ValueError(
        f"Missing required credential fields: {', '.join(missing)}"
    )

# Ensure use_ssl exists
if "use_ssl" not in credentials:
    # Fallback: assume SSL if using default SSL port
    credentials["use_ssl"] = credentials.get("port") == 6697


''' Load settings '''

settings = load_json(SETTINGS_FILE)


''' Helpers '''

def is_command_enabled(command_name: str) -> bool:
    # Return True if the command is not listed in disabled_commands.
    return command_name not in settings.get("disabled_commands", [])
