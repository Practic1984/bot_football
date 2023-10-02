import telebot
from telebot import types

from config import TOKEN, ADMIN_USER, ADMIN_LIST, GROUP_ID

import logging
import msg
import keybords
from sqliteormmagic import SQLiteDB
import sqliteormmagic as som
import pandas as pd
import openpyxl

db_games =SQLiteDB('games.db')

bot = telebot.TeleBot(token=TOKEN, parse_mode='HTML', skip_pending=True)    
bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Запуск бота"),
    ],)


def main():
    @bot.message_handler(commands=['start'])
    def start_user(message):
        bot.send_message(chat_id=GROUP_ID, text=msg.start_msg_user, reply_markup=keybords.menu_user())
        bot.send_message(chat_id=message.from_user.id, text=msg.start_msg_user, reply_markup=keybords.menu_user())
        

     
    @bot.message_handler(commands=['admin']) # меню админа   
    def start_fnc(message):
        print(message.from_user.id)
        if message.from_user.id in ADMIN_LIST:
            bot.send_message(chat_id=message.from_user.id, text=msg.start_msg_admin,reply_markup=keybords.menu_admin())
        
    # @bot.message_handler(content_types=['photo'])
    # def get_photo(message):
    #     foto = message.photo[len(message.photo) - 1].file_id
    #     file_info = bot.get_file(foto)
    #     photo = bot.download_file(file_info.file_path)

    # @bot.message_handler(content_types=['video'])
    # def get_video(message):
    #     video = message.video.file_id
    #     file_info = bot.get_file(video)
    #     video = bot.download_file(file_info.file_path)
    
    # @bot.message_handler(content_types=['document'])
    # def get_document(message):
    #     document = message.document.file_id
    #     file_info = bot.get_file(document)
    #     document = bot.download_file(file_info.file_path)
        
    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
 
        if call.data == 'create':                    # меню админа   
            db_games.create_table('games', [
            ('date_game', 'TEXT UNIQUE'), 
            ('status', 'TEXT'),
        ])
            m = bot.send_message(chat_id=call.from_user.id, text=msg.create_game_msg)
            bot.register_next_step_handler(m, create_game)
        
        elif call.data == 'close':                   # меню админа   
            list_tuple_games = db_games.find_elements_in_column(table_name='games', key_name='open', column_name='status')
            print(list_tuple_games)
            list_games = []
            for date_txt in list_tuple_games:
                list_games.append(date_txt[0])
            print(list_games)
            bot.send_message(chat_id=call.from_user.id, text=msg.choice_date_msg_admin, reply_markup=keybords.close_games(list_games))
                      
        elif 'close_game' in call.data:              # меню админа
            print(call.data)
            game_name = call.data.split('::')[1]
            connection = som.create_connection('games.db')
            query = f"""SELECT * 
                FROM {game_name}
                """ 
            players = som.execute_query_select(connection, query=query, params=[])
            connection.close()
            if players != None:
                #добавить статистику игроков в таблицу players
                for player in players:
                    print(player)
                    
                    connection = som.create_connection('games.db')
                    query = f"""
                    UPDATE players 
                    SET goals=goals+{player[4]}, pas=pas+{player[5]}  
                    WHERE from_user_id={player[0]};
                    """
                    som.execute_query_select(connection, query=query, params=[])
                    connection.close()
            else:
                bot.send_message(chat_id=call.from_user.id, text=f'На эту игру {game_name} небыло регистраций игроков, но мы все равно ее закрываем')
           
            #удалить таблицу статистики на дату
            connection = som.create_connection('games.db')
            query = f""" DROP TABLE {game_name};
                """ 
            som.execute_query_select(connection, query=query, params=[])
            connection.close()
            db_games.upd_element_in_column(table_name='games', upd_par_name='status', key_par_name='close', upd_column_name='date_game', key_column_name=game_name)
            bot.send_message(chat_id=call.from_user.id, text=f'Игра {game_name} успешно закрыта', reply_markup=keybords.back_admin())
        elif call.data == 'choice':                  # меню админа   
            list_tuple_games = db_games.find_elements_in_column(table_name='games', key_name='open', column_name='status')
            print(list_tuple_games)
            list_games = []
            for date_txt in list_tuple_games:
                list_games.append(date_txt[0])
            print(list_games)
            bot.send_message(chat_id=call.from_user.id, text=msg.choice_date_msg_admin, reply_markup=keybords.games_admin_board(list_games))
                      

        elif 'date_admin_game' in call.data:         # меню админа  
            print(call.data)
            table_name = call.data.split('::')[1]
            connection = som.create_connection('games.db')
            query = f"""SELECT * 
                FROM {table_name}
                """ 
            players = som.execute_query_select(connection, query=query, params=[])
            connection.close()
            if players != None:
                for player in players:
                    print(player)
                    text = ''
                    text = f"""
ID в Телеграмм {player[0]}
Username в Телеграмм @{player[1]}
Имя игрока на поле <b>{player[2]}</b>
Номер телефона {player[3]}
Голов забито в игре {player[4]}
Голевых передач в игре {player[5]}
    """             
                    for user_id in ADMIN_LIST:
                        bot.send_message(chat_id=user_id, text=text, reply_markup=keybords.up_stats(user_id=player[0], table_name=table_name))
            else:
                for user_id in ADMIN_LIST:
                    bot.send_message(chat_id=user_id, text=msg.no_players_text, reply_markup=keybords.back_admin())
        
        elif call.data == 'admin_stats':
            print(call.data)
            connection = som.create_connection('games.db')
            query = f"""
SELECT * FROM players;
            """
            players = pd.read_sql_query(query, connection)
            print(players)
            # res = som.execute_query(connection=connection, query=query, params=[])
            connection.close()
            
            players['rating'] = (players['goals'] + players['goals'])/players['matches']
            players_sort = players.sort_values (by = ['rating'], ascending = [ False ])
            players_sort.to_excel('res_stats.xlsx',index=False)
            with open('res_stats.xlsx', mode='rb') as filename:
                bot.send_document(call.from_user.id, document=filename, caption='Отчет по рейтингу в прикрепленном файле')
            print(players_sort)    

        elif 'stats' in call.data:                     # меню админа  

            if 'plus_goal' in call.data:
                print(call.data)
                table_name = call.data.split('::')[3]
                user_id = call.data.split('::')[2]
                connection = som.create_connection('games.db')
                query = """
                UPDATE {table_name} 
                SET goals=goals+1 
                WHERE from_user_id={from_user_id};
                """.format(table_name=table_name, from_user_id=user_id)
                som.execute_query(connection=connection, query=query, params=[])
                connection.close()
                bot.send_message(chat_id=call.from_user.id, text=f"Статистика на {table_name} изменена", reply_markup=keybords.back_admin())

            elif 'minus_goal' in call.data:
                print(call.data)
                table_name = call.data.split('::')[3]
                user_id = call.data.split('::')[2]
                connection = som.create_connection('games.db')
                query = """
                UPDATE {table_name} 
                SET goals=goals-1 
                WHERE from_user_id={from_user_id};
                """.format(table_name=table_name, from_user_id=user_id)
                som.execute_query(connection=connection, query=query, params=[])
                connection.close()
                bot.send_message(chat_id=call.from_user.id, text=f"Статистика на {table_name} изменена", reply_markup=keybords.back_admin())


            elif 'plus_pas' in call.data:
                print(call.data)
                table_name = call.data.split('::')[3]
                user_id = call.data.split('::')[2]
                connection = som.create_connection('games.db')
                query = """
                UPDATE {table_name} 
                SET pas=pas+1 
                WHERE from_user_id={from_user_id};
                """.format(table_name=table_name, from_user_id=user_id)
                som.execute_query(connection=connection, query=query, params=[])
                connection.close()
                bot.send_message(chat_id=call.from_user.id, text=f"Статистика на {table_name} изменена", reply_markup=keybords.back_admin())


            elif 'minus_pas' in call.data:
                print(call.data)
                table_name = call.data.split('::')[3]
                user_id = call.data.split('::')[2]
                connection = som.create_connection('games.db')
                query = """
                UPDATE {table_name} 
                SET pas=pas-1 
                WHERE from_user_id={from_user_id};
                """.format(table_name=table_name, from_user_id=user_id)
                som.execute_query(connection=connection, query=query, params=[])
                connection.close()
                bot.send_message(chat_id=call.from_user.id, text=f"Статистика на {table_name} изменена", reply_markup=keybords.back_admin())


        elif call.data == 'back_admin':              # меню админа   
            bot.send_message(chat_id=call.from_user.id, text=msg.start_msg_admin,reply_markup=keybords.menu_admin())

        elif call.data == 'register':                # меню игрока  
            db_games.create_table('players', [
                ('from_user_id', 'INTEGER UNIQUE'), 
                ('from_user_username', 'TEXT'),
                ('player_name', 'TEXT'),
                ('phone', 'TEXT'),
                ('matches', 'INTEGER'),                
                ('goals', 'INTEGER'),
                ('pas', 'INTEGER'),                

            ])
            db_games.ins_unique_row('players', [
                ('from_user_id', call.from_user.id), 
                ('from_user_username', call.from_user.username),
                ('player_name', 'None'),
                ('phone', 'None'),
                ('matches', 0),                
                ('goals', 0),
                ('pas', 0),  
            ])
            
            m = bot.send_message(chat_id=call.from_user.id, text=msg.input_name_in_game)
            bot.register_next_step_handler(m, input_name_in_game)
        
        elif call.data == 'record':
            list_tuple_games = db_games.find_elements_in_column(table_name='games', key_name='open', column_name='status')
            print(list_tuple_games)
            list_games = []
            for date_txt in list_tuple_games:
                list_games.append(date_txt[0])
            print(list_games)
            bot.send_message(chat_id=call.from_user.id, text=msg.choice_date_msg, reply_markup=keybords.games_board(list_games))
        
        elif call.data == 'unsubscribe':
            list_tuple_games = db_games.find_elements_in_column(table_name='games', key_name='open', column_name='status')
            print(list_tuple_games)
            list_games = []
            for date_txt in list_tuple_games:
                list_games.append(date_txt[0])
            print(list_games)
            bot.send_message(chat_id=call.from_user.id, text=msg.outgame_date_msg, reply_markup=keybords.out_games_board(list_games))
        

        elif 'dategame' in call.data:
            print(call.data)
            dategame = call.data.split('::')[1].strip()
            
            print(dategame)
             
            connection = som.create_connection('games.db')
            query = """
            UPDATE players 
            SET matches=matches+1 
            WHERE from_user_id={from_user_id};
            """.format(from_user_id=call.from_user.id)

            som.execute_query(connection=connection, query=query, params=[])
            connection.close()

            print('************************')
            db_games.create_table(table=f"{dategame}", list_query_params=[
                ('from_user_id', 'INTEGER UNIQUE'), 
                ('from_user_username', 'TEXT'),
                ('player_name', 'TEXT'),
                ('phone', 'TEXT'),
                ('goals', 'INTEGER'),
                ('pas', 'INTEGER')  
            ])
            res = db_games.find_elements_in_column(table_name='players', key_name=call.from_user.id, column_name='from_user_id')
            res = res[0]
            print(res)
            print('************************')
            db_games.ins_unique_row(table_name=f"{dategame}", list_query_params=[
                ('from_user_id', call.from_user.id), 
                ('from_user_username', call.from_user.username),
                ('player_name', res[2]),
                ('phone', res[3]),
                ('goals', 0),
                ('pas', 0)  
            ])
            date_txt = dategame[1:]
            text_record_group = f"""
Игрок {res[2]} 
Username @{res[1]}
записался на {date_txt}
"""         
            bot.send_message(chat_id=GROUP_ID, text=text_record_group)   
            bot.send_message(chat_id=call.from_user.id, text=msg.date_msg_sucess.format(date_txt=date_txt), reply_markup=keybords.back_user())
        

        elif 'outgame' in call.data:
            print(call.data)
            dategame = call.data.split('::')[1].strip()
            
            print(dategame)
             
            connection = som.create_connection('games.db')
            query = """
            UPDATE players 
            SET matches=matches-1 
            WHERE from_user_id={from_user_id};
            """.format(from_user_id=call.from_user.id)

            som.execute_query(connection=connection, query=query, params=[])
            connection.close()

            print('************************')
            db_games.create_table(table=f"{dategame}", list_query_params=[
                ('from_user_id', 'INTEGER UNIQUE'), 
                ('from_user_username', 'TEXT'),
                ('player_name', 'TEXT'),
                ('phone', 'TEXT'),
                ('goals', 'INTEGER'),
                ('pas', 'INTEGER')  
            ])
            res = db_games.find_elements_in_column(table_name='players', key_name=call.from_user.id, column_name='from_user_id')
            res = res[0]
            print(res)
            print('************************')
            # здесь надо не добавить а удалить запись
            connection = som.create_connection('games.db')
            query = f"""
DELETE FROM {dategame} WHERE from_user_id={res[0]};
            """
            som.execute_query(connection=connection, query=query, params=[])
            connection.close()
            # db_games.ins_unique_row(table_name=f"{dategame}", list_query_params=[
            #     ('from_user_id', call.from_user.id), 
            #     ('from_user_username', call.from_user.username),
            #     ('player_name', res[2]),
            #     ('phone', res[3]),
            #     ('goals', 0),
            #     ('pas', 0)  
            # ])
            date_txt = dategame[1:]
            text_record_group = f"""
Игрок {res[2]} 
Username @{res[1]}
не придет на игры {date_txt}
"""         
            bot.send_message(chat_id=GROUP_ID, text=text_record_group)   
            bot.send_message(chat_id=call.from_user.id, text=msg.date_msg_outgame.format(date_txt=date_txt), reply_markup=keybords.back_user())
        

        elif call.data == 'statistic':
            print(call.data)
            player = db_games.find_elements_in_column(table_name='players', key_name=call.from_user.id, column_name='from_user_id')
            player = player[0]
            matches = player[4]
            goals = player[5]
            pas = player[6]
            print(player)
            rating = (goals + pas)/matches
            text = f"""
Ваши показатели ⤵️
Рейтинг: <b>{rating}</b>
Игровых дней: <b>{matches}</b>
Голов забито: <b>{goals}</b>
Голевых передач: <b>{pas}</b>
"""
            bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keybords.record_game())




        elif call.data == 'back_user':
            bot.send_message(chat_id=call.from_user.id, text=msg.main_menu_msg, reply_markup=keybords.record_game())

            
    @bot.message_handler(content_types=['text'])
    def get_text(message):
        if message.chat.id != GROUP_ID:
            print(message)
            print(f"message {message.text}")

    def create_game(message):
        if message.chat.id != GROUP_ID:
            if message.from_user.id in ADMIN_LIST:       # меню игрока     
                db_games.ins_unique_row('games', [
                ('date_game', message.text), 
                ('status', 'open'),
                ])
                bot.send_message(chat_id=message.from_user.id, text=msg.create_game_msg_sucess.format(game=message.text), reply_markup=keybords.back_admin())
        
    def input_name_in_game(message):                 # меню игрока
        if message.chat.id != GROUP_ID:
            print(f"message {message.text}")
            name_in_game = message.text
            db_games.upd_element_in_column(table_name='players', upd_par_name='player_name', key_par_name=name_in_game, upd_column_name='from_user_id', key_column_name=message.from_user.id)      
            m = bot.send_message(chat_id=message.from_user.id, text=msg.input_phone)
            bot.register_next_step_handler(m, input_phone)

    def input_phone(message):                        # меню игрока
        if message.chat.id != GROUP_ID:
            print(f"message {message.text}")
            phone = message.text
            db_games.upd_element_in_column(table_name='players', upd_par_name='phone', key_par_name=phone, upd_column_name='from_user_id', key_column_name=message.from_user.id)       
            bot.send_message(chat_id=message.from_user.id, text=msg.main_menu_msg, reply_markup=keybords.record_game())


    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    main()

    