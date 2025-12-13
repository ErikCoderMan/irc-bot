from core.storage import add_note, read_notes, wipe_notes
from core.config import settings

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
            bot.writer.write(f"PRIVMSG {bot.channel} :Notes empty!\r\n".encode())
            await bot.writer.drain()
            return
        
        for note in notes:
            bot.writer.write(
                f"PRIVMSG {bot.channel} :{note['timestamp']}, {note['user']}, {note['content']}\r\n".encode()
            )
            await bot.writer.drain()
    
    elif note_mode == "wipe":
        wipe_notes()
        bot.writer.write(f"PRIVMSG {bot.channel} :Notes wiped by {user}\r\n".encode())
        await bot.writer.drain()
    
    elif note_mode == "add" and len(tokens) >= 3:
        current_notes = read_notes()
        max_notes = settings.get("max_notes", 50)
        
        if len(current_notes) >= max_notes:
            bot.writer.write(
                f"PRIVMSG {bot.channel} :Cannot add note, max notes ({max_notes}) reached!\r\n".encode()
            )
            await bot.writer.drain()
            return
        
        new_note = " ".join(tokens[2:])
        add_note(user, new_note)
        bot.writer.write(f"PRIVMSG {bot.channel} :{user}'s note has been added!\r\n".encode())
        await bot.writer.drain()
