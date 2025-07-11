import os
from dotenv import load_dotenv
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# Загружаем переменные из .env
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')

print(f"API_TOKEN: {'Есть' if API_TOKEN else 'НЕТ'}")
print(f"WEBAPP_URL: {WEBAPP_URL}")

bot = telebot.TeleBot(API_TOKEN)

# Ссылки на каналы (замени на свои)
CHANNELS = {
    'news_ru': 'https://t.me/durov',
    'news_en': 'https://t.me/durov',
    'reviews_ru': 'https://t.me/telegram',
    'reviews_en': 'https://t.me/telegram'
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
    print("Создана клавиатура выбора языка")
    return markup

def get_main_menu_keyboard(lang):
    """Создает главное меню в зависимости от языка"""
    markup = InlineKeyboardMarkup()
    texts = TEXTS[lang]
    
    # Проверяем WEBAPP_URL
    if WEBAPP_URL:
        markup.add(InlineKeyboardButton(texts['shop_button'], web_app=WebAppInfo(url=WEBAPP_URL)))
    else:
        markup.add(InlineKeyboardButton(texts['shop_button'], callback_data="no_webapp"))
    
    markup.row(
        InlineKeyboardButton(texts['news_button'], url=CHANNELS[f'news_{lang}']),
        InlineKeyboardButton(texts['reviews_button'], url=CHANNELS[f'reviews_{lang}'])
    )
    print(f"Создана главная клавиатура для языка: {lang}")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    print(f"Получена команда /start от пользователя {message.from_user.id}")
    try:
        bot.send_message(
            message.chat.id,
            TEXTS['ru']['choose_language'],
            reply_markup=get_language_keyboard()
        )
        print("Сообщение с выбором языка отправлено")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    """Обработка всех callback'ов"""
    print(f"Получен callback: {call.data} от пользователя {call.from_user.id}")
    
    if call.data.startswith('lang_'):
        handle_language_selection(call)
    elif call.data == "no_webapp":
        bot.answer_callback_query(call.id, "WEBAPP_URL не настроен!")
    else:
        bot.answer_callback_query(call.id, f"Неизвестная команда: {call.data}")

def handle_language_selection(call):
    """Обработка выбора языка"""
    user_id = call.from_user.id
    lang = call.data.split('_')[1]  # ru или en
    
    print(f"Пользователь {user_id} выбрал язык: {lang}")
    
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
    
    print(f"Отправляем главное меню на языке: {lang}")
    
    try:
        bot.send_message(
            message.chat.id,
            texts['welcome'],
            reply_markup=get_main_menu_keyboard(lang)
        )
        print("Главное меню отправлено")
    except Exception as e:
        print(f"Ошибка при отправке главного меню: {e}")

@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    print(f"Получены данные из веб-приложения: {message.web_app_data.data}")
    data = message.web_app_data.data
    bot.send_message(message.chat.id, f"✅ Получен заказ:\n{data}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработка всех остальных сообщений"""
    print(f"Получено сообщение: {message.text} от пользователя {message.from_user.id}")
    bot.send_message(message.chat.id, "Используйте команду /start для начала работы")

if __name__ == "__main__":
    print("Бот запущен...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
