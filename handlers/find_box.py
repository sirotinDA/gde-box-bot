from aiogram import types
from aiogram.dispatcher import Dispatcher
import aiosqlite
from database.db import DB_PATH

async def find_box(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args().strip().lower()

    if not args:
        await message.answer("❗ Укажи, что искать. Пример:\n`/find насос`", parse_mode="Markdown")
        return

    results = []
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT photo, description, location FROM boxes WHERE user_id = ?", (user_id,)
        ) as cursor:
            async for row in cursor:
                photo, desc, loc = row
                if args in desc.lower():
                    results.append((photo, desc, loc))

    if not results:
        await message.answer("🔍 *Ничего не найдено.*", parse_mode="Markdown")
    else:
        await message.answer(f"*🔎 Найдено:* `{len(results)}`", parse_mode="Markdown")
        for photo, desc, loc in results:
            await message.answer_photo(
                photo,
                caption=f"*📦* `{desc}`\n*📍* `{loc}`",
                parse_mode="Markdown"
            )

def register(dp: Dispatcher):
    dp.register_message_handler(find_box, commands=["find"])
