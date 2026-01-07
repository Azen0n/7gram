from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from sevengram.services import EmojiPackCreateService

emoji_pack_router = Router(name='emoji_pack')


class EmojiPackAddForm(StatesGroup):
    title = State()


@emoji_pack_router.message(Command('addemojipack'))
async def add_emoji_pack(message: Message, state: FSMContext) -> None:
    """Handle a command to create a new Emoji Pack.

    Expects user to fill required data from EmojiPackAddForm in FSM.
    """
    await state.set_state(EmojiPackAddForm.title)
    await message.answer("What's your Emoji Pack title?")


@emoji_pack_router.message(EmojiPackAddForm.title)
async def process_title(message: Message, state: FSMContext, **kwargs) -> None:
    """Read user's input and create a new Emoji Pack."""
    await state.update_data(title=message.text)
    data = await state.get_data()

    emoji_pack_name = await EmojiPackCreateService(
        bot=message.bot,
        user=kwargs['user'],
        **data,
    ).execute()

    await state.clear()

    await message.answer(
        text=(
            f'<a href="https://t.me/addemoji/{emoji_pack_name}">Emoji Pack</a> '
            'successfully created!'
        ),
        parse_mode=ParseMode.HTML,
    )
