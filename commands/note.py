from datetime import datetime, timezone
from json import JSONDecodeError

from core.storage import read_json, write_json, wipe_json
from core.config import config, NOTES_FILE
from utils.text import sanitize_text, truncate_text

async def note_command(bot, user, target, tokens):
    note_mode = tokens[0]

    if note_mode == "note_read":
        notes = await read_json(NOTES_FILE)

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
        await wipe_json(NOTES_FILE)
        await bot.send_privmsg(
            target=target,
            message=f"Notes wiped by {user}"
        )

    elif note_mode == "note_add":
        if len(tokens) < 2:
            await bot.send_privmsg(
                target=target,
                message="Usage: note-add [text]"
            )
            return

        notes = await read_json(NOTES_FILE)
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
        await write_json(NOTES_FILE, notes)

        await bot.send_privmsg(
            target=target,
            message=f"Note from {user} has been added!"
        )
