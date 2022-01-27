"""Программа-клиент"""

import sys
import json
import socket
import time
import argparse
import logging
from errors import ReqFieldMissingError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, ACCOUNT_NAME, SENDER, MESSAGE, MESSAGE_TEXT
from common.utils import get_message, send_message
from loging_decos import Log
from errors import ReqFieldMissingError, ServerError

# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


@Log()
class ClientApp:

    @classmethod
    def message_from_server(cls, message):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
            inbox_message = f'От пользователя:{message[SENDER]} получено сообщение :\n {message[MESSAGE_TEXT]}'
            print(inbox_message)
            CLIENT_LOGGER.info(inbox_message)
        else:
            CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')

    @classmethod
    def create_message(cls, sock, account_name='Guest'):
        """
        Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды
        """
        message = input('Введите сообщение для отправки или \'exit\' для завершения работы: ')
        if message == 'exit':
            sock.close()
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        message_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: account_name,
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        return message_dict

    @classmethod
    def create_presence(cls, account_name='Guest'):
        '''
        Функция генерирует запрос о присутствии клиента
        :param account_name:
        :return:
        '''
        # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        out = {ACTION: PRESENCE,
               TIME: time.time(),
               USER: {ACCOUNT_NAME: account_name}
            }
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    @classmethod
    def process_response_ans(cls, message):
        """
        Функция разбирает ответ сервера на сообщение о присутствии,
        возращает 200 если все ОК или генерирует исключение при ошибке
        """
        CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @classmethod
    def process_answer(cls, message):
        '''
        Функция разбирает ответ сервера
        :param message:
        :return:
        '''
        CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ReqFieldMissingError(RESPONSE)

    @classmethod
    def arg_parser(cls):
        """
        Создаём парсер аргументов коммандной строки
        и читаем параметры, возвращаем 3 параметра
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
        parser.add_argument('-m', '--mode', default='listen', nargs='?')
        parser.add_argument('-u', '--user', default='Guest', nargs='?')
        namespace = parser.parse_args(sys.argv[2:])
        server_address = namespace.addr
        server_port = namespace.port
        client_mode = namespace.mode
        client_name = namespace.user

        # проверим подходящий номер порта
        if not 1023 < server_port < 65536:
            CLIENT_LOGGER.critical(f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
                                   f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
            sys.exit(1)
        # Проверим допустим ли выбранный режим работы клиента
        if client_mode not in ('listen', 'send'):
            CLIENT_LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
                                   f'допустимые режимы: listen , send')
            sys.exit(1)
        return server_address, server_port, client_mode, client_name

    @classmethod
    def main(cls, *args, **kwargs):
        '''Загружаем параметы коммандной строки'''
        # client.py 192.168.0.100 8079
        server_address, server_port, client_mode, client_name = ClientApp.arg_parser()

        CLIENT_LOGGER.info(f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
                    f'порт: {server_port}, режим работы: {client_mode}')

        # переменные для тестов
        if args:
            if args[0] == 'test':
                CLIENT_LOGGER.debug(f'Запущен тест ClientApp с параметрами: {args}')
                sys.argv = args

        # Сбор параметров подключения перенесено в отдельную функцию
        # try:
        #     server_address = sys.argv[2]
        #     server_port = int(sys.argv[3])
        #     if server_port < 1024 or server_port > 65535:
        #         raise ValueError
        # except IndexError:
        #     server_address = DEFAULT_IP_ADDRESS
        #     server_port = DEFAULT_PORT
        # except ValueError:
        #     # print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        #     CLIENT_LOGGER.error(f'В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        #     # sys.exit('BAD PORT')
        #     # raise SystemExit('BAD PORT')
        #     # raise ValueError('BAD PORT')
        #     return 'BAD PORT'
        #     # sys.exit(1)
        #
        # CLIENT_LOGGER.info(f'Запущен клиент с парамертами: (адрес сервера: {server_address}, порт: {server_port})')


        # Инициализация сокета и обмен приветствиями
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((server_address, server_port))
            message_to_server = ClientApp.create_presence()
            send_message(transport, message_to_server)
            answer = ClientApp.process_answer(get_message(transport))
            CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
            print(answer)  # Печатаем ответ от сервера в косоль для наглядности
        # except (ValueError, json.JSONDecodeError):
        #     print('Не удалось декодировать сообщение сервера.')
        except json.JSONDecodeError:
            CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                f'{missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                                   f'сервер отверг запрос на подключение.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # начинаем обмен с ним, согласно требуемому режиму.
            # основной цикл прогрммы:
            if client_mode == 'send':
                print('Режим работы - отправка сообщений.')
            else:
                print('Режим работы - приём сообщений.')
            while True:
                # режим работы - отправка сообщений
                if client_mode == 'send':
                    try:
                        send_message(transport, ClientApp.create_message(transport, client_name))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)

                # Режим работы приём:
                if client_mode == 'listen':
                    try:
                        ClientApp.message_from_server(get_message(transport))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)




if __name__ == '__main__':
    ClientApp = ClientApp()
    ClientApp.main()

# client.py 192.168.0.49 8888 -m send -u TestSender