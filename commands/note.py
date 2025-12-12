from core.storage import add_note, read_notes, wipe_notes

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
        for note in notes:
            bot.writer.write(f"PRIVMSG {bot.channel} :{note['timestamp']}, {note['user']}, {note['content']}\r\n".encode())
            await bot.writer.drain()
    
    elif note_mode == "wipe":
        wipe_notes()
        bot.writer.write(f"PRIVMSG {bot.channel} :Notes wiped by {user}\r\n".encode())
        await bot.writer.drain()
    
    elif note_mode == "add" and len(tokens) >= 3:
        new_note = " ".join(tokens[2:])
        add_note(user, new_note)
        bot.writer.write(f"PRIVMSG {bot.channel} :{user}'s note has been added!\r\n".encode())
        await bot.writer.drain()
