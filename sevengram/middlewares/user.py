from collections.abc import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

from sevengram.database.core import get_session
from sevengram.repositories import UserRepository


class UserMiddleware(BaseMiddleware):
    """Middleware that adds a User to a handler context."""

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, any]], Awaitable[any]],
        event: Message,
        data: dict[str, any],
    ) -> any:
        async with get_session() as session:
            user_repository = UserRepository(session)
            user, _ = await user_repository.get_or_create(event.from_user.id)
        data['user'] = user
        return await handler(event, data)
