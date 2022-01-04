"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import csv
import re


os_prod_list = []
os_name_list = []
os_code_list = []
os_type_list = []
main_data = []
headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']

def get_data():
    for i in range(1, 4):
        with open(f'info_{i}.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if re.match('Изготовитель системы', line) or re.match('Название ОС', line) or re.match('Код продукта', line) or re.match('Тип системы', line):
                    key = (re.findall('(.+)[:]', line)).pop()
                    item = (re.findall('[:]\s+(\w+.*$)', line)).pop()
                    if key == 'Изготовитель системы':
                        os_prod_list.append(item)
                    if key == 'Название ОС':
                        os_name_list.append(item)
                    if key == 'Код продукта':
                        os_code_list.append(item)
                    if key == 'Тип системы':
                        os_type_list.append(item)
    # print(os_prod_list, os_name_list, os_code_list, os_type_list)

    main_data.append(headers)
    for i in range(0, len(os_prod_list)):
        system_data = []
        system_data.append(os_prod_list.pop(0))
        system_data.append(os_name_list.pop(0))
        system_data.append(os_code_list.pop(0))
        system_data.append(os_type_list.pop(0))
        # print(system_data)
        main_data.append(system_data)
    # print(main_data)

def write_to_csv(file_name):
    get_data()
    with open(file_name, "w") as file:
        file_writer = csv.writer(file)
        for row in main_data:
            file_writer.writerow(row)

write_to_csv('system_data.csv')