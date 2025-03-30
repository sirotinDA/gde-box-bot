from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import Dispatcher
from states import AddBox

# user_id -> list of box dicts
BOXES = {}

# 🟦 Главное меню клавиатура
main_menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add("📦 Мои коробки", "➕ Добавить коробку")
main_menu_keyboard.add("📍 Места хранения", "🔍 Поиск")
main_menu_keyboard.add("🗑 Удалить коробку")

# 🔙 Только кнопка Назад
cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.add("⬅ Назад")

async def start_add(message: types.Message, state: FSMContext):
    await message.answer("📷 Пришли *фото коробки*", parse_mode="Markdown", reply_markup=cancel_keyboard)
    await AddBox.waiting_for_photo.set()

async def handle_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("❗ Это не фото. Пришли *фото коробки*", parse_mode="Markdown", reply_markup=cancel_keyboard)
        return
    await state.update_data(photo=message.photo[-1].file_id)
    await message.answer(
        "✏️ Напиши, *что лежит в коробке*\n\n_Пример:_ Шуруповёрт, кабель, перчатки",
        parse_mode="Markdown", reply_markup=cancel_keyboard
    )
    await AddBox.waiting_for_description.set()

async def handle_description(message: types.Message, state: FSMContext):
    desc = message.text.strip()
    if not desc:
        await message.answer("❗ Опиши содержимое словами", parse_mode="Markdown", reply_markup=cancel_keyboard)
        return
    await state.update_data(description=desc)
    await message.answer(
        "📍 Напиши *место хранения* коробки\n\n_Пример:_ Гараж, Кладовка, Балкон",
        parse_mode="Markdown", reply_markup=cancel_keyboard
    )
    await AddBox.waiting_for_location.set()

async def handle_location(message: types.Message, state: FSMContext):
    location = message.text.strip().capitalize()
    user_id = message.from_user.id
    data = await state.get_data()

    # Сохраняем коробку в память
    if user_id not in BOXES:
        BOXES[user_id] = []

    BOXES[user_id].append({
        "photo": data["photo"],
        "description": data["description"],
        "location": location
    })

    await message.answer(
        f"✅ *Коробка добавлена!*\n"
        f"📍 Место: `{location}`\n"
        f"📦 Содержимое: `{data['description']}`\n\n"
        f"_Посмотреть все коробки: нажми «📦 Мои коробки»_",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard
    )
    await state.finish()

# 🔙 Назад в главное меню
async def handle_back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ Добавление отменено.", reply_markup=main_menu_keyboard)

def register(dp: Dispatcher):
    dp.register_message_handler(start_add, Command("add"))
    dp.register_message_handler(start_add, Text(equals="➕ Добавить коробку"), state=None)
    dp.register_message_handler(handle_back, Text(equals="⬅ Назад"), state="*")
    dp.register_message_handler(handle_photo, content_types=types.ContentType.PHOTO, state=AddBox.waiting_for_photo)
    dp.register_message_handler(handle_description, state=AddBox.waiting_for_description)
    dp.register_message_handler(handle_location, state=AddBox.waiting_for_location)
