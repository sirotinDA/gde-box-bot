from aiogram import types
from aiogram.dispatcher import Dispatcher
from handlers.keyboards import get_main_keyboard
import aiosqlite
from database.db import DB_PATH

async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM boxes WHERE user_id = ?", (user_id,))
        count = (await cursor.fetchone())[0]
        has_boxes = count > 0

    await message.answer(
        "*Добро пожаловать в GdeBOX!* 📦\n\n"
        "Этот бот помогает вести учёт того, что ты хранишь:\n"
        "- Добавляй коробки с фото и описанием\n"
        "- Указывай место хранения (гараж, кладовка и т.д.)\n"
        "- Ищи вещи по названию или по месту\n"
        "- Удаляй ненужные коробки\n\n"
        "Выбери действие ниже:",
        reply_markup=get_main_keyboard(has_boxes),
        parse_mode="Markdown"
    )

def register(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
