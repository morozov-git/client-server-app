"""Программа-сервер"""

import socket
import sys
import json
import argparse
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, \
    MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, ACCOUNT_NAME, SENDER, MESSAGE, MESSAGE_TEXT
from common.utils import get_message, send_message
import logging
import time
import logs.config_server_log
from loging_decos import Log
import select



# Инициализация серверного логера
SERVER_LOGGER = logging.getLogger('server')

@Log()
class ServerApp:

    @classmethod
    def process_client_message(cls, message, messages_list, client):
        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента

        :param message:
        :return:
        '''
        SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
            send_message(client, {RESPONSE: 200})
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
                TIME in message and MESSAGE_TEXT in message:
            messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
            return

        else:
            send_message(client, {RESPONSE: 400, ERROR: 'Bad Request'})
            return


    @classmethod
    def arg_parser(cls):
        """Парсер аргументов коммандной строки"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[2:])
        listen_address = namespace.a
        listen_port = namespace.p

        # проверка получения корретного номера порта для работы сервера.
        if not 1023 < listen_port < 65536:
            SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                                   f'{listen_port}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)
        return listen_address, listen_port


    @classmethod
    def main(cls, *args, **kwargs):
        '''
        Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
        Сначала обрабатываем порт:
        server.py -p 8079 -a 192.168.0.86
        :return:
        '''
        listen_address, listen_port = ServerApp.arg_parser()
        # переменные для тестов
        if args:
            if args[0] == 'test':
                SERVER_LOGGER.debug(f'Запущен тест ServerApp с параметрами: {args}')
                sys.argv = args

        SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                    f'адрес с которого принимаются подключения: {listen_address}. '
                    f'Если адрес не указан, принимаются соединения с любых адресов.')

        try:
            if '-p' in sys.argv:
                listen_port = int(sys.argv[sys.argv.index('-p') + 1])
            else:
                listen_port = DEFAULT_PORT
            if listen_port < 1024 or listen_port > 65535:
                raise ValueError
        except IndexError:
            # print('После параметра -\'p\' необходимо указать номер порта.')
            SERVER_LOGGER.error(f'После параметра -\'p\' необходимо указать номер порта.')
            # sys.exit(1)
            # для тестов
            return 'PORT NOT SET'

        except ValueError:
            # print('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
            SERVER_LOGGER.error(f'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
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
            # print('После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
            SERVER_LOGGER.error(f'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
            sys.exit(1)
        server_start_message = f'Сервер запущен. Адрес: {listen_address} Порт: {listen_port}'
        SERVER_LOGGER.debug(server_start_message)
        print(server_start_message)

        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((listen_address, listen_port))
        transport.settimeout(0.5)

        # список клиентов , очередь сообщений
        clients = []
        messages = []

        # Слушаем порт
        transport.listen(MAX_CONNECTIONS)
        # Основной цикл программы сервера
        while True:
            try:
                client, client_address = transport.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'Установлено соедение с Клиентом: {client_address}')
                clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass
            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        ServerApp.process_client_message(get_message(client_with_message), messages, client_with_message)
                    except:
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            if messages and send_data_lst:
                message = {ACTION: MESSAGE,
                           SENDER: messages[0][0],
                           TIME: time.time(),
                           MESSAGE_TEXT: messages[0][1]}
                del messages[0]
                for waiting_client in send_data_lst:
                    try:
                        send_message(waiting_client, message)
                    except:
                        SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        clients.remove(waiting_client)

            # try:
            #     message_from_client = get_message(client)
            #     # print(message_from_client)
            #     SERVER_LOGGER.info(f'Сообщение от клиента: {message_from_client}')
            #     # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
            #     response = ServerApp.process_client_message(message_from_client)
            #     SERVER_LOGGER.debug(f'Отправка сообщения: {response} клиенту: {message_from_client["user"]["account_name"]}.')
            #     send_message(client, response)
            #     client.close()
            #     SERVER_LOGGER.debug(f'Клиент остановлен.')
            # except (ValueError, json.JSONDecodeError):
            #     # print('Принято некорретное сообщение от клиента.')
            #     SERVER_LOGGER.error(f'Принято некорретное сообщение от клиента.')
            #     client.close()
            #     SERVER_LOGGER.debug(f'Клиент остановлен.')


if __name__ == '__main__':
    ServerApp = ServerApp()
    ServerApp.main()

# server.py -p 8888 -a 192.168.0.49
# server.py -p 8888 -a 192.168.0.101