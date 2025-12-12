import json
from datetime import datetime

# Path to notes file
from core.paths import NOTES_FILE

def read_notes():
    """
    Read all notes from notes.json.
    Returns a list of note dictionaries.
    """
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
            if not isinstance(notes, list):
                raise ValueError("notes.json must contain a list of notes")
            return notes
            
    except FileNotFoundError:
        # If the file doesn't exist, return empty list
        return []
        
    except json.JSONDecodeError:
        raise ValueError(f"{NOTES_FILE} contains invalid JSON!")


def add_note(user: str, content: str):
    """
    Add a new note.
    Each note is a dict with timestamp, user, and content.
    """
    notes = read_notes()
    new_note = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "content": content
    }
    notes.append(new_note)
    _write_notes(notes)


def wipe_notes():
    """
    Wipe all notes from the file.
    """
    _write_notes([])


def _write_notes(notes_list):
    """
    Internal helper to write notes list to notes.json.
    """
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes_list, f, indent=4)
