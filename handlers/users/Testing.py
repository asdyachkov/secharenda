from datetime import date

from aiogram.dispatcher import FSMContext
import psycopg2
from data.config import ADMINS, DB_URI
from states import Test
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline import keyb0, keyb_back
from keyboards.inline.callback_datas import month_callback, day_callback
from loader import dp, bot

month_list = ['Январь',
              'Февраль',
              'Март',
              'Апрель',
              'Май',
              'Июнь',
              'Июль',
              'Август',
              'Сентябрь',
              'Октябрь',
              'Ноябрь',
              'Декабрь'
              ]
month_day = {'Январь': 31,
             'Февраль': 28,
             'Март': 31,
             'Апрель': 30,
             'Май': 31,
             'Июнь': 30,
             'Июль': 31,
             'Август': 31,
             'Сентябрь': 30,
             'Октябрь': 31,
             'Ноябрь': 30,
             'Декабрь': 31
             }
chisla = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


@dp.message_handler(Command('start'))
async def start_message(message: types.Message):
    await message.answer('Здравствуйте! 🙂\n'
                         'Данная программа предназначена для аренды нашего домика в деревне. 🏡\n'
                         'Нажмите на кнопку ниже, чтобы записаться.',
                         reply_markup=keyb0)


@dp.message_handler(Command('cancel'), state=Test.Q6)
async def zapis_otmena(message: types.Message, state: FSMContext):
    await message.answer("Запись отменена 📛")
    await message.answer("Для создания новой записи напишите /start",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


@dp.callback_query_handler(state=Test.Q8)
async def start_message(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Здравствуйте! 🙂\n'
                              'Данная программа предназначена для аренды нашего домика в деревне. 🏡\n'
                              'Нажмите на кнопку ниже, чтобы записаться.',
                              reply_markup=keyb0)
    await call.message.delete()
    await state.finish()


@dp.callback_query_handler(text_contains="admin_menu")
async def start_zapis(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    id_client = call.message.chat.id
    tr = 0
    for id_admin in ADMINS:
        if str(id_client) == str(id_admin):
            tr = 1
            break
    if tr == 1:
        trash = []
        db_object.execute("SELECT * FROM zapisi")
        info = db_object.fetchall()
        info.append(('q', 'q', 'q'))
        now = int(str(date.today())[5:7]) - 1
        now_day = int(str(date.today())[-2::])
        await call.message.answer(f'Занятые даты:')
        for i in range(0, len(info)):
            if info[i][0] != month_list[now] or info[i][0] == month_list[now] and int(info[i][1] >= now_day):
                month_start = info[i][0]
                day_start = info[i][1]
                about_client_start = info[i][2]
                month_end = month_start
                day_end = day_start
                for q in range(i, len(info)):
                    if str(about_client_start) == str(info[q][2]):
                        month_end = info[q][0]
                        day_end = info[q][1]
                    elif str(about_client_start) != str(info[q][2]) and str(about_client_start) not in trash:
                        await call.message.answer(f'⚠ Есть запись с {month_start}, {day_start} число '
                                                  f'по {month_end}, {day_end} число\n Номер телефона и имя клиента {about_client_start} ⚠')
                        trash.append(str(about_client_start))
        await call.message.answer('Чтобы вернуться в меню, нажмите на кнопку 😄', reply_markup=keyb_back)
    else:
        await call.message.answer('Вы не обладаете правами администратора 🙁\n'
                                  'Возвращаю в меню',
                                  reply_markup=keyb0)
    await call.message.delete()
    await Test.Q8.set()


@dp.callback_query_handler(text_contains="arend_True")
async def start_zapis(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    now = int(str(date.today())[5:7])-1
    keyb1 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{month_list[now] if now<= 12 else month_list[now-12]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now] if now<= 12 else month_list[now-12]}")),
                InlineKeyboardButton(text=f"{month_list[now+1] if now+1<= 12 else month_list[now-11]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now+1] if now+1<= 12 else month_list[now-11]}"))
            ],
            [
                InlineKeyboardButton(text=f"{month_list[now+2] if now+2<= 12 else month_list[now-10]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now+2] if now+2<= 12 else month_list[now-10]}")),
                InlineKeyboardButton(text=f"{month_list[now+3] if now+3<= 12 else month_list[now-9]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now+3] if now+3<= 12 else month_list[now-9]}"))
            ],
            [
                InlineKeyboardButton(text="Назад ↩", callback_data="cancel")
            ]
        ]
    )
    await call.message.answer("Выберите месяц и число, когда Вы бы хотели к нам приехать 📅",
                              reply_markup=keyb1)
    await call.message.delete()
    await Test.Q2.set()


@dp.callback_query_handler(state=Test.Q2, text_contains="cancel")
async def tell_about(call: CallbackQuery, state: FSMContext):
    await call.answer("Запись отменена 📛", show_alert=True)
    await call.message.answer("Для создания новой записи напишите /start")
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.delete()
    await state.finish()


@dp.callback_query_handler(state=Test.Q2)
async def month_zapis(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    month = str(call.data)[6::]
    now_day = int(str(date.today())[-2::])
    number_today = int(str(date.today())[5:7])-1
    db_object.execute("SELECT * FROM zapisi")
    info = db_object.fetchall()
    zanyato = []
    for i in info:
        if str(i[0]) == month:
            zanyato.append(str(i[1]))
    await state.update_data(answer_month=month)
    keyb2 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{'1' if (now_day < 1 or month != month_list[number_today]) and '1' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="1")),
                InlineKeyboardButton(text=f"{'2' if (now_day < 2 or month != month_list[number_today]) and '2' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="2")),
                InlineKeyboardButton(text=f"{'3' if (now_day < 3 or month != month_list[number_today]) and '3' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="3")),
                InlineKeyboardButton(text=f"{'4' if (now_day < 4 or month != month_list[number_today]) and '4' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="4")),
                InlineKeyboardButton(text=f"{'5' if (now_day < 5 or month != month_list[number_today]) and '5' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="5")),
                InlineKeyboardButton(text=f"{'6' if (now_day < 6 or month != month_list[number_today]) and '6' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="6")),
                InlineKeyboardButton(text=f"{'7' if (now_day < 7 or month != month_list[number_today]) and '7' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="7")),
            ],
            [
                InlineKeyboardButton(text=f"{'8' if (now_day < 8 or month != month_list[number_today]) and '8' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="8")),
                InlineKeyboardButton(text=f"{'9' if (now_day < 9 or month != month_list[number_today]) and '9' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="9")),
                InlineKeyboardButton(text=f"{'10' if (now_day < 10 or month != month_list[number_today]) and '10' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="10")),
                InlineKeyboardButton(text=f"{'11' if (now_day < 11 or month != month_list[number_today]) and '11' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="11")),
                InlineKeyboardButton(text=f"{'12' if (now_day < 12 or month != month_list[number_today]) and '12' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="12")),
                InlineKeyboardButton(text=f"{'13' if (now_day < 13 or month != month_list[number_today]) and '13' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="13")),
                InlineKeyboardButton(text=f"{'14' if (now_day < 14 or month != month_list[number_today]) and '14' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="14")),
            ],
            [
                InlineKeyboardButton(text=f"{'15' if (now_day < 15 or month != month_list[number_today]) and '15' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="15")),
                InlineKeyboardButton(text=f"{'16' if (now_day < 16 or month != month_list[number_today]) and '16' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="16")),
                InlineKeyboardButton(text=f"{'17' if (now_day < 17 or month != month_list[number_today]) and '17' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="17")),
                InlineKeyboardButton(text=f"{'18' if (now_day < 18 or month != month_list[number_today]) and '18' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="18")),
                InlineKeyboardButton(text=f"{'19' if (now_day < 19 or month != month_list[number_today]) and '19' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="19")),
                InlineKeyboardButton(text=f"{'20' if (now_day < 20 or month != month_list[number_today]) and '20' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="20")),
                InlineKeyboardButton(text=f"{'21' if (now_day < 21 or month != month_list[number_today]) and '21' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="21")),
            ],
            [
                InlineKeyboardButton(text=f"{'22' if (now_day < 22 or month != month_list[number_today]) and '22' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="22")),
                InlineKeyboardButton(text=f"{'23' if (now_day < 23 or month != month_list[number_today]) and '23' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="23")),
                InlineKeyboardButton(text=f"{'24' if (now_day < 24 or month != month_list[number_today]) and '24' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="24")),
                InlineKeyboardButton(text=f"{'25' if (now_day < 25 or month != month_list[number_today]) and '25' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="25")),
                InlineKeyboardButton(text=f"{'26' if (now_day < 26 or month != month_list[number_today]) and '26' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="26")),
                InlineKeyboardButton(text=f"{'27' if (now_day < 27 or month != month_list[number_today]) and '27' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="27")),
                InlineKeyboardButton(text=f"{'28' if (now_day < 28 or month != month_list[number_today]) and '28' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="28")),
            ],
            [
                InlineKeyboardButton(text=f"{'29' if month_day[month] > 28 and (now_day < 29 or month != month_list[number_today]) and '29' not in zanyato else ''}",
                                     callback_data=day_callback.new(date=f"{'29' if month_day[month] >= 29 else ''}")),
                InlineKeyboardButton(text=f"{'30' if month_day[month] > 29 and (now_day < 30 or month != month_list[number_today]) and '30' not in zanyato else ''}",
                                     callback_data=day_callback.new(date=f"{'30' if month_day[month] >= 30 else ''}")),
                InlineKeyboardButton(text=f"{'31' if month_day[month] > 30 and (now_day < 31 or month != month_list[number_today]) and '31' not in zanyato else ''}",
                                     callback_data=day_callback.new(date=f"{'31' if month_day[month] >= 31 else ''}"))
            ],
            [
                InlineKeyboardButton(text="Назад ↩", callback_data="cancel")
            ]
        ]
    )
    await call.message.answer("А теперь день 🗓", reply_markup=keyb2)
    await call.message.delete()
    await Test.Q3.set()


@dp.callback_query_handler(state=Test.Q3, text_contains="cancel")
async def another_month(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    now = int(str(date.today())[5:7]) - 1
    keyb1 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{month_list[now] if now <= 12 else month_list[now - 12]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now] if now <= 12 else month_list[now - 12]}")),
                InlineKeyboardButton(text=f"{month_list[now + 1] if now + 1 <= 12 else month_list[now - 11]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now + 1] if now + 1 <= 12 else month_list[now - 11]}"))
            ],
            [
                InlineKeyboardButton(text=f"{month_list[now + 2] if now + 2 <= 12 else month_list[now - 10]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now + 2] if now + 2 <= 12 else month_list[now - 10]}")),
                InlineKeyboardButton(text=f"{month_list[now + 3] if now + 3 <= 12 else month_list[now - 9]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now + 3] if now + 3 <= 12 else month_list[now - 9]}"))
            ],
            [
                InlineKeyboardButton(text="Назад ↩", callback_data="cancel")
            ]
        ]
    )
    await call.message.answer("Выберите месяц и число, когда Вы бы хотели к нам приехать 🗓",
                              reply_markup=keyb1)
    await call.message.delete()
    await Test.Q2.set()


@dp.callback_query_handler(state=Test.Q3)
async def end_zapis(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    day = str(call.data)[6::]
    await state.update_data(answer_day=day)
    data = await state.get_data()
    month = data.get('answer_month')
    now_month = 0
    for i in month_list:
        if i == month:
            break
        now_month += 1
    keyb3 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{month_list[now_month] if now_month <= 12 else month_list[now_month - 12]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now_month] if now_month <= 12 else month_list[now_month - 12]}")),
                InlineKeyboardButton(text=f"{month_list[now_month + 1] if now_month + 1 <= 12 else month_list[now_month - 11]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now_month + 1] if now_month + 1 <= 12 else month_list[now_month - 11]}"))
            ],
            [
                InlineKeyboardButton(text="Назад ↩", callback_data="cancel")
            ]
        ]
    )
    await call.message.answer("Выберите месяц и число, когда Вы планируете выезд 📅",
                              reply_markup=keyb3)
    await call.message.delete()
    await Test.Q4.set()


@dp.callback_query_handler(state=Test.Q4, text_contains="cancel")
async def another_month(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    now = int(str(date.today())[5:7]) - 1
    keyb1 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{month_list[now] if now <= 12 else month_list[now - 12]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now] if now <= 12 else month_list[now - 12]}")),
                InlineKeyboardButton(text=f"{month_list[now + 1] if now + 1 <= 12 else month_list[now - 11]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now + 1] if now + 1 <= 12 else month_list[now - 11]}"))
            ],
            [
                InlineKeyboardButton(text=f"{month_list[now + 2] if now + 2 <= 12 else month_list[now - 10]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now + 2] if now + 2 <= 12 else month_list[now - 10]}")),
                InlineKeyboardButton(text=f"{month_list[now + 3] if now + 3 <= 12 else month_list[now - 9]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now + 3] if now + 3 <= 12 else month_list[now - 9]}"))
            ],
            [
                InlineKeyboardButton(text="Назад ↩", callback_data="cancel")
            ]
        ]
    )
    await call.message.answer("Выберите месяц и число, когда Вы бы хотели к нам приехать 🗓",
                              reply_markup=keyb1)
    await call.message.delete()
    await Test.Q2.set()


@dp.callback_query_handler(state=Test.Q4)
async def day_out_zapis(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    month = str(call.data)[6::]
    await state.update_data(answer_month_out=month)
    data = await state.get_data()
    day = int(data.get('answer_day'))
    month_input = data.get('answer_month')
    db_object.execute("SELECT * FROM zapisi")
    info = db_object.fetchall()
    zanyato = []
    for i in info:
        if str(i[0]) == month:
            zanyato.append(str(i[1]))
    tr = 0
    if month_input != month:
        if '1' in zanyato:
            tr = 1

    def func(l1, l2):
        for x in l1:
            if x in l2:
                return True
        return False
    f = lambda x, y: int(x)-1 if month_input == month else int(y)
    keyb4 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{'1' if (month_input != month or day < 1) and tr == 0 and '1' not in zanyato else ''}",
                                     callback_data=day_callback.new(date="1")),
                InlineKeyboardButton(text=f"{'2' if (month_input != month or day < 2) and tr == 0 and '2' not in zanyato and func(chisla[f(day, 0)], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="2")),
                InlineKeyboardButton(text=f"{'3' if (month_input != month or day < 3) and tr == 0 and '3' not in zanyato and func(chisla[f(day, 1):1], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="3")),
                InlineKeyboardButton(text=f"{'4' if (month_input != month or day < 4) and tr == 0 and '4' not in zanyato and func(chisla[f(day, 2):2], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="4")),
                InlineKeyboardButton(text=f"{'5' if (month_input != month or day < 5) and tr == 0 and '5' not in zanyato and func(chisla[f(day, 3):3], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="5")),
                InlineKeyboardButton(text=f"{'6' if (month_input != month or day < 6) and tr == 0 and '6' not in zanyato and func(chisla[f(day, 4):4], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="6")),
                InlineKeyboardButton(text=f"{'7' if (month_input != month or day < 7) and tr == 0 and '7' not in zanyato and func(chisla[f(day, 5):5], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="7")),
            ],
            [
                InlineKeyboardButton(text=f"{'8' if (month_input != month or day < 8) and tr == 0 and '8' not in zanyato and func(chisla[f(day, 6):6], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="8")),
                InlineKeyboardButton(text=f"{'9' if (month_input != month or day < 9) and tr == 0 and '9' not in zanyato and func(chisla[f(day, 7):7], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="9")),
                InlineKeyboardButton(text=f"{'10' if (month_input != month or day < 10) and tr == 0 and '10' not in zanyato and func(chisla[f(day, 8):8], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="10")),
                InlineKeyboardButton(text=f"{'11' if (month_input != month or day < 11) and tr == 0 and '11' not in zanyato and func(chisla[f(day, 9):9], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="11")),
                InlineKeyboardButton(text=f"{'12' if (month_input != month or day < 12) and tr == 0 and '12' not in zanyato and func(chisla[f(day, 10):10], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="12")),
                InlineKeyboardButton(text=f"{'13' if (month_input != month or day < 13) and tr == 0 and '13' not in zanyato and func(chisla[f(day, 11):11], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="13")),
                InlineKeyboardButton(text=f"{'14' if (month_input != month or day < 14) and tr == 0 and '14' not in zanyato and func(chisla[f(day, 12):12], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="14")),
            ],
            [
                InlineKeyboardButton(text=f"{'15' if (month_input != month or day < 15) and tr == 0 and '15' not in zanyato and func(chisla[f(day, 13):13], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="15")),
                InlineKeyboardButton(text=f"{'16' if (month_input != month or day < 16) and tr == 0 and '16' not in zanyato and func(chisla[f(day, 14):14], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="16")),
                InlineKeyboardButton(text=f"{'17' if (month_input != month or day < 17) and tr == 0 and '17' not in zanyato and func(chisla[f(day, 15):15], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="17")),
                InlineKeyboardButton(text=f"{'18' if (month_input != month or day < 18) and tr == 0 and '18' not in zanyato and func(chisla[f(day, 16):16], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="18")),
                InlineKeyboardButton(text=f"{'19' if (month_input != month or day < 19) and tr == 0 and '19' not in zanyato and func(chisla[f(day, 17):17], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="19")),
                InlineKeyboardButton(text=f"{'20' if (month_input != month or day < 20) and tr == 0 and '20' not in zanyato and func(chisla[f(day, 18):18], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="20")),
                InlineKeyboardButton(text=f"{'21' if (month_input != month or day < 21) and tr == 0 and '21' not in zanyato and func(chisla[f(day, 19):19], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="21")),
            ],
            [
                InlineKeyboardButton(text=f"{'22' if (month_input != month or day < 22) and tr == 0 and '22' not in zanyato and func(chisla[f(day, 20):20], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="22")),
                InlineKeyboardButton(text=f"{'23' if (month_input != month or day < 23) and tr == 0 and '23' not in zanyato and func(chisla[f(day, 21):21], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="23")),
                InlineKeyboardButton(text=f"{'24' if (month_input != month or day < 24) and tr == 0 and '24' not in zanyato and func(chisla[f(day, 22):22], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="24")),
                InlineKeyboardButton(text=f"{'25' if (month_input != month or day < 25) and tr == 0 and '25' not in zanyato and func(chisla[f(day, 23):23], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="25")),
                InlineKeyboardButton(text=f"{'26' if (month_input != month or day < 26) and tr == 0 and '26' not in zanyato and func(chisla[f(day, 24):24], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="26")),
                InlineKeyboardButton(text=f"{'27' if (month_input != month or day < 27) and tr == 0 and '27' not in zanyato and func(chisla[f(day, 25):25], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="27")),
                InlineKeyboardButton(text=f"{'28' if (month_input != month or day < 28) and tr == 0 and '28' not in zanyato and func(chisla[f(day, 26):26], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date="28")),
            ],
            [
                InlineKeyboardButton(text=f"{'29' if month_day[month] >= 29 and (month_input != month or day < 29) and tr == 0 and '29' not in zanyato and func(chisla[f(day, 27):27], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date=f"{'29' if month_day[month] >= 29 else ''}")),
                InlineKeyboardButton(text=f"{'30' if month_day[month] >= 30 and (month_input != month or day < 30) and tr == 0 and '30' not in zanyato and func(chisla[f(day, 28):28], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date=f"{'30' if month_day[month] >= 30 else ''}")),
                InlineKeyboardButton(text=f"{'31' if month_day[month] >= 31 and (month_input != month or day < 31) and tr == 0 and '31' not in zanyato and func(chisla[f(day, 29):29], zanyato) == False else ''}",
                                     callback_data=day_callback.new(date=f"{'31' if month_day[month] >= 31 else ''}"))
            ],
            [
                InlineKeyboardButton(text="Назад ↩", callback_data="cancel")
            ]
        ]
    )
    await call.message.answer("А теперь день 🗓\n"
                              "(Если Вам не из чего выбрать, значит все даты в этом месяце забронированы, или Вы хотите записаться, начиная не с этого месяца, но первое число уже кем-то занято 🙂)", reply_markup=keyb4)
    await call.message.delete()
    await Test.Q5.set()


@dp.callback_query_handler(state=Test.Q5, text_contains="cancel")
async def end_zapis(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    day = str(call.data)[6::]
    await state.update_data(answer_day=day)
    data = await state.get_data()
    month = data.get('answer_month')
    now_month = 0
    for i in month_list:
        if i == month:
            break
        now_month += 1
    keyb3 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{month_list[now_month] if now_month <= 12 else month_list[now_month - 12]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now_month] if now_month <= 12 else month_list[now_month - 12]}")),
                InlineKeyboardButton(text=f"{month_list[now_month + 1] if now_month + 1 <= 12 else month_list[now_month - 11]}",
                                     callback_data=month_callback.new(
                                         month=f"{month_list[now_month + 1] if now_month + 1 <= 12 else month_list[now_month - 11]}"))
            ],
            [
                InlineKeyboardButton(text="Назад ↩", callback_data="cancel")
            ]
        ]
    )
    await call.message.answer("Выберите месяц и число, когда Вы планируете выезд 📅",
                              reply_markup=keyb3)
    await call.message.delete()
    await Test.Q4.set()


@dp.callback_query_handler(state=Test.Q5)
async def zapis_made(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(cache_time=1)
    day_out = str(call.data)[6::]
    await state.update_data(answer_day_out=day_out)
    data = await state.get_data()
    month = data.get('answer_month')
    day = data.get('answer_day')
    month_out = data.get('answer_month_out')
    await call.message.answer("Аренда домика продлится: \n"
                              f"С {month}, {day} число ✅\n"
                              f"По {month_out}, {day_out} число ✅\n"
                              f"Для создания записи скажите как к Вам можно будет обращаться 😀\n"
                              f"И отправьте нам свой номер телефона ☎ \n"
                              f"Для отмены записи введите команду /cancel",
                              reply_markup=types.ReplyKeyboardRemove())
    await call.message.delete()
    await Test.Q6.set()


@dp.message_handler(state=Test.Q6)
async def create_zapis(message: types.message, state: FSMContext):
    await message.answer("Спасибо, запись создана!\n"
                         "В ближайшее время с Вами свяжется наш сотрудник для подтерждения аренды☺")
    phone_number = message.text
    await state.update_data(phone_number=phone_number)
    data = await state.get_data()
    answer1 = data.get('answer_month')
    answer2 = data.get('answer_day')
    answer3 = data.get('answer_month_out')
    answer4 = data.get('answer_day_out')
    await state.finish()
    if answer1 == answer3:
        for i in range(int(answer2), int(answer4) + 1):
            db_object.execute("INSERT INTO zapisi(month, day, telephone) VALUES (%s, %s, %s)", (answer1, i, phone_number))
    else:
        for i in range(int(answer2), month_day[answer1] + 1):
            db_object.execute("INSERT INTO zapisi(month, day, telephone) VALUES (%s, %s, %s)", (answer1, i, phone_number))
        for i in range(1, int(answer4) + 1):
            db_object.execute("INSERT INTO zapisi(month, day, telephone) VALUES (%s, %s, %s)", (answer3, i, phone_number))
    db_connection.commit()
    for i in ADMINS:
        await bot.send_message(chat_id=i,
                               text=f'Новая запись c {answer1}, {answer2} число, по {answer3}, {answer4} число\n'
                                    f'Имя и номер телефона посетителя: {phone_number}')


@dp.callback_query_handler(text="about")
async def tell_about(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer_photo(photo='https://wampi.ru/image/Rkryxpf')
    await call.message.answer('Распложение 📍 \n'
                              'Наш гостевой дом находится  в 10 км от Тулы, на территории эко-парка. 🌳\n'
                              '\n'
                              'Вместимость 🛏\n'
                              'Дом вместимостью 8 взрослых человек +2 по запросу.\n'
                              '\n'
                              'Стоимость и заезд 🛒\n'
                              'Стоимость проживания: 15000₽ сутки. Мы работаем по предоплате!\n'
                              'Регистрация заезда по индивидуальной договорённости (мы найдём подход к каждому гостю).\n'
                              'Возможен ранний check in.\n'
                              '\n'
                              'В стоимость проживания входит ✅\n'
                              'Пользование домом, зоной барбекю, беседкой. На территории имеется парковка.\n'
                              'Площадка Барбекю оборудована всем необходимым: мангал, шампура, казан, решётка гриль. По запросу для Вас подготовят:'
                              ' дрова, уголь, розжиг. 🥩\n'
                              '\n'
                              'Доп услуги 💲\n'
                              'Дополнительно возможен заказ продуктов с фермы (яйца, баранина).\n'
                              'За дополнительную плату на нашей конюшне Вы сможете пройти уроки верховой езды или взять прогулки на лошадях '
                              'или же дрова для камина в дом. 🐎', reply_markup=keyb_back)
    await call.message.delete()
    await Test.Q8.set()


@dp.callback_query_handler(text="helpme")
async def tell_about(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Мы готовы проконсультировать Вас!\n"
                              "Задайте свой вопрос ниже 💬")
    await call.message.delete()
    await Test.Q1.set()


@dp.message_handler(state=Test.Q1)
async def helpme1(message: types.Message, state: FSMContext):
    await bot.send_message('961406924', text=message.text)
    await bot.send_message('961406924', text=f"Спрашивает посетитель: @{message.from_user.username}\n"
                                             f"Попрошу ответить ему в личку.")
    await message.answer("Мы ответим Вам в личные сообщения в ближайшее время.")
    await state.finish()
    await message.answer("Возвращаю Вас в основное меню",
                         reply_markup=keyb0)
