from pathlib import Path
import tomlkit

# Paths
ROOT_DIR = Path(__file__).parent
CONFIG_FILE = ROOT_DIR / "config.toml"
LOGS_DIR = ROOT_DIR / "logs"
DATA_DIR = ROOT_DIR / "data"

# Default config
DEFAULT_CONFIG = {
    "irc": {
        "server": "irc.exampleserver.com",
        "port": 6697,
        "channel": "#examplechannel",
        "nickname": "examplebot",
        "use_ssl": True,
    },
    "bot": {
        "command_prefix": "!",
        "allow_whispers": False,
    },
    "notes": {
        "max_notes": 50,
        "max_note_length": 200,
    },
    "logging": {
        "console_level": "INFO",
        "file_level": "DEBUG",
        "chat_log_enabled": True,
    },
    "commands": {
        "help": True,
        "roll": True,
        "note_add": True,
        "note_read": True,
        "note_wipe": True,
        "funfact": True,
        "quote": True,
        "flip": True,
        "joke": True
    }
}


def create_dirs():
    for d in [LOGS_DIR, DATA_DIR]:
        if not d.exists():
            d.mkdir()
            print(f"Created directory: {d}")


def create_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        tomlkit.dump(DEFAULT_CONFIG, f)
        
    print(f"Created default config: {CONFIG_FILE}")


def main():
    print("Setting up IRC Bot environment...")
    create_dirs()
    create_config()
    print("Setup complete. Make sure to edit the irc values in config.toml before you run main.py")


if __name__ == "__main__":
    main()
