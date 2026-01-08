from sqlalchemy import select

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

    async def list(self, user: User) -> list[StickerSet]:
        """Select all user's Emoji Packs."""
        stmt = (
            select(StickerSet)
            .where(
                StickerSet.user_id == user.id,
                StickerSet.type == StickerType.CUSTOM_EMOJI,
            )
            .order_by(StickerSet.created_at)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()  # type: ignore

    async def get(self, id: int) -> StickerSet | None:
        """Get an Emoji Pack by id."""
        stmt = select(StickerSet).where(
            StickerSet.id == id,
            StickerSet.type == StickerType.CUSTOM_EMOJI,
        )
        result = await self._session.execute(stmt)
        return result.scalars().one_or_none()
