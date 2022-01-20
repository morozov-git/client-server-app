"""Программа-сервер"""

import socket
import sys
import json
from Lesson_5.common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from Lesson_5.common.utils import get_message, send_message

class ServerApp:

    def process_client_message(message):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }


    def main(*args, **kwargs):
        '''
        Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
        Сначала обрабатываем порт:
        server.py -p 8079 -a 192.168.0.86
        :return:
        '''

        # переменные для тестов
        if args:
            if args[0] == 'test':
                sys.argv = args

        try:
            if '-p' in sys.argv:
                listen_port = int(sys.argv[sys.argv.index('-p') + 1])
            else:
                listen_port = DEFAULT_PORT
            if listen_port < 1024 or listen_port > 65535:
                raise ValueError
        except IndexError:
            print('После параметра -\'p\' необходимо указать номер порта.')
            # sys.exit(1)
            # для тестов
            return 'PORT NOT SET'

        except ValueError:
            print('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
            # sys.exit(1)
            # для тестов
            return 'BAD PORT'

        # Затем загружаем какой адрес слушать

        try:
            if '-a' in sys.argv:
                listen_address = sys.argv[sys.argv.index('-a') + 1]
            else:
                listen_address = ''

        except IndexError:
            print(
                'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
            sys.exit(1)

        # Готовим сокет

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))

        # Слушаем порт

        transport.listen(MAX_CONNECTIONS)

        while True:
            client, client_address = transport.accept()
            try:
                message_from_client = get_message(client)
                print(message_from_client)
                # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
                response = ServerApp.process_client_message(message_from_client)
                send_message(client, response)
                client.close()
            except (ValueError, json.JSONDecodeError):
                print('Принято некорретное сообщение от клиента.')
                client.close()


if __name__ == '__main__':
    ServerApp.main()

# server.py -p 8888 -a 192.168.0.61
# server.py -p 8888 -a 192.168.0.101