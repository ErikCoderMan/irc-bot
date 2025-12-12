async def help_command(bot, user, tokens):
    bot.writer.write(
        f"PRIVMSG {bot.channel} :Use prefix '{bot.cmd_prefix}' before the command, available commands: 'help', 'roll', 'note add [TEXT]', 'note read', 'note wipe'\r\n".encode()
    )
    await bot.writer.drain()
