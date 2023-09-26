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


async def get_lot(id, chat_id):
    auction_id = ''
    media = await get_photo(id)
    req = bot_api.get_lot(id)
    if req.get('max_bid_amount') is None:
        bid = round(float(req.get('auction_start_price')), 2)
    else:
        bid = round(float(req.get('max_bid_amount')), 2)
    if bid == 0:
        bid += 1
    new_bid = round(float(bid*1.05), 2)

    message = f"{req.get('name')}\nОписание: {req.get('description')} \nЦена: {req.get('sale_price')} {req.get('currency')}"
    keyboard = InlineKeyboardMarkup(row_width=3)

    button_buy = InlineKeyboardButton(text='Купить', callback_data=f"buy_{id}")
    keyboard.add(button_buy)

    if req['auction_id'] is not None:
        auction_id = req['auction_id']
        message = message.replace('\nЦена', '\nКупить сразу')
        if req.get('max_bid_amount') is None:
            message += f'\nСтартовая цена аукциона: {bid}'

    if req.get('max_bid_amount') is not None:
        button_bid = InlineKeyboardButton(text=f'Сделать ставку {new_bid} {req.get("currency")}',
                                          callback_data=f"bid_{id}_{new_bid}_{auction_id}")
        message += f'\nТекущая ставка: {req.get("max_bid_amount")}\nДата окончания аукциона: {req.get("auction_end_date")}'
        keyboard.add(button_bid)
    else:
        button_bid = InlineKeyboardButton(text=f'Сделать первую ставку {new_bid} {req.get("currency")}',
                                          callback_data=f"bid_{id}_{new_bid}_{auction_id}")
        keyboard.add(button_bid)

    if len(media) > 0:
        await bot.send_message(chat_id, text='Загружаю фото... Подождите')
        await bot.send_media_group(chat_id, media)
    await bot.send_message(chat_id, text=message, reply_markup=keyboard)


async def get_lots(chat_id,):
    responce = ''
    req = bot_api.get_lots()
    if len(req) == 0:
        await bot.send_message(chat_id, text="К сожалению, все раскупили")

    keyboard = InlineKeyboardMarkup(row_width=3)

    row_buttons = []
    for index, item in enumerate(req):
        lot_id = item.get("id")
        button_text = item.get("name")
        button = InlineKeyboardButton(text=button_text, callback_data=f'lot_{lot_id}')
        row_buttons.append(button)

        if len(row_buttons) == 3:
            keyboard.add(*row_buttons)
            row_buttons = []

        responce += f'{index + 1}. {item.get("name")}: {item.get("sale_price")} {item.get("currency")}\n'

    if row_buttons:
        keyboard.add(*row_buttons)

    await bot.send_message(chat_id, text=responce, reply_markup=keyboard)


async def get_categories(chat_id):
    responce = ''
    req = bot_api.get_categories()
    if len(req) == 0:
        await bot.send_message(chat_id, text="К сожалению, все раскупили")

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

    await bot.send_message(chat_id, text=responce, reply_markup=keyboard)


async def get_menu(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lots_button = InlineKeyboardButton(text='Лоты', )
    categories = InlineKeyboardButton(text='Категории', )
    about = InlineKeyboardButton(text='О боте', )
    markup.add(lots_button, categories)
    markup.add(about)

    await bot.send_message(chat_id, text='Главное меню', reply_markup=markup)


async def post_bid(lot_id, auction_id, amount, chat_id, user_id):
    req = bot_api.post_bid(lot_id=lot_id,auction_id=auction_id, amount=amount, user_id=user_id)


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
        await get_lots(message.chat.id)

    elif message.text == 'Категории':
        await get_categories(message.chat.id)

    elif message.text == 'Меню':
        await get_menu(message.chat.id)

    elif message.text == 'О боте':
        repl = "Здесь будет информация о боте."
        await bot.send_message(message.chat.id, text=repl)


@bot.callback_query_handler(func=lambda call: True)
async def handle_callback_query(call):
    if call.data.startswith('lot_'):
        id = call.data.split('_')[1]
        await get_lot(id, call.message.chat.id)

    if call.data.startswith('category_'):
        responce = ''
        id = call.data.split('_')[1]
        req = bot_api.get_lots_by_category(id)

        keyboard = InlineKeyboardMarkup(row_width=3)

        for item in req:
            lot_id = item.get("id")
            button_text = item.get("name")
            button = InlineKeyboardButton(text=button_text, callback_data=f'lot_{lot_id}')
            keyboard.add(button)

            responce += f'{lot_id}. {item.get("name")}: {item.get("sale_price")} {item.get("currency")}\n'
        await bot.send_message(call.message.chat.id, text=responce, reply_markup=keyboard)

    if call.data.startswith('buy_'):
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
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
        await bot.send_message(config['bot_settings']['CHAT_ID'], text=self_notification)

        message = f"""Спасибо! В ближайшее время я (@slvjzz) с вами свяжусь. 
Так же можете написать мне по любым вопросам.

Вы выбрали {lot.get('name')} за {lot.get('sale_price')} {lot.get('currency')}"""
        await bot.send_message(call.message.chat.id, text=message)

    if call.data.startswith('cancel_buy_'):
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        id = call.data.split('_')[2]
        lot = bot_api.get_lot(id)
        message = f"Жаль, что передумали покупать {lot.get('name')}. Возвращаюсь к списку лотов."
        await bot.send_message(call.message.chat.id, text=message)
        await get_lots(call.message.chat.id)

    # if call.data.startswith('counteroffer_'):
    #     await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    #     id = call.data.split('_')[1]
    #     user_id = call.from_user.id
    #     user_nickname = call.from_user.username
    #
    #     await bot.send_message(call.message.chat.id, text='Введите желаемую цену')

    if call.data.startswith('bid_'):
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        lot_id = call.data.split('_')[1]
        auction_id = call.data.split('_')[3]
        amount = call.data.split('_')[2]
        lot = bot_api.get_lot(lot_id)

        question_text = f"Хотите поучаствовать в аукционе за лот \"{lot.get('name')}\"?"
        keyboard = InlineKeyboardMarkup()
        button_yes = InlineKeyboardButton(text='Да', callback_data=f"confirm_bid_{lot_id}_{auction_id}_{amount}")
        button_no = InlineKeyboardButton(text='Нет', callback_data=f"cancel_bid_{lot_id}_{auction_id}_{amount}")
        keyboard.add(button_yes, button_no)
        await bot.send_message(call.message.chat.id, text=question_text, reply_markup=keyboard)

    if call.data.startswith('confirm_bid_'):
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        lot_id = call.data.split('_')[2]
        auction_id = call.data.split('_')[3]
        amount = call.data.split('_')[4]
        lot = bot_api.get_lot(lot_id)
        await post_bid(lot_id, auction_id, amount, call.message.chat.id, call.from_user.username)

        message = f"""Спасибо!

Ваша ставка {amount} {lot.get('currency')} за \"{lot.get('name')}\" принята.
По всем вопросам пишите @slvjzz"""
        await bot.send_message(call.message.chat.id, text=message)

    if call.data.startswith('cancel_bid_'):
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        id = call.data.split('_')[2]
        lot = bot_api.get_lot(id)
        message = f"Жаль, что передумали покупать {lot.get('name')}. Возвращаюсь к списку лотов."
        await bot.send_message(call.message.chat.id, text=message)
        await get_lots(call.message.chat.id)

asyncio.run(bot.polling(none_stop=True, interval=0))
