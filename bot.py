import os
from dotenv import load_dotenv
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

# --- Загрузка переменных ---
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')

# --- Ссылки для кнопок (замените на свои или добавьте в .env) ---
WELCOME_IMAGE_URL = os.getenv('WELCOME_IMAGE_URL', 'https://i.imgur.com/wb0i3l7.png' ) # Пример
NEWS_URL = os.getenv('NEWS_URL', 'https://t.me/your_news_channel' ) # Ваша ссылка на новости
REVIEWS_URL = os.getenv('REVIEWS_URL', 'https://t.me/your_reviews_channel' ) # Ваша ссылка на отзывы

# Проверка наличия токена
if not API_TOKEN:
    raise ValueError("Токен API не найден! Проверьте файл .env и переменную API_TOKEN.")

bot = telebot.TeleBot(API_TOKEN)

# --- ОБНОВЛЕННЫЙ обработчик команды /start ---
# Теперь он сразу отправляет приветственную картинку и главное меню.
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем клавиатуру
    markup = InlineKeyboardMarkup(row_width=1)
    
    # 1. Кнопка "Открыть магазин" (открывает Web App)
    shop_button = InlineKeyboardButton(
        "🛍Открыть магазин/Open a store",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    
    # 2. Кнопки "Новости" и "Отзывы" (ссылки)
    # Они будут в одном ряду для компактности
    links_row = [
        InlineKeyboardButton("Новости/News", url=NEWS_URL),
        InlineKeyboardButton("Отзывы/Reviews", url=REVIEWS_URL)
    ]
    
    # Добавляем кнопки на клавиатуру
    markup.add(shop_button) # Кнопка магазина на всю ширину
    markup.add(*links_row)   # Кнопки новостей и отзывов рядом
    
    # Отправляем приветственную картинку с текстом и готовым меню
    bot.send_photo(
        message.chat.id,
        photo=WELCOME_IMAGE_URL,
        caption="Добро пожаловать в магазин премиум‑реплик!",
        reply_markup=markup
    )

# --- Ваш обработчик для Web App (остается без изменений) ---
@bot.message_handler(content_types=['web_app_data'])
def handle_order(message):
    data = message.web_app_data.data
    bot.send_message(message.chat.id, f"✅ Получен заказ:\n{data}")

# --- Ваш запуск бота (остается без изменений) ---
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()

