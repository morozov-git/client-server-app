"""Программа-клиент"""

import sys
import json
import socket
import time

from Lesson_4.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from Lesson_4.common.utils import get_message, send_message

class ClientApp:
    def create_presence(account_name='Guest'):
        '''
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        '''
        # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        return out


    def process_answer(message):
        '''
        Функция разбирает ответ сервера
        :param message:
        :return:
        '''
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ValueError


    def main(*args, **kwargs):
        '''Загружаем параметы коммандной строки'''
        # client.py 192.168.0.100 8079
        if args[0] == 'test':
            sys.argv = args
        try:
            server_address = sys.argv[2]
            server_port = int(sys.argv[3])
            if server_port < 1024 or server_port > 65535:
                raise ValueError
        except IndexError:
            server_address = DEFAULT_IP_ADDRESS
            server_port = DEFAULT_PORT
        except ValueError:
            print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
            # sys.exit('BAD PORT')
            # raise SystemExit('BAD PORT')
            # raise ValueError('BAD PORT')
            return 'BAD PORT'
            # sys.exit(1)


        # Инициализация сокета и обмен

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = ClientApp.create_presence()
        send_message(transport, message_to_server)
        try:
            answer = ClientApp.process_answer(get_message(transport))
            print(answer)
        except (ValueError, json.JSONDecodeError):
            print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    ClientApp.main()

# client.py 192.168.0.100 8888