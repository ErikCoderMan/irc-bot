from core.config import settings

async def help_command(bot, user, target, tokens=None):
    disabled = settings.get("disabled_commands", [])

    all_commands = [
        "help",
        "roll",
        "note add <text>",
        "note read",
        "note wipe",
    ]

    enabled_cmds = [
        cmd for cmd in all_commands
        if cmd.split()[0] not in disabled
    ]

    if not enabled_cmds:
        message = "No commands are currently enabled."
    else:
        message = (
            f"Use prefix '{bot.cmd_prefix}' before commands. "
            f"Available commands: {', '.join(enabled_cmds)}"
        )

    await bot.send_line(
        f"PRIVMSG {target} :{message}",
        target=target,
        user_msg=message
    )
