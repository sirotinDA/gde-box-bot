from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.db import DB_PATH
import aiosqlite

# Состояние для удаления
class RemoveItemState(StatesGroup):
    waiting_for_item_name = State()

# Временное хранилище выбранной коробки
box_ids = {}

# Шаг 1: пользователь нажал кнопку "Удалить вещь"
async def handle_remove_item_button(callback: types.CallbackQuery, state: FSMContext):
    box_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    box_ids[user_id] = box_id

    await callback.message.answer("✏️ Напиши, какую вещь ты хочешь удалить из коробки.")
    await RemoveItemState.waiting_for_item_name.set()
    await callback.answer()

# Шаг 2: пользователь написал название вещи
async def handle_item_name_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    item = message.text.strip().lower()

    box_id = box_ids.get(user_id)
    if not box_id:
        await message.answer("⚠️ Не удалось определить коробку.")
        await state.finish()
        return

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT description FROM boxes WHERE id = ?", (box_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                await message.answer("❌ Коробка не найдена.")
                await state.finish()
                return

            items = [i.strip() for i in row[0].split(",")]
            lowered = [i.lower() for i in items]

            if item not in lowered:
                await message.answer("❗ Такой вещи нет в этой коробке.")
                await state.finish()
                return

            new_items = [i for i in items if i.lower() != item]

            async with db.cursor() as cur:
                if new_items:
                    # Обновляем описание
                    new_desc = ", ".join(new_items)
                    await cur.execute("UPDATE boxes SET description = ? WHERE id = ?", (new_desc, box_id))
                    await message.answer(f"✅ Вещь \"{item}\" удалена из коробки.")
                else:
                    # Удаляем коробку полностью
                    await cur.execute("DELETE FROM boxes WHERE id = ?", (box_id,))
                    await message.answer("🗑 Коробка была пустой и удалена целиком.")

                await db.commit()

    await message.answer(f"✅ Вещь \"{item}\" удалена из коробки.")
    await state.finish()

# Регистрация хендлеров
def register(dp: Dispatcher):
    dp.register_callback_query_handler(handle_remove_item_button, lambda c: c.data.startswith("remove_item_from:"), state="*")
    dp.register_message_handler(handle_item_name_input, state=RemoveItemState.waiting_for_item_name)
