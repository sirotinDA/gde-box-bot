from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters import Text
from states import SearchState, AddBox
from database.db import DB_PATH
import aiosqlite
from datetime import datetime
from handlers import find_box
from handlers.keyboards import main_menu_keyboard, cancel_keyboard, photo_keyboard

# Главное меню кнопки
main_menu_keyboard = main_menu_keyboard
cancel_keyboard = cancel_keyboard

# Кнопки: стартовые команды
async def button_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text.strip().lower()

    if "удалить коробку" in text or "места хранения" in text:
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
        action = "delete_from" if "удалить" in text else "storage"
        for loc, count in locations.items():
            keyboard.add(types.InlineKeyboardButton(text=f"{loc} ({count})", callback_data=f"{action}:{loc}"))

        label = {
            "delete_from": "🗑 *Выбери место для удаления:*",
            "storage": "📍 *Выберите место хранения:*"
        }

        await message.answer(label[action], reply_markup=keyboard, parse_mode="Markdown")
        return

    if "поиск" in text:
        await message.answer("🔍 *Введите слово для поиска:*", reply_markup=cancel_keyboard, parse_mode="Markdown")
        await SearchState.waiting_for_keyword.set()
        return

# Поиск по описанию
async def process_search(message: types.Message, state: FSMContext):
    await find_box.find_box(message)
    await state.finish()

# Добавление коробки — начало
async def start_add_box(message: types.Message, state: FSMContext):
    await message.answer("📷 Отправь фото коробки или нажми \"Пропустить фото\"", reply_markup=photo_keyboard)
    await AddBox.waiting_for_photo.set()

async def handle_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer(
        "✏️ Напиши, что находится в коробке:\n\n"
        "_Перечисли предметы через запятую, например:_ отвертка, фонарик, батарейки",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )
    await AddBox.waiting_for_description.set()

async def skip_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo="no_photo.jpg")
    await message.answer(
        "✏️ Напиши, что находится в коробке:\n\n"
        "_Перечисли предметы через запятую, например:_ отвертка, фонарик, батарейки",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )
    await AddBox.waiting_for_description.set()


async def handle_description(message: types.Message, state: FSMContext):
    desc = message.text.strip()
    if not desc:
        await message.answer("❗ Опиши содержимое словами", reply_markup=cancel_keyboard)
        return
    await state.update_data(description=desc)

    user_id = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT DISTINCT location FROM boxes WHERE user_id = ?", (user_id,))
        locations = await cursor.fetchall()

    if locations:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for loc in locations:
            keyboard.insert(types.InlineKeyboardButton(text=loc[0], callback_data=f"select_location:{loc[0]}"))
        keyboard.add(types.InlineKeyboardButton("✍ Ввести вручную", callback_data="manual_location"))
        await message.answer("📍 Выберите *место хранения* или введите вручную:", parse_mode="Markdown", reply_markup=keyboard)
    else:
        await message.answer(
            "📍 Напиши *место хранения* коробки\n\n_Пример:_ Гараж, Кладовка, Балкон",
            parse_mode="Markdown", reply_markup=cancel_keyboard
        )

    await AddBox.waiting_for_location.set()

async def manual_location_callback(callback: types.CallbackQuery):
    await callback.message.answer("📍 Напиши *место хранения* коробки вручную:", parse_mode="Markdown", reply_markup=cancel_keyboard)
    await callback.answer()

async def location_chosen_callback(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.replace("select_location:", "")
    await state.update_data(selected_location=location)

    from types import SimpleNamespace

    fake_msg = SimpleNamespace(
        from_user=callback.from_user,
        chat=callback.message.chat,
        text=location,
        answer=lambda *args, **kwargs: callback.message.answer(*args, **kwargs)
    )
    await handle_location_inline(fake_msg, state)
    await callback.answer()

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

# Обработка "Назад" при добавлении коробки
async def handle_cancel_add_box(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ Добавление отменено.", reply_markup=main_menu_keyboard)

# Регистрация хендлеров

def register(dp: Dispatcher):
    dp.register_message_handler(handle_cancel_add_box, Text(equals="⬅ Назад"), state="*")
    dp.register_message_handler(start_add_box, Text(equals="➕ Добавить коробку"), state=None)
    dp.register_message_handler(handle_photo, content_types=types.ContentType.PHOTO, state=AddBox.waiting_for_photo)
    dp.register_message_handler(skip_photo, Text(equals="📷 Пропустить фото"), state=AddBox.waiting_for_photo)
    dp.register_message_handler(handle_description, state=AddBox.waiting_for_description)
    dp.register_message_handler(handle_location_inline, state=AddBox.waiting_for_location)
    dp.register_callback_query_handler(location_chosen_callback, lambda c: c.data.startswith("select_location:"), state=AddBox.waiting_for_location)
    dp.register_callback_query_handler(manual_location_callback, lambda c: c.data == "manual_location", state=AddBox.waiting_for_location)
