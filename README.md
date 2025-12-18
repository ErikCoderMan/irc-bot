# IRC Bot
A simple, configurable IRC bot written in Python.  
Supports basic commands, notes, logging, and modular configuration.

## Features
- Connects to IRC with optional SSL
- Command-based interaction
- Note system with limits and sanitization
- Configurable via TOML files
- File and console logging

## Requirements
- Python 3.10+
- Internet connection

## Installation
During installation replace `python3` with `python` or `py` depending on your system  
1. Clone the repository:
   ```bash
   git clone https://github.com/ErikCoderMan/irc-bot.git
   cd irc-bot
   ```
2. Create and activate a virtual environment  
   Windows:   
   ```bash
   python -m venv venv  
   venv\Scripts\activate  
   ```
   macOS / Linux:  
   ```bash
   python3 -m venv venv  
   source venv/bin/activate  
   ```
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

4. Create necessary files with installer  
   ```bash
   python3 installer.py
   ```
   - Edit `config.toml` with your server details (more info below).    

## Running  
   Run the program by running `main.py`  
   (replace `python3` with `python` or `py` depending on your system):  
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
!note_add hello world
!note_read
!note_wipe
```

## Commands  
(replace prefix `!` to match command prefix configured in `config.toml`)  

- `!help`
- `!roll`
- `!note_add <text>`
- `!note_read`
- `!note_wipe`
- `!funfact [category]`
- `!quote`
- `!flip`
- `!joke`

## Configuration

### config.toml
Example configuration:

```toml
[irc]
server = "irc.exampleserver.com"
port = 6697
channel = "#examplechannel"
nickname = "examplenickname"
use_ssl = true

[bot]
command_prefix = "!"
allow_whispers = false

[notes]
max_notes = 50
max_note_length = 200

[logging]
console_level = "INFO"
file_level = "DEBUG"
chat_log_enabled = true

[commands]
help = true
roll = true
note_add = true
note_read = true
note_wipe = true

```
Settings explained:  
`[irc]`  
`server`: IRC server hostname  
`port`: IRC server port  
`channel`: IRC channel name  
`nickname`: Nickname that will be visible to everyone in the channel  
`use_ssl`: Setting to use encrypted traffic or not (`true`/`false`)  

`[bot]`  
`command_prefix`: Prefix used to trigger commands in chat.  
`allow_whispers`: If bot should allow private messages (PMs) or not (`true`/`false`)  

`[notes]`  
`max_notes`: Maximum number of notes that can be stored.  
`max_note_length`: Maximum character length of a single note (longer notes are truncated).  

`[logging]`  
`console_level`: Minimum level to show in the console  
possible levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.  
`file_level`: Minimum level to write to the log file.  
possible levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.  
`chat_log_enabled`: Option to enable chat log.  

`[commands]`  
Here you can toggle commands (`true`/`false`)  
the bot will not react to any command that is set to `false` in the `config.toml` file  
(loaded during program start so changes will take effect next time main.py is started)  
