import requests
import pandas as pd
import pika
import json


metall = [
    'aluminium', 'copper',
    'lead', 'nickel', 'zink'
]

def get_metalls(metall_name: str):

    # Список источников, нам понадобится информация по 5 видам сырья:
    # алюминий, медь, свинец, никель и цинк
    metalls = {
        'aluminium': 'Al', 'copper': 'Cu',
        'lead': 'Pb', 'nickel': 'Ni', 'zink': 'Zn'
    }

    # Запрос к источнику
    url = f'https://www.westmetall.com/en/markdaten.php?action=table&field=LME_{metalls[metall_name]}_cash'

    responce = requests.get(url)
    # Чтение ответа
    responce_data = pd.read_html(responce.text)

    # Предобработка
    responce_cur_data = responce_data[0]
    responce_cur_data = responce_cur_data.loc[responce_cur_data['date'] != 'date']

    # Преобразование в формат datetime
    responce_cur_data['date'] = responce_cur_data['date'].apply(
        pd.to_datetime).dt.date

    columns = responce_cur_data.columns.to_list()[1:]

    # Преобразование в числовой формат
    for column_name in columns:
        responce_cur_data[column_name] = responce_cur_data[column_name].apply(
            pd.to_numeric)

    # Восстановление коректного порядка для остатков
    responce_cur_data.iloc[:, -1] /= 1000

    # Cоздадим датафрейм из БД
    data = pd.read_csv(
        f'./data/{metall_name}.csv',
        parse_dates=['date']).assign(date=lambda x: x['date'].dt.date)

    # Бэкап БД
    data.to_csv(f'./data/backup/{metall_name}.csv', sep=',')

    data = pd.concat([responce_cur_data, data])
    data.drop_duplicates(inplace=True)
    data.set_index('date', inplace=True)

    return data


if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очереди для отправки сообщений
    channel.queue_declare(queue='metall_queue')

    for i in metall:
        # Получение данных
        data = get_metalls(i)

        # Отправка данных в очередь RabbitMQ
        channel.basic_publish(exchange='', routing_key='metall_queue', body=f'{i}:{data.to_json()}')

    # Закрытие подключения к RabbitMQ
    connection.close()
