from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sevengram.database.core import Base
from sevengram.models.sticker_type import StickerType

if TYPE_CHECKING:
    from sevengram.models.sticker import Sticker
    from sevengram.models.user import User


class StickerSet(Base):
    """A Sticker Set (Sticker Pack) in Telegram."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str]
    type: Mapped[StickerType] = mapped_column(Enum(StickerType))

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(back_populates='sticker_sets')

    stickers: Mapped[list['Sticker']] = relationship(
        back_populates='sticker_set',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
