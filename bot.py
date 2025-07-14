import os
from dotenv import load_dotenv
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# --- Загрузка переменных ---
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

# --- Ссылки для кнопок (замените на свои или добавьте в .env) ---
WELCOME_IMAGE_URL = os.getenv("WELCOME_IMAGE_URL", "https://i.imgur.com/wb0i3l7.png") # Пример
NEWS_URL = os.getenv("NEWS_URL", "https://t.me/your_news_channel") # Ваша ссылка на новости
REVIEWS_URL = os.getenv("REVIEWS_URL", "https://t.me/your_reviews_channel") # Ваша ссылка на отзывы

# Проверка наличия токена
if not API_TOKEN:
    raise ValueError("Токен API не найден! Проверьте файл .env и переменную API_TOKEN.")

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения предпочтений языка пользователей
user_languages = {}

# Тексты для кнопок на разных языках
BUTTON_TEXTS = {
    'ru': {
        'shop': "🛍Открыть магазин",
        'news': "Новости",
        'reviews': "Отзывы",
        'language': "Язык: RU 🇷🇺",
        'welcome_caption': "Добро пожаловать в магазин премиум‑реплик!"
    },
    'en': {
        'shop': "🛍Open a store",
        'news': "News",
        'reviews': "Reviews",
        'language': "Language: EN 🇬🇧",
        'welcome_caption': "Welcome to the premium replica store!"
    }
}

# --- ОБНОВЛЕННЫЙ обработчик команды /start ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_languages[chat_id] = {"lang": "ru"}
    send_main_menu(chat_id)

# Функция для отправки главного меню (чтобы можно было вызывать после смены языка)
def send_main_menu(chat_id, message_id=None):
    lang = user_languages.get(chat_id, 'ru') # Получаем язык пользователя, по умолчанию RU
    texts = BUTTON_TEXTS[lang]

    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=1)
    
    # 1. Кнопка "Открыть магазин" (открывает Web App)
    shop_button = InlineKeyboardButton(
        texts['shop'],
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    
    # 2. Кнопки "Новости" и "Отзывы" (ссылки)
    links_row = [
        InlineKeyboardButton(texts['news'], url=NEWS_URL),
        InlineKeyboardButton(texts['reviews'], url=REVIEWS_URL)
    ]

    # 3. Кнопка смены языка
    language_button = InlineKeyboardButton(
        texts['language'],
        callback_data='change_language'
    )
    
    # Добавляем кнопки на клавиатуру
    markup.add(shop_button) # Кнопка магазина на всю ширину
    markup.add(*links_row)   # Кнопки новостей и отзывов рядом
    markup.add(language_button) # Кнопка смены языка
    
    # Отправляем приветственную картинку с текстом и готовым меню
    # Если сообщение уже существует (например, при смене языка), редактируем его
    # В данном случае, для простоты, всегда отправляем новое сообщение.
    # В реальном проекте лучше использовать edit_message_reply_markup и edit_message_caption
    sent_message = bot.send_photo(
        chat_id,
        photo=WELCOME_IMAGE_URL,
        caption=texts["welcome_caption"],
        reply_markup=markup
    )
    user_languages[chat_id] = {"lang": "ru", "message_id": sent_message.message_id}


# --- Обработчик для Web App (остается без изменений) ---
@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    data = message.web_app_data.data
    bot.send_message(message.chat.id, f"✅ Получен заказ:\n{data}")

# --- Обработчик для callback-запросов (для кнопки смены языка) ---
@bot.callback_query_handler(func=lambda call: call.data == 'change_language')
def callback_change_language(call):
    chat_id = call.message.chat.id
    current_lang_data = user_languages.get(chat_id, {"lang": "ru", "message_id": None})
    current_lang = current_lang_data["lang"]
    message_id = current_lang_data["message_id"]

    new_lang = 'en' if current_lang == 'ru' else 'ru'
    user_languages[chat_id]["lang"] = new_lang
    
    if message_id:
        send_main_menu(chat_id, message_id=message_id)
    else:
        send_main_menu(chat_id)
    
    bot.answer_callback_query(call.id)
# --- Ваш запуск бота (остается без изменений) ---
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
