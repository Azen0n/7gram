from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from sevengram.keyboards.emoji_pack import (
    EmojiPackCallbackData,
    build_emoji_pack_list_keyboard,
)
from sevengram.models import User
from sevengram.services import (
    EmojiPackCreateService,
    EmojiPackGetService,
    EmojiPackListService,
)

emoji_pack_router = Router(name='emoji_pack')


class EmojiPackAddForm(StatesGroup):
    """FSM form to create a new Emoji Pack."""

    title = State()


class EmojiPackInspectState(StatesGroup):
    """State group to inspect an Emoji Pack from a list."""

    in_progress = State()


@emoji_pack_router.message(Command('addemojipack'))
async def add_emoji_pack(message: Message, state: FSMContext) -> None:
    """Handle a command to create a new Emoji Pack.

    Expects user to fill required data from EmojiPackAddForm in FSM.
    """
    await state.set_state(EmojiPackAddForm.title)
    await message.answer("What's your Emoji Pack title?")


@emoji_pack_router.message(EmojiPackAddForm.title)
async def process_title(message: Message, state: FSMContext, user: User) -> None:
    """Read user's input and create a new Emoji Pack."""
    await state.update_data(title=message.text)
    data = await state.get_data()

    emoji_pack_name = await EmojiPackCreateService(
        bot=message.bot,
        user=user,
        **data,
    ).execute()

    await state.clear()

    await message.answer(
        text=(
            f'[Emoji Pack](https://t.me/addemoji/{emoji_pack_name}) successfully created!'
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@emoji_pack_router.message(Command('listemojipacks'))
async def list_emoji_packs(message: Message, state: FSMContext, user: User) -> None:
    """Handle a command to list Emoji Packs of a user."""
    await state.set_state(EmojiPackInspectState.in_progress)

    emoji_packs = await EmojiPackListService(user=user).execute()
    keyboard = build_emoji_pack_list_keyboard(emoji_packs)

    await message.answer(
        text='Choose an Emoji Pack to inspect',
        reply_markup=keyboard,
    )


@emoji_pack_router.callback_query(EmojiPackInspectState.in_progress)
async def inspect_emoji_pack(query: CallbackQuery) -> None:
    """Handle a command to inspect an Emoji Pack of a user."""
    callback_data = EmojiPackCallbackData.unpack(query.data)
    emoji_pack = await EmojiPackGetService(id=callback_data.id).execute()

    await query.message.answer(
        text=f'[{emoji_pack["title"]}](https://t.me/addemoji/{emoji_pack["name"]})',
        parse_mode=ParseMode.MARKDOWN,
    )
