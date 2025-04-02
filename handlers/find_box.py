from aiogram import types
from aiogram.dispatcher import Dispatcher
import aiosqlite
from database.db import DB_PATH
from handlers.keyboards import main_menu_keyboard, box_action_keyboard

async def find_box(message: types.Message):
    try:
        user_id = message.from_user.id
        search_query = (message.text or "").strip()

        if not search_query:
            await message.answer(
                "🔍 Введите что искать:\nПример: <code>кабель</code>",
                parse_mode="HTML",
                reply_markup=main_menu_keyboard
            )
            return

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT id, photo, description, location 
                FROM boxes 
                WHERE user_id = ? AND description LIKE ?
            """, (user_id, f"%{search_query}%"))

            results = await cursor.fetchall()

        if not results:
            await message.answer(
                f"❌ По запросу \"{search_query}\" ничего не найдено",
                reply_markup=main_menu_keyboard
            )
            return

        found_msg = await message.answer(f"🔍 Найдено: {len(results)}", reply_markup=main_menu_keyboard)

        for box in results:
            box_id = box['id']
            description = box['description']
            location = box['location']
            photo = box['photo']

            if photo and isinstance(photo, str) and (photo.endswith(".jpg") or photo.endswith(".png")):
                try:
                    with open(photo, "rb") as f:
                        photo = f.read()
                except Exception as e:
                    print(f"[ERROR] Ошибка открытия файла заглушки: {e}")
                    photo = None

            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                types.InlineKeyboardButton("✏ Добавить предмет", callback_data=f"add_item:{box_id}:{found_msg.message_id}"),
                types.InlineKeyboardButton("🗑 Удалить вещь", callback_data=f"remove_item_from:{box_id}"
                )
            )
            keyboard.add(
                types.InlineKeyboardButton("❌ Удалить коробку", callback_data=f"delete_box_by_id:{box_id}:{found_msg.message_id}")
            )

            # Добавляем кнопку перемещения, если есть >1 место
            async with aiosqlite.connect(DB_PATH) as db_check:
                cursor = await db_check.execute("SELECT DISTINCT location FROM boxes WHERE user_id = ?", (user_id,))
                locations = await cursor.fetchall()
                if len(locations) > 1:
                    keyboard.add(types.InlineKeyboardButton("🔄 Переместить коробку", callback_data=f"move_box:{box_id}"))
                    
            caption = (
                f"📦 <b>Содержимое:</b> {description}\n"
                f"📍 <b>Место:</b> {location}"
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
                print(f"[ERROR] Ошибка при отправке: {e}")
                await message.answer(
                    "⚠ Ошибка при отправке результата.",
                    reply_markup=main_menu_keyboard
                )

    except Exception as e:
        print(f"[FATAL ERROR] Ошибка в find_box: {e}")
        await message.answer("⚠ Произошла ошибка при поиске", reply_markup=main_menu_keyboard)

def register(dp: Dispatcher):
    dp.register_message_handler(find_box, commands=["find"])
