import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import bot_api
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

BOT_API_KEY = config['credentials']['BOT_API_KEY']

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
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lots_button = InlineKeyboardButton(text='Лоты', )
    categories = InlineKeyboardButton(text='Категории', )
    about = InlineKeyboardButton(text='О боте', )
    markup.add(lots_button, categories)
    markup.add(about)

    resp = f"""Привет. Это бот гаражной распродажи. """

    await bot.send_message(message.chat.id,
                           text=resp, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
async def handle_callback_query(message):
    if message.text == 'Лоты':
        responce = ''
        req = bot_api.get_lots()
        if len(req) == 0:
            await bot.send_message(message.chat.id, text="К сожалению, все раскупили")

        keyboard = InlineKeyboardMarkup(row_width=3)

        row_buttons = []
        for item in req:
            lot_id = item.get("id")
            button_text = item.get("name")
            button = InlineKeyboardButton(text=button_text, callback_data=f'lot_{lot_id}')
            row_buttons.append(button)

            if len(row_buttons) == 3:
                keyboard.add(*row_buttons)
                row_buttons = []

            responce += f'{lot_id}. {item.get("name")}: {item.get("sale_price")} {item.get("currency")}\n'

        if row_buttons:
            keyboard.add(*row_buttons)

        await bot.send_message(message.chat.id, text=responce, reply_markup=keyboard)

    elif message.text == 'Категории':
        responce = ''
        req = bot_api.get_categories()
        if len(req) == 0:
            await bot.send_message(message.chat.id, text="К сожалению, все раскупили")

        keyboard = InlineKeyboardMarkup(row_width=2)

        row_buttons = []
        for item in req:
            id = item.get("id")
            category_name = item.get("name")
            button = InlineKeyboardButton(text=category_name, callback_data=f'category_{id}')
            row_buttons.append(button)

            if len(row_buttons) == 2:
                keyboard.add(*row_buttons)
                row_buttons = []

            responce += f'{item.get("name")}\n'

        if row_buttons:
            keyboard.add(*row_buttons)

        await bot.send_message(message.chat.id, text=responce, reply_markup=keyboard)

    elif message.text == 'Меню':

        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        lots_button = InlineKeyboardButton(text='Лоты', )
        categories = InlineKeyboardButton(text='Категории', )
        about = InlineKeyboardButton(text='О боте', )
        markup.add(lots_button, categories)
        markup.add(about)

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

        keyboard = InlineKeyboardMarkup(row_width=3)
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
        if len(req) == 0:
            return await bot.send_message(call.message.chat.id, text="Нет товаров в данной категории. Выбирете другую.",
                                          reply_markup=keyboard)

        keyboard = InlineKeyboardMarkup(row_width=3)

        for item in req:
            lot_id = item.get("id")
            button_text = item.get("name")
            button = InlineKeyboardButton(text=button_text, callback_data=f'lot_{lot_id}')
            keyboard.add(button)

            responce += f'{lot_id}. {item.get("name")}: {item.get("sale_price")} {item.get("currency")}\n'
        await bot.send_message(call.message.chat.id, text=responce, reply_markup=keyboard)

    if call.data.startswith('buy_'):
        id = call.data.split('_')[1]
        lot = bot_api.get_lot(id)

        question_text = f"Вы уверены, что хотите купить {lot.get('name')}?"
        keyboard = InlineKeyboardMarkup()
        button_yes = InlineKeyboardButton(text='Да', callback_data=f"confirm_buy_{id}")
        button_no = InlineKeyboardButton(text='Нет', callback_data=f"cancel_buy_{id}")
        keyboard.add(button_yes, button_no)
        await bot.send_message(call.message.chat.id, text=question_text, reply_markup=keyboard)

    if call.data.startswith('confirm_buy_'):
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        id = call.data.split('_')[2]
        lot = bot_api.get_lot(id)
        req = bot_api.get_lot_buy(id)

        self_notification = f"Пользователь @{call.from_user.username} купил {lot.get('name')} за {lot.get('sale_price')} {lot.get('currency')}"
        print(f"setting: {config['bot_settings']['CHAT_ID']}, type: {type(config['bot_settings']['CHAT_ID'])}")
        await bot.send_message(config['bot_settings']['CHAT_ID'], text=self_notification)

        message = f"""Спасибо! В ближайшее время я (@slvjzz) с вами свяжусь. 
Так же можете написать мне по любым вопросам.

Вы выбрали {lot.get('name')} за {lot.get('sale_price')} {lot.get('currency')}"""
        await bot.send_message(call.message.chat.id, text=message)

    if call.data.startswith('cancel_buy_'):
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        id = call.data.split('_')[2]
        lot = bot_api.get_lot(id)
        message = f"Жаль, что передумали покупать {lot.get('name')}"

        await bot.send_message(call.message.chat.id, text=message)

asyncio.run(bot.polling(none_stop=True, interval=0))
