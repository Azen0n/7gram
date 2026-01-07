import uuid

from aiogram.types import BufferedInputFile, InputSticker


def generate_sticker_set_name(bot_username: str) -> str:
    """Generate valid Telegram Sticker Set name.

    Example: custom_6ffd570fec99468ebe96fa9d04de6952_by_sevengram_bot.
    """
    return f'custom_{uuid.uuid4()}_by_{bot_username}'.replace('-', '')


emote = InputSticker(
    sticker=BufferedInputFile.from_file(path='emote.png'),
    format='static',
    emoji_list=['😏'],
    keywords=['forsenE'],
)
