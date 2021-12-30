"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""

import subprocess
import chardet

yandex_ping = ['ping', 'yandex.ru']
youtube_ping = ['ping', 'youtube.com']
line_count = 0
# host_count = 0

yandex = subprocess.Popen(yandex_ping, stdout=subprocess.PIPE)
youtube = subprocess.Popen(youtube_ping, stdout=subprocess.PIPE)
hosts = [yandex, youtube]


for host in hosts:
	for line in host.stdout:
		result = chardet.detect(line)
		line = line.decode(result['encoding']).encode('utf-8')
		print(line.decode('utf-8'))
		line_count += 1
		if line_count > 5-1:
			break
	line_count = 0
