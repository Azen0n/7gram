import uuid
from io import BytesIO

import imageio.v3 as iio
import numpy as np
from httpx import HTTPError, TimeoutException
from PIL import Image, ImageSequence

from sevengram.api import http_client
from sevengram.constants import (
    CUSTOM_EMOJI_DIMENSIONS,
    EMOTE_FORMAT_TELEGRAM_EXTENSION_MAP,
    MAX_VIDEO_STICKER_DURATION,
    MAX_VIDEO_STICKER_FPS,
)
from sevengram.exceptions import ApiError, ServiceError
from sevengram.models import EmoteFormat


def generate_sticker_set_name(bot_username: str) -> str:
    """Generate valid Telegram Sticker Set name.

    Example: custom_6ffd570fec99468ebe96fa9d04de6952_by_sevengram_bot.
    """
    return f'custom_{uuid.uuid4()}_by_{bot_username}'.replace('-', '')


async def fetch_emote_image(file_url: str) -> bytes:
    """Download image from URL."""
    try:
        response = await http_client.get(file_url, timeout=10)
        response.raise_for_status()
    except TimeoutException as e:
        raise ApiError('Connection to 7TV timed out.') from e
    except HTTPError as e:
        raise ApiError('Failed to fetch an Emote image.') from e
    if not response.headers.get('content-type', '').startswith('image'):
        raise ApiError('Emote file is not an Image.')
    return response.content


class CustomEmojiImageConverter:
    def __init__(
        self,
        image_file: bytes,
        emote_format: EmoteFormat,
    ):
        """Custom Emoji image converter.

        Converts image to one of suitable Telegram formats:
        1. 100x100 pixels .WEBP file for 'static' emotes.
        2. 100x100 pixels .WEBM file for 'video' (animated) emotes.

        :param image_file: Emote image file.
        :param emote_format: Emote format for Telegram.
        """

        self._image = Image.open(BytesIO(image_file))
        self._emote_format = emote_format

    def convert(self) -> bytes:
        """Convert Emote image to suitable Telegram format."""
        emote_format_method_map = {
            EmoteFormat.STATIC: self._transform_image_to_webp_bytes,
            EmoteFormat.VIDEO: self._transform_image_to_webm_bytes,
        }
        transform_method = emote_format_method_map[self._emote_format]
        file_extension = EMOTE_FORMAT_TELEGRAM_EXTENSION_MAP[self._emote_format]

        try:
            emoji_bytes = transform_method()
        except Exception as e:
            raise ServiceError(
                f'Failed to convert {self._emote_format} Emote '
                f'to {file_extension} file: {e}',
            ) from e

        return emoji_bytes

    def _transform_image_to_webp_bytes(self) -> bytes:
        """Transform static image to suitable .WEBP image for Telegram."""
        resized_image = self._image.resize(size=CUSTOM_EMOJI_DIMENSIONS)

        # Save to bytes
        buffer = BytesIO()
        resized_image.save(buffer, format='webp')
        buffer.seek(0)
        return buffer.getvalue()

    def _transform_image_to_webm_bytes(self) -> bytes:
        """Transform animated image to suitable .WEBM video for Telegram."""
        frames = []
        durations = []

        for frame in ImageSequence.Iterator(self._image):
            resized_frame = frame.resize(CUSTOM_EMOJI_DIMENSIONS)
            frame = resized_frame.convert('RGBA')
            frames.append(np.array(frame))
            durations.append(frame.info.get('duration', 100))

        if not frames:
            raise ServiceError('No frames found.')

        # Calculate FPS based on average frame duration in ms
        avg_duration = sum(durations) / len(durations)
        fps = int(min(MAX_VIDEO_STICKER_FPS, 1000 / avg_duration))

        # Limit video to max duration
        frames = frames[: int(MAX_VIDEO_STICKER_DURATION * fps)]

        # Save to bytes
        buffer = BytesIO()
        iio.imwrite(
            buffer,
            frames,
            extension='.webm',
            fps=fps,
            codec='libvpx-vp9',
            pixelformat='yuva420p',
            macro_block_size=1,
            output_params=[
                '-b:v',
                '100k',
                '-maxrate',  # Limiting bitrate to reduce video size
                '100k',
                '-bufsize',
                '200k',
            ],
        )
        buffer.seek(0)
        return buffer.getvalue()
