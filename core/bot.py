import asyncio
import ssl
from random import randint

# Import some modules from core
from core.config import config
from core.logger import log_info, log_error, log_debug
from core.storage import add_note, read_notes, wipe_notes


class IRCBot:
    def __init__(self, server, port, nickname, channel, cmd_prefix = "!", use_ssl="not specified"):
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
                    
                # Ignore messages without actual text content
                if " :" not in line:
                    continue
                
                # Split into prefix + message text 
                prefix_section, msg_text = line.split(" :", 1)
                msg_text = msg_text.strip()
                
                # IRC message prefix (ex: :nick!ident@host)
                irc_prefix = parts[0]
                
                # Extract nickname from IRC prefix
                if irc_prefix.startswith(":") and "!" in irc_prefix:
                    user = irc_prefix[1:irc_prefix.find("!")]
                else:
                    user = irc_prefix
                
                # Command prefix check (bot command)
                if not msg_text.startswith(self.cmd_prefix):
                    continue
                
                tokens = msg_text.split()
                command = tokens[0][1:]
                
                # Commands
                if command == "roll":
                    roll = randint(0, 100)
                    self.writer.write(
                        f"PRIVMSG {self.channel} :{user} rolled a {roll}\r\n".encode()
                    )
                    await self.writer.drain()
                    log_info(f"[roll] {user} executed {self.cmd_prefix}roll and got {roll}")
                
                elif command == "note":
                    if tokens[1]:
                        note_mode = tokens[1]
                        if note_mode == "read":
                            notes = read_notes()
                            for note in notes:
                                self.writer.write(
                                    f"PRIVMSG {self.channel} :{note}\r\n".encode()
                                )
                                await self.writer.drain()
                            log_info(f"[note read] {user} executed {self.cmd_prefix}note read")
                        
                        elif note_mode == "wipe":
                            wipe_notes()
                            self.writer.write(
                                f"PRIVMSG {self.channel} :Notes wiped by {user}\r\n".encode()
                            )
                            await self.writer.drain()
                            log_info(f"[note wipe] {user} executed {self.cmd_prefix}note wipe")
                        
                        elif note_mode == "add" and len(tokens) >= 3:
                            new_note = " ".join(tokens[2:])
                            add_note(user, new_note)
                            self.writer.write(
                                f"PRIVMSG {self.channel} :{user}'s note has been added!\r\n".encode()
                            )
                            log_info(f"[note add] {user} executed note add {new_note}")
                    
                    else:
                        self.writer.write(
                            f"PRIVMSG {self.channel} :Invalid usage of command, try {self.cmd_prefix}help for more info\r\n".encode()
                        )
                        await self.writer.drain()

            except Exception as e:
                log_error(f"Error while reading from server: {e}")
                
