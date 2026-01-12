from urllib.parse import urlparse

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputSticker

from sevengram.api import seventv_client
from sevengram.config import settings
from sevengram.constants import DEFAULT_EMOJI
from sevengram.database.core import get_session
from sevengram.exceptions import ApiError, ServiceError, ValidationError
from sevengram.models import Emote, EmoteFormat, EmoteSource, Sticker, StickerSet
from sevengram.repositories import EmojiRepository, EmoteRepository
from sevengram.services.utils import EmoteConverter


class EmojiAddService:
    def __init__(
        self,
        bot: Bot,
        emoji_pack: StickerSet,
        emote_url: str,
    ):
        """Service that adds an Emoji to an Emoji Pack from 7TV Emote URL.

        :param bot: Telegram bot instance.
        :param emoji_pack: Emoji Pack to add to.
        :param emote_url: Emote 7TV URL.
        """
        self._bot = bot
        self._emoji_pack = emoji_pack
        self._emote_url = emote_url

    async def execute(self) -> str:
        """Add an Emoji to an Emoji Pack.

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
                emote = await self._fetch_and_create_emote(emote_repository, emote_id)

        # Create Emoji in Telegram
        input_emoji = await self._prepare_input_emoji(emote)
        is_created = await self._add_in_telegram(input_emoji)
        if not is_created:
            raise ValidationError('Failed to add emoji. Please try again.')

        # On success create in database
        await self._create_emoji(emote)

        return emote.name

    def _validate(self, url_host: str):
        self._validate_emote_url(url_host)

    def _validate_emote_url(self, url_host: str):
        if url_host != settings.SEVENTV_URL.host:
            raise ValidationError(f'Send {settings.SEVENTV_URL.host} emote.')

    def _parse_url(self, url: str) -> tuple[str, str]:
        parsed_url = urlparse(url)
        return parsed_url.hostname, parsed_url.path

    def _parse_emote_id(self, url_path: str) -> str:
        return url_path.strip().split('/')[-1]

    async def _fetch_and_create_emote(
        self,
        emote_repository: EmoteRepository,
        emote_external_id: str,
    ) -> Emote:
        """Fetch an Emote from 7TV and create it in database."""
        emote_data = await seventv_client.fetch_emote(emote_external_id)
        if emote_data is None:
            raise ApiError('Emote not found.')

        emote_name = emote_data['defaultName']
        is_animated = emote_data['flags']['animated']

        emote_format = EmoteFormat.VIDEO if is_animated else EmoteFormat.STATIC
        file_url = self._extract_file_url(emote_data, emote_format)

        return await emote_repository.create(
            file_id=None,
            source=EmoteSource.SEVENTV,
            external_id=emote_external_id,
            name=emote_name,
            file_url=file_url,
            format=emote_format,
        )

    def _extract_file_url(self, emote_data: dict, emote_format: EmoteFormat) -> str:
        if emote_format == EmoteFormat.VIDEO:
            file_extension = 'avif'
        else:
            file_extension = 'webp'
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
        async with get_session() as session:
            emoji_repository = EmojiRepository(session)
            return await emoji_repository.create(
                file_unique_id=None,
                emoji=DEFAULT_EMOJI,
                emote_id=emote.id,
                sticker_set_id=self._emoji_pack.id,
            )

    async def _prepare_input_emoji(self, emote: Emote) -> InputSticker:
        """Prepare emoji to send to Telegram."""
        # If the file is already stored on the Telegram servers, it can be sent as file_id
        if emote.file_id is not None:
            return InputSticker(
                sticker=emote.file_id,
                format=emote.format,
                emoji_list=[DEFAULT_EMOJI],
                keywords=[emote.name],
            )
        # If not, it will be sent as multipart/form-data file
        return await EmoteConverter(
            image_url=emote.file_url,
            emote_name=emote.name,
            emote_format=emote.format,
        ).convert()

    async def _add_in_telegram(self, input_emoji: InputSticker) -> bool:
        """Add Emoji to Emoji Pack in Telegram.

        :return: is_created flag.
        """
        try:
            return await self._bot.add_sticker_to_set(
                user_id=self._emoji_pack.user.telegram_id,
                name=self._emoji_pack.name,
                sticker=input_emoji,
            )
        except TelegramBadRequest as e:
            raise ApiError(f'Telegram error: {e.message}') from e
