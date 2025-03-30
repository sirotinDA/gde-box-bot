from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from handlers.add_box import BOXES

async def handle_list_boxes(message: types.Message):
    user_id = message.from_user.id
    user_boxes = BOXES.get(user_id, [])

    if not user_boxes:
        await message.answer("📭 *У тебя пока нет коробок.*", parse_mode="Markdown")
        return

    await message.answer(f"*📦 Всего коробок:* `{len(user_boxes)}`", parse_mode="Markdown")

    for box in user_boxes:
        created_at = box.get("created_at")
        date_str = created_at.strftime("%d.%m.%Y %H:%M") if created_at else "неизвестна"

        await message.answer_photo(
            box["photo"],
            caption=(
                f"*📦 Содержимое:* `{box['description']}`\n"
                f"*📍 Место:* `{box['location']}`\n"
                f"*🗓 Добавлено:* `{date_str}`"
            ),
            parse_mode="Markdown"
        )


def register(dp: Dispatcher):
    dp.register_message_handler(handle_list_boxes, Text(equals="📦 Мои коробки"))
