from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN

from handlers import buttons, add_box, start, find_box, list_boxes

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

start.register(dp)
add_box.register(dp)
buttons.register(dp)
find_box.register(dp)
list_boxes.register(dp)

if __name__ == '__main__':
    print("\U0001F680 Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
