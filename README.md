# 📦 GdeBOX telegram-bot

Telegram-бот для отслеживания, где хранятся ваши вещи. Бот помогает запоминать содержимое коробок и находить нужные предметы с помощью поиска.

## 🚀 Возможности

- Добавление коробок с описанием содержимого
- Назначение мест хранения (например, "гараж", "балкон", "кладовка")
- Хранение всех данных в SQLite-базе
- Поиск предметов по ключевым словам
- Просмотр всех коробок по месту хранения
- Удаление вещей из коробки
- Удаленеие коробок
- Возможность пропуска загрузки фото (автоматическая заглушка)  
- Улучшенный интерфейс пошагового добавления 
- Добавление новых предметов в существующие коробки  
- Поэлементное удаление содержимого
- Просмотр всех коробок по локациям  
- Массовое удаление коробок в выбранном месте  
- Полное удаление мест хранения со всем содержимым

## 💠 Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/sirotinDA/gde-box-bot
cd gde-box-bot
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте токен вашего Telegram-бота:

```env
BOT_TOKEN=ваш_токен_бота
```

4. Запустите бота:

```bash
python bot.py
```

## 🛍 Пример использования

- **Добавить коробку**: нажмите "Добавить коробку" → введите место хранения и содержимое
- **Найти предмет**: нажмите "Поиск" → введите название предмета

## 📂 Структура проекта

```
.
gde-box-bot/
├── bot.py                      # Точка входа
├── config.py                   # Загрузка переменных из .env
├── requirements.txt            # Зависимости
├── .env                        # Токен Telegram-бота
├── no_photo.jpg                # Фото-заглушка
├── database/
│   ├── db.py                   # Подключение и инициализация SQLite
│   └── storage.db              # База данных
├── handlers/
│   ├── add_box.py              # Добавление коробки
│   ├── buttons.py              # Обработка кнопок
│   ├── delete_box_by_id.py     # Удаление коробки
│   ├── keyboards.py     # Удаление коробки
│   ├── find_box.py             # Поиск
│   ├── list_boxes.py           # Просмотр коробок
│   ├── remove_item_inline.py   # Удаление вещи из коробки
│   └── start.py                # Стартовое сообщение
├── states.py                   # Состояния FSM
└── README.md
└── CAHGELOG.md
```

## 🔁 Версии

✅ v3.0 (branch: new-functionality) **Обновление функций и исправление ошибок**
- Гибкое добавление коробок
- Возможность пропуска загрузки фото (автоматическая заглушка)
- Улучшенный интерфейс пошагового добавления
- Расширенное управление предметами
- Добавление новых предметов в существующие коробки  
- Поэлементное удаление содержимого
- Полный контроль над местами хранения
- Просмотр всех коробок по локациям  
- Массовое удаление коробок в выбранном месте  
- Полное удаление мест хранения со всем содержимым

🔁 v2.1 (branch: delete-item)
**Кнопки удаления коробки и вещи**

- Возможность удлаления вещи из коробки
- Возможность удлаленяи коробки
- Добавление удаления inline-кнопок

🔁 v2.0 (branch: database)
**Переход на SQLite вместо хранения в памяти**

- Используется база данных storage.db
- Удалён BOXES, все хендлеры обновлены
- Добавлены SQL-запросы вместо .get(...)

🔁 v1.1 
**Добавление даты и времени создания коробки**

- Добавлена дата и время создания коробки

🔁 v1.0 (branch: main)
**Начальная версия**

- Поддержка добавления коробки с описанием, фото и указанием места хранения
- Просмотр всех добавленных коробок
- Поиск по ключевым словам в содержимом
- Удаление коробок по месту хранения
- Реализована FSM-логика для пошагового добавления данных
- Данные временно хранились в оперативной памяти (BOXES)
- Удобное меню-клавиатура и inline-кнопки
- Простая архитектура без внешних зависимостей (только aiogram)

## 📅 Планы на будущее

- ✅ Хранение данных в базе данных
- ✅ Добавление даты создания коробки
- ✅ Удаление вещей из коробок
- ☐  Добавление тегов
- ☐  Улучшенный поиск
- ☐  Интегрирование ИИ и нейронных сетей

## 🌐 Связь

Автор: [sirotinDA](https://github.com/sirotinDA)
Telegram: [Dmitry Sirotin](https://t.me/sirotinDA)

Если у вас есть предложения или баг-репорты — создайте issue или отправьте pull request.

---

Лицензия: MIT
