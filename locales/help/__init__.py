
import json
from pathlib import Path

COMMANDS_DIR = Path(__file__).parent


def load_commands():
    commands = {}

    for file_path in COMMANDS_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        name = data.get("name")

        if name:
            commands[name] = data

    return commands


COMMAND_HELP = load_commands()
