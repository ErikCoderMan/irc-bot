import asyncio
import ssl
from random import randint

# Import core modules
from core.config import credentials, settings, is_command_enabled
from core.logger import log_info, log_error, log_debug
from core.storage import add_note, read_notes, wipe_notes

# Import command functions
from commands.help import help_command
from commands.note import note_command
from commands.roll import roll_command


class IRCBot:
    def __init__(self, server, port, nickname, channel, cmd_prefix="!", use_ssl="not specified"):
        self.server = server
        self.port = port
        self.nick = nickname
        self.channel = channel if channel.startswith("#") else f"#{channel}"
        self.cmd_prefix = cmd_prefix

        # Auto-detect SSL unless forced
        self.use_ssl = (self.port == 6697) if use_ssl == "not specified" else use_ssl
        self.ssl_context = ssl.create_default_context() if self.use_ssl else None

        self.connected = False
        self.reader = None
        self.writer = None

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.server,
                self.port,
                ssl=self.ssl_context
            )
        except Exception as e:
            log_error(f"Failed to connect to {self.server}:{self.port} - {e}")
            return False

        # Send initial handshake
        self.writer.write(f"NICK {self.nick}\r\n".encode())
        self.writer.write(f"USER {self.nick} 0 * :{self.nick}\r\n".encode())
        await self.writer.drain()
        return True

    async def run(self):
        if not await self.connect():
            return

        while True:
            try:
                line = await self.reader.readline()
                if not line:
                    continue

                line = line.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                parts = line.split()
                if not parts:
                    continue

                # Handle server PING
                if parts[0] == "PING":
                    self.writer.write(f"PONG {parts[1]}\r\n".encode())
                    await self.writer.drain()
                    continue

                # Wait for 001 welcome message
                if not self.connected and len(parts) >= 2 and parts[1] == "001":
                    self.writer.write(f"JOIN {self.channel}\r\n".encode())
                    await self.writer.drain()
                    self.connected = True
                    log_info(f"Connected to {self.server}, joined {self.channel}")
                    continue

                # Only process lines with actual message content
                if " :" not in line:
                    continue

                prefix_section, msg_text = line.split(" :", 1)
                msg_text = msg_text.strip()

                # Extract user from prefix
                irc_prefix = parts[0]
                if irc_prefix.startswith(":") and "!" in irc_prefix:
                    user = irc_prefix[1:irc_prefix.find("!")]
                else:
                    user = irc_prefix

                # Command prefix check
                if not msg_text.startswith(self.cmd_prefix):
                    continue

                tokens = msg_text.split()
                command = tokens[0][1:]

                # Execute commands if enabled
                try:
                    if command == "help" and is_command_enabled("help"):
                        await help_command(self, user, tokens)
                        log_info(f"{user} executed help command")

                    elif command == "note" and is_command_enabled("note"):
                        await note_command(self, user, tokens)
                        log_info(f"{user} executed note command: {tokens[1:] if len(tokens) > 1 else []}")

                    elif command == "roll" and is_command_enabled("roll"):
                        await roll_command(self, user, tokens)
                        log_info(f"{user} executed roll command")

                    else:
                        log_debug(f"Unknown or disabled command: {command} from {user}")

                except Exception as cmd_err:
                    log_error(f"Error executing command '{command}' for user {user}: {cmd_err}")

            except Exception as e:
                log_error(f"Error while reading from server: {e}")


# Entry point for tests
if __name__ == "__main__":
    bot = IRCBot(
        server=credentials["server"],
        port=int(credentials["port"]),
        nickname=credentials["nickname"],
        channel=credentials["channel"],
        cmd_prefix=settings.get("command_prefix", "!")
    )
    asyncio.run(bot.run())
