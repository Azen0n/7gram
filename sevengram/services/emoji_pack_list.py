from sevengram.database.core import get_session
from sevengram.exceptions import NotFoundError
from sevengram.models import StickerSet, StickerType, User
from sevengram.repositories import StickerSetRepository


class EmojiPackListService:
    def __init__(self, user: User):
        """Service that lists user's Emoji Packs.

        :param user: User (Emoji Packs' owner).
        :raise: NotFoundError if user has no Emoji Packs.
        """
        self._user = user

    async def execute(self) -> list[StickerSet]:
        async with get_session() as session:
            sticker_set_repository = StickerSetRepository(session)
            sticker_sets = await sticker_set_repository.list_all(
                user=self._user,
                type=StickerType.CUSTOM_EMOJI,
            )
        if not sticker_sets:
            raise NotFoundError(
                'You don’t have any Emoji Packs yet. '
                'Create your first one with the /addemojipack command.',
            )
        return sticker_sets
