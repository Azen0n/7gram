from sqlalchemy import select

from sevengram.models import User
from sevengram.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get_or_create(self, telegram_id: int) -> tuple[User, bool]:
        """Return an existing User or create a new one.

        :return: tuple of User and is_created flag.
        """
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is not None:
            return user, False

        user = User(telegram_id=telegram_id)
        self._session.add(user)
        await self._session.flush()
        return user, True
