
import json
from pathlib import Path
from functools import lru_cache


LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"


@lru_cache(maxsize=32)
def load_locale(filename: str) -> dict:
    relative_path = Path(filename)

    if (
        relative_path.is_absolute()
        or ".." in relative_path.parts
        or relative_path.suffix != ".json"
    ):
        raise ValueError("Invalid locale filename.")

    file_path = (LOCALES_DIR / relative_path).resolve()

    if not file_path.is_relative_to(LOCALES_DIR.resolve()):
        raise ValueError("Locale path is outside the locales directory.")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Locale file '{filename}' must contain a JSON object."
        )

    return data


def get_translations(filename: str) -> dict:
    data = load_locale(filename)
    translations = data.get("translations", {})

    if not isinstance(translations, dict):
        raise ValueError(
            f"'translations' in '{filename}' must be a JSON object."
        )

    return translations


def get_translation(
    filename: str,
    language: str,
    key: str,
    default=None,
):
    translations = get_translations(filename)

    language_data = translations.get(language, {})
    english_data = translations.get("en", {})

    return language_data.get(
        key,
        english_data.get(key, default),
    )
