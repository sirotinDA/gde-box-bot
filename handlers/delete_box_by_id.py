from aiogram import types
from aiogram.dispatcher import Dispatcher
from database.db import DB_PATH
import aiosqlite

async def handle_delete_box_by_id(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        box_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.message.answer("❗ Ошибка: некорректный ID коробки.")
        await callback.answer()
        return

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id FROM boxes WHERE id = ? AND user_id = ?", (box_id, user_id)) as cursor:
            row = await cursor.fetchone()

        if row:
            await db.execute("DELETE FROM boxes WHERE id = ?", (box_id,))
            await db.commit()

            try:
                await callback.message.delete()
            except Exception as e:
                await callback.message.answer(f"⚠️ Ошибка при удалении сообщения: {e}")
        else:
            await callback.message.answer("❌ Коробка не найдена или не принадлежит тебе.")

    await callback.answer()

# 🔧 Регистрация
def register(dp: Dispatcher):
    dp.register_callback_query_handler(handle_delete_box_by_id, lambda c: c.data.startswith("delete_box_by_id:"))
