from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from database.db import DB_PATH
import aiosqlite
from datetime import datetime

async def handle_list_boxes(message: types.Message):
    user_id = message.from_user.id
    boxes = []

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, photo, description, location, created_at
            FROM boxes
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)) as cursor:
            async for row in cursor:
                try:
                    box_id, photo, description, location, created_at = row
                    created_at = datetime.fromisoformat(created_at)
                    boxes.append({
                        "id": box_id,
                        "photo": photo,
                        "description": description,
                        "location": location,
                        "created_at": created_at
                    })
                except Exception as e:
                    await message.answer(f"⚠️ Ошибка при загрузке одной из коробок: {e}")

    if not boxes:
        await message.answer("📭 *У тебя пока нет коробок.*", parse_mode="Markdown")
        return

    await message.answer(f"*📦 Всего коробок:* `{len(boxes)}`", parse_mode="Markdown")

    for box in boxes:
        try:
            date_str = box["created_at"].strftime("%d.%m.%Y %H:%M")

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(
                    text="🗑 Удалить вещь", callback_data=f"remove_item_from:{box['id']}"
                ),
                types.InlineKeyboardButton(
                    text="❌ Удалить коробку", callback_data=f"delete_box_by_id:{box['id']}"
                )
            )

            await message.answer_photo(
                box["photo"],
                caption=(
                    f"*📦 Содержимое:* `{box['description']}`\n"
                    f"*📍 Место:* `{box['location']}`\n"
                    f"*🗓 Добавлено:* `{date_str}`"
                ),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            await message.answer(f"⚠️ Ошибка при отображении коробки: {e}")

# Регистрируем хендлер
def register(dp: Dispatcher):
    dp.register_message_handler(handle_list_boxes, Text(equals="📦 Мои коробки"))
