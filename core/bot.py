import asyncio
import ssl
from json import JSONDecodeError

from core.config import settings, is_command_enabled
from core.logger import log_info, log_error, log_debug

from commands.help import help_command
from commands.note import note_command
from commands.roll import roll_command

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
        self.ssl_context = ssl.create_default_context() if self.use_ssl else None

        self.connected = False
        self.reader = None
        self.writer = None

        self.commands_map = {
            "help": help_command,
            "note": note_command,
            "roll": roll_command
        }

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.server, self.port, ssl=self.ssl_context
            )
        except Exception as e:
            log_error(f"Failed to connect to {self.server}:{self.port} - {e}")
            return False

        self.writer.write(f"NICK {self.nick}\r\n".encode())
        self.writer.write(f"USER {self.nick} 0 * :{self.nick}\r\n".encode())
        await self.writer.drain()
        return True

    async def send_line(self, line: str, target: str = None, user_msg: str = None):
        """Send a line to the server and log it. Optionally log to chat.log."""
        if not self.writer:
            return

        self.writer.write(f"{line}\r\n".encode())
        await self.writer.drain()

        log_info(f"<send> {line}")

        if target and user_msg is not None:
            await log_chat(user=self.nick, target=target, message=user_msg)

    async def handle_ping(self, parts):
        reply = f"PONG {parts[1]}"
        await self.send_line(reply)
        log_debug(f"PING -> {reply}")

    async def handle_welcome(self, parts):
        await self.send_line(f"JOIN {self.channel}")
        self.connected = True
        log_info(f"Connected to {self.server}, joined {self.channel}")

    async def handle_event(self, user, command, parts):
        target = parts[2] if len(parts) > 2 else self.channel
        await log_chat(user, target, command.lower())

    async def handle_privmsg(self, user, parts, line):
        # Need at least: :nick PRIVMSG target :message
        if len(parts) < 3 or " :" not in line:
            return

        target = parts[2]
        _, msg_text = line.split(" :", 1)
        msg_text = msg_text.strip()

        if not msg_text:
            return

        is_pm = target == self.nick
        target = user if is_pm else target
        
        # Ignore PMs if disabled
        if is_pm and settings.get("ignore_whispers", False):
            log_info(f"Ignored PM from {user}: {msg_text}")
            return

        # Log incoming chat
        await log_chat(user, target, msg_text)

        # Command check
        if not msg_text.startswith(self.cmd_prefix):
            return

        tokens = msg_text.split()
        cmd_name = tokens[0][len(self.cmd_prefix):]
        cmd_func = self.commands_map.get(cmd_name)

        try:
            if cmd_func and is_command_enabled(cmd_name):
                await cmd_func(self, user, target, tokens)
                log_info(
                    f"Executed '{' '.join(tokens)}' from '{user}' "
                    f"in {'PM' if is_pm else target}"
                )
            else:
                log_debug(f"Unknown or disabled command: {cmd_name} from {user}")

        except JSONDecodeError as e:
            log_error(f"JSON error in command '{cmd_name}' from '{user}': {e}")
            await self.send_line(
                f"PRIVMSG {target} :Data file is corrupt",
                target=target,
                user_msg="Data file is corrupt"
            )

        except Exception as e:
            log_error(f"Exception in command '{cmd_name}' from '{user}': {e}")
            await self.send_line(
                f"PRIVMSG {target} :Unexpected error, check logs",
                target=target,
                user_msg="Unexpected error"
            )
            
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
                    
                line = sanitize_text(line)

                parts = line.split()
                if not parts:
                    continue

                # Extract basic info
                prefix = parts[0]
                command = parts[1]
                user = prefix[1:prefix.find("!")] if "!" in prefix else prefix

                # Log line
                if command in ("PRIVMSG", "JOIN", "PART", "QUIT"):
                    log_info(f"<recv> {line}")
                else:
                    log_debug(f"<recv> {line}")

                # Handle different types
                if command == "PING":
                    await self.handle_ping(parts)
                    continue

                if not self.connected and len(parts) >= 2 and parts[1] == "001":
                    await self.handle_welcome(parts)
                    continue

                if command in ("JOIN", "PART", "QUIT"):
                    await self.handle_event(user, command, parts)
                    continue

                if command == "PRIVMSG" and " :" in line:
                    await self.handle_privmsg(user, parts, line)
                    continue

            except Exception as e:
                log_error(f"Fatal connection error: {e}")
                if self.writer:
                    self.writer.close()
                    await self.writer.wait_closed()
                return
