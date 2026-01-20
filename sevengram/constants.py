from enum import StrEnum, auto


class StickerSetInspectAction(StrEnum):
    """Available actions while inspecting a Sticker Set."""

    ADD = auto()


DEFAULT_EMOJI = '⬜️'

CUSTOM_EMOJI_DIMENSIONS = (100, 100)  # in pixels

MAX_VIDEO_STICKER_DURATION = 3  # in seconds

MAX_VIDEO_STICKER_FPS = 30

MAX_VIDEO_STICKER_SIZE = 256_000  # bytes
