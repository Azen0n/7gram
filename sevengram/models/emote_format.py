from enum import StrEnum, auto


class EmoteFormat(StrEnum):
    """Sticker format in Telegram."""

    STATIC = auto()
    VIDEO = auto()
