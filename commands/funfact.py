from pathlib import Path
from core.storage import read_json
from random import choice

RESOURCES_DIR = Path(__file__).parent / "resources" / "funfact"
FACTS_FILE = RESOURCES_DIR / "facts.json"

async def funfact_command(bot, user, target, tokens=None):
    all_facts = await read_json(FACTS_FILE)
    arg = tokens[1] if tokens and len(tokens) > 1 else None

    if arg:
        if arg not in all_facts:
            await bot.send_privmsg(
                target=target,
                message=f"Unknown category: {arg}"
            )
            return

        category_name = arg
        random_fact = choice(all_facts[arg])

    else:
        category_name = choice(list(all_facts.keys()))
        random_fact = choice(all_facts[category_name])

    await bot.send_privmsg(
        target=target,
        message=f"{category_name.capitalize()}: {random_fact.lower()}"
    )
