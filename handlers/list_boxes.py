from aiogram import types
from aiogram.dispatcher import Dispatcher
import aiosqlite
from database.db import DB_PATH
from handlers.keyboards import get_main_keyboard
from datetime import datetime

async def list_boxes(message: types.Message):
    user_id = message.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT id, photo, description, location, created_at 
            FROM boxes WHERE user_id = ?
        """, (user_id,))
        boxes = await cursor.fetchall()

    if not boxes:
        await message.answer("📭 У тебя пока нет коробок.", reply_markup=get_main_keyboard(False))
        return

    for box in boxes:
        box_id = box['id']
        photo = box['photo']
        description = box['description']
        location = box['location']
        created_at = box['created_at']

        # Проверка на заглушку (локальный файл)
        if photo and isinstance(photo, str) and (photo.endswith(".jpg") or photo.endswith(".png")):
            try:
                with open(photo, "rb") as f:
                    photo = f.read()
            except Exception as e:
                print(f"[ERROR] Не удалось открыть фото: {e}")
                photo = None

        # Формируем клавиатуру
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.row(
            types.InlineKeyboardButton("✏ Добавить предмет", callback_data=f"add_item:{box_id}:0"),
            types.InlineKeyboardButton("🗑 Удалить вещь", callback_data=f"remove_item_from:{box_id}")
        )
        keyboard.row(
            types.InlineKeyboardButton("❌ Удалить коробку", callback_data=f"confirm_delete_box:{box_id}")
        )

        date_str = datetime.fromisoformat(created_at).strftime("%d.%m.%Y %H:%M")
        caption = (
            f"📦 <b>Содержимое:</b> {description}\n"
            f"📍 <b>Место:</b> {location}\n"
            f"🗓 <b>Добавлено:</b> {date_str}"
        )

        try:
            if photo:
                await message.answer_photo(
                    photo=photo,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            else:
                await message.answer(
                    text=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        except Exception as e:
            print(f"[ERROR] Ошибка при отправке коробки: {e}")
            await message.answer("⚠ Не удалось отобразить коробку.", reply_markup=get_main_keyboard(True))

def register(dp: Dispatcher):
    dp.register_message_handler(list_boxes, commands=["list"])
