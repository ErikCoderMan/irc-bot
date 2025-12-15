from random import randint

async def roll_command(bot, user, target, tokens=None):
    roll = randint(0, 100)
    message = f"{user} rolled {roll}"
    
    await bot.send_privmsg(
        target=target,
        message=message
    )
