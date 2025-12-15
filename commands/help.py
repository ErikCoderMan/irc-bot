from core.config import settings

async def help_command(bot, user, target, tokens=None):
    from commands.registry import COMMANDS
    
    disabled = settings.get("disabled_commands", [])

    arg = tokens[1] if len(tokens) > 1 else None
    result = []

    if arg:
        cmd_info = COMMANDS.get(arg)
        if cmd_info and arg not in disabled:
            usage = f"{bot.cmd_prefix}{cmd_info.get('usage', arg)}"
            description = cmd_info.get("description", "")
            result.append(f"{usage} - {description}")
        else:
            result.append(f"No info for command '{arg}' or command is disabled.")
    else:
        for cmd_name, cmd_info in COMMANDS.items():
            if cmd_name not in disabled:
                usage = f"{bot.cmd_prefix}{cmd_info.get('usage', cmd_name)}"
                description = cmd_info.get("description", "")
                result.append(f"{usage} - {description}")

        if not result:
            result.append("No commands are currently enabled.")
            
        else:
            result.insert(0, f"List of available commands:")

    for line in result:
        await bot.send_privmsg(target=target, message=line)
