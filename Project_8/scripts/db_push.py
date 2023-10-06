import pandas as pd
import json
import pika

metall = [
    'aluminium', 'copper',
    'lead', 'nickel', 'zink'
]


def get_metalls(metall_name: str):

    # Cоздадим датафрейм из БД
    data = pd.read_csv(
        f'./data/{metall_name}.csv', index_col='date', parse_dates=['date'])

    # Отправка данных в очередь RabbitMQ
    channel.basic_publish(
        exchange='',
        routing_key=f'raw_queue',
        body=json.dumps({
            'id': target,
            'type':'raw_data',
            'body': data.to_json()}
        )
    )



if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очереди для отправки сообщений
    channel.queue_declare(queue=f'raw_queue')

    for target in metall:
        data = get_metalls(target)

    # Закрытие подключения к RabbitMQ
    connection.close()
