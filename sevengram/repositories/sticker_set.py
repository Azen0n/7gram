from sqlalchemy import select
from sqlalchemy.orm import joinedload

from sevengram.models import StickerSet, StickerType, User
from sevengram.repositories.base import BaseRepository


class StickerSetRepository(BaseRepository):
    async def create(
        self,
        user: User,
        name: str,
        title: str,
        type: StickerType,
    ) -> StickerSet:
        """Create a new Sticker Set."""
        sticker_set = StickerSet(
            user=user,
            name=name,
            title=title,
            type=type,
        )
        self._session.add(sticker_set)
        await self._session.flush()
        return sticker_set

    async def list_all(self, user: User, type: StickerType) -> list[StickerSet]:
        """Select all user's Sticker Sets."""
        stmt = (
            select(StickerSet)
            .where(
                StickerSet.user_id == user.id,
                StickerSet.type == type,
            )
            .order_by(StickerSet.created_at)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()  # type: ignore

    async def get(self, id: int) -> StickerSet | None:
        """Get a Sticker Set by id."""
        stmt = (
            select(StickerSet)
            .where(StickerSet.id == id)
            .options(joinedload(StickerSet.user))
        )
        result = await self._session.execute(stmt)
        return result.scalars().one_or_none()
