# import all bot commands
from commands.help import help_command
from commands.note import note_command
from commands.roll import roll_command

COMMANDS = {
    "help": {
        "func": help_command,
        "description": "Shows available commands",
        "usage": "help"
    },
    "roll": {
        "func": roll_command,
        "description": "Rolls a number between 0 and 100",
        "usage": "roll"
    },
    "note_add": {
        "func": note_command,
        "description": "Add a note to the notes list",
        "usage": "note_add [text]"
    },
    "note_read": {
        "func": note_command,
        "description": "Read all stored notes",
        "usage": "note_read"
    },
    "note_wipe": {
        "func": note_command,
        "description": "Remove all stored notes",
        "usage": "note_wipe"
    }
}
