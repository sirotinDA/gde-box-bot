from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from database.db import DB_PATH
import aiosqlite
from datetime import datetime

async def handle_list_boxes(message: types.Message):
    user_id = message.from_user.id
    boxes = []

    # Получаем коробки пользователя из базы данных
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT photo, description, location, created_at
            FROM boxes
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)) as cursor:
            async for row in cursor:
                photo, description, location, created_at = row
                created_at = datetime.fromisoformat(created_at)
                boxes.append({
                    "photo": photo,
                    "description": description,
                    "location": location,
                    "created_at": created_at
                })

    if not boxes:
        await message.answer("📭 *У тебя пока нет коробок.*", parse_mode="Markdown")
        return

    await message.answer(f"*📦 Всего коробок:* `{len(boxes)}`", parse_mode="Markdown")

    for box in boxes:
        date_str = box["created_at"].strftime("%d.%m.%Y %H:%M")
        await message.answer_photo(
            box["photo"],
            caption=(
                f"*📦 Содержимое:* `{box['description']}`\n"
                f"*📍 Место:* `{box['location']}`\n"
                f"*🗓 Добавлено:* `{date_str}`"
            ),
            parse_mode="Markdown"
        )

# Регистрируем хендлер
def register(dp: Dispatcher):
    dp.register_message_handler(handle_list_boxes, Text(equals="📦 Мои коробки"))
