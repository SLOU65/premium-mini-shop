import os
from dotenv import load_dotenv
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# Загружаем переменные окружения
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')  # Ссылка на ваш HTML-магазин

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения языка пользователя
user_lang = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Кнопки выбора языка
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(
        message.chat.id,
        "Выберите язык / Choose a language:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def language_selected(call):
    bot.answer_callback_query(call.id)  # ОТВЕЧАЕМ на callback, иначе кнопка зависнет

    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang

    # Настройка текста и кнопок по языку
    if lang == "ru":
        welcome_text = "Добро пожаловать в магазин премиум-реплик!"
        open_shop = "🛍 Открыть магазин"
        reviews = "Отзывы"
        news = "Новости"
    else:
        welcome_text = "Welcome to the premium replicas store!"
        open_shop = "🛍 Open Store"
        reviews = "Reviews"
        news = "News"

    # Основные кнопки
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(open_shop, web_app=WebAppInfo(url=WEBAPP_URL)))
    markup.add(
        InlineKeyboardButton(reviews, url="https://t.me/your_reviews_channel"),  # ← сюда вставь ссылку на отзывы
        InlineKeyboardButton(news, url="https://t.me/your_news_channel")         # ← сюда вставь ссылку на новости
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=welcome_text,
        reply_markup=markup
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    data = message.web_app_data.data
    bot.send_message(message.chat.id, f"✅ Получен заказ:\n{data}")

if __name__ == "__main__":
    print("🤖 Бот запущен...")
    bot.infinity_polling()
