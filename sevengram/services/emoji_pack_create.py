from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from sevengram.config import settings
from sevengram.database.core import get_session
from sevengram.exceptions import ValidationError
from sevengram.models import StickerType, User
from sevengram.repositories import EmojiPackRepository
from sevengram.services.utils import emote, generate_sticker_set_name


class EmojiPackCreateService:
    def __init__(
        self,
        bot: Bot,
        user: User,
        title: str,
    ):
        """Service that creates a new Emoji Pack.

        :param bot: Telegram bot instance.
        :param user: User (Emoji Pack's owner).
        :param title: Emoji Pack's title.
        """
        self._bot = bot
        self._user = user
        self._title = title

    async def execute(self) -> str:
        """Create a new Emoji Pack in Telegram and database.

        :return: Emoji Pack's name (https://t.me/addemoji/name).
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
        """Create Emoji Pack in Telegram.

        :return: is_created flag.
        """
        try:
            return await self._bot.create_new_sticker_set(
                user_id=self._user.telegram_id,
                name=name,
                title=self._title,
                sticker_type=StickerType.CUSTOM_EMOJI,
                stickers=[emote],
            )
        except TelegramBadRequest as e:
            raise ValidationError(f'Telegram error: {e.message}') from e

    async def _create_in_database(self, name: str):
        """Create Emoji Pack in database and return its id."""
        async with get_session() as session:
            emoji_pack_repository = EmojiPackRepository(session)
            await emoji_pack_repository.create(
                user=self._user,
                name=name,
                title=self._title,
            )
