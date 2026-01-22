from urllib.parse import urlparse

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BufferedInputFile, InputSticker

from sevengram.api import seventv_client
from sevengram.config import settings
from sevengram.constants import (
    DEFAULT_EMOJI,
    EMOTE_FORMAT_SEVENTV_EXTENSION_MAP,
    EMOTE_FORMAT_TELEGRAM_EXTENSION_MAP,
)
from sevengram.database.core import get_session
from sevengram.exceptions import ApiError, ServiceError, ValidationError
from sevengram.models import (
    Emote,
    EmoteFormat,
    EmoteSource,
    Sticker,
    StickerSet,
    StickerType,
)
from sevengram.repositories import EmoteRepository, StickerRepository
from sevengram.services.utils import CustomEmojiImageConverter, fetch_emote_image


class CustomEmojiAddService:
    def __init__(
        self,
        bot: Bot,
        sticker_set: StickerSet,
        emote_url: str,
    ):
        """Service that adds a Custom Emoji to a Sticker Set from 7TV Emote URL.

        :param bot: Telegram bot instance.
        :param sticker_set: Sticker Set to add to.
        :param emote_url: Emote 7TV URL.
        """
        self._bot = bot
        self._sticker_set = sticker_set
        self._emote_url = emote_url

    async def execute(self) -> str:
        """Add a Custom Emoji to a Sticker Set.

        :return: Emote name.
        """
        host, path = self._parse_url(self._emote_url)
        self._validate(host)

        emote_id = self._parse_emote_id(path)

        async with get_session() as session:
            emote_repository = EmoteRepository(session)

            # Find an existing Emote
            emote = await emote_repository.get_by_external_id(
                external_id=emote_id,
                source=EmoteSource.SEVENTV,
            )

            # Or create a new one
            if emote is None:
                emote = await self._create_new_emote(emote_repository, emote_id)

        # Create Emoji in Telegram
        is_created = await self._add_in_telegram(emote)
        if not is_created:
            raise ValidationError('Failed to add emoji. Please try again.')

        # On success create in database
        await self._create_emoji(emote)

        return emote.name

    def _validate(self, url_host: str):
        self._validate_sticker_set()
        self._validate_emote_url(url_host)

    def _validate_sticker_set(self):
        if self._sticker_set.type != StickerType.CUSTOM_EMOJI:
            raise ValidationError('You can only add an Emoji to an Emoji Pack.')

    def _validate_emote_url(self, url_host: str):
        if url_host != settings.SEVENTV_URL.host:
            raise ValidationError(f'Send {settings.SEVENTV_URL.host} emote.')

    def _parse_url(self, url: str) -> tuple[str, str]:
        parsed_url = urlparse(url)
        return parsed_url.hostname, parsed_url.path

    def _parse_emote_id(self, url_path: str) -> str:
        return url_path.strip().split('/')[-1]

    async def _create_new_emote(
        self,
        emote_repository: EmoteRepository,
        emote_id: str,
    ) -> Emote:
        """Upload an Emote image file to Telegram and create a new Emote in database."""
        # Fetch an Emote from 7TV
        emote_data = await self._fetch_emote(emote_id)

        is_animated = emote_data['flags']['animated']
        emote_format = EmoteFormat.VIDEO if is_animated else EmoteFormat.STATIC

        emote_name = emote_data['defaultName']
        file_url = self._extract_file_url(emote_data, emote_format)

        # Upload an Emote image to Telegram
        input_file = await self._fetch_and_convert_emote_image(
            emote_url=file_url,
            emote_name=emote_name,
            emote_format=emote_format,
        )
        file_id = await self._upload_sticker_file(input_file, emote_format)

        # Create an Emote in database
        return await emote_repository.create(
            file_id=file_id,
            source=EmoteSource.SEVENTV,
            external_id=emote_id,
            name=emote_name,
            file_url=file_url,
            format=emote_format,
        )

    async def _upload_sticker_file(
        self,
        sticker: BufferedInputFile,
        sticker_format: EmoteFormat,
    ) -> str:
        """Upload an Emote file to the Telegram servers and return its file_id."""
        try:
            result = await self._bot.upload_sticker_file(
                user_id=self._bot.id,
                sticker=sticker,
                sticker_format=sticker_format,
            )
        except TelegramBadRequest as e:
            raise ApiError(f'Telegram error while uploading the file: {e.message}') from e
        return result.file_id

    async def _fetch_emote(self, emote_external_id: str) -> dict:
        """Fetch an Emote from 7TV and create it in database."""
        emote_data = await seventv_client.fetch_emote(emote_external_id)
        if emote_data is None:
            raise ApiError('Emote not found.')
        return emote_data

    def _extract_file_url(self, emote_data: dict, emote_format: EmoteFormat) -> str:
        """Extract an Emote image URL in 3x resolution."""
        file_extension = EMOTE_FORMAT_SEVENTV_EXTENSION_MAP[emote_format]
        # 3x is closest to 100x100 size (96x96)
        image_suffix = f'3x.{file_extension}'
        emote_images_filter = filter(
            lambda image: image['url'].endswith(image_suffix),
            emote_data['images'],
        )
        try:
            return next(emote_images_filter)['url']
        except (StopIteration, KeyError) as e:
            raise ServiceError('Failed to extract emote image URL.') from e

    async def _create_emoji(self, emote: Emote) -> Sticker:
        """Create an Emoji in database."""
        async with get_session() as session:
            sticker_repository = StickerRepository(session)
            return await sticker_repository.create(
                file_unique_id=None,
                type=StickerType.CUSTOM_EMOJI,
                emoji=DEFAULT_EMOJI,
                emote_id=emote.id,
                sticker_set_id=self._sticker_set.id,
            )

    async def _fetch_and_convert_emote_image(
        self,
        emote_url: str,
        emote_name: str,
        emote_format: EmoteFormat,
    ) -> BufferedInputFile:
        """Prepare an Emote image to be uploaded to Telegram."""
        emote_image = await fetch_emote_image(emote_url)
        converted_image = CustomEmojiImageConverter(
            image_file=emote_image,
            emote_format=emote_format,
        ).convert()
        file_extension = EMOTE_FORMAT_TELEGRAM_EXTENSION_MAP[emote_format]
        return BufferedInputFile(
            file=converted_image,
            filename=f'{emote_name}.{file_extension}',
        )

    async def _add_in_telegram(self, emote: Emote) -> bool:
        """Add an Emoji to a Sticker Set in Telegram.

        :return: is_created flag.
        """
        try:
            input_sticker = InputSticker(
                sticker=emote.file_id,
                format=emote.format,
                emoji_list=[DEFAULT_EMOJI],
            )
            return await self._bot.add_sticker_to_set(
                user_id=self._sticker_set.user.telegram_id,
                name=self._sticker_set.name,
                sticker=input_sticker,
            )
        except TelegramBadRequest as e:
            raise ApiError(f'Telegram error while adding an Emoji: {e.message}') from e
