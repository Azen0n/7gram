from sevengram.models import StickerSet, StickerType, User
from sevengram.repositories.base import BaseRepository


class EmojiPackRepository(BaseRepository):
    async def create(
        self,
        user: User,
        name: str,
        title: str,
    ) -> StickerSet:
        """Create a new Emoji Pack."""
        emoji_pack = StickerSet(
            user=user,
            name=name,
            title=title,
            type=StickerType.CUSTOM_EMOJI,
        )
        self._session.add(emoji_pack)
        await self._session.flush()
        return emoji_pack
