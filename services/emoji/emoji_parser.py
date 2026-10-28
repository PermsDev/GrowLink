import re

from database.growlink.emoji_manager import get_emoji


EMOJI_PATTERN = re.compile(r"(?<![<\w:]):([a-zA-Z0-9_]+):(?![>\w:])")


def parse_emojis(text: str) -> str:
    return EMOJI_PATTERN.sub(
        lambda match: get_emoji(
            match.group(1),
            default=match.group(0),
        ),
        text,
    )