from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
def menu_user():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Пройти регистрацию", callback_data="register"),
    )

    return markup

def record_game():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Запись на игру", callback_data="record"),
        InlineKeyboardButton("Отписаться от игры", callback_data="unsubscribe"),        
        InlineKeyboardButton("Статиcтика", callback_data="statistic"),

    )

    return markup

def back_user():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Назад", callback_data="back_user"),
    )

    return markup

def games_board(list_):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    list_butt = []
    for i in list_:
        list_butt.append(InlineKeyboardButton(i, callback_data=f"dategame::{i}"))
    markup.add(*list_butt)
    return markup

def out_games_board(list_):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    list_butt = []
    for i in list_:
        list_butt.append(InlineKeyboardButton(i, callback_data=f"outgame::{i}"))
    markup.add(*list_butt)
    return markup

def games_admin_board(list_):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    list_butt = []
    for i in list_:
        list_butt.append(InlineKeyboardButton(i, callback_data=f"date_admin_game::{i}"))

    markup.add(*list_butt)

    return markup

def close_games(list_):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    list_butt = []
    for i in list_:
        list_butt.append(InlineKeyboardButton(i, callback_data=f"close_game::{i}"))

    markup.add(*list_butt)

    return markup

def up_stats(user_id, table_name):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("+ гол", callback_data=f"stats::plus_goal::{user_id}::{table_name}"),
        InlineKeyboardButton("- гол", callback_data=f"stats::minus_goal::{user_id}::{table_name}"),
        InlineKeyboardButton("+ пас", callback_data=f"stats::plus_pas::{user_id}::{table_name}"),
        InlineKeyboardButton("- пас", callback_data=f"stats::minus_pas::{user_id}::{table_name}"),
    )

    return markup

def menu_admin():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("создать", callback_data="create"),
        InlineKeyboardButton("закрыть", callback_data="close"),
        InlineKeyboardButton("выбрать", callback_data="choice"),  
        InlineKeyboardButton("рейтинг", callback_data="admin_stats"),     
    )

    return markup


def back_admin():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Назад", callback_data="back_admin"),
  
    )

    return markup