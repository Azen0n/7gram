from sevengram.database.core import get_session
from sevengram.exceptions import NotFoundError
from sevengram.models import StickerSet
from sevengram.repositories import StickerSetRepository


class StickerSetGetService:
    def __init__(self, id: int):
        """Service that gets a Sticker Set by id.

        :param id: Sticker Set's id.
        """
        self._id = id

    async def execute(self) -> StickerSet:
        async with get_session() as session:
            sticker_set_repository = StickerSetRepository(session)
            sticker_set = await sticker_set_repository.get(id=self._id)
        if sticker_set is None:
            raise NotFoundError('Sticker Set not found.')
        return sticker_set
