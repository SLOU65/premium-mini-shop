import os
from dotenv import load_dotenv
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# Загружаем переменные из .env
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')

bot = telebot.TeleBot(API_TOKEN)

# Ссылки на каналы (замени на свои)
CHANNELS = {
    'news_ru': 'https://t.me/your_news_channel_ru',
    'news_en': 'https://t.me/your_news_channel_en',
    'reviews_ru': 'https://t.me/your_reviews_channel_ru',
    'reviews_en': 'https://t.me/your_reviews_channel_en'
}

# Словарь для хранения выбранного языка пользователей
user_languages = {}

# Тексты для разных языков
TEXTS = {
    'ru': {
        'welcome': 'Добро пожаловать в магазин премиум‑реплик!',
        'choose_language': 'Выберите язык / Choose language:',
        'shop_button': '🛍 Открыть магазин',
        'news_button': '📰 Новости',
        'reviews_button': '⭐ Отзывы',
        'back_button': '🔙 Назад',
        'language_set': 'Язык установлен: Русский'
    },
    'en': {
        'welcome': 'Welcome to the premium replica store!',
        'choose_language': 'Choose language / Выберите язык:',
        'shop_button': '🛍 Open Store',
        'news_button': '📰 News',
        'reviews_button': '⭐ Reviews',
        'back_button': '🔙 Back',
        'language_set': 'Language set: English'
    }
}

def get_language_keyboard():
    """Создает клавиатуру для выбора языка"""
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🇷🇺 RU", callback_data="lang_ru"),
        InlineKeyboardButton("🇺🇸 EN", callback_data="lang_en")
    )
    return markup

def get_main_menu_keyboard(lang):
    """Создает главное меню в зависимости от языка"""
    markup = InlineKeyboardMarkup()
    texts = TEXTS[lang]
    
    markup.add(InlineKeyboardButton(texts['shop_button'], web_app=WebAppInfo(url=WEBAPP_URL)))
    markup.row(
        InlineKeyboardButton(texts['news_button'], url=CHANNELS[f'news_{lang}']),
        InlineKeyboardButton(texts['reviews_button'], url=CHANNELS[f'reviews_{lang}'])
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    # Отправляем приветственную картинку (замени на свою картинку)
    welcome_photo = "https://raw.githubusercontent.com/SLOU65/premium-mini-shop/refs/heads/main/image1.jpg"
    
    try:
        bot.send_photo(
            message.chat.id, 
            welcome_photo,
            caption=TEXTS['ru']['choose_language'],
            reply_markup=get_language_keyboard()
        )
    except:
        # Если картинка не загружается, отправляем просто текст
        bot.send_message(
            message.chat.id,
            TEXTS['ru']['choose_language'],
            reply_markup=get_language_keyboard()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    """Обработка выбора языка"""
    user_id = call.from_user.id
    lang = call.data.split('_')[1]  # ru или en
    
    # Сохраняем выбранный язык
    user_languages[user_id] = lang
    texts = TEXTS[lang]
    
    # Подтверждаем выбор языка
    bot.answer_callback_query(call.id, texts['language_set'])
    
    # Отправляем главное меню
    show_main_menu(call.message, lang)

def show_main_menu(message, lang):
    """Показывает главное меню"""
    texts = TEXTS[lang]
    
    # Картинка для главного меню (замени на свою)
    menu_photo = "https://raw.githubusercontent.com/SLOU65/premium-mini-shop/refs/heads/main/image1.jpg"
    
    try:
        bot.send_photo(
            message.chat.id,
            menu_photo,
            caption=texts['welcome'],
            reply_markup=get_main_menu_keyboard(lang)
        )
    except:
        # Если картинка не загружается, отправляем просто текст
        bot.send_message(
            message.chat.id,
            texts['welcome'],
            reply_markup=get_main_menu_keyboard(lang)
        )

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    data = message.web_app_data.data
    bot.send_message(message.chat.id, f"✅ Получен заказ:\n{data}")

if __name__ == "__main__":
    bot.infinity_polling()
