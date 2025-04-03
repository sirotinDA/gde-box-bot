from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
import aiosqlite
from database.db import DB_PATH
from handlers.keyboards import get_main_keyboard

async def handle_delete_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    location = callback.data.replace("delete_from:", "")

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, description FROM boxes WHERE user_id = ? AND location = ?", (user_id, location)) as cursor:
            boxes = await cursor.fetchall()

    if not boxes:
        await callback.message.answer("📭 В этом месте нет коробок.", reply_markup=get_main_keyboard)
        await callback.answer()
        return

    text = f"📍 <b>{location}</b>\nВыбери коробку для удаления:"
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for box_id, desc in boxes:
        short = (desc[:30] + "...") if len(desc) > 30 else desc
        keyboard.add(types.InlineKeyboardButton(f"❌ {short}", callback_data=f"confirm_delete_box:{box_id}"))

    await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()

async def confirm_delete(callback: types.CallbackQuery):
    box_id = int(callback.data.split(":")[1])

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("✅ Да", callback_data=f"delete_box_now:{box_id}"),
        types.InlineKeyboardButton("❌ Нет", callback_data="cancel_delete")
    )

    try:
        if callback.message.content_type == "photo":
            await callback.message.edit_caption("⚠️ Вы точно хотите удалить эту коробку?", reply_markup=keyboard)
        else:
            await callback.message.edit_text("⚠️ Вы точно хотите удалить эту коробку?", reply_markup=keyboard)
    except Exception as e:
        print("[ERROR при подтверждении удаления]:", e)
        await callback.message.answer("⚠ Не удалось показать подтверждение.")

    await callback.answer()

async def delete_box_now(callback: types.CallbackQuery):
    box_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM boxes WHERE id = ? AND user_id = ?", (box_id, user_id))
        await db.commit()

    try:
        await callback.message.delete()
    except Exception as e:
        print("[ERROR при удалении сообщения]:", e)

    await callback.message.bot.send_message(
        chat_id=callback.from_user.id,
        text="✅ Коробка удалена!"
    )
    
    await callback.answer()

async def cancel_delete(callback: types.CallbackQuery):
    await callback.message.answer("❌ Удаление отменено.", reply_markup=get_main_keyboard)
    await callback.answer()

async def do_nothing(callback: types.CallbackQuery):
    await callback.answer()

def register(dp: Dispatcher):
    dp.register_callback_query_handler(handle_delete_start, lambda c: c.data.startswith("delete_from:"), state="*")
    dp.register_callback_query_handler(confirm_delete, lambda c: c.data.startswith("confirm_delete_box:"), state="*")
    dp.register_callback_query_handler(delete_box_now, lambda c: c.data.startswith("delete_box_now:"), state="*")
    dp.register_callback_query_handler(cancel_delete, lambda c: c.data == "cancel_delete", state="*")
    dp.register_callback_query_handler(do_nothing, lambda c: c.data == "none", state="*")