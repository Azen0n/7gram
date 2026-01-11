from sevengram.database.core import get_session
from sevengram.exceptions import NotFoundError
from sevengram.models import StickerSet, User
from sevengram.repositories import EmojiPackRepository


class EmojiPackListService:
    def __init__(self, user: User):
        """Service that lists user's Emoji Packs.

        :param user: User (Emoji Packs' owner).
        :raise: NotFoundError if user has no Emoji Packs.
        """
        self._user = user

    async def execute(self) -> list[StickerSet]:
        async with get_session() as session:
            emoji_pack_repository = EmojiPackRepository(session)
            emoji_packs = await emoji_pack_repository.list_all(user=self._user)
        if not emoji_packs:
            raise NotFoundError(
                'You don’t have any Emoji Packs yet. '
                'Create your first one with the /addemojipack command.',
            )
        return emoji_packs
