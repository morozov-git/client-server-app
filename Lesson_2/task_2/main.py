"""
2. Задание на закрепление знаний по модулю json. Есть файл orders
в формате JSON с информацией о заказах. Написать скрипт, автоматизирующий
его заполнение данными.

Для этого:
Создать функцию write_order_to_json(), в которую передается
5 параметров — товар (item), количество (quantity), цена (price),
покупатель (buyer), дата (date). Функция должна предусматривать запись
данных в виде словаря в файл orders.json. При записи данных указать
величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json()
с передачей в нее значений каждого параметра.

ПРОШУ ВАС НЕ УДАЛЯТЬ ИСХОДНЫЙ JSON-ФАЙЛ
ПРИМЕР ТОГО, ЧТО ДОЛЖНО ПОЛУЧИТЬСЯ

{
    "orders": [
        {
            "item": "принтер", (возможные проблемы с кирилицей)
            "quantity": "10",
            "price": "6700",
            "buyer": "Ivanov I.I.",
            "date": "24.09.2017"
        },
        {
            "item": "scaner",
            "quantity": "20",
            "price": "10000",
            "buyer": "Petrov P.P.",
            "date": "11.01.2018"
        },
        {
            "item": "scaner",
            "quantity": "20",
            "price": "10000",
            "buyer": "Petrov P.P.",
            "date": "11.01.2018"
        },
        {
            "item": "scaner",
            "quantity": "20",
            "price": "10000",
            "buyer": "Petrov P.P.",
            "date": "11.01.2018"
        }
    ]
}

вам нужно подгрузить JSON-объект
и достучаться до списка, который и нужно пополнять
а потом сохранять все в файл
"""

import json

orders = {
	"orders": [
		{
			"item": "принтер",
			"quantity": "10",
			"price": "6700",
			"buyer": "Ivanov I.I.",
			"date": "24.09.2017"
		},
		{
			"item": "scaner",
			"quantity": "20",
			"price": "10000",
			"buyer": "Petrov P.P.",
			"date": "11.01.2018"
		},
		{
			"item": "scaner",
			"quantity": "20",
			"price": "10000",
			"buyer": "Petrov P.P.",
			"date": "11.01.2018"
		},
		{
			"item": "scaner",
			"quantity": "20",
			"price": "10000",
			"buyer": "Petrov P.P.",
			"date": "11.01.2018"
		}
	]
}

# for item in orders["orders"]:
# 	keys = list(item.keys())
# 	values = list(item.values())
	# print(*keys)
	# print(*values)


def json_writer(item, quantity, price, buyer, date):
	with open('orders_out.json', 'r') as orders_f:
		orders_f_CONTENT = orders_f.read()
		orders_dict = json.loads(orders_f_CONTENT)
	# print(orders_dict['orders'])

	with open('orders_out.json', 'w', encoding='utf-8') as orders_out_f:
		orders_list = orders_dict['orders']
		order_data = {'item': item, 'quantity': quantity, 'price': price, 'buyer': buyer, 'date': date}
		orders_list.append(order_data)
		json.dump(orders_dict, orders_out_f, indent=4, ensure_ascii=False)



# цикл для обработки словаря из шапки задания и автоматической записи данных
for item in orders["orders"]:
	keys = list(item.keys())
	values = list(item.values())
	item, quantity, price, buyer, date = values
	json_writer(item, quantity, price, buyer, date)

# Если нужно дописать отдельные данные в файл, то вызываем функцию json_writer с нужными параметрами
json_writer("монитор", "20", "7700", "Petrov I.I.", "22.11.2021")