# === Файл: keyboards.py ===
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add("🔍 Поиск")
main_menu_keyboard.add("➕ Добавить коробку", "✏ Добавить предмет")
main_menu_keyboard.add("📍 Места хранения", "🗑 Удалить коробку")

# Кнопка "Назад"
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.add("⬅ Назад")

# Для фото с кнопкой пропуска
photo_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
photo_keyboard.add("📷 Пропустить фото", "⬅ Назад")

# Inline-кнопки под коробкой
def box_action_keyboard(box_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("✏ Добавить предмет", callback_data=f"add_item:{box_id}"),
            InlineKeyboardButton("🗑 Удалить вещь", callback_data=f"remove_item_from:{box_id}"),
            InlineKeyboardButton("❌ Удалить коробку", callback_data=f"delete_box_by_id:{box_id}")
        ]
    ])
