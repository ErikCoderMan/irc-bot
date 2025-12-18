from random import randint

async def flip_command(bot, user, target, tokens=None):
    roll = randint(0, 1)
    result = "Heads" if roll == 1 else "Tails"
    message = f"{user} flipped {result}"
    
    await bot.send_privmsg(
        target=target,
        message=message
    )
