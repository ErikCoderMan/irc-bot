# IRC Bot
A simple, configurable IRC bot written in Python.  
Supports basic commands, notes, logging, and modular configuration.

## Features
- Connects to IRC with optional SSL
- Command-based interaction
- Note system with limits and sanitization
- Configurable via JSON files
- File and console logging

## Requirements
- Python 3.10+
- Internet connection

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ErikCoderMan/irc-bot.git
   cd irc-bot
   ```
2. Create and activate a virtual environment  
   Windows:  
   (replace `python3` with `python` or `py` depending on your system)  
   ```bash
   python -m venv venv  
   venv\Scripts\activate  
   ```
   macOS / Linux:  
   (replace `python3` with `python` or `py` depending on your system)  
   ```bash
   python3 -m venv venv  
   source venv/bin/activate  
   ```
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

4. Create necessary JSON files from example templates  
   ```bash
   cp credentials_example.json credentials.json
   cp settings_example.json settings.json
   ```
   - Edit `credentials.json` with your server details.  
   - Edit `settings.json` if needed (optional) See example below.  

## Running  
   Run the program by running `main.py`:  
   (replace `python3` with `python` or `py` depending on your system)  
   ```bash
   python3 main.py
   ```  

## Usage  
1. Connect to the same IRC channel using your preferred IRC client.  
2. Send commands in the channel.

Example (using default prefix `!`):  
```md
!help
!roll
!note-add hello world
!note-read
!note-wipe
```

## Commands  
(replace prefix `!` to match command prefix configured in `settings.json`)  

- `!help`
- `!roll`
- `!note-add <text>`
- `!note-read`
- `!note-wipe`

## Configuration

### settings.json
Example configuration:

```json
{
  "command_prefix": "!",
  "max_notes": 50,
  "max_note_length": 200,
  "allow_whispers": false,
  
  "log": {
    "console_level": "INFO",
    "file_level": "DEBUG",
    "chat_log_enabled": true
  },
  
  "disabled_commands": []
}

```
Settings explained:  
- `command_prefix`: Prefix used to trigger commands in chat.  
- `max_notes`: Maximum number of notes that can be stored.  
- `max_note_length`: Maximum character length of a single note (longer notes are truncated).  
- `ignore_whispers`: If bot should ignore private messages (PMs) or not (true/false)
-  `log`: Logging configuration  
   - `console_level`: Minimum level to show in the console  
   possible levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.  
   - `file_level`: Minimum level to write to the log file.  
   possible levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.  
   - `chat_log_enabled`: Option to enable chat log.

- `disabled_commands`: List of command names to disable  
(e.g. `["roll"]` or `["roll", "note"]`)  

### credentials.json  
Contains the IRC server connection info:

- `server`: IRC server hostname
- `port`: IRC server port
- `nickname`: Bot nickname
- `channel`: Channel to join
- `use_ssl`: Enable SSL connection (true/false)

