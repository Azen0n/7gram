from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from sevengram.api.seventv import SevenTvApiClient
from sevengram.config import settings
from sevengram.constants import EmojiPackInspectAction
from sevengram.exceptions import ValidationError
from sevengram.keyboards.emoji_pack import (
    EmojiPackCallbackData,
    build_emoji_pack_inspect_keyboard,
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

    inspect = State()
    add_emoji = State()


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
    emoji_packs = await EmojiPackListService(user=user).execute()

    keyboard = build_emoji_pack_list_keyboard(emoji_packs)
    await state.set_state(EmojiPackInspectState.inspect)

    await message.answer(
        text='Choose an Emoji Pack to inspect',
        reply_markup=keyboard,
    )


@emoji_pack_router.callback_query(EmojiPackInspectState.inspect)
async def inspect_emoji_pack(query: CallbackQuery, state: FSMContext) -> None:
    """Handle a command to inspect an Emoji Pack of a user."""
    callback_data = EmojiPackCallbackData.unpack(query.data)
    emoji_pack = await EmojiPackGetService(id=callback_data.id).execute()

    keyboard = build_emoji_pack_inspect_keyboard()
    await state.set_state(EmojiPackInspectState.add_emoji)

    await query.message.answer(
        text=f'[{emoji_pack.title}](https://t.me/addemoji/{emoji_pack.name})',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )
    await query.answer()


@emoji_pack_router.callback_query(
    EmojiPackInspectState.add_emoji,
    F.data == EmojiPackInspectAction.ADD,
)
async def add_emoji_waiting_for_url(query: CallbackQuery) -> None:
    """Handle a command to add a new Emoji to an Emoji Pack.

    Waits for an Emote URL in user input.
    """
    await query.message.answer(
        text='Send URL to a 7TV emote. Browse emotes here: https://7tv.app/emotes',
        parse_mode=ParseMode.MARKDOWN,
    )
    await query.answer()


@emoji_pack_router.message(EmojiPackInspectState.add_emoji)
async def add_emoji(message: Message, state: FSMContext) -> None:
    """Handle a command to add a new Emoji to an Emoji Pack."""
    if not message.text.startswith('https://7tv.app/'):
        raise ValidationError('URL must start with https://7tv.app/')

    emote_id = message.text.strip().split('/')[-1]

    await message.answer(f'Fetching emote with id={emote_id} from 7TV...')

    client = SevenTvApiClient(settings.SEVENTV_URL.encoded_string())
    data = await client.fetch_emote(emote_id)
    emote_name = data['emotes']['emote']['defaultName']

    await message.answer(f'Emote name from 7TV: {emote_name}')
