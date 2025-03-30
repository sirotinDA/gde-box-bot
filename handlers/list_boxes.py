from aiogram import types
from aiogram.dispatcher import Dispatcher
from handlers.add_box import BOXES

async def list_all_boxes(message: types.Message):
    user_id = message.from_user.id
    user_boxes = BOXES.get(user_id, [])

    if not user_boxes:
        await message.answer("📭 *У тебя пока нет коробок.*", parse_mode="Markdown")
        return

    await message.answer(f"*📦 Всего коробок:* `{len(user_boxes)}`", parse_mode="Markdown")

    for box in user_boxes:
        await message.answer_photo(
            box["photo"],
            caption=(
                f"*📦 Содержимое:* `{box['description']}`\n"
                f"*📍 Место:* `{box['location']}`"
            ),
            parse_mode="Markdown"
        )

def register(dp: Dispatcher):
    dp.register_message_handler(list_all_boxes, commands=["boxes"])
