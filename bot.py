import telebot
import bot_api

BOT_API_KEY = '6569744404:AAEGTiIWt0L2486WsISA1j6WSoSJJP83k0o'

bot = telebot.TeleBot(BOT_API_KEY)


@bot.message_handler(commands=['start'])
def bot_home(message):
    responce = ''
    req = bot_api.get_home()
    for key in req.keys():
        responce += f'{key}:     {req.get(key)}\n'

    bot.send_message(message.chat.id,
                     text=responce)


bot.polling(none_stop=True, interval=0)
