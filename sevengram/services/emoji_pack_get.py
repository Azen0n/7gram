from sevengram.database.core import get_session
from sevengram.exceptions import NotFoundError
from sevengram.models import StickerSet
from sevengram.repositories import StickerSetRepository


class EmojiPackGetService:
    def __init__(self, id: int):
        """Service that gets an Emoji Pack by id.

        :param id: Emoji Pack's id.
        """
        self._id = id

    async def execute(self) -> StickerSet | None:
        async with get_session() as session:
            sticker_set_repository = StickerSetRepository(session)
            sticker_set = await sticker_set_repository.get(id=self._id)
        if sticker_set is None:
            raise NotFoundError('Emoji Pack not found.')
        return sticker_set
