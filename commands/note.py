from core.storage import add_note, read_notes, wipe_notes
from core.config import settings
from utils.text import sanitize_text, truncate_text

async def note_command(bot, user, target, tokens=None):
    if len(tokens) < 2:
        await bot.send_privmsg(
            target=target,
            message=f"Invalid usage, try !help"
        )
        return
    
    note_mode = tokens[1]
    
    if note_mode == "read":
        notes = await read_notes()
        
        if not notes:
            await bot.send_privmsg(
                target=target,
                message=f"Notes empty!"
            )
            return
        
        for note in notes:
            line = f"{note['timestamp']}, {note['user']}, {note['content']}"
            await bot.send_privmsg(
                target=target,
                message=f"{line}"
            )
    
    elif note_mode == "wipe":
        await wipe_notes()
        await bot.send_privmsg(
            target=target,
            message=f"Notes wiped by {user}"
        )
    
    elif note_mode == "add" and len(tokens) >= 3:
        notes = await read_notes()
        max_notes = settings.get("max_notes", 50)
        
        if len(notes) >= max_notes:
            await bot.send_privmsg(
                target=target,
                message=f"Cannot add note, max notes ({max_notes}) reached!"
            )
            return
        
        # Sanitize and truncate text content
        raw_text = " ".join(tokens[2:])
        clean_text = sanitize_text(raw_text)
        clean_text = truncate_text(clean_text, settings['max_note_length'])
        
        if not clean_text:
            await bot.send_privmsg(
                target=target,
                message=f"Note is empty after sanitization"
            )
            return
            
        await add_note(user, clean_text)
        await bot.send_privmsg(
            target=target,
            message=f"Note from {user} has been added!"
        )
