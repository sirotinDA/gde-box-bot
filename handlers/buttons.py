from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters import Text
from states import SearchState, AddBox, AddItemFromMenu, AddItemToBox
from database.db import DB_PATH
import aiosqlite
from datetime import datetime
from handlers import find_box
from handlers import delete_box_by_id as delete_handlers
from handlers.keyboards import main_menu_keyboard, cancel_keyboard, photo_keyboard

main_menu_keyboard = main_menu_keyboard
cancel_keyboard = cancel_keyboard

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
            await message.answer("📜 *У тебя пока нет коробок.*", parse_mode="Markdown")
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

    if "добавить предмет" in text:
        locations = []
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT DISTINCT location FROM boxes WHERE user_id = ?", (user_id,)) as cursor:
                locations = await cursor.fetchall()

        if not locations:
            await message.answer("📝 У тебя пока нет коробок.", reply_markup=main_menu_keyboard)
            return

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for (loc,) in locations:
            keyboard.insert(types.InlineKeyboardButton(text=loc, callback_data=f"choose_location_for_add:{loc}"))

        await message.answer("✏ Выбери место, где находится коробка:", reply_markup=keyboard)
        await AddItemFromMenu.waiting_for_location.set()

async def process_search(message: types.Message, state: FSMContext):
    await find_box.find_box(message)
    await state.finish()

async def handle_choose_location_for_add(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, description FROM boxes WHERE user_id = ? AND location = ?", (user_id, location)) as cursor:
            boxes = await cursor.fetchall()

    if not boxes:
        await callback.message.answer("❗ В этом месте нет коробок.", reply_markup=main_menu_keyboard)
        await callback.answer()
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for box_id, desc in boxes:
        short_desc = (desc[:30] + "...") if len(desc) > 30 else desc
        keyboard.add(types.InlineKeyboardButton(text=short_desc, callback_data=f"add_to_box:{box_id}"))

    await callback.message.answer("📦 Выбери коробку для добавления предмета:", reply_markup=keyboard)
    await callback.answer()

async def handle_add_to_box(callback: types.CallbackQuery, state: FSMContext):
    box_id = int(callback.data.split(":")[1])
    await state.update_data(box_id=box_id)
    await callback.message.answer("✍ Введи предмет, который хочешь добавить в коробку:")
    await AddItemToBox.waiting_for_text.set()
    await callback.answer()

async def handle_view_location(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    location = callback.data.replace("storage:", "")

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, description FROM boxes WHERE user_id = ? AND location = ?", (user_id, location)) as cursor:
            boxes = await cursor.fetchall()

    if not boxes:
        await callback.message.answer("📭 В этом месте нет коробок.")
        await callback.answer()
        return

    text = f"📍 <b>{location}</b>\n\n"
    for i, (box_id, desc) in enumerate(boxes, 1):
        text += f"📦 <b>{i}:</b> {desc}\n"

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🗑 Удалить коробку", callback_data=f"remove_from_location:{location}"),
        types.InlineKeyboardButton("❌ Удалить место", callback_data=f"confirm_delete_location:{location}")
    )

    await callback.message.answer(text.strip(), parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

async def handle_remove_from_location(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.replace("remove_from_location:", "")
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, description FROM boxes WHERE user_id = ? AND location = ?", (user_id, location)) as cursor:
            boxes = await cursor.fetchall()

    if not boxes:
        await callback.message.answer("📭 В этом месте нет коробок.")
        await callback.answer()
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for box_id, desc in boxes:
        short = (desc[:30] + "...") if len(desc) > 30 else desc
        keyboard.add(types.InlineKeyboardButton(text=f"❌ {short}", callback_data=f"confirm_delete_box:{box_id}"))

    await callback.message.answer("🗑 Выбери коробку для удаления:", reply_markup=keyboard)
    await callback.answer()

async def confirm_delete_box(callback: types.CallbackQuery):
    box_id = int(callback.data.split(":")[1])

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("✅ Да", callback_data=f"delete_box_now:{box_id}"),
        types.InlineKeyboardButton("❌ Нет", callback_data="cancel_delete_box")
    )

    await callback.message.edit_text("⚠️ Вы точно хотите удалить эту коробку?", reply_markup=keyboard)
    await callback.answer()

async def delete_box_now(callback: types.CallbackQuery):
    box_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM boxes WHERE id = ? AND user_id = ?", (box_id, user_id))
        await db.commit()

    await callback.message.delete()
    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text="✅ Коробка удалена!"
    )
    await callback.answer()

async def cancel_delete_box(callback: types.CallbackQuery):
    await callback.message.answer("❌ Удаление отменено.", reply_markup=main_menu_keyboard)
    await callback.answer()

async def confirm_delete_location(callback: types.CallbackQuery):
    location = callback.data.replace("confirm_delete_location:", "")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✅ Да, удалить", callback_data=f"delete_location:{location}"),
        types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_delete_location")
    )
    await callback.message.answer(f"⚠️ Удалить все коробки из места «{location}»?", reply_markup=keyboard)
    await callback.answer()

async def handle_delete_location(callback: types.CallbackQuery):
    location = callback.data.replace("delete_location:", "")
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM boxes WHERE user_id = ? AND location = ?", (user_id, location))
        await db.commit()

    await callback.message.answer(f"✅ Место «{location}» и все коробки удалены.")
    await callback.answer()

async def cancel_delete_location(callback: types.CallbackQuery):
    await callback.message.answer("❌ Удаление места отменено.", reply_markup=main_menu_keyboard)
    await callback.answer()

async def do_nothing(callback: types.CallbackQuery):
    await callback.answer()

def register(dp: Dispatcher):
    dp.register_message_handler(button_handler, state=None)
    dp.register_message_handler(process_search, state=SearchState.waiting_for_keyword)
    dp.register_callback_query_handler(handle_choose_location_for_add, lambda c: c.data.startswith("choose_location_for_add:"), state=AddItemFromMenu.waiting_for_location)
    dp.register_callback_query_handler(handle_add_to_box, lambda c: c.data.startswith("add_to_box:"), state="*")
    dp.register_callback_query_handler(handle_view_location, lambda c: c.data.startswith("storage:"), state="*")
    dp.register_callback_query_handler(handle_remove_from_location, lambda c: c.data.startswith("remove_from_location:"), state="*")
    dp.register_callback_query_handler(confirm_delete_box, lambda c: c.data.startswith("confirm_delete_box:"), state="*")
    dp.register_callback_query_handler(delete_box_now, lambda c: c.data.startswith("delete_box_now:"), state="*")
    dp.register_callback_query_handler(cancel_delete_box, lambda c: c.data == "cancel_delete_box", state="*")
    dp.register_callback_query_handler(confirm_delete_location, lambda c: c.data.startswith("confirm_delete_location:"), state="*")
    dp.register_callback_query_handler(handle_delete_location, lambda c: c.data.startswith("delete_location:"), state="*")
    dp.register_callback_query_handler(cancel_delete_location, lambda c: c.data == "cancel_delete_location", state="*")
    dp.register_callback_query_handler(do_nothing, lambda c: c.data == "none", state="*")