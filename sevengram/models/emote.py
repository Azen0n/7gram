from datetime import datetime

from sqlalchemy import Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from sevengram.database.core import Base
from sevengram.models.emote_format import EmoteFormat
from sevengram.models.emote_source import EmoteSource


class Emote(Base):
    """An Emote."""

    id: Mapped[int] = mapped_column(primary_key=True)
    file_id: Mapped[str]
    """File identifier, which can be used to reuse the file on Telegram servers."""

    source: Mapped[EmoteSource] = mapped_column(Enum(EmoteSource))
    external_id: Mapped[str]
    """Emote identifier from external source."""
    name: Mapped[str]
    file_url: Mapped[str]
    """File URL from external source."""
    format: Mapped[EmoteFormat] = mapped_column(Enum(EmoteFormat))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
