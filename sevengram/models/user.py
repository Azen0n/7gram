from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sevengram.database.core import Base

if TYPE_CHECKING:
    from sevengram.models.sticker_set import StickerSet


class User(Base):
    """A Telegram User."""

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)

    sticker_sets: Mapped[list['StickerSet']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
