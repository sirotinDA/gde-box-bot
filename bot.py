from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.db import init_db
from handlers import buttons, add_box, start, find_box, list_boxes

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Инициализация базы данных при старте
async def on_startup(dp: Dispatcher):
    await init_db()
    print("✅ База данных инициализирована")

# Регистрируем обработчики
start.register(dp)
add_box.register(dp)
buttons.register(dp)
find_box.register(dp)
list_boxes.register(dp)

# Точка входа
if __name__ == '__main__':
    print("🚀 Бот запущен...")
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
