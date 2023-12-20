import telebot
import timetable_parser as ps

bot = telebot.TeleBot("6597882072:AAEAj1gGHd3MkboF2mYryrDRsLoF9nkq5QY")

states = {}
group = ''
login = ''
password = ''


@bot.message_handler(commands=['start'])
def main(message):
    ps.create_database()
    states[message.chat.id] = 'group'
    bot.send_message(message.chat.id, f'Привет, {message.from_user.username}! Учишься в политехе?)\n'
                                      'давай настроим для твоей группы бота с расписанием)'
                                      'В какой группе ты учишься? (нужно полное название, например\n '
                                      'ИВТАПбд-31)')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global login   # Declare login as a global variable
    chat_id = message.chat.id
    if chat_id in states:
        state = states[chat_id]

        if state == 'group':
            group = message.text
            bot.send_message(chat_id, 'Сейчас проверю, вдруг кто-то уже настроил бота для твоей группы')
            data = ps.retrieve_data(group)
            if len(data) > 0:
                bot.send_message(chat_id, 'Расписание уже было считано. могу вывести его для тебя)')
                states[chat_id] = ''
            else:
                states[chat_id] = 'login'
                bot.send_message(chat_id, 'похоже, что ты первый меня нашёл из своих одногруппников\n'
                                          'сразу предупрежу, я не сохраняю даные, мне это не к чему!\n'
                                          'Я запрашиваю следующую информацию, чтобы мой создатель не получил '
                                          'бан в своём же университете)\n'
                                          'Введи логин от личного кабинета:')
        if state == 'login':
            login = message.text
            bot.send_message(chat_id, 'Введи пароль:')
            states[chat_id] = 'password'
        if state == 'password':
            password = message.text
            bot.send_message(chat_id, 'Давай посмотрим, какое у твоей группы расписание')
            states[chat_id] = ''

    print(login)
    if login != '':
        if ps.parse_database(group, login, password) == 1:
            bot.send_message(chat_id, 'Кажется при вводе данных была допущена ошибка')
            states[chat_id] = 'login'


bot.infinity_polling()
