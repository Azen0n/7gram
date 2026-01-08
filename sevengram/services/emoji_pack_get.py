from sevengram.database.core import get_session
from sevengram.exceptions import NotFoundError
from sevengram.models import StickerSet
from sevengram.repositories import EmojiPackRepository


class EmojiPackGetService:
    def __init__(self, id: int):
        """Service that gets an Emoji Pack by id.

        :param id: Emoji Pack's id.
        """
        self._id = id

    async def execute(self) -> StickerSet | None:
        async with get_session() as session:
            emoji_pack_repository = EmojiPackRepository(session)
            emoji_pack = await emoji_pack_repository.get(id=self._id)
        if emoji_pack is None:
            raise NotFoundError('Emoji Pack not found.')
        return emoji_pack
