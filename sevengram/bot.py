import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message

from sevengram.config import settings
from sevengram.exceptions import ValidationError
from sevengram.handlers import routers
from sevengram.middlewares import UserMiddleware

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f'Hello {message.from_user.first_name}')


@dp.error(ExceptionTypeFilter(ValidationError), F.update.message.as_('message'))
async def validation_error_handler(event: ErrorEvent, message: Message):
    await message.answer(f'Validation error: {event.exception}')


@dp.error(F.update.message.as_('message'))
async def error_handler(event: ErrorEvent, message: Message):
    await message.answer(f'Wowzers! Unhandled exception! BatChesting\n{event.exception}')


async def main() -> None:
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp.include_routers(*routers)
    dp.message.middleware(UserMiddleware())
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
