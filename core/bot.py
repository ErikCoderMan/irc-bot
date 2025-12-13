import asyncio
import ssl
from json import JSONDecodeError

# Import core modules
from core.config import is_command_enabled
from core.logger import log_info, log_error, log_debug

# Import command functions
from commands.help import help_command
from commands.note import note_command
from commands.roll import roll_command

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
                    reply = f"PONG {parts[1]}"
                    self.writer.write(f"{reply}\r\n".encode())
                    await self.writer.drain()
                    log_debug(f"Replied to PING with '{reply}'")
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
                
                except JSONDecodeError as e:
                    log_error(f"JSONDecodeError error while executing command: '{command}' from user: '{user}', error: {e}")
                    self.writer.write(
                        f"PRIVMSG {self.channel} :Data file is corrupt, check logs or try reset related data\r\n".encode()
                    )
                    await self.writer.drain()
                
                except Exception as e:
                    log_error(f"Exception error while executing command: '{command}' from user: '{user}': error: {e}")
                    self.writer.write(f"PRIVMSG {self.channel} :Unexpected error while executing command: '{command}', exiting now, check logs\r\n".encode())
                    await self.writer.drain()
                    return
            
            except Exception as e:
                log_error(f"Fatal connection error: {e}")
                if self.writer:
                    self.writer.close()
                    await self.writer.wait_closed()
                    
                return


