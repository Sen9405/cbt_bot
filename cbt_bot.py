#!/usr/bin/env python3
"""
🧠 КПТ-Терапия Бот (Telegram)
Telegram-бот для работы в рамках когнитивно-поведенческой терапии.
"""
import telebot
from telebot import types
from cbt_core import *
import math
import re

# ========== ПАГИНАЦИЯ ЗАПИСЕЙ ==========
RECORDS_PER_PAGE = 5  # записей на одной странице

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🧠 КПТ Дневник"),
        types.KeyboardButton("📋 Планы на день"),
        types.KeyboardButton("🏆 Мои достижения"),
        types.KeyboardButton("❓ Помощь"),
        types.KeyboardButton("🔄 /start")
    )
    return markup

def cbt_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📝 Новая запись"),
        types.KeyboardButton("📋 Мои записи"),
        types.KeyboardButton("✏️ Редактировать"),
        types.KeyboardButton("🗑 Удалить запись"),
        types.KeyboardButton("📊 Выгрузить Excel"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup

def fill_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        types.KeyboardButton("📍 Ситуация"),
        types.KeyboardButton("💭 Мысль"),
        types.KeyboardButton("✅ Подтверждения мысли"),
        types.KeyboardButton("❌ Опровержения мысли"),
        types.KeyboardButton("😌 Эмоция"),
        types.KeyboardButton("🔹 Реакция - Тело"),
        types.KeyboardButton("🔹 Реакция - Поведение"),
        types.KeyboardButton("📅 Изменить дату/время"),
        types.KeyboardButton("✅ Завершить запись"),
    ]
    for btn in buttons:
        markup.add(btn)
    markup.add(types.KeyboardButton("◀️ Назад в КПТ дневник"), types.KeyboardButton("🏠 Главное меню"))
    return markup

def edit_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        types.KeyboardButton("📅 Дата и время"),
        types.KeyboardButton("📍 Ситуация"),
        types.KeyboardButton("💭 Мысль"),
        types.KeyboardButton("✅ Подтверждения мысли"),
        types.KeyboardButton("❌ Опровержения мысли"),
        types.KeyboardButton("😌 Эмоция"),
        types.KeyboardButton("🔹 Реакция - Тело"),
        types.KeyboardButton("🔹 Реакция - Поведение"),
        types.KeyboardButton("🗑 Удалить запись"),
    ]
    for btn in buttons:
        markup.add(btn)
    markup.add(types.KeyboardButton("◀️ Назад в КПТ дневник"), types.KeyboardButton("🏠 Главное меню"))
    return markup

def records_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Последние 3 дня"),
        types.KeyboardButton("📅 Последняя неделя"),
        types.KeyboardButton("📅 Последний месяц"),
        types.KeyboardButton("🔍 Свой период"),
    )
    markup.add(types.KeyboardButton("◀️ Назад в КПТ дневник"), types.KeyboardButton("🏠 Главное меню"))
    return markup

def achievement_records_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Последние 3 дня"),
        types.KeyboardButton("📅 Последняя неделя"),
        types.KeyboardButton("📅 Последний месяц"),
        types.KeyboardButton("📅 За всё время"),
        types.KeyboardButton("🔍 Свой период"),
    )
    markup.add(types.KeyboardButton("◀️ Назад в достижения"), types.KeyboardButton("🏠 Главное меню"))
    return markup

def plans_records_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Последние 3 дня"),
        types.KeyboardButton("📅 Последняя неделя"),
        types.KeyboardButton("📅 Последний месяц"),
        types.KeyboardButton("📅 За всё время"),
        types.KeyboardButton("🔍 Свой период"),
    )
    markup.add(types.KeyboardButton("◀️ Назад в планы"), types.KeyboardButton("🏠 Главное меню"))
    return markup

def edit_records_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Последние 3 дня✏️"),
        types.KeyboardButton("📅 Последняя неделя✏️"),
        types.KeyboardButton("📅 Последний месяц✏️"),
        types.KeyboardButton("🔍 Свой период✏️"),
    )
    markup.add(types.KeyboardButton("◀️ Назад в КПТ дневник"), types.KeyboardButton("🏠 Главное меню"))
    return markup


def delete_records_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Последние 3 дня❌"),
        types.KeyboardButton("📅 Последняя неделя❌"),
        types.KeyboardButton("📅 Последний месяц❌"),
        types.KeyboardButton("🔍 Свой период❌"),
    )
    markup.add(types.KeyboardButton("◀️ Назад в КПТ дневник"), types.KeyboardButton("🏠 Главное меню"))
    return markup


def records_keyboard_with_nav():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Последние 3 дня📋"),
        types.KeyboardButton("📅 Последняя неделя📋"),
        types.KeyboardButton("📅 Последний месяц📋"),
        types.KeyboardButton("🔍 Свой период📋"),
    )
    markup.add(types.KeyboardButton("◀️ Назад в КПТ дневник"), types.KeyboardButton("🏠 Главное меню"))
    return markup


def cancel_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("◀️ Назад"), types.KeyboardButton("🏠 Главное меню"))
    return markup

# ========== КЛАВИАТУРЫ ПЛАНОВ ==========
def plans_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📝 Новый план"),
        types.KeyboardButton("📋 Мои планы"),
        types.KeyboardButton("✏️ Редактировать план"),
        types.KeyboardButton("✅ Отметить выполнение"),
        types.KeyboardButton("📊 Выгрузить Excel"),
        types.KeyboardButton("🗑 Удалить план"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup

def plan_view_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Сегодня"),
        types.KeyboardButton("📅 Завтра"),
        types.KeyboardButton("📅 Выбрать дату"),
        types.KeyboardButton("📅 Последняя неделя"),
        types.KeyboardButton("📅 За всё время📋"),
        types.KeyboardButton("◀️ Назад в планы"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup

def plan_edit_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Сегодня✏️"),
        types.KeyboardButton("📅 Завтра✏️"),
        types.KeyboardButton("📅 Выбрать дату✏️"),
        types.KeyboardButton("📅 Последняя неделя✏️"),
        types.KeyboardButton("◀️ Назад в планы"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup

def plan_date_choice_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📅 Сегодня"),
        types.KeyboardButton("📅 Завтра"),
        types.KeyboardButton("📅 Выбрать дату"),
        types.KeyboardButton("◀️ Назад в планы"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup

def plan_fill_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("✅ Готово"),
        types.KeyboardButton("◀️ Назад в планы"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup

def plan_item_actions_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("➕ Добавить пункт"),
        types.KeyboardButton("✏️ Редактировать пункт"),
        types.KeyboardButton("🗑 Удалить пункт"),
        types.KeyboardButton("◀️ Назад в планы"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup


def achievements_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("➕ Добавить одно"),
        types.KeyboardButton("📝 Добавить несколько"),
        types.KeyboardButton("📋 Мои достижения"),
        types.KeyboardButton("✏️ Редактировать достижения"),
        types.KeyboardButton("🗑 Удалить достижение"),
        types.KeyboardButton("🗑 Удалить все"),
        types.KeyboardButton("📊 Выгрузить Excel"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup


def achievement_fill_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("✅ Готово"),
        types.KeyboardButton("🗑 Удалить все"),
        types.KeyboardButton("◀️ Назад в достижения"),
        types.KeyboardButton("🏠 Главное меню")
    )
    return markup


# ========== СОСТОЯНИЯ ==========
user_states = {}
# Отдельный контекст раздела (не сбрасывается операциями)
user_context = {}

# ========== БОТ ==========
def create_bot(token):
    from telebot import apihelper
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    # Настраиваем HTTP-сессию с retry и увеличенным таймаутом
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    apihelper.SESSION = session
    
    bot = telebot.TeleBot(token)
    
    # ── Пагинация: вспомогательные функции ──
    def _format_record_text(rec):
        """Форматирует одну запись для вывода."""
        status_icon = "⌛" if len(rec) > 12 and rec[12] == 'draft' else "✅"
        return (
            f"{status_icon} #{rec[0]} [{db_to_display(rec[2])}]\n"
            f"📍 {rec[3] or '-'}\n"
            f"💭 {rec[4] or '-'}\n"
            f"✅ {rec[8] or '-'}\n"
            f"❌ {rec[9] or '-'}\n"
            f"😌 {rec[5] or '-'}\n"
            f"🔹 Тело: {rec[6] or '-'}  🔹 Повед: {rec[7] or '-'}\n\n"
        )
    
    def _send_records_page(chat_id, user_id, records, page=0):
        """Отправляет одну страницу записей с inline-клавиатурой пагинации."""
        total = len(records)
        total_pages = max(1, math.ceil(total / RECORDS_PER_PAGE))
        page = max(0, min(page, total_pages - 1))
        
        start = page * RECORDS_PER_PAGE
        end = min(start + RECORDS_PER_PAGE, total)
        page_records = records[start:end]
        
        text = f"📋 **Записей: {total}** (стр. {page + 1}/{total_pages})\n\n"
        for rec in page_records:
            text += _format_record_text(rec)
        
        kb = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        if page > 0:
            buttons.append(types.InlineKeyboardButton("◀️", callback_data=f"rec_page_{user_id}_{page - 1}"))
        buttons.append(types.InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="rec_page_info"))
        if page < total_pages - 1:
            buttons.append(types.InlineKeyboardButton("▶️", callback_data=f"rec_page_{user_id}_{page + 1}"))
        kb.add(*buttons)
        
        
        # Сохраняем записи в user_states для пагинации по callback
        if user_id not in user_states:
            user_states[user_id] = {}
        user_states[user_id]['page_records'] = records
        
        bot.send_message(chat_id, text, reply_markup=kb, parse_mode='Markdown')
    
    # ── Callback: пагинация записей ──
    @bot.callback_query_handler(func=lambda c: c.data.startswith('rec_page_') and not c.data.startswith('rec_page_info'))
    def records_page_callback(call):
        parts = call.data.split('_')
        try:
            target_user_id = int(parts[2])
            page = int(parts[3])
        except (IndexError, ValueError):
            bot.answer_callback_query(call.id, "Ошибка")
            return
        
        # Проверяем, что это тот же пользователь
        if call.from_user.id != target_user_id:
            bot.answer_callback_query(call.id, "Это не ваша сессия")
            return
        
        # Получаем сохранённые записи из user_states
        st = user_states.get(target_user_id, {})
        records = st.get('page_records', [])
        if not records:
            bot.answer_callback_query(call.id, "Сессия истекла, выберите период заново")
            return
        
        # Обновляем сообщение (редактируем)
        bot.answer_callback_query(call.id)
        _send_records_page(call.message.chat.id, target_user_id, records, page)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
    
    @bot.callback_query_handler(func=lambda c: c.data == 'rec_page_info')
    def records_page_info_callback(call):
        bot.answer_callback_query(call.id, "Листайте кнопками ◀️ ▶️")
    
    # ── Глобальный обработчик навигации ──
    @bot.message_handler(func=lambda m: m.text == "🏠 Главное меню")
    def global_main_menu(message):
        user_id = message.from_user.id
        user_states[user_id] = {}
        bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')

    # ── КПТ Дневник (вход в раздел) ──
    @bot.message_handler(func=lambda m: m.text == "🧠 КПТ Дневник")
    def cpt_section_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {}
        user_context[user_id] = 'kpt'
        bot.send_message(user_id, "📝 **КПТ Дневник**\n\nВыберите действие:", reply_markup=cbt_keyboard(), parse_mode='Markdown')

    # ── Назад в КПТ Дневник ──
    @bot.message_handler(func=lambda m: m.text == "◀️ Назад в КПТ дневник")
    def back_to_cpt_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {}
        user_context[user_id] = 'kpt'
        bot.send_message(user_id, "📝 **КПТ Дневник**\n\nВыберите действие:", reply_markup=cbt_keyboard(), parse_mode='Markdown')

    # ── /start ──
    @bot.message_handler(func=lambda m: m.text in ("/start", "/start@OpenclawDSensbot", "🔄 /start"))
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {}
        
        welcome = (
            "<b>🧠 КПТ-Терапия Бот</b>\n\n"
            "Бот для работы в рамках когнитивно-поведенческой терапии.\n\n"
            "<b>Разделы:</b>\n"
            "🧠 <b>КПТ Дневник</b> — записывай ситуации, мысли, эмоции и реакции\n"
            "📋 <b>Планы на день</b> — планируй задачи и отмечай выполнение\n"
            "🏆 <b>Мои достижения</b> — копилка твоих побед и успехов\n\n"
            "Выберите раздел в меню:"
        )
        
        if user_id != ADMIN_ID:
            count = get_records_count(user_id)
            remaining = MAX_FREE_RECORDS - count
            plans_left = max(0, MAX_FREE_PLANS - count_user_plans(user_id))
            ach_left = max(0, MAX_FREE_ACHIEVEMENTS - count_achievements(user_id))
            welcome += f"\n\n⚠️ <b>Бесплатная версия</b>"
            if remaining > 0:
                welcome += f"\n🧠 Записи: <b>осталось {remaining}/{MAX_FREE_RECORDS}</b>"
            else:
                welcome += f"\n❌🧠 Записи: <b>лимит ({MAX_FREE_RECORDS}/{MAX_FREE_RECORDS})</b>"
            if plans_left > 0:
                welcome += f"\n📋 Планы: <b>осталось {plans_left}/{MAX_FREE_PLANS}</b>"
            else:
                welcome += f"\n❌📋 Планы: <b>лимит ({MAX_FREE_PLANS}/{MAX_FREE_PLANS})</b>"
            if ach_left > 0:
                welcome += f"\n🏆 Достижения: <b>осталось {ach_left}/{MAX_FREE_ACHIEVEMENTS}</b>"
            else:
                welcome += f"\n❌🏆 Достижения: <b>лимит ({MAX_FREE_ACHIEVEMENTS}/{MAX_FREE_ACHIEVEMENTS})</b>"
            welcome += f"\nЧтобы снять лимиты — свяжись с @dmr_167"
        else:
            welcome += "\n\n👑 Полный доступ без ограничений"
        
        welcome += "\n\nВыбери раздел в меню:"
        
        bot.send_message(user_id, welcome, reply_markup=main_keyboard(), parse_mode='HTML')
    
    # ── Помощь ──
    @bot.message_handler(func=lambda m: m.text == "❓ Помощь")
    def help_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {}
        bot.send_message(message.chat.id,
            "❓ **Помощь**\n\n"
            "🧠 **КПТ Дневник**\n"
            "📝 **Новая запись** — заполнить ситуацию, мысли, подтверждения/опровержения, эмоции, реакции\n"
            "📋 **Мои записи** — просмотр записей за период\n"
            "✏️ **Редактировать** — изменить существующую запись\n"
            "🗑 **Удалить запись** — удалить запись по ID с подтверждением\n"
            "📊 **Выгрузить Excel** — скачать все записи таблицей\n\n"
            "📋 **Планы на день**\n"
            "📝 **Новый план** — создать план на сегодня/завтра/свою дату\n"
            "📋 **Мои планы** — просмотр планов\n"
            "✏️ **Редактировать план** — добавить/удалить/переименовать пункты\n"
            "✅ **Отметить выполнение** — отметить пункты как выполненные\n"
            "🗑 **Удалить план** — удалить план на дату\n"
            "📊 **Выгрузить Excel** — скачать планы за период таблицей\n\n"
            "🏆 **Мои достижения**\n"
            "➕ **Добавить одно** — добавить одно достижение\n"
            "📝 **Добавить несколько** — добавить список достижений\n"
            "📋 **Мои достижения** — просмотр всех достижений\n"
            "✏️ **Редактировать** — изменить текст достижения\n"
            "🗑 **Удалить** — удалить достижение\n"
            "📊 **Выгрузить Excel** — скачать достижения за период таблицей\n\n"
            "**Формат даты:** `ДД-ММ-ГГГГ ЧЧ:ММ`\n"
            "Например: `23-04-2026 15:30`\n"
            "Для планов достаточно `ДД-ММ-ГГГГ`",
            reply_markup=main_keyboard(), parse_mode='Markdown')
    
    # ── Новая запись ──
    @bot.message_handler(func=lambda m: m.text == "📝 Новая запись")
    def new_record_handler(message):
        user_id = message.from_user.id
        
        # Проверка лимита для не-админов
        if user_id != ADMIN_ID:
            count = get_records_count(user_id)
            if count >= MAX_FREE_RECORDS:
                bot.send_message(user_id,
                    f"⚠️ **Достигнут лимит бесплатных записей**\n\n"
                    f"Вы можете создать только **{MAX_FREE_RECORDS}** записи в бесплатной версии.\n"
                    f"Чтобы снять ограничение, свяжитесь с @dmr_167",
                    reply_markup=main_keyboard(), parse_mode='Markdown')
                return
        
        now = now_str()
        user_states[user_id] = {'state': 'filling', 'data': {'created_at': display_to_db(now)}}
        bot.send_message(user_id,
            f"✅ **Новая запись!**\n📅 {now}\n\nВыберите поле:",
            reply_markup=fill_keyboard(), parse_mode='Markdown')
    
    # ── Выбор поля при заполнении ──
    FILL_BTNS = {
        "📍 Ситуация": "situation",
        "💭 Мысль": "thought",
        "✅ Подтверждения мысли": "confirmation",
        "❌ Опровержения мысли": "refutation",
        "😌 Эмоция": "emotion",
        "🔹 Реакция - Тело": "body_reaction",
        "🔹 Реакция - Поведение": "behavior_reaction",
        "📅 Изменить дату/время": "created_at"
    }
    
    @bot.message_handler(func=lambda m: m.text in FILL_BTNS and user_states.get(m.from_user.id, {}).get('state') != 'editing')
    def select_fill_field(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') != 'filling':
            bot.send_message(user_id, "❌ Начните через 📝 **Новая запись**",
                           reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        
        field = FILL_BTNS[message.text]
        user_states[user_id]['current_field'] = field
        user_states[user_id]['state'] = 'waiting_value'
        
        prompts = {
            "created_at": f"📅 **Дата и время** в формате:\n`{DATE_FORMAT_DISPLAY}`\nНапример: `{DATE_FORMAT_EXAMPLE}`",
            "situation": "📍 **Опишите ситуацию:**\nЧто произошло? Где? С кем?",
            "thought": "💭 **Какая мысль пришла в голову?**\nЧто вы подумали в тот момент?",
            "confirmation": "✅ **Подтверждения мысли:**\nКакие факты или доводы подтверждают эту мысль?",
            "refutation": "❌ **Опровержения мысли:**\nКакие факты или доводы опровергают эту мысль? Взгляните на ситуацию объективно.",
            "emotion": "😌 **Какую эмоцию вы испытали?**\nНапример: тревога, гнев, грусть, радость, страх",
            "body_reaction": "🔹 **Ощущения в теле?**\nНапряжение, сердцебиение, дрожь...",
            "behavior_reaction": "🔹 **Как вы себя повели?**\nЧто сделали? Как отреагировали?"
        }
        bot.send_message(user_id, prompts[field], reply_markup=cancel_keyboard(), parse_mode='Markdown')
    
    # ── Завершить запись ──
    @bot.message_handler(func=lambda m: m.text == "✅ Завершить запись")
    def finish_record(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') not in ['filling', 'waiting_value']:
            bot.send_message(user_id, "❌ Нет активной записи.", reply_markup=cbt_keyboard())
            return
        
        record_id = save_record(user_id, st.get('data', {}))
        record = get_record_by_id(record_id, user_id)
        bot.send_message(user_id, f"✅ **Запись #{record_id} сохранена!**\n\n{format_record(record)}",
                        reply_markup=cbt_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {}
    
    # ── Ввод значения (заполнение) ──
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'waiting_value')
    def handle_value(message):
        user_id = message.from_user.id
        field = user_states[user_id].get('current_field')
        data = user_states[user_id].get('data', {})
        value = message.text.strip()
        
        if field == 'created_at':
            try:
                display_to_db(value)  # проверка формата
                data[field] = display_to_db(value)  # храним в БД-формате
            except:
                bot.send_message(user_id,
                    f"❌ Неверный формат. Используйте: `{DATE_FORMAT_DISPLAY}`\nНапример: `{DATE_FORMAT_EXAMPLE}`",
                    reply_markup=cancel_keyboard(), parse_mode='Markdown')
                return
        else:
            data[field] = value
        
        user_states[user_id]['data'] = data
        user_states[user_id]['state'] = 'filling'
        
        d = data
        status = (
            f"📝 **Текущая запись:**\n"
            f"📅 Дата/время: {db_to_display(d.get('created_at', ''))}\n"
            f"📍 Ситуация: {d.get('situation', '❌')}\n"
            f"💭 Мысль: {d.get('thought', '❌')}\n"
            f"✅ Подтверждения: {d.get('confirmation', '❌')}\n"
            f"❌ Опровержения: {d.get('refutation', '❌')}\n"
            f"😌 Эмоция: {d.get('emotion', '❌')}\n"
            f"🔹 Тело: {d.get('body_reaction', '❌')}\n"
            f"🔹 Поведение: {d.get('behavior_reaction', '❌')}\n\n"
            f"Выберите поле или ✅ **Завершить запись**:"
        )
        bot.send_message(user_id, status, reply_markup=fill_keyboard(), parse_mode='Markdown')
    
    # ── Мои записи ──
    @bot.message_handler(func=lambda m: m.text == "📋 Мои записи")
    def my_records_handler(message):
        user_id = message.from_user.id
        bot.send_message(user_id, "📅 **Выберите период:**", reply_markup=records_keyboard_with_nav())
        user_states[user_id] = {'state': 'records_choose_period'}
    
    # ── Выбор периода для просмотра записей ──
    RECORDS_PERIOD_MAP = {
        "📅 Последние 3 дня📋": 3,
        "📅 Последняя неделя📋": 7,
        "📅 Последний месяц📋": 30,
    }
    
    @bot.message_handler(func=lambda m: m.text in RECORDS_PERIOD_MAP)
    def handle_records_period(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') != 'records_choose_period':
            bot.send_message(user_id, "❌ Сначала нажмите 📋 **Мои записи**", reply_markup=cbt_keyboard(), parse_mode='Markdown')
            return
        
        days = RECORDS_PERIOD_MAP[message.text]
        records = get_records(user_id, days)
        label = {3: "3 дня", 7: "неделю", 30: "месяц"}.get(days, f"{days} дн.")
        
        if not records:
            bot.send_message(user_id, f"❌ Нет записей за последние {label}.", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        _send_records_page(user_id, user_id, records, page=0)
        user_states[user_id]['state'] = 'records_choose_period'
        user_states[user_id]['back_to_records'] = True

    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'records_choose_period' and m.text == "◀️ Назад")
    def handle_records_back(message):
        user_id = message.from_user.id
        bot.send_message(user_id, "📅 **Выберите период:**", reply_markup=records_keyboard_with_nav())
        user_states[user_id] = {'state': 'records_choose_period'}

    @bot.message_handler(func=lambda m: m.text == "🔍 Свой период📋")
    def handle_records_custom_period(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') != 'records_choose_period':
            bot.send_message(user_id, "❌ Сначала нажмите 📋 **Мои записи**", reply_markup=cbt_keyboard(), parse_mode='Markdown')
            return
        
        bot.send_message(user_id,
            "📅 Введите даты в формате:\n`ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\n(начало и конец через пробел)\nНапример: `23-04-2026 23-04-2026`",
            reply_markup=cancel_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'records_waiting_custom_period'}
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'records_waiting_custom_period')
    def handle_records_custom_period_input(message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text == "◀️ Назад":
            bot.send_message(user_id, "📅 **Выберите период:**", reply_markup=records_keyboard_with_nav())
            user_states[user_id] = {'state': 'records_choose_period'}
            return
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        
        parts = text.split()
        if len(parts) < 2:
            bot.send_message(user_id,
                "❌ Формат: `ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        try:
            start_date = datetime.strptime(parts[0], "%d-%m-%Y").date()
            end_date = datetime.strptime(parts[1], "%d-%m-%Y").date()
        except:
            bot.send_message(user_id,
                "❌ Неверный формат. Используйте: `ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        start = start_date.strftime(DB_DATE_FORMAT[:10])
        end = end_date.strftime("%Y-%m-%d 23:59")
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT * FROM cbt_records WHERE user_id = ? AND created_at >= ? AND created_at <= ? ORDER BY created_at DESC',
                  (user_id, start, end))
        records = c.fetchall()
        conn.close()
        
        if not records:
            bot.send_message(user_id, f"❌ Нет записей за {parts[0]} — {parts[1]}", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        _send_records_page(user_id, user_id, records, page=0)
        user_states[user_id]['state'] = 'records_choose_period'
        user_states[user_id]['back_to_records'] = True
    
    @bot.message_handler(func=lambda m: m.text in ["📅 Последние 3 дня", "📅 Последняя неделя", "📅 Последний месяц", "📅 За всё время"] and \
        user_states.get(m.from_user.id, {}).get('state') in (None, 'export_choose', 'records_choose_period'))
    def show_or_export(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        state = st.get('state')
        
        # Если в режиме выбора экспорта — экспортируем
        if state == 'export_choose':
            _do_export(user_id, message.text)
            return
        
        # Иначе показываем записи (только для КПТ)
        period_map = {"📅 Последние 3 дня": 3, "📅 Последняя неделя": 7, "📅 Последний месяц": 30}
        days = period_map[message.text]
        
        records = get_records(user_id, days)
        if not records:
            bot.send_message(user_id, f"❌ Нет записей за {days} дн.", reply_markup=cbt_keyboard())
            return
        
        _send_records_page(user_id, user_id, records, page=0)
        user_states[user_id].pop('back_to_records', None)
        user_states[user_id]['state'] = ''
    
    @bot.message_handler(func=lambda m: m.text == "✏️ Редактировать")
    def edit_handler(message):
        user_id = message.from_user.id
        bot.send_message(user_id, "📅 **Выберите период для редактирования:**", reply_markup=edit_records_keyboard())
        user_states[user_id] = {'state': 'edit_choose_period'}
    
    # ── Удаление записи ──
    @bot.message_handler(func=lambda m: m.text == "🗑 Удалить запись" and \
        not user_states.get(m.from_user.id, {}).get('state', '').startswith(('delete_waiting', 'delete_choose', 'delete_confirm', 'editing', 'waiting_edit')))
    def delete_handler(message):
        user_id = message.from_user.id
        bot.send_message(user_id, "🗑 **Выберите период для удаления записей:**", reply_markup=delete_records_keyboard())
        user_states[user_id] = {'state': 'delete_choose_period'}
    
    # ── Выбор периода для редактирования ──
    EDIT_PERIOD_MAP = {
        "📅 Последние 3 дня✏️": 3,
        "📅 Последняя неделя✏️": 7,
        "📅 Последний месяц✏️": 30,
    }
    
    @bot.message_handler(func=lambda m: m.text in EDIT_PERIOD_MAP)
    def handle_edit_period(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') != 'edit_choose_period':
            bot.send_message(user_id, "❌ Сначала нажмите ✏️ **Редактировать**", reply_markup=cbt_keyboard(), parse_mode='Markdown')
            return
        
        days = EDIT_PERIOD_MAP[message.text]
        records = get_records(user_id, days)
        label = {3: "3 дня", 7: "неделю", 30: "месяц"}.get(days, f"{days} дн.")
        
        if not records:
            bot.send_message(user_id, f"❌ Нет записей за последние {label}.", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        # Сохраняем список доступных ID из этого периода
        valid_ids = {rec[0] for rec in records}
        
        text = f"✏️ **Редактирование — последние {label}**\n\n"
        text += f"Найдено записей: {len(records)}\n\n"
        for rec in records[:10]:
            text += f"#{rec[0]} — {db_to_display(rec[2])} — {rec[3] or '-'}\n"
        if len(records) > 10:
            text += f"\n... и ещё {len(records) - 10} записей"
        text += "\n\n**Введите ID записи для редактирования:**"
        
        bot.send_message(user_id, text[:2000], reply_markup=cancel_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'waiting_edit_id', 'valid_ids': valid_ids}
    
    @bot.message_handler(func=lambda m: m.text == "🔍 Свой период✏️")
    def handle_edit_custom_period(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') != 'edit_choose_period':
            bot.send_message(user_id, "❌ Сначала нажмите ✏️ **Редактировать**", reply_markup=cbt_keyboard(), parse_mode='Markdown')
            return
        
        bot.send_message(user_id,
            "📅 Введите даты в формате:\n`ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\n(начало и конец через пробел)\nНапример: `23-04-2026 23-04-2026`",
            reply_markup=cancel_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'edit_waiting_custom_period'}
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'waiting_edit_id')
    def handle_edit_id(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states.get(user_id, {})
        valid_ids = st.get('valid_ids', set())
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        
        if text == "◀️ Назад":
            st = user_states.get(user_id, {})
            prev_state = st.get('state')
            
            if prev_state == 'records_choose_period':
                user_states[user_id] = {}
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
                return
            
            bot.send_message(user_id, "📅 **Выберите период для редактирования:**", reply_markup=edit_records_keyboard())
            user_states[user_id] = {'state': 'edit_choose_period'}
            return
        
        try:
            record_id = int(text)
        except:
            bot.send_message(user_id, "❌ Введите число (ID).", reply_markup=cancel_keyboard())
            return
        
        # Проверяем, что ID есть в выбранном периоде
        if valid_ids and record_id not in valid_ids:
            bot.send_message(user_id,
                f"❌ Запись #{record_id} не найдена в выбранном периоде.\n"
                f"Выберите ID из списка выше и попробуйте снова.",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        record = get_record_by_id(record_id, user_id)
        if not record:
            bot.send_message(user_id, "❌ Запись не найдена. Проверьте ID.", reply_markup=cancel_keyboard())
            return
        
        user_states[user_id] = {'state': 'editing', 'record_id': record_id}
        bot.send_message(user_id,
            f"✏️ **Редактирование #{record_id}**\n\n{format_record(record)}\n\nВыберите поле:",
            reply_markup=edit_keyboard(), parse_mode='Markdown')
    
    EDIT_BTNS = {
        "📅 Дата и время": "created_at",
        "📍 Ситуация": "situation",
        "💭 Мысль": "thought",
        "✅ Подтверждения мысли": "confirmation",
        "❌ Опровержения мысли": "refutation",
        "😌 Эмоция": "emotion",
        "🔹 Реакция - Тело": "body_reaction",
        "🔹 Реакция - Поведение": "behavior_reaction"
    }
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'editing')
    def handle_edit_choice(message):
        user_id = message.from_user.id
        text = message.text
        st = user_states[user_id]
        
        if text == "🗑 Удалить запись":
            delete_record(st['record_id'], user_id)
            bot.send_message(user_id, f"✅ Запись #{st['record_id']} удалена!", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        if text in EDIT_BTNS:
            field = EDIT_BTNS[text]
            record = get_record_by_id(st['record_id'], user_id)
            old_value = record[{'created_at': 2, 'situation': 3, 'thought': 4, 'confirmation': 8, 'refutation': 9, 'emotion': 5, 'body_reaction': 6, 'behavior_reaction': 7}[field]]
            st['old_value'] = old_value
            st['edit_field'] = field
            st['state'] = 'waiting_edit_value'
            
            if field == 'created_at':
                old_display = db_to_display(old_value) if old_value else '-'
                # Отдельным сообщением старое значение
                bot.send_message(user_id, f"📅 **Старое значение:**\n`{old_display}`", parse_mode='Markdown')
                msg = f"✏️ Введите **новую дату/время**:\nФормат: `{DATE_FORMAT_DISPLAY}`\nПример: `{DATE_FORMAT_EXAMPLE}`"
            else:
                # Отдельным сообщением старое значение
                bot.send_message(user_id, f"📝 **{FIELD_NAMES[field]}**\nСтарое значение (нажмите чтобы скопировать):\n`{old_value or '-'}`", parse_mode='Markdown')
                msg = f"✏️ Теперь напишите **новое значение**:"
            
            bot.send_message(user_id, msg, reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 Главное меню", reply_markup=cbt_keyboard())
            return
        
        bot.send_message(user_id, "❌ Выберите поле из кнопок ниже:", reply_markup=edit_keyboard())
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'waiting_edit_value')
    def handle_edit_value(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states[user_id]
        
        # Навигация
        if text == "◀️ Назад":
            record = get_record_by_id(st['record_id'], user_id)
            st['state'] = 'editing'
            bot.send_message(user_id,
                f"✏️ **Редактирование #{st['record_id']}**\n\n{format_record(record)}\n\nВыберите поле:",
                reply_markup=edit_keyboard(), parse_mode='Markdown')
            return
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        
        field = st.get('edit_field')
        record_id = st.get('record_id')
        value = text
        
        if field == 'created_at':
            try:
                display_to_db(value)
                value_db = display_to_db(value)
            except:
                bot.send_message(user_id,
                    f"❌ Неверный формат. Используйте: `{DATE_FORMAT_DISPLAY}`\nНапример: `{DATE_FORMAT_EXAMPLE}`",
                    reply_markup=cancel_keyboard(), parse_mode='Markdown')
                return
        else:
            value_db = value
        
        update_record(record_id, user_id, field, value_db)
        record = get_record_by_id(record_id, user_id)
        
        bot.send_message(user_id,
            f"✅ **Обновлено!**\n\n{format_record(record)}\n\nЧто ещё изменить?",
            reply_markup=edit_keyboard(), parse_mode='Markdown')
        user_states[user_id]['state'] = 'editing'
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'edit_waiting_custom_period')
    def handle_edit_custom_period_input(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states.get(user_id, {})
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        if text == "◀️ Назад":
            bot.send_message(user_id, "📅 **Выберите период для редактирования:**", reply_markup=edit_records_keyboard())
            user_states[user_id] = {'state': 'edit_choose_period'}
            return
        
        parts = text.split()
        if len(parts) < 2:
            bot.send_message(user_id,
                "❌ Формат: `ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        try:
            start_date = datetime.strptime(parts[0], "%d-%m-%Y").date()
            end_date = datetime.strptime(parts[1], "%d-%m-%Y").date()
        except:
            bot.send_message(user_id,
                "❌ Неверный формат. Используйте: `ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        start = start_date.strftime(DB_DATE_FORMAT[:10])
        end = end_date.strftime("%Y-%m-%d 23:59")
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT * FROM cbt_records WHERE user_id = ? AND created_at >= ? AND created_at <= ? ORDER BY created_at DESC',
                  (user_id, start, end))
        records = c.fetchall()
        conn.close()
        
        if not records:
            bot.send_message(user_id, f"❌ Нет записей за {parts[0]} — {parts[1]}", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        # Сохраняем список доступных ID из этого периода
        valid_ids = {rec[0] for rec in records}
        
        text_msg = f"✏️ **Редактирование — {parts[0]} — {parts[1]}**\n\n"
        text_msg += f"Найдено записей: {len(records)}\n\n"
        for rec in records[:10]:
            text_msg += f"#{rec[0]} — {db_to_display(rec[2])} — {rec[3] or '-'}\n"
        if len(records) > 10:
            text_msg += f"\n... и ещё {len(records) - 10} записей"
        text_msg += "\n\n**Введите ID записи для редактирования:**"
        
        bot.send_message(user_id, text_msg[:2000], reply_markup=cancel_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'waiting_edit_id', 'valid_ids': valid_ids}
    
    # ── Удаление записи ──
    @bot.message_handler(func=lambda m: m.text == "🗑 Удалить запись" and \
        user_states.get(m.from_user.id, {}).get('state', '').startswith(('delete_waiting', 'delete_choose')))
    def handle_delete_in_state(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        state = st.get('state', '')
        
        if state == 'delete_choose_period':
            bot.send_message(user_id, "📅 **Выберите период для удаления записей:**",
                           reply_markup=delete_records_keyboard(), parse_mode='Markdown')
            return
        elif state in ('delete_waiting_id', 'delete_confirm'):
            bot.send_message(user_id, "❌ Вы уже выбрали период. Введите ID записи для удаления:",
                           reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
    
    DELETE_PERIOD_MAP = {
        "📅 Последние 3 дня❌": 3,
        "📅 Последняя неделя❌": 7,
        "📅 Последний месяц❌": 30,
    }
    
    @bot.message_handler(func=lambda m: m.text in DELETE_PERIOD_MAP)
    def handle_delete_period(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') != 'delete_choose_period':
            bot.send_message(user_id, "❌ Сначала нажмите 🗑 **Удалить запись** в меню.",
                           reply_markup=cbt_keyboard(), parse_mode='Markdown')
            return
        
        days = DELETE_PERIOD_MAP[message.text]
        records = get_records(user_id, days)
        label = {3: "3 дня", 7: "неделю", 30: "месяц"}.get(days, f"{days} дн.")
        
        if not records:
            bot.send_message(user_id, f"❌ Нет записей за последние {label}.", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        valid_ids = {rec[0] for rec in records}
        
        text = f"🗑 **Удаление записей — последние {label}**\n\n"
        text += f"Найдено записей: {len(records)}\n\n"
        for rec in records[:10]:
            text += f"#{rec[0]} — {db_to_display(rec[2])} — {rec[3] or '-'}\n"
        if len(records) > 10:
            text += f"\n... и ещё {len(records) - 10} записей"
        text += "\n\n**Введите ID записи для удаления:**"
        
        bot.send_message(user_id, text[:2000], reply_markup=cancel_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'delete_waiting_id', 'valid_ids': valid_ids}
    
    @bot.message_handler(func=lambda m: m.text == "🔍 Свой период❌")
    def handle_delete_custom_period(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') != 'delete_choose_period':
            bot.send_message(user_id, "❌ Сначала нажмите 🗑 **Удалить запись** в меню КПТ.",
                           reply_markup=cbt_keyboard(), parse_mode='Markdown')
            return
        
        bot.send_message(user_id,
            "📅 Введите даты в формате:\n`ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\n"
            "(начало и конец через пробел)\nНапример: `23-04-2026 23-04-2026`",
            reply_markup=cancel_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'delete_waiting_custom_period'}
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'delete_waiting_id')
    def handle_delete_id(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states.get(user_id, {})
        valid_ids = st.get('valid_ids', set())
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        
        if text == "◀️ Назад":
            bot.send_message(user_id, "📅 **Выберите период:**", reply_markup=delete_records_keyboard())
            user_states[user_id] = {'state': 'delete_choose_period'}
            return
        
        try:
            record_id = int(text)
        except:
            bot.send_message(user_id, "❌ Введите число (ID).", reply_markup=cancel_keyboard())
            return
        
        if valid_ids and record_id not in valid_ids:
            bot.send_message(user_id,
                f"❌ Запись #{record_id} не найдена в выбранном периоде.\n"
                f"Выберите ID из списка выше.",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        record = get_record_by_id(record_id, user_id)
        if not record:
            bot.send_message(user_id, "❌ Запись не найдена. Проверьте ID.", reply_markup=cancel_keyboard())
            return
        
        user_states[user_id] = {'state': 'delete_confirm', 'record_id': record_id}
        bot.send_message(user_id,
            f"🗑 **Точно удалить запись #{record_id}?**\n\n"
            f"{format_record(record)}\n\n"
            f"Нажми **✅ Да, удалить** для подтверждения или **◀️ Назад**.",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
                types.KeyboardButton("✅ Да, удалить"),
                types.KeyboardButton("◀️ Назад"),
                types.KeyboardButton("🏠 Главное меню")), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'delete_confirm')
    def handle_delete_confirm(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states.get(user_id, {})
        record_id = st.get('record_id')
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        
        if text == "◀️ Назад":
            bot.send_message(user_id, "🗑 Удаление отменено.", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        if text == "✅ Да, удалить":
            delete_record(record_id, user_id)
            bot.send_message(user_id, f"✅ Запись #{record_id} удалена!", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        bot.send_message(user_id, "❌ Неверный выбор. Нажми **✅ Да, удалить** или **◀️ Назад**.",
                       reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
                           types.KeyboardButton("✅ Да, удалить"),
                           types.KeyboardButton("◀️ Назад"),
                           types.KeyboardButton("🏠 Главное меню")), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'delete_waiting_custom_period')
    def handle_delete_custom_period_input(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states.get(user_id, {})
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        if text == "◀️ Назад":
            bot.send_message(user_id, "📅 **Выберите период:**", reply_markup=delete_records_keyboard())
            user_states[user_id] = {'state': 'delete_choose_period'}
            return
        
        parts = text.split()
        if len(parts) < 2:
            bot.send_message(user_id,
                "❌ Формат: `ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        try:
            start_date = datetime.strptime(parts[0], "%d-%m-%Y").date()
            end_date = datetime.strptime(parts[1], "%d-%m-%Y").date()
        except:
            bot.send_message(user_id,
                "❌ Неверный формат. Используйте: `ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        start = start_date.strftime(DB_DATE_FORMAT[:10])
        end = end_date.strftime("%Y-%m-%d 23:59")
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT * FROM cbt_records WHERE user_id = ? AND created_at >= ? AND created_at <= ? ORDER BY created_at DESC',
                  (user_id, start, end))
        records = c.fetchall()
        conn.close()
        
        if not records:
            bot.send_message(user_id, f"❌ Нет записей за {parts[0]} — {parts[1]}.", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        valid_ids = {rec[0] for rec in records}
        
        text_msg = f"🗑 **Удаление — {parts[0]} — {parts[1]}**\n\n"
        text_msg += f"Найдено записей: {len(records)}\n\n"
        for rec in records[:10]:
            text_msg += f"#{rec[0]} — {db_to_display(rec[2])} — {rec[3] or '-'}\n"
        if len(records) > 10:
            text_msg += f"\n... и ещё {len(records) - 10} записей"
        text_msg += "\n\n**Введите ID записи для удаления:**"
        
        bot.send_message(user_id, text_msg[:2000], reply_markup=cancel_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'delete_waiting_id', 'valid_ids': valid_ids}
    
    # ── Выгрузка Excel ──
    def _send_excel(user_id, records, label):
        """Отправить Excel файл пользователю (КПТ)"""
        excel_data = export_to_excel(records)
        bot.send_document(user_id, excel_data, visible_file_name=f"kpt_dnevnik_{label}.xlsx",
                         caption=f"📊 **КПТ Дневник**\n{label}\nЗаписей: {len(records)}")
        bot.send_message(user_id, "✅ Готово!", reply_markup=cbt_keyboard())
    
    def _send_achievements_excel(user_id, records, label):
        """Отправить Excel файл пользователю (достижения)"""
        excel_data = export_achievements_to_excel(records)
        bot.send_document(user_id, excel_data, visible_file_name=f"dostizheniya_{label}.xlsx",
                         caption=f"🏆 **Достижения**\n{label}\nЗаписей: {len(records)}")
        bot.send_message(user_id, "✅ Готово!", reply_markup=achievements_keyboard())
    
    def _send_plans_excel(user_id, plans_data, label):
        """Отправить Excel файл пользователю (планы)"""
        excel_data = export_plans_to_excel(plans_data, label)
        # Считаем количество пунктов
        total_items = sum(len(p['items']) for p in plans_data)
        bot.send_document(user_id, excel_data, visible_file_name=f"plany_{label}.xlsx",
                         caption=f"📋 **Планы на день**\n{label}\nПланов: {len(plans_data)}, пунктов: {total_items}")
        bot.send_message(user_id, "✅ Готово!", reply_markup=plans_keyboard())
    
    def _do_export(user_id, option):
        """Выполнить экспорт по выбранному периоду"""
        ctx = user_states.get(user_id, {}).get('export_section', 'kpt')
        user_states[user_id] = {}
        period_map = {"📅 Последние 3 дня": 3, "📅 Последняя неделя": 7, "📅 Последний месяц": 30}
        
        if option in period_map:
            days = period_map[option]
            start = (datetime.now() - timedelta(days=days)).strftime("%d-%m-%Y")
            end = datetime.now().strftime("%d-%m-%Y")
            start_date = datetime.strptime(start, "%d-%m-%Y").date()
            end_date = datetime.strptime(end, "%d-%m-%Y").date()
            
            if ctx == 'achievements':
                records = get_achievements_by_period(user_id, start_date, end_date)
                if not records:
                    bot.send_message(user_id, f"❌ Нет достижений за {start} — {end}", reply_markup=achievements_keyboard())
                    return
                _send_achievements_excel(user_id, records, f"{start} — {end}")
            elif ctx == 'plans':
                plans = get_plans_by_period(user_id, start_date, end_date)
                if not plans:
                    bot.send_message(user_id, f"❌ Нет планов за {start} — {end}", reply_markup=plans_keyboard())
                    return
                _send_plans_excel(user_id, plans, f"{start} — {end}")
            else:
                records = get_records_by_period(user_id, start_date, end_date)
                if not records:
                    bot.send_message(user_id, f"❌ Нет записей за {start} — {end}", reply_markup=cbt_keyboard())
                    return
                _send_excel(user_id, records, f"{start} — {end}")
        elif option == "📅 За всё время":
            if ctx == 'achievements':
                records = get_achievements_all(user_id)
                if not records:
                    bot.send_message(user_id, "❌ Нет достижений.", reply_markup=achievements_keyboard())
                    return
                _send_achievements_excel(user_id, records, "все")
            elif ctx == 'plans':
                plans = get_all_plans(user_id)
                if not plans:
                    bot.send_message(user_id, "❌ Нет планов.", reply_markup=plans_keyboard())
                    return
                _send_plans_excel(user_id, plans, "все")
            else:
                records = get_records(user_id, 99999)
                if not records:
                    bot.send_message(user_id, "❌ Нет записей.", reply_markup=cbt_keyboard())
                    return
                _send_excel(user_id, records, "все")
        elif option == "🔍 Свой период":
            bot.send_message(user_id,
                "📅 Введите даты в формате:\n`ДД-ММ-ГГГГ ДД-ММ-ГГГГ`\n(начало и конец через пробел)\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            user_states[user_id] = {'state': 'waiting_excel_period', 'export_section': ctx}
    
    # ── Экспорт Excel (определяет контекст из user_states) ──
    @bot.message_handler(func=lambda m: m.text == "📊 Выгрузить Excel")
    def export_choose(message):
        user_id = message.from_user.id
        # Определяем контекст: user_context устанавливается ПРИ КАЖДОМ входе/возврате в раздел
        # Приоритет: achievements > plans > kpt (default)
        ctx = user_context.get(user_id, 'kpt')
        if ctx not in ('achievements', 'plans'):
            ctx = 'kpt'
        user_states[user_id] = {'state': 'export_choose', 'export_section': ctx}
        if ctx == 'achievements':
            kb = achievement_records_keyboard()
        elif ctx == 'plans':
            kb = plans_records_keyboard()
        else:
            kb = records_keyboard()
        bot.send_message(user_id, "📅 **Выберите период для выгрузки:**", reply_markup=kb)
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'waiting_excel_period')
    def handle_excel_period(message):
        user_id = message.from_user.id
        text = message.text.strip()
        ctx = user_states.get(user_id, {}).get('export_section', 'kpt')
        
        if text in ("◀️ Назад", "◀️ Назад в достижения", "◀️ Назад в планы"):
            st = user_states.get(user_id, {})
            if ctx == 'achievements':
                kb = achievement_records_keyboard()
            elif ctx == 'plans':
                kb = plans_records_keyboard()
            else:
                kb = records_keyboard()
            bot.send_message(user_id, "📅 **Выберите период для выгрузки:**", reply_markup=kb)
            user_states[user_id] = {'state': 'export_choose', 'export_section': ctx}
            return
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        
        parts = text.split()
        
        # 📅 За всё время
        if text == "📅 За всё время":
            if ctx == 'achievements':
                records = get_achievements_all(user_id)
                if not records:
                    bot.send_message(user_id, "❌ Нет достижений.", reply_markup=achievements_keyboard())
                    return
                excel_data = export_achievements_to_excel(records)
                bot.send_document(user_id, excel_data, visible_file_name="dostizheniya_vse.xlsx",
                                 caption=f"🏆 **Все достижения**\nЗаписей: {len(records)}")
                bot.send_message(user_id, "✅ Готово!", reply_markup=achievements_keyboard())
            elif ctx == 'plans':
                plans = get_all_plans(user_id)
                if not plans:
                    bot.send_message(user_id, "❌ Нет планов.", reply_markup=plans_keyboard())
                    return
                _send_plans_excel(user_id, plans, "все")
            else:
                records = get_records(user_id, 99999)
                if not records:
                    bot.send_message(user_id, "❌ Нет записей.", reply_markup=cbt_keyboard())
                    return
                excel_data = export_to_excel(records)
                bot.send_document(user_id, excel_data, visible_file_name="kpt_dnevnik_vse.xlsx",
                                 caption=f"📊 **Все записи КПТ**\nЗаписей: {len(records)}")
                bot.send_message(user_id, "✅ Готово!", reply_markup=cbt_keyboard())
            user_states[user_id] = {}
            return
        
        if len(parts) < 2:
            bot.send_message(user_id,
                f"❌ Формат: `{DATE_FORMAT_DISPLAY} {DATE_FORMAT_DISPLAY}`\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        try:
            start_date = datetime.strptime(parts[0], "%d-%m-%Y").date()
            end_date = datetime.strptime(parts[1], "%d-%m-%Y").date()
        except:
            bot.send_message(user_id,
                f"❌ Неверный формат. Используйте: `{DATE_FORMAT_DISPLAY}`\nНапример: `23-04-2026 23-04-2026`",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
            return
        
        if ctx == 'achievements':
            records = get_achievements_by_period(user_id, start_date, end_date)
            if not records:
                bot.send_message(user_id, f"❌ Нет достижений за {parts[0]} — {parts[1]}")
                user_states[user_id] = {}
                return
            excel_data = export_achievements_to_excel(records)
            filename = f"dostizheniya_{parts[0]}_po_{parts[1]}.xlsx"
            bot.send_document(user_id, excel_data, visible_file_name=filename,
                             caption=f"🏆 **Достижения**\n{parts[0]} — {parts[1]}\nЗаписей: {len(records)}")
            bot.send_message(user_id, "✅ Готово!", reply_markup=achievements_keyboard())
        elif ctx == 'plans':
            plans = get_plans_by_period(user_id, start_date, end_date)
            if not plans:
                bot.send_message(user_id, f"❌ Нет планов за {parts[0]} — {parts[1]}")
                user_states[user_id] = {}
                return
            _send_plans_excel(user_id, plans, f"{parts[0]} — {parts[1]}")
        else:
            records = get_records_by_period(user_id, start_date, end_date)
            if not records:
                bot.send_message(user_id, f"❌ Нет записей за {parts[0]} — {parts[1]}")
                user_states[user_id] = {}
                return
            excel_data = export_to_excel(records)
            filename = f"kpt_dnevnik_{parts[0]}_po_{parts[1]}.xlsx"
            bot.send_document(user_id, excel_data, visible_file_name=filename,
                             caption=f"📊 **КПТ Дневник**\n{parts[0]} — {parts[1]}\nЗаписей: {len(records)}")
            bot.send_message(user_id, "✅ Готово!", reply_markup=cbt_keyboard())
        user_states[user_id] = {}
    
    # ==================== ПЛАНЫ НА ДЕНЬ ====================
    
    @bot.message_handler(func=lambda m: m.text == "📋 Планы на день")
    def plans_section_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {}
        user_context[user_id] = 'plans'
        bot.send_message(user_id, "📋 **Планы на день**\n\nВыберите действие:", reply_markup=plans_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: m.text == "◀️ Назад в планы")
    def back_to_plans_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {}
        user_context[user_id] = 'plans'
        bot.send_message(user_id, "📋 **Планы на день**\n\nВыберите действие:", reply_markup=plans_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: m.text == "🗑 Удалить план")
    def delete_plan_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {'state': 'plan_deleting'}
        bot.send_message(user_id, "📅 **Выберите план для удаления:**", reply_markup=plan_edit_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_deleting')
    def delete_plan_period_handler(message):
        user_id = message.from_user.id
        text = message.text
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        elif text == "◀️ Назад в планы":
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        elif text == "📅 Выбрать дату✏️":
            user_states[user_id] = {'state': 'plan_deleting_input_date'}
            bot.send_message(user_id, "📅 **Введи дату в формате ДД-ММ-ГГГГ** (например, 01-05-2026):",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
            return
        
        days_map = {
            "📅 Сегодня✏️": 0,
            "📅 Завтра✏️": 1,
            "📅 Последняя неделя✏️": 7,
        }
        days = days_map.get(text)
        if days is None:
            bot.send_message(user_id, "❌ Неверный выбор.", reply_markup=plan_edit_keyboard(), parse_mode='Markdown')
            return
        
        if days <= 1:
            target_date = date.today().strftime("%Y-%m-%d") if days == 0 else (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            plan_id = get_or_create_plan(user_id, target_date)
            
            # Проверяем, есть ли хоть что-то
            items = get_plan_items(plan_id)
            if not items:
                # Нет пунктов — просто удаляем
                delete_plan(plan_id)
                bot.send_message(user_id, f"🗑 **План на {fmt_date_str(target_date)} удалён.**", reply_markup=plans_keyboard(), parse_mode='Markdown')
                user_states[user_id] = {}
                return
            
            user_states[user_id] = {'state': 'plan_deleting_confirm', 'plan_id': plan_id, 'plan_date': target_date}
            plan_list = "\n".join([f"{'✅' if i[2] else '⬜'} {i[1]}" for i in items])
            bot.send_message(user_id,
                f"🗑 **Удалить план на {fmt_date_str(target_date)}?**\n\n{plan_list}\n\n"
                f"Напиши **да** чтобы подтвердить или **нет** для отмены:",
                reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
        else:
            plans = get_user_plans(user_id, days=7)
            if plans:
                msg = "🗑 **Планы за неделю**\n\n"
                for pid, pdate in plans:
                    items = get_plan_items(pid)
                    total = len(items)
                    msg += f"📅 **{fmt_date_str(pdate)}** — {total} пунктов\n"
                msg += "\nВыбери день для удаления."
                bot.send_message(user_id, msg, reply_markup=plan_edit_keyboard(), parse_mode='Markdown')
            else:
                bot.send_message(user_id, "📋 Нет планов за последнюю неделю.", reply_markup=plan_edit_keyboard())
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_deleting_confirm')
    def delete_plan_confirm_handler(message):
        user_id = message.from_user.id
        text = message.text.strip().lower()
        st = user_states.get(user_id, {})
        
        if text in ("🏠 Главное меню", "◀️ Назад в планы", "нет", "✅ Готово"):
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        if text == "да":
            plan_id = st.get('plan_id')
            plan_date = st.get('plan_date', 'неизвестно')
            if plan_id:
                delete_plan(plan_id)
                bot.send_message(user_id, f"🗑 **План на {fmt_date_str(plan_date)} удалён.**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            else:
                bot.send_message(user_id, "❌ Ошибка. Попробуй ещё раз.", reply_markup=plans_keyboard())
            user_states[user_id] = {}
        else:
            bot.send_message(user_id, "❌ Напиши **да** для подтверждения или **нет** для отмены.",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_deleting_input_date')
    def delete_plan_input_date_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text in ("✅ Готово", "◀️ Назад в планы", "🏠 Главное меню"):
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        try:
            parsed = datetime.strptime(text, "%d-%m-%Y")
            target_date = parsed.strftime("%Y-%m-%d")
            
            # Ищем план
            existing_id, has_items = check_plan_exists(user_id, target_date)
            if not existing_id:
                bot.send_message(user_id, f"❌ План на {fmt_date_str(target_date)} не найден. Выбери другую дату:",
                               reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
                return
            
            if not has_items:
                delete_plan(existing_id)
                bot.send_message(user_id, f"🗑 **План на {fmt_date_str(target_date)} удалён.**", reply_markup=plans_keyboard(), parse_mode='Markdown')
                user_states[user_id] = {}
                return
            
            user_states[user_id] = {'state': 'plan_deleting_confirm', 'plan_id': existing_id, 'plan_date': target_date}
            items = get_plan_items(existing_id)
            plan_list = "\n".join([f"{'✅' if i[2] else '⬜'} {i[1]}" for i in items])
            bot.send_message(user_id,
                f"🗑 **Удалить план на {fmt_date_str(target_date)}?**\n\n{plan_list}\n\n"
                f"Напиши **да** чтобы подтвердить или **нет** для отмены:",
                reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
        except ValueError:
            bot.send_message(user_id, "❌ Неверный формат. Введи дату как **ДД-ММ-ГГГГ** (например, 01-05-2026):",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: m.text == "📝 Новый план")
    def new_plan_handler(message):
        user_id = message.from_user.id
        if user_id != ADMIN_ID:
            count = count_user_plans(user_id)
            if count >= MAX_FREE_PLANS:
                bot.send_message(user_id,
                    f"⚠️ **Бесплатная версия**\n\n"
                    f"Ты можешь создать только **{MAX_FREE_PLANS}** плана в бесплатной версии.\n"
                    f"Чтобы продолжить — свяжись с @dmr_167",
                    reply_markup=plans_keyboard(), parse_mode='Markdown')
                return
        user_states[user_id] = {'state': 'plan_choosing_date'}
        bot.send_message(user_id,
            "📝 **Новый план**\n\n"
            "Выбери дату, на которую хочешь составить план:",
            reply_markup=plan_date_choice_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_choosing_date')
    def plan_choose_date_handler(message):
        user_id = message.from_user.id
        text = message.text
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        elif text == "◀️ Назад в планы":
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        elif text == "✏️ Редактировать план":
            user_states[user_id] = {}
            bot.send_message(user_id, "📅 **Выберите план для редактирования:**", reply_markup=plan_edit_keyboard(), parse_mode='Markdown')
            user_states[user_id] = {'state': 'plan_edit'}
            return
        
        target_date = None
        if text == "📅 Сегодня":
            target_date = date.today().strftime("%Y-%m-%d")
        elif text == "📅 Завтра":
            target_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif text == "📅 Выбрать дату":
            user_states[user_id] = {'state': 'plan_input_date'}
            bot.send_message(user_id, "📅 **Введи дату в формате ДД-ММ-ГГГГ** (например, 01-05-2026):",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
            return
        else:
            bot.send_message(user_id, "❌ Неверный выбор.", reply_markup=plan_date_choice_keyboard(), parse_mode='Markdown')
            return
        
        existing_id, has_items = check_plan_exists(user_id, target_date)
        if existing_id:
            if has_items:
                bot.send_message(user_id,
                    f"⚠️ **План на {fmt_date_str(target_date)} уже существует!**\n\n"
                    f"Ты можешь отредактировать его через **✏️ Редактировать план** "
                    f"или выбрать другую дату для создания нового плана.",
                    reply_markup=plans_keyboard(), parse_mode='Markdown')
                return
            # Если план существует, но пуст — разрешаем добавить пункты
            user_states[user_id] = {'state': 'plan_adding', 'plan_id': existing_id, 'plan_date': target_date}
            bot.send_message(user_id,
                f"📝 **План на {fmt_date_str(target_date)}** (пустой)\n\n"
                "Добавляй пункты...",
                reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
            return
        
        plan_id = get_or_create_plan(user_id, target_date)
        user_states[user_id] = {'state': 'plan_adding', 'plan_id': plan_id, 'plan_date': target_date}
        bot.send_message(user_id,
            f"📝 **План на {fmt_date_str(target_date)}**\n\n"
            "Пиши пункты плана по одному. Каждый пункт — новое сообщение.\n"
            "Когда закончишь — нажми **✅ Готово**.",
            reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_input_date')
    def plan_input_date_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text in ("✅ Готово", "◀️ Назад в планы", "🏠 Главное меню"):
            if text == "🏠 Главное меню":
                user_states[user_id] = {}
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            elif text == "◀️ Назад в планы":
                user_states[user_id] = {}
                bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            else:
                user_states[user_id] = {}
                bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        try:
            parsed = datetime.strptime(text, "%d-%m-%Y")
            target_date = parsed.strftime("%Y-%m-%d")
            existing_id, has_items = check_plan_exists(user_id, target_date)
            if existing_id:
                if has_items:
                    bot.send_message(user_id,
                        f"⚠️ **План на {fmt_date_str(target_date)} уже существует!**\n\n"
                        f"Ты можешь отредактировать его через **✏️ Редактировать план** "
                        f"или выбрать другую дату.",
                        reply_markup=plans_keyboard(), parse_mode='Markdown')
                    return
                user_states[user_id] = {'state': 'plan_adding', 'plan_id': existing_id, 'plan_date': target_date}
                bot.send_message(user_id,
                    f"📝 **План на {fmt_date_str(target_date)}** (пустой)\n\n"
                    "Добавляй пункты...",
                    reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
                return
            
            plan_id = get_or_create_plan(user_id, target_date)
            user_states[user_id] = {'state': 'plan_adding', 'plan_id': plan_id, 'plan_date': target_date}
            bot.send_message(user_id,
                f"📝 **План на {fmt_date_str(target_date)}**\n\n"
                "Пиши пункты плана по одному. Каждый пункт — новое сообщение.\n"
                "Когда закончишь — нажми **✅ Готово**.",
                reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
        except ValueError:
            bot.send_message(user_id, "❌ Неверный формат. Введи дату как **ДД-ММ-ГГГГ** (например, 01-05-2026):",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: m.text == "✅ Готово" and not user_states.get(m.from_user.id, {}).get('state', '').startswith('ach_'))
    def plan_done_handler(message):
        user_id = message.from_user.id
        st = user_states.get(user_id, {})
        if st.get('state') == 'plan_adding':
            plan_id = st['plan_id']
            plan_date = st.get('plan_date', date.today().strftime("%Y-%m-%d"))
            items = get_plan_items(plan_id)
            if items:
                plan_list = "\n".join([f"{'✅' if i[2] else '⬜'} {i[1]}" for i in items])
                bot.send_message(user_id,
                    f"✅ **План на {fmt_date_str(plan_date)} сохранён!**\n\n{plan_list}",
                    reply_markup=plans_keyboard(), parse_mode='Markdown')
            else:
                bot.send_message(user_id, "⚠️ План пуст. Добавь хотя бы один пункт.", reply_markup=plans_keyboard())
            user_states[user_id] = {}
        else:
            bot.send_message(user_id, "❌ Нет активного плана.", reply_markup=plans_keyboard())
    
    # Обработчик добавления пунктов в план
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_adding')
    def plan_add_item_handler(message):
        user_id = message.from_user.id
        st = user_states[user_id]
        text = message.text.strip()
        if len(text) > 0 and text != "✅ Готово" and text != "◀️ Назад в планы" and text != "🏠 Главное меню":
            add_plan_item(st['plan_id'], text)
            bot.send_message(user_id, f"✅ Добавлено: _{text}_\nМожешь добавить ещё или нажми **✅ Готово**.",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
    
    # Просмотр планов
    @bot.message_handler(func=lambda m: m.text == "📋 Мои планы")
    def plans_view_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {'state': 'plan_view'}
        bot.send_message(user_id, "📅 **Выберите период:**", reply_markup=plan_view_keyboard(), parse_mode='Markdown')
    
    # Обработчик кнопок просмотра планов
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_view')
    def plans_view_period_handler(message):
        user_id = message.from_user.id
        text = message.text
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        elif text == "◀️ Назад в планы":
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        elif text == "📅 Выбрать дату":
            user_states[user_id] = {'state': 'plan_mark_done_date_input'}
            bot.send_message(user_id, "📅 **Введи дату в формате ДД-ММ-ГГГГ** (например, 01-05-2026):",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
            return
        
        # 📅 За всё время для планов
        if text == "📅 За всё время📋":
            all_plans = get_all_plans(user_id)
            if not all_plans:
                bot.send_message(user_id, "❌ Нет планов.", reply_markup=plan_view_keyboard(), parse_mode='Markdown')
                return
            msg = "📋 **Все планы**\n\n"
            for plan in all_plans:
                items_html = "\n".join([f"  {'✅' if i[2] else '⬜'} {i[1]}" for i in plan['items']])
                msg += f"📅 **{fmt_date_str(plan['date'])}**\n{items_html}\n\n"
            msg = msg[:4000]
            bot.send_message(user_id, msg, reply_markup=plan_view_keyboard(), parse_mode='Markdown')
            return
        
        days_map = {
            "📅 Сегодня": 0,
            "📅 Завтра": 1,
            "📅 Последняя неделя": 7,
        }
        days = days_map.get(text)
        if days is None:
            bot.send_message(user_id, "❌ Неверный выбор.", reply_markup=plan_view_keyboard(), parse_mode='Markdown')
            return
        
        if days == 1:
            target_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            target_date = date.today().strftime("%Y-%m-%d") if days == 0 else None
        
        if days <= 1:
            plan_id = get_or_create_plan(user_id, target_date)
            items = get_plan_items(plan_id)
            day_label = "Сегодня" if days == 0 else "Завтра"
            if items:
                plan_list = "\n".join([f"{'✅' if i[2] else '⬜'} {i[1]}" for i in items])
                msg = f"📋 **План на {fmt_date_str(target_date)}**\n\n{plan_list}"
            else:
                msg = f"📋 **План на {fmt_date_str(target_date)}**\n\n_Пока пусто. Напиши пункты через **📝 Новый план**_"
            bot.send_message(user_id, msg, reply_markup=plan_view_keyboard(), parse_mode='Markdown')
        else:
            plans = get_user_plans(user_id, days=7)
            if plans:
                msg = "📋 **Планы за неделю**\n\n"
                for pid, pdate in plans:
                    items = get_plan_items(pid)
                    total = len(items)
                    done = sum(1 for i in items if i[2])
                    msg += f"📅 **{fmt_date_str(pdate)}** — {done}/{total} ✅\n"
            else:
                msg = "📋 Нет планов за последнюю неделю."
            bot.send_message(user_id, msg, reply_markup=plan_view_keyboard(), parse_mode='Markdown')
    
    # Редактирование планов
    @bot.message_handler(func=lambda m: m.text == "✏️ Редактировать план")
    def plans_edit_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {'state': 'plan_edit'}
        bot.send_message(user_id, "📅 **Выберите план для редактирования:**", reply_markup=plan_edit_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_edit')
    def plans_edit_period_handler(message):
        user_id = message.from_user.id
        text = message.text
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        elif text == "◀️ Назад в планы":
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        if text == "📅 Выбрать дату✏️":
            user_states[user_id] = {'state': 'plan_edit_input_date'}
            bot.send_message(user_id, "📅 **Введи дату в формате ДД-ММ-ГГГГ** (например, 01-05-2026):",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
            return
        
        days_map = {
            "📅 Сегодня✏️": 0,
            "📅 Завтра✏️": 1,
            "📅 Последняя неделя✏️": 7,
        }
        days = days_map.get(text)
        if days is None:
            bot.send_message(user_id, "❌ Неверный выбор.", reply_markup=plan_edit_keyboard(), parse_mode='Markdown')
            return
        
        target_date = date.today().strftime("%Y-%m-%d")
        if days == 1:
            target_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        if days <= 1:
            plan_id = get_or_create_plan(user_id, target_date)
            items = get_plan_items(plan_id)
            if items:
                plan_list = "\n".join([f"{'✅' if i[2] else '⬜'} **#{idx+1}** {i[1]}" for idx, i in enumerate(items)])
                msg = f"📋 **План на {fmt_date_str(target_date)}**\n\n{plan_list}\n\nЧто хочешь сделать?"
            else:
                msg = "📋 План пуст. Добавь пункты через **➕ Добавить пункт**."
            
            user_states[user_id] = {'state': 'plan_editing_items', 'plan_id': plan_id}
            bot.send_message(user_id, msg, reply_markup=plan_item_actions_keyboard(), parse_mode='Markdown')
        else:
            plans = get_user_plans(user_id, days=7)
            if plans:
                msg = "📋 **Планы за неделю для редактирования**\n\n"
                for pid, pdate in plans:
                    items = get_plan_items(pid)
                    total = len(items)
                    done = sum(1 for i in items if i[2])
                    msg += f"📅 **{fmt_date_str(pdate)}** (#{pid}) — {done}/{total} ✅\n"
                msg += "\nВыбери день выше или используй **📅 Сегодня✏️ / 📅 Завтра✏️**"
                bot.send_message(user_id, msg, reply_markup=plan_edit_keyboard(), parse_mode='Markdown')
            else:
                bot.send_message(user_id, "📋 Нет планов за последнюю неделю.", reply_markup=plan_edit_keyboard())
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_edit_input_date')
    def plan_edit_input_date_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text in ("✅ Готово", "◀️ Назад в планы", "🏠 Главное меню"):
            if text == "🏠 Главное меню":
                user_states[user_id] = {}
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                user_states[user_id] = {}
                bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        try:
            parsed = datetime.strptime(text, "%d-%m-%Y")
            target_date = parsed.strftime("%Y-%m-%d")
            plan_id = get_or_create_plan(user_id, target_date)
            items = get_plan_items(plan_id)
            if items:
                plan_list = "\n".join([f"{'✅' if i[2] else '⬜'} **#{idx+1}** {i[1]}" for idx, i in enumerate(items)])
                msg = f"📋 **План на {fmt_date_str(target_date)}**\n\n{plan_list}\n\nЧто хочешь сделать?"
            else:
                msg = "📋 План пуст. Добавь пункты через **➕ Добавить пункт**."
            user_states[user_id] = {'state': 'plan_editing_items', 'plan_id': plan_id}
            bot.send_message(user_id, msg, reply_markup=plan_item_actions_keyboard(), parse_mode='Markdown')
        except ValueError:
            bot.send_message(user_id, "❌ Неверный формат. Введи дату как **ДД-ММ-ГГГГ** (например, 01-05-2026):",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_editing_items')
    def plan_item_actions_handler(message):
        user_id = message.from_user.id
        text = message.text
        st = user_states.get(user_id, {})
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        elif text == "◀️ Назад в планы":
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        elif text == "➕ Добавить пункт":
            user_states[user_id] = {'state': 'plan_adding_item', 'plan_id': st.get('plan_id')}
            bot.send_message(user_id, "✏️ **Напиши новый пункт плана:**", reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
            return
        elif text == "🗑 Удалить пункт":
            user_states[user_id] = {'state': 'plan_deleting_item', 'plan_id': st.get('plan_id')}
            items = get_plan_items(st.get('plan_id'))
            items_list = "\n".join([f"#{idx+1} — {i[1]}" for idx, i in enumerate(items)])
            bot.send_message(user_id, f"🗑 **Напиши номер пункта (#N) для удаления:**\n\n{items_list}",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
            return
        elif text == "✏️ Редактировать пункт":
            user_states[user_id] = {'state': 'plan_renaming_choose', 'plan_id': st.get('plan_id')}
            items = get_plan_items(st.get('plan_id'))
            items_list = "\n".join([f"#{idx+1} — {i[1]}" for idx, i in enumerate(items)])
            bot.send_message(user_id, f"✏️ **Напиши номер пункта (#ID), который хочешь изменить:**\n\n{items_list}",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
            return
        
        # Чекбокс — переключение по #ID
        if text.startswith("#"):
            try:
                item_id = int(text[1:].split()[0])
                toggle_plan_item(item_id)
                items = get_plan_items(st.get('plan_id'))
                plan_list = "\n".join([f"{'✅' if i[2] else '⬜'} **#{idx+1}** {i[1]}" for idx, i in enumerate(items)])
                bot.send_message(user_id, f"✅ Обновлено!\n\n{plan_list}",
                               reply_markup=plan_item_actions_keyboard(), parse_mode='Markdown')
            except:
                bot.send_message(user_id, "❌ Неверный формат. Используй **#ID** (например, #5).",
                               reply_markup=plan_item_actions_keyboard(), parse_mode='Markdown')
            return
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_adding_item')
    def plan_add_one_item_handler(message):
        user_id = message.from_user.id
        text = message.text
        st = user_states.get(user_id, {})
        
        if text == "✅ Готово" or text == "◀️ Назад в планы" or text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        add_plan_item(st['plan_id'], text)
        bot.send_message(user_id, f"✅ Добавлено: _{escape_md(text)}_", reply_markup=plan_item_actions_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'plan_editing_items', 'plan_id': st['plan_id']}
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_renaming_choose')
    def plan_rename_choose_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states.get(user_id, {})
        
        if text in ("✅ Готово", "◀️ Назад в планы", "🏠 Главное меню"):
            if text == "🏠 Главное меню":
                user_states[user_id] = {}
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                user_states[user_id] = {}
                bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        try:
            local_idx = int(text.lstrip('#')) - 1
            items = get_plan_items(st.get('plan_id'))
            if local_idx < 0 or local_idx >= len(items):
                bot.send_message(user_id, f"❌ Неверный номер. Используй #1, #2 и т.д.",
                               reply_markup=plan_fill_keyboard())
                return
            item_id = items[local_idx][0]
            current_text = items[local_idx][1]
            user_states[user_id] = {'state': 'plan_renaming_input', 'plan_id': st['plan_id'], 'item_id': item_id}
            
            # Отправляем сообщение с удобным копированием
            bot.send_message(user_id,
                f"✏️ **Редактирование пункта #{local_idx+1}**\n\n"
                f"Текущий текст (нажмите чтобы скопировать):\n`{current_text}`\n\n"
                f"Напиши новый текст для этого пункта:",
                reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
        except ValueError:
            bot.send_message(user_id, "❌ Напиши номер пункта (например, 5 или #5).",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_renaming_input')
    def plan_rename_input_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states.get(user_id, {})
        
        if text in ("✅ Готово", "◀️ Назад в планы", "🏠 Главное меню"):
            if text == "🏠 Главное меню":
                user_states[user_id] = {}
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                user_states[user_id] = {}
                bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        item_id = st.get('item_id')
        if not item_id:
            user_states[user_id] = {}
            bot.send_message(user_id, "❌ Что-то пошло не так.", reply_markup=plans_keyboard())
            return
        
        if not text:
            bot.send_message(user_id, "❌ Текст не может быть пустым. Напиши новый текст для пункта:",
                           reply_markup=plan_fill_keyboard())
            return
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('UPDATE plan_items SET text = ? WHERE id = ?', (text, item_id))
        conn.commit()
        conn.close()
        
        bot.send_message(user_id, f"✅ Пункт #{item_id} обновлён: _{text}_",
                       reply_markup=plan_item_actions_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {'state': 'plan_editing_items', 'plan_id': st['plan_id']}
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_deleting_item')
    def plan_delete_item_handler(message):
        user_id = message.from_user.id
        text = message.text
        st = user_states.get(user_id, {})
        
        if text == "✅ Готово" or text == "◀️ Назад в планы" or text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        try:
            item_id = int(text.strip().lstrip('#'))
            delete_plan_item(item_id)
            bot.send_message(user_id, f"✅ Пункт удалён.", reply_markup=plan_item_actions_keyboard())
        except:
            bot.send_message(user_id, "❌ Напиши номер пункта (например, 5 или #5).",
                           reply_markup=plan_fill_keyboard())
            return
        
        user_states[user_id] = {'state': 'plan_editing_items', 'plan_id': st['plan_id']}

    # ==== ОТМЕТИТЬ ВЫПОЛНЕНИЕ (инлайн-чекбоксы) ====
    @bot.message_handler(func=lambda m: m.text == "✅ Отметить выполнение")
    def plan_mark_done_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {'state': 'plan_mark_done'}
        bot.send_message(user_id, "📅 **Выберите день:**", reply_markup=plan_view_keyboard(), parse_mode='Markdown')
    
    def build_plan_inline_keyboard(plan_id):
        items = get_plan_items(plan_id)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for iid, text, done, _ in items:
            emoji = "✅" if done else "⬜"
            keyboard.add(types.InlineKeyboardButton(f"{emoji} {text}", callback_data=f"plan_toggle_{iid}"))
        return keyboard
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_mark_done_date_input')
    def plan_mark_done_date_input_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text in ("✅ Готово", "◀️ Назад в планы", "🏠 Главное меню"):
            if text == "🏠 Главное меню":
                user_states[user_id] = {}
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                user_states[user_id] = {}
                bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        try:
            parsed = datetime.strptime(text, "%d-%m-%Y")
            target_date = parsed.strftime("%Y-%m-%d")
            plan_id = get_or_create_plan(user_id, target_date)
            items = get_plan_items(plan_id)
            
            if items:
                keyboard = build_plan_inline_keyboard(plan_id)
                bot.send_message(user_id, f"📋 **План на {fmt_date_str(target_date)}**\n\nНажимай на пункты, чтобы переключить статус:",
                               reply_markup=keyboard, parse_mode='Markdown')
            else:
                bot.send_message(user_id, f"📋 **План на {fmt_date_str(target_date)}**\n\n_Пока пуст._",
                               reply_markup=plans_keyboard(), parse_mode='Markdown')
                user_states[user_id] = {}
        except ValueError:
            bot.send_message(user_id, "❌ Неверный формат. Введи дату как **ДД-ММ-ГГГГ** (например, 01-05-2026):",
                           reply_markup=plan_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'plan_mark_done')
    def plan_mark_done_period_handler(message):
        user_id = message.from_user.id
        text = message.text
        
        if text == "🏠 Главное меню":
            user_states[user_id] = {}
            bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        elif text == "◀️ Назад в планы":
            user_states[user_id] = {}
            bot.send_message(user_id, "📋 **Планы на день**", reply_markup=plans_keyboard(), parse_mode='Markdown')
            return
        
        days_map = {
            "📅 Сегодня": 0,
            "📅 Завтра": 1,
            "📅 Последняя неделя": 7,
        }
        days = days_map.get(text)
        if days is None:
            bot.send_message(user_id, "❌ Неверный выбор.", reply_markup=plan_view_keyboard(), parse_mode='Markdown')
            return
        
        if days <= 1:
            target_date = date.today().strftime("%Y-%m-%d") if days == 0 else (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            plan_id = get_or_create_plan(user_id, target_date)
            items = get_plan_items(plan_id)
            day_label = "Сегодня" if days == 0 else "Завтра"
            
            if items:
                keyboard = build_plan_inline_keyboard(plan_id)
                bot.send_message(user_id, f"📋 **План на {fmt_date_str(target_date)}**\n\nНажимай на пункты, чтобы переключить статус:",
                               reply_markup=keyboard, parse_mode='Markdown')
            else:
                bot.send_message(user_id, f"📋 **План на {fmt_date_str(target_date)}**\n\n_Пока пуст._",
                               reply_markup=plans_keyboard(), parse_mode='Markdown')
                user_states[user_id] = {}
        else:
            plans = get_user_plans(user_id, days=7)
            if plans:
                msg = "📋 **Планы за неделю**\n\n"
                for pid, pdate in plans:
                    items = get_plan_items(pid)
                    total = len(items)
                    done = sum(1 for i in items if i[2])
                    msg += f"📅 **{fmt_date_str(pdate)}** — {done}/{total} ✅\n"
                msg += "\nВыбери день выше для отметки."
                bot.send_message(user_id, msg, reply_markup=plan_view_keyboard(), parse_mode='Markdown')
            else:
                bot.send_message(user_id, "📋 Нет планов за последнюю неделю.", reply_markup=plan_view_keyboard())
                user_states[user_id] = {}
    
    @bot.callback_query_handler(func=lambda c: c.data.startswith('plan_toggle_'))
    def plan_toggle_callback(call):
        user_id = call.from_user.id
        item_id = int(call.data.replace('plan_toggle_', ''))
        
        toggle_plan_item(item_id)
        
        # Находим plan_id из базы (любой пункт из того же плана)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT plan_id FROM plan_items WHERE id = ?', (item_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            plan_id = row[0]
            keyboard = build_plan_inline_keyboard(plan_id)
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.id, reply_markup=keyboard)
        
        bot.answer_callback_query(call.id)
    
    # ==================== ДОСТИЖЕНИЯ ====================
    
    @bot.message_handler(func=lambda m: m.text == "🏆 Мои достижения")
    def achievements_section_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {'section': 'achievements'}
        user_context[user_id] = 'achievements'
        count = count_achievements(user_id)
        msg = f"🏆 **Мои достижения** ({count} шт.)\n\n"
        if user_id != ADMIN_ID:
            msg += f"⚠️ Бесплатно: **{count}/{MAX_FREE_ACHIEVEMENTS}**\n\n"
        msg += "Выберите действие:"
        bot.send_message(user_id, msg, reply_markup=achievements_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: m.text == "◀️ Назад в достижения")
    def back_to_achievements_handler(message):
        user_id = message.from_user.id
        user_states[user_id] = {'section': 'achievements'}
        user_context[user_id] = 'achievements'
        count = count_achievements(user_id)
        bot.send_message(user_id,
            f"🏆 **Мои достижения** ({count} шт.)\n\nВыберите действие:",
            reply_markup=achievements_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: m.text == "➕ Добавить одно")
    def add_one_achievement_handler(message):
        user_id = message.from_user.id
        if user_id != ADMIN_ID and count_achievements(user_id) >= MAX_FREE_ACHIEVEMENTS:
            bot.send_message(user_id,
                f"⚠️ **Бесплатная версия**\n\n"
                f"Ты можешь добавить только **{MAX_FREE_ACHIEVEMENTS}** достижения в бесплатной версии.\n"
                f"Чтобы продолжить — свяжись с @dmr_167",
                reply_markup=achievements_keyboard(), parse_mode='Markdown')
            return
        user_states[user_id] = {'state': 'ach_adding_one'}
        bot.send_message(user_id,
            "🏆 **Добавить достижение**\n\n"
            "Напиши текст достижения. После добавления можно будет добавить ещё.\n"
            "Готово — **✅ Готово** или **◀️ Назад в достижения**",
            reply_markup=achievement_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'ach_adding_one')
    def ach_add_one_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        if text in ("✅ Готово", "🗑 Удалить все", "◀️ Назад в достижения", "🏠 Главное меню"):
            user_states[user_id] = {}
            if text == "🏠 Главное меню":
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                count = count_achievements(user_id)
                bot.send_message(user_id, f"🏆 Сейчас у тебя **{count}** достижений.",
                               reply_markup=achievements_keyboard(), parse_mode='Markdown')
            return
        
        if not text:
            bot.send_message(user_id, "❌ Текст не может быть пустым. Напиши достижение:", reply_markup=achievement_fill_keyboard())
            return
        
        cleaned = clean_achievement_text(text)
        add_achievement(user_id, cleaned)
        count = count_achievements(user_id)
        bot.send_message(user_id, f"✅ '{cleaned}' добавлено! Теперь у тебя **{count}** достижений.\n\nМожешь добавить ещё или **✅ Готово**.",
                       reply_markup=achievement_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: m.text == "📝 Добавить несколько")
    def add_multi_achievement_handler(message):
        user_id = message.from_user.id
        if user_id != ADMIN_ID and count_achievements(user_id) >= MAX_FREE_ACHIEVEMENTS:
            bot.send_message(user_id,
                f"⚠️ **Бесплатная версия**\n\n"
                f"Ты можешь добавить только **{MAX_FREE_ACHIEVEMENTS}** достижения в бесплатной версии.\n"
                f"Чтобы продолжить — свяжись с @dmr_167",
                reply_markup=achievements_keyboard(), parse_mode='Markdown')
            return
        user_states[user_id] = {'state': 'ach_adding_multi'}
        bot.send_message(user_id,
            "🏆 **Добавить несколько достижений**\n\n"
            "Пришли список, каждый пункт с новой строки:\n\n"
            "```\nНаписал первую главу книги\n"
            "Пробежал 5 км\n"
            "Помыл посуду\n```\n\n"
            "Готово — **✅ Готово** или **◀️ Назад в достижения**",
            reply_markup=achievement_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'ach_adding_multi')
    def ach_add_multi_handler(message):
        user_id = message.from_user.id
        text = message.text
        
        if text == "✅ Готово" or text == "◀️ Назад в достижения" or text == "🏠 Главное меню" or text == "🗑 Удалить все":
            user_states[user_id] = {}
            if text == "🏠 Главное меню":
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                count = count_achievements(user_id)
                bot.send_message(user_id, f"🏆 Сейчас у тебя **{count}** достижений.",
                               reply_markup=achievements_keyboard(), parse_mode='Markdown')
            return
        
        # Разбиваем текст на строки, чистим пустые
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            bot.send_message(user_id, "❌ Нет текста. Пришли список достижений, каждый с новой строки.",
                           reply_markup=achievement_fill_keyboard())
            return
        
        added = 0
        if user_id != ADMIN_ID:
            current = count_achievements(user_id)
            remaining = MAX_FREE_ACHIEVEMENTS - current
            if len(lines) > remaining:
                total_requested = len(lines)
                lines = lines[:remaining]
                added = len(lines)
                bot.send_message(user_id,
                    f"⚠️ Бесплатная версия — максимум **{MAX_FREE_ACHIEVEMENTS}** достижения.\n"
                    f"Добавлено только **{added}** из {total_requested}.",
                    reply_markup=achievement_fill_keyboard(), parse_mode='Markdown')
        for line in lines:
            cleaned = clean_achievement_text(line)
            add_achievement(user_id, cleaned)
            added += 1
        
        count = count_achievements(user_id)
        bot.send_message(user_id, f"✅ Добавлено **{added}** достижений! Теперь у тебя **{count}** шт.\n\nМожешь добавить ещё или **✅ Готово**.",
                       reply_markup=achievement_fill_keyboard(), parse_mode='Markdown')
    
    @bot.message_handler(func=lambda m: m.text == "📋 Мои достижения" and user_states.get(m.from_user.id, {}).get('state') != 'ach_adding_multi')
    def view_achievements_handler(message):
        user_id = message.from_user.id
        items = get_user_achievements(user_id)
        if not items:
            bot.send_message(user_id, "🏆 **У тебя пока нет достижений.**\n\nНачни добавлять через **➕ Добавить одно** или **📝 Добавить несколько**.",
                           reply_markup=achievements_keyboard(), parse_mode='Markdown')
            return
        
        # Перестраиваем с нумерацией
        numbered = []
        for idx, (iid, text, pos) in enumerate(items, 1):
            numbered.append(f"{idx}. {text}")
        
        chunks = []
        current = []
        for line in numbered:
            current.append(line)
            if len(current) == 20:
                chunks.append("\n".join(current))
                current = []
        if current:
            chunks.append("\n".join(current))
        
        msg = f"🏆 **Мои достижения** ({len(items)} шт.)\n\n"
        bot.send_message(user_id, msg + chunks[0], reply_markup=achievements_keyboard(), parse_mode='Markdown')
        for chunk in chunks[1:]:
            bot.send_message(user_id, chunk, reply_markup=achievements_keyboard(), parse_mode='Markdown')
    @bot.message_handler(func=lambda m: m.text in ("✏️ Редактировать достижения", "🗑 Удалить достижение", "🗑 Удалить все"))
    def ach_edit_del_handler(message):
        txt = message.text
        uid = message.from_user.id
        user_states[uid] = {}
        is_edit = txt == "✏️ Редактировать достижения"
        is_del_all = txt == "🗑 Удалить все"
        
        if is_del_all:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('DELETE FROM achievements WHERE user_id = ?', (uid,))
            conn.commit()
            conn.close()
            bot.send_message(uid, "✅ Все достижения удалены!", reply_markup=achievements_keyboard())
            return
        
        items = get_user_achievements(uid)
        if not items:
            emoji = "✏️" if is_edit else "🗑"
            bot.send_message(uid, f"{emoji} Нет достижений.", reply_markup=achievements_keyboard())
            return
        
        item_lines = [f"#{idx+1} {text}" for idx, (iid, text, pos) in enumerate(items)]
        
        chunks = []
        current = []
        current_len = 0
        for line in item_lines:
            line_len = len(line) + 1
            if current_len + line_len > 3500:
                chunks.append("\n".join(current))
                current = []
                current_len = 0
            current.append(line)
            current_len += line_len
        if current:
            chunks.append("\n".join(current))
        
        if is_edit:
            user_states[uid] = {'state': 'ach_editing_choose'}
            header = f"✏️ **Редактировать достижения**\n\nНапиши **#ID** достижения, которое хочешь изменить:\n\n"
        else:
            user_states[uid] = {'state': 'ach_deleting'}
            header = f"🗑 **Удалить достижение**\n\nНапиши **#ID** достижения для удаления:\n\n"
        
        bot.send_message(uid, header + chunks[0], reply_markup=achievement_fill_keyboard(), parse_mode='Markdown')
        for chunk in chunks[1:]:
            bot.send_message(uid, chunk, reply_markup=achievement_fill_keyboard(), parse_mode='Markdown')
































    @bot.message_handler(func=lambda m: m.text == "🗑 Удалить все" and user_states.get(m.from_user.id, {}).get('state', '').startswith('ach_'))
    def ach_del_all_from_state_handler(message):
        uid = message.from_user.id
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DELETE FROM achievements WHERE user_id = ?', (uid,))
        conn.commit()
        conn.close()
        user_states[uid] = {}
        bot.send_message(uid, "✅ Все достижения удалены!", reply_markup=achievements_keyboard())
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'ach_editing_choose')
    def ach_edit_choose_handler(message):
        uid = message.from_user.id
        text = message.text.strip()
        
        if text in ("✅ Готово", "🗑 Удалить все", "◀️ Назад в достижения", "🏠 Главное меню"):
            user_states[uid] = {}
            if text == "🏠 Главное меню":
                bot.send_message(uid, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                count = count_achievements(uid)
                bot.send_message(uid, f"🏆 **Мои достижения** ({count} шт.)", reply_markup=achievements_keyboard(), parse_mode='Markdown')
            return
        
        try:
            local_idx = int(text.lstrip('#')) - 1
            items = get_user_achievements(uid)
            if local_idx < 0 or local_idx >= len(items):
                bot.send_message(uid, f"❌ Неверный номер. Используй #1, #2 и т.д.",
                               reply_markup=achievement_fill_keyboard())
                return
            item_id = items[local_idx][0]
            current_text = items[local_idx][1]
            
            user_states[uid] = {'state': 'ach_editing_input', 'edit_id': item_id, 'edit_idx': local_idx+1}
            bot.send_message(uid,
                f"✏️ **Редактирование #{local_idx+1}**\n\n"
                f"Текущий текст (нажмите чтобы скопировать):\n`{current_text}`\n\n"
                f"Напиши новый текст:",
                reply_markup=achievement_fill_keyboard(), parse_mode='Markdown')
        except ValueError:
            bot.send_message(uid, "❌ Напиши номер достижения (например, 5 или #5).",
                           reply_markup=achievement_fill_keyboard())
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'ach_editing_input')
    def ach_edit_input_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        st = user_states.get(user_id, {})
        
        if text in ("✅ Готово", "🗑 Удалить все", "◀️ Назад в достижения", "🏠 Главное меню"):
            user_states[user_id] = {}
            if text == "🏠 Главное меню":
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                count = count_achievements(user_id)
                bot.send_message(user_id, f"🏆 **Мои достижения** ({count} шт.)", reply_markup=achievements_keyboard(), parse_mode='Markdown')
            return
        
        item_id = st.get('edit_id')
        if not item_id:
            user_states[user_id] = {}
            bot.send_message(user_id, "❌ Ошибка. Попробуй ещё раз.", reply_markup=achievements_keyboard())
            return
        
        if not text:
            bot.send_message(user_id, "❌ Текст не может быть пустым. Напиши новый текст:", reply_markup=achievement_fill_keyboard())
            return
        
        update_achievement(item_id, text)
        idx = st.get("edit_idx", item_id)
        bot.send_message(user_id, f"✅ Достижение #{idx} обновлено: _{text}_",
                       reply_markup=achievements_keyboard(), parse_mode='Markdown')
        user_states[user_id] = {}
    
    @bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'ach_deleting')
    def ach_delete_handler(message):
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text in ("✅ Готово", "🗑 Удалить все", "◀️ Назад в достижения", "🏠 Главное меню"):
            user_states[user_id] = {}
            if text == "🏠 Главное меню":
                bot.send_message(user_id, "🏠 **Главное меню**", reply_markup=main_keyboard(), parse_mode='Markdown')
            else:
                count = count_achievements(user_id)
                bot.send_message(user_id, f"🏆 **Мои достижения** ({count} шт.)", reply_markup=achievements_keyboard(), parse_mode='Markdown')
            return
        
        try:
            local_idx = int(text.lstrip('#')) - 1
            items = get_user_achievements(user_id)
            if local_idx < 0 or local_idx >= len(items):
                bot.send_message(user_id, "❌ Неверный номер. Используй #1, #2 и т.д.",
                               reply_markup=achievement_fill_keyboard())
                return
            delete_achievement(items[local_idx][0])
            count = count_achievements(user_id)
            bot.send_message(user_id, f"✅ Удалено! Осталось **{count}** достижений.",
                           reply_markup=achievements_keyboard(), parse_mode='Markdown')
            user_states[user_id] = {}
        except ValueError:
            bot.send_message(user_id, "❌ Напиши номер достижения (например, 5 или #5).",
                           reply_markup=achievement_fill_keyboard())
    
    # ========== CATCH-ALL (логгирование неперехваченных сообщений) ==========
    @bot.message_handler(func=lambda m: True)
    def catch_all(message):
        user_id = message.from_user.id
        text = message.text or "<не текст>"
        print(f"[CATCH-ALL] user={user_id}, text={text[:80]}, state={user_states.get(user_id, {}).get('state')}")
        st = user_states.get(user_id, {}).get('state')
        if st == 'filling':
            bot.send_message(user_id,
                "ℹ️ Вы в режиме заполнения записи. Используйте кнопки меню.\n"
                "Если хотите сохранить — нажмите ✅ **Завершить запись**",
                reply_markup=fill_keyboard(), parse_mode='Markdown')
        elif st == 'waiting_value':
            bot.send_message(user_id,
                "ℹ️ Я жду ваш ответ на предыдущий вопрос 😊\n"
                "Напишите текст или нажмите ◀️ **Отмена**",
                reply_markup=cancel_keyboard(), parse_mode='Markdown')
    
    # ── Назад (резервный — срабатывает если нет state) ──
    @bot.message_handler(func=lambda m: m.text == "◀️ Назад")
    def back_handler(message):
        user_id = message.from_user.id
        ctx = user_context.get(user_id, 'kpt')
        user_states[user_id] = {}
        
        if ctx == 'achievements':
            count = count_achievements(user_id)
            bot.send_message(user_id, f"🏆 **Мои достижения** ({count} шт.)\n\nВыберите действие:",
                           reply_markup=achievements_keyboard(), parse_mode='Markdown')
        elif ctx == 'plans':
            bot.send_message(user_id, "📋 **Планы на день**\n\nВыберите действие:",
                           reply_markup=plans_keyboard(), parse_mode='Markdown')
        else:
            bot.send_message(user_id, "📝 **КПТ Дневник**\n\nВыберите действие:",
                           reply_markup=cbt_keyboard(), parse_mode='Markdown')
    
    return bot

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    import signal
    import sys
    
    # При SIGTERM выходим с ошибкой, чтобы systemd Restart=always сработал
    def _handle_sigterm(signum, frame):
        print("⚠️ Получен SIGTERM, завершаюсь с ошибкой для autorestart...")
        sys.exit(1)
    
    signal.signal(signal.SIGTERM, _handle_sigterm)
    
    init_db()
    print("✅ База данных готова")
    
    import os
    BOT_TOKEN = os.getenv("CBT_BOT_TOKEN", "")
    if not BOT_TOKEN:
        print("\n⚠️  Нужен токен от @BotFather")
        print("Укажи в .env: CBT_BOT_TOKEN=...")
        BOT_TOKEN = input("Введи токен: ").strip()
        if not BOT_TOKEN:
            print("❌ Без токена не запустить")
            exit(1)
    
    print("🔄 Запуск бота...")
    bot = create_bot(BOT_TOKEN)
    print("✅ Бот запущен! Жду сообщения...")
    bot.infinity_polling(skip_pending=False)
