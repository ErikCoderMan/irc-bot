from core.config import settings

async def help_command(bot, user, tokens):
    disabled = settings.get("disabled_commands", [])

    # List all commands
    all_commands = ["help", "roll", "note add [TEXT]", "note read", "note wipe"]

    # Filter away disabled commands
    enabled_cmds = [cmd for cmd in all_commands if cmd.split()[0] not in disabled]

    if not enabled_cmds:
        message = "No commands are currently enabled."
        
    else:
        message = f"Use prefix '{bot.cmd_prefix}' before the command. Available commands: {', '.join(enabled_cmds)}"

    # Send message
    bot.writer.write(f"PRIVMSG {bot.channel} :{message}\r\n".encode())
    await bot.writer.drain()
