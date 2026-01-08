from sevengram.database.core import get_session
from sevengram.models import StickerSet, User
from sevengram.repositories import EmojiPackRepository


class EmojiPackListService:
    def __init__(self, user: User):
        """Service that lists user's Emoji Packs.

        :param user: User (Emoji Packs' owner).
        """
        self._user = user

    async def execute(self) -> list[dict]:
        async with get_session() as session:
            emoji_pack_repository = EmojiPackRepository(session)
            emoji_packs = await emoji_pack_repository.list(user=self._user)
        return self._serialize(emoji_packs)

    def _serialize(self, emoji_packs: list[StickerSet]) -> list[dict]:
        """Serialize a list of Emoji Packs."""
        data = []
        for emoji_pack in emoji_packs:
            data.append(
                {
                    'id': emoji_pack.id,
                    'title': emoji_pack.title,
                    'name': emoji_pack.name,
                },
            )
        return data
