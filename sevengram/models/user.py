from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from sevengram.database.core import Base


class User(Base):
    """A Telegram User."""

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
