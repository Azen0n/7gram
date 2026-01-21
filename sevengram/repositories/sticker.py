from sevengram.models import Sticker, StickerType
from sevengram.repositories.base import BaseRepository


class StickerRepository(BaseRepository):
    async def create(
        self,
        file_unique_id: str | None,
        type: StickerType,
        emoji: str | None,
        emote_id: int,
        sticker_set_id: int,
    ) -> Sticker:
        """Create a new Sticker."""
        sticker = Sticker(
            file_unique_id=file_unique_id,
            type=type,
            emoji=emoji,
            emote_id=emote_id,
            sticker_set_id=sticker_set_id,
        )
        self._session.add(sticker)
        await self._session.flush()
        return sticker
