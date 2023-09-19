import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import bot_api

BOT_API_KEY = '6569744404:AAEGTiIWt0L2486WsISA1j6WSoSJJP83k0o'

bot = AsyncTeleBot(BOT_API_KEY)


async def get_photo(id):
    media = []
    req = bot_api.get_lot_photos(id)
    if req is not None:
        for i in req:
            media.append(telebot.types.InputMediaPhoto(open(i, 'rb')))
    else:
        print('No photo')
    print(media)
    return media


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

        keyboard = InlineKeyboardMarkup()

        for item in req:
            id = item.get("id")
            category_name = item.get("name")
            button = InlineKeyboardButton(text=category_name, callback_data=f'category_{id}')
            keyboard.add(button)

            responce += f'{item.get("name")}\n'

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
        media = await get_photo(id)
        req = bot_api.get_lot(id)
        print(req)

        message = f"{req.get('name')}\nОписание: {req.get('description')}\nЦена: {req.get('sale_price')} {req.get('currency')}"

        keyboard = InlineKeyboardMarkup()
        button_buy = InlineKeyboardButton(text='Купить', callback_data=f"buy_{id}")
        keyboard.add(button_buy)

        if len(media) > 0:
            await bot.send_message(call.message.chat.id, text='Загружаю фото... Подождите')
            await bot.send_media_group(call.message.chat.id, media)
        await bot.send_message(call.message.chat.id, text=message, reply_markup=keyboard)

    if call.data.startswith('category_'):
        responce = ''
        id = call.data.split('_')[1]
        req = bot_api.get_lots_by_category(id)

        keyboard = InlineKeyboardMarkup()

        for item in req:
            lot_id = item.get("id")
            button_text = item.get("name")
            button = InlineKeyboardButton(text=button_text, callback_data=f'lot_{lot_id}')
            keyboard.add(button)

            responce += f'{lot_id}. {item.get("name")}: {item.get("sale_price")} {item.get("currency")}\n'
        await bot.send_message(call.message.chat.id, text=responce, reply_markup=keyboard)

    if call.data.startswith('buy_'):
        responce = ''
        id = call.data.split('_')[1]
        req = bot_api.get_lot_buy(id)

asyncio.run(bot.polling(none_stop=True, interval=0))
