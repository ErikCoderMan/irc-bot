import asyncio
import ssl

# configs
from core.config import config, is_command_enabled

# logger functions
from core.logger import log_info, log_error, log_debug

# import all of the bot commands from one place
from commands.registry import COMMANDS 

# util
from utils.chat_logger import log_chat
from utils.text import sanitize_text

class IRCBot:
    def __init__(self, server, port, nickname, channel, use_ssl, cmd_prefix="!"):
        # Bot connection info
        self.server = server
        self.port = port
        self.nick = nickname
        self.channel = channel if channel.startswith("#") else f"#{channel}"
        self.cmd_prefix = cmd_prefix
        
        # SSL context if needed
        self.use_ssl = use_ssl
        self.ssl_context = ssl.create_default_context() if use_ssl else None
        
        # Async connection streams
        self.reader = None
        self.writer = None
        self.connected = False

    # Connect to IRC server and register nick
    async def connect(self):
        # Open connection
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.server,
                self.port,
                ssl=self.ssl_context,
            )
        except Exception as e:
            log_error(f"Failed to connect: {e}")
            return False
        
        # Register nick
        await self.send_raw(f"NICK {self.nick}")
        await self.send_raw(f"USER {self.nick} 0 * :{self.nick}")
        
        return True

    # Send raw IRC line
    async def send_raw(self, line: str):
        if not self.writer:
            return
        
        # Write line to server
        self.writer.write(f"{line}\r\n".encode())
        await self.writer.drain()
        
        # Log sent line
        log_info(f"<send> {line}")

    # Send PRIVMSG
    async def send_privmsg(self, target: str, message: str):
        # Sanitize text
        message = sanitize_text(message)
        
        # Send PRIVMSG to target (channel or user)
        await self.send_raw(f"PRIVMSG {target} :{message}")
        
        # Log message if chat logging is enabled
        if config["logging"].get("chat_log_enabled", True):
            await log_chat(self.nick, target, message)

    # Respond to server PINGs
    async def handle_ping(self, parts):
        await self.send_raw(f"PONG {parts[1]}")

    # Handle welcome message and join channel
    async def handle_welcome(self):
        await self.send_raw(f"JOIN {self.channel}")
        self.connected = True
        log_info(f"Joined {self.channel}")

    # Handle events like, JOIN, PART, QUIT for logging
    async def handle_event(self, user, command, parts):
        # Target of the event (channel or fallback)
        target = parts[2] if len(parts) > 2 else self.channel
        
        # Log the event in chat log
        if config["logging"].get("chat_log_enabled", True):
            await log_chat(user, target, command.lower())

    # Handle PRIVMSG (channel or private message)
    async def handle_privmsg(self, user, parts, line):
        if len(parts) < 3 or " :" not in line:
            return
        
        raw_target = parts[2] # Channel or bot nickname
        _, msg_text = line.split(" :", 1)
        msg_text = msg_text.strip()
        
        # Early return if message text is empty
        if not msg_text:
            return
        
        is_pm = raw_target == self.nick
        allow_whispers = config["bot"].get("allow_whispers", False)
        
        # Ignore PMs if not allowed
        if is_pm and not allow_whispers:
            log_debug(f"Ignored PM from {user}")
            return
        
        # Validate user to avoid sending messages to full hostnames
        if user and is_pm:
            if any(c in user for c in ("!", "@", " ", ":")):
                log_debug(f"Invalid user format received: {user}")
                return
        
        # Determine target (user for PM, channel otherwise)
        target = user if is_pm else raw_target
        
        # Log message if chat logging is enabled
        if config["logging"].get("chat_log_enabled", True):
            await log_chat(user, target, msg_text)
        
        # Handle bot commands
        if not msg_text.startswith(self.cmd_prefix):
            return
        
        # Parse message content
        tokens = msg_text.split()
        raw_cmd = tokens[0]
        cmd_name = raw_cmd[len(self.cmd_prefix):]
        tokens = [cmd_name, *tokens[1:]]
        
        # Try to get command dict related to command from command registry
        cmd_entry = COMMANDS.get(cmd_name)

        try:
            if cmd_entry and is_command_enabled(cmd_name):
                # Execute enabled command
                await cmd_entry["func"](self, user, target, tokens)
                log_info(f"Executed '{cmd_name}' from '{user}' in {'PM' if is_pm else target}")
            
            elif cmd_entry and not is_command_enabled(cmd_name):
                # Inform target command is disabled
                await self.send_privmsg(target, f"Disabled command: {cmd_name}")
                
                log_info(f"Ignored disabled command: {cmd_name}")
            
            else:
                # Command unknown, do not spam channel, command may be enabled for other bots
                log_debug(f"Unknown command: {cmd_name}")
        
        except Exception as e:
            # Log execution error and notify user with limited details
            log_error(f"Command error in {cmd_name}: ", exc=e)
            await self.send_privmsg(target, "Unexpected error, check logs")

    # Main bot loop
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
                
                prefix = parts[0]  # Sender or server prefix
                command = parts[1]
                user = prefix[1:prefix.find("!")] if "!" in prefix else prefix
                
                if command == "PING":
                    await self.handle_ping(parts)
                    continue
                
                # IRC numeric reply 001 signals end of welcome
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
                
                # Close connection gracefully
                if self.writer:
                    self.writer.close()
                    await self.writer.wait_closed()
                
                # Exit run method
                return
