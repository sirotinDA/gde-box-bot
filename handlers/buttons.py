# handlers/buttons.py
from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from handlers.add_box import BOXES
from states import SearchState, AddBox

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

    if "удалить" in text:
        boxes = BOXES.get(user_id, [])
        if not boxes:
            await message.answer("📭 *У тебя пока нет коробок.*", parse_mode="Markdown")
            return
        locations = {}
        for box in boxes:
            loc = box["location"]
            locations[loc] = locations.get(loc, 0) + 1
        keyboard = types.InlineKeyboardMarkup()
        for loc, count in locations.items():
            keyboard.add(types.InlineKeyboardButton(text=f"{loc} ({count})", callback_data=f"delete_from:{loc}"))
        await message.answer("🗑 *Выбери место для удаления:*", reply_markup=keyboard, parse_mode="Markdown")
        return

    if "мои коробки" in text:
        boxes = BOXES.get(user_id, [])
        if not boxes:
            await message.answer("📬 *У тебя пока нет коробок.*", parse_mode="Markdown")
            return
        locations = {}
        for box in boxes:
            loc = box["location"]
            locations[loc] = locations.get(loc, 0) + 1
        keyboard = types.InlineKeyboardMarkup()
        for loc, count in locations.items():
            keyboard.add(types.InlineKeyboardButton(text=f"{loc} ({count})", callback_data=f"location:{loc}"))
        await message.answer("📦 *Выбери место:*", reply_markup=keyboard, parse_mode="Markdown")
        return

    if "места хранения" in text:
        boxes = BOXES.get(user_id, [])
        if not boxes:
            await message.answer("❗ *У тебя пока нет мест.*", parse_mode="Markdown")
            return
        locations = {}
        for box in boxes:
            loc = box["location"]
            locations[loc] = locations.get(loc, 0) + 1
        keyboard = types.InlineKeyboardMarkup()
        for loc, count in locations.items():
            keyboard.add(types.InlineKeyboardButton(text=f"{loc} ({count})", callback_data=f"storage:{loc}"))
        await message.answer("📍 *Выберите место хранения:*", reply_markup=keyboard, parse_mode="Markdown")
        return

    if "поиск" in text:
        await message.answer("🔍 *Введите слово для поиска:*", reply_markup=cancel_keyboard, parse_mode="Markdown")
        await SearchState.waiting_for_keyword.set()
        return

# ➕ Добавление коробки
async def start_add_box(message: types.Message, state: FSMContext):
    await message.answer("📷 Отправь фото коробки:", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅ Назад", callback_data="cancel")))
    await AddBox.waiting_for_photo.set()

async def handle_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer("✏️ Напиши, что находится в коробке:", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅ Назад", callback_data="cancel")))
    await AddBox.waiting_for_description.set()

async def handle_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("🏷 Укажи место хранения (например, 'гараж'):", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅ Назад", callback_data="cancel")))
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

    from datetime import datetime  # добавь вверху файла, если ещё не было

    box = {
        "photo": photo,
        "description": description,
        "location": location,
        "created_at": datetime.now()
    }

    if user_id not in BOXES:
        BOXES[user_id] = []
    BOXES[user_id].append(box)

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
    boxes = [b for b in BOXES.get(user_id, []) if b["location"] == location]

    if not boxes:
        await callback.message.answer("❗ *В этом месте нет коробок.*", parse_mode="Markdown")
        await callback.answer()
        return

    for b in boxes:
        date_str = b.get("created_at").strftime("%d.%m.%Y %H:%M") if b.get("created_at") else "неизвестно"
        caption = (
            f"*📦* `{b['description']}`\n"
            f"*📍* `{b['location']}`\n"
            f"*🗓 Добавлено:* `{date_str}`"
        )
        await callback.message.answer_photo(b["photo"], caption=caption, parse_mode="Markdown")

    await callback.answer()

# 📍 Полный список предметов по месту
async def handle_storage_overview(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    location = callback.data.replace("storage:", "")
    boxes = [b for b in BOXES.get(user_id, []) if b["location"] == location]

    if not boxes:
        await callback.message.answer("❗ *В этом месте нет коробок.*", parse_mode="Markdown")
        await callback.answer()
        return

    all_items = []
    for b in boxes:
        all_items += [i.strip() for i in b["description"].split(",")]

    formatted = "\n".join(f"- `{i}`" for i in sorted(set(all_items)))
    await callback.message.answer(
        f"*📍 Место:* `{location}`\n*📦 Коробок:* `{len(boxes)}`\n\n*🧾 Все предметы:*\n{formatted}",
        parse_mode="Markdown"
    )
    await callback.answer()

# 🔍 Поиск
async def process_search(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    keyword = message.text.lower()
    boxes = BOXES.get(user_id, [])
    results = [b for b in boxes if keyword in b["description"].lower()]

    if not results:
        await message.answer("❗ *Ничего не найдено.*", reply_markup=main_menu_keyboard, parse_mode="Markdown")
    else:
        await message.answer(f"*🔎 Найдено:* `{len(results)}`", reply_markup=main_menu_keyboard, parse_mode="Markdown")
        for b in results:
            await message.answer_photo(b["photo"], caption=f"*📦* `{b['description']}`\n*📍* `{b['location']}`", parse_mode="Markdown")

    await state.finish()

# 🗑 Удаление — выбор коробки
async def handle_delete_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    location = callback.data.replace("delete_from:", "")
    boxes = [b for b in BOXES.get(user_id, []) if b["location"] == location]

    if not boxes:
        await callback.message.answer("❗ *В этом месте нет коробок.*", parse_mode="Markdown")
        await callback.answer()
        return

    for idx, b in enumerate(boxes):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Удалить", callback_data=f"delete_box:{location}:{idx}"))
        await callback.message.answer_photo(b["photo"], caption=f"*📦* `{b['description']}`\n*📍* `{b['location']}`", reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()

# ✅ Удаление коробки
async def handle_delete_box(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    _, location, idx = callback.data.split(":")
    idx = int(idx)
    user_boxes = BOXES.get(user_id, [])
    filtered = [b for b in user_boxes if b["location"] == location]

    if idx >= len(filtered):
        await callback.message.answer("⚠️ Коробка не найдена.")
        await callback.answer()
        return

    BOXES[user_id].remove(filtered[idx])
    await callback.message.answer("✅ Коробка удалена!", reply_markup=main_menu_keyboard)
    await callback.answer()

# 🧹 Удаление пустого места
async def handle_delete_location(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    location = callback.data.replace("delete_location:", "")
    before = len(BOXES.get(user_id, []))
    BOXES[user_id] = [b for b in BOXES.get(user_id, []) if b["location"] != location]
    after = len(BOXES[user_id])
    if before == after:
        await callback.message.answer(f"✅ Место `{location}` удалено.", parse_mode="Markdown")
    else:
        await callback.message.answer(f"⚠ В месте `{location}` есть коробки. Сначала удали их.", parse_mode="Markdown")
    await callback.answer()
