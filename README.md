# 📦 GdeBOX telegram-bot

Telegram-бот для отслеживания, где хранятся ваши вещи. Бот помогает запоминать содержимое коробок и находить нужные предметы с помощью поиска.

## 🚀 Возможности

- Добавление коробок с описанием содержимого
- Назначение мест хранения (например, "гараж", "балкон", "кладовка")
- Поиск предметов по ключевым словам
- Просмотр всех коробок по месту хранения

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
├── bot.py             # Основной файл с логикой бота
├── handlers.py        # Обработчики команд и состояний
├── storage.json       # Простое хранение данных
├── requirements.txt   # Зависимости Python
└── .env               # Конфигурация токена бота
```

## ✅ Планы на будущее

- Хранение данных в базе данных (PostgreSQL)
- Поддержка фотографий коробок
- Фильтрация и сортировка коробок по дате
- Интегрировании ИИ и нейронных сетей

## 🌐 Связь

Автор: [sirotinDA](https://github.com/sirotinDA)

Если у вас есть предложения или баг-репорты — создайте issue или отправьте pull request.

---

Лицензия: MIT
