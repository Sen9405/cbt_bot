# 🧠 CBT-бот (КПТ-терапия)

[![Tests](https://github.com/Sen9405/cbt_bot/workflows/Tests/badge.svg)](https://github.com/Sen9405/cbt_bot/actions)

Telegram-бот для ведения дневника когнитивно-поведенческой терапии.

## Возможности

- **🧠 КПТ Дневник** — запись ситуаций, мыслей, эмоций и реакций
- **📋 Планы на день** — планирование задач с отметкой выполнения
- **🏆 Мои достижения** — список достижений
- **📊 Выгрузка Excel** — экспорт данных в .xlsx
- **🔓 Free-лимиты** — до 20 записей/планов/достижений для бесплатных пользователей
- **👑 Админ-доступ** — безлимитный доступ для администратора

## Установка

```bash
git clone https://github.com/dmr-167/cbt_bot.git
cd cbt_bot
cp .env.example .env
# Отредактируйте .env, вставив свои токены
pip install -r requirements.txt
python3 cbt_bot.py
```

## Зависимости

```
pyTelegramBotAPI
python-dotenv
openpyxl
requests
```

## Лицензия

MIT
