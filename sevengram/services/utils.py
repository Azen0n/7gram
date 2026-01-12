import uuid
from io import BytesIO

import imageio.v3 as iio
import numpy as np
from aiogram.types import BufferedInputFile, InputSticker
from httpx import HTTPError, TimeoutException
from PIL import Image, ImageSequence

from sevengram.api import http_client
from sevengram.constants import (
    CUSTOM_EMOJI_DIMENSIONS,
    DEFAULT_EMOJI,
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


def get_placeholder_emote() -> InputSticker:
    """Temporary placeholder emote from file system."""
    return InputSticker(
        sticker=BufferedInputFile.from_file(path='emote.png'),
        format='static',
        emoji_list=['😏'],
        keywords=['forsenE'],
    )


class EmoteConverter:
    def __init__(
        self,
        image_url: str,
        emote_name: str,
        emote_format: EmoteFormat,
    ):
        """Emote image converter.

        Downloads and converts image to one of suitable Telegram formats:
        1. 100x100 pixels .WEBP file for 'static' emotes.
        2. 100x100 pixels .WEBM file for 'video' (animated) emotes.

        :param image_url: Emote image URL.
        :param emote_name: Emote name.
        :param emote_format: Emote format for Telegram.
        """

        self._image_url = image_url
        self._emote_name = emote_name
        self._emote_format = emote_format

    async def convert(self) -> InputSticker:
        """Convert Emote image to InputSticker."""
        # Download Image from URL
        image = await self._get_image_from_url()

        # Transform Image to suitable file in bytes
        file_extension = '???'
        try:
            if self._emote_format == EmoteFormat.VIDEO:
                file_extension = 'webm'
                emoji_bytes = self._transform_image_to_webm_bytes(image)
            else:
                file_extension = 'webp'
                emoji_bytes = self._transform_image_to_webp_bytes(image)
        except Exception as e:
            raise ServiceError(
                f'Failed to convert {self._emote_format} Emote '
                f'to {file_extension} file: {e}',
            ) from e

        input_file = BufferedInputFile(
            file=emoji_bytes,
            filename=f'{self._emote_name}.{file_extension}',
        )
        return InputSticker(
            sticker=input_file,
            format=self._emote_format,
            emoji_list=[DEFAULT_EMOJI],
            keywords=[self._emote_name],
        )

    async def _get_image_from_url(self) -> Image:
        try:
            response = await http_client.get(self._image_url, timeout=10)
            response.raise_for_status()
        except TimeoutException as e:
            raise ApiError('Connection to 7TV timed out.') from e
        except HTTPError as e:
            raise ApiError('Failed to fetch emote image.') from e
        return Image.open(BytesIO(response.content))

    def _transform_image_to_webp_bytes(self, image: Image) -> bytes:
        """Transform static image to suitable .WEBP image for Telegram."""
        resized_image = image.resize(size=CUSTOM_EMOJI_DIMENSIONS)

        # Save to bytes
        buffer = BytesIO()
        resized_image.save(buffer, format='webp')
        buffer.seek(0)
        return buffer.getvalue()

    def _transform_image_to_webm_bytes(self, image: Image) -> bytes:
        """Transform animated image to suitable .WEBM video for Telegram."""
        frames = []
        durations = []

        for frame in ImageSequence.Iterator(image):
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
