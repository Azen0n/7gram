from enum import StrEnum, auto

from sevengram.models.emote_format import EmoteFormat


class StickerSetInspectAction(StrEnum):
    """Available actions while inspecting a Sticker Set."""

    ADD = auto()


EMOTE_FORMAT_SEVENTV_EXTENSION_MAP = {
    EmoteFormat.STATIC: 'webp',
    EmoteFormat.VIDEO: 'avif',
}
"""Mapping of an Emote format to an image file extension in 7TV."""

EMOTE_FORMAT_TELEGRAM_EXTENSION_MAP = {
    EmoteFormat.STATIC: 'webp',
    EmoteFormat.VIDEO: 'webm',
}
"""Mapping of an Emote format to a sticker-compatible file extension in Telegram."""


DEFAULT_EMOJI = '⬜️'

CUSTOM_EMOJI_DIMENSIONS = (100, 100)  # in pixels

MAX_VIDEO_STICKER_DURATION = 3  # in seconds

MAX_VIDEO_STICKER_FPS = 30

MAX_VIDEO_STICKER_SIZE = 256_000  # bytes
