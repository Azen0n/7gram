from sevengram.database.core import get_session
from sevengram.models import StickerSet
from sevengram.repositories import EmojiPackRepository


class EmojiPackGetService:
    def __init__(self, id: int):
        """Service that gets an Emoji Pack by id.

        :param id: Emoji Pack's id.
        """
        self._id = id

    async def execute(self) -> dict:
        async with get_session() as session:
            emoji_pack_repository = EmojiPackRepository(session)
            emoji_pack = await emoji_pack_repository.get(id=self._id)
        return self._serialize(emoji_pack)

    def _serialize(self, emoji_pack: StickerSet) -> dict:
        """Serialize an instance of Emoji Pack."""
        return {
            'id': emoji_pack.id,
            'title': emoji_pack.title,
            'name': emoji_pack.name,
        }
