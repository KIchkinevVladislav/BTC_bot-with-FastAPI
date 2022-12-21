import telebot
import math

import config
import client
from database import crud


bot = telebot.TeleBot(config.BOT_TOKEN)

page = 1 # переменная используется при пагинации


@bot.message_handler(commands=['start'])
def start_message(message):
    """
    После команды "/start" пользователей получает кнопки для взаимодействия с ботом
    :param message:
    :return:
    """
    try:
        client.create_user(
            {
                'tg_ID': message.from_user.id,
                'nick': message.from_user.username
            }
        )
    except Exception as Ex:
        bot.send_message(message.chat.id, f'Возникла ошибка: {Ex.args}')
    markup = telebot.types.ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )

    btn1 = telebot.types.KeyboardButton('Кошелек')
    btn2 = telebot.types.KeyboardButton('Перевести')
    btn3 = telebot.types.KeyboardButton('История')

    markup.add(btn1, btn2, btn3)

    text = f'Привет {message.from_user.full_name}, я твой бот-криптокошелек, \n' \
           'у меня ты можешь хранить и отправлять биткоины'

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Кошелек')
def wallet(message):
    """
    Обработчик кнопки "Кошелек"
    Возвращает адрес и баланс кошелька
    """
    wallet = client.get_user_wallet_by_tg_id(message.from_user.id)
    markup = telebot.types.ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Ваш баланс: {wallet["balance"]/100000000} BTC\n' \
           f'Ваш адрес: {wallet["address"]}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='История')
def history(message):
    """
     Обработчик кнопки "Кошелек"
     Возвращает список транзакций пользователя
     """
    markup = telebot.types.ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    transactions = client.get_user_transactions(client.get_user_by_tg_id(message.from_user.id)['id'])
    text = f'Ваши транзакции: \n{transactions}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Меню')
def menu(message):
    """
     Обработчик кнопки "Меню"
     Возвращает пользователя в основное меню с тремя кнопками
     """
    markup = telebot.types.ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    btn1 = telebot.types.KeyboardButton('Кошелек')
    btn2 = telebot.types.KeyboardButton('Перевести')
    btn3 = telebot.types.KeyboardButton('История')
    markup.add(btn1, btn2, btn3)

    text = f'Главное меню'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Я в консоли')
def print_me(message):
    """
     Обработчик обращения к боту: 'Я в консоли'
     Возвращает пользователю его ID в Телеграм и иные данные
     """
    markup = telebot.types.ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    print(message.from_user.to_dict())
    text = f'Ты: {message.from_user.to_dict()}'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.TG_ADMIN_ID and message.text == 'Админ-панель')
def admin_panel(message):
    """
     Обработчик обращения к боту: 'Админ-панель'
     Возвращает кнопки доступные лишь администратору
     """
    markup = telebot.types.ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True
    )
    btn1 = telebot.types.KeyboardButton('Общий баланс')
    btn2 = telebot.types.KeyboardButton('Все пользователи')
    btn3 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1, btn2, btn3)
    text = f'Админ-панель'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.TG_ADMIN_ID and message.text == 'Все пользователи')
def all_users(message):
    """
     Обработчик кнопки "Все пользователи"
     Возвращает перечень пользователей
     с пагинацией по 4 пользователя на страницу
     """
    global page
    page = 1
    users = client.get_users()
    print(users)
    pages = math.ceil(len(users) / 4)
    text = f'Пользователи:'
    inline_markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    for user in users[page-1:page*4]:
        inline_markup.add(telebot.types.InlineKeyboardButton(
            text=f'Пользователь: {user["tg_ID"]}',
            callback_data=f"user_{user['tg_ID']}")
        )
    forward_btn = telebot.types.InlineKeyboardButton(text='Вперед', callback_data='forward')
    page_btn = telebot.types.InlineKeyboardButton(text=f'{page}/{pages}', callback_data='page')
    inline_markup.add(page_btn, forward_btn)

    bot.send_message(message.chat.id, text,
                     reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """
    Инлайт-кнопки для взаимодействия со списком пользователей
    """
    global page
    query_type = call.data.split('_')[0]
    users = client.get_users()
    pages = math.ceil(len(users) / 4)

    if query_type == 'user':
        page = 1
        user_id = call.data.split('_')[1]
        inline_markup = telebot.types.InlineKeyboardMarkup()
        for user in users:
            if str(user['tg_ID']) == user_id:
                inline_markup.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data='users'),
                                  telebot.types.InlineKeyboardButton(text="Удалить пользователя",
                                                                     callback_data=f'delete_user_{user_id}'))

                bot.edit_message_text(text=f'Данные о пользователе:\n'
                                           f'ID: {user["tg_ID"]}\n'
                                           f'Ник: {user.get("nick")}\n'
                                           f'Баланс: {client.get_user_balance_by_id(user["id"])}',
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=inline_markup)
                print(f"Запрошен {user}")
                break

    if query_type == 'users':
        inline_markup = telebot.types.InlineKeyboardMarkup()
        for user in users[(page-1) * 4:page * 4]:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Пользователь: {user["tg_ID"]}',
                                                                 callback_data=f"user_{user['tg_ID']}"))
        forward_btn = telebot.types.InlineKeyboardButton(text='Вперед', callback_data='forward')
        page_btn = telebot.types.InlineKeyboardButton(text=f'{page}/{pages}', callback_data='page')
        inline_markup.add(page_btn, forward_btn)

        bot.edit_message_text(text="Пользователи:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_markup)

    if query_type == 'delete' and call.data.split('_')[1] == 'user':
        user_id = int(call.data.split('_')[2])
        for i, user in enumerate(users):
            if user['tg_ID'] == user_id:
                print(f'Удален пользователя: {users[i]}')
                client.delete_user(users.pop(i)['id'])
        users = client.get_users()
        inline_markup = telebot.types.InlineKeyboardMarkup()
        for user in users[(page-1) * 4:page * 4]:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Пользователь: {user["tg_ID"]}',
                                                                 callback_data=f"user_{user['tg_ID']}"))
        forward_btn = telebot.types.InlineKeyboardButton(text='Вперед', callback_data='forward')
        page_btn = telebot.types.InlineKeyboardButton(text=f'{page}/{pages}', callback_data='page')
        inline_markup.add(page_btn, forward_btn)

        bot.edit_message_text(text="Пользователи:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_markup)

    if query_type in ('forward', 'back'):
        inline_markup = telebot.types.InlineKeyboardMarkup(row_width=3)
        if query_type == 'forward':
            page += 1
        else:
            page -= 1
        print(query_type, page)
        back_btn = telebot.types.InlineKeyboardButton(text='Назад', callback_data='back')
        forward_btn = telebot.types.InlineKeyboardButton(text='Вперед', callback_data='forward')
        page_btn = telebot.types.InlineKeyboardButton(text=f'{page}/{pages}', callback_data='page')
        for user in users[(page-1) * 4:page * 4]:
            inline_markup.add(telebot.types.InlineKeyboardButton(text=f'Пользователь: {user["tg_ID"]}',
                                                                 callback_data=f"user_{user['tg_ID']}"))
        if page == 1:
            inline_markup.add(page_btn, forward_btn)
        elif page == pages:
            inline_markup.add(back_btn, page_btn)
        else:
            inline_markup.add(back_btn, page_btn, forward_btn)
        bot.edit_message_text(text="Пользователи:",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_markup)


@bot.message_handler(func=lambda message: message.from_user.id == config.TG_ADMIN_ID and message.text == "Общий баланс")
def total_balance(message):
    """
    Обработчик кнопки "Общий баланс"
    Возвращает суммарный баланс всех пользователей
    """
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    btn2 = telebot.types.KeyboardButton('Админ-панель')
    markup.add(btn1, btn2)
    balance = client.get_total_balance()
    text = f'Общий баланс: {balance/100000000} BTC'
    bot.send_message(message.chat.id, text, reply_markup=markup)


# автомат для обработки диалога с отправкой транзакции
states_list = ["ADDRESS", "AMOUNT", "CONFIRM"]
states_of_users = {}


@bot.message_handler(regexp='Перевести')
def start_transaction(message):
    """
    Обработчик кнопки "Перевести"
    Ожидает введение пользователей адреса кошелька
    осуществляем переход на следующее состояние
    """
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Введите адрес кошелька куда хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)
    # предоставляется состояние при котором будет возвращаться следующее сообщение пользователю
    states_of_users[message.from_user.id] = {"STATE":"ADDRESS"}


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'ADDRESS')
def get_amount_of_transaction(message):
    """
    Запрос у пользователя суммы для перевода
    Переход к следующему состоянию
    """
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    text = f'Введите сумму в сатоши, которую хотите перевести: '
    bot.send_message(message.chat.id, text, reply_markup=markup)
    states_of_users[message.from_user.id]["STATE"] = "AMOUNT"
    states_of_users[message.from_user.id]["ADDRESS"] = message.text


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'AMOUNT')
def get_confirmation_of_transaction(message):
    """
    Осуществляется проверка достаточности средств для перевода,
    а также введения числовых данных
    Переход к следующему состоянию, через кнопку "Подтверждаю"
    """
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('Меню')
    markup.add(btn1)
    if message.text.isdigit():
        text = f'Вы хотите перевести {message.text} сатоши,\n' \
               f'на биткоин-адрес {states_of_users[message.from_user.id]["ADDRESS"]}: '
        confirm = telebot.types.KeyboardButton('Подтверждаю')
        markup.add(confirm)
        bot.send_message(message.chat.id, text, reply_markup=markup)
        states_of_users[message.from_user.id]["STATE"] = "CONFIRM"
        states_of_users[message.from_user.id]["AMOUNT"] = int(message.text)
    else:
        text = f'Вы ввели не число, попробуйте заново: '
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: states_of_users.get(message.from_user.id)["STATE"] == 'CONFIRM')
def get_hash_of_transaction(message):
    """
    При взаимодействии с кнопкой "Подтверждаю"
    создается транзакция,
    пользователю возвращается информация об отправленной транзакции
    """
    if message.text == "Меню":
        del states_of_users[message.from_user.id]
        menu(message)
    elif message.text == "Подтверждаю":
        bot.send_message(message.chat.id, f" Ваша транзакция: "+str(client.create_transaction(message.from_user.id,
                                         states_of_users[message.from_user.id]['ADDRESS'],
                                         states_of_users[message.from_user.id]['AMOUNT'])))
        del states_of_users[message.from_user.id]
        menu(message)

"""
Приведенный ниже код
заполнит Вашу базу пользователями
"""
if __name__ == '__main__':
    try:
        crud.get_user_by_id(1)  # проверяем не созданы ли в базе пользователи
    except:
            with crud.db_session:
                # присваиваем пользователю наш ID в Телеграм
                # для работы с админ панелью
                crud.create_user(config.TG_ADMIN_ID)
                # создаем остальных пользователей
                crud.create_user(111)
                crud.create_user(222)
                crud.create_user(333)
                crud.create_user(444)

    bot.infinity_polling()  # запускаем бот
