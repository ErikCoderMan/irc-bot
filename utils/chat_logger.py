import aiofiles
from datetime import datetime, timezone
from core.config import CHAT_LOG_FILE
from utils.text import sanitize_text

async def log_chat(user: str, target: str, message: str):
    clean_message = sanitize_text(message)
    
    # Create timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Normalize PMs
    location = target if target.startswith("#") else "PM"

    # Build log line
    line = f"{timestamp} | {location} | {user} | {clean_message}\n"

    async with aiofiles.open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
        await f.write(line)
