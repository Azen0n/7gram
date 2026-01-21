from sevengram.database.core import get_session
from sevengram.exceptions import NotFoundError
from sevengram.models import StickerSet, StickerType, User
from sevengram.repositories import StickerSetRepository


class StickerSetListService:
    def __init__(self, user: User, type: StickerType):
        """Service that lists user's Sticker Sets.

        :param user: User (Sticker Sets' owner).
        :param type: Type of Sticker Set.
        :raise: NotFoundError if user has no Sticker Sets.
        """
        self._user = user
        self._type = type

    async def execute(self) -> list[StickerSet]:
        async with get_session() as session:
            sticker_set_repository = StickerSetRepository(session)
            sticker_sets = await sticker_set_repository.list_all(
                user=self._user,
                type=self._type,
            )
        if not sticker_sets:
            raise NotFoundError(
                'You don’t have any Sticker Sets yet. '
                'Create your first one with the /addemojipack '
                'or the /addstickerpack command.',
            )
        return sticker_sets
