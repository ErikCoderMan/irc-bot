from core.storage import add_note, read_notes, wipe_notes
from core.config import settings
from utils.text import sanitize_text, truncate_text

async def note_command(bot, user, tokens):
    if len(tokens) < 2:
        bot.writer.write(
            f"PRIVMSG {bot.channel} :Invalid usage, try !help\r\n".encode()
        )
        await bot.writer.drain()
        return
    
    note_mode = tokens[1]
    
    if note_mode == "read":
        notes = read_notes()
        
        if not notes:
            bot.writer.write(
                f"PRIVMSG {bot.channel} :Notes empty!\r\n".encode()
            )
            await bot.writer.drain()
            return
        
        for note in notes:
            bot.writer.write(
                f"PRIVMSG {bot.channel} :{note['timestamp']}, {note['user']}, {note['content']}\r\n".encode()
            )
            await bot.writer.drain()
    
    elif note_mode == "wipe":
        wipe_notes()
        bot.writer.write(
            f"PRIVMSG {bot.channel} :Notes wiped by {user}\r\n".encode()
        )
        await bot.writer.drain()
    
    elif note_mode == "add" and len(tokens) >= 3:
        notes = read_notes()
        max_notes = settings.get("max_notes", 50)
        
        if len(notes) >= max_notes:
            bot.writer.write(
                f"PRIVMSG {bot.channel} :Cannot add note, max notes ({max_notes}) reached!\r\n".encode()
            )
            await bot.writer.drain()
            return
        
        # Sanitize and truncate textcontent
        raw_text = " ".join(tokens[2:])
        clean_text = sanitize_text(raw_text)
        clean_text = truncate_text(clean_text, settings['max_note_length'])
        
        if not clean_text:
            bot.writer.write(
                f"PRIVMSG {bot.channel} :Note is empty after sanitization\r\n".encode()
            )
            await bot.writer.drain()
            return
            
        add_note(user, clean_text)
        bot.writer.write(
            f"PRIVMSG {bot.channel} :{user}'s note has been added!\r\n".encode()
        )
        await bot.writer.drain()
