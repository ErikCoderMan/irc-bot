import tomllib
from pathlib import Path

''' Project paths '''

# Project root (…/project)
ROOT_DIR = Path(__file__).parent.parent

# Config file
CONFIG_FILE = ROOT_DIR / "config.toml"

# Data dir
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok = True)

# Logs dir
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok = True)

''' Config loading '''

with open(CONFIG_FILE, "rb") as f:
    config = tomllib.load(f)


''' Validate required values in config irc field '''

required = ["server", "port", "channel", "nickname"]
missing = [key for key in required if config["irc"].get(key) is None]
if missing:
    raise ValueError(
        f"Missing required config values: {', '.join(missing)}"
    )

# Ensure use_ssl exists
if "use_ssl" not in config["irc"]:
    # Fallback: assume SSL if using default SSL port
    config["irc"]["use_ssl"] = config["irc"].get("port") == 6697


''' Helpers '''

enabled_commands = []
for key, value in config["commands"].items():
    if value is True:
        enabled_commands.append(key)


def is_command_enabled(command_name: str) -> bool:
    # Return True if the command is enabled or False if not
    return bool(config["commands"].get(command_name, False))
    
