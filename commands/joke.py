from pathlib import Path
from core.storage import read_json
from random import choice

RESOURCES_DIR = Path(__file__).parent / "resources" / "joke"
JOKES_FILE = RESOURCES_DIR / "jokes.json"

async def joke_command(bot, user, target, tokens=None):
    all_jokes = await read_json(JOKES_FILE)
    
    if not all_jokes:
        await bot.send_privmsg(target=target, message="No jokes available")
        return
    
    random_joke = choice(all_jokes)
    
    await bot.send_privmsg(
        target=target,
        message=random_joke.capitalize()
    )
