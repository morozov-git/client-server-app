"""
Задание 6.

Создать  НЕ программно (вручную) текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».

Принудительно программно открыть файл в формате Unicode и вывести его содержимое.
Что это значит? Это значит, что при чтении файла вы должны явно указать кодировку utf-8
и файл должен открыться у ЛЮБОГО!!! человека при запуске вашего скрипта.

При сдаче задания в папке должен лежать текстовый файл!

Это значит вы должны предусмотреть случай, что вы по дефолту записали файл в cp1251,
а прочитать пытаетесь в utf-8.

Преподаватель будет запускать ваш скрипт и ошибок НЕ ДОЛЖНО появиться!

Подсказки:
--- обратите внимание, что заполнять файл вы можете в любой кодировке
но открыть нужно ИМЕННО!!! в формате Unicode (utf-8)
--- обратите внимание на чтение файла в режиме rb
для последующей переконвертации в нужную кодировку

НАРУШЕНИЕ обозначенных условий - задание не выполнено!!!
"""
from chardet import detect


with open('test_file.txt', 'rb') as file:
	file_content = file.read()
encoding = detect(file_content)['encoding']
print(f"Кодировка файла: {encoding}")
# if encoding == 'utf-8':
try:
	with open('test_file.txt', 'r', encoding='utf-8') as file:
		print(file.read())
# else:
except:
	with open('test_file.txt', 'r', encoding=encoding) as file:
		print(file.read())

