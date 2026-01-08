from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sevengram.constants import EmojiPackInspectAction
from sevengram.models import StickerSet


class EmojiPackCallbackData(CallbackData, prefix='emojipack'):
    """Callback data of a selected Emoji Pack from a list."""

    id: int


def build_emoji_pack_list_keyboard(emoji_packs: list[StickerSet]) -> InlineKeyboardMarkup:
    """Inline keyboard with a list of Emoji Packs."""
    builder = InlineKeyboardBuilder()
    for emoji_pack in emoji_packs:
        builder.button(
            text=emoji_pack.title,
            callback_data=EmojiPackCallbackData(id=emoji_pack.id),
        )
    builder.adjust(1, repeat=True)  # 1 button per row
    return builder.as_markup()


def build_emoji_pack_inspect_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard with a list of actions on an Emoji Pack."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Add Emoji',
                    callback_data=EmojiPackInspectAction.ADD,
                ),
            ],
        ],
    )
