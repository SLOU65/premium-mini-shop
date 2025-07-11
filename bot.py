import os
from dotenv import load_dotenv
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton


# Загружаем переменные из .env
load_dotenv()


API_TOKEN = os.getenv("API_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
WELCOME_IMAGE_URL = os.getenv("WELCOME_IMAGE_URL") # Новая переменная для URL изображения


bot = telebot.TeleBot(API_TOKEN)


# Словарь для хранения выбранного языка пользователя
user_languages = {}

# Словари для переводов
translations = {
    'ru': {
        'welcome_message': 'Добро пожаловать! Пожалуйста, выберите язык:',
        'shop_button': '🛍 Открыть магазин',
        'news_button': '📰 Новости',
        'reviews_button': '⭐ Отзывы',
        'main_menu_message': 'Добро пожаловать в магазин премиум-реплик!',
        'order_received': '✅ Получен заказ:\n{}'
    },
    'en': {
        'welcome_message': 'Welcome! Please choose your language:',
        'shop_button': '🛍 Open Shop',
        'news_button': '📰 News',
        'reviews_button': '⭐ Reviews',
        'main_menu_message': 'Welcome to the premium replica store!',
        'order_received': '✅ Order received:\n{}'
    }
}

def get_text(user_id, key):
    lang = user_languages.get(user_id, 'ru') # По умолчанию русский
    return translations[lang].get(key, 'Текст не найден')

def send_main_menu(message, lang):
    user_languages[message.chat.id] = lang
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(get_text(message.chat.id, 'shop_button'), web_app=WebAppInfo(url=WEBAPP_URL)))
    markup.add(InlineKeyboardButton(get_text(message.chat.id, 'news_button'), callback_data='news'))
    markup.add(InlineKeyboardButton(get_text(message.chat.id, 'reviews_button'), callback_data='reviews'))
    
    # Изменяем существующее сообщение вместо отправки нового
    bot.edit_message_caption(chat_id=message.chat.id, message_id=message.message_id, caption=get_text(message.chat.id, 'main_menu_message'))
    bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🇷🇺 RU', callback_data='lang_ru'))
    markup.add(InlineKeyboardButton('🇬🇧 EN', callback_data='lang_en'))
    
    bot.send_photo(message.chat.id, WELCOME_IMAGE_URL, caption=get_text(message.chat.id, 'welcome_message'), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def choose_language(call):
    lang = call.data.split('_')[1]
    # Вместо удаления и отправки нового сообщения, редактируем существующее
    send_main_menu(call.message, lang)

@bot.callback_query_handler(func=lambda call: call.data == 'news')
def show_news(call):
    bot.answer_callback_query(call.id, text=get_text(call.message.chat.id, 'news_button'))
    bot.send_message(call.message.chat.id, 'Здесь будут новости (на выбранном языке).') # TODO: Добавить реальные новости

@bot.callback_query_handler(func=lambda call: call.data == 'reviews')
def show_reviews(call):
    bot.answer_callback_query(call.id, text=get_text(call.message.chat.id, 'reviews_button'))
    bot.send_message(call.message.chat.id, 'Здесь будут отзывы (на выбранном языке).') # TODO: Добавить реальные отзывы

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    data = message.web_app_data.data
    bot.send_message(message.chat.id, get_text(message.chat.id, 'order_received').format(data))


if __name__ == '__main__':
    if not WELCOME_IMAGE_URL:
        print("Error: WELCOME_IMAGE_URL not set in .env. Please provide a URL for the welcome image.")
        exit()
    bot.infinity_polling()


