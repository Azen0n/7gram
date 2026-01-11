from sevengram.models import Sticker, StickerType
from sevengram.repositories.base import BaseRepository


class EmojiRepository(BaseRepository):
    async def create(
        self,
        file_unique_id: str | None,
        emoji: str | None,
        emote_id: int,
        sticker_set_id: int,
    ) -> Sticker:
        """Create a new Emote."""
        emoji = Sticker(
            file_unique_id=file_unique_id,
            type=StickerType.CUSTOM_EMOJI,
            emoji=emoji,
            emote_id=emote_id,
            sticker_set_id=sticker_set_id,
        )
        self._session.add(emoji)
        await self._session.flush()
        return emoji
