"""Программа-клиент"""

import sys
import json
import socket
import time
import argparse
import logging
from errors import ReqFieldMissingError
from Lesson_5.common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from Lesson_5.common.utils import get_message, send_message


# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')

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
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out


    def process_answer(message):
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
        raise ValueError


    def main(*args, **kwargs):
        '''Загружаем параметы коммандной строки'''
        # client.py 192.168.0.100 8079

        # переменные для тестов
        if args:
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

        CLIENT_LOGGER.info(f'Запущен клиент с парамертами:\n '
                           f' адрес сервера: {server_address},\n'
                           f' порт: {server_port}')

        # Инициализация сокета и обмен

        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = ClientApp.create_presence()
        send_message(transport, message_to_server)
        try:
            answer = ClientApp.process_answer(get_message(transport))
            CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
            print(answer)
        # except (ValueError, json.JSONDecodeError):
        #     print('Не удалось декодировать сообщение сервера.')
        except json.JSONDecodeError:
            CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        except ReqFieldMissingError as missing_error:
            CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                f'{missing_error.missing_field}')
        except ConnectionRefusedError:
            CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                                   f'сервер отверг запрос на подключение.')




if __name__ == '__main__':
    ClientApp.main()

# client.py 192.168.0.61 8888