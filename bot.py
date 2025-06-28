# bot.py
import telebot
from telebot.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = 'ТВОЙ_ТОКЕН_ОТ_BOTFATHER'
WEBAPP_URL = 'https://ТВОЙ_САЙТ.github.io/shop/'  # или Vercel/Netlify

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        text="🛍 Открыть магазин",
        web_app=WebAppInfo(url=WEBAPP_URL)
    ))
    bot.send_message(message.chat.id, "Добро пожаловать в магазин премиум-реплик!", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message: telebot.types.Message):
    try:
        data = message.web_app_data.data
        bot.send_message(message.chat.id, f"✅ Заказ получен:\n{data}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

bot.infinity_polling()
