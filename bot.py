import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import bot_api

BOT_API_KEY = '6569744404:AAEGTiIWt0L2486WsISA1j6WSoSJJP83k0o'

bot = AsyncTeleBot(BOT_API_KEY)


@bot.message_handler(commands=['start'])
async def bot_home(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    lots_button = InlineKeyboardButton(text='Лоты', )
    categories = InlineKeyboardButton(text='Категории', )
    markup.add(lots_button)
    markup.add(categories)

    resp = f"""Привет. Это бот гаражной распродажи. """

    await bot.send_message(message.chat.id,
                           text=resp, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
async def handle_callback_query(message):
    if message.text == 'Лоты':
        responce = ''
        req = bot_api.get_lots()

        keyboard = InlineKeyboardMarkup()

        for item in req:
            lot_id = item.get("id")
            button_text = item.get("name")
            button = InlineKeyboardButton(text=button_text, callback_data=f'lot_{lot_id}')
            keyboard.add(button)

            responce += f'{lot_id}. {item.get("name")}: {item.get("sale_price")} {item.get("currency")}\n'
        await bot.send_message(message.chat.id, text=responce, reply_markup=keyboard)

    elif message.text == 'Категории':
        responce = ''
        req = bot_api.get_categories()

        keyboard = ReplyKeyboardMarkup()

        for item in req:
            button = KeyboardButton(text=item.get("name"))
            keyboard.add(button)

            responce += f'{item.get("name")}: {item.get("sale_price")} {item.get("currency")}\n'

        menu = InlineKeyboardButton(text='Меню', )
        keyboard.add(menu)
        await bot.send_message(message.chat.id, text=responce, reply_markup=keyboard)

    elif message.text == 'Меню':

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        lots_button = InlineKeyboardButton(text='Лоты', )
        categories = InlineKeyboardButton(text='Категории', )
        markup.add(lots_button)
        markup.add(categories)

        await bot.send_message(message.chat.id, text='Главное меню', reply_markup=markup)

    elif message.text.startswith('Лот_'):
        id = message.text.split('_')[1].split(':')[0]
        req = bot_api.get_lot(id)
        print(req)


@bot.callback_query_handler(func=lambda call: True)
async def handle_callback_query(call):
    print('CALLL!!!!!')
    print(call)
    if call.data.startswith('lot_'):
        id = call.data.split('_')[1]
        req = bot_api.get_lot(id)
        message = f"{req.get('name')}\nОписание:{req.get('description')}\nЦена: {req.get('sale_price')} {req.get('currency')}"
        await bot.send_message(call.message.chat.id, text=message)
    #    lot_id = int(call.data.split('_')[1])
    #     response = requests.get(f'http://your_flask_server/bot/lots/{lot_id}')
    #     if response.status_code == 200:
    #         lot_data = response.json()
    #         # Обработайте данные лота, например, отправьте их обратно пользователю в чате бота.
    # elif call.data == 'menu':
    #     # Обработка нажатия на кнопку "Меню"
    #     # Добавьте ваш код для обработки этой кнопки
    #     pass

asyncio.run(bot.polling(none_stop=True, interval=0))
