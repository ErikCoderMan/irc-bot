import asyncio
import ssl
from json import JSONDecodeError

# configs
from core.config import settings, is_command_enabled

# logger functions
from core.logger import log_info, log_error, log_debug

# import all of the bot commands from one place
from commands.registry import COMMANDS 

# util
from utils.chat_logger import log_chat
from utils.text import sanitize_text

class IRCBot:
    def __init__(self, server, port, nickname, channel, use_ssl, cmd_prefix="!"):
        self.server = server
        self.port = port
        self.nick = nickname
        self.channel = channel if channel.startswith("#") else f"#{channel}"
        self.cmd_prefix = cmd_prefix

        self.use_ssl = use_ssl
        self.ssl_context = ssl.create_default_context() if use_ssl else None

        self.reader = None
        self.writer = None
        self.connected = False

    # Connection
    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.server,
                self.port,
                ssl=self.ssl_context,
            )
        except Exception as e:
            log_error(f"Failed to connect: {e}")
            return False

        await self.send_raw(f"NICK {self.nick}")
        await self.send_raw(f"USER {self.nick} 0 * :{self.nick}")
        return True

    async def send_raw(self, line: str):
        if not self.writer:
            return

        self.writer.write(f"{line}\r\n".encode())
        await self.writer.drain()
        log_info(f"<send> {line}")

    async def send_privmsg(self, target: str, message: str):
        message = sanitize_text(message)
        await self.send_raw(f"PRIVMSG {target} :{message}")

        if settings.get("chat_log_enabled", True):
            await log_chat(self.nick, target, message)

    # Handlers
    async def handle_ping(self, parts):
        await self.send_raw(f"PONG {parts[1]}")

    async def handle_welcome(self):
        await self.send_raw(f"JOIN {self.channel}")
        self.connected = True
        log_info(f"Joined {self.channel}")

    async def handle_event(self, user, command, parts):
        target = parts[2] if len(parts) > 2 else self.channel

        if settings.get("chat_log_enabled", True):
            await log_chat(user, target, command.lower())

    async def handle_privmsg(self, user, parts, line):
        if len(parts) < 3 or " :" not in line:
            return

        raw_target = parts[2]
        _, msg_text = line.split(" :", 1)
        msg_text = msg_text.strip()

        if not msg_text:
            return

        is_pm = raw_target == self.nick
        allow_whispers = settings.get("allow_whispers", False)

        if is_pm and not allow_whispers:
            log_debug(f"Ignored PM from {user}")
            return

        target = user if is_pm else raw_target

        if settings.get("chat_log_enabled", True):
            await log_chat(user, target, msg_text)

        # Command handling
        if not msg_text.startswith(self.cmd_prefix):
            return

        tokens = msg_text.split()
        raw_cmd = tokens[0]
        cmd_name = raw_cmd[len(self.cmd_prefix):]
        tokens = [cmd_name, *tokens[1:]]
        
        cmd_entry = COMMANDS.get(cmd_name)

        try:
            if cmd_entry and is_command_enabled(cmd_name):
                # Call bot-command function
                await cmd_entry["func"](self, user, target, tokens)
                
                log_info(
                    f"Executed '{cmd_name}' from '{user}' in {'PM' if is_pm else target}"
                )
            else:
                log_debug(f"Unknown/disabled command: {cmd_name}")

        except Exception as e:
            log_error(f"Command error in {cmd_name}: ", exc=e)
            await self.send_privmsg(target, "Unexpected error, check logs")

    # Run 
    async def run(self):
        if not await self.connect():
            return

        while True:
            try:
                raw = await self.reader.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                
                log_debug(f"<recv> {line}")
                
                parts = line.split()
                if len(parts) < 2:
                    continue

                prefix = parts[0]
                command = parts[1]
                user = prefix[1:prefix.find("!")] if "!" in prefix else prefix

                if command == "PING":
                    await self.handle_ping(parts)
                    continue

                if not self.connected and command == "001":
                    await self.handle_welcome()
                    continue

                if command in ("JOIN", "PART", "QUIT"):
                    await self.handle_event(user, command, parts)
                    continue

                if command == "PRIVMSG":
                    await self.handle_privmsg(user, parts, line)

            except Exception as e:
                log_error(f"Fatal error: ", e)
                if self.writer:
                    self.writer.close()
                    await self.writer.wait_closed()
                return
