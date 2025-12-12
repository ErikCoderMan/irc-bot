from random import randint

async def roll_command(bot, user, tokens):
    roll = randint(0, 100)
    bot.writer.write(f"PRIVMSG {bot.channel} :{user} rolled a {roll}\r\n".encode())
    await bot.writer.drain()
