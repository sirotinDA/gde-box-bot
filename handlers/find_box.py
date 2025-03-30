from aiogram import types
from aiogram.dispatcher import Dispatcher
from handlers.add_box import BOXES

async def find_box(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args().strip().lower()

    if not args:
        await message.answer("❗ Укажи, что искать. Пример:\n`/find насос`", parse_mode="Markdown")
        return

    boxes = BOXES.get(user_id, [])
    results = [b for b in boxes if args in b["description"].lower()]

    if not results:
        await message.answer("🔍 *Ничего не найдено.*", parse_mode="Markdown")
    else:
        await message.answer(f"*🔎 Найдено:* `{len(results)}`", parse_mode="Markdown")
        for box in results:
            await message.answer_photo(
                box["photo"],
                caption=f"*📦* `{box['description']}`\n*📍* `{box['location']}`",
                parse_mode="Markdown"
            )

def register(dp: Dispatcher):
    dp.register_message_handler(find_box, commands=["find"])
