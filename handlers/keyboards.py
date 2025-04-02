from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# 📋 Главное меню — динамическое
def get_main_keyboard(has_boxes: bool = True) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    if has_boxes:
        keyboard.add("🔍 Поиск")
        keyboard.row("➕ Добавить коробку", "✏ Добавить предмет")
        keyboard.row("📍 Места хранения", "🗑 Удалить коробку")
    else:
        keyboard.add("➕ Добавить коробку")

    return keyboard

# ⬅ Кнопка "Назад"
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.add("⬅ Назад")

# 📷 Фото или пропуск
photo_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
photo_keyboard.add("📷 Пропустить фото", "⬅ Назад")

# 🔘 Inline-кнопки под коробкой
def box_action_keyboard(box_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("✏ Добавить предмет", callback_data=f"add_item:{box_id}"),
            InlineKeyboardButton("🗑 Удалить вещь", callback_data=f"remove_item_from:{box_id}")
        ],
        [
            InlineKeyboardButton("❌ Удалить коробку", callback_data=f"delete_box_by_id:{box_id}")
        ]
    ])
