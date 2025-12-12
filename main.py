import asyncio
from core.config import config
from core.logger import log_info, log_error
from core.bot import IRCBot


async def main():
    log_info("Starting IRC bot...")

    try:
        bot = IRCBot(
            server=config["server"],
            port=int(config["port"]),
            nickname=config["nickname"],
            channel=config["channel"]
        )
        
    except Exception as e:
        log_error(f"Failed to initialize bot: {e}")
        return

    try:
        await bot.run()
        
    except KeyboardInterrupt:
        log_info("Bot stopped manually.")
        
    except Exception as e:
        log_error(f"Unexpected error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
