import os
from dotenv import load_dotenv
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton


# Загружаем переменные из .env
load_dotenv()


API_TOKEN = os.getenv('API_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')

bot = telebot.TeleBot(API_TOKEN)

# Словарь для хранения предпочтений языка пользователя
user_language = {}

# Тексты для разных языков
TEXTS = {
    'ru': {
        'welcome': 'Добро пожаловать! Пожалуйста, выберите язык:',
        'main_menu_welcome': 'Добро пожаловать в магазин премиум-реплик!',
        'open_shop': '🛍 Открыть магазин',
        'news': '📰 Новости',
        'reviews': '⭐ Отзывы',
        'language_selected': 'Вы выбрали русский язык.',
        'order_received': '✅ Получен заказ:',
    },
    'en': {
        'welcome': 'Welcome! Please select your language:',
        'main_menu_welcome': 'Welcome to the premium replica store!',
        'open_shop': '🛍 Open Shop',
        'news': '📰 News',
        'reviews': '⭐ Reviews',
        'language_selected': 'You have selected English.',
        'order_received': '✅ Order received:',
    }
}

# URL для новостей и отзывов (заглушки)
NEWS_URL = 'https://example.com/news'  # Замените на вашу ссылку
REVIEWS_URL = 'https://example.com/reviews' # Замените на вашу ссылку

def get_main_menu_markup(lang):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(TEXTS[lang]['open_shop'], web_app=WebAppInfo(url=WEBAPP_URL)))
    markup.add(InlineKeyboardButton(TEXTS[lang]['news'], url=NEWS_URL))
    markup.add(InlineKeyboardButton(TEXTS[lang]['reviews'], url=REVIEWS_URL))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Русский', callback_data='lang_ru'))
    markup.add(InlineKeyboardButton('English', callback_data='lang_en'))
    # Здесь будет отправка приветственной картинки, пока просто текст
    bot.send_photo(message.chat.id, photo="https://raw.githubusercontent.com/SLOU65/premium-mini-shop/refs/heads/main/image1.jpg", caption=TEXTS["ru"]["welcome"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def callback_inline(call):
    lang = call.data.split('_')[1]
    user_language[call.message.chat.id] = lang
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXTS[lang]["language_selected"])
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, TEXTS[lang]["main_menu_welcome"], reply_markup=get_main_menu_markup(lang))

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    data = message.web_app_data.data
    lang = user_language.get(message.chat.id, 'ru') # По умолчанию русский, если язык не выбран
    bot.send_message(message.chat.id, f"{TEXTS[lang]['order_received']}\n{data}")


if __name__ == "__main__":
    bot.infinity_polling()
