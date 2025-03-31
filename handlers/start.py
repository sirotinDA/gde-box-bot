from aiogram import types
from aiogram.dispatcher import Dispatcher
from handlers.keyboards import main_menu_keyboard

async def cmd_start(message: types.Message):
    await message.answer(
        "*Добро пожаловать в GdeBOX!* 📦\n\n"
        "Этот бот помогает учитывать, где и что ты хранишь:\n"
        "- Добавляй коробки с фото и описанием\n"
        "- Указывай место хранения (гараж, кладовка и т.д.)\n"
        "- Ищи вещи по названию или по месту\n"
        "- Удаляй ненужные коробки\n\n"
        "Выбери действие ниже:",
        reply_markup=main_menu_keyboard,
        parse_mode="Markdown"
    )

def register(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
