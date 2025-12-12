import json

# Path to credentials file
from core.paths import CREDENTIALS_FILE

try:
    # Load credentials from JSON
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)
        config = {
            "server": loaded.get("server", ""),
            "port": loaded.get("port", 6667),
            "channel": loaded.get("channel", ""),
            "nickname": loaded.get("nickname", "")
        }
        
except FileNotFoundError:
    raise FileNotFoundError(
        f"{CREDENTIALS_FILE} is missing! "
        f"Please create {CREDENTIALS_FILE.name} using credentials_example.json as a template."
    )
    
except json.JSONDecodeError:
    raise ValueError(
        f"{CREDENTIALS_FILE} contains invalid JSON! "
        "Please check the file format."
    )

# Extra check: ensure all required fields are present and not empty
missing = [key for key, value in config.items() if value in ("", None)]
if missing:
    raise ValueError(
        f"Missing or empty values for: {', '.join(missing)} in {CREDENTIALS_FILE.name}!"
    )
