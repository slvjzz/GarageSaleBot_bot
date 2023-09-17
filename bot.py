import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import bot_api

BOT_API_KEY = '6569744404:AAEGTiIWt0L2486WsISA1j6WSoSJJP83k0o'

bot = telebot.TeleBot(BOT_API_KEY)


@bot.message_handler(commands=['start'])
def bot_home(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = InlineKeyboardButton(text='/Лоты',)
    markup.add(btn1)

    resp = f"""Привет. Это бот гаражной распродажи. """

    bot.send_message(message.chat.id,
                     text=resp, reply_markup=markup)


@bot.message_handler(commands=['Лоты'])
def lots(message):
    responce = ''
    req = bot_api.get_home()

    keyboard = ReplyKeyboardMarkup()

    for key in req.keys():
        button = KeyboardButton(text=req.get(key).get("name"))
        keyboard.add(button)

        responce += f'{req.get(key).get("name")}: {req.get(key).get("sale_price")} {req.get(key).get("currency")}\n'

    bot.send_message(message.chat.id,
                     text=responce, reply_markup=keyboard)


bot.polling(none_stop=True, interval=0)
