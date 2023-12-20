import json
import sys

import requests
import datetime
import sqlite3

lesson_start_end = [
    '8:30-9:50', '10:00-11:20',
    '11:30-12:50', '13:30-14:50',
    '15:00-16:20', '16:30-17:50',
    '18:00-19:20', '19:30-20:50']
db_name = 'lab2.db'


#  функция, которая считывает расписание с сайта
# для этой функции можно запрашивать логин и пароль пользователя
def getjson(group, login, password):
    payload = {
        'login': login,
        'password': password
    }
    with requests.Session() as s:
        s.post("https://lk.ulstu.ru/?q=auth/login", data=payload)

        r = s.get(f'https://time.ulstu.ru/api/1.0/timetable?filter={group}')  # можно передавать сюда группу

        try:
            parsed_timetable = json.loads(r.text)
        except json.JSONDecodeError:
            print("Ошибка API! Проверьте логи и пароль.")
            sys.exit()

    return parsed_timetable


# функция для определения текущего дня и недели от начала сентября
def get_current_week_n_day():
    september_1 = datetime.date(datetime.date.today().year, 9, 1)
    current_date = datetime.date.today()
    current_week_number = (current_date - september_1).days // 7 + 1
    current_week_day = datetime.date.today().weekday()
    current_week_number = 0 if (current_week_number - 1) % 2 == 0 else 1

    return current_week_number, current_week_day + 1


# форматирование даты и времени для красивого вывода
def format_date(date):
    months = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
        'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ]

    day = date.day + 1
    month = months[date.month - 1]

    return f'{day} {month}'


# функция для определения номер дня недели по полному названию
def get_weekday_number(weekday_name):
    weekday_dict = {
        'понедельник': 0,
        'вторник': 1,
        'среда': 2,
        'четверг': 3,
        'пятница': 4,
        'суббота': 5,
        'воскресенье': 6
    }

    if weekday_name.lower() in weekday_dict:
        return weekday_dict[weekday_name.lower()]
    else:
        return "Ошибка: неправильный ввод дня недели."


# функция создания базы данных в том случае, если её нет
def create_database():
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS timetable
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   week INTEGER,
                   day INTEGER,
                   lesson_number INTEGER,
                   group_name TEXT,
                   lesson TEXT,
                   teacher TEXT,
                   room TEXT,
                   parsed_by INTEGER)''')  # группа должна быть указана пользователем
    connect.commit()
    connect.close()


def update_database(changing_data, new_data):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute('''UPDATE timetable SET week=?, day=?, lesson_number=?, room=? 
                    WHERE week=? AND day=? AND lesson_number=?''',
                   (new_data[0], new_data[1], new_data[2], new_data[3],
                    changing_data[0], changing_data[1], changing_data[2]))
    connect.commit()
    connect.close()


def delete_entry(week, day, lesson_number):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute('DELETE FROM timetable WHERE week = ? AND day = ? AND lesson_number = ?',
                   (week, day, lesson_number))
    connect.commit()
    connect.close()


# функция вставки данных в базу данных
def insert_data(week_num, day_number, lesson_number, group_name, lesson_name,
                teacher_name, room_number, parsed_by_who):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute('''INSERT INTO timetable (week, day, lesson_number, 
        group_name, lesson, teacher, room, parsed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (week_num,
                    day_number,
                    lesson_number,
                    group_name,
                    lesson_name,
                    teacher_name,
                    room_number,
                    parsed_by_who))  # группа должна быть указана пользователем
    connect.commit()
    connect.close()


# функция считывания данных из бд
def retrieve_data(group):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM timetable WHERE group_name=?", (group,))
    data = cursor.fetchall()
    connect.close()
    return data


# функция парса json формата данных из расписания из функции getjson
def parse_database(group, login, password):
    create_database()
    timetable = getjson(group, login, password)
    if len(timetable) == 0:
        return 1

    for week in timetable["response"]["weeks"]:
        week_number = 1 if int(week) % 2 != 0 else 0
        week_day = 0
        for day in timetable["response"]["weeks"][f"{week}"]["days"]:
            lesson_n = 0
            for lesson in timetable["response"]["weeks"][f"{week}"]["days"][day["day"]]["lessons"]:
                if len(lesson) > 0:
                    insert_data(week_number, week_day, lesson_n,
                                'ИВТАПбд-31', lesson[0]['nameOfLesson'],
                                lesson[0]['teacher'], lesson[0]['room'], 'bot')
                lesson_n += 1
            week_day += 1
    return 0
