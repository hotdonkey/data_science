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

    return data


if __name__ == '__main__':
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Создание очереди для отправки сообщений

    for i in metall:
        channel.queue_declare(queue=f'raw_{i}_queue')

    for target in metall:
        # Получение данных
        data = get_metalls(target)

        # Отправка данных в очередь RabbitMQ
        channel.basic_publish(
            exchange='', 
            routing_key=f'raw_{target}_queue', 
            body=json.dumps({
                'id':target,
                'body':data.to_json()}
            )
        )

    # Закрытие подключения к RabbitMQ
    connection.close()
