from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputSticker

from sevengram.config import settings
from sevengram.constants import DEFAULT_EMOJI
from sevengram.database.core import get_session
from sevengram.exceptions import ApiError, ValidationError
from sevengram.models import StickerType, User
from sevengram.repositories import StickerSetRepository
from sevengram.services.utils import generate_sticker_set_name


class StickerSetCreateService:
    def __init__(
        self,
        bot: Bot,
        user: User,
        title: str,
        type: StickerType,
    ):
        """Service that creates a new Sticker Set.

        :param bot: Telegram bot instance.
        :param user: User (Sticker Set's owner).
        :param title: Sticker Set's title.
        :param type: Sticker Set's type.
        """
        self._bot = bot
        self._user = user
        self._title = title
        self._type = type

    async def execute(self) -> str:
        """Create a new Sticker Set in Telegram and database.

        :return: Sticker Set's name
          (https://t.me/addemoji/name or https://t.me/addstickers/name).
        """
        self._validate()
        name = generate_sticker_set_name(settings.BOT_USERNAME)
        is_created = await self._create_in_telegram(name)
        if not is_created:
            raise ValidationError('Failed to create sticker set. Please try again.')
        await self._create_in_database(name)
        return name

    def _validate(self):
        self._validate_title()

    def _validate_title(self):
        if not (1 <= len(self._title) <= 64):
            raise ValidationError('Title must be 1-64 characters.')

    async def _create_in_telegram(self, name: str) -> bool:
        """Create Sticker Set in Telegram.

        :return: is_created flag.
        """
        sticker_placeholder = self._get_initial_sticker_placeholder()
        try:
            return await self._bot.create_new_sticker_set(
                user_id=self._user.telegram_id,
                name=name,
                title=self._title,
                sticker_type=self._type,
                stickers=[sticker_placeholder],
            )
        except TelegramBadRequest as e:
            raise ApiError(f'Telegram error: {e.message}') from e

    def _get_initial_sticker_placeholder(self) -> InputSticker:
        """Return an initial input Sticker to satisfy Sticker Set's requirement for
        at least 1 sticker.

        Initial Sticker is not tracked in the database at the moment.
        """
        if self._type == StickerType.CUSTOM_EMOJI:
            placeholder_file_id = settings.CUSTOM_EMOJI_PLACEHOLDER_FILE_ID
        else:
            placeholder_file_id = settings.REGULAR_STICKER_PLACEHOLDER_FILE_ID
        return InputSticker(
            sticker=placeholder_file_id,
            format='static',
            emoji_list=[DEFAULT_EMOJI],
        )

    async def _create_in_database(self, name: str):
        """Create Sticker Set in database and return its id."""
        async with get_session() as session:
            sticker_set_repository = StickerSetRepository(session)
            await sticker_set_repository.create(
                user=self._user,
                name=name,
                title=self._title,
                type=self._type,
            )
