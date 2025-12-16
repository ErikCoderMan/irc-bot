import asyncio
from core.config import config
from core.logger import log_info, log_error
from core.bot import IRCBot


async def main():
    log_info("Starting IRC bot...")

    try:
        bot = IRCBot(
            server=config["irc"]["server"],
            port=int(config["irc"]["port"]),
            nickname=config["irc"]["nickname"],
            channel=config["irc"]["channel"],
            cmd_prefix=config["bot"].get("command_prefix", "!"),  # fallback if not set
            use_ssl=config["irc"]["use_ssl"]
        )
        
    except Exception as e:
        log_error(f"Failed to initialize bot", exc=e)
        return

    try:
        await bot.run()
        
    except KeyboardInterrupt:
        log_info("Bot stopped manually.")
        
    except Exception as e:
        log_error(f"Unexpected error in main", exc=e)


if __name__ == "__main__":
    asyncio.run(main())
