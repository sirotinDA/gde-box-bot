from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
import aiosqlite
from database.db import DB_PATH
from handlers.keyboards import get_main_keyboard
from states import AddItemToBox, AddItemFromMenu
from datetime import datetime

# 🗑 Удалить вещь — выбор
async def remove_item_from_box(callback: types.CallbackQuery):
    box_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT description, photo, location FROM boxes WHERE id = ? AND user_id = ?", (box_id, user_id))
        row = await cursor.fetchone()

        if not row:
            await callback.message.answer("❌ Коробка не найдена.", reply_markup=get_main_keyboard(False))
            return

        items = [item.strip() for item in row["description"].split(",") if item.strip()]

        if not items:
            await callback.message.answer("📭 Коробка уже пустая.", reply_markup=get_main_keyboard(True))
            return

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for item in items:
            keyboard.add(
                types.InlineKeyboardButton(text=f"❌ {item}", callback_data=f"confirm_remove_item:{box_id}:{item}")
            )

        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()

async def confirm_remove_item(callback: types.CallbackQuery):
    _, box_id, item_to_remove = callback.data.split(":", 2)
    box_id = int(box_id)
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT description, photo, location FROM boxes WHERE id = ? AND user_id = ?", (box_id, user_id))
        box = await cursor.fetchone()

        if not box:
            await callback.message.answer("❌ Коробка не найдена.", reply_markup=get_main_keyboard(True))
            return

        description = box["description"]
        photo = box["photo"]
        location = box["location"]

        # Удаляем выбранный предмет
        items = [item.strip() for item in description.split(",") if item.strip().lower() != item_to_remove.lower()]
        new_desc = ", ".join(items)

        await db.execute("UPDATE boxes SET description = ? WHERE id = ?", (new_desc, box_id))
        await db.commit()

    # Удаляем старое сообщение
    try:
        await callback.message.delete()
    except:
        pass

    # Новая inline-клавиатура
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.row(
        types.InlineKeyboardButton("✏ Добавить предмет", callback_data=f"add_item:{box_id}:0"),
        types.InlineKeyboardButton("🗑 Удалить вещь", callback_data=f"remove_item_from:{box_id}")
    )
    keyboard.row(
        types.InlineKeyboardButton("❌ Удалить коробку", callback_data=f"confirm_delete_box:{box_id}")
    )

    caption = (
        f"📦 <b>Содержимое:</b> {new_desc or '—'}\n"
        f"📍 <b>Место:</b> {location}"
    )

    # Используем file_id, если фото не заглушка
    if photo != "no_photo.jpg":
        await callback.message.bot.send_photo(
            chat_id=callback.from_user.id,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await callback.message.bot.send_message(
            chat_id=callback.from_user.id,
            text=caption,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text="✅ Вещь удалена!",
        reply_markup=get_main_keyboard(True)
    )

    await callback.answer()

# ✏ Добавить предмет — старт
async def start_add_item(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    box_id = int(parts[1])
    await state.update_data(box_id=box_id)
    await callback.message.answer("✍ Введи предмет, который хочешь добавить в коробку:")
    await AddItemToBox.waiting_for_text.set()
    await callback.answer()

# ✏ Добавить предмет — текст
async def add_item_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    box_id = data["box_id"]
    new_item = message.text.strip()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT description, photo, location FROM boxes WHERE id = ?", (box_id,))
        box = await cursor.fetchone()

        if not box:
            await message.answer("❌ Коробка не найдена.", reply_markup=get_main_keyboard(False))
            await state.finish()
            return

        old_desc = box["description"]
        photo = box["photo"]
        location = box["location"]

        updated_desc = f"{old_desc}, {new_item}" if old_desc else new_item
        await db.execute("UPDATE boxes SET description = ? WHERE id = ?", (updated_desc, box_id))
        await db.commit()

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.row(
        types.InlineKeyboardButton("✏ Добавить предмет", callback_data=f"add_item:{box_id}:0"),
        types.InlineKeyboardButton("🗑 Удалить вещь", callback_data=f"remove_item_from:{box_id}")
    )
    keyboard.row(
        types.InlineKeyboardButton("❌ Удалить коробку", callback_data=f"confirm_delete_box:{box_id}")
    )

    caption = (
        f"📦 <b>Содержимое:</b> {updated_desc}\n"
        f"📍 <b>Место:</b> {location}"
    )

    if photo and (photo.endswith(".jpg") or photo.endswith(".png")):
        try:
            with open(photo, "rb") as f:
                photo = f.read()
        except:
            photo = None
    else:
        photo = None

    if photo:
        await message.answer_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(caption, parse_mode="HTML", reply_markup=keyboard)

    await message.answer("✅ Предмет добавлен!", reply_markup=get_main_keyboard(True))
    await state.finish()

# Регистрация
def register(dp: Dispatcher):
    dp.register_callback_query_handler(remove_item_from_box, lambda c: c.data.startswith("remove_item_from:"), state="*")
    dp.register_callback_query_handler(confirm_remove_item, lambda c: c.data.startswith("confirm_remove_item:"), state="*")
    dp.register_callback_query_handler(start_add_item, lambda c: c.data.startswith("add_item:"), state="*")
    dp.register_message_handler(add_item_text, state=AddItemToBox.waiting_for_text)
