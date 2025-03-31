from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from states import SearchState, AddBox
from database.db import DB_PATH
import aiosqlite
from datetime import datetime

main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add("📦 Мои коробки", "➕ Добавить коробку")
main_menu_keyboard.add("📍 Места хранения", "🔍 Поиск")
main_menu_keyboard.add("🗑 Удалить коробку")

cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.add("⬅ Назад")

def register(dp: Dispatcher):
    dp.register_message_handler(button_handler, state=None)
    dp.register_callback_query_handler(handle_location_choice, lambda c: c.data.startswith("location:"), state="*")
    dp.register_callback_query_handler(handle_storage_overview, lambda c: c.data.startswith("storage:"), state="*")
    dp.register_callback_query_handler(handle_delete_box, lambda c: c.data.startswith("delete_box:"), state="*")
    dp.register_callback_query_handler(handle_delete_start, lambda c: c.data.startswith("delete_from:"), state="*")
    dp.register_callback_query_handler(handle_delete_location, lambda c: c.data.startswith("delete_location:"), state="*")
    dp.register_message_handler(process_search, state=SearchState.waiting_for_keyword)
    dp.register_message_handler(start_add_box, Text(equals="➕ Добавить коробку"), state=None)
    dp.register_callback_query_handler(cancel_action_callback, lambda c: c.data == "cancel", state="*")
    dp.register_message_handler(handle_photo, content_types=types.ContentType.PHOTO, state=AddBox.waiting_for_photo)
    dp.register_message_handler(handle_description, state=AddBox.waiting_for_description)
    dp.register_message_handler(handle_location_inline, state=AddBox.waiting_for_location)

# 🔘 Главное меню: кнопки
async def button_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip().lower()

    if "удалить" in text or "мои коробки" in text or "места хранения" in text:
        locations = {}
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT location FROM boxes WHERE user_id = ?", (user_id,)) as cursor:
                async for row in cursor:
                    loc = row[0]
                    locations[loc] = locations.get(loc, 0) + 1

        if not locations:
            await message.answer("📭 *У тебя пока нет коробок.*", parse_mode="Markdown")
            return

        keyboard = types.InlineKeyboardMarkup()
        action = "delete_from" if "удалить" in text else "storage" if "места хранения" in text else "location"
        for loc, count in locations.items():
            keyboard.add(types.InlineKeyboardButton(text=f"{loc} ({count})", callback_data=f"{action}:{loc}"))

        label = {
            "delete_from": "🗑 *Выбери место для удаления:*",
            "storage": "📍 *Выберите место хранения:*",
            "location": "📦 *Выбери место:*"
        }

        await message.answer(label[action], reply_markup=keyboard, parse_mode="Markdown")
        return

    if "поиск" in text:
        await message.answer("🔍 *Введите слово для поиска:*", reply_markup=cancel_keyboard, parse_mode="Markdown")
        await SearchState.waiting_for_keyword.set()
        return

# ➕ Добавление коробки
async def start_add_box(message: types.Message, state: FSMContext):
    await message.answer("📷 Отправь фото коробки:", reply_markup=cancel_keyboard)
    await AddBox.waiting_for_photo.set()

async def handle_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer("✏️ Напиши, что находится в коробке:", reply_markup=cancel_keyboard)
    await AddBox.waiting_for_description.set()

async def handle_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("🏷 Укажи место хранения (например, 'гараж'):", reply_markup=cancel_keyboard)
    await AddBox.waiting_for_location.set()

async def handle_location_inline(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    photo = data.get("photo")
    description = data.get("description")
    location = message.text.strip().capitalize()

    if not all([photo, description, location]):
        await message.answer("⚠️ Ошибка добавления. Попробуй снова.", reply_markup=main_menu_keyboard)
        await state.finish()
        return

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO boxes (user_id, photo, description, location, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, photo, description, location, datetime.now().isoformat()))
        await db.commit()

    await message.answer("✅ Коробка добавлена!", reply_markup=main_menu_keyboard)
    await state.finish()

# ⬅ Отмена
async def cancel_action_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.answer("❌ Действие отменено.", reply_markup=main_menu_keyboard)
    await callback.answer()

# 📦 Показ коробок по месту
async def handle_location_choice(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    location = callback.data.replace("location:", "")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT photo, description, location, created_at
            FROM boxes WHERE user_id = ? AND location = ?
        """, (user_id, location)) as cursor:
            boxes = await cursor.fetchall()

    if not boxes:
        await callback.message.answer("❗ *В этом месте нет коробок.*", parse_mode="Markdown")
        await callback.answer()
        return

    for row in boxes:
        photo, description, location, created_at = row
        date_str = datetime.fromisoformat(created_at).strftime("%d.%m.%Y %H:%M")
        caption = f"*📦* `{description}`\n*📍* `{location}`\n*🗓 Добавлено:* `{date_str}`"
        await callback.message.answer_photo(photo, caption=caption, parse_mode="Markdown")

    await callback.answer()

# 📍 Полный список предметов по месту
async def handle_storage_overview(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    location = callback.data.replace("storage:", "")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT description FROM boxes WHERE user_id = ? AND location = ?
        """, (user_id, location)) as cursor:
            descriptions = await cursor.fetchall()

    if not descriptions:
        await callback.message.answer("❗ *В этом месте нет коробок.*", parse_mode="Markdown")
        await callback.answer()
        return

    all_items = []
    for (desc,) in descriptions:
        all_items += [i.strip() for i in desc.split(",")]

    formatted = "\n".join(f"- `{i}`" for i in sorted(set(all_items)))
    await callback.message.answer(
        f"*📍 Место:* `{location}`\n*📦 Коробок:* `{len(descriptions)}`\n\n*🧾 Все предметы:*\n{formatted}",
        parse_mode="Markdown"
    )
    await callback.answer()

# 🔍 Поиск
async def process_search(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    keyword = message.text.lower()

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT photo, description, location FROM boxes WHERE user_id = ?
        """, (user_id,)) as cursor:
            results = []
            async for row in cursor:
                photo, desc, loc = row
                if keyword in desc.lower():
                    results.append((photo, desc, loc))

    if not results:
        await message.answer("❗ *Ничего не найдено.*", reply_markup=main_menu_keyboard, parse_mode="Markdown")
    else:
        await message.answer(f"*🔎 Найдено:* `{len(results)}`", reply_markup=main_menu_keyboard, parse_mode="Markdown")
        for photo, desc, loc in results:
            await message.answer_photo(photo, caption=f"*📦* `{desc}`\n*📍* `{loc}`", parse_mode="Markdown")

    await state.finish()

# 🗑 Удаление — выбор коробки
async def handle_delete_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    location = callback.data.replace("delete_from:", "")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, photo, description FROM boxes WHERE user_id = ? AND location = ?
        """, (user_id, location)) as cursor:
            boxes = await cursor.fetchall()

    if not boxes:
        await callback.message.answer("❗ *В этом месте нет коробок.*", parse_mode="Markdown")
        await callback.answer()
        return

    for box_id, photo, desc in boxes:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Удалить", callback_data=f"delete_box:{box_id}"))
        await callback.message.answer_photo(photo, caption=f"*📦* `{desc}`", reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()

# ✅ Удаление коробки
async def handle_delete_box(callback: types.CallbackQuery):
    box_id = int(callback.data.split(":")[1])
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM boxes WHERE id = ?", (box_id,))
        await db.commit()

    await callback.message.answer("✅ Коробка удалена!", reply_markup=main_menu_keyboard)
    await callback.answer()

# 🧹 Удаление места (если там пусто)
async def handle_delete_location(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    location = callback.data.replace("delete_location:", "")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT COUNT(*) FROM boxes WHERE user_id = ? AND location = ?
        """, (user_id, location)) as cursor:
            (count,) = await cursor.fetchone()

    if count == 0:
        await callback.message.answer(f"✅ Место `{location}` удалено.", parse_mode="Markdown")
    else:
        await callback.message.answer(f"⚠ В месте `{location}` есть коробки. Сначала удали их.", parse_mode="Markdown")
    await callback.answer()
