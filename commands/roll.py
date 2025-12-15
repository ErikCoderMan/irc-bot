from random import randint

async def roll_command(bot, user, target, tokens=None):
    roll = randint(0, 100)
    message = f"{user} rolled {roll}"
    
    await bot.send_line(
        f"PRIVMSG {target} :{message}",
        target=target,
        user_msg=message
    )
    await bot.writer.drain()
