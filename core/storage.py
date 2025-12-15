import json
import aiofiles
from datetime import datetime, timezone
from json import JSONDecodeError

from core.paths import NOTES_FILE

async def read_notes() -> list:
    # Read all notes from the JSON file.
    try:
        async with aiofiles.open(NOTES_FILE, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content) if content else []

    except FileNotFoundError:
        # Notes file does not exist yet, treat as empty
        return []

    except JSONDecodeError:
        # Corrupt JSON, let caller decide how to handle
        raise

async def write_notes(notes: list):
    # Write the full notes list to JSON file.
    async with aiofiles.open(NOTES_FILE, "w", encoding="utf-8") as f:
        await f.write(
            json.dumps(notes, ensure_ascii=False, indent=4)
        )

async def add_note(user: str, content: str):
    # Add a note to the list with timestamp and user.
    notes = await read_notes()

    note = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + " UTC",
        "user": user,
        "content": content
    }

    notes.append(note)
    await write_notes(notes)

async def wipe_notes():
    # Clear all notes.
    await write_notes([])
