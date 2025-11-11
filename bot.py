import os
import uuid
import json
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')
WELCOME_IMAGE_URL = os.getenv('WELCOME_IMAGE_URL', 'https://i.imgur.com/wb0i3l7.png')
SECTION_IMAGES = {
    "socials": "https://i.imgur.com/your_socials_image.png",
    "reviews": "https://i.imgur.com/your_reviews_image.png",
    "faq": "https://i.imgur.com/your_faq_image.png",
    "support": "https://i.imgur.com/your_support_image.png",
    "profile": "https://i.imgur.com/your_profile_image.png"
}

ADMIN_ID = int(os.getenv('ADMIN_ID', '5008534281'))  # замените на свой Telegram ID или через .env

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
bot.remove_webhook()

# Хранилища в памяти
user_language = {}
user_purchases = {}
user_orders = {}
last_bot_message = {}
known_users = set()
broadcast_target = {}

# Полные заказы по order_id
orders_store = {}  # order_id -> full order object

def generate_order_id():
    return str(uuid.uuid4())[:8]

def send_and_replace(chat_id, user_id, send_func):
    if user_id in last_bot_message:
        try:
            bot.delete_message(chat_id, last_bot_message[user_id])
        except Exception:
            pass
    msg = send_func()
    if msg:
        last_bot_message[user_id] = msg.message_id

def show_main_menu(chat_id, lang):
    markup = InlineKeyboardMarkup()
    if lang == "ru":
        caption = "*🏬 Добро пожаловать!*"
        markup.add(InlineKeyboardButton("🛍 Открытие магазина", web_app=WebAppInfo(url=WEBAPP_URL)))
        markup.add(
            InlineKeyboardButton("⭐ Отзывы", callback_data="reviews"),
            InlineKeyboardButton("❓ F.A.Q", callback_data="faq")
        )
        markup.add(
            InlineKeyboardButton("🛠 Поддержка", callback_data="support"),
            InlineKeyboardButton("👤 Профиль", callback_data="profile")
        )
        markup.add(
            InlineKeyboardButton("📱 Социальные сети", callback_data="socials"),
            InlineKeyboardButton("🌐 Смена языка", callback_data="change_lang")
        )
    else:
        caption = "*🏬 Welcome!*"
        markup.add(InlineKeyboardButton("🛍 Open Store", web_app=WebAppInfo(url=WEBAPP_URL)))
        markup.add(
            InlineKeyboardButton("⭐ Reviews", callback_data="reviews"),
            InlineKeyboardButton("❓ F.A.Q", callback_data="faq")
        )
        markup.add(
            InlineKeyboardButton("🛠 Support", callback_data="support"),
            InlineKeyboardButton("👤 Profile", callback_data="profile")
        )
        markup.add(
            InlineKeyboardButton("📱 Social Media", callback_data="socials"),
            InlineKeyboardButton("🌐 Change Language", callback_data="change_lang")
        )

    if chat_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("🛠 Админ-панель", callback_data="admin_panel"))

    send_and_replace(chat_id, chat_id, lambda: bot.send_photo(chat_id, WELCOME_IMAGE_URL, caption=caption, reply_markup=markup))

@bot.message_handler(commands=['start'])
def start(message):
    known_users.add(message.from_user.id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(
        message.chat.id,
        "*👋 Привет! Выберите язык / Please choose your language:*",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    lang = call.data.split("_")[1]
    user_language[call.from_user.id] = lang
    bot.answer_callback_query(call.id, text="✅ Язык выбран")
    show_main_menu(call.message.chat.id, lang)

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    user_id = message.from_user.id
    lang = user_language.get(user_id, "ru")

    # Проверка наличия данных
    if not getattr(message, "web_app_data", None) or not getattr(message.web_app_data, "data", None):
        bot.send_message(message.chat.id, "⚠️ Не удалось получить данные заказа. Попробуйте снова.")
        return

    # Парсинг JSON
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        bot.send_message(message.chat.id, "⚠️ Неверный формат данных заказа.")
        return

    # Нормализация полей
    items = data.get("items", []) or []
    total = data.get("total") if data.get("total") is not None else data.get("sum") or 0
    order_id = data.get("order_id") or data.get("orderId") or generate_order_id()
    date = data.get("date") or "—"
    time = data.get("time") or "—"
    language = data.get("language") or lang
    customer_name = data.get("fullname") or data.get("name") or data.get("fullName") or "—"
    address = data.get("address") or "—"
    phone = data.get("phone") or "—"
    email = data.get("email") or "—"

    # Нормализация items: поддерживаем разные ключи
    normalized_items = []
    for it in items:
        name = it.get("name") or it.get("item") or "Untitled"
        price = it.get("price") or it.get("item_price") or 0
        qty = it.get("quantity") or it.get("qty") or 1
        try:
            price = float(price)
        except Exception:
            price = 0.0
        try:
            qty = int(qty)
        except Exception:
            qty = 1
        normalized_items.append({"name": name, "price": price, "quantity": qty})

    # Вычисление total, если не предоставлен
    if not total:
        total = sum(i["price"] * i["quantity"] for i in normalized_items)

    # Сохранение полного заказа
    order_obj = {
        "order_id": order_id,
        "user_id": user_id,
        "fullname": customer_name,
        "address": address,
        "phone": phone,
        "email": email,
        "items": normalized_items,
        "total": float(total),
        "date": date,
        "time": time,
        "language": language,
        "paid": False
    }
    orders_store[order_id] = order_obj

    # Обновление статистики пользователя
    user_orders.setdefault(user_id, []).append(order_id)
    user_purchases[user_id] = user_purchases.get(user_id, 0) + 1

    # Формирование текста для пользователя
    if normalized_items:
        item_lines = "\n".join([f"• {i['name']} x{i['quantity']} — €{i['price']:.2f}" for i in normalized_items])
    else:
        item_lines = "—"

    if language == "ru":
        user_text = (
            f"*✅ Заказ успешно оформлен!*\n"
            f"🧾 *Номер заказа:* `{order_id}`\n"
            f"📅 *Дата:* {date}, {time}\n"
            f"📦 *Товары:*\n{item_lines}\n"
            f"💰 *Сумма:* *€{order_obj['total']:.2f}*\n"
            f"🛒 *Всего покупок:* *{user_purchases[user_id]}*\n\n"
            f"📬 Свяжитесь с менеджером и укажите номер заказа."
        )
    else:
        user_text = (
            f"*✅ Order placed successfully!*\n"
            f"🧾 *Order ID:* `{order_id}`\n"
            f"📅 *Date:* {date}, {time}\n"
            f"📦 *Items:*\n{item_lines}\n"
            f"💰 *Total:* *€{order_obj['total']:.2f}*\n"
            f"🛒 *Total purchases:* *{user_purchases[user_id]}*\n\n"
            f"📬 Contact our manager with your order ID."
        )

    # Отправка подтверждения пользователю
    try:
        bot.send_message(message.chat.id, user_text, parse_mode="Markdown")
    except Exception:
        fallback = f"Order {order_id} placed. Total: €{order_obj['total']:.2f}"
        bot.send_message(message.chat.id, fallback)

    # Уведомление админу
    try:
        admin_text = (
            f"🆕 *Новый заказ* #{order_id}\n"
            f"Пользователь: `{message.from_user.id}`\n"
            f"Сумма: €{order_obj['total']:.2f}\n"
            f"Товары:\n{item_lines}\n"
            f"Контакты: {customer_name} | {phone} | {email}\n"
            f"Адрес: {address}"
        )
        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    except Exception:
        pass

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text and m.from_user.id in broadcast_target)
def handle_broadcast_text(message):
    lang = broadcast_target.pop(message.from_user.id)
    count = 0
    for uid in known_users:
        if user_language.get(uid) == lang:
            try:
                bot.send_message(uid, message.text)
                count += 1
            except Exception:
                continue
    bot.send_message(message.chat.id, f"✅ Сообщение отправлено {count} пользователям с языком {lang.upper()}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    bot.answer_callback_query(call.id)
    lang = user_language.get(call.from_user.id, "ru")

    def back_btn():
        return InlineKeyboardButton("🔙 Назад" if lang == "ru" else "🔙 Back", callback_data="main")

    def send_section(photo_url, text, markup):
        send_and_replace(call.message.chat.id, call.from_user.id, lambda: bot.send_photo(call.message.chat.id, photo=photo_url, caption=text, reply_markup=markup))

    if call.data == "main":
        show_main_menu(call.message.chat.id, lang)

    elif call.data == "admin_panel":
        if call.from_user.id != ADMIN_ID:
            bot.send_message(call.message.chat.id, "⛔ Нет доступа")
            return

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📢 Рассылка RU", callback_data="broadcast_ru"),
            InlineKeyboardButton("📢 Рассылка EN", callback_data="broadcast_en"),
            InlineKeyboardButton("📋 Статистика", callback_data="stats"),
            back_btn()
        )
        text = "*🛠 Админ-панель:*" if lang == "ru" else "*🛠 Admin Panel:*"
        send_section(SECTION_IMAGES["support"], text, markup)

    elif call.data in ["broadcast_ru", "broadcast_en"]:
        if call.from_user.id != ADMIN_ID:
            bot.send_message(call.message.chat.id, "⛔ Нет доступа")
            return

        target_lang = "ru" if call.data == "broadcast_ru" else "en"
        broadcast_target[call.from_user.id] = target_lang
        bot.send_message(call.message.chat.id, f"✍️ Введите сообщение для рассылки ({target_lang.upper()}):")

    elif call.data == "stats":
        ru_count = sum(1 for uid in known_users if user_language.get(uid) == "ru")
        en_count = sum(1 for uid in known_users if user_language.get(uid) == "en")
        total = sum(1 for uid in known_users)
        text = (
            f"*📊 Статистика:*\n"
            f"👥 Всего пользователей: *{total}*\n"
            f"🇷🇺 Русских: *{ru_count}*\n"
            f"🇬🇧 Английских: *{en_count}*"
            if lang == "ru" else
            f"*📊 Stats:*\n"
            f"👥 Total users: *{total}*\n"
            f"🇷🇺 Russian: *{ru_count}*\n"
            f"🇬🇧 English: *{en_count}*"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

    elif call.data == "socials":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Telegram", url="https://t.me/your_channel"),
            InlineKeyboardButton("TikTok", url="https://tiktok.com/@your_profile"),
            InlineKeyboardButton("Instagram", url="https://instagram.com/your_profile"),
            back_btn()
        )
        text = "*📱 Социальные сети:*" if lang == "ru" else "*📱 Social Media:*"
        send_section(SECTION_IMAGES["socials"], text, markup)

    elif call.data == "reviews":
        markup = InlineKeyboardMarkup().add(back_btn())
        text = "*⭐ Оставьте отзыв:*" if lang == "ru" else "*⭐ Leave a review:*"
        send_section(SECTION_IMAGES["reviews"], text, markup)

    elif call.data == "faq":
        markup = InlineKeyboardMarkup().add(back_btn())
        text = (
            "*❓ Часто задаваемые вопросы:*\n*1.* Как оформить заказ?\n*2.* Как работает доставка?"
            if lang == "ru" else
            "*❓ Frequently Asked Questions:*\n*1.* How to place an order?\n*2.* How does delivery work?"
        )
        send_section(SECTION_IMAGES["faq"], text, markup)

    elif call.data == "support":
        markup = InlineKeyboardMarkup().add(back_btn())
        text = "*🛠 Напишите нам для поддержки.*" if lang == "ru" else "*🛠 Contact us for support.*"
        send_section(SECTION_IMAGES["support"], text, markup)

    elif call.data == "profile":
        markup = InlineKeyboardMarkup().add(back_btn())
        purchases = user_purchases.get(call.from_user.id, 0)
        orders = user_orders.get(call.from_user.id, [])
        order_list = "\n".join([f"🧾 *{oid}*" for oid in orders]) if orders else "—"
        text = (
            f"*👤 Личный кабинет:*\n"
            f"🙍‍♂️ *Пользователь:* @{call.from_user.username}\n"
            f"🔑 *ID:* `{call.from_user.id}`\n"
            f"🛒 *Количество покупок:* *{purchases}*\n"
            f"📦 *Заказы:*\n{order_list}"
            if lang == "ru" else
            f"*👤 Profile:*\n"
            f"🙍‍♂️ *User:* @{call.from_user.username}\n"
            f"🔑 *ID:* `{call.from_user.id}`\n"
            f"🛒 *Purchases:* *{purchases}*\n"
            f"📦 *Orders:*\n{order_list}"
        )
        send_section(SECTION_IMAGES["profile"], text, markup)

    elif call.data == "change_lang":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        )
        send_and_replace(
            call.message.chat.id,
            call.from_user.id,
            lambda: bot.send_message(
                call.message.chat.id,
                "*🌐 Выберите язык / Choose your language:*",
                reply_markup=markup
            )
        )

if __name__ == "__main__":
    print("🚀 Бот запущен... (Polling активен)")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=10)
