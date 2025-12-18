from datetime import datetime, timezone

from core.storage import read_json, write_json, wipe_json
from core.config import config, DATA_DIR
from utils.text import sanitize_text, truncate_text, sanitize_filename

NOTE_DIR = DATA_DIR / "note"
NOTE_DIR.mkdir(parents=True, exist_ok = True)

async def note_command(bot, user, target, tokens):
    if not tokens:
        return
    
    note_mode = tokens[0]
    
    note_filename = sanitize_text(target).strip().lower()
    note_filename = sanitize_filename(note_filename)
    note_filename = f"channel_{note_filename}" if target.startswith("#") else f"private_{note_filename}"
    note_file = NOTE_DIR / f"{note_filename}.json"

    if note_mode == "note_read":
        notes = await read_json(note_file)

        if not notes:
            await bot.send_privmsg(
                target=target,
                message="Notes empty!"
            )
            return

        for note in notes:
            line = f"{note['timestamp']}, {note['user']}, {note['content']}"
            await bot.send_privmsg(target=target, message=line)

    elif note_mode == "note_wipe":
        await wipe_json(note_file)
        await bot.send_privmsg(
            target=target,
            message=f"Notes wiped by {user}"
        )

    elif note_mode == "note_add":
        if len(tokens) < 2:
            await bot.send_privmsg(
                target=target,
                message="Usage: note_add [text]"
            )
            return

        notes = await read_json(note_file)
        max_notes = config["notes"].get("max_notes", 50)

        if len(notes) >= max_notes:
            await bot.send_privmsg(
                target=target,
                message=f"Cannot add note, max notes ({max_notes}) reached!"
            )
            return

        raw_text = " ".join(tokens[1:])
        clean_text = sanitize_text(raw_text)
        clean_text = truncate_text(
            clean_text,
            config["notes"].get("max_note_length", 200)
        )

        if not clean_text:
            await bot.send_privmsg(
                target=target,
                message="Note is empty after sanitization"
            )
            return

        note = {
            "timestamp": datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            ) + " UTC",
            "user": user,
            "content": clean_text
        }

        notes.append(note)
        await write_json(note_file, notes)

        await bot.send_privmsg(
            target=target,
            message=f"Note from {user} has been added!"
        )
