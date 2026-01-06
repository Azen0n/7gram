from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sevengram.database.core import Base
from sevengram.models.sticker_type import StickerType

if TYPE_CHECKING:
    from sevengram.models.sticker_set import StickerSet


class Sticker(Base):
    """A Sticker in Telegram."""

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: Unique Sticker identifier in Telegram
    type: Mapped[StickerType] = mapped_column(Enum(StickerType))
    emoji: Mapped[str | None]
    """Emoji associated with the sticker."""

    sticker_set_id: Mapped[int] = mapped_column(
        ForeignKey('sticker_set.id', ondelete='CASCADE'),
    )
    sticker_set: Mapped['StickerSet'] = relationship(back_populates='stickers')

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
