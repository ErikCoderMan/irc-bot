from core.config import enabled_commands

async def help_command(bot, user, target, tokens=None):
    from commands.registry import COMMANDS

    arg = tokens[1] if tokens and len(tokens) > 1 else None
    
    # Case: !help <command>
    if arg:
        if arg not in enabled_commands or arg not in COMMANDS:
            message = f"Unknown or disabled command: {arg}."
            
        else:
            cmd_info = COMMANDS[arg]
            usage = f"{bot.cmd_prefix}{cmd_info.get('usage', arg)}"
            description = cmd_info.get("description", "")
            message = f"{usage} - {description}"
            
        await bot.send_privmsg(target=target, message=message)

    # Case: !help
    else:
        commands = []

        for cmd_name in sorted(enabled_commands):
            if cmd_name in COMMANDS:
                commands.append(f"{bot.cmd_prefix}{cmd_name}")

        if not commands:
            message = "No commands are currently enabled."
            await bot.send_privmsg(target=target, message=message)
            
        else:
            message = f"Available commands: {', '.join(commands)}"
        
            await bot.send_privmsg(target=target, message=message)
            
            await bot.send_privmsg(
                target=target,
                message=f"Use {bot.cmd_prefix}help [command] for more info on a specific command."
            )
