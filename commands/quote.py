from pathlib import Path
from core.storage import read_json
import random

RESOURCES_DIR = Path(__file__).parent / "resources" / "quote"
QUOTES_FILE = RESOURCES_DIR / "quotes.json"

async def quote_command(bot, user, target, tokens=None):
    all_quotes = await read_json(QUOTES_FILE)
    
    if not all_quotes:
        await bot.send_privmsg(target=target, message="No quotes available.")
        return

    random_quote = random.choice(all_quotes)
    result = f"{random_quote['quote'].capitalize()} - {random_quote['from'].title()}"

    await bot.send_privmsg(
        target=target,
        message=result
    )
